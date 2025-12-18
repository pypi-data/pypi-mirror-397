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
__all__ = ["split_model_on_sequences", "search_cycles_on_model"]

import onnx

from ..tools import (ensure_model_type, convert_model_to, find_no_initializer_inputs,
                     extract_model_from_tensor_names, is_convertible)


@ensure_model_type
def split_model_on_sequences(model, skip_outbounds={}):
    """Split a model into sequences of consecutive nodes based on graph structure.

    This function traverses the model graph and extracts sub-models (sequences) that start from
    nodes connected to graph inputs and extend as far as possible until one of the following
    conditions is met:
      - The outbound node has multiple children (branching).
      - The outbound node is linked to a graph output.
      - Any child of the outbound node is a merge node (has multiple parents).
      - The target node itself is a merge node.

    Optionally, certain outbound nodes can be skipped using the `skip_outbounds` mapping.

    Args:
        model (Any): the model to split.
        skip_outbounds (dict, optional): a mapping where each key is an output tensor name
            and each value is the name of the output node to use instead of it.
            Note this allows to skip a set of nodes during traversal of graph. Defaults to {}.

    Returns:
        list of onnx.ModelProto: the list of sub-models.
    """
    def _insert_node_in_queue(node):
        if node not in visited_nodes:
            node_queue.append(node)
            visited_nodes.append(node)

    def _is_merge_node(node):
        return len(model.get_parents(node, oname_to_node)) > 1

    iname_to_nodes = model.input_name_to_nodes()
    oname_to_node = model.output_name_to_node()
    graph_input_names = [x.name for x in model.input]
    graph_output_names = [x.name for x in model.output]
    if (incompatible_skip := [x for x in skip_outbounds
                              if (x not in iname_to_nodes or x in graph_output_names)]):
        raise ValueError(f"{incompatible_skip} was not found in model or is a graph output.")

    # Adds all nodes linked to an input into the queue.
    node_queue, visited_nodes = [], []
    for node in model.nodes():
        if any(x in graph_input_names for x in node.input):
            _insert_node_in_queue(node)

    # Iter over the queue.
    sequences = []
    while len(node_queue) > 0:
        target_node = outbound_node = node_queue.pop(0)
        # Find the longest sequence of consecutive nodes until one of the following criteria
        # * outbound_node has multiple children
        # * outbound_node is linked to the graph output (len(child_nodes) == 0)
        # * some child of outbound_node is a merge node
        # * target node is a merge node
        # * childs contains the same operation type (all quantized or not)
        # Note child are skipped if they are in 'skip_outbounds'.
        child_nodes = [target_node]
        while (len(child_nodes) == 1 and
                not any(_is_merge_node(node) for node in child_nodes) and
                outbound_node.output[0] not in graph_output_names and
                is_convertible(child_nodes[0]) == is_convertible(target_node)):
            outbound_node = child_nodes[0]
            # Update outbound with 'skip_outbounds' info.
            while (outbound_output := outbound_node.output[0]) in skip_outbounds:
                outbound_node = oname_to_node[skip_outbounds[outbound_output]]
            # Compute new children for next iter.
            child_nodes = model.get_children(outbound_node, iname_to_nodes)

        # Extract the sequence of consecutive nodes between target_node and outbound_node.
        input_names = find_no_initializer_inputs(target_node, model.model)
        seq_model = extract_model_from_tensor_names(model, input_names, outbound_node.output)
        seq_model = convert_model_to(seq_model, new_type=onnx.ModelProto)
        sequences.append(seq_model)

        # Append children into queue.
        for node in model.get_children(outbound_node, iname_to_nodes):
            _insert_node_in_queue(node)
    return sequences


@ensure_model_type
def search_cycles_on_model(model):
    """Identify and extract the loop structures (cycles) within an ONNX model graph.

    This function traverses the model graph to find nodes where multiple branches
    reconverge to the same node, indicating the presence of a loop or cycle
    (complete skip connection).

    For each detected loop, it extracts the corresponding sub-model representing
    the looped sequence. The function also ensures that the extracted loop
    sub-models maintain the correct graph structure and do not produce incomplete
    branches.

    Args:
        model (Any): The ONNX model to extract the sub-models.

    Returns:
        list of onnx.ModelProto: A list of sub-models.
    """
    iname_to_nodes = model.input_name_to_nodes()
    oname_to_node = model.output_name_to_node()
    graph_output_names = [x.name for x in model.output]

    # Add all split nodes in the queue.
    splits = [(node, first_queue) for node in model.nodes()
              if len(first_queue := model.get_children(node, iname_to_nodes)) > 1]

    # Precompute topological order to accelerate ordering algorithm.
    node2index = {node.SerializeToString(): idx for idx, node in enumerate(model.nodes())}

    skip_loops = []
    for split_node, queue in splits:
        # Update the queue with node outbounds until they all converge to one.
        while not all(node == queue[0] for node in queue):
            # Search the split/merge/output outbound.
            current_node = target_node = queue[0]
            while True:
                children = model.get_children(target_node, iname_to_nodes)
                parents = model.get_parents(target_node, oname_to_node)
                if (len(children) != 1 or len(parents) != 1 or
                        children[0].output[0] in graph_output_names):
                    break
                target_node = children[0]

            # Updated current node in the queue with the following criteria:
            # * current is different from target
            # * children when target is a split node
            # * target's outbound when it is a merge node.
            # Note we are able to finish the algorithm if target is linked to an output.
            queue[0] = target_node
            if current_node == target_node:
                if len(children) > 1:
                    # Split node case.
                    queue.pop(0)
                    queue.extend(children)
                elif len(children) == 1:
                    # Merge node case.
                    queue[0] = children[0]
                # Break if there is a node in the queue linked to an output.
                if any(node.output[0] in graph_output_names for node in queue):
                    break

            # Sort the queue to follow a topological order (for next iterations).
            # Then remove repeated nodes.
            new_queue = []
            for node in sorted(queue, key=lambda n: node2index[n.SerializeToString()]):
                if node not in new_queue:
                    new_queue.append(node)
            queue = new_queue

        # Store the sequence if branches converge to the same node merge.
        if all(node == queue[0] for node in queue):
            outgoing_node = queue[0]
            try:
                loop_model = extract_model_from_tensor_names(model,
                                                             split_node.output,
                                                             outgoing_node.output)
            except Exception:
                # Prune sequence as it is not 'coherent'.
                continue
            else:
                loop_model = convert_model_to(loop_model, new_type=onnx.ModelProto)
                skip_loops.append(loop_model)
    return skip_loops
