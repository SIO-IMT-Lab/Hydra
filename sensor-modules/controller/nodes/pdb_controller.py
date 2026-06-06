import asyncio

from core.node import Node
from core.message_types import PDB_ServiceRequest, PDB_ServiceResponse, PDB_State, Time
from core.utils import get_exchange_name
from .ads import ADS
from .mcp import MCP


class PDB_Controller(Node):
    
    def __init__(self, config: dict, pdb_config: dict):
        super().__init__("pdb_controller", config)

        self.pdb_config = pdb_config

        ads_ratio = self.node_config.get("ads_ratio", 11.060)
        ads_interval = self.node_config.get("ads_interval", 1.0)
        self.publish_exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "publish_exchange",
        )
        self.ads = ADS(ads_ratio, pdb_config.get("ADS_Info", {}), self.logger)
        self.pdb_publisher = self.create_publisher(
            msg_type=PDB_State, 
            exchange=self.publish_exchange_name
        )
        self.create_timer(ads_interval, self.publish_voltages)
        
        mcp_address = self.node_config.get("mcp_address", 0x20)
        request_exchange = get_exchange_name(
            self.node_config,
            self.exchanges,
            "service_request_exchange",
        )
        response_exchange = get_exchange_name(
            self.node_config,
            self.exchanges,
            "service_response_exchange",
        )
        self.mcp = MCP(mcp_address, pdb_config.get("Control_Pins", {}), self.logger)
        self.create_service(
            request_type=PDB_ServiceRequest,
            response_type=PDB_ServiceResponse,
            request_exchange=request_exchange,
            response_exchange=response_exchange,
            user_callback=self.handle_request,
        )

    async def publish_voltages(self):
        voltages = await asyncio.to_thread(self.ads.read_all_voltages)
        timestamp = Time.now()
        msg = PDB_State(voltages=voltages, timestamp=timestamp)
        self.pdb_publisher.publish(msg, self.publish_exchange_name)
        self.logger.info("Published PDB voltages: %s", voltages)

    async def handle_request(self, request: PDB_ServiceRequest):
        self.logger.info("Received PDB request: %s", request)

        pin_set_status = await asyncio.to_thread(self.mcp.set_pin, request.pin_name, request.new_state)
        await asyncio.sleep(5.0) # Give the PDB enough time to settle
        pin_voltage = await asyncio.to_thread(self.ads.read_specific_voltages, request.pin_name)

        default_voltage = self.pdb_config.get("ADS_Info", {}).get(request.pin_name, {}).get("default_voltage", 0.0)

        if pin_set_status is None or pin_voltage is None:
            return PDB_ServiceResponse(
                correlation_id=request.correlation_id,
                pin_name=request.pin_name,
                success=False,
                actual_voltage=0.0,
                error_message=f"{request.pin_name} doesn't exist. Check pdb_pins.yaml config"
            )
        
        if request.new_state:
            success = pin_voltage > 1.0
            # success = pin_voltage > 0.8 * default_voltage
        else:
            success = pin_voltage < 1.0  
            # success = pin_voltage < 0.2 * default_voltage
            
        return PDB_ServiceResponse(
            correlation_id=request.correlation_id,
            pin_name=request.pin_name,
            success=success,
            actual_voltage=pin_voltage,
            error_message=""
        )
