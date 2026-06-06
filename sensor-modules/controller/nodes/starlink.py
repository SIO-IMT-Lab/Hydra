import asyncio
import uuid
 
from core.message_types import PDB_ServiceRequest, PDB_ServiceResponse
from core.utils import get_exchange_name
from nodes.pdb_client import PDB_Client
 
 
class StarLink(PDB_Client):
 
    def __init__(self, config: dict, action: str):
        super().__init__("starlink", config)

        self.action = action 
        self.create_task(self.run_once)
 
    async def run_once(self):
        try:
            success = False
            for attempt in range(1, 4): 
                success = await self.send_service_call("STARLINK", self.action == "enable")
                if success:
                    break
                self.logger.warning(
                    "Attempt %d to %s STARLINK failed, retrying...",
                    attempt,
                    self.action
                )
                await asyncio.sleep(1)
 
            if not success:
                self.logger.error(
                    "Could not %s STARLINK after retries; shutting down",
                    self.action
                )

        finally:
            await self.stop()
