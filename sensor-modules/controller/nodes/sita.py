import asyncio
import serial_asyncio

from core.node import Node 
from core.message_types import String
from core.launch import spin


# TODO: Again please put this in a config file
POWER_UP = b"\r\n:020605000100F2\r\n"
NO_CAL = b"\r\n:020601000600F1\r\n"
SAMPLE = b"\r\n:020601000B00EC\r\n"
QUERY = b"\r\n:020618000500DB\r\n"
POWER_OFF = b"\r\n:020605000000F3\r\n"
STOP = b"\r\n:020618000000E0\r\n"

DEFAULT_SERIAL_PORT = "/dev/ttyUSB2"
DEFAULT_BAUDRATE = 57600
DEFAULT_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 1.0
DEFAULT_MEASURE_LIMIT = 20.0

class SITA(Node):
    
    def __init__(self):
        super().__init__("sita")
        # TODO: Anything else we need to publish?
        self.sita_publisher = self.create_publisher(String, 'sita') 
        self.create_task(self.publish_sita)

    async def publish_sita(self):
        # Note that open_serial_connection is a wrapper for 
        # create_serial_connection() which is a coroutine. Calls 
        # asyncio.get_event_loop() under the hood. The documenation
        # says the params are the same as Serial() but you need to
        # pass it in as url.
        reader, writer = await serial_asyncio.open_serial_connection(
            url=DEFAULT_SERIAL_PORT,
            baudrate=DEFAULT_BAUDRATE
        )

        writer.write(POWER_UP)
        await writer.drain()

        try:
            while True:
                writer.write(NO_CAL)
                await asyncio.sleep(3)
                writer.write(SAMPLE)
                await asyncio.sleep(1)

                writer.write(QUERY)
                await asyncio.sleep(0.04)

                line = await reader.readline()
                line = line.decode(encoding="utf-8", errors="ignore").strip()
                msg = String(data=line)
                self.sita_publisher.publish(msg, "sita")

                writer.write(STOP)
                await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            try:
                writer.write(POWER_OFF)
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
    sita = SITA()
    spin(sita)

if __name__ == '__main__':
    main()

