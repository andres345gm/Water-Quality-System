import pandas as pd
import argparse
from datetime import datetime

import zmq
import socket

import time

from MeasureService import MeasureService
import threading

import ntplib
from time import ctime
import datetime

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Class NTPServer
class NTPServer:

    # Method: Constructor
    def __init__(self):
        self.ntp_server = 'pool.ntp.org'
        self.clientNTP = ntplib.NTPClient()

    # end def

    # Method: Insert measure into database
    def obtain_real_time(self):
        try:
            # Query NTP Server
            response = self.clientNTP.request(self.ntp_server)

            # Returns time
            return datetime.datetime.fromtimestamp(response.tx_time)

        except Exception as e:
            # Error
            return datetime.datetime(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # end def

# end class

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

LIMIT_VALUES = {"temperature": (68, 89), "PH": (6.0, 8.0), "oxygen": (2.0, 11.0)}

IP_ADDRESS_PROXY = "127.0.0.1"
PORT_PROXY = "5555"

IP_ADDRESS_QUALITY_SYSTEM = "127.0.0.1"
PORT_QUALITY_SYSTEM = "7777"

IP_ADDRESS_HEALTH_CHECK = "127.0.0.1"
PORT_HEALTH_CHECK = "8888"

IP_ADDRESS_HEALTH_CHECK_MONITOR = "127.0.0.1"
PORT_HEALTH_CHECK_MONITOR = "8889"

NTPServer = NTPServer()

# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Monitor
class Monitor:

    # Method: Constructor
    def __init__(self, topic):
        # Initialize ZeroMQ context and subscriber socket
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.topic = topic
        self.subscribed = set()
        self.subscribe = set()
        self.subscriber.connect(f"tcp://{IP_ADDRESS_PROXY}:{PORT_PROXY}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.subscriber.setsockopt(zmq.RCVTIMEO,1000)  # Configura un tiempo de espera de 1000 ms (1 segundo)

        # Initialize publisher socket
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(
            f"tcp://{IP_ADDRESS_QUALITY_SYSTEM}:{PORT_QUALITY_SYSTEM}"
        )

        # Testing
        self.values = []
        self.send_times = []
        self.arrival_times = []
        self.substraction = []

        self.health_check_publisher = self.context.socket(zmq.PUB)
        self.health_check_publisher.connect(f"tcp://{IP_ADDRESS_HEALTH_CHECK}:{PORT_HEALTH_CHECK}")

        self.health_check_subscriber = self.context.socket(zmq.SUB)
        self.health_check_subscriber.connect(f"tcp://{IP_ADDRESS_HEALTH_CHECK_MONITOR}:{PORT_HEALTH_CHECK_MONITOR}")
        self.health_check_subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.health_check_subscriber.setsockopt(zmq.RCVTIMEO,
                                                1000)  # Configura un tiempo de espera de 1000 ms (1 segundo)

        self.measure_service = MeasureService()
        print(topic + " monitor running...")
        # Iniciar el subproceso para publicar el topic
        topic_publisher_thread = threading.Thread(target=self.publish_topic)
        topic_publisher_thread.daemon = True
        topic_publisher_thread.start()
        

    # end def

    def close_program(self):
        self.subscriber.close()
        self.publisher.close()
        self.health_check_subscriber.unbind(f"tcp://{IP_ADDRESS_HEALTH_CHECK_MONITOR}:{PORT_HEALTH_CHECK_MONITOR}")
        self.health_check_publisher.close()
        self.context.term()

    def publish_topic(self):
        while True:
            self.health_check_publisher.send_string(self.topic)
            time.sleep(1)

    def receive(self):
        # While the program is running, receive messages
        while True:
            try:
                health_check_message = self.health_check_subscriber.recv_multipart()
            except zmq.error.Again:
                pass
            else:
                fall_monitors = health_check_message[1].decode()
                if fall_monitors != 'set()':
                    fall_monitors = fall_monitors.replace("{", "").replace("}", "").replace("'", "").split(", ")
                    # Crear una copia del conjunto
                    subscribed_copy = self.subscribed.copy()
                    for monitor in subscribed_copy:
                        if monitor not in fall_monitors:
                            self.subscriber.setsockopt_string(zmq.UNSUBSCRIBE, monitor)
                            self.subscribed.remove(monitor)
                    for monitor in fall_monitors:
                        if monitor not in self.subscribed:
                            self.subscriber.setsockopt_string(zmq.SUBSCRIBE, monitor)
                            self.subscribed.add(monitor)
                else:
                    # Suscribirse al tema original
                    for monitor in self.subscribed:
                        self.subscriber.setsockopt_string(zmq.UNSUBSCRIBE, monitor)


            try:
                message = self.subscriber.recv_multipart()
            except zmq.error.Again:
                # No llegó ningún mensaje en el tiempo de espera
                pass
            else:
                topic = message[0].decode()
                received_value = message[1].decode()
                time_stamp = message[2].decode()
                current_time = NTPServer.obtain_real_time().strftime("%Y-%m-%d %H:%M:%S.%f")

                if time_stamp != "0001-01-01 00:00:00.000000" and current_time != "0001-01-01 00:00:00.000000":
                    self.values.append(received_value)
                    self.send_times.append(time_stamp)
                    self.arrival_times.append(current_time)
                    subtraction_result = format(abs(substraction_times(current_time, time_stamp).total_seconds()), '.5f')
                    self.substraction.append(subtraction_result)
                
                print(topic,"=>",time_stamp, ": ", received_value)
                # Check if the received value is within the limits
                self.check_value(topic, received_value, time_stamp)


    # Method: Quality control

    # Method: Send alarm
    def send_alarm(self, message):
        # Send the alarm message to the quality system
        try:
            self.publisher.send_string(str(message))
        except Exception as e:
            print("An error occurred:", str(e))
        # end try

    # end def

    # Method: Check value
    def check_value(self, topic, received_value, time_stamp):
        # Check if the received value is within the limits
        if float(received_value) < 0:
            return

        self.measure_service.insert_measure(self.create_measure_json(topic, received_value, time_stamp))

        if LIMIT_VALUES[topic][0] > float(received_value):
            self.send_alarm(
                time_stamp
                + ": "
                + topic
                + " is too low, the current "
                + topic
                + " is: "
                + received_value
            )
        elif LIMIT_VALUES[topic][1] < float(received_value):
            self.send_alarm(
                time_stamp
                + ": "
                + topic
                + " is too high, the current "
                + topic
                + " is: "
                + received_value
            )

    # end def

    # Method create measure JSON
    def create_measure_json(self, topic, received_value, time_stamp):
        return {
            "type of measure": topic,
            "value": received_value,
            "datetime": time_stamp
        }

    # end def


# end class

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def substraction_times(time_a, time_b):
    return datetime.datetime.strptime(time_a, "%Y-%m-%d %H:%M:%S.%f") - datetime.datetime.strptime(time_b, "%Y-%m-%d %H:%M:%S.%f")

# Method: Validate arguments
def validate_arguments():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Sensor Argument Validator")
    # Define the arguments
    parser.add_argument(
        "-t",
        "--type",
        required=True,
        choices=["temperature", "PH", "oxygen"],
        help="Monitor type (temperature, ph, or oxygen)",
    )

    args = parser.parse_args()
    return args


# end def


# Method: Main
def main():
    # Validate the arguments
    args = validate_arguments()
    # Create a monitor object and receive messages
    monitor = Monitor(args.type)
    try:
        monitor.receive()
    except KeyboardInterrupt:
        df = pd.DataFrame({
            'Valor': monitor.values,
            'Tiempo Envío': monitor.send_times,
            'Tiempo Llegada': monitor.arrival_times,
            'Resta': monitor.substraction
        })
        df.to_excel("MonitorTiempo.xlsx", index=False)
    # end try


# end def


if __name__ == "__main__":
    main()
