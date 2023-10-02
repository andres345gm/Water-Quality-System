# Water Quality System
## Proyecto de Sistemas Distribuidos

![Black And White Modern Vintage Retro Brand Logo (1)](https://github.com/andres345gm/Water-Quality-System/assets/103542486/42b3c692-d20f-4703-a11a-48931cbbc547)


### Descripción del Proyecto
El proyecto consta de varios programas diseñados para simular un sistema de monitoreo de sensores y un sistema de calidad. Los sensores generan datos simulados y los envían al sistema de calidad para su control. Los programas incluyen:

1. **QualitySystem.py:** Un sistema de calidad que recibe y controla los datos de los sensores.

2. **Monitor.py:** Monitorea un tipo específico de sensor y verifica si los datos están dentro de los límites adecuados.

3. **proxy.py:** Actúa como intermediario entre los sensores y el sistema de calidad para enrutar los mensajes correctamente.

4. **Sensor.py:** Simula un sensor que genera valores aleatorios para su monitoreo.

A continuación, se detallarán las librerías necesarias y las instrucciones de ejecución.

### Librerías Necesarias
Para ejecutar este proyecto, debe asegurarse de tener instaladas las siguientes librerías de Python. Puede instalarlas usando `pip` de la siguiente manera:

```bash
pip install zmq argparse
```

El programa además utiliza otras librerías, pero son STD, por lo tanto, no son indicadas en esta instancia.

### Instrucciones de Ejecución en Orden

El proyecto debe ejecutarse en el siguiente orden para que funcione correctamente debido a la interdependencia entre los programas:

1. **proxy.py:** El proxy actúa como intermediario entre los sensores y el sistema de calidad. Debe ejecutarse primero.

   ```bash
   python proxy.py
   ```

2. **QualitySystem.py:** El sistema de calidad debe estar en funcionamiento antes de que los monitores y los sensores comiencen a enviar datos.

   ```bash
   python QualitySystem.py
   ```

3. **Monitor.py:** Puede haber varios monitores, uno para cada tipo de sensor. Deben ejecutarse después del sistema de calidad.

   ```bash
   python Monitor.py -t [sensor_type]
   ```

   Sustituye `[sensor_type]` por el tipo de sensor que deseas monitorear, por ejemplo, "temperature," "PH," o "oxygen."

4. **Sensor.py:** Puede haber varios sensores, uno para cada tipo de sensor. Deben ejecutarse después del sistema de calidad.

   ```bash
   python Sensor.py -t [sensor_type] -c [config_file] -i [interval]
   ```

   - Sustituye `[sensor_type]` por el tipo de sensor que deseas simular.
   - Sustituye `[config_file]` por un archivo JSON de configuración que define las probabilidades de generación de valores.
   - Sustituye `[interval]` por el intervalo de tiempo en segundos para generar valores simulados.

### Por qué se Deben Ejecutar en ese Orden
El orden de ejecución es crucial para el funcionamiento del proyecto debido a la dependencia entre los componentes:

1. **proxy.py:** El proxy actúa como intermediario y debe estar en funcionamiento antes de que los otros componentes intenten conectarse a él.

2. **QualitySystem.py:** El sistema de calidad debe estar en funcionamiento antes de que los monitores y los sensores comiencen a enviar datos, ya que es responsable de recibir y controlar los datos.

3. **Monitor.py:** Los monitores dependen del sistema de calidad para recibir y verificar los datos. Deben ejecutarse después de que el sistema de calidad esté en funcionamiento.

4. **Sensor.py:** Los sensores generan datos simulados y los envían al sistema de calidad a través del proxy. Deben ejecutarse después de que el sistema de calidad y el proxy estén en funcionamiento.

Siguiendo este orden, aseguramos que todos los componentes estén en su lugar y listos para interactuar de manera efectiva.

# Authors 
[@Alejandro Uscátegui](https://github.com/Uscateguito)<br>
Fabito
Andrés
Luisa
