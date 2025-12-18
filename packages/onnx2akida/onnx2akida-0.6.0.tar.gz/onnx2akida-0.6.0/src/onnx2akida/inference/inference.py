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

__all__ = ["AkidaInferenceSession"]

import os

import akida
import onnx
import onnxruntime as ort
from onnxruntime_extensions import get_library_path


def _check_akida_device_availability(path_or_bytes):
    # Taken from onnxruntime.InferenceSession.__init__()
    if isinstance(path_or_bytes, (str, os.PathLike)):
        model = onnx.load(os.fspath(path_or_bytes))
    elif isinstance(path_or_bytes, bytes):
        model = onnx.load_from_string(path_or_bytes)
    else:
        raise TypeError(f"Unable to load from type '{type(path_or_bytes)}'")

    # Check for Akida device if the model contains Akida ops
    akida_ops = [node for node in model.graph.node if "AkidaOp" in node.op_type]
    if akida_ops and len(akida.devices()) == 0:
        raise RuntimeError("No Akida devices found for model inference.")


class AkidaInferenceSession(ort.InferenceSession):
    """A wrapper around onnxruntime.InferenceSession that ensures the Akida custom ops
    library is registered.

    Args:
        path_or_bytes (str or bytes): path to the ONNX model file or the model in bytes.
        sess_options (ort.SessionOptions, optional): session options for the inference session.
            Defaults to None.
        providers (list, optional): list of execution providers. Defaults to None.
        provider_options (list, optional): list of provider options. Defaults to None.
        **kwargs: additional keyword arguments for the InferenceSession.
    """
    def __init__(self, path_or_bytes, sess_options=None, providers=None,
                 provider_options=None, **kwargs):

        _check_akida_device_availability(path_or_bytes)

        if sess_options is None:
            sess_options = ort.SessionOptions()

        # A workaround to check if the custom ops library is already registered
        try:
            sess_options.get_session_config_entry("registered")
        except RuntimeError:
            sess_options.register_custom_ops_library(get_library_path())
            sess_options.add_session_config_entry("registered", "true")

        super().__init__(path_or_bytes, sess_options,
                         providers, provider_options, **kwargs)
