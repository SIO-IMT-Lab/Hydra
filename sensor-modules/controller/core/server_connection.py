import asyncio

import pika
from pika.adapters.asyncio_connection import AsyncioConnection


class ServerConnection:
    """
    A Node's broker for communication channels

    Every time a Node is created, it will use this ServerConnection class to
    ask for a communication channel for each of its subscribers and publishers
    """

    def __init__(self, logger, host: str = 'localhost'):
        self.logger = logger.getChild("server_connection")
        self.host = host
        self.connection = None
        self.is_connected = asyncio.Event()
        
    def connect(self) -> None:
        if self.connection is not None:
            return            
        
        self.connection = AsyncioConnection(
            parameters=pika.ConnectionParameters(host=self.host),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )
        
    def on_connection_open(self, _unused_connection):
        """
        After the RabbitMQ connection is established, set flag to indicate we
        can now create channels.
        """
        self.logger.info("RabbitMQ Connection Opened")
        self.is_connected.set()

    def on_connection_open_error(self, _unused_connection, err):
        self.logger.error(
            "RabbitMQ connection open error: %r",
            err,
        )
        self.connection = None
        self.is_connected.clear()
        
    def on_connection_closed(self, _unused_connection, reason):
        self.logger.info(
            "RabbitMQ connection closed: %r",
            reason,
        )
        self.connection = None
        self.is_connected.clear()
        
    async def create_channel(self, exchange_name, exchange_type="topic"):
        if self.connection is None:
            self.connect()
        
        await self.is_connected.wait()
        
        channel = await self.open_channel()
        await self.declare_exchange(channel, exchange_name, exchange_type)
        
        return channel

    async def open_channel(self):
        loop = asyncio.get_running_loop()
        channel_future = loop.create_future()
        
        def on_channel_open(ch):
            if not channel_future.done():
                channel_future.set_result(ch)
                
        self.connection.channel(on_open_callback=on_channel_open)
        return await channel_future

    async def declare_exchange(self, channel, exchange_name, exchange_type='topic'):
        loop = asyncio.get_running_loop()
        exchange_future = loop.create_future()
        
        def on_exchange_declared(frame: pika.frame.Method):
            if not exchange_future.done():
                exchange_future.set_result(frame)
                
        channel.exchange_declare(exchange=exchange_name, 
                                 exchange_type=exchange_type, 
                                 callback=on_exchange_declared)
        await exchange_future
    
    def close(self) -> None:
        if self.connection is not None and not self.connection.is_closed:
            self.connection.close()
