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

__all__ = ["remove_pointless_quantizers"]

import numpy as np

from quantizeml.onnx_support.quantization import ONNXModel
from quantizeml.onnx_support.graph_tools import get_tensor_dtype

from ..tools import rename_tensors


def _find_dequantizer_input_quantizers_to_remove(qmodel):
    nodes_to_remove = []
    for dequantizer in qmodel.nodes():
        if (dequantizer.op_type == "Dequantizer" and
                (children := qmodel.get_children(dequantizer))):
            # The nodes are removable if:
            # * all children are InputQuantizer
            if not all(child.op_type == "InputQuantizer" for child in children):
                continue

            valid_sequence = True
            if (deq_vi := qmodel.find_value_info_by_name(dequantizer.input[0])) is None:
                continue
            deq_dtype = get_tensor_dtype(deq_vi)
            deq_scale = qmodel.get_variable(dequantizer.input[1])
            for input_quantizer in children:
                # * Dequantizer input type is the same than InputQuantizer output type
                if (iq_vi := qmodel.find_value_info_by_name(input_quantizer.output[0])) is None:
                    valid_sequence = False
                    break
                valid_sequence &= deq_dtype == get_tensor_dtype(iq_vi)
                # * scales are the same
                valid_sequence &= np.all(deq_scale == qmodel.get_variable(input_quantizer.input[1]))
                # * InputQuantizer zero point is zero
                valid_sequence &= np.all(qmodel.get_variable(input_quantizer.input[2]) == 0)

            # Store nodes to remove.
            if valid_sequence:
                nodes_to_remove.append((dequantizer, children))
    return nodes_to_remove


def remove_pointless_quantizers(qmodel):
    """Removes pointless Dequantizer and InputQuantizer from a quantized ONNX model.

    Specifically, it eliminates consecutive Dequantizer and InputQuantizer nodes, if:
    - there are no intermediate ops between Dequantizer and InputQuantizer
    - Dequantizer input type match with InputQuantizer output type
    - scales between Dequantizer and InputQuantizer are the same
    - InputQuantizer has zero point equal to zero

    Args:
        qmodel (ONNXModel): The ONNX model to be processed.
    """
    assert isinstance(qmodel, ONNXModel)
    tensor_map = {}
    nodes_to_remove = []

    # Check if there are nodes to remove
    if len(nodes_to_remove := _find_dequantizer_input_quantizers_to_remove(qmodel)) == 0:
        return

    # Update nodes
    flat_nodes_to_remove = []
    for dequantizer, children in nodes_to_remove:
        flat_nodes_to_remove.append(dequantizer)
        for input_quantizer in children:
            # Replace InputQuantizer output by Dequantizer input
            qmodel.replace_input_of_all_nodes(input_quantizer.output[0], dequantizer.input[0])

            # Rename Dequantizer input (previous node output) to be able to match QNode to
            # the float sequence when computing compatibility
            tensor_map[dequantizer.input[0]] = dequantizer.output[0]

            # Remove InputQuantizer
            flat_nodes_to_remove.append(input_quantizer)

    qmodel.remove_nodes(flat_nodes_to_remove, update_graph=True)
    rename_tensors(qmodel, tensor_map, inplace=True)

    # Clear value infos to infer new types
    qmodel.graph().ClearField("value_info")
    qmodel.check_model()
