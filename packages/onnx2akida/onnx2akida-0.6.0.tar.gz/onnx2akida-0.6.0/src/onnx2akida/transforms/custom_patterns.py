#!/usr/bin/env python
# ******************************************************************************
# Copyright 2025 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
__all__ = ["get_custom_pattern_map"]

import os

from quantizeml.onnx_support import layers


def fold_mul_add_into_matmul(nodes, graph, tensor_ranges):
    # Simulate to fold Add/Mul in GEMM
    nodes = [node for node in nodes if node.op_type in ['Flatten', 'Gemm']]
    return layers.get_qgemm(nodes, graph, tensor_ranges)


def include_sub_op_into_rescale(nodes, graph, tensor_ranges):
    # Include Sub as one rescaling node
    return layers.get_input_quantizer(nodes, graph, tensor_ranges)


def get_custom_pattern_map():
    patterns_map = {}
    # Include experimental patterns if environment variable is set
    if os.environ.get("EXPERIMENTAL_PATTERNS", "0") == "1":
        patterns_map.update({
            ('Mul', 'Add', 'Transpose', 'Flatten', 'Gemm'): fold_mul_add_into_matmul,
            ('Mul', 'Sub', 'Mul', 'Pad', 'Transpose'): include_sub_op_into_rescale,
        })
    return patterns_map
