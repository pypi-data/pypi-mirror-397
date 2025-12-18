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
__all__ = ["convert_to_hybrid"]

import re
import tqdm
import akida
import onnx
import numpy as np
import warnings
from onnxscript import ir

from cnn2snn import convert as cnn2snn_convert
from quantizeml.onnx_support.layers.base_layer import IR_VERSION

from .sequences import search_cycles_on_model, split_model_on_sequences
from ..hybrid_model import HybridModel, get_ir_output_dtype
from ..compatibility_info import ModelCompatibilityInfo
from ..tools import (ensure_model_type, extract_model_from_tensor_names, is_convertible,
                     find_no_initializer_inputs, convert_model_to, ONNXExtractorModel)


def _find_tensors_by_error_msg(error, model):
    assert all(node.name != "" for node in model.nodes()), "node names are required."
    # Search tensor to split model by specific patterns in error message.
    error_msg = str(error)
    # Build a set of all node names in the model.
    node_names = [re.escape(node.name) for node in model.nodes()]
    # Create a regex pattern that matches any node name exactly.
    # Note name could be closed by quotes or ':'.
    pattern = re.compile(r"[\b'\"]?(" + "|".join(node_names) + r")[.\b'\":]+")
    # Find all node in the error message.
    matched_names = set(pattern.findall(error_msg))
    target_nodes = [node for node in model.nodes() if node.name in matched_names]
    if len(target_nodes) > 0:
        # Split model before and after target_node.
        input_names = find_no_initializer_inputs(target_nodes[0], model.model)
        output_names = target_nodes[0].output[:]
    else:
        warnings.warn(f"Node was not found in error: {error_msg}.", stacklevel=2)
        # Split model after first node.
        input_names = output_names = list(model.nodes()[0].output)
    return input_names, output_names


def _find_inbound_names(sub_model, oname_to_node):
    inbound_names = []
    for input_ in sub_model.input:
        if (inode := oname_to_node.get(input_.name, None)) is not None:
            inbound_names.append(inode.name)
    return inbound_names


def _rename_akida_input_layer(model, new_input_data_name):
    if model.layers[0].parameters.layer_type == akida.LayerType.InputData:
        model_dict = model.to_dict()
        model_dict["layers"][0]["name"] = new_input_data_name
        # Rename next layer with the new input data name.
        model_dict["layers"][1]["inbounds"][0] = new_input_data_name
        model = akida.model_from_dict(model_dict)
    return model


def _get_transpose_model(input_shape, ttype, name, channel_first=False):
    x = ir.Input("X", shape=ir.Shape(('N', *input_shape)), type=ttype)
    tape = ir.tape.Tape(ir.Graph(inputs=[x], outputs=[], nodes=[],
                                 opset_imports={"": 15}, name="transpose"))
    if len(input_shape) == 1:
        # Expand inputs to match with 4D shape.
        shape = [0, 1, 1, input_shape[0]] if channel_first else [0, input_shape[0], 1, 1]
        ir_shape = tape.initializer(ir.Tensor(np.array(shape, "int64"), name=f"{name}/shape"))
        y = tape.op("Reshape", [x, ir_shape], name=name)
    else:
        # Permute channels.
        perm = ir.AttrInt64s("perm", [0, 2, 3, 1] if channel_first else [0, 3, 1, 2])
        y = tape.op("Transpose", [x], attributes={"perm": perm}, name=name)
    # Build the model.
    tape.graph_like.outputs.append(y)
    ir_model = ir.Model(tape.graph_like, ir_version=IR_VERSION)
    return onnx.shape_inference.infer_shapes(ir.to_proto(ir_model))


def _get_flatten_model(ak_layer):
    input_shape = f"[N, {', '.join([str(x) for x in ak_layer.output_dims])}]"
    output_shape = f"[N, {np.prod(ak_layer.output_dims)}]"
    dtype = str(get_ir_output_dtype(ak_layer)).lower()
    assert "int" in dtype, "Only integer models are allowed."
    model = onnx.parser.parse_model(f"""< ir_version: 10, opset_import: ["" : 15] >
            flatten ({dtype}{input_shape} X) => ({dtype}{output_shape} Y){{Y = Flatten(X)}}""")
    model.graph.node[0].name = f"{ak_layer.name}/flatten"
    return model


def _add_submodel(hybrid_model, sub_model, inbound_names):
    # Check if sub_model requires transpose nodes.
    for idx, iname in enumerate(inbound_names):
        layer = hybrid_model.get_layer(iname)
        transpose_params = {"name": f"{layer.name}/transpose"}
        layer_names = [ly.name for ly in hybrid_model.layers]
        if isinstance(layer, akida.Layer):
            if isinstance(sub_model, akida.Model):
                # Nothing to do: links between Akida models are possible.
                continue
            # Define parameters to create transpose.
            transpose_params.update(dict(input_shape=layer.output_dims,
                                         ttype=get_ir_output_dtype(layer),
                                         channel_first=False))
        else:
            if isinstance(sub_model, onnx.ModelProto):
                # Nothing to do: links between ONNX models are possible.
                continue
            # Define parameters to create transpose.
            transpose_params.update(dict(input_shape=layer.outputs[0].shape[1:],
                                         ttype=layer.outputs[0].type,
                                         channel_first=True))

        # Create a new transpose if it does not exist (avoiding creating pointless transpose).
        if transpose_params["name"] not in layer_names:
            hybrid_model._add(_get_transpose_model(**transpose_params), [iname])
        # Update inbound with new transpose.
        inbound_names[idx] = transpose_params["name"]

    # Insert sub_model in hybrid model.
    hybrid_model._add(sub_model, inbound_names)


def cnn2snn_convert_and_map(model, device=None, input_data_name=None, **device_kwargs):
    """Generates an Akida model based on an ONNX quantizeml model.

    Args:
        model (obj:`onnx.ModelProto`): a ONNX model to convert.
        device (akida.Device, optional): the Akida device to map the Akida sub models.
            Defaults to None.
        input_data_name (str, optional): fix InputData name. Defaults to None.
        device_kwargs (dict, optional): parameters for computing device if device = None.
            Defaults to {}.

    Returns:
        akida.Model: the generated Akida model.
    """
    akida_model = cnn2snn_convert(model)

    # Rename InputData if required.
    if input_data_name:
        akida_model = _rename_akida_input_layer(akida_model, input_data_name)

    # Compute device.
    map_on_device = akida.compute_min_device(
        akida_model, **device_kwargs) if device is None else device

    # Map model.
    akida_model.map(map_on_device, mode=akida.mapping.MapMode.Minimal, hw_only=False)

    # Check all sequences were mapped in hardware.
    if sw := [seq for seq in akida_model.sequences if seq.backend != akida.BackendType.Hardware]:
        # Throws error on the first SW sequence in a different format:
        # 1. If it is the first sequence, raise native error.
        if (first_sequence := sw[0]) == akida_model.sequences[0]:
            akida_model.map(map_on_device, mode=akida.MapMode.Minimal, hw_only=True)
        # 2. Show sequence location on the model, allowing to find it by the search node algorithm.
        passes = first_sequence.passes
        raise RuntimeError(f"{passes[0].layers[0].name} -> {passes[-1].layers[-1].name}: "
                           "could not find a compatible sequence.")
    return akida_model


@ensure_model_type
def search_convertible_sequences(model, device=None, **device_kwargs):
    """Identify and return all fully convertible sequences in a quantized model.

    This function analyzes the model graph to find cycles (loops) and filter out them when
    they are not fully convertible. Finally, the function splits the model into sequences
    returning a list of sub-models that are suitable for conversion.

    Args:
        model (Any): the quantized ONNX model to analyze.
        device (akida.Device, optional): the Akida device to map the Akida sub models.
            Defaults to None.
        device_kwargs (dict, optional): parameters for computing device if device = None.
            Defaults to {}.

    Returns:
        list: a list of ONNX sub-models.
    """
    # Search cycles in the model.
    loop_sequences = search_cycles_on_model(model)

    # Process cycles in several steps:
    filtered_loop_sequences = []
    for sub_model in loop_sequences:
        # * removes non-quantized cycles completely
        if not all(is_convertible(n) for n in sub_model.graph.node):
            continue
        # * remove cycles with full branches (non-mappable)
        merged_node = sub_model.graph.node[-1]
        graph_input_names = [x.name for x in sub_model.graph.input]
        if len(set(merged_node.input[:]).intersection(graph_input_names)) == 0:
            continue
        filtered_loop_sequences.append(sub_model)
    # * merge all 'sequential' cycles
    # Note we can compare cycles by index since search_cycles returns them in topological order.
    idx = 0
    while idx < len(filtered_loop_sequences) - 1:
        first_sub_model = filtered_loop_sequences[idx]
        second_sub_model = filtered_loop_sequences[idx + 1]
        if (first_sub_model.graph.output[0].name == second_sub_model.graph.input[0].name):
            try:
                new_model = extract_model_from_tensor_names(model,
                                                            [first_sub_model.graph.input[0].name],
                                                            [second_sub_model.graph.output[0].name])
                new_model = convert_model_to(new_model, new_type=onnx.ModelProto)
            except Exception:
                idx += 1
            else:
                filtered_loop_sequences.insert(idx, new_model)
                filtered_loop_sequences.remove(first_sub_model)
                filtered_loop_sequences.remove(second_sub_model)
        else:
            idx += 1

    # Check which sub_model is fully convertible.
    skip_outbounds = {}
    inames_to_nodes = model.input_name_to_nodes()
    onames_to_node = model.output_name_to_node()
    loop_sequences = []
    for sub_model in filtered_loop_sequences:
        try:
            # To avoid conversion issues, cycle must contain one quantized node
            # at the input and at the output. Reasons:
            # - InputData cannot be a split node and
            # - merge node develops into next quantized node
            parent_node = onames_to_node[sub_model.graph.input[0].name]
            child_nodes = inames_to_nodes[sub_model.graph.output[0].name]
            if not (is_convertible(parent_node) and is_convertible(child_nodes[0])):
                continue
            new_input_name = find_no_initializer_inputs(parent_node, model.model)
            if len(new_output_name := [n.output[0] for n in child_nodes]) != 1:
                # We avoid converting cycles with multiple outputs.
                continue
            model_to_convert = extract_model_from_tensor_names(model,
                                                               new_input_name,
                                                               new_output_name)
            cnn2snn_convert_and_map(model_to_convert.model, device, **device_kwargs)
        except Exception:
            continue
        else:
            # Store the link between input_name and merge_node to compute sequences.
            loop_sequences.append(model_to_convert.model)
            skip_outbounds[sub_model.graph.input[0].name] = sub_model.graph.output[0].name

    # Split model in sequences.
    base_sequences = split_model_on_sequences(model, skip_outbounds=skip_outbounds)

    # Verify sequences are fully convertible. If this is not the case, divide the sub_models
    # based on loop_sequences.
    sequences = []
    while len(base_sequences) > 0:
        sub_model = base_sequences.pop(0)
        if all(is_convertible(n) for n in sub_model.graph.node):
            try:
                cnn2snn_convert_and_map(sub_model, device, **device_kwargs)
            except Exception:
                target_loop = None
                for loop_model in loop_sequences:
                    if all(n in sub_model.graph.node for n in loop_model.graph.node):
                        target_loop = loop_model
                        break

                # Split sub_model with target_loop to ensure that at least it is convertible.
                if target_loop is not None:
                    edges_to_split = ((sub_model.graph.input, target_loop.graph.input),
                                      (target_loop.graph.output, sub_model.graph.output))
                    for input_, output_ in edges_to_split:
                        input_names = [i.name for i in input_]
                        output_names = [o.name for o in output_]
                        e_model = extract_model_from_tensor_names(model, input_names, output_names)
                        if len(e_model.nodes()) > 0:
                            # Add extracted model into the queue to analyze if it contains
                            # another loop_sequence in next iterations.
                            base_sequences.append(e_model.model)

                    # Replace sub_model by target_loop (model to add in sequences list).
                    sub_model = target_loop
        sequences.append(sub_model)
    return sequences


@ensure_model_type
def convert_sequential(qmodel, device=None, hybrid_model=None, oname_to_node=None,
                       compatibility_info=None, **device_kwargs):
    """Recursively converts a quantized ONNX model into a HybridModel.

    This function attempts to convert the provided quantized ONNX model into an Akida model using
    `cnn2snn.convert`. If the conversion fails, it splits the model in several ones and recursively
    tries to convert each sequence independently. Convertible sequences are added as Akida models,
    while non-convertible ones are retained as ONNX models within the HybridModel.

    The function also manages necessary input/output format conversions (e.g., transpose) to ensure
    compatibility between models.

    Args:
        qmodel (Any): the quantized ONNX model to convert.
        device (akida.Device, optional): the Akida device to map the Akida sub models.
            If not present, compute one. Defaults to None.
        hybrid_model (HybridModel, optional): an existing HybridModel to which sub-models
            will be added. If None, a new HybridModel is created. Defaults to None.
        oname_to_node (dict, optional): a mapping from output tensor names to ONNX nodes.
            If None, it is initialized from the provided qmodel. Defaults to None.
        compatibility_info (ModelCompatibilityInfo, optional): an existing ModelCompatibilityInfo
            object to accumulate incompatibility information during conversion and mapping.
            If None, incompatibilities are not recorded. Defaults to None.
        device_kwargs (dict, optional): parameters for computing device if device = None.
            Defaults to {}.

    Returns:
        HybridModel: a hybrid model containing both Akida and ONNX sub-models, with appropriate
            format conversions and connections to preserve the original model's topology.
    """
    def _update_compatibility_info(sub_model, ex):
        if compatibility_info is None:
            # Nothing to record.
            return
        reason, stage = str(ex), "Mapping"
        if "Cannot convert" in reason:
            stage = "Conversion"
            reason = str(ex.__cause__)
        node_sequence = sub_model.nodes()[:]
        compatibility_info._set_incompatibility(node_sequence=node_sequence,
                                                stage=stage,
                                                faulty_node=node_sequence[0].name,
                                                reason=reason)

    if oname_to_node is None:
        oname_to_node = qmodel.output_name_to_node()
    if hybrid_model is None:
        hybrid_model = HybridModel()
    convert_kwargs = {"device": device, **device_kwargs}
    kwargs = {"oname_to_node": oname_to_node,
              "compatibility_info": compatibility_info,
              **convert_kwargs}

    # Nothing to convert.
    if len(qmodel.nodes()) == 0:
        return hybrid_model

    # Analyze error source when converting.
    try:
        # Create a new InputData name since HybridModel cannot contain layers with duplicate names.
        input_name = f"{qmodel.input[0].name}/InputData"
        idx = len(list(filter(lambda ly: input_name in ly.name, hybrid_model.layers)))
        input_name = f"{input_name}_{idx}"
        ak_model = cnn2snn_convert_and_map(
            qmodel.model, input_data_name=input_name, **convert_kwargs)
    except Exception as e:
        # End condition: conversion failure in single-node model.
        if len(qmodel.nodes()) == 1:
            _add_submodel(hybrid_model, qmodel.model, _find_inbound_names(qmodel, oname_to_node))
            _update_compatibility_info(qmodel, e)
            return hybrid_model
        # Try to parse the node which produces the error.
        split_before, split_after = _find_tensors_by_error_msg(e, qmodel)
        # Split model into three parts:
        model_list = [
            extract_model_from_tensor_names(qmodel, output_names=split_before),
            extract_model_from_tensor_names(qmodel, split_before, split_after),
            extract_model_from_tensor_names(qmodel, input_names=split_after)
        ]
        # Try to convert each sub-model.
        for sub_model in model_list:
            convert_sequential(sub_model, hybrid_model=hybrid_model, **kwargs)
    else:
        # Add the model to the HybridModel.
        _add_submodel(hybrid_model, ak_model, _find_inbound_names(qmodel, oname_to_node))

        # Adds a flatten model if the original output is 2D since Akida outputs are 4D.
        if len(qmodel.output[0].type.tensor_type.shape.dim) == 2:
            flatten = _get_flatten_model(ak_model.layers[-1])
            hybrid_model._add(flatten, [ak_model.layers[-1].name])

            # Update outbound names for the next model.
            oname_to_node[qmodel.output[0].name] = flatten.graph.node[0]
    return hybrid_model


@ensure_model_type
def convert_to_hybrid(qmodel, device=None, *, enable_hwpr=False,
                      sram_size=None, minimal_memory=False, initial_num_nodes=36):
    """Converts a quantized ONNX model into a HybridModel containing Akida and ONNX sub-models.

    This function splits the input quantized model into convertible sequences, attempts to convert
    and map each fully quantized sequence to an Akida model and adds it to the HybridModel.
    Sequences that cannot be converted and mapped to Akida are added on ONNX domain. The function
    also manages inbound connections between sub-models to preserve the original model's topology.

    When device is not provided, a mimimal device is computed independently for each akida
    compatible model, then a common device is computed and used to map the HybridModel.

    Args:
        qmodel (Any): the quantized ONNX model to convert.
        device (akida.Device, optional): the Akida device to map the Akida sub models.
            Defaults to None.
        enable_hwpr (bool, optional): if True, the device is computed assuming partial
            reconfiguration. Used when `device` is None. Defaults to False.
        sram_size (akida.NP.SramSize, optional): Size of shared SRAM available inside the mesh.
            Ignored when `minimal_memory` is True. Used when `device` is None. Defaults to None.
        minimal_memory (bool, optional): if True, computes and sets the minimal required
            inputs and weights memory for the device.  Used when `device` is None.
            Defaults to False.
        initial_num_nodes (int, optional): the initial number of nodes with which to compute
            the base device. Used when `device` is None. Defaults to 36.

    Returns:
        HybridModel: a hybrid model containing Akida and ONNX sub-models.
    """
    if device is not None and (enable_hwpr or sram_size is not None or minimal_memory
                               or initial_num_nodes != 36):
        warnings.warn(
            "When 'device' is provided, the parameters 'enable_hwpr', 'sram_size', "
            "'minimal_memory', and 'initial_num_nodes' are ignored. Continuing execution."
        )
    device_params = dict(device=device,
                         enable_hwpr=enable_hwpr,
                         sram_size=sram_size,
                         minimal_memory=minimal_memory,
                         initial_num_nodes=initial_num_nodes)

    # Split model in (un)convertible sequences.
    sequences = search_convertible_sequences(qmodel, **device_params)

    # Sort sequences topologically.
    sequences = sorted(sequences, key=lambda x: qmodel.nodes()[:].index(x.graph.node[0]))

    # Convert sequences into Akida (when possible) and add them to the HybridModel.
    model = HybridModel()
    compatibility_info = ModelCompatibilityInfo(qmodel.model)
    oname_to_node = qmodel.output_name_to_node()
    for sub_model in tqdm.tqdm(sequences, desc="Converting"):
        sub_model = ONNXExtractorModel(sub_model)
        # Convert sub_model to Akida if all nodes are convertible.
        if all(is_convertible(n) for n in sub_model.nodes()):
            # Note we transfer extractor to speed runtime.
            sub_model.extractor = qmodel.extractor
            convert_sequential(sub_model,
                               hybrid_model=model,
                               oname_to_node=oname_to_node,
                               compatibility_info=compatibility_info,
                               **device_params)
        else:
            # Add non-convertible sub_models.
            _add_submodel(model, sub_model.model, _find_inbound_names(sub_model, oname_to_node))

    # Sort outputs to align them with quantized model order.
    model._assign_outputs_order([oname_to_node[out.name].name for out in qmodel.output])

    # Post mapping to map all Akida sub models on a common device.
    # Applied only when using minimum device
    if device is None and len(model.akida_models) != 0:
        device = akida.compute_common_device(model.akida_models)
        model.map(device, mode=akida.MapMode.Minimal)

    return model, compatibility_info
