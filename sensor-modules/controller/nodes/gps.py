import asyncio
import serial_asyncio

from core.node import Node 
from core.message_types import String
from core.launch import spin

# TODO: Put these in a dedicated config file or something
DEFAULT_GPIO_PIN = 16
DEFAULT_SERIAL_PORT = "/dev/serial0"
DEFAULT_BAUDRATE = 9600

class GPS(Node):
    
    def __init__(self):
        super().__init__("gps")
        # TODO: Anything else we need to publish?
        self.time_publisher = self.create_publisher(String, 'time')        
        self.date_publisher = self.create_publisher(String, 'date')        
        self.create_task(self.publish_gps)

    async def publish_gps(self):
        # Note that open_serial_connection is a wrapper for 
        # create_serial_connection() which is a coroutine. Calls 
        # asyncio.get_event_loop() under the hood. The documenation
        # says the params are the same as Serial() but you need to
        # pass it in as url.
        reader, writer = await serial_asyncio.open_serial_connection(
            url=DEFAULT_SERIAL_PORT,
            baudrate=DEFAULT_BAUDRATE
        )

        while True:
            raw_data = await reader.readline()
            line = raw_data.decode(errors="ignore").strip()
            # TODO: Perhaps put this "$GPRMC param in the config"
            if "$GPRMC" in line:
                # TODO: Come up with better variable names 
                items = line.split(",")
                time, date = items[1], items[9]

                msg = String(data=time)
                self.time_publisher.publish(msg, "gps_time")
                
                msg2 = String(data=date)
                self.time_publisher.publish(msg2, "gps_date")
        
def main(args=None):
    gps = GPS()
    spin(gps)

if __name__ == '__main__':
    main()
