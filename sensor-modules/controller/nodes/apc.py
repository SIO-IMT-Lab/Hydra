import asyncio

from core.node import Node 
from core.message_types import APCData, Time
from core.utils import get_exchange_name


class APC(Node):
    
    def __init__(self, config: dict):
        super().__init__("apc", config)

        self.serial_port = self.node_config.get("serial_port", "/dev/ttyUSB2")
        self.baudrate = self.node_config.get("baudrate", 9600)
        self.read_timeout = self.node_config.get("read_timeout", 5.0)
        self.exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "publish_exchange",
        )

        self.apc_publisher = self.create_publisher(APCData, self.exchange_name)
        self.create_task(self.publish_apc)

    async def publish_apc(self):
        reader, writer = await self.open_serial_connection(
            url=self.serial_port,
            baudrate=self.baudrate
        )

        try:
            while True:
                try:
                    raw_data = await asyncio.wait_for(
                        reader.readline(),
                        timeout=self.read_timeout
                    )
                except asyncio.TimeoutError:
                    self.logger.warning(
                        "Timed out waiting for apc data"
                    )
                    continue
                timestamp = Time.now() # Want the time as soon as possible

                data = raw_data.decode(errors="ignore").strip()
                if not data:
                    continue
                
                data = data.split(",")
                value1 = float(data[0])
                value2 = float(data[1])

                msg = APCData(value_1=value1, value_2=value2, timestamp=timestamp)
                self.apc_publisher.publish(msg, self.exchange_name)
                self.logger.info(f"Published APC data: {msg.to_dict()}")
        finally:
            writer.close()
            await writer.wait_closed()
