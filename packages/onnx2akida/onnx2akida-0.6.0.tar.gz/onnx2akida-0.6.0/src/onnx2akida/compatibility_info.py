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

__all__ = ["ModelCompatibilityInfo"]

from collections import namedtuple
from itertools import chain

import onnx

_IncompatibleSequence = namedtuple("IncompatibleSequence",
                                   ("nodes", "stage", "faulty_node", "reason"))


class ModelCompatibilityInfo:
    """Tracks Akida compatibility of an ONNX model.

    Args:
        model (onnx.ModelProto): The ONNX model to analyze.
    """

    def __init__(self, model):
        self.model = model
        self.incompatible_sequences = []

    @property
    def incompatible_nodes(self):
        """Returns a list of all incompatible nodes.

        Returns:
            list: list of nodes from all incompatible sequences.
        """
        return list(chain.from_iterable(
            sequence.nodes for sequence in self.incompatible_sequences))

    @property
    def incompatible_op_types(self):
        """Returns a list of unique op types of incompatible nodes.

        Returns:
            list: list of unique op types of incompatible nodes.
        """
        return sorted({node.op_type for node in self.incompatible_nodes})

    @property
    def compatibility_percentage(self):
        """Returns the model compatibility percentage with the Akida accelerator.

        Returns:
            float: percentage of compatible nodes in the model.
        """
        total = len(self.model.graph.node)
        return round(100.0 * (1 - len(self.incompatible_nodes) / total) if total else 0.0, 4)

    @property
    def incompatibilities(self):
        """Returns a list of incompatibilities with reasons and other information.

        Example
        -------
        .. code-block:: python

            [
                {
                    "node_sequence": [
                        {"name": "cos_node", "op_type": "Cos"},
                        ...
                    ],
                    "stage": "Quantization",
                    "faulty_node": "cos_node",
                    "reason": "Unsupported op."
                },
                ...
            ]

        Returns:
            list: list of incompatibilities with reasons and other information.
        """
        incompatibilities = []
        for sequence in self.incompatible_sequences:
            sequence_desc = [
                {"name": node.name, "op_type": node.op_type}
                for node in sequence.nodes
            ]
            incompatibilities.append({
                "node_sequence": sequence_desc,
                "stage": sequence.stage,
                "faulty_node": sequence.faulty_node,
                "reason": sequence.reason
            })

        return incompatibilities

    def _set_incompatibility(self, node_sequence, stage, faulty_node, reason):
        """Registers an incompatibility for a given sequence of ONNX nodes.

        Args:
            node_sequence (list[onnx.NodeProto]): The sequence of ONNX nodes that are incompatibles.
            stage (str): The processing stage where the incompatibility was detected
                        (e.g., 'Quantization', 'Conversion', 'Mapping').
            faulty_node (str): The name of the node responsible for the incompatibility.
            reason (str): A human-readable explanation of why the incompatibility occurred.
        """
        self.incompatible_sequences.append(_IncompatibleSequence(node_sequence,
                                                                 stage,
                                                                 faulty_node,
                                                                 reason))

    def save_tagged_model(self, save_path):
        """Saves a model with node op_types tagged as 'AK<>' for compatible nodes
        and 'CPU<>' for incompatible nodes.

        Args:
            save_path (str): File path to save the tagged model.
        """
        incompatible_nodes = self.incompatible_nodes
        copy_model = self.model.__deepcopy__()

        for node in copy_model.graph.node:
            if node not in incompatible_nodes:
                node.op_type = "AK<" + node.op_type + ">"
            else:
                node.op_type = "CPU<" + node.op_type + ">"
        onnx.save_model(copy_model, save_path)
