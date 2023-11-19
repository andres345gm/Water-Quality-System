import argparse
from datetime import datetime

import zmq
import time

from MeasureService import MeasureService
import threading

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

# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""
# Function: Performance Test
def performance_test(time_stamp):
    source_message_time = datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    time_delta = current_time - source_message_time
    print(f"The time from occurrence to storage of the measurement is: {time_delta}")
"""


# end def


# Monitor
class Monitor:

    # Method: Constructor
    def __init__(self, topic):
        # Initialize ZeroMQ context and subscriber socket
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.topic = topic
        self.subscriber.connect(f"tcp://{IP_ADDRESS_PROXY}:{PORT_PROXY}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        # Initialize publisher socket
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(
            f"tcp://{IP_ADDRESS_QUALITY_SYSTEM}:{PORT_QUALITY_SYSTEM}"
        )

        self.health_check_publisher = self.context.socket(zmq.PUB)
        self.health_check_publisher.connect(f"tcp://{IP_ADDRESS_HEALTH_CHECK}:{PORT_HEALTH_CHECK}")

        self.health_check_subscriber = self.context.socket(zmq.SUB)
        self.health_check_subscriber.bind(f"tcp://{IP_ADDRESS_HEALTH_CHECK_MONITOR}:{PORT_HEALTH_CHECK_MONITOR}")
        self.health_check_subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

        self.measure_service = MeasureService()
        print(topic + " monitor running...")
        # Iniciar el subproceso para publicar el topic
        topic_publisher_thread = threading.Thread(target=self.publish_topic)
        topic_publisher_thread.daemon = True
        topic_publisher_thread.start()

    # end def

    def publish_topic(self):
        while True:
            self.health_check_publisher.send_string(self.topic)
            time.sleep(3)
    '''
    # Method: Receive
    def receive(self):
        # While the program is running, receive messages
        while True:
            healthCheckMessage = self.health_check_subscriber.recv_multipart()
            newMonitors = healthCheckMessage[1].decode()
            if newMonitors != "":
                print("Se ha detectado que los monitores: " + newMonitors + " están caidos")
                #suscribirse a los nuevos monitores y a el mismo tambien
                self.subscriber.setsockopt_string(zmq.SUBSCRIBE,  )
            else:
                self.subscriber.setsockopt_string(zmq.SUBSCRIBE, self.topic)
            message = self.subscriber.recv_multipart()
            received_value = message[1].decode()
            time_stamp = message[2].decode()
            print(time_stamp, ": ", received_value)
            # Check if the received value is within the limits
            self.check_value(received_value, time_stamp)
            # performance_test(time_stamp)

        # end while

    # end def
    '''
    def receive(self):
        # While the program is running, receive messages
        while True:
            # Recibir mensaje del health check
            print("Esperando mensaje de health check")
            health_check_message = self.health_check_subscriber.recv_multipart()
            print("Mensaje recibido")
            # Mirar cuantos objetos hay en el mensaje
            print("Longitud del mensaje: " + str(len(health_check_message)))

            if len(health_check_message) == 3:
                print("Mensaje: " + str(health_check_message))
                print("Mensaje 0: " + str(health_check_message[0].decode()))
                print("Mensaje 1: " + str(health_check_message[1].decode()))
                print("Mensaje 2: " + str(health_check_message[2].decode()))
                new_monitors = health_check_message[1].decode()
            # Verificar si no hay que suplir a nadie
            #if new_monitors != "":
                print(f"Se ha detectado que los monitores: {new_monitors} están caídos")

                # Suscribirse a los nuevos monitores y al mismo también
                topics_to_subscribe = new_monitors.split()
                topics_to_subscribe.append(self.topic)

                self.subscriber.setsockopt_string(zmq.SUBSCRIBE, " ".join(topics_to_subscribe))
            else:
                print("la longitud del mensaje no es 3")
                print("Mensaje: " + str(health_check_message))
                #self.subscriber.setsockopt_string(zmq.SUBSCRIBE, self.topic)

            print("Esperando mensaje del sensor")
            message = self.subscriber.recv_multipart()
            print("Mensaje recibido del sensor")
            received_value = message[1].decode()
            time_stamp = message[2].decode()
            print(time_stamp, ": ", received_value)

            # Check if the received value is within the limits
            self.check_value(received_value, time_stamp)


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
    def check_value(self, received_value, time_stamp):
        # Check if the received value is within the limits
        if float(received_value) < 0:
            return

        self.measure_service.insert_measure(self.create_measure_json(received_value, time_stamp))

        if LIMIT_VALUES[self.topic][0] > float(received_value):
            self.send_alarm(
                time_stamp
                + ": "
                + self.topic
                + " is too low, the current "
                + self.topic
                + " is: "
                + received_value
            )
        elif LIMIT_VALUES[self.topic][1] < float(received_value):
            self.send_alarm(
                time_stamp
                + ": "
                + self.topic
                + " is too high, the current "
                + self.topic
                + " is: "
                + received_value
            )

    # end def

    # Method create measure JSON
    def create_measure_json(self, received_value, time_stamp):
        return {
            "type of measure": self.topic,
            "value": received_value,
            "datetime": time_stamp
        }

    # end def


# end class

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


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
        monitor.subscriber.close()
        monitor.context.term()
        monitor.health_check_subscriber.close()
        monitor.health_check_publisher.close()
        monitor.context.term()

    # end try


# end def


if __name__ == "__main__":
    main()
