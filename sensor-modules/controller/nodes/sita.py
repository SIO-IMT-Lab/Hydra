from gpiozero import DigitalOutputDevice
import asyncio

from core.node import Node 
from core.message_types import SITAData, Time
from core.utils import get_exchange_name
from config.constants import SITA_COMMANDS


ENABLE_PIN = 4

class SITA(Node):
    
    def __init__(self, config: dict):
        super().__init__("sita", config)

        self.serial_port = self.node_config.get("serial_port", "/dev/ttyUSB1")
        self.baudrate = self.node_config.get("baudrate", 57600)

        self.warmup_time = self.node_config.get("warmup_time", 4.0)
        self.sample_read_interval = self.node_config.get("sample_read_interval", 30.0)
        self.serial_read_timeout = self.node_config.get("serial_read_timeout", 0.04)
        self.measure_time_limit = self.node_config.get("measure_time_limit", 20.0)
        self.min_valid_response_length = self.node_config.get("min_valid_response_length", 20)

        self.exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "publish_exchange",
        )

        self.enable_pin = DigitalOutputDevice(ENABLE_PIN)

        self.sita_publisher = self.create_publisher(SITAData, self.exchange_name)
        self.create_task(self.publish_sita)

    async def publish_sita(self):
        self.enable_pin.on()
        try:
            await asyncio.sleep(self.warmup_time)
            
            reader, writer = await self.open_serial_connection(
                url=self.serial_port,
                baudrate=self.baudrate
            )

            try:
                while True:
                    await self.power_on(writer)
                    line, timestamp = await self.take_measurement(reader, writer)
                    await self.power_off(writer)

                    if line is None:
                        self.logger.warning("SITA measurement timed out")
                    else:
                        values = self.parse_line(line)
                        msg = SITAData(timestamp=timestamp, **values)
                        self.sita_publisher.publish(msg, self.exchange_name)
                        self.logger.info(f"Published SITA data: {msg.to_dict()}")

                    await asyncio.sleep(self.sample_read_interval)
            finally:
                try:
                    await self.power_off(writer)
                except Exception as e:
                    self.logger.warning(f"Could not power off SITA: {e}")
                writer.close()
                await writer.wait_closed()
        finally:
            self.enable_pin.off()
            self.enable_pin.close()

    async def power_on(self, writer):
        await self.send_command(writer, SITA_COMMANDS.POWER_UP)
        await asyncio.sleep(1)
        await self.send_command(writer, SITA_COMMANDS.NO_CAL)
        await asyncio.sleep(3)
        await self.send_command(writer, SITA_COMMANDS.SAMPLE)
        await asyncio.sleep(1)
    
    async def power_off(self, writer):
        await self.send_command(writer, SITA_COMMANDS.POWER_OFF)
        await asyncio.sleep(0.2)
        await self.send_command(writer, SITA_COMMANDS.STOP)
        await asyncio.sleep(0.2)

    async def take_measurement(self, reader, writer):
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.measure_time_limit

        while loop.time() < deadline:
            await self.send_command(writer, SITA_COMMANDS.QUERY)

            try:
                raw = await asyncio.wait_for(
                    reader.readline(),
                    timeout=self.serial_read_timeout,
                )
            except asyncio.TimeoutError:
                continue

            timestamp = Time.now()
            line = raw.decode("utf-8", errors="ignore").strip()

            if len(line) >= self.min_valid_response_length:
                return line, timestamp

        return None, None

    async def send_command(self, writer, command):
        writer.write(command.value)
        await writer.drain()
    
    def parse_line(self, line):
        """
        Parses SITA Data Line...Not sure what it looks like rn
        """
        pass

