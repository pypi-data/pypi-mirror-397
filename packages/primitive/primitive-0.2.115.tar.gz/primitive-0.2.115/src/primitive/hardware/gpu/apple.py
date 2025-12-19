import json
import subprocess
import typing

from loguru import logger


if typing.TYPE_CHECKING:
    pass

from primitive.utils.shell import which


def _get_supported_metal_device() -> int | None:
    """
    Checks if metal hardware is supported. If so, the index
    of the supported metal device is returned
    """
    supported_metal_device = None
    is_system_profiler_available = bool(which("system_profiler"))
    if is_system_profiler_available:
        system_profiler_display_data_type_command = (
            "system_profiler SPDisplaysDataType -json"
        )
        try:
            system_profiler_display_data_type_output = subprocess.check_output(
                system_profiler_display_data_type_command.split(" ")
            )
        except subprocess.CalledProcessError as exception:
            message = f"Error running system_profiler: {exception}"
            logger.exception(message)
            return supported_metal_device

        try:
            system_profiler_display_data_type_json = json.loads(
                system_profiler_display_data_type_output
            )
        except json.JSONDecodeError as exception:
            message = f"Error decoding JSON: {exception}"
            logger.exception(message)
            return supported_metal_device

        # Checks if any attached displays have metal support
        # Note, other devices here could be AMD GPUs or unconfigured Nvidia GPUs
        for index, display in enumerate(
            system_profiler_display_data_type_json["SPDisplaysDataType"]
        ):
            if "spdisplays_mtlgpufamilysupport" in display:
                supported_metal_device = index
                return supported_metal_device

    return supported_metal_device
