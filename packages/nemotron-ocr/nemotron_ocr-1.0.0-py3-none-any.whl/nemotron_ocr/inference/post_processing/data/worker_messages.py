# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

class WorkerMessage:
    def __init__(self):
        pass

    ####
    # Pickle methods
    ####
    def __getstate__(self):
        state = dict()
        self.build_state(state)
        return state

    def __setstate__(self, state):
        self.update_state(state)

    ####

    def build_state(self, state):
        pass

    def update_state(self, state):
        for k, v in state.items():
            setattr(self, k, v)


class TargetEncoderMessage(WorkerMessage):
    def __init__(self, name):
        self.name = name

    def build_state(self, state):
        state["name"] = self.name
