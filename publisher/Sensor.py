import zmq
import time
import datetime
import random
import sys
import argparse
import json

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

IP_ADDRESS = "127.0.0.1"
PORT = "6666"

LIMIT_VALUES = {
    'temperature': (68, 89),
    'PH': (6.0, 8.0),
    'oxygen': (2.0, 11.0)
}

# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Sensor

class Sensor:
    def __init__(self, sensor, interval, probability):
        self.sensor = sensor
        self.interval = interval
        self.probability = probability
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(f"tcp://{IP_ADDRESS}:{PORT}")
        print("The" + self.sensor + " sensor running...")

    def generate_random_value(self):
        num = [1,2,3]
        x =random.choices(num, weights=(self.probability['correct'],
                                        self.probability['out_of_range'],
                                        self.probability['error']))[0]
        if x == 1:
            return str(random.uniform(LIMIT_VALUES[self.sensor][0], LIMIT_VALUES[self.sensor][1]))
        elif x == 2:
            return str(random.uniform(0, 68) if random.random() < 0.5 else random.uniform(90, 100))
        elif x == 3:
            return str(-1)

    def send(self):
        try:
            value = self.generate_random_value()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.publisher.send_multipart([self.sensor.encode("UTF-8"), value.encode("UTF-8"),current_time.encode("UTF-8")])
            print(current_time)
            print("Message sent:", value)
        except Exception as e:
            print("An error occurred:", str(e))

#end Sensor

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Argument verification
def verify_args():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Sensor - Introduction to Distributed Systems")

    # Define the arguments
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-c','--config', help='JSON configuration file', required=True)
    requiredNamed.add_argument('-s','--sensor', choices=['temperature', 'PH', 'oxygen'], help='Sensor type', required=True)
    requiredNamed.add_argument('-i','--interval', type=int, help='Time interval (in seconds)', required=True)

    # Parse command-line arguments
    args = parser.parse_args()

    return args

# Create sensor with the obtained arguments
def create_sensor(args):
    try:
        with open(args.config, 'r') as file:
            data = json.load(file)
            # MISSING
            # Verify that 'correct', 'out_of_range', and 'error' are present in the JSON
            sensor = Sensor(args.sensor, args.interval, data)
            return sensor
        
    except FileNotFoundError:
        print(f"The file {args.config} was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"The file {args.config} is not a valid JSON.")
        sys.exit(1)


def main():
    
    args = verify_args()
    sensor = create_sensor(args)
    
    try:
        while True:
            sensor.send()
            time.sleep(sensor.interval)
    except KeyboardInterrupt:
        sensor.publisher.close()
        sensor.context.term()


if __name__ == "__main__":
    main()





