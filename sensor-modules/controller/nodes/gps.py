import asyncio
import serial_asyncio

from core.node import Node 
from core.launch import spin
from core.message_types import Time
from datetime import datetime, timezone

# TODO: Put these in a dedicated config file or something
DEFAULT_GPIO_PIN = 16
DEFAULT_SERIAL_PORT = "/dev/serial0"
DEFAULT_BAUDRATE = 9600

class GPS(Node):
    
    def __init__(self):
        super().__init__("gps")
        # TODO: Anything else we need to publish?
        self.gps_publisher = self.create_publisher(Time, 'gps')   
        self.create_task(self.publish_gps)

    def gps_to_epoch_ns(self, gps_time: str, gps_date: str) -> int:
        """
        Convert NMEA gps_time="hhmmss.sss" and gps_date="ddmmyy"
        into Unix epoch nanoseconds (UTC).
        """

        day = int(gps_date[0:2])
        month = int(gps_date[2:4])
        year = int(gps_date[4:6]) + 2000

        hour = int(gps_time[0:2])
        minute = int(gps_time[2:4])
        second = int(gps_time[4:6])
        if "." in time_str:
            microsecond = int(float("0." + time_str[7:]) * 1_000_000) 
        else:
            microsecond = 0

        dt = datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            tzinfo=timezone.utc,
        )

        return int(dt.timestamp() * 1e9)

    async def publish_gps(self):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=DEFAULT_SERIAL_PORT,
            baudrate=DEFAULT_BAUDRATE
        )

        while True:
            raw_data = await reader.readline()
            line = raw_data.decode(errors="ignore").strip()
            # TODO: Perhaps put this "$GPRMC param in the config"
            if "$GPRMC" in line:
                items = line.split(",")
                time, date = items[1], items[9]
                epoch_ns = self.gps_to_epoch_ns(time, date)
                msg = Time(ns=epoch_ns)
                self.gps_publisher.publish(msg=msg, routing_key="time")
        
def main(args=None):
    gps = GPS()
    spin(gps)

if __name__ == '__main__':
    main()
