import zmq
import time

IP_ADDRESS_MONITOR = "127.0.0.1"
PORT_MONITOR = "8888"  # Puerto utilizado para los controles de salud
HEALTH_CHECK_TIMEOUT = 5   # Tiempo de espera para considerar que un monitor está inactivo (5 segundos)

class HealthCheck:
    def __init__(self):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.bind(f"tcp://{IP_ADDRESS_MONITOR}:{PORT_MONITOR}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(f"tcp://{IP_ADDRESS_MONITOR}:{PORT_MONITOR}")


        # Inicializa contadores para cada tipo de mensaje
        self.message_counters = {
            "temperature": 0,
            "Ph": 0,
            "oxygen": 0
        }

        print("Health Check running...")

    def receive(self):
        print("Control de salud en ejecución...")
        last_message_time = time.time()

        while True:
            message = self.subscriber.recv_string()
            print(message)

            # Actualiza el contador para el tipo de mensaje recibido
            message_type = message.split(":")[0].strip()
            if message_type in self.message_counters:
                self.message_counters[message_type] += 1

            # Verifica si han pasado 4 segundos y resetea los contadores
            current_time = time.time()
            if current_time - last_message_time >= HEALTH_CHECK_TIMEOUT:
                last_message_time = current_time
                for message_type in self.message_counters:
                    if self.message_counters[message_type] == 0:
                        print(f"Advertencia: No se recibieron mensajes de tipo {message_type} en {HEALTH_CHECK_TIMEOUT} segundos.")
                    else:
                        print("Enviando mensaje a todos los demás monitores")
                    # Reinicia el contador
                    self.message_counters[message_type] = 0

def main():
    health_check = HealthCheck()
    try:
        health_check.receive()
    except KeyboardInterrupt:
        health_check.subscriber.close()
        health_check.context.term()

if __name__ == "__main__":
    main()