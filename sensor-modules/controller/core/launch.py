import sys
import asyncio
from typing import Sequence

from .node import Node


async def run_nodes(nodes: Sequence[Node]):
    await asyncio.gather(*(node.start() for node in nodes))
    await asyncio.Event().wait()
    
def launch(nodes: Sequence[Node]):
    try:
        asyncio.run(run_nodes(nodes))
    except KeyboardInterrupt:
        pass


async def run_node(node: Node):
    await node.start()
    await asyncio.Event().wait() 
    
def spin(node: Node):
    try:
        asyncio.run(run_node(node))
    except KeyboardInterrupt:
        pass
    
