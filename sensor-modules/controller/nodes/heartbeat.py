import asyncio
from gpiozero import DigitalOutputDevice

from core.node import Node 


PULSE_PIN = 27 


class Heartbeat(Node):
    
    def __init__(self, config: dict):
        super().__init__("heartbeat", config)
        
        self.on_time = self.node_config.get("high_time", 1.0)
        self.off_time = self.node_config.get("low_time", 5.0)
        
        self.pulse_pin = DigitalOutputDevice(PULSE_PIN)

        self.create_task(self.send_pulses)

    async def send_pulses(self):
        while True:
            self.pulse_pin.on()
            await asyncio.sleep(self.on_time)
            self.pulse_pin.off()
            await asyncio.sleep(self.off_time)

