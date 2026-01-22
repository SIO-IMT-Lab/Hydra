import pika
from pika.adapters.asyncio_connection import AsyncioConnection

class ServerConnection:
    """
    A Node's broker for communication channels

    Every time a Node is created, it will use this ServerConnection class to
    ask for a communication channel for each of its subscribers and publishers
    """

    def __init__(self):
        self.connection = None
        self.is_connected = asyncio.Event()
        
    def connect(self) -> None:
        self.connection = AsyncioConnection(
            parameters=pika.ConnectionParameters(host='localhost'),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)
        
    def on_connection_open(self, _unused_connection):
        """
        After the RabbitMQ connection is established, we can now safely create
        channels
        """
        self.is_connected.set()

    def on_connection_open_error(self, _unused_connection, err):
        print(err)

    def on_connection_closed(self, _unused_connection, reason):
        print(reason)

    async def create_channel(self, exchange_name):
        await self.is_connected.wait()
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
        return channel
