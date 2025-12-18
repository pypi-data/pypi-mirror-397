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
__all__ = ["extract_model_from_tensor_names", "ONNXExtractorModel",
           "convert_model_to", "ensure_model_type", "rename_tensors", "remove_nodes",
           "insert_graph_at", "replace_graph", "extract_nodes_from_tensor_names"]

import functools
import onnx
import uuid

from quantizeml.onnx_support.quantization import ONNXModel
from onnxruntime.quantization.quant_utils import find_by_name
from onnx.utils import Extractor


class ONNXExtractorModel(ONNXModel):
    """Interface with some tools to handle `onnx.ModelProto` objects.

    Args:
        Model (`onnx.ModelProto`): the base model
    """

    def __init__(self, model):
        # Overwrite __init__ in order to avoid check_model() call.
        self.model = model
        self._extractor = None

    @property
    def extractor(self):
        return self._extractor

    @extractor.setter
    def extractor(self, new_extractor):
        assert isinstance(new_extractor, Extractor)
        self._extractor = new_extractor

    def compute_extractor(self):
        self.extractor = Extractor(self.model)

    def clone(self):
        new_model = ONNXExtractorModel(self.model.__deepcopy__())
        if self.extractor is not None:
            new_model.extractor = self.extractor
        return new_model

    def extract_model(self, input_names, output_names):
        if self.extractor is None:
            self.compute_extractor()

        # Rebuild input/output dicts
        self.extractor.outmap = self.extractor._build_output_dict(self.extractor.graph)
        model_proto = self.extractor.extract_model(input_names=input_names,
                                                   output_names=output_names)
        model_proto.graph.name = self.model.graph.name
        return ONNXExtractorModel(model_proto)


def convert_model_to(model, new_type):
    """Transform a model into a desired type.

    Args:
        model (onnx.ModelProto or ONNModel or ONNXExtractorModel): the model to convert.

    Returns:
        Any: the converted model.
    """
    supported_types = (onnx.ModelProto, ONNXModel, ONNXExtractorModel)
    if not (new_type in supported_types and isinstance(model, supported_types)):
        raise TypeError(f"Cannot convert {type(model)} into {new_type}. "
                        f"Supported types: {supported_types}.")
    if isinstance(model, new_type):
        return model
    elif new_type == onnx.ModelProto:
        return model.model
    elif isinstance(model, onnx.ModelProto):
        return new_type(model)
    return new_type(model.model)


def ensure_model_type(func):
    """Decorator to handle model types.

    This transform the first argument of the decorated function into `ONNXExtractorModel`, then
    apply `func` and finally de-convert the `ONNXExtractorModel` to the original type.

    Args:
        func (callable): the function to decorate.

    Returns:
        callable: the decorated function.
    """
    @functools.wraps(func)
    def wrapper(model, *args, **kwargs):
        model_type = type(model)
        converted_model = convert_model_to(model, new_type=ONNXExtractorModel)
        transformed_model = func(converted_model, *args, **kwargs)
        if isinstance(transformed_model, tuple):
            return tuple(convert_model_to(elem, new_type=model_type)
                         if isinstance(elem, ONNXExtractorModel) else elem
                         for elem in transformed_model)
        elif isinstance(transformed_model, ONNXExtractorModel):
            return convert_model_to(transformed_model, new_type=model_type)
        return transformed_model
    return wrapper


@ensure_model_type
def extract_nodes_from_tensor_names(model, input_names=None, output_names=None):
    """Extract the list of nodes between the specified input and output tensor names.

    Args:
        model (Any): the model from which to extract the nodes.
        input_names (list, optional): the names of the input tensors.
            If not specified, model inputs are used. Defaults to None.
        output_names (list, optional): the names of the output tensors.
            If not specified, model outputs are used. Defaults to None.

    Returns:
        list of onnx.NodeProto: the list of nodes.
    """
    if input_names is None:
        input_names = [x.name for x in model.input]
    if output_names is None:
        output_names = [x.name for x in model.output]

    # Inintialize variables.
    nodes = []
    iname_to_nodes = model.input_name_to_nodes()

    # Remove tensor containing in both lists.
    input_names = set(x for x in input_names if x not in output_names)

    # Sanity check.
    all_tensors = sum([n.input[:] + n.output[:] for n in model.nodes()], [])
    wrong_tensors = input_names.difference(all_tensors) | set(output_names).difference(all_tensors)
    if wrong_tensors:
        raise ValueError(f"Unrecognized {wrong_tensors}: they are not in the graph.")

    # Loop graph from input_names until output_names.
    while len(input_names) > 0:
        target_tensor = input_names.pop()
        for node in iname_to_nodes.get(target_tensor, []):
            if node not in nodes:
                nodes.append(node)
                # Include in the queue the output.
                for toutput in node.output:
                    if toutput not in output_names:
                        input_names.add(toutput)

    # Sort nodes topologically.
    all_nodes = model.nodes()[:]
    return sorted(nodes, key=lambda x: all_nodes.index(x))


@ensure_model_type
def extract_model_from_tensor_names(model, input_names=None, output_names=None, check_model=True):
    """Extract a submodel based on specified input and output tensor names.

    Args:
        model (Any): the model from which to extract the submodel.
        input_names (list, optional): the names of the input tensors to be extracted.
            If not specified, model inputs are used. Defaults to None.
        output_names (list, optional): the names of the output tensors to be extracted.
            If not specified, model outputs are used. Defaults to None.
        check_model (bool, optional): whether to run model checker on the extracted model.
            Defaults to True.

    Returns:
        Any: the submodel between `input_names` and `output_names`.
    """
    if input_names is None:
        input_names = [x.name for x in model.input]
    if output_names is None:
        output_names = [x.name for x in model.output]

    # Sanity checks.
    try:
        extracted_model = model.extract_model(input_names, output_names)
        if check_model:
            extracted_model.check_model(infer_shapes=False)

            # Check if all inputs are linked to at least a node (if any).
            input_names_set = set(input_names)
            all_inputs = set(inp for node in extracted_model.nodes() for inp in node.input)
            if len(all_inputs) > 0 and len(unlinked := input_names_set.difference(all_inputs)) > 0:
                raise ValueError(f"{unlinked} are disconnected from the graph.")

            # Check if intermediate nodes have the same number of outbounds or
            # they must be linked to an output.
            org_iname_to_nodes = model.input_name_to_nodes()
            ext_iname_to_nodes = extracted_model.input_name_to_nodes()
            initializer_names = extracted_model.get_initializer_name_set()
            ext_iname_to_nodes = {k: v for k, v in ext_iname_to_nodes.items()
                                  if k not in input_names_set | initializer_names}
            for iname in ext_iname_to_nodes:
                for node in org_iname_to_nodes[iname]:
                    if node not in ext_iname_to_nodes[iname]:
                        raise ValueError(f"It was expected that {node} was linked to {iname}.")

    except Exception as e:
        raise ValueError(f"Impossible to extract sub_model on {model.graph().name} "
                         f"from {input_names} until {output_names}.") from e
    return extracted_model


@ensure_model_type
def rename_tensors(model, tensor_map, inplace=False):
    """Rename tensors in the model according to the provided tensor_map.

    Args:
        model (Any): the base model.
        tensor_map (dict): map that describes the source to rename (keys) and its new name (values).
        inplace (bool, optional): whether to modify model. Defaults to False.

    Returns:
        Any: the model modified.
    """
    dparams = dict(prefix="", rename_inputs=False, rename_nodes=False, rename_edges=False,
                   rename_outputs=False, rename_initializers=False, rename_value_infos=False)
    g = onnx.compose.add_prefix_graph(model.graph(),
                                      name_map=tensor_map,
                                      inplace=inplace,
                                      **dparams)
    if not inplace:
        model = model.clone()
        model.graph().CopyFrom(g)
    return model


@ensure_model_type
def remove_nodes(model, from_tensors, until_tensors):
    """Remove all nodes between 'from_tensors' and 'until_tensors'.

    Note that the model will potentially no longer be compatible (e.g. disconnected graph or
    some error when running `onnx.checker.check_model`).

    Args:
        model (Any): the model to modify.
        from_tensors (list of str): starting edge point where to remove nodes.
        until_tensors (list of str): end edge point where outputs will be connected.
    """
    assert len(from_tensors) > 0 and len(until_tensors) > 0
    model2remove = extract_model_from_tensor_names(model, from_tensors, until_tensors)

    # Remove graph in several steps:
    # 1. Remove nodes.
    model.remove_nodes(model2remove.nodes())
    # 2. Remove initializers (if they are not used by any remaining node).
    model.clean_initializers()
    # 3. Remove value_infos.
    for value_info in model2remove.graph().value_info:
        # Only remove value_info if it is not an input/output and it is still in the graph.
        # As they are needed for extract_model
        if value_info in model.graph().value_info and (value_info not in model.input) \
           and (value_info not in model.output):
            model.graph().value_info.remove(value_info)


@ensure_model_type
def insert_graph_at(model, subgraph_to_insert, anchor_node=None):
    """Insert a subgraph into the model immediately after a specified node.

    This function injects all nodes from `subgraph_to_insert` into `model`,
    placing them right after `anchor_node`. If it is None, the subgraph is inserted
    at the beginning of the `model`.

    Args:
        model (Any): the model to be extended.
        subgraph_to_insert (Any): the graph to insert.
        anchor_node (onnx.NodeProto, None): the node in `model` after which to insert the subgraph.
            If `None`, insertion occurs at position 0. Defaults to None.
    """
    # Normalize subgraph type
    subgraph_to_insert = convert_model_to(subgraph_to_insert, new_type=onnx.ModelProto)

    # (took from onnx.compose.merge_models) check model versions and opset imports.
    if model.ir_version() != subgraph_to_insert.ir_version:
        raise ValueError(
            f"IR version mismatch {model.ir_version()} != {subgraph_to_insert.ir_version}. "
            "Both models should have the same IR version.")
    opset_import_map = {}
    for entry in model.opset_import()[:] + subgraph_to_insert.opset_import[:]:
        if entry.domain in opset_import_map:
            found_version = opset_import_map[entry.domain]
            if entry.version != found_version:
                raise ValueError(
                    "Can't add two models with different operator set ids for a given domain. "
                    f"Got: {model.opset_import()} and {subgraph_to_insert.opset_import}."
                )
        else:
            opset_import_map[entry.domain] = entry.version

    # Transfer nodes.
    # Note we implicitly convert protobuf.RepeatedCompositeCo to a list since 'index' function
    # is not supported before python 3.11.
    start_idx = model.nodes()[:].index(anchor_node) + 1 if anchor_node is not None else 0
    for node in subgraph_to_insert.graph.node:
        model.nodes().insert(start_idx, node)
        start_idx += 1

    # Transfer graph objects.
    for new_initializer in subgraph_to_insert.graph.initializer:
        model.add_initializer(new_initializer)
    model.graph().value_info.extend(subgraph_to_insert.graph.value_info)
    model.functions.extend(subgraph_to_insert.functions)
    for opset_import in subgraph_to_insert.opset_import:
        if opset_import not in model.opset_import():
            model.set_opset_import(opset_import.domain, opset_import.version)

    # Sanity check.
    model.check_model(infer_shapes=False)


@ensure_model_type
def replace_graph(model, replacement_graph, from_tensors, until_tensors, prefix=None):
    """Replace all nodes between 'from_tensors' and 'until_tensors' by 'replacement_graph'.

    The replacement happens in the following steps:
        * `model` nodes between 'from_tensors' and 'until_tensors' are pruned
        * `replacement_graph` tensor names are renamed, avoiding collision names and matching
          with 'from_tensors' and 'until_tensors'
        * `replacement_graph` is inserted after the last node that produces one `from_tensors`

    Args:
        model (Any): the model to modify.
        replacement_graph (Any): the model to be inserted.
        from_tensors (list of str): starting edge point where to insert the model.
        until_tensors (list of str): end edge point where outputs will be connected.
        prefix (str, optional): name used to rename InputQuantizer/Dequantizer.
            If not specified, a random value is assigned. Defaults to None.
    """
    def _add_suffix_to_map(node, suffix):
        base_name = f"{prefix or str(uuid.uuid4())}/{suffix}"
        tensor_map[node.input[1]] = f"{base_name}_scale"
        if len(node.input) > 2 and node.input[2]:
            tensor_map[node.input[2]] = f"{base_name}_zp"
        node.name = base_name

    # Store the value infos of the edge tensors to add it back after insertion.
    # This is needed as these last value infos are removed by remove_nodes.
    # And they are still needed (e.g. for extract_model)
    vi_to_add = [model.find_value_info_by_name(tensor) for tensor in from_tensors + until_tensors]

    # Normalize subgraph type
    replacement_graph = convert_model_to(replacement_graph, new_type=onnx.ModelProto)

    if from_tensors == until_tensors and len(replacement_graph.graph.node) > 0:
        raise NotImplementedError("Inserting a subgraph at the same point is not supported yet.")

    # Add prefix to InputQuantizer/Dequantizer initializers to avoid name collisions.
    tensor_map = {}
    num_iq, num_dq = 0, 0
    for node in replacement_graph.graph.node:
        if node.op_type == "InputQuantizer":
            _add_suffix_to_map(node, f"quantizer_{num_iq}")
            tensor_map[node.output[0]] = node.name.replace('/quantizer_', '/quantize_')
            num_iq += 1
        elif node.op_type == "Dequantizer":
            _add_suffix_to_map(node, f"dequantizer_{num_dq}")
            num_dq += 1

    # Rename tensors in replacement_graph having the same name as 'from_tensors' or 'until_tensor'.
    for node in replacement_graph.graph.node:
        for x in node.input[:] + node.output[:]:
            if x in from_tensors + until_tensors:
                tensor_map[x] = f"{x}_renamed"

    # Finally, rename replacement_graph inputs/outputs to match
    # with 'from_tensors' and 'until_tensors', respectively.
    for input_, new_name in zip(replacement_graph.graph.input, from_tensors):
        tensor_map[input_.name] = new_name
    for output, new_name in zip(replacement_graph.graph.output, until_tensors):
        tensor_map[output.name] = new_name
    replacement_graph = rename_tensors(replacement_graph, tensor_map)

    # Replace graph through the following steps:
    # 1. remove nodes between 'from_tensors' and 'until_tensors'.
    remove_nodes(model, from_tensors, until_tensors)
    # 2. remove duplicate functions.
    for f in model.functions:
        if f_to_prune := find_by_name(f.name, replacement_graph.functions):
            replacement_graph.functions.remove(f_to_prune)
    # 3. rename tensors if needed (linking the graph broken by remove_nodes).
    if len(replacement_graph.graph.node) == 0:
        tensor_map = {x: y for x, y in zip(from_tensors, until_tensors)}
        rename_tensors(model, tensor_map, inplace=True)
        from_tensors = until_tensors
    # 4. insert replacement_graph graph between 'from_tensors' and 'until_tensors'.
    if any(input_.name in from_tensors for input_ in model.input):
        anchor_node = None
    else:
        anchor_node = [node for node in model.nodes() if node.output[0] in from_tensors][-1]

    # Add back the value infos.
    for vi in vi_to_add:
        if model.find_value_info_by_name(vi.name) is None:
            model.graph().value_info.append(vi)
    insert_graph_at(model, replacement_graph, anchor_node=anchor_node)
