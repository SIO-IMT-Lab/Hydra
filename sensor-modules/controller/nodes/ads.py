from collections import defaultdict

import board

from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn


class ADS:
    
    def __init__(self, 
                 ratio: float,
                 ADS_info_config: dict[str, str],
                 logger
    ) -> None:
        """
        Create an ADS reader for multiple ADS1015 devices.

        :param ratio: Scaling factor applied to each voltage reading.
        :param ADS_info_config: Configuration dict for ADS info.
        :param logger: Logger instance for logging messages.
        """
        
        self.ratio = ratio
        self.ADS_info_config = ADS_info_config
        self.logger = logger.getChild("ads")
        
        address_to_device = defaultdict(dict)
        for name, config in self.ADS_info_config.items():
            addr = config.get("i2c_address")
            ch = config.get("ads_channel")
            if addr is None:
                self.logger.warning(
                    "No I2C address specified for ADS device '%s' in config.",
                    name,
                )
                continue
            address_to_device[addr][ch] = name
            
        i2c = board.I2C()
        self.ads_devices = {
            addr: ADS1015(i2c, address=addr) 
            for addr in address_to_device
        }
        self.channels = {
            name: AnalogIn(self.ads_devices[addr], ch)
            for addr, channel_map in address_to_device.items()
            for ch, name in channel_map.items()
        }
        
    def read_ads(self):
        """Read voltage values from all channels of all ADS1015 devices"""
        ads_values = {}
        for name, ch in self.channels.items():
            voltage = ch.voltage * self.ratio
            ads_values[name] = voltage
        return ads_values
