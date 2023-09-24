import zmq

LIMIT_VALUES_TEMPERATURE = [68, 89]
LIMIT_VALUES_PH = [6.0, 8.0]
LIMIT_VALUES_OXYGEN = [2.0, 11.0]


class Monitor:
    def __init__(self, topic, ip, port):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.topic = topic
        self.subscriber.connect(f"tcp://{ip}:{port}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        print(topic + " monitor running...")

    def receive(self):
        while True:
            message = self.subscriber.recv_multipart()
            print("Message received:", message[1].decode())


# Create the subscriber socket
monitor = Monitor("ph", "127.0.0.1", "5555")
monitor.receive()

context = zmq.Context()
