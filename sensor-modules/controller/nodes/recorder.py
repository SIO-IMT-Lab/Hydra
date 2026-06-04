from pathlib import Path
import asyncio

import aiofiles

from core.node import Node
from core.message_types import get_message_class
from core.utils import dict_to_csv_line, get_exchange_config


class Recorder(Node):

    def __init__(self, config: dict):
        super().__init__("recorder", config)

        self.output_dir = Path(self.node_config.get("output_dir", "/mnt/hydra_data"))
        # Create any missing parent directories in the path and 
        # prevents a FileExistsError if the directory already exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.check_permissions()

        self.subscriptions = []
        exchange_keys = self.node_config.get("subscribe_exchanges", [])
        for key in exchange_keys:
            exchange_cfg = get_exchange_config(
                {"subscribe_exchange": key}, 
                self.exchanges, 
                "subscribe_exchange"
            )
            exchange_name = exchange_cfg.get("name")
            message_type_cls = get_message_class(exchange_cfg.get("message_type"))

            sub = self.create_subscription(
                msg_type=message_type_cls,
                exchange=exchange_name,
                user_callback=self.recorder_callback_factory(exchange_name),
                binding_keys=["#"],
            )
            self.subscriptions.append(sub)

        self.header_lock = asyncio.Lock() # Prevents duplicate headers
        self.initialized_files = set()

    def check_permissions(self):
        """
        A potential problem I see is that the current user doesn't have the right
        permissions to write to the directory. Thus, this function will check that
        and raise an exception if needed.
        """
        pass

    def recorder_callback_factory(self, exchange: str):
        filename = f"{exchange}_data.csv"
        file_path = self.output_dir / filename

        async def callback(msg):
            fields = msg.csv_fields()

            async with self.header_lock:
                if file_path not in self.initialized_files:
                    file_exists = file_path.exists() and file_path.stat().st_size > 0
                    if not file_exists:
                        header = ",".join(fields) + "\n"
                        await self.write_to_file(file_path, header)
                self.initialized_files.add(file_path)

            csv_entry = dict_to_csv_line(fields, msg.to_csv_row())
            await self.write_to_file(file_path, csv_entry)

        return callback           

    async def write_to_file(self, file_path: Path, data: str):
        try:
            async with aiofiles.open(file_path, mode='a') as f:
                await f.write(data)
            self.logger.info("Wrote data to %s", file_path)
        except OSError as e:
            self.logger.error("OS error writing to %s: %s", file_path, e)
