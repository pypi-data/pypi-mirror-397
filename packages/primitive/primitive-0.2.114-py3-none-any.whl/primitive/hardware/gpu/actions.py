from pathlib import Path
import typing
import time
import re
import subprocess
from loguru import logger
import json
import platform
from primitive.hardware.gpu.base import analyze_gpu
from primitive.utils.shell import which
from primitive.utils.actions import BaseAction
from primitive.hardware.gpu.nvidia import get_nvidia_gpu_config
from primitive.hardware.gpu.apple import _get_supported_metal_device
from primitive.utils.memory_size import MemorySize

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
    except Exception:
        return ""


class GPU(BaseAction):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gpu_config = self._get_gpu_config()

    def _get_gpu_config(self):
        """
        For Nvidia based systems, nvidia-smi will be used to profile the gpu/s.
        For Metal based systems, we will gather information from SPDisplaysDataType.
        """
        gpu_config = []
        pci_based_gpus = self.get_gpus_from_lspci()
        gpu_config.extend(pci_based_gpus)

        gpu_config.extend(get_nvidia_gpu_config(gpu_config=gpu_config))
        if len(gpu_config) > 0:
            for gpu in gpu_config:
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

                gpu_config.append(gpu_info)

        return gpu_config

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

    def get_gpus_from_lspci(self) -> list[dict[str, typing.Any]]:
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
                    }
                )
        return devices

    def safety_teardown(self):
        logger.info("Automating teardown (Killing processes/modules)...")

        procs = ["nvidia-smi", "nvidia-persistenced", "nv-fabricmanager"]
        for p in procs:
            logger.info(f"Killing process: {p}")
            run_cmd(f"pkill -9 {p}", shell=True)

        modules = ["nvidia_uvm", "nvidia_drm", "nvidia_modeset", "nvidia"]
        for mod in modules:
            logger.info(f"Unloading module: {mod}")
            subprocess.run(
                ["rmmod", "-f", mod],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        lsmod = run_cmd("lsmod")
        if "nvidia" in lsmod:
            logger.error("[DANGER] NVIDIA drivers failed to unload! Aborting.")
            return False
        return True

    def reload_driver(self):
        logger.info("Reloading NVIDIA drivers...")
        run_cmd(["modprobe", "nvidia"])
        run_cmd(["modprobe", "nvidia_uvm"])
        time.sleep(1)
        run_cmd(["nvidia-smi"])

    def get_bridge_control_state(self, device):
        bridge_bdf = device["bridge_bdf"]
        if bridge_bdf == "Unknown":
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
        if cur_speed != max_speed and cur_speed != "N/A":
            speed_str = f"{speed_str} (DEGRADED)"

        width_str = f"{cur_width}/{max_width}"
        if cur_width != max_width and cur_width != "N/A":
            width_str = f"{width_str} (DEGRADED)"

        device["link_speed"] = speed_str
        device["link_width"] = width_str

    def resolve_targets(self, devices, target_idx):
        if 0 <= target_idx < len(devices):
            return [devices[target_idx]]
        else:
            return []

    # --- ACTIONS ---

    def disable_link(self):
        """Disable GPU"""
        if not self.gpu_config:
            logger.warning("No GPU configuration found, skipping disable_link.")
            return
        device = self.gpu_config[0]
        if device["bridge_bdf"] == "Unknown":
            logger.warning("Bridge device unknown, cannot disable link.")
            return

        logger.info(f"DISABLING Link: {device['bridge_bdf']} -> {device['gpu_bdf']}")
        curr_hex = run_cmd(["setpci", "-s", device["bridge_bdf"], pcie_cap_offset_cmd])
        if curr_hex:
            new_val = int(curr_hex, 16) | 0x0010
            run_cmd(
                [
                    "setpci",
                    "-s",
                    device["bridge_bdf"],
                    f"{pcie_cap_offset_cmd}={new_val:04x}",
                ]
            )

    def enable_link(self):
        """Enable GPU"""
        if not self.gpu_config:
            logger.warning("No GPU configuration found, skipping enable_link.")
            return

        device = self.gpu_config[0]
        if device["bridge_bdf"] == "Unknown":
            logger.warning("Bridge device unknown, cannot enable link.")
            return
        logger.info(f"ENABLING Link: {device['bridge_bdf']} -> {device['gpu_bdf']}")
        curr_hex = run_cmd(["setpci", "-s", device["bridge_bdf"], pcie_cap_offset_cmd])
        if curr_hex:
            new_val = int(curr_hex, 16) & 0xFFEF
            run_cmd(
                [
                    "setpci",
                    "-s",
                    device["bridge_bdf"],
                    f"{pcie_cap_offset_cmd}={new_val:04x}",
                ]
            )

    def remove_and_rescan(self):
        """Remove & Rescan GPUs"""
        if not self.gpu_config:
            logger.warning("No GPU configuration found, skipping remove_and_rescan.")
            return

        device = self.gpu_config[0]
        if device["bridge_bdf"] == "Unknown":
            logger.warning("Bridge device unknown, cannot remove and rescan.")
            return

        if not self.safety_teardown():
            return

        logger.info(f"Removing {device['gpu_bdf']} from kernel...")
        path = Path(f"/sys/bus/pci/devices/0000:{device['gpu_bdf']}/remove")
        if path.exists():
            with path.open("w") as f:
                f.write("1")

        logger.info("Triggering global rescan...")
        with Path("/sys/bus/pci/rescan").open("w") as f:
            f.write("1")
        time.sleep(2)
        self.reload_driver()

    def retrain_link(self):
        """Retrain GPU Link"""
        if not self.gpu_config:
            logger.warning("No GPU configuration found, skipping retrain_link.")
            return

        device = self.gpu_config[0]
        if device["bridge_bdf"] == "Unknown":
            logger.warning("Bridge device unknown, cannot retrain link.")
            return
        logger.info(f"RETRAINING Link: {device['bridge_bdf']} -> {device['gpu_bdf']}")
        curr_hex = run_cmd(["setpci", "-s", device["bridge_bdf"], pcie_cap_offset_cmd])
        logger.info(f"Current PCIe Control Register Value: {curr_hex}")
        if curr_hex:
            new_val = int(curr_hex, 16) | 0x0020
            run_cmd(
                [
                    "setpci",
                    "-s",
                    device["bridge_bdf"],
                    f"{pcie_cap_offset_cmd}={new_val:04x}",
                ]
            )
