import asyncio

import serial_asyncio

from core.node import Node 
from core.message_types import SensorData, Time


class APC(Node):
    
    def __init__(self, config: dict):
        super().__init__("apc", config)

        self.serial_port = self.config.get("serial_port", "/dev/ttyUSB2")
        self.baudrate = self.config.get("baudrate", 9600)
        exchange_key = self.config.get("publish_exchange", "apc")
        exchange_cfg = self.exchanges.get(exchange_key, {})
        self.exchange_name = exchange_cfg.get("name", exchange_key)

        self.apc_publisher = self.create_publisher(SensorData, self.exchange_name)
        self.create_task(self.publish_apc)

    async def publish_apc(self):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=self.serial_port,
            baudrate=self.baudrate
        )

        try:
            while True:
                raw_data = await reader.readline()
                timestamp = Time.now() # Want the time right when the bytes arrive
                data = raw_data.decode(errors="ignore").strip()
                msg = SensorData(data=data, timestamp=timestamp)
                self.conductivity_publisher.publish(msg, self.exchange_name)
        finally:
            writer.close()
            await writer.wait_closed()

