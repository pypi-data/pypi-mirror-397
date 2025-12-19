import platform
from primitive.utils.actions import BaseAction
from subprocess import PIPE, Popen
from loguru import logger
from datetime import datetime, timedelta
from primitive.utils.shell import does_executable_exist
from primitive.utils.config import update_config_file

IDENTIFIER_NVRM_XID = "NVRM: Xid"
IDENTIFIER_GPU_HANG = "GPU HANG"
IDENTIFIER_GPU_FAULT = "GPU fault"


class RootComplex(BaseAction):
    def __init__(self, primitive):
        super().__init__(primitive)
        self.can_parse_journalctl = (
            platform.system() == "Linux" and does_executable_exist("journalctl")
        )

        if config_journalctl_timestamp := self.primitive.host_config.get(
            "latest_journalctl_timestamp", None
        ):
            try:
                self.latest_journalctl_timestamp = datetime.fromisoformat(
                    config_journalctl_timestamp
                )
            except Exception as exception:
                logger.error(
                    "Error parsing latest_journalctl_timestamp from config: {}",
                    exception,
                )
        else:
            self.latest_journalctl_timestamp = datetime.now() - timedelta(minutes=60)

        self.previous_messages = set()
        self.actionable_identifiers = [
            IDENTIFIER_NVRM_XID,
            IDENTIFIER_GPU_HANG,
            IDENTIFIER_GPU_FAULT,
        ]
        self.should_restore_nvidia_gpus = False

    def reset_settings(self):
        # when we start reading the next block of journalctl logs, reset state
        self.should_restore_nvidia_gpus = False

    def write_timestamp(self):
        if self.primitive.host_config is not None:
            self.primitive.host_config["latest_journalctl_timestamp"] = (
                self.latest_journalctl_timestamp.isoformat()
            )
            update_config_file(
                new_config={self.primitive.host: self.primitive.host_config}
            )

    def handle_side_effects(self):
        # based on the set of messages seen in the last loop, take a single action
        if self.should_restore_nvidia_gpus:
            self.primitive.gpu.restore_nvidia_gpus()
        self.reset_settings()

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
            if process.stdout is None:
                logger.error("Failed to read journalctl output.")
                return

            for line in process.stdout.read().decode("utf-8").split("\n"):
                if line is None:
                    continue

                if line.strip() == "":
                    continue

                try:
                    ts_part = " ".join(line.split()[:3])  # e.g. "Dec 09 18:31:22"
                    line_timestamp = datetime.strptime(
                        ts_part, "%b %d %H:%M:%S"
                    ).replace(year=datetime.now().year)
                except Exception as exception:
                    if "No entries" in line:
                        logger.info("No new journalctl entries since last check.")
                        continue
                    logger.debug(
                        "Error parsing timestamp from line: {}: {}", line, exception
                    )
                    continue

                if line_timestamp > self.latest_journalctl_timestamp:
                    self.write_timestamp()
                    self.previous_messages = set()

                self.latest_journalctl_timestamp = line_timestamp
                # this is where do we do logic if we see the problem
                logger.debug("New dmesg line: {}", line)

                if any(
                    identifier in line for identifier in self.actionable_identifiers
                ):
                    if line in self.previous_messages:
                        continue

                    self.previous_messages.add(line)

                    logger.warning("Found actionable dmesg line: {}", line)

                    if IDENTIFIER_NVRM_XID in line:
                        self.should_restore_nvidia_gpus = True

                        self.primitive.messaging.create_and_send_event(
                            event_type="XID",
                            severity="ERROR",
                            summary=f"nVidia XID Event: {line}",
                            message=line,
                            timestamp=line_timestamp,
                        )

                else:
                    continue

        self.handle_side_effects()
