import logging

from core.launch import launch
from core.utils import load_config
from nodes.user import User


def main(args=None):
    node_config = load_config("config/nodes.yaml")
    pdb_config = load_config("config/pdb_pins.yaml")
    logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S%z'
    )
   
    nodes = [        
        User(node_config),        
    ]
    
    launch(nodes)

if __name__ == '__main__':
    main()
