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
__all__ = ["HybridModel"]

import akida
import onnx
import os
import math
from collections import defaultdict, Counter

from onnxscript import ir
from onnxruntime.quantization.quant_utils import find_by_name
from quantizeml.onnx_support.layers import BRN_OPSET, ONNX_OPSET
from quantizeml.onnx_support.layers.base_layer import IR_VERSION


def _return_element_or_list(list_object):
    if len(list_object) == 1:
        return list_object[0]
    return list_object


def _get_ir_dimensions(values):
    # Remove batch dimension.
    return _return_element_or_list([list(v.shape[1:]) for v in values])


def _get_layers(model):
    return model.layers if isinstance(model, akida.Model) else list(model.graph)


def _get_model_inputs(model):
    if isinstance(model, akida.Model):
        # Embed layer in tuple to match with ONNX format.
        return (model.layers[0],)
    return model.graph.inputs


def get_ir_input_dtype(ak_layer):
    """Determines the appropriate ONNX IR input data type for a given Akida layer.

    Args:
        ak_layer (akida.Layer): the Akida layer to determine the input data type.

    Returns:
        ir.TensorType: the corresponding ONNX IR tensor type.
    """
    layer_params = ak_layer.parameters
    if ((layer_params.layer_type == akida.LayerType.InputData and layer_params.input_signed)
            or layer_params.layer_type != akida.LayerType.InputConv2D):
        return ir.TensorType(ir.DataType.INT8)
    return ir.TensorType(ir.DataType.UINT8)


def get_ir_output_dtype(ak_layer):
    """Determines the appropriate ONNX IR output data type for a given Akida layer.

    Args:
        ak_layer (akida.Layer): the Akida layer to determine the output data type.

    Returns:
        ir.TensorType: the corresponding ONNX IR tensor type.
    """
    layer_params = ak_layer.parameters
    if layer_params.layer_type == akida.LayerType.InputData:
        return get_ir_input_dtype(ak_layer)
    if layer_params.layer_type == akida.LayerType.Dequantizer:
        return ir.TensorType(ir.DataType.FLOAT)
    return ir.TensorType(ir.DataType.INT8 if layer_params.output_bits <= 8 else ir.DataType.INT32)


def convert_ak_model_into_onnx(ak_model, program_path, ir_input=None, ir_output=None):
    """Converts an Akida model into its equivalent ONNX model.

    This function wraps the Akida model as a single ONNX node AkidaOp operator,
    preserving input and output shapes and data types. The resulting ONNX model can be used
    in ONNX pipelines and supports integration with other ONNX models.

    Note that inferences must be made through ``AkidaExecutionProvider``.

    Args:
        ak_model (akida.Model): the Akida model to convert.
        program_path (str): path where Akida program(s) will be saved to be referenced
            by the ONNX node.
        ir_input (onnxscript.ir.Value): value used as model input. If not provided,
            create a new one based on the first layer of the model. Defaults to None.
        ir_output (onnxscript.ir.Value): value used as model output. If not provided,
            create a new one based on the last layer of the model. Defaults to None.

    Returns:
        ir.Model: the ONNX equivalent model.
    """
    program_base, ext = os.path.splitext(program_path)
    assert ext == ".bin", f"Wrong extension in {program_path}. It must be '.bin'."
    if not isinstance(ak_model.device, akida.HardwareDevice):
        raise ValueError("Model must be mapped on a physical HardwareDevice "
                         f"(virtual devices cannot be used). Current device: {ak_model.device}.")

    # Save program(s) from the Akida model.
    program_path_and_layer = []
    for idx, sequence in enumerate(ak_model.sequences):
        if sequence.backend != akida.BackendType.Hardware:
            raise RuntimeError(f"Impossible to extract the program(s): sequence {idx} of model "
                               "has not been mapped on a hardware-based backend. "
                               f"Current backend: {sequence.backend}.")
        if len(ak_model.sequences) > 1:
            program_path = program_base + f"_{idx}" + ext
        program_path_and_layer.insert(idx, (program_path, sequence.passes[-1].layers[-1]))
        with open(program_path, "wb") as f:
            f.write(sequence.program)

    # Define input/output.
    output_layer = ak_model.layers[-1]
    if ir_input is None:
        input_layer = ak_model.layers[0]
        ir_input = ir.Value(
            name="X",
            shape=ir.Shape((ir.SymbolicDim("N"), *input_layer.input_dims)),
            type=get_ir_input_dtype(input_layer))
    if ir_output is None:
        if (output_dtype := get_ir_output_dtype(output_layer)).dtype == ir.DataType.FLOAT:
            # We reject this because Dequantizer must run in CPU.
            raise RuntimeError("Cannot convert models whose output is float.")
        ir_output = ir.Value(
            name="Y",
            shape=ir.Shape((ir.SymbolicDim("N"), *output_layer.output_dims)),
            type=output_dtype)

    # Record the akida op(s).
    tape = ir.tape.Tape()
    y = ir_input
    for program_path, ak_layer in program_path_and_layer:
        op_type = "AkidaOpInt8" if ak_layer.parameters.output_bits <= 8 else "AkidaOpInt32"
        y = tape.op(op_type=op_type,
                    inputs=[y],
                    attributes={"program_path": ir.AttrString("program_path", str(program_path))},
                    name=ak_layer.name,
                    domain=BRN_OPSET.domain,
                    version=BRN_OPSET.version)
        # Assign value attributes to avoid name collisions when building complex models.
        y.name = ak_layer.name
        y.shape = ir.Shape((ir.SymbolicDim("N"), *ak_layer.output_dims))
        y.type = get_ir_output_dtype(ak_layer)

    # onnxscript <= 0.2.5 does not support 'output' as parameter of 'tape.op'.
    # That is why we must do it manually.
    y.producer()._outputs = (ir_output,)

    ir_input._graph = None
    ir_output._graph = None
    # Build the model.
    ir_model = ir.Model(ir.Graph(inputs=[ir_input],
                                 outputs=[ir_output],
                                 nodes=tape.nodes,
                                 name="akida_op",
                                 opset_imports={k: v for k, v in tape.used_opsets}),
                        ir_version=IR_VERSION)
    return ir_model


class ir_Value(ir.Value):
    """Extension of onnxscript.ir.Value to handle Akida layers.

    This class overrides the `is_graph_output` method to bypass check when producer is an
    akida.Layer, supporting model creation through ``ir.Graph`` interface.
    """

    def is_graph_output(self):
        if isinstance(self.producer(), akida.Layer):
            return False
        return super().is_graph_output()


class HybridModel:
    """A container for combining and managing multiple Akida and ONNX models as a single one.

    HybridModel allows to sequentially add Akida or ONNX models, connect their inputs and outputs,
    and manage their relationships. It provides a unified interface to access layers,
    input/output shapes and to retrieve or connect sub-models by **layer name**.

    The class ensures model integrity by checking for unique layer names and
    valid inbound connections.

    Args:
        models (list, optional): list of Akida or ONNX models to initialize the hybrid model with.
            Defaults to None.
        name (str, optional): name of the hybrid model. Defaults to "HybridModel".
    """

    def __init__(self, models=None, name="HybridModel"):
        self.name = name
        self._models = []
        self._ak_output_layers_map = {}
        self._output_layer_names = None
        if models is not None:
            [self._add(model) for model in models]

    @property
    def _outgoing(self):
        values = []
        for model in self._models:
            if isinstance(model, akida.Model):
                values.append(self._ak_output_layers_map[model.layers[-1].name])
            else:
                values.extend(model.graph.outputs)
        return values

    @property
    def outputs(self):
        outputs_ = [v for v in self._outgoing if len(v.consumers()) == 0]
        if self._output_layer_names:
            # Sort outputs following output names order.
            outputs_ = sorted(
                outputs_, key=lambda x: self._output_layer_names.index(x.producer().name))
        return outputs_

    @property
    def layers(self):
        """Returns the hybrid model layers.

        Returns:
            list: the model layers.
        """
        return [ly for model in self._models for ly in _get_layers(model)]

    @property
    def _output_layers(self):
        return [v.producer() for v in self.outputs]

    @property
    def input_shape(self):
        """Returns the hybrid model input shape.

        Returns:
            list: the model input shape.
        """
        # By HybridModel construction, only one model can be connected to the input.
        input_model = self._models[0]
        if isinstance(input_model, akida.Model):
            return input_model.input_shape
        return _get_ir_dimensions(input_model.graph.inputs)

    @property
    def output_shape(self):
        """Returns the hybrid model output shape.

        Returns:
            list: the model output shape.
        """
        return _get_ir_dimensions(self.outputs)

    @property
    def akida_models(self):
        """Returns a list of Akida models within the hybrid model.

        Returns:
            list: the akida models within the hybrid model.
        """
        return [model for model in self._models if isinstance(model, akida.Model)]

    def get_layer(self, name):
        """Retrieves a layer from the model by its name.

        Args:
            name (str): the name of the layer to retrieve.

        Returns:
            Layer: the layer.
        """
        if (layer := find_by_name(name, self.layers)) is None:
            raise ValueError(f"Layer with name '{name}' not found in '{self.name}'.")
        return layer

    def _add(self, model, inbound_names=[]):
        """Adds a new Akida or ONNX model and connects its inputs to specified inbounds.

        This method performs several checks and conversions:
        - validates the model type (must be akida.Model or onnx.ModelProto)
        - converts ONNX models to the internal IR representation if necessary
        - determines the inbound layers/nodes to connect the new model's inputs
        - updates the internal inbound mapping and appends the model to the HybridModel.

        Args:
            model (akida.Model or onnx.ModelProto): the model to add.
            inbound_names (list, optional): list of layer names in the HybridModel to which
                the new model's inputs will be connected. If not provided, the model will be
                connected to all current outbounds. Defaults to [].
        """
        if not isinstance(model, supported := (akida.Model, onnx.ModelProto)):
            raise TypeError(f"Failed to add {model} to '{self.name}'. "
                            f"Supported types: {supported}.")

        # Convert onnx.ModelProto into ir.
        if isinstance(model, onnx.ModelProto):
            onnx.checker.check_model(model, full_check=True)
            model = ir.from_proto(model)

        # Retrieve incoming_values from their names.
        if len(inbound_names) == 0:
            incoming_values = self.outputs
        else:
            incoming_values = self._get_inbound_outputs_from_names(inbound_names)

        # Check if model is able to be added.
        self._check_model_integrity(model, incoming_values)

        # Update model inputs with the outputs from its inbounds.
        if len(incoming_values) > 0:
            model_inputs = _get_model_inputs(model)
            if isinstance(model, ir.Model):
                # Replace inputs with inbound outputs.
                ir.convenience.replace_all_uses_with(model_inputs, incoming_values)
                # Overwrite model inputs to allow sub_model inference.
                model.graph._inputs = incoming_values
            else:
                # Insert the first layer as new consumer of ir.Value
                incoming_values[0]._add_usage(model.layers[0], 0)

        # Create a outgoing value when model is an Akida one, used for incoming models.
        if isinstance(model, akida.Model):
            ak_layer = model.layers[-1]
            self._ak_output_layers_map[ak_layer.name] = ir_Value(
                producer=ak_layer,
                index=0,
                name=ak_layer.name,
                shape=ir.Shape((ir.SymbolicDim("N"), *ak_layer.output_dims)),
                type=get_ir_output_dtype(ak_layer))

        # Append the new model in the list.
        self._models.append(model)

        # Reset output_names each time a model is added, as the model output may change.
        self._output_layer_names = None

    def map(self, device, mode=akida.MapMode.AllNps):
        """Map (if possible) all akida models to a given device.

        Args:
            device (akida.Device): An Akida device.
            mode (akida.MapMode, optional): The mapping mode. Defaults to AllNps.
        """
        for idx, model in enumerate(self.akida_models):
            try:
                model.map(device, hw_only=True, mode=mode)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to map Akida model at index {idx} within 'akida_models'. "
                    f"Reason: {str(e)}."
                )

    def generate_inference_model(self, dirpath="."):
        """Generates a unified ONNX inference model from all sub-models in the HybridModel.

        This method combines all Akida and ONNX sub-models added to the HybridModel into a single
        ONNX model suitable for inference. It handles the conversion of Akida models to ONNX
        and connects sub-models according to their inbounds.

        The resulting model can be used for inferences based on ``AkidaExecutionProvider``:

        >>> inference_model = model.generate_inference_model()
        >>> sess = onnxruntime.InferenceSession(inference_model.SerializeToString(),
        ...                                     providers=["AkidaExecutionProvider"])
        >>> outputs = sess.run(None, feeds)

        Args:
            dirpath (str, optional): directory path where Akida programs will be saved.
                Defaults to the current directory.

        Returns:
            onnx.ModelProto: the combined ONNX model ready for inference.
        """
        if len(self._models) == 0:
            raise RuntimeError("At least one model is required to generate the inference model.")
        if (len(self.akida_models) > 0 and
                not all(self.akida_models[0].device == m.device for m in self.akida_models)):
            raise RuntimeError("All akida models must be mapped in the same device.")

        graph_params, functions = defaultdict(list), []
        for sub_model_id, sub_model in enumerate(self._models):
            # Akida model processing.
            if isinstance(sub_model, akida.Model):
                # Search the outgoing which contains the first layer as consumer (link value).
                if sub_model_id == 0:
                    ak_ir_input = None
                else:
                    ak_ir_input = [v for v in self._outgoing
                                   if sub_model.layers[0] in v.consumers()][0]
                    ak_ir_input._graph = None
                    ak_ir_input._producer = None

                # Convert the model to ONNX.
                # Note we keep ir_output to correctly track it in the global model.
                program_path = os.path.join(dirpath, f"program_{sub_model_id}.bin")
                ir_output = self._ak_output_layers_map[sub_model.layers[-1].name]
                sub_model = convert_ak_model_into_onnx(sub_model,
                                                       program_path,
                                                       ir_input=ak_ir_input,
                                                       ir_output=ir_output)

            # Rename sub_model outputs to avoid name collisions.
            for idx, v_output in enumerate(sub_model.graph.outputs):
                v_output.name = f"{self.name}_{sub_model_id}/output{idx}"

            # Remove graph in nodes/initializer/inputs/outputs since onnxscript does not support
            # creating new graph with elements from other graphs.
            for node in sub_model.graph:
                node.graph = None

            for initializer in sub_model.graph.initializers.values():
                initializer._graph = None

            for input_ in sub_model.graph.inputs:
                input_._graph = None

            for output in sub_model.graph.outputs:
                output._graph = None

            # Transfer sub_model parameters to global one:
            # * graph inputs
            if sub_model_id == 0:
                graph_params["inputs"] = sub_model.graph.inputs
            # * nodes and initializers
            graph_params["nodes"].extend(list(sub_model.graph))
            graph_params["initializers"].extend(sub_model.graph.initializers.values())
            # * functions
            for f in sub_model.functions.values():
                if f not in functions:
                    functions.append(f)
        # * graph outputs and opset imports
        graph_params["outputs"] = self.outputs
        graph_params["opset_imports"] = {"": ONNX_OPSET.version,
                                         BRN_OPSET.domain: BRN_OPSET.version}

        # Build graph and model.
        ir_model = ir.Model(ir.Graph(**graph_params, name=self.name),
                            ir_version=IR_VERSION,
                            functions=functions)

        # Convert ir_model to onnx.ModelProto
        model = ir.to_proto(ir_model)

        # Clean value info to avoid mismatch in batch size.
        model.graph.ClearField("value_info")

        # Sanity check.
        onnx.checker.check_model(model, full_check=True)
        return model

    def compute_data_movement(self):
        """Computes the data movement between CPU and Akida for models in the HybridModel.

        For each Akida model sequence, this method calculates:
        - The amount of data transferred from CPU to Akida.
        - The amount of data transferred from Akida to CPU.

        The size is computed as the product of the input or output dimensions.

        Returns:
            list of dict: a list of dictionaries, each containing :
                - "layer": the Akida layer involved in the data transfer.
                - "type": a string indicating the direction ("CPU to Akida" or "Akida to CPU").
                - "size": The size in bytes of the data movement.
        """
        data_movement = []
        # Compute data movement for each sequence.
        for ak_model in self.akida_models:
            for seq in ak_model.sequences:
                # First layer requires a data movement from CPU to Akida.
                input_layer = seq.passes[0].layers[0]
                factor = get_ir_input_dtype(input_layer).dtype.itemsize
                data_movement.append({"layer": input_layer,
                                      "type": "CPU to Akida",
                                      "size": math.prod(input_layer.input_dims) * factor})
                # Last layer requires a data movement from Akida to CPU.
                output_layer = seq.passes[-1].layers[-1]
                factor = get_ir_output_dtype(output_layer).dtype.itemsize
                data_movement.append({"layer": output_layer,
                                      "type": "Akida to CPU",
                                      "size": math.prod(output_layer.output_dims) * factor})
        return data_movement

    def _assign_outputs_order(self, inbound_names):
        """Assigns a custom order to the outputs of the HybridModel.

        This method sets the order of model outputs based on the provided list of inbound names.

        Args:
            inbound_names (list of str): list of names to define the desired output order.
        """
        prev_output_layer_names = set(ly.name for ly in self._output_layers)
        if prev_output_layer_names.difference(inbound_names):
            raise ValueError(f"{inbound_names} must exactly contain "
                             f"the following names: {prev_output_layer_names}.")
        self._output_layer_names = inbound_names

    def _get_inbound_outputs_from_names(self, names):
        assert isinstance(names, list), f"Inbounds must be a list. Receives: {names}."
        expected_bound_names = set(v.producer().name for v in self._outgoing)
        if any(name not in expected_bound_names for name in names):
            raise ValueError(f"Invalid inbounds provided: {names}. "
                             "It can only add a model to one of the following layers: "
                             f"{expected_bound_names}.")
        return [self._get_layer_outputs(self.get_layer(name)) for name in names]

    def _check_model_integrity(self, model, incoming_values):
        # For a model to be compatible, it must:
        # * has unique and non-empty names
        try:
            new_layers = _get_layers(model)
            new_layer_names = [ly.name for ly in new_layers]
            if len(dup_names := [k for k, c in Counter(new_layer_names).items() if c > 1]) > 0:
                raise ValueError(f"There are some duplicate names in model: {dup_names}.")
            if wrong_layers := [ly for ly in new_layers if ly.name in ["", None]]:
                raise ValueError(f"Model has node/layers with empty names: {wrong_layers}.")
        except Exception as e:
            raise RuntimeError(f"Impossible to add {model}.") from e

        # * there are no previously saved layers with the same name.
        layer_names = set(ly.name for ly in self.layers)
        new_layer_names = set(new_layer_names)
        if len(unsupported_layers := new_layer_names.intersection(layer_names)) > 0:
            raise ValueError(f"Impossible to add {model}: it contains layers with the same name "
                             f"as those already stored: {unsupported_layers}.")

        if len(self._models) > 0:
            # * model has the same inputs than required inbounds.
            model_inputs = _get_model_inputs(model)
            if (model_num := len(model_inputs)) != (inbound_num := len(incoming_values)):
                raise ValueError(f"Number of inbounds provided ({model_num}) does not match with "
                                 f"the number of model inputs ({inbound_num}).")

            # * input shape and type correspond to values to be linked.
            for i_value, o_value in zip(incoming_values, model_inputs):
                if isinstance(o_value, akida.Layer):
                    # Build a fake ir.Value to compare.
                    o_value = ir.Value(name=o_value.name,
                                       shape=ir.Shape((None, *o_value.input_dims)),
                                       type=get_ir_input_dtype(o_value))
                try:
                    if i_value.shape[1:] != o_value.shape[1:]:
                        raise ValueError(f"Shape mismatch. Expected: {i_value.shape[1:]}, "
                                         f"got: {o_value.shape[1:]}.")
                    elif i_value.dtype != o_value.dtype:
                        raise ValueError(f"Type mismatch. Expected: {i_value.type}, "
                                         f"got: {o_value.type}.")
                except Exception as e:
                    raise ValueError(f"Impossible to connect {i_value.name} with "
                                     f"{o_value.name}.") from e

    def _get_layer_outputs(self, layer):
        if layer.name in self._ak_output_layers_map:
            return self._ak_output_layers_map[layer.name]
        elif isinstance(layer, ir.Node):
            return layer.outputs[0]
        raise ValueError(f"Impossible to find outputs for {layer.name}.")
