import asyncio
import serial_asyncio

from core.node import Node 
from core.message_types import String
from core.launch import spin

# TODO: Put these in a dedicated config file or something
# TODO: /dev/USB0 could change, may need a script to scan connected USBs
DEFAULT_SERIAL_PORT = "/dev/ttyUSB1"
DEFAULT_BAUDRATE = 9600

class Conductivity(Node):
    
    def __init__(self):
        super().__init__("conductivity")
        # TODO: Anything else we need to publish?
        self.conductivity_publisher = self.create_publisher(String, 'conductivity') 
        self.create_task(self.publish_conductivity)

    async def publish_conductivity(self):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=DEFAULT_SERIAL_PORT,
            baudrate=DEFAULT_BAUDRATE
        )

        try:
            while True:
                line = await reader.readline()
                line = line.decode(errors="ignore").strip()
                msg = String(data=line)
                self.conductivity_publisher.publish(msg, "conductivity")
        except asyncio.CancelledError:
            try:
                await writer.drain()
            except Exception:
                pass
            raise
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        
def main(args=None):
    conductivity = Conductivity()
    spin(conductivity)

if __name__ == '__main__':
    main()

