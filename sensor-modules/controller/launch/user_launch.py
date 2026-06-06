import logging

from core.launch import launch
from core.utils import load_config
from nodes.user import User


def main(args=None):
    node_config = load_config("config/nodes.yaml")
    pdb_config = load_config("config/pdb_pins.yaml")
   
    nodes = [        
        User(node_config, pdb_config),
    ]
    
    launch(nodes, log_level=logging.INFO)

if __name__ == '__main__':
    main()
