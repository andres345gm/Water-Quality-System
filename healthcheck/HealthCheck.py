import zmq
import time

IP_ADDRESS_MONITOR = "127.0.0.1"
PORT_MONITOR = "8888"  # Puerto utilizado para los controles de salud

IP_ADDRESS_MONITOR_HEALTH_CHECK = "127.0.0.1"
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
            print("No hay un monitor asignado para suplir a los monitores caidos")
            if "temperature" not in self.fall_monitors:
                self.supplier = "temperature"
            elif "Ph" not in self.fall_monitors:
                self.supplier = "Ph"
            elif "oxygen" not in self.fall_monitors:
                self.supplier = "oxygen"
            #Verificar que haya un monitor disponible para suplir
            print("Eligiendo el monitor para suplir los monitores caidos")
            if self.supplier is not None:
                print("El monitor asignado para suplir es: ", self.supplier)
                print("Enviando mensaje al monitor para suplir a los monitores caidos")
                print("los monitores caidos son", self.fall_monitors)
                self.publisher.send_multipart([self.supplier.encode(),
                                                str(self.fall_monitors).encode()])
            else:
                print("No hay monitores disponibles para poder suplir la operación")
        else:
            print("El monitor asignado para suplir es: ", self.supplier)
            # Verificar si el monitor que estaba supliendo ya no está caido
            if self.supplier in self.fall_monitors:
                print("El monitor asignado se cayó, debemos elegir un nuevo monitor")
                self.supplier = None
                self.notify_supplier()
            else:
                print("Enviando mensaje al monitor para suplir a los monitores caidos")
                print("los monitores caidos son", self.fall_monitors)
                # Notificar al monitor que debe suplir o seguir supliendo a los monitores caidos
                self.publisher.send_multipart([self.supplier.encode(),
                                                str(self.fall_monitors).encode()])

        
    def receive(self):
        print("Control de salud en ejecución...")
        last_message_time = {monitor: time.time() for monitor in self.all_monitors}

        while True:
            message = self.subscriber.recv_string()
            print("el mensaje es ", message)
            # Actualiza el contador para el tipo de mensaje recibido
            message_type = message.split(":")[0].strip()
            if message_type in self.message_counters:
                self.message_counters[message_type] += 1
                # Actualiza el tiempo del último mensaje recibido para este tipo de monitor
                last_message_time[message_type] = time.time()

            # Verifica si han pasado 5 segundos y resetea los contadores
            current_time = time.time()
            for monitor, last_time in last_message_time.items():
                if current_time - last_time >= HEALTH_CHECK_TIMEOUT:
                    print(f"Advertencia: No se recibieron mensajes de tipo {monitor} en {HEALTH_CHECK_TIMEOUT} segundos.")
                    print("los monitores caidos son", self.fall_monitors)
                    self.fall_monitors.add(monitor)
                    print("los monitores caidos son", self.fall_monitors)
                    # Notificar al monitor asignado que debe suplir al monitor caído
                    self.notify_supplier()
                else:
                    '''monitor in self.message_counters and self.message_counters[monitor] > 0'''
                    # Si se recibieron mensajes, quitar el monitor caído de la lista
                    if monitor in self.fall_monitors:
                        print(f"Enviando mensaje al monitor para dejar de suplir {monitor}")
                        self.fall_monitors.remove(monitor)
                        self.notify_supplier()



def main():
    health_check = HealthCheck()
    try:
        health_check.receive()
    except KeyboardInterrupt:
        health_check.subscriber.close()
        health_check.context.term()

if __name__ == "__main__":
    main()