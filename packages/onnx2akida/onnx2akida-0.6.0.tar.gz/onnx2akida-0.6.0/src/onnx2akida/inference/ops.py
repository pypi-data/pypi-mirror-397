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

import akida
from onnxruntime_extensions import PyOp, onnx_op
from quantizeml.onnx_support.layers import BRN_OPSET


def _load_program(program_path):
    with open(program_path, "rb") as file:
        program = file.read()
        file.close()
    return program


def _akida_forward(x, program_path):
    device = akida.devices()[0]
    device.program = _load_program(program_path)
    out = device.forward(x)
    device.unprogram()
    return out


@onnx_op(
    op_type=f"{BRN_OPSET.domain}::AkidaOpInt8",
    inputs=[PyOp.dt_int8],
    outputs=[PyOp.dt_int8],
    attrs={"program_path": PyOp.dt_string},
)
def _akida_op_i_int8_o_int8(x, program_path):
    return _akida_forward(x, program_path)


@onnx_op(
    op_type=f"{BRN_OPSET.domain}::AkidaOpInt8",
    inputs=[PyOp.dt_uint8],
    outputs=[PyOp.dt_int8],
    attrs={"program_path": PyOp.dt_string},
)
def _akida_op_i_uint8_o_int8(x, program_path):
    return _akida_forward(x, program_path)


@onnx_op(
    op_type=f"{BRN_OPSET.domain}::AkidaOpInt32",
    inputs=[PyOp.dt_int8],
    outputs=[PyOp.dt_int32],
    attrs={"program_path": PyOp.dt_string},
)
def _akida_op_i_int8_o_int32(x, program_path):
    return _akida_forward(x, program_path)


@onnx_op(
    op_type=f"{BRN_OPSET.domain}::AkidaOpInt32",
    inputs=[PyOp.dt_uint8],
    outputs=[PyOp.dt_int32],
    attrs={"program_path": PyOp.dt_string},
)
def _akida_op_i_uint8_o_int32(x, program_path):
    return _akida_forward(x, program_path)
