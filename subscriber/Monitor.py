import sys

import zmq

LIMIT_VALUES_TEMPERATURE = [68, 89]
LIMIT_VALUES_PH = [6.0, 8.0]
LIMIT_VALUES_OXYGEN = [2.0, 11.0]


class Monitor:
    def __init__(self, topic, ip_sub, port_sub, ip_pub, port_pub):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.topic = topic
        self.subscriber.connect(f"tcp://{ip_sub}:{port_sub}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(f"tcp://{ip_pub}:{port_pub}")
        print(topic + " monitor running...")

    def receive(self):
        while True:
            message = self.subscriber.recv_multipart()
            received_value = message[1].decode()
            print("Message received:", received_value)
            self.check_value(received_value)

    def send_alarm(self, message):
        try:
            self.publisher.send_string(str(message))
            print("Message sent:", message)
        except Exception as e:
            print("An error occurred:", str(e))

    def check_value(self, received_message):
        if self.topic == "temperature":
            if float(received_message) < LIMIT_VALUES_TEMPERATURE[0]:
                self.send_alarm("ALARM! Temperature is too low, the current temperature is: " + received_message + "°F")
            elif float(received_message) > LIMIT_VALUES_TEMPERATURE[1]:
                self.send_alarm("ALARM! Temperature is too high, the current temperature is: " + received_message + "ºF")
        elif self.topic == "ph":
            if float(received_message) < LIMIT_VALUES_PH[0]:
                self.send_alarm("ALARM! pH is too low, the current pH is: " + received_message)
            elif float(received_message) > LIMIT_VALUES_PH[1]:
                self.send_alarm("ALARM! pH is too high, the current pH is: " + received_message)
        elif self.topic == "oxygen":
            if float(received_message) < LIMIT_VALUES_OXYGEN[0]:
                self.send_alarm("ALARM! Oxygen is too low, the current oxygen is: " + received_message)
            elif float(received_message) > LIMIT_VALUES_OXYGEN[1]:
                self.send_alarm("ALARM! Oxygen is too high, the current oxygen is: " + received_message)


def validate_arguments():
    # The expected arguments are: -t topic
    # An example of the input is: python3 Sensor.py -t topic
    if len(sys.argv) != 3:
        arguments_message()
        sys.exit(1)

    if sys.argv[1] != "-t":
        arguments_message()
        sys.exit(1)

    if sys.argv[2] != "temperature" and sys.argv[2] != "ph" and sys.argv[2] != "oxygen":
        arguments_message()
        sys.exit(1)


def arguments_message():
    print("The expected arguments are: -t topic")
    print("The topic must be temperature, ph or oxygen")
    print("An example of the input is python3 Sensor.py -t temperature")


validate_arguments()
monitor = Monitor("ph", "127.0.0.1", "5555", "127.0.0.1", "7777")
try:
    monitor.receive()
except KeyboardInterrupt:
    monitor.subscriber.close()
    monitor.context.term()
