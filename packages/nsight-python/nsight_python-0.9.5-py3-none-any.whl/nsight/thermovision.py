# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import time
from typing import Any

"""
This module provides GPU thermal monitoring and throttling prevention using NVIDIA's NVML library.

It monitors GPU temperature and T.limit, and delays execution when the GPU
is too hot to avoid thermal throttling. Initialization is done lazily when needed.
"""

# Guard NVML imports
try:
    from pynvml import (
        NVML_TEMPERATURE_GPU,
        NVMLError_NotSupported,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetMarginTemperature,
        nvmlDeviceGetTemperature,
        nvmlInit,
    )

    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    print(
        "Warning: Cannot import pynvml (provided by nvidia-ml-py). Ensure nsight-python was installed properly with all dependencies."
    )

HANDLE: Any = None  # Will be initialized lazily


def init() -> bool:
    """
    Initializes the thermovision module by setting up the necessary hardware handle
    and checking if temperature retrieval is supported.

    Returns:
        True if temperature retrieval is supported, False otherwise.

    Notes:
        - This function uses the NVML (NVIDIA Management Library) to initialize
          the GPU handle if the handle has not been set.
        - The global variable `HANDLE` is used to store the GPU handle.
    """

    if not PYNVML_AVAILABLE:
        return False

    global HANDLE
    if HANDLE is None:
        nvmlInit()
        HANDLE = nvmlDeviceGetHandleByIndex(0)

    return is_temp_retrieval_supported()


def throttle_guard(wait_threshold: int = 10, continue_threshold: int = 40) -> None:
    """
    Delays execution if the GPU T.limit is below a specified threshold.

    This function polls the GPU T.limit using NVML, and if it's below the `wait_threshold`,
    it waits until it reaches at least the `continue_threshold`, checking at regular intervals.

    Args:
        wait_threshold: The T.limit value below which execution is paused.
        Default: ``10``
        continue_threshold: The T.limit value at or above which execution resumes.
        Default: ``40``
    """

    tlimit = get_gpu_tlimit(HANDLE)
    if tlimit is None:
        return

    if tlimit <= wait_threshold:
        while tlimit is not None and tlimit < continue_threshold:
            temperature = get_gpu_temp(HANDLE)
            tlimit = get_gpu_tlimit(HANDLE)
            print(
                f"Waiting for GPU to cool down. Current temperature: {temperature}°C, T.limit: {tlimit}"
            )
            time.sleep(0.5)


def is_temp_retrieval_supported() -> bool:
    """
    Checks if the GPU supports temperature retrieval.
    """
    try:
        nvmlDeviceGetMarginTemperature(HANDLE)
        return True
    except Exception as e:
        print("Warning: Nsight Python Thermovision is not supported on this machine")
        return False


def get_gpu_tlimit(handle: Any) -> int | None:
    """
    Returns the GPU T.Limit temparature for the given device handle.
    """
    try:
        return nvmlDeviceGetMarginTemperature(handle)  # type: ignore[no-any-return]
    except NVMLError_NotSupported as e:
        # Handle the case where the GPU does not support this feature
        print("Error: GPU does not support temperature limit retrieval:", e)
        return None
    except Exception as e:
        raise e


def get_gpu_temp(handle: Any) -> int:
    return nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)  # type: ignore[no-any-return]
