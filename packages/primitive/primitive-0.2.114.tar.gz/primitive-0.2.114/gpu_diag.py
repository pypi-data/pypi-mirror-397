#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import time
import re

# ==============================================================================
# Constants & Colors
# ==============================================================================
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


class PciGpuDiag:
    def __init__(self):
        if os.geteuid() != 0:
            print(f"{RED}Error: Must run as root.{RESET}")
            sys.exit(1)

        self.nvidia_vendor_id = "10de"
        self.pcie_cap_offset_cmd = "CAP_EXP+10.w"

        # Locate utilities
        self.lspci_cmd = shutil.which("lspci")
        if not self.lspci_cmd:
            for path in [
                "/usr/sbin/lspci",
                "/sbin/lspci",
                "/usr/bin/lspci",
                "/bin/lspci",
            ]:
                if os.path.exists(path):
                    self.lspci_cmd = path
                    break

        if not self.lspci_cmd:
            print(f"{RED}CRITICAL: 'lspci' not found.{RESET}")
            sys.exit(1)

        self.setpci_cmd = shutil.which("setpci") or "setpci"

    def run_cmd(self, command_list, shell=False):
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

    # --- SAFETY AUTOMATION ---
    def safety_teardown(self):
        print(
            f"{YELLOW}[SAFETY] Automating teardown (Killing processes/modules)...{RESET}"
        )

        procs = ["nvidia-smi", "nvidia-persistenced", "nv-fabricmanager"]
        for p in procs:
            self.run_cmd(f"pkill -9 {p}", shell=True)

        modules = ["nvidia_uvm", "nvidia_drm", "nvidia_modeset", "nvidia"]
        for mod in modules:
            subprocess.run(
                ["rmmod", "-f", mod],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        lsmod = self.run_cmd("lsmod")
        if "nvidia" in lsmod:
            print(f"{RED}[DANGER] NVIDIA drivers failed to unload! Aborting.{RESET}")
            return False
        return True

    def reload_driver(self):
        print(f"{GREEN}[INFO] Reloading NVIDIA drivers...{RESET}")
        self.run_cmd(["modprobe", "nvidia"])
        self.run_cmd(["modprobe", "nvidia_uvm"])
        time.sleep(1)
        self.run_cmd(["nvidia-smi"])

    # --- DISCOVERY & STATUS ---
    def find_bridge_via_scan(self, gpu_bdf):
        try:
            gpu_bus_hex = gpu_bdf.split(":")[0]
        except Exception:
            return "Unknown"
        out = self.run_cmd(f"{self.lspci_cmd} -n -d ::0604", shell=True)
        for line in out.splitlines():
            bridge_bdf = line.split()[0]
            sec_bus = self.run_cmd(
                [self.setpci_cmd, "-s", bridge_bdf, "SECONDARY_BUS.b"]
            )
            if sec_bus and sec_bus.lower() == gpu_bus_hex.lower():
                return bridge_bdf
        return "Unknown"

    def get_nvidia_topology(self):
        print(f"{YELLOW}... Scanning PCIe topology ...{RESET}")
        cmd = f"{self.lspci_cmd} -d {self.nvidia_vendor_id}: -n"
        lspci_out = self.run_cmd(cmd, shell=True)

        devices = []
        for line in lspci_out.splitlines():
            if not line:
                continue
            parts = line.split()
            bdf = parts[0]
            class_code = parts[1].strip(":")
            if class_code.startswith("03"):
                sys_path = f"/sys/bus/pci/devices/0000:{bdf}/parent"
                if os.path.exists(sys_path):
                    bridge_bdf = os.path.basename(os.path.realpath(sys_path))
                    if bridge_bdf.startswith("0000:"):
                        bridge_bdf = bridge_bdf[5:]
                else:
                    bridge_bdf = self.find_bridge_via_scan(bdf)
                devices.append({"gpu": bdf, "bridge": bridge_bdf})
        devices.sort(key=lambda x: x["gpu"])
        return devices

    def get_bridge_control_state(self, bridge_bdf):
        if bridge_bdf == "Unknown":
            return f"{RED}Unknown{RESET}"
        val_hex = self.run_cmd(
            [self.setpci_cmd, "-s", bridge_bdf, self.pcie_cap_offset_cmd]
        )
        if not val_hex:
            return "Error"
        is_disabled = (int(val_hex, 16) & 0x0010) > 0
        return f"{RED}DISABLED{RESET}" if is_disabled else f"{GREEN}Active{RESET}"

    def test_gpu_register_access(self, gpu_bdf):
        vendor_id = self.run_cmd([self.setpci_cmd, "-s", gpu_bdf, "0.w"])
        if not vendor_id or vendor_id.lower() == "ffff":
            return False, f"{RED}FAIL{RESET}"
        return True, f"{GREEN}OK{RESET}"

    def get_link_details(self, gpu_bdf):
        """Parses lspci -vv to find negotiated Speed/Width vs Capability."""
        out = self.run_cmd(f"{self.lspci_cmd} -s {gpu_bdf} -vv", shell=True)

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

        # Formatting colors if degraded
        speed_str = f"{cur_speed}/{max_speed}"
        if cur_speed != max_speed and cur_speed != "N/A":
            speed_str = f"{YELLOW}{speed_str}{RESET}"

        width_str = f"{cur_width}/{max_width}"
        if cur_width != max_width and cur_width != "N/A":
            width_str = f"{YELLOW}{width_str}{RESET}"

        return speed_str, width_str

    # --- ACTIONS ---
    def disable_link(self, devices, target_idx):
        targets = self.resolve_targets(devices, target_idx)
        if not targets:
            return

        for dev in targets:
            if dev["bridge"] == "Unknown":
                continue
            print(f"DISABLING Link: {dev['bridge']} -> {dev['gpu']}")
            curr_hex = self.run_cmd(
                [self.setpci_cmd, "-s", dev["bridge"], self.pcie_cap_offset_cmd]
            )
            if curr_hex:
                new_val = int(curr_hex, 16) | 0x0010
                self.run_cmd(
                    [
                        self.setpci_cmd,
                        "-s",
                        dev["bridge"],
                        f"{self.pcie_cap_offset_cmd}={new_val:04x}",
                    ]
                )
        time.sleep(0.5)
        self.print_status(targets)

    def enable_link(self, devices, target_idx):
        targets = self.resolve_targets(devices, target_idx)
        if not targets:
            return

        for dev in targets:
            if dev["bridge"] == "Unknown":
                continue
            print(f"ENABLING Link: {dev['bridge']} -> {dev['gpu']}")
            curr_hex = self.run_cmd(
                [self.setpci_cmd, "-s", dev["bridge"], self.pcie_cap_offset_cmd]
            )
            if curr_hex:
                new_val = int(curr_hex, 16) & 0xFFEF
                self.run_cmd(
                    [
                        self.setpci_cmd,
                        "-s",
                        dev["bridge"],
                        f"{self.pcie_cap_offset_cmd}={new_val:04x}",
                    ]
                )
        print("Waiting 2s for training...")
        time.sleep(2)
        self.print_status(targets)

    def retrain_link(self, devices, target_idx):
        targets = self.resolve_targets(devices, target_idx)
        if not targets:
            return

        for dev in targets:
            if dev["bridge"] == "Unknown":
                continue
            print(f"RETRAINING Link: {dev['bridge']} -> {dev['gpu']}")
            curr_hex = self.run_cmd(
                [self.setpci_cmd, "-s", dev["bridge"], self.pcie_cap_offset_cmd]
            )
            if curr_hex:
                new_val = int(curr_hex, 16) | 0x0020
                self.run_cmd(
                    [
                        self.setpci_cmd,
                        "-s",
                        dev["bridge"],
                        f"{self.pcie_cap_offset_cmd}={new_val:04x}",
                    ]
                )
        print("Waiting 2s for link negotiation...")
        time.sleep(2)
        self.print_status(targets)

    def remove_and_rescan(self, devices, target_idx):
        targets = self.resolve_targets(devices, target_idx)
        if not self.safety_teardown():
            return

        if targets:
            for dev in targets:
                print(f"Removing {dev['gpu']} from kernel...")
                path = f"/sys/bus/pci/devices/0000:{dev['gpu']}/remove"
                if os.path.exists(path):
                    with open(path, "w") as f:
                        f.write("1")

        print("Triggering global rescan...")
        with open("/sys/bus/pci/rescan", "w") as f:
            f.write("1")
        time.sleep(2)
        self.reload_driver()

    def resolve_targets(self, devices, target_idx):
        if 0 <= target_idx < len(devices):
            return [devices[target_idx]]
        else:
            return []

    def print_status(self, devices):
        print("\n" + "=" * 135)
        print(
            f"{'IDX':<4} | {'GPU BDF':<10} | {'BRIDGE':<10} | {'STATE':<14} | {'REG TEST':<14} | {'SPEED (Cur/Max)':<20} | {'WIDTH (Cur/Max)'}"
        )
        print("-" * 135)
        for i, dev in enumerate(devices):
            bridge_state = self.get_bridge_control_state(dev["bridge"])
            is_up, msg = self.test_gpu_register_access(dev["gpu"])

            # Get Link Details
            speed_str, width_str = "N/A", "N/A"
            if is_up:
                speed_str, width_str = self.get_link_details(dev["gpu"])

            print(
                f"{i:<4} | {dev['gpu']:<10} | {dev['bridge']:<10} | {bridge_state:<14} | {msg:<14} | {speed_str:<20} | {width_str}"
            )
        print("=" * 135 + "\n")

    def interactive_menu(self):
        devices = self.get_nvidia_topology()
        if not devices:
            print(f"{YELLOW}No devices found via scan.{RESET}")

        while True:
            print(f"\n{YELLOW}PCIe Diag Tool v7{RESET}")
            print("1. Status")
            print("2. DISABLE Link (Kill)")
            print("3. ENABLE Link (Restore)")
            print("4. Remove & Rescan (Safe)")
            print("5. Retrain Link")
            print("6. Exit")

            choice = input("Option: ")

            if choice == "1":
                devices = self.get_nvidia_topology()
                if devices:
                    self.print_status(devices)
            elif choice == "2":
                self.disable_link(devices, self.get_selection(devices))
            elif choice == "3":
                self.enable_link(devices, self.get_selection(devices))
            elif choice == "4":
                if not devices:
                    devices = self.get_nvidia_topology()
                self.remove_and_rescan(devices, self.get_selection(devices))
                devices = self.get_nvidia_topology()
            elif choice == "5":
                self.retrain_link(devices, self.get_selection(devices))
            elif choice == "6":
                sys.exit(0)

    def get_selection(self, devices):
        if not devices:
            return -2
        self.print_status(devices)
        sel = input("Enter Index: ")
        return int(sel) if sel.isdigit() else -2


if __name__ == "__main__":
    PciGpuDiag().interactive_menu()
