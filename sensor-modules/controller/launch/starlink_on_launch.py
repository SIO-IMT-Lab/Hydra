import logging

from core.launch import launch
from core.utils import load_config
from nodes.starlink_on import StarLinkOn 


def main(args=None):
    node_config = load_config("config/nodes.yaml")
    pdb_config = load_config("config/pdb_pins.yaml")
    logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S%z'
    )
   
    nodes = [        
        StarLinkOn(node_config),
    ]
    
    launch(nodes)

if __name__ == '__main__':
    main()

