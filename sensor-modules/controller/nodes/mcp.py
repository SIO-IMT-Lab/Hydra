import board
import digitalio

from adafruit_mcp230xx.mcp23017 import MCP23017


class MCP:
    
    def __init__(self, 
                 address: int, 
                 control_pins_config: dict[str, str], 
                 logger
    ) -> None:
        self.control_pins_config = control_pins_config        
        self.logger = logger.getChild("mcp")

        i2c = board.I2C()
        self.mcp = MCP23017(i2c, address=address)
        for i in range(16):
            pin = self.mcp.get_pin(i)
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = False

    def set_pin(self, name: str, value: bool) -> bool | None:
        """
        Set a pin. Returns True on success, or None if the pin name is unknown.

        Note: Made this return None instead of False for consistency with similar functions
        """
        pin_obj = self._get_pin_obj(name)
        if pin_obj is None:
            return None
        pin_obj.value = value
        return True

    def get_pin(self, name: str) -> bool | None:
        """Get a pin's value, or None if the pin name is unknown."""
        pin_obj = self._get_pin_obj(name)
        if pin_obj is None:
            return None
        return pin_obj.value
            
    def _get_pin_obj(self, name: str):
        pin = self.control_pins_config.get(name)
        if pin is None:
            self.logger.warning(
                "No control pin found for device '%s'.",
                name,
            )            
            return None

        try:
            letter = pin[0].upper()
            index = int(pin[1:])
        except (IndexError, ValueError):
            self.logger.warning(
                "Invalid pin format '%s' for device '%s'. Expected format like 'A0' or 'B3'.",
                pin,
                name,
            )
            return None

        if letter not in {"A", "B"}:
            self.logger.warning(
                "Invalid pin bank '%s' for device '%s'. Expected 'A' or 'B'.",
                letter,
                name,
            )
            return None

        if not (0 <= index <= 7):
            self.logger.warning(
                "Invalid pin index '%s' for device '%s'. Valid range is 0-7.",
                index,
                name,
            )
            return None

        if letter == "A":
            return self.mcp.get_pin(index)
        elif letter == "B":
            return self.mcp.get_pin(index+8)
            
