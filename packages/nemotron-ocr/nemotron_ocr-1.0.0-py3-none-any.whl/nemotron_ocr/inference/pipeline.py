# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import base64
import io
import json
import os
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F
from nemotron_ocr.inference.encoders.recognizer_encoder import RecognitionTargetEncoder
from nemotron_ocr.inference.encoders.relational_encoder import RelationalTargetEncoder
from nemotron_ocr.inference.models.detector.fots_detector import FOTSDetector
from nemotron_ocr.inference.models.recognizer import TransformerRecognizer
from nemotron_ocr.inference.models.relational import GlobalRelationalModel
from nemotron_ocr.inference.post_processing.indirect_grid_sample import IndirectGridSample
from nemotron_ocr.inference.post_processing.data.text_region import TextBlock
from nemotron_ocr.inference.post_processing.quad_rectify import QuadRectify
from nemotron_ocr.inference.post_processing.research_ops import parse_relational_results, reorder_boxes
from nemotron_ocr.inference.pre_processing import interpolate_and_pad, pad_to_square
from nemotron_ocr.inference.weight_downloader import ensure_weights_available
from nemotron_ocr_cpp import quad_non_maximal_suppression, region_counts_to_indices, rrect_to_quads
from PIL import Image, ImageDraw, ImageFont
from torch import amp
from torchvision.io import read_image, decode_image
from torchvision.transforms.functional import convert_image_dtype

PAD_COLOR = torch.tensor([0.485, 0.456, 0.406], dtype=torch.float16)
INFER_LENGTH = 1024
DETECTOR_DOWNSAMPLE = 4
NMS_PROB_THRESHOLD = 0.5
NMS_IOU_THRESHOLD = 0.5
NMS_MAX_REGIONS = 0

MERGE_LEVELS = {"word", "sentence", "paragraph"}
DEFAULT_MERGE_LEVEL = "paragraph"


class NemotronOCR:
    """
    A high-level pipeline for performing OCR on images.
    
    Model weights are automatically downloaded from Hugging Face Hub
    (nvidia/nemotron-ocr-v1) if not found locally.
    
    Args:
        model_dir: Path to directory containing model checkpoints.
                   If None, weights are downloaded to HuggingFace cache.
                   If provided path exists and contains weights, uses them directly.
                   If provided path doesn't have weights, downloads to HF cache.
        hf_token: Hugging Face authentication token (optional).
        force_download: If True, re-download weights even if they exist.
    """

    def __init__(
        self,
        model_dir: Optional[str] = None,
        hf_token: Optional[str] = None,
        force_download: bool = False,
    ):
        # Resolve model directory - download from HuggingFace if needed
        if model_dir is not None:
            local_path = Path(model_dir)
            # Check if the provided path has all required files
            required_files = ["detector.pth", "recognizer.pth", "relational.pth", "charset.txt"]
            if all((local_path / f).is_file() for f in required_files) and not force_download:
                self._model_dir = local_path
            else:
                # Download from HuggingFace
                self._model_dir = ensure_weights_available(
                    model_dir=local_path,
                    force_download=force_download,
                    token=hf_token,
                )
        else:
            # No model_dir specified - download to HuggingFace cache
            self._model_dir = ensure_weights_available(
                model_dir=None,
                force_download=force_download,
                token=hf_token,
            )

        self._load_models()
        self._load_charset()
        self._initialize_processors()

    def _load_models(self):
        """Loads all necessary models into memory."""
        self.detector = FOTSDetector(coordinate_mode="RBOX", backbone="regnet_y_8gf", verbose=False)
        self.detector.load_state_dict(
            torch.load(self._model_dir / "detector.pth", weights_only=True), strict=True
        )

        self.recognizer = TransformerRecognizer(nic=self.detector.num_features[-1], num_tokens=858, max_width=32)
        self.recognizer.load_state_dict(
            torch.load(self._model_dir / "recognizer.pth", weights_only=True), strict=True
        )

        self.relational = GlobalRelationalModel(
            num_input_channels=self.detector.num_features,
            recog_feature_depth=self.recognizer.feature_depth,
            dropout=0.1,
            k=16,
            num_layers=4,
        )
        self.relational.load_state_dict(
            torch.load(self._model_dir / "relational.pth", weights_only=True), strict=True
        )

        for model in (self.detector, self.recognizer, self.relational):
            model = model.cuda()
            model.eval()
            model.inference_mode = True

    def _initialize_processors(self):
        """Initializes helper classes for pre/post-processing."""
        self.recognizer_quad_rectifier = QuadRectify(8, 32)
        self.relational_quad_rectifier = QuadRectify(2, 3, isotropic=False)
        self.grid_sampler = IndirectGridSample()

        self.recog_encoder = RecognitionTargetEncoder(
            charset=self.charset,
            input_size=[1024, 1920],
            sequence_length=32,
            amp_opt=2,
            combine_duplicates=False,
            is_train=False,
        )
        self.relation_encoder = RelationalTargetEncoder(input_size=[1024, 1920], amp_opt=2, is_train=False)

    def _load_charset(self):
        with open(self._model_dir / "charset.txt", "r", encoding="utf-8") as file:
            self.charset = json.load(file)

    def __call__(self, image, merge_level=DEFAULT_MERGE_LEVEL, visualize=False):
        """
        Performs OCR on a single image.

        Args:
            image (str | bytes | np.ndarray | Image.Image): The input image. Can be a:
                - file path (str)
                - base64 encoded string (bytes)
                - NumPy array (H, W, C)
                - In-memory byte stream (io.BytesIO)
            merge_level (str): The granularity of text merging ('word', 'sentence', 'paragraph').
            visualize (bool): If True, saves an annotated image.

        Returns:
            list: A list of prediction dictionaries.
        """
        image_tensor = self._load_image_to_tensor(image)

        predictions = self._process_tensor(image_tensor, merge_level)

        original_path = image if isinstance(image, str) and Path(image).is_file() else None
        if visualize:
            if original_path is None:
                raise ValueError("Visualization is only supported when the input is a file path.")
            self._save_annotated_image(original_path, predictions)

        return predictions

    def _load_image_to_tensor(self, image):
        """
        Loads an image from various sources and converts it to a standardized tensor.
        """
        if isinstance(image, str):
            image_path = Path(image)
            if not image_path.is_file():
                raise FileNotFoundError(f"Input string is not a valid file path: {image}")
            img_tensor = read_image(str(image_path), mode="RGB")

        elif isinstance(image, bytes):
            try:
                img_bytes = base64.b64decode(image)
                img_tensor = decode_image(torch.frombuffer(img_bytes, dtype=torch.uint8), mode="RGB")
            except (ValueError, TypeError, base64.binascii.Error) as e:
                raise ValueError("Input is not a valid base64-encoded image.") from e

        elif isinstance(image, np.ndarray):
            # PyTorch expects CHW, NumPy use HWC, so we permute
            if image.ndim == 2:  # Handle grayscale by stacking
                image = np.stack([image] * 3, axis=-1)
            # Handle RGBA images by stripping the alpha channel
            if image.shape[2] == 4:
                image = image[..., :3]
            img_tensor = torch.from_numpy(image).permute(2, 0, 1)

        elif isinstance(image, io.BytesIO):
            image.seek(0)
            img_bytes = image.getvalue()
            img_tensor = decode_image(torch.frombuffer(img_bytes, dtype=torch.uint8), mode="RGB")

        else:
            raise TypeError(
                f"Unsupported input type: {type(image)}. "
                "Supported types are file path (str), base64 (str/bytes), NumPy array, and io.BytesIO"
            )

        return convert_image_dtype(img_tensor, dtype=torch.float16)

    def _process_tensor(self, image_tensor, merge_level):
        """
        Runs the core OCR inference pipeline on a standardized image tensor.
        """
        if merge_level not in MERGE_LEVELS:
            raise ValueError(f"Invalid merge level: {merge_level}. Must be one of {MERGE_LEVELS}.")

        original_shape = image_tensor.shape[1:]
        padded_length = max(original_shape)

        padded_image = interpolate_and_pad(
            pad_to_square(image_tensor, padded_length, how="bottom_right").unsqueeze(0),
            PAD_COLOR,
            INFER_LENGTH,
        )

        with amp.autocast("cuda", enabled=True), torch.no_grad():
            det_conf, _, det_rboxes, det_feature_3 = self.detector(padded_image.cuda())

        with amp.autocast("cuda", enabled=True), torch.no_grad():
            e2e_det_conf = torch.sigmoid(det_conf)
            e2e_det_coords = rrect_to_quads(det_rboxes.float(), DETECTOR_DOWNSAMPLE)

            # FIXME: quad_non_maximal_suppression fails with batch size > 1
            all_quads = []
            all_confidence = []
            all_region_counts = []

            for idx in range(e2e_det_coords.shape[0]):
                quads, confidence, region_counts = quad_non_maximal_suppression(
                    e2e_det_coords[idx].unsqueeze(0),
                    e2e_det_conf[idx].unsqueeze(0),
                    prob_threshold=NMS_PROB_THRESHOLD,
                    iou_threshold=NMS_IOU_THRESHOLD,
                    kernel_height=2,
                    kernel_width=3,
                    max_regions=NMS_MAX_REGIONS,
                    verbose=False,
                )[:3]
                all_quads.append(quads)
                all_confidence.append(confidence)
                all_region_counts.append(region_counts)

            quads = torch.cat(all_quads, dim=0)
            confidence = torch.cat(all_confidence, dim=0)
            region_counts = torch.cat(all_region_counts, dim=0)

        if quads.shape[0] == 0:
            rec_rectified_quads = torch.empty(0, 128, 8, 32, dtype=torch.float32, device=padded_image.device)
            rel_rectified_quads = torch.empty(0, 128, 2, 3, dtype=torch.float32, device=padded_image.device)
        else:
            rec_rectified_quads = self.recognizer_quad_rectifier(
                quads.detach(), padded_image.shape[2], padded_image.shape[3]
            )
            rel_rectified_quads = self.relational_quad_rectifier(
                quads.cuda().detach(), padded_image.shape[2], padded_image.shape[3]
            )

            input_indices = region_counts_to_indices(region_counts, quads.shape[0])

            rec_rectified_quads = self.grid_sampler(det_feature_3.float(), rec_rectified_quads.float(), input_indices)
            rel_rectified_quads = self.grid_sampler(
                det_feature_3.float().cuda(),
                rel_rectified_quads,
                input_indices.cuda(),
            )

        if rec_rectified_quads.shape[0] == 0:
            rec_output = torch.empty(0, 32, 858, dtype=torch.float16, device=rec_rectified_quads.device)
            rec_features = torch.empty(0, 32, 256, dtype=torch.float16, device=rec_rectified_quads.device)
        else:
            with amp.autocast("cuda", enabled=True), torch.no_grad():
                rec_output, rec_features = self.recognizer(rec_rectified_quads.cuda())

        predictions = []

        if region_counts.sum() > 0:
            rel_output = self.relational(
                rel_rectified_quads.cuda(),
                quads.cuda(),
                region_counts.cpu(),
                rec_features.cuda(),
            )
            words, lines, line_var = (
                rel_output["words"],
                rel_output["lines"],
                rel_output["line_log_var_unc"],
            )

            with amp.autocast("cuda", enabled=True), torch.no_grad():
                words = [F.softmax(r, dim=1, dtype=torch.float32)[:, 1:] for r in words]

                output = {
                    "sequences": F.softmax(rec_output, dim=2, dtype=torch.float32),
                    "region_counts": region_counts,
                    "quads": quads,
                    "raw_detector_confidence": e2e_det_conf,
                    "confidence": confidence,
                    "relations": words,
                    "line_relations": lines,
                    "line_rel_var": line_var,
                    "fg_colors": None,
                    "fonts": None,
                    "tt_log_var_uncertainty": None,
                    "e2e_recog_features": rec_features,
                }

            quads = output["quads"]

            lengths = [padded_length / INFER_LENGTH] * region_counts.item()

            lengths_tensor = torch.tensor(lengths, dtype=torch.float32, device=quads.device).view(quads.shape[0], 1, 1)

            quads *= lengths_tensor

            # TODO: Incorporate the quad scale factor
            batch = self.recog_encoder.convert_targets_to_labels(output, image_size=None, is_gt=False)
            relation_batch = self.relation_encoder.convert_targets_to_labels(output, image_size=None, is_gt=False)

            for example, rel_example in zip(batch, relation_batch):
                example.relation_graph = rel_example.relation_graph
                example.prune_invalid_relations()

            for example in batch:
                if example.relation_graph is None:
                    continue
                for paragraph in example.relation_graph:
                    block = []
                    for line in paragraph:
                        for relational_idx in line:
                            block.append(example[relational_idx])
                    if block:
                        example.blocks.append(TextBlock(block))

            for example in batch:
                for text_region in example:
                    text_region.region = text_region.region.vertices

            for example in batch:
                boxes, texts, scores = parse_relational_results(example, level=merge_level)
                boxes, texts, scores = reorder_boxes(boxes, texts, scores, mode="top_left", dbscan_eps=10)

                orig_h, orig_w = original_shape

                if len(boxes) == 0:
                    boxes = ["nan"]
                    texts = ["nan"]
                    scores = ["nan"]
                else:
                    # Convert to numpy array and reshape to (N, 4, 2) for easier processing
                    boxes_array = np.array(boxes).reshape(-1, 4, 2)

                    # Divide X coordinates by orig_w and Y coordinates by orig_h
                    boxes_array[:, :, 0] = boxes_array[:, :, 0] / orig_w  # X coordinates
                    boxes_array[:, :, 1] = boxes_array[:, :, 1] / orig_h  # Y coordinates
                    boxes = boxes_array.astype(np.float16).tolist()

                for box, text, conf in zip(boxes, texts, scores):
                    if box == "nan":
                        break
                    predictions.append(
                        {
                            "text": text,
                            "confidence": conf,
                            "left": min(p[0] for p in box),
                            "upper": max(p[1] for p in box),
                            "right": max(p[0] for p in box),
                            "lower": min(p[1] for p in box),
                        }
                    )

        return predictions

    def _save_annotated_image(self, image_path, predictions):
        """Saves a copy of the image with bounding boxes overlaid."""
        output_path = os.path.splitext(image_path)[0] + "-annotated" + os.path.splitext(image_path)[1]

        pil_image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(pil_image)

        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

        img_width, img_height = pil_image.size

        color = (255, 0, 0)

        for pred in predictions:
            if isinstance(pred.get("left"), str) and pred["left"] == "nan":
                continue

            left = int(pred["left"] * img_width)
            right = int(pred["right"] * img_width)
            upper = int(pred["upper"] * img_height)
            lower = int(pred["lower"] * img_height)

            confidence = pred["confidence"]
            text = pred["text"]

            draw.rectangle([left, lower, right, upper], outline=color, width=2)

            display_text = f"{text}"
            conf_text = f"({confidence:.2f})"

            text_y = max(0, upper - 25)

            text_bbox = draw.textbbox((left, text_y), display_text, font=font)
            conf_bbox = draw.textbbox((left, text_y + 18), conf_text, font=small_font)

            draw.rectangle(
                [
                    text_bbox[0] - 2,
                    text_bbox[1] - 2,
                    text_bbox[2] + 2,
                    text_bbox[3] + 2,
                ],
                fill=(255, 255, 255, 180),
                outline=color,
            )
            draw.rectangle(
                [
                    conf_bbox[0] - 2,
                    conf_bbox[1] - 2,
                    conf_bbox[2] + 2,
                    conf_bbox[3] + 2,
                ],
                fill=(255, 255, 255, 180),
                outline=color,
            )

            draw.text((left, text_y), display_text, fill=color, font=font)
            draw.text((left, text_y + 18), conf_text, fill=color, font=small_font)

        pil_image.save(output_path)

        print(f"Annotated image saved to: {output_path}")
        print(
            f"Total predictions overlaid: {len([p for p in predictions if not (isinstance(p.get('left'), str) and p['left'] == 'nan')])}"
        )
