import asyncio

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
        self.is_connected = None
        
    def connect(self) -> None:
        if self.is_connected is None:
            self.is_connected = asyncio.Event()
        
        self.connection = AsyncioConnection(
            parameters=pika.ConnectionParameters(host='localhost'),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )
        
    def on_connection_open(self, _unused_connection):
        """
        After the RabbitMQ connection is established, set flag to indicate we
        can now create channels.
        """
        print("CONNECTION OPENED")
        self.is_connected.set()

    # TODO : Create proper connection error handling
    def on_connection_open_error(self, _unused_connection, err):
        print(f"CONNECTION OPEN ERROR: {err!r}")

    # TODO : Create proper connection close handling
    def on_connection_closed(self, _unused_connection, reason):
        print(f"CONNECTION OPEN CLOSED: {reason!r}")

    async def create_channel(self, exchange_name):
        await self.is_connected.wait()
        # Insert error handling code that will check if self.connection exists
        loop = asyncio.get_running_loop()
        
        channel_future = loop.create_future()
        def on_channel_open(ch):
            if not channel_future.done():
                channel_future.set_result(ch)
        self.connection.channel(on_open_callback=on_channel_open)
        channel = await channel_future
        
        exchange_future = loop.create_future()
        def on_exchange_declared(frame: pika.frame.Method):
            if not exchange_future.done():
                exchange_future.set_result(frame)
        channel.exchange_declare(exchange=exchange_name, 
                                 exchange_type='topic', 
                                 callback=on_exchange_declared)
        await exchange_future
        
        return channel
