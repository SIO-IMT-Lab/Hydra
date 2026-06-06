import asyncio
import uuid
 
from core.message_types import PDB_ServiceRequest, PDB_ServiceResponse
from core.utils import get_exchange_name
from nodes.pdb_client import PDB_Client
 
 
class StarLink(PDB_Client):
 
    def __init__(self, config: dict, new_state: str):
        super().__init__(f"starlink_{new_state}", config)

        self.new_state = new_state
        self.create_task(self.run_once)
 
    async def run_once(self):
        try:
            success = False
            for attempt in range(1, 4): 
                success = await self.send_service_call("STARLINK", self.turn_on)
                if success:
                    break
                self.logger.warning(
                    "Attempt %d to %s STARLINK failed, retrying...",
                    attempt,
                    self.new_state
                )
                await asyncio.sleep(1)
 
            if not success:
                self.logger.error(
                    "Could not %s STARLINK after retries; shutting down",
                    self.new_state
                )

        finally:
            await self.stop()
