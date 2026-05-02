import asyncio

from core.node import Node 
from core.message_types import ConductivityData, Time
from core.utils import get_exchange_name, parse_float


class Conductivity(Node):
    
    def __init__(self, config: dict):
        super().__init__("conductivity", config)
        
        self.serial_port = self.node_config.get("serial_port", "/dev/ttyUSB1")
        self.baudrate = self.node_config.get("baudrate", 9600)
        self.read_timeout = self.node_config.get("read_timeout", 5.0)
        self.exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "publish_exchange",
        )

        self.conductivity_publisher = self.create_publisher(ConductivityData, self.exchange_name) 
        self.create_task(self.publish_conductivity)

    async def publish_conductivity(self):
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
                        "Timed out waiting for conductivity data"
                    )
                    continue
                timestamp = Time.now() # Want the time as soon as possible

                data = raw_data.decode(errors="ignore").strip()
                clean_data = parse_float(data)
                if clean_data is None:
                    self.logger.warning("Bad conductivity data: %r", data)
                    continue

                msg = ConductivityData(conductivity=float(clean_data), timestamp=timestamp)
                self.conductivity_publisher.publish(msg, self.exchange_name)
                self.logger.info(f"Published conductivity data: {msg.to_dict()}")
        finally:
            writer.close()
            await writer.wait_closed()

