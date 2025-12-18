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
__all__ = ["experimental_context"]

import os
from contextlib import contextmanager

EXPERIMENTAL_ENV = "EXPERIMENTAL_PATTERNS"


@contextmanager
def experimental_context(enable):
    """Enable or disable experimental context

    Args:
        enable (bool): True to enable context, False to disable it
    """
    value = "1" if enable else "0"
    _prev_state = os.environ.get(EXPERIMENTAL_ENV, None)
    try:
        os.environ[EXPERIMENTAL_ENV] = value
        yield
    finally:
        # Recover default value
        if _prev_state is not None:
            os.environ[EXPERIMENTAL_ENV] = _prev_state
        else:
            os.environ.pop(EXPERIMENTAL_ENV)
