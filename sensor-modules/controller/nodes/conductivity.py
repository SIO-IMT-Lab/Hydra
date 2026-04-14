import serial_asyncio

from core.node import Node 
from core.message_types import SensorData, Time
from core.utils import get_exchange_name


class Conductivity(Node):
    
    def __init__(self, config: dict):
        super().__init__("conductivity", config)
        
        self.serial_port = self.config.get("serial_port", "/dev/ttyUSB1")
        self.baudrate = self.config.get("baudrate", 9600)
        self.exchange_name = get_exchange_name(
            self.config,
            self.exchanges,
            "publish_exchange",
        )

        self.conductivity_publisher = self.create_publisher(SensorData, self.exchange_name) 
        self.create_task(self.publish_conductivity)

    async def publish_conductivity(self):
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

