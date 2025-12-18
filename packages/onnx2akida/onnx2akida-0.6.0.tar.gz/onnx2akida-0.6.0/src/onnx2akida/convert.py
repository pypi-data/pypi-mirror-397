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

__all__ = ["convert", "print_report"]

import onnx
import onnx_ir as ir
from onnx_ir.passes.common import NameFixPass

from quantizeml.onnx_support.quantization import custom_pattern_scope
from quantizeml.onnx_support.quantization.shape import set_model_shape
from quantizeml.onnx_support.quantization.transforms import sanitize

from .compatibility_info import ModelCompatibilityInfo
from .pipeline import quantize, convert_to_hybrid
from .tools import (ensure_model_type, extract_model_from_tensor_names, convert_model_to,
                    experimental_context, ONNXExtractorModel)
from .transforms import get_custom_pattern_map


def _match_qnode_on_model(qnode, qmodel, float_model):
    # Search node input names.
    input_names = []
    for node in qmodel.get_parents(qnode):
        if node.op_type == "InputQuantizer":
            # Rename qnode.input to match with a tensor in float_model.
            input_names.append(node.input[0])
        else:
            input_names.append(node.output[0])

    # Search node output names.
    output_name = qnode.output[0]
    if len(children := qmodel.get_children(qnode)) == 1 and children[0].op_type == "Dequantizer":
        # Rename qnode.output to match with model.
        output_name = children[0].output[0]

    # Search all nodes in float_model between inputs and outputs.
    # TODO: improve this search
    return extract_model_from_tensor_names(float_model, input_names, [output_name]).nodes()[:]


def _get_compatibility_info(node, compatibility):
    for sequence in compatibility.incompatible_sequences:
        if any(seq_node.name == node.name for seq_node in sequence.nodes):
            return sequence


def _set_compatibility_info(new_sequence, compatibility):
    if any(new_sequence.faulty_node == node.name for node in compatibility.incompatible_nodes):
        # Sequences was already added in compatibility.
        return

    # Add sequence into compatibility info.
    compatibility.incompatible_sequences.append(new_sequence)


@ensure_model_type
def convert(model,
            input_shape=None,
            input_dtype="uint8",
            enable_experimental=True,
            device=None,
            enable_hwpr=False,
            sram_size=None,
            minimal_memory=False,
            initial_num_nodes=36):
    """Check ONNX model compatibility with Akida and convert the model into a HybridModel.

    Args:
        model (onnx.ModelProto): The ONNX model.
        input_shape (Iterable, optional): An iterable specifying the new model input shape
            excluding batch dimension. Defaults to None.
        input_dtype (np.dtype or str, optional): expected model input format. If given as a string,
            should follow numpy string type requirements. Defaults to 'uint8'.
        enable_experimental (bool, optional): Enable or Disable experimental patterns context.
            Defaults to True.
        device (akida.Device, optional): the Akida device to map the Akida sub models.
            Defaults to None.
        enable_hwpr (bool, optional): if True, the device is computed assuming partial
            reconfiguration. Used when `device` is None. Defaults to False.
        sram_size (akida.NP.SramSize, optional): Size of shared SRAM available inside the mesh.
            Ignored when `minimal_memory` is True. Used when `device` is None. Defaults to None.
        minimal_memory (bool, optional): if True, computes and sets the minimal required
            inputs and weights memory for the device.  Used when `device` is None.
            Defaults to False.
        initial_num_nodes (int, optional): The initial number of nodes that will be used to compute
            the base device. Defaults to 36.

    Returns:
        HybridModel, ModelCompatibilityInfo: converted model and
        object containing information about model compatibility.
    """
    # Check model validity.
    try:
        model.check_model()
    except onnx.checker.ValidationError as e:
        raise ValueError(f"Invalid ONNX model: {e}")
    # Sanitize the model, since _check_akida_compatibility required it.
    model = set_model_shape(model.clone(), input_shape=input_shape)
    sanitized_model = sanitize(model)
    # Convert to extractor model to handle compatibility info.
    sanitized_model = convert_model_to(sanitized_model, new_type=ONNXExtractorModel)
    # Generates node names to better understand incompatibilities.
    # Use onnx_ir NameFixPass to fix when there are duplicates
    ir_pass = NameFixPass()
    sanitized_model.model = ir.to_proto(ir_pass(ir.from_proto(sanitized_model.model)).model)
    # Quantize model.
    with experimental_context(enable_experimental), custom_pattern_scope(get_custom_pattern_map()):
        qmodel, q_compatibility_info = quantize(sanitized_model, input_dtype=input_dtype)

    # Convert model.
    hybrid_model, ak_compatibility_info = convert_to_hybrid(qmodel,
                                                            device=device,
                                                            enable_hwpr=enable_hwpr,
                                                            sram_size=sram_size,
                                                            minimal_memory=minimal_memory,
                                                            initial_num_nodes=initial_num_nodes)

    # Merge compatibilities into just one.
    compatibility_info = ModelCompatibilityInfo(sanitized_model.model)
    for node in sanitized_model.nodes():
        if incompatible_seq := _get_compatibility_info(node, q_compatibility_info):
            # Transfer incompatibility to general info.
            _set_compatibility_info(incompatible_seq, compatibility_info)
        elif incompatible_seq := _get_compatibility_info(node, ak_compatibility_info):
            # Match node sequence in float model before to set in general info.
            node_sequence = [_match_qnode_on_model(qnode, qmodel, sanitized_model)
                             for qnode in incompatible_seq.nodes]
            # Transfer incompatibility to general info.
            compatibility_info._set_incompatibility(node_sequence=sum(node_sequence, []),
                                                    stage=incompatible_seq.stage,
                                                    faulty_node=incompatible_seq.faulty_node,
                                                    reason=incompatible_seq.reason)
    return hybrid_model, compatibility_info


def print_report(compatibility_info, hybrid_model):
    """Prints a report of the model compatibility with Akida.

    Args:
        compatibility_info (ModelCompatibilityInfo): The compatibility information.
        hybrid_model (HybridModel): The converted hybrid model.
    """
    # Color codes
    RESET = "\033[0m"
    RED = "\033[1;31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    GREEN = "\033[1;32m"

    incompatibilities = compatibility_info.incompatibilities

    if incompatibilities:
        lines = [
            f"\n{RED}Set of Incompatible op_types:{RESET} {YELLOW}"
            f"{compatibility_info.incompatible_op_types}{RESET}",
            f"{RED}List of Incompatibilities:{RESET}",
        ]

        for incompatibility in incompatibilities:
            seq_desc = ", ".join(
                f"{n['name']}({YELLOW}op_type={n['op_type']}{RESET})"
                for n in incompatibility["node_sequence"]
            )
            lines.append(f" ❌ Node sequence: [{seq_desc}]")
            lines.append(f"     • {CYAN}Stage{RESET}: {incompatibility['stage']}")
            lines.append(f"     • {CYAN}Faulty node{RESET}: {incompatibility['faulty_node']}")
            lines.append(f"     • {CYAN}Reason{RESET}: {incompatibility['reason']}\n")

        print("\n".join(lines))

    print(
        f"[INFO]: Percentage of nodes compatible with akida: "
        f"{GREEN}{compatibility_info.compatibility_percentage:.4f} %{RESET}"
    )

    if data_movement := hybrid_model.compute_data_movement():
        print(f"\n{RED}List of backends exchanges:{RESET}")
        for data in data_movement:
            size_kb = data['size'] / 1024
            print(f" • {CYAN}{data['type']}{RESET} at layer "
                  f"{YELLOW}{data['layer'].name}{RESET}: {GREEN}{size_kb:.3f} KB{RESET}")
        print()
