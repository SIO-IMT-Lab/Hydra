from node import Node
from message_types import String
from launch import spin

class TestSubscriber(Node):

    def __init__(self):
        super().__init__('test_subscriber')
        self.subscription = self.create_subscription(String, 'test', self.listener_callback)

    def listener_callback(self, msg):
        print(f"I heard: {msg.data}")
        # self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    minimal_subscriber = TestSubscriber()
    spin(minimal_subscriber)

if __name__ == '__main__':
    main()
