import zmq


class Quality_system:
    def __init__(self, ip, port):
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.SUB)
        self.publisher.bind(f"tcp://{ip}:{port}")
        self.publisher.setsockopt_string(zmq.SUBSCRIBE, "")
        print("Quality system running...")

    def receive(self):
        while True:
            message = self.publisher.recv_multipart()
            print("Message received:", message[1].decode())

