import json
import platform
import re
import subprocess
import time
import typing
from typing import Optional, Any
from pathlib import Path

from loguru import logger

from primitive.hardware.gpu.apple import _get_supported_metal_device
from primitive.hardware.gpu.base import analyze_gpu
from primitive.hardware.gpu.nvidia import get_nvidia_gpu_config
from primitive.utils.actions import BaseAction
from primitive.utils.config import (
    PRIMITIVE_GPU_FILEPATH,
    read_config_file,
    update_config_file,
)
from primitive.utils.memory_size import MemorySize
from primitive.utils.shell import which

if typing.TYPE_CHECKING:
    pass

nvidia_vendor_id = "10de"
pcie_cap_offset_cmd = "CAP_EXP+10.w"


def run_cmd(command_list, shell=False):
    try:
        result = subprocess.run(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=shell,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exception:
        logger.error(f"Command '{command_list}' failed: {exception}")
        return ""


class GPU(BaseAction):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gpu_config = None
        self.cached_gpu_values = read_config_file(
            filepath=PRIMITIVE_GPU_FILEPATH,
        )

    def _generate_cached_gpu_values(self, gpu_config: list[dict] = []):
        update_cache = False
        if (
            self.cached_gpu_values
            and len(gpu_config) != self.cached_gpu_values.get("total_gpus", -1)
        ) or not self.cached_gpu_values:  # noqa
            if len(gpu_config) > self.cached_gpu_values.get("total_gpus", -1):
                logger.info("Found GPU count is greater than cached value.")
                update_cache = True
            elif len(gpu_config) < self.cached_gpu_values.get("total_gpus", -1):
                logger.warning("Found GPU count is less than cached value.")

        if gpu_config and update_cache:
            update_config_file(
                filepath=PRIMITIVE_GPU_FILEPATH,
                new_config={
                    "total_gpus": len(gpu_config),
                    "gpu_config": gpu_config,
                },
            )

    def _get_gpu_config(self):
        """
        For Nvidia based systems, nvidia-smi will be used to profile the gpu/s.
        For Metal based systems, we will gather information from SPDisplaysDataType.
        """
        new_gpu_config = []
        pci_based_gpus = self.get_gpus_from_lspci()
        new_gpu_config.extend(pci_based_gpus)

        new_gpu_config.extend(get_nvidia_gpu_config(gpu_config=new_gpu_config))
        new_gpu_config = sorted(new_gpu_config, key=lambda item: item["gpu_bdf"])
        if len(new_gpu_config) > 0:
            for gpu in new_gpu_config:
                self.get_bridge_control_state(gpu)
                self.test_gpu_register_access(gpu)
                self.get_link_details(gpu)
                advanced_details = analyze_gpu(gpu)
                if advanced_details:
                    gpu["advanced_details"] = advanced_details

        if platform.system() == "Darwin":
            # Check Metal gpu availability
            supported_metal_device = _get_supported_metal_device()
            if supported_metal_device is not None:
                # Since Apple's SoC contains Metal,
                # we query the system itself for total memory
                system_profiler_hardware_data_type_command = (
                    "system_profiler SPHardwareDataType -json"
                )

                try:
                    system_profiler_hardware_data_type_output = subprocess.check_output(
                        system_profiler_hardware_data_type_command.split(" ")
                    )
                except subprocess.CalledProcessError as exception:
                    message = f"Error running {system_profiler_hardware_data_type_command}: {exception}"  # noqa
                    logger.exception(message)
                    raise exception

                try:
                    system_profiler_hardware_data_type_json = json.loads(
                        system_profiler_hardware_data_type_output
                    )
                except json.JSONDecodeError as exception:
                    message = f"Error decoding JSON: {exception}"  # noqa
                    logger.exception(message)
                    raise exception

                metal_device_json = system_profiler_hardware_data_type_json[
                    "SPHardwareDataType"
                ][supported_metal_device]

                gpu_info = {}
                gpu_info["name"] = metal_device_json.get("chip_type")

                # Refactor key into B
                physical_memory = metal_device_json.get("physical_memory")
                memory_size = MemorySize(physical_memory)
                gpu_info["memory_total"] = memory_size.to_bytes()

                new_gpu_config.append(gpu_info)

        if self.gpu_config is None:
            self.gpu_config = new_gpu_config
            return self.gpu_config

        # Update existing gpu_config with new values
        # keep old gpu's that were not found in the new scan
        new_gpu_bdfs = [gpu["gpu_bdf"] for gpu in new_gpu_config]
        for gpu in new_gpu_config:
            for index, old_gpu in enumerate(self.gpu_config):
                if gpu["gpu_bdf"] == old_gpu["gpu_bdf"]:
                    self.gpu_config[index].update(gpu)
                    # if the device came back, remove fallen_off_bus flag
                    if "fallen_off_bus" in self.gpu_config[index]:
                        del self.gpu_config[index]["fallen_off_bus"]
                if old_gpu["gpu_bdf"] not in new_gpu_bdfs:
                    self.gpu_config[index]["fallen_off_bus"] = True

        self._generate_cached_gpu_values(gpu_config=self.gpu_config)
        return self.gpu_config

    def find_bridge_via_scan(self, gpu_device_number: str) -> str:
        output = subprocess.run(
            "lspci -n -d ::0604",
            encoding="utf-8",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        for line in output.splitlines():
            bridge_bdf = line.split()[0]
            secondary_bus = subprocess.run(
                f"setpci -s {bridge_bdf} SECONDARY_BUS.b",
                encoding="utf-8",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout.strip()
            if secondary_bus and secondary_bus.lower() == gpu_device_number.lower():
                return bridge_bdf
        return "Unknown"

    def get_gpus_from_lspci(self) -> list[dict[str, Any]]:
        if not which("lspci"):  # Ensure lspci is available
            logger.debug(
                "lspci command not found; cannot retrieve PCI-based GPU information."
            )
            return []
        output = subprocess.run(
            "lspci -nn -D",
            encoding="utf-8",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        devices = []
        for line in output.split("\n"):
            if not line:
                continue

            # Filter for NVIDIA (11de) or AMD (1002) Display Controllers
            if any(x in line for x in ["[10de:", "[1002:"]) and "[03" in line:
                parts = line.split(" ")
                full_gpu_bdf = parts[0]
                gpu_bdf = full_gpu_bdf.lstrip("0000:")
                gpu_device_number = full_gpu_bdf.split(":")[1]
                bridge_bdf = ""

                # sys_path = Path(f"/sys/bus/pci/devices/0000:{gpu_bdf}/parent")
                # if sys_path.exists():
                #     bridge_bdf = sys_path
                #     bridge_bdf = os.path.basename(os.path.realpath(sys_path))
                #     if bridge_bdf.startswith("0000:"):
                #         bridge_bdf = bridge_bdf[5:]
                # else:
                bridge_bdf = self.find_bridge_via_scan(
                    gpu_device_number=gpu_device_number
                )

                devices.append(
                    {
                        "gpu_bdf": gpu_bdf,
                        "bridge_bdf": bridge_bdf,
                        "name": " ".join(parts[1:]),
                        "driver": False,
                    }
                )
        return devices

    def safety_teardown(self):
        logger.info("Automating teardown (Killing processes/modules)...")

        procs = ["nvidia-smi", "nvidia-persistenced", "nv-fabricmanager"]
        for p in procs:
            logger.debug(f"Killing process: {p}")
            run_cmd(f"pkill -9 {p}", shell=True)

        modules = ["nvidia_uvm", "nvidia_drm", "nvidia_modeset", "nvidia"]
        for mod in modules:
            logger.debug(f"Unloading module: {mod}")
            run_cmd(
                ["modprobe", "-r", "-f", mod],
            )

        lsmod = run_cmd("lsmod")
        if "nvidia" in lsmod:
            logger.error("NVIDIA drivers failed to unload! Aborting.")
            return False
        return True

    def check_driver(self):
        which_result = which("nvidia-smi")
        if not which_result:
            logger.debug("nvidia-smi not found in PATH")
            return

        basic_smi_result = subprocess.run(
            "nvidia-smi", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        basic_smi_output = basic_smi_result.stdout.decode(
            "utf-8", errors="ignore"
        ).strip()
        if basic_smi_output.startswith("NVIDIA-SMI has failed"):
            logger.error(basic_smi_output)
            self.reload_driver()

    def reload_driver(self):
        logger.info("Reloading NVIDIA drivers. Takes a few seconds...")
        modules = ["nvidia_uvm", "nvidia_drm", "nvidia_modeset", "nvidia"]
        for mod in modules:
            logger.debug(f"Loading module: {mod}")
            run_cmd(["modprobe", "-i", mod])
        time.sleep(1)
        run_cmd(["nvidia-smi"])

    def get_bridge_control_state(self, device):
        bridge_bdf = device.get("bridge_bdf", None)
        if bridge_bdf == "Unknown" or bridge_bdf is None:
            return "Unknown"

        val_hex = run_cmd(["setpci", "-s", bridge_bdf, pcie_cap_offset_cmd])
        if not val_hex:
            device["bridge_control_state"] = "ERROR"
            return

        is_disabled = (int(val_hex, 16) & 0x0010) > 0
        if is_disabled:
            device["bridge_control_state"] = "DISABLED"
        else:
            device["bridge_control_state"] = "ENABLED"

    def test_gpu_register_access(self, device):
        gpu_bdf = device["gpu_bdf"]

        register_access = True
        register_access_status = "OK"

        vendor_id = run_cmd(["setpci", "-s", gpu_bdf, "0.w"])
        if not vendor_id or vendor_id.lower() == "ffff":
            register_access = False
            register_access_status = "FAIL"

        device["register_access"] = register_access
        device["register_access_status"] = register_access_status

    def get_link_details(self, device):
        """Parses lspci -vv to find negotiated Speed/Width vs Capability."""
        gpu_bdf = device["gpu_bdf"]
        out = run_cmd(f"lspci -s {gpu_bdf} -vv", shell=True)

        # Defaults
        cur_speed, cur_width = "N/A", "N/A"
        max_speed, max_width = "N/A", "N/A"

        # Parse LnkSta (Current Status)
        lnk_sta = re.search(r"LnkSta:\s+(.*)", out)
        if lnk_sta:
            s = re.search(r"Speed ([\d\.]+\w+/s)", lnk_sta.group(1))
            w = re.search(r"Width (x\d+)", lnk_sta.group(1))
            if s:
                cur_speed = s.group(1)
            if w:
                cur_width = w.group(1)

        # Parse LnkCap (Capabilities)
        lnk_cap = re.search(r"LnkCap:\s+(.*)", out)
        if lnk_cap:
            s = re.search(r"Speed ([\d\.]+\w+/s)", lnk_cap.group(1))
            w = re.search(r"Width (x\d+)", lnk_cap.group(1))
            if s:
                max_speed = s.group(1)
            if w:
                max_width = w.group(1)

        # Formatting if degraded
        speed_str = f"{cur_speed}/{max_speed}"
        link_speed_degraded = False
        if cur_speed != max_speed and cur_speed != "N/A":
            speed_str = f"{speed_str} (DEGRADED)"
            link_speed_degraded = True

        width_str = f"{cur_width}/{max_width}"
        link_width_degraded = False
        if cur_width != max_width and cur_width != "N/A":
            width_str = f"{width_str} (DEGRADED)"
            link_width_degraded = True

        device["link_speed"] = speed_str
        device["link_width"] = width_str
        device["link_speed_degraded"] = link_speed_degraded
        device["link_width_degraded"] = link_width_degraded

    def resolve_targets(self, devices, target_idx):
        if 0 <= target_idx < len(devices):
            return [devices[target_idx]]
        else:
            return []

    # --- ACTIONS ---

    def disable_link(
        self,
        bridge_bdf: str,
        gpu_bdf: Optional[str] = None,
    ):
        """Disable GPU"""
        logger.debug(
            f"DISABLING Link: {bridge_bdf if bridge_bdf else 'Unknown'} -> {gpu_bdf}"
        )
        curr_hex = run_cmd(["setpci", "-s", bridge_bdf, pcie_cap_offset_cmd])
        if curr_hex:
            new_val = int(curr_hex, 16) | 0x0010
            run_cmd(
                [
                    "setpci",
                    "-s",
                    bridge_bdf,
                    f"{pcie_cap_offset_cmd}={new_val:04x}",
                ]
            )

    def enable_link(
        self,
        bridge_bdf: str,
        gpu_bdf: Optional[str] = None,
    ):
        """Enable GPU"""
        logger.debug(
            f"ENABLING Link: {bridge_bdf if bridge_bdf else 'Unknown'} -> {gpu_bdf}"
        )
        curr_hex = run_cmd(["setpci", "-s", bridge_bdf, pcie_cap_offset_cmd])
        if curr_hex:
            new_val = int(curr_hex, 16) & 0xFFEF
            run_cmd(
                [
                    "setpci",
                    "-s",
                    bridge_bdf,
                    f"{pcie_cap_offset_cmd}={new_val:04x}",
                ]
            )

    def remove_and_rescan(self, gpu_bdf: str):
        """Remove & Rescan GPUs"""
        if not self.safety_teardown():
            return

        logger.debug(f"Removing {gpu_bdf} from kernel...")
        path = Path(f"/sys/bus/pci/devices/0000:{gpu_bdf}/remove")
        if path.exists():
            with path.open("w") as f:
                f.write("1")

        logger.debug("Triggering global rescan...")
        with Path("/sys/bus/pci/rescan").open("w") as f:
            f.write("1")
        time.sleep(2)
        self.reload_driver()

    def retrain_link(
        self,
        bridge_bdf: str,
        gpu_bdf: Optional[str] = None,
    ):
        """Retrain GPU Link"""

        logger.debug(
            f"RETRAINING Link: {gpu_bdf if gpu_bdf else 'Unknown'} -> {bridge_bdf}"
        )
        curr_hex = run_cmd(["setpci", "-s", bridge_bdf, pcie_cap_offset_cmd])
        logger.debug(f"Current PCIe Control Register Value: {curr_hex}")
        if curr_hex:
            new_val = int(curr_hex, 16) | 0x0020
            run_cmd(
                [
                    "setpci",
                    "-s",
                    bridge_bdf,
                    f"{pcie_cap_offset_cmd}={new_val:04x}",
                ]
            )

    def find_degraded_devices(self) -> list[dict[str, Any]]:
        degraded_devices = []
        for device in self._get_gpu_config():
            if (
                device.get("driver", None) is not True
                or device.get("fallen_off_bus", False)
                or device["bridge_control_state"] == "DISABLED"
                or device["register_access_status"] == "FAIL"
                or device["link_speed_degraded"]
                or device["link_width_degraded"]
            ):
                logger.warning(f"GPU at {device['gpu_bdf']} still degraded.")
                degraded_devices.append(device)
        return degraded_devices

    def handle_link_degradation(
        self,
        bridge_bdf: str,
        link_speed_degraded: bool,
        link_width_degraded: bool,
        gpu_bdf: Optional[str] = None,
    ):
        # first, we will disable and re-enable the link 3 times, waiting in between each
        for attempt in range(3):
            logger.debug(f"Link Restore Attempt {attempt + 1}/3: Disabling link...")
            self.disable_link(bridge_bdf=bridge_bdf, gpu_bdf=gpu_bdf)
            logger.debug(f"Link Restore Attempt {attempt + 1}/3: Enabling link...")
            self.enable_link(bridge_bdf=bridge_bdf, gpu_bdf=gpu_bdf)
            time.sleep(2)
            self.gpu_config = self._get_gpu_config()
            # refresh the device
            device = [d for d in self.gpu_config if d["bridge_bdf"] == bridge_bdf][0]
            if not (device["link_speed_degraded"] or device["link_width_degraded"]):
                message = f"Link restored for GPU {gpu_bdf if gpu_bdf else 'Unknown'} at BDF {bridge_bdf}: after {attempt + 1} attempts."  # noqa
                logger.debug(message)
                self.primitive.messaging.create_and_send_event(
                    event_type="LINK_RESTORE_SUCCESS",
                    severity="INFO",
                    summary=message,
                    message=message,
                )
                break

        if link_speed_degraded or link_width_degraded:
            message = f"Failed to restore link for GPU {gpu_bdf if gpu_bdf else 'Unknown'} at BDF {bridge_bdf}: after 3 attempts."  # noqa
            logger.error(message)
            self.primitive.messaging.create_and_send_event(
                event_type="LINK_RESTORE_FAILURE",
                severity="ERROR",
                summary=message,
                message=message,
            )

    def restore_nvidia_gpus(
        self,
    ):
        if not self.gpu_config:
            self.gpu_config = self._get_gpu_config()

        if not self.gpu_config:
            logger.warning("No GPU configuration found, skipping restore handler.")
            return

        self.primitive.hardware.push_own_system_info()

        # first try to handle link degradation
        degraded_devices = self.find_degraded_devices()
        for device in degraded_devices:
            self.handle_link_degradation(
                gpu_bdf=device.get("gpu_bdf", None),
                bridge_bdf=device["bridge_bdf"],
                link_speed_degraded=device["link_speed_degraded"],
                link_width_degraded=device["link_width_degraded"],
            )
        if degraded_devices:
            self.safety_teardown()
            self.reload_driver()

        degraded_devices = self.find_degraded_devices()
        if degraded_devices:
            logger.warning(
                "GPUs are unstable after reload. Attempting retrain of all GPU links."
            )
            for device in degraded_devices:
                self.retrain_link(
                    gpu_bdf=device.get("gpu_bdf", None), bridge_bdf=device["bridge_bdf"]
                )
            self.safety_teardown()
            self.reload_driver()

        degraded_devices = self.find_degraded_devices()
        self.primitive.hardware.push_own_system_info()
        if degraded_devices:
            logger.warning(
                "GPUs are unstable after reload and retrain. Asking controller to reboot the node."
            )

            self.primitive.messaging.create_and_send_event(
                event_type="REBOOT_REQUEST",
                severity="ERROR",
                message="Triggering Reboot due to unstable GPUs after XID event.",
            )
        else:
            logger.success(
                f"All {len(self.gpu_config)} / {self.cached_gpu_values.get('total_gpus', -1)} GPUs stable after restore actions."
            )
