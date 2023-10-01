import zmq


class QualitySystem:
    def __init__(self, ip, port):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.bind(f"tcp://{ip}:{port}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        print("Quality system running...")

    def receive(self):
        while True:
            message = self.subscriber.recv_string()
            print(message)


quality_system = QualitySystem("127.0.0.1", "7777")
try:
    quality_system.receive()
except KeyboardInterrupt:
    quality_system.subscriber.close()
    quality_system.context.term()
