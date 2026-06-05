import asyncio
import uuid

from core.message_types import PDB_ServiceRequest, PDB_ServiceResponse
from core.utils import get_exchange_name
from nodes.pdb_client import PDB_Client


class User(PDB_Client):
    
    def __init__(self, config: dict):
        super().__init__("user", config)

        self.create_task(self.run_cli)

    async def run_cli(self):
        """Interactive shell for PDB pin control."""
        print("PDB pin control CLI")
        print("Commands: set <PIN> on|off, toggle <PIN>, status, exit")
 
        try:
            while True:
                # input() blocks, so offload it to a thread to keep the
                # event loop responsive.
                raw = await asyncio.to_thread(input, ">>> ")
                command = raw.strip()
                if not command:
                    continue
 
                parts = command.split()
                keyword = parts[0].lower()
 
                if keyword == "exit":
                    print("Exiting...")
                    break
 
                elif keyword == "set":
                    if len(parts) == 3:
                        pin_name = parts[1].upper()
                        state = parts[2].lower()
                        if state in ("on", "off"):
                            success = await self.send_service_call(
                                pin_name, state == "on"
                            )
                            if success:
                                print(f"Set {pin_name} {state.upper()}")
                            else:
                                print(f"Failed to set {pin_name}")
                        else:
                            print("Invalid state. Example: set CNDT on")
                    else:
                        print("Invalid command format. Example: set CNDT on")
 
                elif keyword == "toggle":
                    # TODO: needs a current-state read before flipping
                    pass
 
                elif keyword == "status":
                    # TODO: needs a state query service
                    pass
 
                else:
                    print("Unknown command. Available: set, toggle, status, exit")
 
        except (KeyboardInterrupt, EOFError):
            print("\nExiting cleanly...")

    async def send_service_call(self, pin_name: str, new_state: bool):
        response = await self.call_service(
            request=PDB_ServiceRequest(
                        correlation_id=str(uuid.uuid4()),
                        pin_name=pin_name,
                        new_state=new_state,
            ),
            request_publisher=self.pdb_request_publisher,
            response_type=PDB_ServiceResponse,
            response_exchange=self.response_exchange,
            timeout=5.0,
        )
        if response is not None:
            if response.success:
                self.logger.info(
                    "%s request SUCCEEDED: Voltage at %.2fV",
                    pin_name,
                    response.actual_voltage
                )
                return True
            else:
                self.logger.info(
                    "%s request FAILED: Error message: %s",
                    pin_name,
                    response.error_message
                )

        self.logger.warning(
            "Service request for pin %s timed out", 
            pin_name
        )

        return False
