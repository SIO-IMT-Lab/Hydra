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

    def recorder_callback_factory(self, exchange: str):
        filename = f"{exchange}_data.csv"
        file_path = self.output_dir / filename

        async def callback(msg):
            if not file_path.exists():
                await self.write_to_file(file_path, msg.csv_header() + "\n")
            csv_entry = dict_to_csv_line(msg.csv_header(), msg.to_csv_row())
            await self.write_to_file(file_path, csv_entry)

        return callback           

    # TODO: Move this into another utility module or something, since we'll
    #       probably want to use it in other places too
    async def write_to_file(self, file_path: Path, data: str):
        try:
            async with aiofiles.open(file_path, mode='a') as f:
                await f.write(data)
            print(f"[INFO] Wrote data to {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

