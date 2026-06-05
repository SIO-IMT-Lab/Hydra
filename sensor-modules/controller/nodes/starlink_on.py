import asyncio
import uuid
 
from core.message_types import PDB_ServiceRequest, PDB_ServiceResponse
from core.utils import get_exchange_name
from nodes.pdb_client import PDB_Client
 
 
class StarLinkOn(PDB_Client):
 
    def __init__(self, config: dict):
        super().__init__("starlink_on", config)
 
        self.create_task(self.run_once)
 
    async def run_once(self):
        try:
            success = False
            for attempt in range(1, 4): 
                success = await self.send_service_call("STARLINK", True)
                if success:
                    break
                self.logger.warning(
                    "Attempt %d to enable %s failed, retrying...",
                    attempt,
                    self.pin_name,
                )
                await asyncio.sleep(1)
 
            if not success:
                self.logger.error(
                    "Could not enable %s after retries; shutting down",
                    self.pin_name,
                )

        finally:
            # Always tear down so systemd sees the unit complete.
            await self.shutdown()
 
    async def shutdown(self):
        pass
