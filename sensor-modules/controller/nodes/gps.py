import serial_asyncio

from core.node import Node 
from core.message_types import String
from launch import spin

# TODO: Put these in a dedicated config file or something
DEFAULT_GPIO_PIN = 16
DEFAULT_SERIAL_PORT = "/dev/serial0"
DEFAULT_BAUDRATE = 9600

class GPS(Node):
    
    def __init__(self):
        super().__init__("gps")
        # TODO: Anything else we need to publish?
        self.time_publisher = self.create_publisher(String, 'time')        
        self.create_task(self.test_publish)

    async def test_publish(self):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=DEFAULT_SERIAL_PORT,
            baudrate=DEFAULT_BAUDRATE
        )

        while True:
            line = await reader.readline()
            line = line.decode(errors="ignore").strip()
            if "$GPRMC" in line:
                msg = String(data=line)
                self.time_publisher.publish(msg, "gps_time")
        
def main(args=None):
    gps = GPS()
    spin(gps)

if __name__ == '__main__':
    main()
