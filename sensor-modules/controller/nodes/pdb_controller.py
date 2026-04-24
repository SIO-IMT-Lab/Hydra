import asyncio

from core.node import Node
from core.message_types import PDB_Command, get_message_class
from core.utils import get_exchange_name
from .ads import ADS
from .mcp import MCP


class PDB_Controller(Node):
    
    def __init__(self, config: dict, pdb_config: dict):
        super().__init__("pdb_controller", config)
        
        ads_addresses = self.config.get("ads_addresses", [0x48, 0x49, 0x4A, 0x4B])
        ads_ratio = self.config.get("ads_ratio", 11.060)
        ads_interval = self.config.get("ads_interval", 1.0)
        self.publish_exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "publish_exchange",
        )
        self.ads = ADS(ads_addresses, ads_ratio, ads_interval)
        self.pdb_publisher = self.create_publisher(
            msg_type=SensorData, 
            exchange=self.publish_exchange_name
        )
        self.create_timer(ads_interval, self.publish_voltages)
        
        mcp_address = self.config.get("mcp_address", 0x20)
        subscribe_exchange_name = get_exchange_name(
            self.config,
            self.exchanges,
            "subscribe_exchange",
        )
        self.mcp = MCP(mcp_address, pdb_config.get("Control_Pins", {}))
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

    async def receive_commands(self, msg: PDB_Command):
        self.mcp.set_pin(msg.pin_name, msg.new_state)
