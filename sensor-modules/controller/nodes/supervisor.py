from core.node import Node 
from core.message_types import PDB_Command
from core.utils import get_exchange_name


class Supervisor(Node):
    
    def __init__(self, config: dict, pdb_config: dict):
        super().__init__("supervisor", config)
        
        publish_exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "publish_exchange",
        )
        self.pdb_command_publisher = self.create_publisher(PDB_Command, publish_exchange_name) 
        self.create_task(self.publish_ads)

    async def publish_pdb_command(self):
        command = PDB_Command(pin_name="CNDT", new_state=True)
        self.pdb_command_publisher.publish(command)
