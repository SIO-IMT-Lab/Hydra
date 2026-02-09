import argparse
from typing import Sequence

from core.node import Node
from core.message_types import String
from core.launch import spin

class Recorder(Node):

    def __init__(self):
        super().__init__('recorder')
        self.time_subscriber = self.create_subscription(
                msg_type=String, 
                exchange="time",
                user_callback=self.recorder_callback,
                binding_keys=['#']
        )
        self.conductivity_subscriber = self.create_subscription(
                msg_type=String, 
                exchange="conductivity",
                user_callback=self.recorder_callback,
                binding_keys=['#']
        )

    def recorder_callback(self, msg):
        # TODO: Log the data into a 
        print(f"I heard: {msg.data}")
        # self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    recorder = Recorder()
    spin(recorder)

if __name__ == '__main__':
    main()

