from pathlib import Path
import asyncio

import aiofiles

from core.node import Node
from core.message_types import get_message_class, SensorData


class Recorder(Node):

    def __init__(self, config: dict):
        super().__init__("recorder", config)

        self.output_dir = Path(self.config.get("output_dir", "/mnt/hydra_data"))

        self.subscriptions = []
        exchange_keys = self.config.get("subscribe_exchanges", [])
        for key in exchange_keys:
            exchange_cfg = self.exchanges.get(key, key)
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
            line = f"{msg.timestamp},{msg.data}\n"

            print(line)
            if not file_path.exists():
                await self.write_to_file(file_path, "timestamp,value\n")

            await self.write_to_file(file_path, line)

        return callback           

    # TODO: Move this into another utility module or something, since we'll
    #       probably want to use it in other places too
    async def write_to_file(self, file_path: Path, data: str):
        try:
            async with aiofiles.open(file_path, mode='a') as f:
                await f.write(data)
            # TODO: When we get a proper logging module make this [INFO]
            # print(f"Successfully wrote {data} to {filename}")
        except Exception as e:
            print(f"An error occurred: {e}")

