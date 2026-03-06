from datetime import datetime, timezone

import asyncio
import aiofiles
from pathlib import Path

from core.node import Node
from core.message_types import String
from core.launch import spin


DATA_DIRECTORY = "hydra_data"
DATA_DIRECTORY_PATH = Path.home() / DATA_DIRECTORY
DATA_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)

class Recorder(Node):
    def __init__(self):
        super().__init__("recorder")
        self.subscriptions = []

        exchanges = [
            ("conductivity", String),
            ("sita", String),
            ("apc", String),
        ]

        for exchange, msg_type in exchanges:
            sub = self.create_subscription(
                msg_type=msg_type,
                exchange=exchange,
                user_callback=self.recorder_callback_factory(exchange),
                binding_keys=["#"],
            )
            self.subscriptions.append(sub)
            
    def recorder_callback_factory(self, exchange: str):
        async def callback(msg):
            # TODO: For testing I'll use a .txt but better to use .csv
            #       so it's easier to parse later on
            precise_datetime_utc = datetime.now(timezone.utc)
            precise_time_str = precise_datetime_utc.strftime("%Y-%m-%d %H:%M:%S.%f UTC")
            print(precise_time_str)
            await self.write_to_file(f"{exchange}_data.txt", msg.data)

        return callback
    
    # TODO: Move this into another utility module or something, since we'll
    #       probably want to use it in other places too
    async def write_to_file(self, filename: str, data: str):
        try:
            file_path = DATA_DIRECTORY_PATH / filename
            async with aiofiles.open(file_path, mode='a') as f:
                await f.write(data)
            # TODO: When we get a proper logging module make this [INFO]
            # print(f"Successfully wrote {data} to {filename}")
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    node = Recorder()
    spin(node)

if __name__ == "__main__":
    main()

