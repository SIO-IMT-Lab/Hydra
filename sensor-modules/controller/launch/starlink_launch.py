import argparse
from email import parser
import logging

from core.launch import launch
from core.utils import load_config
from nodes.starlink import StarLink


def main():
    parser = argparse.ArgumentParser(description="Starklink Launcher")
    parser.add_argument("--state", choices=["enable", "disable"], required=True)
    args = parser.parse_args()
    
    node_config = load_config("config/nodes.yaml")
   
    nodes = [        
        StarLink(node_config, action=args.state),
    ]
    
    launch(nodes)

if __name__ == '__main__':
    main()

