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
        self.logger.info("PDB pin control CLI")
        self.logger.info("Commands: set <PIN> on|off, toggle <PIN>, status, exit")

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
                    self.logger.info("Exiting...")
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
                                self.logger.info("Set %s %s", pin_name, state.upper())
                            else:
                                self.logger.error("Failed to set %s", pin_name)
                        else:
                            self.logger.warning("Invalid state. Example: set CNDT on")
                    else:
                        self.logger.warning("Invalid command format. Example: set CNDT on")

                elif keyword == "toggle":
                    # TODO: needs a current-state read before flipping
                    pass

                elif keyword == "status":
                    # TODO: needs a state query service
                    pass

                else:
                    self.logger.warning("Unknown command. Available: set, toggle, status, exit")

        except (KeyboardInterrupt, EOFError):
            self.logger.info("Exiting cleanly...")
            
        finally:
            await self.stop()