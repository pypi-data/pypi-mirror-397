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
__all__ = ["quantize"]

import io
import re
import warnings
from contextlib import redirect_stdout

import numpy as np
import tqdm
import onnx_ir as ir
from onnx_ir.passes.common import NameFixPass
from onnxruntime.quantization.calibrate import TensorData
from quantizeml.models import QuantizationParams, quantization
from quantizeml.onnx_support.graph_tools import infer_partial_io
from quantizeml.onnx_support.quantization.quantize import calibrate
from quantizeml.onnx_support.quantization.quantize import quantize_calibrated as qml_quantize
from quantizeml.onnx_support.quantization.transforms import insert_rescaling, sanitize
from quantizeml.onnx_support.random import generate_onnx_random_samples
from quantizeml.onnx_support.quantization.shape import set_model_shape

from ..compatibility_info import ModelCompatibilityInfo
from ..tools import (ONNXExtractorModel, ensure_model_type, convert_model_to,
                     extract_model_from_tensor_names, is_quantized, rename_tensors, replace_graph,
                     extract_nodes_from_tensor_names)
from ..transforms import remove_pointless_quantizers
from .sequences import search_cycles_on_model, split_model_on_sequences

_WARNINGS_TO_BE_HANDLE_AS_ERRORS = ["The following nodes were not quantized",
                                    "Impossible to quantize"]


def get_tensors_range(model):
    """Generates calibration tensor ranges for an ONNX model using random samples.

    This function creates random input samples for the model and performs model calibration
    to obtain the value ranges for each tensor.

    Args:
        model (onnx.ModelProto): the ONNX model to calibrate.

    Returns:
        TensorsData: An object containing the calibration ranges for each tensor in the model.
    """
    # Generate the random samples.
    samples = generate_onnx_random_samples(model.graph)[model.graph.input[0].name]
    if np.issubdtype(samples.dtype, np.floating):
        # Rescale samples to [-128, 127].
        samples = np.array(255, samples.dtype) * samples
        samples = samples - np.array(128, samples.dtype)

    # Calibrate the model with samples.
    tensors_range = calibrate(model, samples)

    # Fill ranges that were not calibrated.
    fake_tensor_range = TensorData(lowest=np.array(0, "float32"), highest=np.array(1, "float32"))
    for node in model.graph.node:
        if (new_range := node.output[0]) not in tensors_range:
            tensors_range.data[new_range] = fake_tensor_range

    # Duplicate all ranges to enable quantization when introducing rescaling nodes.
    new_tensors = {}
    for k, v in tensors_range.data.items():
        if (rescaled_name := f"{k}/rescaled") not in tensors_range.data:
            new_tensors[rescaled_name] = v
    tensors_range.data.update(new_tensors)
    return tensors_range


def _find_source_error(error_warning_list):
    for obj in error_warning_list:
        if isinstance(obj, Exception):
            return str(obj)
        elif (isinstance(obj, warnings.WarningMessage) and
                any(x in str(obj.message) for x in _WARNINGS_TO_BE_HANDLE_AS_ERRORS)):
            # Partial quantization occurred.
            return str(obj.message)
    # No error source found.
    return None


def _find_tensors_by_error_msg(error_msg, model):
    assert all(node.name != "" for node in model.nodes()), "node names are required."
    # Search tensor to split model by specific patterns in error message.
    # Note all nodes between input_names and output_names are incompatibles to quantization.
    if "The following nodes were not quantized" in error_msg:
        # Partial quantization (e.g ['node1_name (node1_op)', 'node2_name (node2_op)', ...]):
        # * search for nodes that were not quantized
        node_names = re.findall(r"'(.+?) \([^\)]+\)'", error_msg)
        remaining_nodes = [node for node in model.nodes() if node.name in node_names]
        # * target tensors will be the inputs in the node list.
        input_names, _ = infer_partial_io(remaining_nodes,
                                          exclude=list(model.get_initializer_name_set()))
        # Since we don't know how many nodes are incompatible, inputs are equal to outputs.
        output_names = input_names
    elif "Impossible to quantize" in error_msg:
        # There was a list of nodes that did not allow to finalize the model quantization:
        # (e.g. [print(node_proto1), print(node_proto2), ...])
        # * search for incompatible nodes in the list
        error_msg = re.sub(r'attribute\s*{[^}]*}', '', error_msg, flags=re.DOTALL)
        node_names = re.findall(r'name:\s*"([^"]+)"', error_msg)
        remaining_nodes = [node for node in model.nodes() if node.name in node_names]
        # * split model before and after the incompatible list
        input_names, output_names = infer_partial_io(
            remaining_nodes, exclude=list(model.get_initializer_name_set()))
    else:
        warnings.warn(f"Node was not found in error (not handled yet): {error_msg}.", stacklevel=2)
        # Split model after first node.
        # Note input_names is None to take as incompatible the nodes from graph input.
        input_names = None
        output_names = list(model.nodes()[0].output)
    return input_names, output_names


@ensure_model_type
def quantize_calibrated(model, tensors_range, input_dtype="int8", ensure_fully_quantized=True):
    """Quantizes a model using provided calibration tensor ranges.

    This function replicates `quantizeml.models.quantize()` avoiding sanitize and calibrate steps.

    Args:
        model (Any): the model to quantize. An already sanitized model is expected.
        tensors_range (TensorsData): calibration ranges, typically obtained from a calibration step.
        input_dtype (str, optional): the data type used to quantize the inputs. Defaults to "int8".
        ensure_fully_quantized (bool, optional): If True, raises an error if the model is not
            fully quantized. Otherwise, allows partial quantization. Defaults to True.

    Returns:
        Any: the quantized model.
    """
    # Clone the model because insert_rescaling is performed inplace.
    model = model.clone()
    with redirect_stdout(io.StringIO()), warnings.catch_warnings(record=ensure_fully_quantized):
        if ensure_fully_quantized:
            for message in _WARNINGS_TO_BE_HANDLE_AS_ERRORS:
                warnings.filterwarnings('error', message=message)
        # Rescaling nodes must be inserted as they are transformed into InputQuantizer.
        insert_rescaling(model)
        # Quantize with tensors_range and input_dtype.
        with quantization(QuantizationParams(input_dtype=input_dtype)):
            qmodel = qml_quantize(model, tensors_range=tensors_range)
        # Rename dequantizer outputs to match with original tensor names
        # (required when merging float graphs with quantized ones).
        tensor_map = {}
        for node in qmodel.nodes():
            if node.op_type == "Dequantizer":
                # Rename dequantizer input to allow naming the output to its old name.
                tensor_map[node.input[0]] = f"{node.input[0]}/to_dequantize"
                tensor_map[node.output[0]] = node.input[0]
        rename_tensors(qmodel, tensor_map, inplace=True)
    return convert_model_to(qmodel, new_type=ONNXExtractorModel)


@ensure_model_type
def search_quantizable_sequences(model, tensors_range=None):
    """Identify and return all quantizable sequences in a model.

    This function iteratively splits the model into sequences of consecutive nodes. Moreover,
    a sequence can contain multiple branches only if the nodes between the shared input and
    its merge node are fully quantizable.

    Args:
        model (Any): the model to split.
        tensor_ranges (TensorsData, optional): calibration ranges. If not provided,
            they are computed by increasing the runtime. Defaults to None.

    Returns:
        list of onnx.ModelProto: A list of sub-models.
    """
    # Search cycles in the model
    loop_sequences = search_cycles_on_model(model)

    # Check which sub_model is fully quantizable.
    skip_outbounds = {}
    if tensors_range is None:
        tensors_range = get_tensors_range(model.model)
    for sub_model in loop_sequences:
        try:
            quantize_calibrated(sub_model, tensors_range)
            # Store the link between input_name and merge_node to compute sequences.
            skip_outbounds[sub_model.graph.input[0].name] = sub_model.graph.output[0].name
        except Exception:
            continue

    # Split model in sequences.
    return split_model_on_sequences(model, skip_outbounds=skip_outbounds)


@ensure_model_type
def quantize_sequential(model, input_dtype='int8', tensors_range=None, compatibility_info=None):
    """Quantize a sequential ONNX model, handling partial quantization and errors as needed.

    Note:
        * This function expects a sanitized model
        * This function has unexpected behavior if there are quantization errors in branches.

    Args:
        model (Any): the ONNX model to quantize.
        input_dtype (np.dtype or str, optional): expected model input format. If given as a string,
            should follow numpy string type requirements. Defaults to 'int8'.
        tensor_ranges (TensorsData, optional): calibration ranges. If not provided,
            they are computed by increasing the runtime. Defaults to None.
        compatibility_info (ModelCompatibilityInfo, optional): an existing ModelCompatibilityInfo
            object to accumulate incompatibility information during quantization.
            If None, incompatibilities are not recorded. Defaults to None.

    Returns:
        Any, ModelCompatibilityInfo: the quantized model and the incompatibilites.
    """
    if len(model.nodes()) == 0:
        # Return the empty graph.
        return model

    # Compute tensors range if needed.
    if tensors_range is None:
        tensors_range = get_tensors_range(model.model)

    # Analyze error source when quantizing.
    qparams = dict(input_dtype=input_dtype,
                   tensors_range=tensors_range,
                   compatibility_info=compatibility_info)
    try:
        # Try to quantize the whole model, triggering partial quantization as an error.
        qmodel = model.clone()
        with warnings.catch_warnings(record=True) as errors_queue:
            # Quantize model with tensors_range.
            qmodel = quantize_calibrated(qmodel, tensors_range, input_dtype,
                                         ensure_fully_quantized=False)
    except Exception as e:
        # Append the error into the queue. Please note that we give higher priority to warnings,
        # since they occur before errors.
        errors_queue.append(e)

    # If there is any source of error, continue the algorithm.
    if source_error := _find_source_error(errors_queue):
        # Try to parse the node which produces the error.
        split_before, split_after = _find_tensors_by_error_msg(source_error, qmodel)
        # Add nodes to info with its error message.
        if (len(wrong_nodes := extract_nodes_from_tensor_names(model, split_before, split_after))
                and compatibility_info is not None):
            compatibility_info._set_incompatibility(node_sequence=wrong_nodes,
                                                    stage="Quantization",
                                                    faulty_node=wrong_nodes[0].name,
                                                    reason=source_error)
        # Quantize nodes after 'split_after'.
        # Note input dtype changes if there are some quantized node.
        head_model = extract_model_from_tensor_names(qmodel, input_names=split_after)
        if qparams["input_dtype"] != 'int8' and any(is_quantized(node) for node in qmodel.nodes()):
            qparams["input_dtype"] = 'int8'
        qhead_model = quantize_sequential(head_model, **qparams)
        replace_graph(qmodel,
                      qhead_model,
                      from_tensors=split_after,
                      until_tensors=[x.name for x in head_model.output])
    return qmodel


@ensure_model_type
def quantize(model, input_dtype='uint8', input_shape=None):
    """Quantizes an ONNX model, handling partial quantization and quantization errors as needed.

    This function attempts to quantize the entire model in one pass. If quantization fails
    due to unsupported or unquantizable nodes, it analyzes the error, splits the model at
    the problematic nodes, and recursively quantizes each sub-model. The quantized sub-models
    are then merged back into the original model graph. This approach ensures that all
    quantizable parts of the model are quantized, while gracefully handling sections that
    cannot be quantized.

    Args:
        model (Any): the ONNX model to quantize.
        input_dtype (np.dtype or str, optional): expected model input format. If given as a string,
            should follow numpy string type requirements. Defaults to 'uint8'.
        input_shape (Iterable, optional): an iterable specifying the new model input shape.
            If not specified, keeps the shape. Defaults to None.

    Returns:
        Any, ModelCompatibilityInfo: the quantized model and the incompatibilites (optional).
    """
    # Prevent requantization
    if any(is_quantized(node) for node in model.nodes()):
        raise ValueError("Requantizing a model is not supported. "
                         "Please quantize the original float model directly.")
    # Sanitize model.
    model = set_model_shape(model.clone(), input_shape=input_shape)
    qmodel = sanitize(model)
    # Convert to extractor model to handle compatibility info.
    qmodel = convert_model_to(qmodel, new_type=ONNXExtractorModel)
    # Generates node names to better understand incompatibilities.
    # Use onnx_ir NameFixPass to fix when there are duplicates
    ir_pass = NameFixPass()
    qmodel.model = ir.to_proto(ir_pass(ir.from_proto(qmodel.model)).model)

    compatibility_info = ModelCompatibilityInfo(qmodel.model)
    # Compute tensors range
    tensors_range = get_tensors_range(qmodel.model)
    # Quantize each quantizable sequence independently.
    print("[INFO] Searching sequences...", end=" ")
    sequences = search_quantizable_sequences(qmodel, tensors_range)
    print("done")
    for seq_id, base_model in enumerate(tqdm.tqdm(sequences, desc="Quantizing")):
        # Use input_dtype only if no node has been quantized yet.
        if input_dtype != 'int8' and any(is_quantized(node) for node in qmodel.nodes()):
            input_dtype = 'int8'
        input_names = [x.name for x in base_model.graph.input]
        output_names = [x.name for x in base_model.graph.output]
        # Quantize the sequence.
        # Note we transfer extractor to speed runtime.
        base_model = ONNXExtractorModel(base_model)
        base_model.extractor = qmodel.extractor
        qbase_model = quantize_sequential(base_model,
                                          input_dtype,
                                          tensors_range,
                                          compatibility_info)
        # Update the quantized sequence in the main model.
        replace_graph(qmodel, qbase_model, input_names, output_names, prefix=f"sequence_{seq_id}")

    # Remove pointless quantizers
    remove_pointless_quantizers(qmodel)

    # Return a new ONNXExtractorModel to remove extractor (was not updated when quantizing
    # to speed up the computation).
    model = ONNXExtractorModel(qmodel.model)
    return model, compatibility_info
