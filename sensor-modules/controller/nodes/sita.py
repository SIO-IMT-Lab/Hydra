from gpiozero import DigitalOutputDevice
import asyncio
import serial_asyncio

from core.node import Node 
from core.message_types import String
from core.launch import spin
from config.constants import SITA_COMMANDS


DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
DEFAULT_BAUDRATE = 57600
DEFAULT_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 1.0
DEFAULT_MEASURE_LIMIT = 20.0

ENABLE_PIN = 4

class SITA(Node):
    
    def __init__(self):
        super().__init__("sita")
        # TODO: Anything else we need to publish?
        self.sita_publisher = self.create_publisher(String, 'sita') 
        self.create_task(self.publish_sita)

    # TODO: The original code spams the SITA with QUERY and it seems to work?
    #       Still need to add timeout feature like the original code though
    async def take_measurement(self, reader, writer):
        while True:
            writer.write(SITA_COMMANDS.QUERY)
            await writer.drain()
            await asyncio.sleep(0.04)

            line = await reader.readline()
            line = line.decode(encoding="utf-8", errors="ignore").strip()
            if len(line) > 20:
                return line

    async def publish_sita(self):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=DEFAULT_SERIAL_PORT,
            baudrate=DEFAULT_BAUDRATE
        )

        writer.write(SITA_COMMANDS.POWER_UP)
        await writer.drain()

        enable_pin = DigitalOutputDevice(ENABLE_PIN)
        enable_pin.on()

        try:
            while True:
                writer.write(SITA_COMMANDS.NO_CAL)
                await writer.drain()
                await asyncio.sleep(3)
                writer.write(SITA_COMMANDS.SAMPLE)
                await writer.drain()
                await asyncio.sleep(1)

                line = await self.take_measurement(reader, writer)
                msg = String(data=line)
                self.sita_publisher.publish(msg, "sita")

                writer.write(SITA_COMMANDS.STOP)
                await writer.drain()
                await asyncio.sleep(DEFAULT_TIMEOUT)
        except asyncio.CancelledError:
            try:
                writer.write(SITA_COMMANDS.POWER_OFF)
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

