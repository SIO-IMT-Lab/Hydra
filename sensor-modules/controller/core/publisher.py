import json
from typing import Generic, Protocol, TypeVar

import pika

from .message_types import SerializableMsg
from .server_connection import ServerConnection

TMsg = TypeVar("TMsg", bound=SerializableMsg)

class Publisher(Generic[TMsg]):

    def __init__(self, 
                 msg_type: type[TMsg], 
                 exchange: str,
    ) -> None:
        """
        Create a container for a publisher.

        .. warning:: Do not create a publisher with this constructor, instead
            call :method:`.Node.create_publisher`.

        A publisher is used as a primary means of communication by publishing
        messages on an exchange.

        :param msg_type: The type of messages the publisher will publish.
        :param exchange: The name of the exchange the publisher will publish to.
        """
        self._msg_type = msg_type
        self._exchange = exchange
        self._channel = None

    def attach_channel(self, channel: pika.channel.Channel) -> None:
        self._channel = channel
    
    def publish(self, msg: TMsg, routing_key: str) -> None:
        """
        Send a message to the exchange for the publisher.

        :param msg: The message to publish.
        :param routing_key: Key that helps filter different messages. 
        :raises: TypeError if the type of the passed message isn't an instance
            of the provided type when the publisher was constructed.
        """
        if self._channel is None:
            raise RuntimeError("Publisher not started. node.start() must be " +
                               "called before publishing messages.")

        if not isinstance(msg, self._msg_type):
            raise TypeError(
                f"Publisher expected {self._msg_type.__name__}, got {type(msg).__name__}"
            )

        body = json.dumps(msg.to_dict()).encode("utf-8")
        self._channel.basic_publish(
            exchange=self._exchange, routing_key=routing_key, body=body)

    @property
    def exchange_name(self) -> str:
        """
        Name of the exchange this publisher publishes to.
        """
        return self._exchange 
