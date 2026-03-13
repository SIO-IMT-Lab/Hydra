import asyncio
import serial_asyncio

from core.node import Node 
from core.message_types import String
from core.launch import spin

# TODO: Put these in a dedicated config file or something
# TODO: /dev/USB0 could change, may need a script to scan connected USBs
DEFAULT_SERIAL_PORT = "/dev/ttyUSB2"
DEFAULT_BAUDRATE = 9600

class APC(Node):
    
    def __init__(self):
        super().__init__("apc")
        # TODO: Anything else we need to publish?
        self.apc_publisher = self.create_publisher(String, 'apc') 
        self.create_task(self.publish_apc)

    async def publish_apc(self):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=DEFAULT_SERIAL_PORT,
            baudrate=DEFAULT_BAUDRATE
        )

        try:
            while True:
                line = await reader.readline()
                line = line.decode(errors="ignore").strip()
                msg = String(data=line)
                self.apc_publisher.publish(msg, "apc")
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
    apc = APC()
    spin(apc)

if __name__ == '__main__':
    main()

