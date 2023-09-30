import zmq
import time
import sys


class Sensor:
    def __init__(self, topic, ip, port):
        self.topic = topic
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(f"tcp://{ip}:{port}")
        print(topic + " sensor running...")

    def send(self, message):
        try:
            self.publisher.send_multipart([self.topic.encode("UTF-8"), message.encode("UTF-8")])
            print("Message sent:", message)
        except Exception as e:
            print("An error occurred:", str(e))


"""
def validate_arguments:
    #The expected arguments are: topic, t, file
    #An example of the input is python3 Sensor.py -t temperature -v 68.89 -f temperature.txt
    if sys.argv != 5:
        print("The expected arguments are: topic, t, file")
        print("An example of the input is python3 Sensor.py -t temperature -v 68.89 -f temperature.txt")
        sys.exit(1)
"""


sensor = Sensor("ph", "127.0.0.1", "6666")
try:
    while True:
        sensor.send("9.0")
        time.sleep(5)
except KeyboardInterrupt:
    sensor.publisher.close()
    sensor.context.term()
