from typing import Any, Callable, TypeVar, Awaitable, Sequence
import asyncio
import logging

import serial_asyncio
from serial.serialutil import SerialException

from .server_connection import ServerConnection
from .publisher import Publisher
from .subscriber import Subscriber
from .message_types import SerializableMsg


TMsg = TypeVar("TMsg", bound=SerializableMsg)
TRequest = TypeVar("TRequest", bound=SerializableMsg)
TResponse = TypeVar("TResponse", bound=SerializableMsg)

class Node:
    """
    A Node in the graph.

    A Node is the primary entrypoint for system communication.
    It can be used to create entities such as publishers, subscribers, 
    services, and clients.
    """
    def __init__(self, node_name: str, config: dict) -> None:
        """
        Create a Node.

        :param node_name: A name to give to this node.
        :param config: A dictionary containing the node's configuration.
        """
        self.node_name = node_name
        self.logger = logging.getLogger(f"node.{node_name}")
        
        self.node_config = config.get("nodes", {}).get(node_name, {})
        self.exchanges = config.get("exchanges", {})
        
        self.is_started = asyncio.Event()
        self._server_connection = ServerConnection(self.logger)
        
        self._publishers = []
        self._subscribers = []
        
        self.pending_tasks = []
        self._tasks = []
    
    # When I start I want to connect to the RabbitMQ Server
    async def start(self):
        self._server_connection.connect()
        
        for publisher in self._publishers:
            channel = await self._server_connection.create_channel(publisher.exchange_name)
            publisher.attach_channel(channel)

        for subscriber in self._subscribers:
            channel = await self._server_connection.create_channel(subscriber.exchange_name)
            await subscriber.attach_channel(channel)
        
        for task in self.pending_tasks:
            self._tasks.append(asyncio.create_task(task()))
        self.pending_tasks.clear()
                    
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
                            user_callback: Callable[[TMsg], Awaitable[Any]],
                            binding_keys: Sequence[str]
    ) -> Subscriber:
        """
        Create a new subscription.

        :param msg_type: The type of messages the subscription will subscribe to.
        :param exchange: The name of the exchange the subscription will subscribe to.
        :param callback: A user-defined callback function that is called when a
            message is received by the subscription.
        """
        subscriber = Subscriber(msg_type, exchange, user_callback, binding_keys)
        self._subscribers.append(subscriber)
        return subscriber
    
    def create_service(self,
                       response_type: type[TResponse],
                       response_exchange: str,
                       request_type: type[TRequest],
                       request_exchange: str, 
                       user_callback: Callable[[TRequest], Awaitable[Any]],
    ) -> None:
        """
        Create a new service.

        :param response_type:
        :param response_exchange:
        :param request_type:
        :param request_exchange:
        :param user_callback:
        """
        response_publisher = self.create_publisher(response_type, response_exchange)

        async def service_handler(request: TRequest) -> None:
            response = await user_callback(request)
            response_publisher.publish(response, response.correlation_id)
        
        self.create_subscription(
            msg_type=request_type,
            exchange=request_exchange,
            user_callback=service_handler,
            binding_keys=["#"],
        )
    
    async def call_service(self,
                           response_type: type[TResponse],
                           response_exchange: str,
                           request_publisher: Publisher,
                           request: TRequest,
                           timeout: float = 5.0
    ) -> TResponse:
        """
        Create a Publisher
        """
        loop = asyncio.get_running_loop()
        service_future = loop.create_future()

        async def on_response(response: TResponse) -> None:
            if not service_future.done():
                service_future.set_result(response)

        subscriber = Subscriber(
            msg_type=response_type,
            exchange=response_exchange,
            user_callback=on_response,
            binding_keys=[request.correlation_id]
        )
        channel = await self._server_connection.create_channel(response_exchange)
        await subscriber.attach_channel(channel)

        request_publisher.publish(request, request.correlation_id)

        try:
            return await asyncio.wait_for(service_future, timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(
                "Service call with correlation ID %s timed out after %ss",
                request.correlation_id,
                timeout
            )
        finally:
            if not channel.is_closed:
                channel.close() 

    def create_task(self, task_callback: Callable[[], Awaitable[Any]]) -> None:
        """
        Creates a new asyncio task that runs the provided callback. This is an
        internal and external interface for running any asynchronous code that 
        needs to run.
        
        :param task_callback: Description
        """
        if not self.is_started.is_set():
            self.pending_tasks.append(task_callback)
        else:
            self._tasks.append(asyncio.create_task(task_callback()))

    def create_timer(self, 
                     timer_period: float, 
                     timer_callback: Callable[[], Awaitable[Any]]
    ):
        self.create_task(lambda: self._timer_loop(timer_period, timer_callback))

    async def _timer_loop(self, 
                          timer_period: float, 
                          timer_callback: Callable[[], Awaitable[Any]]
    ):
        await self.is_started.wait()
        while self.is_started.is_set():
            start = asyncio.get_running_loop().time()
            await timer_callback()
            elapsed = asyncio.get_running_loop().time() - start
            sleep_time = max(0.0, timer_period - elapsed)
            await asyncio.sleep(sleep_time)

    async def open_serial_connection(self, url: str, baudrate: int):
        retry_period = 2
        max_attempts = 3
        attempts = 0

        while True:
            try:
                reader, writer = await serial_asyncio.open_serial_connection(
                    url=url,
                    baudrate=baudrate,
                )

                self.logger.info(
                    "Connected to %s at %s baud",
                    url,
                    baudrate,
                )

                return reader, writer

            except SerialException as err:
                attempts += 1

                if attempts < max_attempts:
                    self.logger.warning(
                        "Serial connection failed: %s. Attempt %s/%s failed. "
                        "Retrying in %s seconds...",
                        err,
                        attempts,
                        max_attempts,
                        retry_period,
                    )
                    await asyncio.sleep(retry_period)
                else:
                    self.logger.error(
                        "Serial connection failed after %s attempts: %s",
                        max_attempts,
                        err,
                    )
                    raise

            except ValueError as err:
                self.logger.error(
                    "Invalid serial configuration: %s. Check baudrate.",
                    err,
                )
                raise

            except Exception:
                self.logger.exception(
                    "Unexpected error while opening serial connection"
                )
                raise
                
