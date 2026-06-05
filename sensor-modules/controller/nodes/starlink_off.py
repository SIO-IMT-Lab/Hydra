import asyncio
 
from core.utils import get_exchange_name
from nodes.pdb_client import PDB_Client
 
 
class StarLinkOff(PDB_Client):
 
    def __init__(self, config: dict):
        super().__init__("starlink_off", config)
 
        self.create_task(self.run_once)
 
    async def run_once(self):
        try:
            success = False
            for attempt in range(1, 4): 
                success = await self.send_service_call("STARLINK", False)
                if success:
                    break
                self.logger.warning(
                    "Attempt %d to disable STARLINK failed, retrying...",
                    attempt
                )
                await asyncio.sleep(1)
 
            if not success:
                self.logger.error(
                    "Could not disable STARLINK after retries; shutting down",
                )

        finally:
            # Always tear down so systemd sees the unit complete.
            await self.stop()

