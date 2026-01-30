import sys
import asyncio

from node import Node

def spin(node: Node):
    async def loop():
        await node.start()
        await asyncio.Event().wait() 

    try:
        asyncio.run(loop())
    except KeyboardInterrupt:
        pass
    
