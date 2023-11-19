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
        self.publisher.bind(f"tcp://{IP_ADDRESS_MONITOR}:{PORT_MONITOR_HEALTH_CHECK}")


        # Inicializa contadores para cada tipo de mensaje
        self.message_counters = {
            "temperature": 0,
            "PH": 0,
            "oxygen": 0
        }
        # Monitores caidos
        self.fall_monitors = set()
        self.all_monitors = set(["temperature", "PH", "oxygen"])
        self.supplier = None
        print("Health Check running...")

    def choose_supplier(self):
        if "temperature" not in self.fall_monitors:
            self.supplier = "temperature"
        elif "PH" not in self.fall_monitors:
            self.supplier = "PH"
        elif "oxygen" not in self.fall_monitors:
            self.supplier = "oxygen"

    def notify_supplier(self):
        #Verificar si aun no tenemos un monitor que supla a otros
        if self.supplier is None or self.supplier in self.fall_monitors:
            self.choose_supplier()

        if self.supplier is not None:
            print("El monitor que suplira a los monitores caidos es", self.supplier)
            print("Enviando mensaje al monitor para suplir a los monitores caidos")
            print("los monitores caidos son", self.fall_monitors)
            # Notificar al monitor que debe suplir o seguir supliendo a los monitores caidos
            self.publisher.send_multipart([self.supplier.encode(),
                                            str(self.fall_monitors).encode()])
        else:
            print("No hay monitores disponibles para suplir la operación")

        
    def receive(self):
        print("Control de salud en ejecución...")
        last_message_time = {monitor: time.time() for monitor in self.all_monitors}

        while True:
            message = self.subscriber.recv_string()
            print(message)
            # Actualiza el contador para el tipo de mensaje recibido
            message_type = message.split(":")[0].strip()
            if message_type in self.message_counters:
                self.message_counters[message_type] += 1
                # Actualiza el tiempo del último mensaje recibido para este tipo de monitor
                last_message_time[message_type] = time.time()

            # Verifica si han pasado 5 segundos y resetea los contadores
            current_time = time.time()
            for monitor, last_time in last_message_time.items():
                previous_monitors_fall = list(self.fall_monitors)
                if current_time - last_time >= HEALTH_CHECK_TIMEOUT:
                    print(f"Advertencia: No se recibieron mensajes de tipo {monitor} en {HEALTH_CHECK_TIMEOUT} segundos.")
                    self.fall_monitors.add(monitor)
                    # Notificar al monitor asignado que debe suplir al monitor caído
                elif monitor in self.message_counters and self.message_counters[monitor] > 0:
                    # Si se recibieron mensajes, quitar el monitor caído de la lista
                    if monitor in self.fall_monitors:
                        print(f"El monitor {monitor} ahora está activo.")
                        self.fall_monitors.remove(monitor)
                if previous_monitors_fall != list(self.fall_monitors):
                    print("Los monitores caidos han cambiado")
                    # Notificar al monitor asignado que debe suplir al monitor caído
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