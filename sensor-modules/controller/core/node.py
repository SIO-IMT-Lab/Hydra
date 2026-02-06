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
        self.is_started = None
        self._server_connection = ServerConnection()
        
        self._publishers = []
        self._subscribers = []
        self._tasks = []
    
    # When I start I want to connect to the RabbitMQ Server
    async def start(self):
        if self.is_started is None:
            self.is_started = asyncio.Event()
            
        self._server_connection.connect()
        
        for publisher in self._publishers:
            channel = await self._server_connection.create_channel(publisher.exchange_name)
            publisher.attach_channel(channel)

        for subscriber in self._subscribers:
            channel = await self._server_connection.create_channel(subscriber.exchange_name)
            await subscriber.attach_channel(channel)
            
        self.is_started.set()

    def create_publisher(self, 
                         msg_type: type[TMsg], 
                         exchange: str
    ) -> Publisher:
        """
        Create a new publisher.

        :param msg_type: The type of messages the publisher will publish.
        :param exchange: The name of the exchange the publisher will publish to.
        """
        publisher = Publisher(msg_type, exchange)
        self._publishers.append(publisher)
        return publisher

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
        subscriber = Subscriber(msg_type, exchange, user_callback)
        self._subscribers.append(subscriber)
        return subscriber

    def create_task(self, task_callback: Callable[[], Awaitable[Any]]) -> None:
        """
        Creates a new asyncio task that runs the provided callback. This is an
        internal and external interface for running any asynchronous code that 
        needs to run.
        
        :param task_callback: Description
        """
        self._tasks.append(asyncio.create_task(task_callback()))

    # TODO: Create and return a dedicated Timer class
    def create_timer(self, 
                     timer_period: float, 
                     timer_callback: Callable[[], Awaitable[Any]]
    ):
        self.create_task(self._timer_loop(timer_period, timer_callback))

    async def _timer_loop(self, 
                          timer_period: float, 
                          timer_callback: Callable[[], Awaitable[Any]]
    ):
        await self.is_started.wait()
        while self.is_started.is_set():
            await asyncio.sleep(timer_period)
            await timer_callback()
