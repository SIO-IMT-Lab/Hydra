import board

from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn


class ADS:
    
    def __init__(self, addresses: list[int], ratio: float, interval: float):
        """
        Create an ADS reader for multiple ADS1015 devices.

        :param addresses: List of I2C addresses for ADS1015 devices.
        :param ratio: Scaling factor applied to each voltage reading.
        :param interval: float
            Delay between consecutive readings in seconds.
        """
        self.addresses = addresses
        self.ratio = ratio
        self.interval = interval
        
        devices = [ADS1015(board.I2C(), address=addr) for addr in self.addresses]
        self.channels = [[AnalogIn(dev, ch) for ch in range(4)] for dev in devices]

    def read_ads(self):
        """Read voltage values from all channels of all ADS1015 devices"""
        ads_values = []
        for ch_list in self.channels:
            for ch in ch_list:
                voltage = ch.voltage * self.ratio
                ads_values.append(voltage)
        return ads_values
