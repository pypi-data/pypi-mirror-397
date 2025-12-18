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
__all__ = ["find_nodes_by_op", "find_no_initializer_inputs", "is_quantized", "is_convertible"]

from quantizeml.onnx_support.layers.base_layer import BRN_OPSET


def find_nodes_by_op(model, op_type):
    return [node for node in model.graph.node if node.op_type == op_type]


def find_no_initializer_inputs(node, model):
    initializer_names = [x.name for x in model.graph.initializer]
    return set([x for x in node.input if x not in initializer_names and len(x)])


def is_quantized(node):
    """Checks if a given node is quantized.

    Args:
        node (onnx.NodeProto): the node to check.

    Returns:
        bool: True if the node is quantized, False otherwise.
    """
    return (node.domain == BRN_OPSET.domain and
            ("Quantized" in node.op_type or node.op_type in ("InputQuantizer", "Dequantizer")))


def is_convertible(node):
    """Checks if a given node is convertible.

    Args:
        node (onnx.NodeProto): the node to check.

    Returns:
        bool: True if the node is convertible, False otherwise.
    """
    # Reject InputQuantizer and Dequantizer nodes to process it in CPU.
    return is_quantized(node) and node.op_type not in ("InputQuantizer", "Dequantizer")
