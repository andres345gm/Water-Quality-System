import zmq


class Proxy:
    def __init__(self, frontend_port, backend_port):
        self.context = zmq.Context()
        self.frontend = self.context.socket(zmq.XSUB)
        self.frontend.bind("tcp://*:" + frontend_port)
        self.backend = self.context.socket(zmq.XPUB)
        self.backend.bind("tcp://*:" + backend_port)
        print("Proxy running...")

    def run(self):
        try:
            zmq.proxy(self.frontend, self.backend)
        except Exception as e:
            print("An error occurred:", str(e))


def main():
    proxy = Proxy("6666", "5555")
    try:
        proxy.run()
    except KeyboardInterrupt:
        proxy.frontend.close()
        proxy.backend.close()
        proxy.context.term()


if __name__ == "__main__":
    main()
