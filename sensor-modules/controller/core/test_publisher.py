from node import Node 
from message_types import String
from launch import spin

class TestPublisher(Node):

    def __init__(self):
        super().__init__("test_publisher")
        self.publisher = self.create_publisher(String, 'test')
        self.create_timer(5.0, self.test_publish)

    async def test_publish(self):
        msg = String(data="Did it work?")
        self.publisher.publish(msg, "test")

def main(args=None):
    test_publisher = TestPublisher()
    spin(test_publisher)

if __name__ == '__main__':
    main()
