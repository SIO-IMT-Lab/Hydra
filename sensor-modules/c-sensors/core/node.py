class Node:
    """
    A Node in the graph.

    A Node is the primary entrypoint for system communication.
    It can be used to create entities such as publishers, subscribers, 
    services, and client.
    """
    def __init__(self, node_name: str) -> None:
        """
        Create a Node.

        :param node_name: A name to give to this node.
        """
        self.node_name = node_name

    def create_publisher(self, msg_type: , topic: str):
        """
        Create a new publisher.

        :param msg_type: The type of messages the publisher will publish.
        :param topic: The name of the topic the publisher will publish to.
        """

    def create_subscription(self, msg_type: , topic: str, callback: ):
        """
        Create a new subscription.

        :param msg_type: The type of messages the subscription will subscribe to.
        :param topic: The name of the topic the subscription will subscribe to.
        :param callback: A user-defined callback function that is called when a message is
            received by the subscription.
        """

