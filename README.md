# bowerbird
Permite obtener datos del uso de cartas y barajas de Clash Royale a partir de capturas de pantalla de TV Royale.

/////////////////////////////////////////////////

- Funciona correctamente en Ubuntu 16.04 LTS con python 2.7.12 y gcc (Ubuntu 5.4.0-6ubuntu1~16.04.4) 5.4.0 20160609

- Capturas hechas con un móvil Sony Xperia M2 D2303

/////////////////////////////////////////////////

- DEPENDENCIAS: PIL (instalar Pillow, ya que PIL com tal desapareció).

/////////////////////////////////////////////////

CÓMO USAR BOWERBIRD:

- Copiar las capturas que se quieran identificar en ~/src/capturas_pendientes

- Para ejecutar el programa, ejecutar en la consola: python ~/src/bowerbird_main.py o .~/run_bowerbird.sh

- Una vez en el programa, recortar las capturas.

- Cuando estén recortadas, identificarlas. El programa pedirá un nombre y dónde guardar el archivo donde se guardarán los datos.

- Para ver información sobre las capturas identificadas, seleccionar la opción de procesar datos. Se podrán ver así las 10 cartas más usadas y las 3 barajas más usadas.

/////////////////////////////////////////////////

Partes del código se han implementado gracias a respuestas en Stack Overflow.

- https://stackoverflow.com/questions/46242485/get-combinations-between-two-given-ones#comment79466235_46242485
- https://stackoverflow.com/users/2979617/m-oehm

- https://stackoverflow.com/a/43407858
- https://stackoverflow.com/users/6364089/yi-xiao

- https://stackoverflow.com/a/3536261
- https://stackoverflow.com/users/381345/casablanca

- https://stackoverflow.com/a/46308012
- https://stackoverflow.com/users/1106540/ismael-luceno

- https://stackoverflow.com/a/46398712
- https://stackoverflow.com/users/15168/jonathan-leffler
