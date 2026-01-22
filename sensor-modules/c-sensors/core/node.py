from typing import Any, Callable, TypeVar, Awaitable
import asyncio

from server_connection import ServerConnection
from publisher import Publisher
from subscriber import Subscriber
from timer import Timer 
from message_types import SerializableMsg

TMsg = TypeVar("TMsg", bound=SerializableMsg)

class Node:
    """
    A Node in the graph.

    A Node is the primary entrypoint for system communication.
    It can be used to create entities such as publishers, subscribers, 
    services, and clients.
    """
    def __init__(self, node_name: str) -> None:
        """
        Create a Node.

        :param node_name: A name to give to this node.
        """
        self.node_name = node_name
        self.is_started = asyncio.Event()
        self._server_connection = ServerConnection()
    
    # When I start I want to connect to the RabbitMQ Server
    def start(self):
        self.is_started.set()

    def stop(self):
        self.is_started.clear()

    def create_publisher(self, 
                         msg_type: type[TMsg], 
                         exchange: str
    ) -> Publisher:
        """
        Create a new publisher.

        :param msg_type: The type of messages the publisher will publish.
        :param exchange: The name of the exchange the publisher will publish to.
        """
        new_channel = self._server_connection.setup_channel(exchange)
        return Publisher(msg_type, exchange, new_channel)

    def create_subscription(self, 
                            msg_type: type[TMsg], 
                            exchange: str, 
                            user_callback: Callable[[TMsg], Awaitable[Any]]
    ) -> Subscriber:
        """
        Create a new subscription.

        :param msg_type: The type of messages the subscription will subscribe to.
        :param exchange: The name of the exchange the subscription will subscribe to.
        :param callback: A user-defined callback function that is called when a
            message is received by the subscription.
        """
        new_channel = self._server_connection.setup_channel(exchange)
        return Subscriber(msg_type, exchange, user_callback, new_channel)

    # TODO: Create a dedicated Timer class to return
    def create_timer(self, 
                     timer_period: float, 
                     timer_callback: Callable[[], Awaitable[Any]]
    ):
        asyncio.create_task(self._timer_loop(timer_period, timer_callback))


    async def _timer_loop(self, 
                         timer_period: float, 
                         timer_callback: Callable[[], Awaitable[Any]]
    ):
        await self.is_started.wait()
        while self.is_started.is_set():
            await asyncio.sleep(timer_period)
            await timer_callback()


        

