import asyncio
from typing import Sequence

from .node import Node


async def run_nodes(nodes: Sequence[Node]):
    await asyncio.gather(*(node.start() for node in nodes))
    await asyncio.gather(*(node.is_stopped.wait() for node in nodes))
    
def launch(nodes: Sequence[Node]):
    try:
        asyncio.run(run_nodes(nodes))
    except KeyboardInterrupt:
        pass


async def run_node(node: Node):
    await node.start()
    await node.is_stopped.wait()
    
def spin(node: Node):
    try:
        asyncio.run(run_node(node))
    except KeyboardInterrupt:
        pass
    
