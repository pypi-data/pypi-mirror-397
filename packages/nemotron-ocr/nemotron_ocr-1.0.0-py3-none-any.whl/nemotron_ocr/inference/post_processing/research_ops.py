# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def parse_relational_results(result, level="sentence"):
    """
    Parses the relational results from the OCR model.
    Supported levels:
    - "word" returns a list of words, each with a bounding box, text, and confidence.
    - "sentence" returns a list of sentences, each with a bounding box, text, and confidence.
    - "paragraph" returns a list of paragraphs, each with a bounding box, text, and confidence.

    Args:
        result (object): The result object from the OCR model.
        level (str, optional): The level to parse the results to. Defaults to "sentence".

    Returns:
        np array [N x 4 x 2]: The bounding boxes of the OCR results.
        np array [N]: The text of the OCR results
        np array [N]: The confidence scores of the OCR results
    """
    if level not in ["word", "sentence", "paragraph"]:
        raise ValueError(
            f"Invalid level: {level}. Supported levels are 'word', 'sentence', and 'paragraph'."
        )
    results = []
    for block_ids in result.relation_graph:
        sentences = []
        for sentence_ids in block_ids:
            regions = [result.regions[idx] for idx in sentence_ids]
            bboxes = [region.region.numpy() for region in regions]
            texts = [region.text for region in regions]
            confs = [region.confidence for region in regions]

            if level == "word":
                for bbox, text, conf in zip(bboxes, texts, confs):
                    results.append(
                        {
                            "bbox": bbox,
                            "text": text,
                            "confidence": conf,
                        }
                    )
            else:
                bboxes = np.stack(bboxes)
                xmin = bboxes[:, :, 0].min().item()
                ymin = bboxes[:, :, 1].min().item()
                xmax = bboxes[:, :, 0].max().item()
                ymax = bboxes[:, :, 1].max().item()

                sentences.append(
                    {
                        "bbox": [
                            [xmin, ymin],
                            [xmax, ymin],
                            [xmax, ymax],
                            [xmin, ymax],
                        ],
                        "text": " ".join(texts),
                        "confidence": np.mean(confs),
                    }
                )
        if level == "word":
            pass
        elif level == "sentence":
            results += sentences
        else:
            bboxes = np.stack([s["bbox"] for s in sentences])
            texts = [s["text"] for s in sentences]
            confs = [s["confidence"] for s in sentences]
            xmin = bboxes[:, :, 0].min().item()
            ymin = bboxes[:, :, 1].min().item()
            xmax = bboxes[:, :, 0].max().item()
            ymax = bboxes[:, :, 1].max().item()
            results.append(
                {
                    "bbox": [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]],
                    "text": " ".join(texts),
                    "confidence": np.mean(confs),
                }
            )

    boxes = np.array([r["bbox"] for r in results])
    texts = np.array([r["text"] for r in results])
    confidences = np.array([r["confidence"] for r in results])
    return boxes, texts, confidences


def reorder_boxes(boxes, texts, confs, mode="center", dbscan_eps=10):
    """
    Reorders the boxes in reading order.
    If mode is "center", the boxes are reordered using bbox center.
    If mode is "top_left", the boxes are reordered using the top left corner.
    If dbscan_eps is not 0, the boxes are reordered using DBSCAN clustering.

    Args:
        boxes (np array [n x 4 x 2]): The bounding boxes of the OCR results.
        texts (np array [n]): The text of the OCR results.
        confs (np array [n]): The confidence scores of the OCR results.
        mode (str, optional): The mode to reorder the boxes. Defaults to "center".
        dbscan_eps (float, optional): The epsilon parameter for DBSCAN. Defaults to 10.

    Returns:
        np array [n x 4 x 2]: The reordered bounding boxes.
        np array [n]: The reordered texts.
        np array [n]: The reordered confidence scores.
    """
    df = pd.DataFrame(
        [[b, t, c] for b, t, c in zip(boxes, texts, confs)],
        columns=["bbox", "text", "conf"],
    )

    if mode == "center":
        df["x"] = df["bbox"].apply(lambda box: (box[0][0] + box[2][0]) / 2)
        df["y"] = df["bbox"].apply(lambda box: (box[0][1] + box[2][1]) / 2)
    elif mode == "top_left":
        df["x"] = df["bbox"].apply(lambda box: (box[0][0]))
        df["y"] = df["bbox"].apply(lambda box: (box[0][1]))

    if dbscan_eps:
        do_naive_sorting = False
        try:
            dbscan = DBSCAN(eps=dbscan_eps, min_samples=1)
            dbscan.fit(df["y"].values[:, None])
            df["cluster"] = dbscan.labels_
            df["cluster_centers"] = df.groupby("cluster")["y"].transform("mean").astype(int)
            df = df.sort_values(["cluster_centers", "x"], ascending=[True, True], ignore_index=True)
        except ValueError:
            do_naive_sorting = True
    else:
        do_naive_sorting = True

    if do_naive_sorting:
        df["y"] = np.round((df["y"] - df["y"].min()) // 5, 0)
        df = df.sort_values(["y", "x"], ascending=[True, True], ignore_index=True)

    bboxes = [p.tolist() for p in df["bbox"].values.tolist()]
    texts = df["text"].values.tolist()
    confs = df["conf"].values.tolist()
    return bboxes, texts, confs
