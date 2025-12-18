import platform
from primitive.utils.actions import BaseAction
from subprocess import PIPE, Popen
from loguru import logger
from datetime import datetime, timedelta
from primitive.utils.shell import does_executable_exist
import re


class RootComplex(BaseAction):
    def __init__(self, primitive):
        super().__init__(primitive)
        self.can_parse_journalctl = (
            platform.system() == "Linux" and does_executable_exist("journalctl")
        )
        self.latest_journalctl_timestamp = datetime.now() - timedelta(minutes=60)

    def write_to_kmsg(self, message: str = "hello from python"):
        # 6 = KERN_INFO
        msg = "<6>{}\n".format(message)

        with open("/dev/kmsg", "w") as f:
            f.write(msg)

    def parse_journalctl(self):
        if not self.can_parse_journalctl:
            logger.warning("Cannot parse journalctl on this system.")
            return

        with Popen(
            [
                "journalctl",
                "--boot=0",
                "--dmesg",
                "--since="
                + str(self.latest_journalctl_timestamp.strftime("%b %d %H:%M:%S")),
            ],
            stdout=PIPE,
        ) as process:
            for line in process.stdout.read().decode("utf-8").split("\n"):
                if line == "" or not line:
                    continue

                try:
                    ts_part = " ".join(line.split()[:3])  # e.g. "Dec 09 18:31:22"
                    line_timestamp = datetime.strptime(
                        ts_part, "%b %d %H:%M:%S"
                    ).replace(year=datetime.now().year)
                except Exception as exception:
                    logger.error(
                        "Error parsing timestamp from line: {}: {}", line, exception
                    )
                    continue

                self.latest_journalctl_timestamp = line_timestamp
                # this is where do we do logic if we see the problem
                logger.debug("New dmesg line: {}", line)
                if "NVRM: Xid" in line:
                    logger.warning("Found actionable dmesg line: {}", line)

                    xid_detail = None
                    nvrm_message = re.search(r"NVRM: Xid.*?,\s*\d+,\s*(.*)$", line)
                    if nvrm_message:
                        xid_detail = nvrm_message.group(1).strip()
                        logger.debug("Parsed XID detail: {}", xid_detail)

                    self.primitive.messaging.create_and_send_event(
                        event_type="XID_EVENT",
                        severity="ERROR",
                        correlation_id="test-correlation-id",
                        summary=f"nVidia XID Event: {xid_detail}",
                        message=line,
                        metadata={"key": "value"},
                    )
                else:
                    continue
