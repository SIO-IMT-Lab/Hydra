from typing import Sequence
import asyncio
import logging
import signal

from .node import Node


async def run_nodes(nodes: Sequence[Node]):
    loop = asyncio.get_running_loop()

    def shutdown():
        asyncio.create_task(asyncio.gather(*(node.stop() for node in nodes)))

    loop.add_signal_handler(signal.SIGTERM, shutdown) # For systemd
    loop.add_signal_handler(signal.SIGINT, shutdown)
    
    await asyncio.gather(*(node.start() for node in nodes))
    await asyncio.gather(*(node.is_stopped.wait() for node in nodes))
    
def launch(nodes: Sequence[Node], log_level=logging.WARNING):
    logging.basicConfig(
            level=log_level,
            format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S%z'
    )
    asyncio.run(run_nodes(nodes))


async def run_node(node: Node):
    
    loop = asyncio.get_running_loop()

    def shutdown():
        asyncio.create_task(asyncio.gather(*(node.stop() for node in nodes)))

    loop.add_signal_handler(signal.SIGTERM, shutdown) # For systemd
    loop.add_signal_handler(signal.SIGINT, shutdown)
    
    await node.start()
    await node.is_stopped.wait()
    
def spin(node: Node):
    asyncio.run(run_node(node))
    
