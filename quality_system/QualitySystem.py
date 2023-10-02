import zmq

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

IP_ADDRESS = "127.0.0.1"
PORT = "7777"

# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Quality System
class QualitySystem:
    # Method: Constructor
    def __init__(self):
        # Initialize ZeroMQ context and subscriber socket
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.bind(f"tcp://{IP_ADDRESS}:{PORT}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        print("Quality system running...")

    # end def

    # Method: Receive
    def receive(self):
        # While the program is running, receive messages
        while True:
            message = self.subscriber.recv_string()
            print(message)
        # end while
    # end def

# end class

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def main():
    # Create a quality system object and receive messages
    quality_system = QualitySystem()
    try:
        quality_system.receive()
    except KeyboardInterrupt:
        # Close the publisher and terminate the ZeroMQ context on KeyboardInterrupt
        quality_system.subscriber.close()
        quality_system.context.term()
    # end try


if __name__ == "__main__":
    main()
