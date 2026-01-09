class Publisher:

    def __init__(self, msg_type, topic: str) -> None:
        """
        Create a container for a publisher.

        .. warning:: Do not create a publisher with this constructor, instead
           call :method:`.Node.create_publisher`.

        A publisher is used as a primary means of communication by publishing
        messages on a topic.

        :param msg_type: The type of messages the publisher will publish.
        :param topic: The name of the topic the publisher will publish to.
        """
        self.msg_type = msg_type
        self.topic = topic

    def publish(msg):
        """
        Send a message to the topic for the publisher.

        :param msg: The message to publish.
        :raises: TypeError if the type of the passed message isn't an instance
          of the provided type when the publisher was constructed.
        """

    def get_subscription_count(self) -> int:
        """Get the amount of subscribers that this publisher has."""
        with self.handle:
            return self.__publisher.get_subscription_count()

    @property
    def topic_name(self) -> str:
        with self.handle:
            return self.__publisher.get_topic_name()

    @property
    def logger_name(self) -> str:
        """Get the name of the logger associated with the node of the publisher."""
        with self.handle:
            return self.__publisher.get_logger_name()
