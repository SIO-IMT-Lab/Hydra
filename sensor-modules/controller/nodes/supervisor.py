import asyncio

from core.node import Node 
from core.message_types import PDB_Command
from core.utils import get_exchange_name


class Supervisor(Node):
    
    def __init__(self, config: dict):
        super().__init__("supervisor", config)

        self.publish_exchange_name = get_exchange_name(
            self.node_config,
            self.exchanges,
            "publish_exchange",
        )
        self.pdb_command_publisher = self.create_publisher(PDB_Command, self.publish_exchange_name) 
        self.create_timer(5.0, self.publish_pdb_command)

    async def publish_pdb_command(self):
        command = PDB_Command(pin_name='CNDT', new_state=True)
        self.pdb_command_publisher.publish(command, self.publish_exchange_name)

        command = PDB_Command(pin_name='APC', new_state=True)
        self.pdb_command_publisher.publish(command, self.publish_exchange_name)

        # command = PDB_Command(pin_name='STARLINK', new_state=True)
        # self.pdb_command_publisher.publish(command, self.publish_exchange_name)
