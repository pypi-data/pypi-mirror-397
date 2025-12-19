import csv
import io
import subprocess
from shutil import which
from typing import List

from loguru import logger

from primitive.utils.memory_size import MemorySize


def get_nvidia_gpu_config(
    gpu_config: List[dict[str, str | int]] = [],
) -> List[dict[str, str | int]]:
    nvidia_gpus = []
    # Check nVidia gpu availability

    is_nvidia_smi_available = bool(which("nvidia-smi"))
    if is_nvidia_smi_available:
        nvidia_smi_query_gpu_csv_output = None
        nvidia_smi_query_gpu_csv_command = "nvidia-smi --query-gpu=gpu_name,driver_version,memory.total,pci.bus_id --format=csv"  # noqa
        try:
            nvidia_smi_query_gpu_csv_output = subprocess.check_output(
                nvidia_smi_query_gpu_csv_command.split(" "),
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as exception:
            output_text = (exception.output or b"").decode("utf-8", errors="ignore")
            if "No devices were found" in output_text:
                logger.info(
                    "nvidia-smi reports no devices were found; skipping Nvidia GPU profiling."
                )
            else:
                # see if nvidia smi itself has an error
                basic_smi_result = subprocess.run(
                    "nvidia-smi", stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                basic_smi_output = basic_smi_result.stdout.decode(
                    "utf-8", errors="ignore"
                ).strip()
                if basic_smi_output.startswith("NVIDIA-SMI has failed"):
                    logger.error(basic_smi_output)
                else:
                    message = f"Command {nvidia_smi_query_gpu_csv_command} failed with exception: {exception}"
                    logger.exception(message)

        if nvidia_smi_query_gpu_csv_output:
            try:
                nvidia_smi_query_gpu_csv_decoded = (
                    nvidia_smi_query_gpu_csv_output.decode("utf-8")
                    .replace("\r", "")
                    .replace(", ", ",")
                    .lstrip("\n")
                )
            except UnicodeDecodeError as exception:
                message = f"Error decoding: {exception}"
                logger.exception(message)
                raise exception

            # if the csv headers are not the first value, an error message was returned
            output_by_line = nvidia_smi_query_gpu_csv_decoded.split("\n")
            csv_header_index = 0
            for index, line in enumerate(output_by_line):
                if "name,driver_version,memory.total [MiB],pci.bus_id" in line:
                    csv_header_index = index
            nvidia_smi_query_gpu_csv_decoded = "\n".join(
                output_by_line[csv_header_index:]
            )

            nvidia_smi_query_gpu_csv_dict_reader = csv.DictReader(
                io.StringIO(nvidia_smi_query_gpu_csv_decoded)
            )

            for gpu_info in nvidia_smi_query_gpu_csv_dict_reader:
                # Refactor key into B
                if gpu_info.get("memory.total [MiB]", None):
                    memory_total_in_mebibytes = gpu_info.pop("memory.total [MiB]")
                    memory_size = MemorySize(memory_total_in_mebibytes)
                    gpu_info["memory_total"] = memory_size.to_bytes()

                nvidia_gpus.append(gpu_info)
    else:
        logger.debug("nvidia-smi not found; skipping nVidia GPU profiling.")

    if nvidia_gpus and gpu_config:
        for nvidia_gpu in nvidia_gpus:
            nvidia_pci_bus_id = nvidia_gpu.get("pci.bus_id", "").lower()
            for pci_index, pci_based_gpu in enumerate(gpu_config):
                pci_based_gpu_bdf = pci_based_gpu.get("gpu_bdf", "").lower()
                if nvidia_pci_bus_id and pci_based_gpu_bdf:
                    if pci_based_gpu_bdf in nvidia_pci_bus_id:
                        nvidia_gpu["driver"] = True
                        nvidia_gpu["gpu_bdf"] = pci_based_gpu_bdf
                        nvidia_gpu["pci_name"] = pci_based_gpu.get("name", "")
                        nvidia_gpu["bridge_bdf"] = pci_based_gpu.get("bridge_bdf", "")
                        gpu_config.pop(pci_index)
                        break
    return nvidia_gpus
