import asyncio

from node import Node

def spin(node: Node):
    node.start()

    async def loop():
        try:
            while True:
                await asyncio.sleep(0)
        except KeyboardInterrupt:
            sys.exit(130)

    asyncio.run(loop())
    
