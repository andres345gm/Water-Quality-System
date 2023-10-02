import zmq

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

PORT_FRONTEND = "6666"
PORT_BACKEND = "5555"

# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Proxy
class Proxy:
    # Method: Constructor
    def __init__(self):
        self.context = zmq.Context()
        self.frontend = self.context.socket(zmq.XSUB)
        self.frontend.bind("tcp://*:" + PORT_FRONTEND)
        self.backend = self.context.socket(zmq.XPUB)
        self.backend.bind("tcp://*:" + PORT_BACKEND)
        print("Proxy running...")

    # end def

    # Method: Run
    def run(self):
        try:
            zmq.proxy(self.frontend, self.backend)
        except Exception as e:
            print("An error occurred:", str(e))

    # end def


# end class

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def main():
    # Create a proxy object and run it
    proxy = Proxy()
    try:
        proxy.run()
    except KeyboardInterrupt:
        # Close the publisher and terminate the ZeroMQ context on KeyboardInterrupt
        proxy.frontend.close()
        proxy.backend.close()
        proxy.context.term()
    # end try


if __name__ == "__main__":
    main()
