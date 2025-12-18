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
import argparse
import os

import akida
import cnn2snn
import onnx
from quantizeml import load_model

from .convert import convert, print_report


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", type=str, required=True, help="Model to check")
    parser.add_argument("-nb", "--initial_num_nodes", type=int, default=36,
                        help="Initial number of nodes. Defaults to %(default)s.")
    parser.add_argument("-dcp", "--disable_custom_patterns", action="store_false",
                        dest="enable_experimental",
                        help="Disable experimental patterns context.")
    parser.add_argument("-id", "--input_dtype", type=str, default="uint8",
                        help="Numpy-like dtype format to quantize the inputs")
    parser.add_argument("--input_shape",
                        type=lambda x: tuple(map(int, x.split(','))),
                        default=None,
                        help="Shape to use for input_shape (Excluding batch dimension). "
                        "Provide comma separated list for the shape. All values must be "
                        "integers > 0. e.g. --input_shape 3,256,256.")
    parser.add_argument("-s", "--save_model", type=str,
                        help="Save model to draw in Netron (not inference)")
    return parser.parse_args()


def main():
    args = get_args()

    # Load model.
    model = onnx.load(args.model)

    # Check model compatibility and convert to HybridModel.
    hybrid_model, model_compatibility_info = convert(
        model,
        input_shape=args.input_shape,
        input_dtype=args.input_dtype,
        enable_experimental=args.enable_experimental,
        initial_num_nodes=args.initial_num_nodes)

    # Print report.
    print_report(model_compatibility_info, hybrid_model)

    # Save model if needed.
    if args.save_model:
        model_compatibility_info.save_tagged_model(args.save_model)
        print(f"[INFO]: Save modified graph in {args.save_model}.")


def summary():
    """ Summary CLI entry point.

    Print the device information and the summary of the model mapped on it.

    Complete arguments lists available using the -h or --help argument.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", type=str, required=True,
                        help="Akida model or quantized model to convert.")
    parser.add_argument("-n", "--number_of_nodes", type=int, default=36,
                        help="Intial number of nodes. Defaults to %(default)s.")
    parser.add_argument("-hwpr", "--enable_hwpr", action='store_true',
                        help="Compute min device with reconfiguration. Defaults to %(default)s.")
    args = parser.parse_args()

    # Load model and convert it into akida
    model_extension = os.path.splitext(args.model.lower())[-1]

    if model_extension == '.fbz':
        model = akida.Model(args.model)
    else:
        model = load_model(args.model)
        model = cnn2snn.convert(model)

    # Compute minimum device
    device = akida.compute_min_device(model,
                                      enable_hwpr=args.enable_hwpr,
                                      initial_num_nodes=args.number_of_nodes)

    # Map model and print summary
    model.map(device, mode=akida.mapping.MapMode.Minimal, hw_only=True)
    model.summary()

    # Print basic info about device
    print("\nDevice info:")
    print("\t- Number of nps:", len(device.mesh.nps))
    skip_dmas_channels = sum([skip_dma.ident.channel for skip_dma in device.mesh.skip_dmas])
    print("\t- Number of skip dmas channels:", skip_dmas_channels)
