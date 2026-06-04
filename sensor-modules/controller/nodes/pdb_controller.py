import asyncio

from core.node import Node
from core.message_types import PDB_Command, PDB_State, Time
from core.utils import get_exchange_name
from .ads import ADS
from .mcp import MCP


class PDB_Controller(Node):
    
    def __init__(self, config: dict, pdb_config: dict):
        super().__init__("pdb_controller", config)
        
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
        subscribe_exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "subscribe_exchange",
        )
        self.mcp = MCP(mcp_address, pdb_config.get("Control_Pins", {}), self.logger)
        self.pdb_subscriber = self.create_subscription(
            msg_type=PDB_Command, 
            exchange=subscribe_exchange_name,
            user_callback=self.receive_commands,
            binding_keys=["#"]
        )

    async def publish_voltages(self):
        voltages = await asyncio.to_thread(self.ads.read_ads)
        timestamp = Time.now()
        msg = PDB_State(voltages=voltages, timestamp=timestamp)
        self.pdb_publisher.publish(msg, self.publish_exchange_name)
        self.logger.info("Published PDB voltages: %s", voltages)

    async def receive_commands(self, command: PDB_Command):
        self.logger.info("Received PDB command: %s", command)
        await asyncio.to_thread(self.mcp.set_pin, command.pin_name, command.new_state)
