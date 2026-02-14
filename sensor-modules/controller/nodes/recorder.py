from core.node import Node
from core.message_types import String
from core.launch import spin

class Recorder(Node):
    def __init__(self):
        super().__init__("recorder")

        self._subs = []

        exchanges = [
            ("conductivity", String),
            ("sita", String),
            ("gps", Time),
        ]

        for exchange, msg_type in exchanges:
            sub = self.create_subscription(
                msg_type=msg_type,
                exchange=exchange,
                user_callback=self._make_callback(exchange),
                binding_keys=["#"],
            )
            self._subs.append(sub)

    def _make_callback(self, exchange: str):
        def _cb(msg):
            print(f"[{exchange}] {msg.data}")
        return _cb

def main():
    node = Recorder()
    spin(node)

if __name__ == "__main__":
    main()

