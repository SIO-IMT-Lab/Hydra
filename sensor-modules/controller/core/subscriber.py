import asyncio
import json
from typing import Any, Awaitable, Callable, Generic, Sequence, TypeVar

import pika

from .message_types import SerializableMsg
from .server_connection import ServerConnection

TMsg = TypeVar("TMsg", bound=SerializableMsg)

class Subscriber(Generic[TMsg]):

    def __init__(self, 
                 msg_type: type[TMsg], 
                 exchange: str, 
                 user_callback: Callable[[TMsg], Awaitable[Any]],  
                 binding_keys: Sequence[str] = ['#']
    ) -> None:
        """
        Create a container for a subscriber.

        .. warning:: Do not create a subscriber with this constructor, instead
            call :method:`.Node.create_subscription`.

        A subscriber is used as a primary means of communication by subscribing 
        messages on an exchange.

        :param msg_type: The type of messages the subscriber will publish.
        :param exchange: The name of the exchange the subscriber will publish to.
        :param user_callback: An async defined function detailing code that
                              runs whenever a message is received.
        :param binding_keys: Filters incoming messages whose routing key matches
                             any of the ones in this list 
                             (default '#' receives all messages on the exchange).
        """
        self._msg_type = msg_type
        self._exchange = exchange 
        self._user_callback = user_callback
        self._channel = None
        self._binding_keys = binding_keys

    async def attach_channel(self, channel: pika.channel.Channel) -> None:
        self._channel = channel

        loop = asyncio.get_running_loop()

        queue_future = loop.create_future()
        def on_queue_declared(frame: pika.frame.Method):
            if not queue_future.done():
                queue_future.set_result(frame.method.queue)
        self._channel.queue_declare(queue='', 
                                    exclusive=True,
                                    callback=on_queue_declared)
        queue_name = await queue_future

        for binding_key in self._binding_keys:
            self._channel.queue_bind(
                exchange=self._exchange, 
                queue=queue_name, 
                routing_key=binding_key
            )

        self._channel.basic_consume(
            queue=queue_name, 
            on_message_callback=self._on_message, 
            auto_ack=False
        )

    def _on_message(self, 
                    channel: pika.channel.Channel, 
                    method: pika.spec.Basic.Deliver, 
                    properties: pika.spec.BasicProperties, 
                    body: bytes
    ) -> None:
        asyncio.create_task(self._dispatch(channel, method.delivery_tag, body))

    async def _dispatch(self, 
                        channel: pika.channel.Channel, 
                        delivery_tag: int, 
                        body: bytes
    ) -> None:
        try:
            res_dict = json.loads(body.decode('utf-8'))
            res_msg = self._msg_type.from_dict(res_dict)
            await self._user_callback(res_msg)
            channel.basic_ack(delivery_tag=delivery_tag)
        except Exception:
            channel.basic_nack(delivery_tag=delivery_tag, requeue=False)

    @property
    def exchange_name(self) -> str:
        """
        Name of the exchange this subscriber subscribes from.
        """
        return self._exchange 

