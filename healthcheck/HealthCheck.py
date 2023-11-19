import zmq
import time

IP_ADDRESS_MONITOR = "127.0.0.1"
PORT_MONITOR = "8888"  # Puerto utilizado para los controles de salud
PORT_MONITOR_HEALTH_CHECK = "8889"  # Puerto utilizado para los controles de salud
HEALTH_CHECK_TIMEOUT = 5   # Tiempo de espera para considerar que un monitor está inactivo (5 segundos)

class HealthCheck:
    def __init__(self):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.bind(f"tcp://{IP_ADDRESS_MONITOR}:{PORT_MONITOR}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(f"tcp://{IP_ADDRESS_MONITOR}:{PORT_MONITOR_HEALTH_CHECK}")


        # Inicializa contadores para cada tipo de mensaje
        self.message_counters = {
            "temperature": 0,
            "Ph": 0,
            "oxygen": 0
        }
        # Monitores caidos
        self.fall_monitors = set()
        self.all_monitors = set(["temperature", "Ph", "oxygen"])
        self.supplier = None
        print("Health Check running...")


    def notify_supplier(self):
        #Verificar si aun no tenemos un monitor que supla a otros
        if self.supplier is None:
            if "temperature" not in self.fall_monitors:
                self.supplier = "temperature"
            elif "Ph" not in self.fall_monitors:
                self.supplier = "Ph"
            elif "oxygen" not in self.fall_monitors:
                self.supplier = "oxygen"
            #Verificar que haya un monitor disponible para suplir
            if self.supplier is not None:
                print("Enviando mensaje al monitor para suplir a los monitores caidos")
                print("")
                self.subscriber.send_multipart([self.supplier.encode(),
                                                self.fall_monitors.encode()])
            else:
                print("No hay monitores disponibles para poder suplir la operación")
        else:
            # Verificar si el monitor que estaba supliendo ya no está caido
            if(self.supplier in self.fall_monitors):
                self.supplier = None
                self.notify_supplier()
            else:
                # Notificar al monitor que debe suplir o seguir supliendo a los monitores caidos
                self.subscriber.send_multipart([self.supplier.encode(),
                                                self.fall_monitors.encode()])

        
    def receive(self):
        print("Control de salud en ejecución...")
        last_message_time = time.time()

        while True:
            print("Esperando mensaje...")
            message = self.subscriber.recv_string()
            
            print("el mensaje es ", message)
            # Actualiza el contador para el tipo de mensaje recibido
            message_type = message.split(":")[0].strip()
            if message_type in self.message_counters:
                self.message_counters[message_type] += 1

            # Verifica si han pasado 5 segundos y resetea los contadores
            current_time = time.time()
            if current_time - last_message_time >= HEALTH_CHECK_TIMEOUT:
                last_message_time = current_time
                for message_type, count in self.message_counters.items():
                    if count == 0:
                        print(f"Advertencia: No se recibieron mensajes de tipo {message_type} en {HEALTH_CHECK_TIMEOUT} segundos.")
                        self.fall_monitors.add(message_type)
                        #Notidicar al monitor asignado que debe suplir al monitor caido
                        self.notify_supplier()
                    else:
                        print(f"Enviando mensaje al monitor para dejar de suplir {message_type}")
                        #Notificar al monitor que estaba supliendo que ya no debe hacerlo
                        self.fall_monitors.remove(message_type)
                        self.notify_supplier()
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