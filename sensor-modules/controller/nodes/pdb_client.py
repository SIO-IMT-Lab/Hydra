import asyncio
import uuid

from core.node import Node 
from core.message_types import PDB_ServiceRequest, PDB_ServiceResponse
from core.utils import get_exchange_name


class PDB_Client(Node):
    
    def __init__(self, node_name: str, config: dict):
        super().__init__(node_name, config)

        request_exchange = get_exchange_name(
            self.node_config,
            self.exchanges,
            "service_request_exchange",
        )
        self.response_exchange = get_exchange_name(
            self.node_config,
            self.exchanges,
            "service_response_exchange",
        )
        self.pdb_request_publisher = self.create_publisher(PDB_ServiceRequest, request_exchange)

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
