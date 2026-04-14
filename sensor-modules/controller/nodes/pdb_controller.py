from core.node import Node 
from core.message_types import PDB_Command
from core.utils import get_exchange_name
from .ads import ADS
from .mcp import MCP


class PDB_Controller(Node):
    
    def __init__(self, config: dict, pdb_config: dict):
        super().__init__("pdb_controller", config)
        
        # self.ads = ADS()
        # publish_exchange_name = get_exchange_name(
        #     self.node_config,
        #     self.exchanges,
        #     "publish_exchange",
        # )
        # self.pdb_publisher = self.create_publisher(SensorData, publish_exchange_name) 
        # self.create_task(self.publish_ads)
        
        self.mcp_address = self.config.get("mcp_address", 0x20)
        subscribe_exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "subscribe_exchange",
        )
        self.mcp = MCP(self.mcp_address, pdb_config.get("Control_Pins", {}))
        self.pdb_subscriber = self.create_subscription(
            msg_type=PDB_Command,
            exchange=subscribe_exchange_name,
            user_callback=self.receive_commands,
            binding_keys=["#"],
        )

    async def receive_commands(self, msg: PDB_Command):
        self.mcp.set_pin(msg.pin_name, msg.new_state)
