import board
import digitalio

from adafruit_mcp230xx.mcp23017 import MCP23017


class MCP:
    
    def __init__(self, address: int = 0x20):
        self.mcp = MCP23017(board.I2C(), address=address)
        self.pins = []
        for pin_num in range(8):
            pin = self.mcp.get_pin(pin_num)
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = False
            self.pins.append(pin)

    def set_pin(self, pin_num: int, value: bool) -> None:
        """Set the value of a specific pin on the MCP23017."""
        if 0 <= pin_num < 8:
            self.pins[pin_num].value = value
        else:
            # Put a Logging Warning here about invalid pin number
            print(f"Warning: Invalid pin number {pin_num}. Valid range is 0-7.")
    
    def get_pin(self, pin_num: int) -> bool:
        """Get the value of a specific pin on the MCP23017."""
        if 0 <= pin_num < 8:
            return self.pins[pin_num].value
        else:            
            # Put a Logging Warning here about invalid pin number
            print(f"Warning: Invalid pin number {pin_num}. Valid range is 0-7.")
            return False
            
            
