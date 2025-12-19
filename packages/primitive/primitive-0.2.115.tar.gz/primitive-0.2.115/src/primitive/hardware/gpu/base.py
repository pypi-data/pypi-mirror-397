import subprocess
from typing import Literal, Any
from loguru import logger
# NOTES:
# - bdf stands for Bus:Device.Function

# --- Constants ---
PCI_CAP_ID_EXP = 0x10  # Standard PCIe Cap
PCI_EXT_CAP_ID_AER = 0x0001  # Extended AER Cap


def read_registry(
    bdf: str,
    offset: int,
    width: Literal[
        "b",
        "w",
        "l",
    ] = "l",
) -> int:
    result = (
        subprocess.check_output(
            f"setpci -s {bdf} {offset:x}.{width}",
            shell=True,
            stderr=subprocess.STDOUT,
        )
        .decode()
        .strip()
    )
    return int(result, 16) if result else 0


def write_registry(
    bdf: str,
    offset: int,
    val: int,
    width: Literal[
        "b",
        "w",
        "l",
    ] = "l",
) -> None:
    subprocess.check_output(
        f"setpci -s {bdf} {offset:x}.{width}={val:x}".split(),
        shell=True,
        stderr=subprocess.STDOUT,
    ).decode().strip()


def find_cap(gpu_bdf, cap_id):
    # Standard Cap Walk (Starts at 0x34)
    status = read_registry(gpu_bdf, 0x06, "w")
    if not (status & 0x10):
        return 0  # Cap list not present

    next_ptr = read_registry(gpu_bdf, 0x34, "b")
    limit = 48
    while next_ptr != 0 and limit > 0:
        limit -= 1
        cap = read_registry(gpu_bdf, next_ptr, "b")
        if cap == cap_id:
            return next_ptr
        next_ptr = read_registry(gpu_bdf, next_ptr + 1, "b")
    return 0


def find_ext_cap(gpu_bdf, cap_id):
    # Extended Cap Walk (Starts at 0x100)
    # Only works if config space > 256 bytes (PCIe)
    next_ptr = 0x100
    limit = 96
    while next_ptr != 0 and limit > 0:
        limit -= 1
        # Read Header (32 bits): [Next:20-31][Ver:16-19][ID:0-15]
        header = read_registry(gpu_bdf, next_ptr, "l")
        if header == 0 or header == 0xFFFFFFFF:
            break

        curr_id = header & 0xFFFF
        if curr_id == cap_id:
            return next_ptr

        next_ptr = (header >> 20) & 0xFFF
        if next_ptr < 0x100:
            break  # Should not point backwards/null
    return 0


def get_correctable_errors(gpu_bdf):
    aer_base = find_ext_cap(gpu_bdf, PCI_EXT_CAP_ID_AER)
    if not aer_base:
        logger.debug(
            "get_correctable_errors: No Extended AER Capability found (Hardware might not support it)"
        )
        return

    correctable_error_status = read_registry(gpu_bdf, aer_base + 0x10, "l")
    message = None
    if correctable_error_status:
        if correctable_error_status & 0x01:
            message = "Receiver Error (Physical Layer issue!)"
        elif correctable_error_status & 0x40:
            message = "Bad TLP"
        elif correctable_error_status & 0x80:
            message = "Bad DLLP"
        elif correctable_error_status & 0x100:
            message = "REPLAY_NUM Rollover"
        elif correctable_error_status & 0x1000:
            message = "Replay Timer Timeout"
        elif correctable_error_status & 0x2000:
            message = "Advisory Non-Fatal Error"

    if message:
        logger.warning(
            f"Correctable Errors Detected (Raw: {hex(correctable_error_status)}) - {message}"
        )
    else:
        message = "No correctable errors detected."

    correctable_error = {"status": correctable_error_status, "message": message}

    return correctable_error


def get_uncorrectable_errors(gpu_bdf):
    aer_base = find_ext_cap(gpu_bdf, PCI_EXT_CAP_ID_AER)
    if not aer_base:
        logger.debug(
            "get_uncorrectable_errors: No Extended AER Capability found (Hardware might not support it)"
        )
        return None

    uncorrectable_error_status = read_registry(gpu_bdf, aer_base + 0x04, "l")
    message = None
    if uncorrectable_error_status:
        if uncorrectable_error_status & 0x10:
            message = "Data Link Protocol Error"
        elif uncorrectable_error_status & 0x1000:
            message = "Poisoned TLP"
        elif uncorrectable_error_status & 0x4000:
            message = "Completion Timeout"
        if uncorrectable_error_status & 0x8000:
            message = "Completer Abort"
        if uncorrectable_error_status & 0x10000:
            message = "Unexpected Completion"
        if uncorrectable_error_status & 0x20000:
            message = "Receiver Overflow"
        if uncorrectable_error_status & 0x40000:
            message = "Malformed TLP"
        if uncorrectable_error_status & 0x80000:
            message = "ECRC Error"
        if uncorrectable_error_status & 0x200000:
            message = "Unsupported Request Error"

    if message:
        logger.error(
            f"Uncorrectable Errors Detected (Raw: {hex(uncorrectable_error_status)}) - {message}"
        )
    else:
        message = "No uncorrectable errors detected."

    uncorrectable_error = {"status": uncorrectable_error_status, "message": message}

    return uncorrectable_error


def analyze_gpu(device) -> dict[str, Any]:
    gpu_bdf = device["gpu_bdf"]
    logger.debug(f"\nAnalyzing {gpu_bdf}...")

    pcie_cap = find_cap(gpu_bdf, PCI_CAP_ID_EXP)
    if not pcie_cap:
        logger.debug("No PCIe Cap found.")
        return {}

    # Link Status
    link_status = read_registry(gpu_bdf, pcie_cap + 0x12, "w")
    speed = link_status & 0xF
    width = (link_status >> 4) & 0x3F
    logger.debug(f"Current Link: Gen{speed} x{width}")

    # Basic Device Status Summary
    device_status = read_registry(gpu_bdf, pcie_cap + 0x0A, "w")
    logger.debug(f"Summary Error Flags: {hex(device_status)}")
    if device_status & 0xF:
        logger.debug("  (Summary bits set, checking AER details...)")

    correctable_errors = get_correctable_errors(gpu_bdf)
    uncorrectable_errors = get_uncorrectable_errors(gpu_bdf)

    return {
        "device_status": device_status,
        "correctable_errors": correctable_errors,
        "uncorrectable_errors": uncorrectable_errors,
    }
