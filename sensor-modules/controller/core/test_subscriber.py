import argparse
from typing import Sequence

from .node import Node
from .message_types import String
from .launch import spin

class TestSubscriber(Node):

    def __init__(self, exchange: str = "test", 
                       binding_keys: Sequence[str] = ['#']):
        super().__init__('test_subscriber')
        self.subscription = self.create_subscription(
                msg_type=String, 
                exchange=exchange,
                user_callback=self.listener_callback,
                binding_keys=binding_keys
        )

    async def listener_callback(self, msg):
        print(f"I heard: {msg.data}")
        # self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    parser = argparse.ArgumentParser(description="Subscriber Tester")
    parser.add_argument(
        "--exchange",
        default="test",
        help="Exchange this subscriber should listen to. Default is 'test'."
    )
    parser.add_argument(
        "--binding_keys",
        nargs='*',
        default=['#'],
        help="Any binding_keys this subscriber should filter. Default is no filter."
    )
    args = parser.parse_args()
    minimal_subscriber = TestSubscriber(args.exchange, args.binding_keys)
    spin(minimal_subscriber)

if __name__ == '__main__':
    main()
