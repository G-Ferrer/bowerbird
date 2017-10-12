#!/usr/bin/env python
# -*- coding: utf-8 -*-


#############################################################################
#
#    Copyright (C) 2017  Guillermo Ferrer López.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################


import os
import sys
import imghdr
from multiprocessing import Array, Lock, Pool, cpu_count
from PIL import Image

contador_exitos_errores = Array('i', 3)
lock = Lock()


def elegir_cantidad_cpus():
    # Función para pedir al usuario cuántas CPU's quiere utilizar.

    int_valido = False

    while int_valido == False:

        print('\n %s CPU\'s disponibles' % cpu_count())
        cpus = raw_input('\n ¿Cuántas utilizar? \n  >>  ')

        try:
            cpus = int(cpus)
            int_valido = True
        except ValueError:
            int_valido = False

        if (cpus > 0 and cpus <= cpu_count()):
            int_valido = True
        else:
            int_valido = False

        os.system('clear')
        print " RECORTAR\n"

    return cpus


def incluido(sublista, lista):
    # Devuelve True si 'sublista' está incluida dentro de 'lista'.
    # En caso contrario, devuelve 'False'.

    # a = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    # b = [(4, 5, 8), (1, 2, 3), (4, 5, 6), (7, 8, 9), (2, 6, 8)]
    # incluido(a, b) >> True

    sublista_str = ' '. join(str(x) for x in sublista)
    lista_str = ' '. join(str(x) for x in lista)

    for i in range(len(lista_str)-len(sublista_str)+1):
        if sublista_str == lista_str[i:i+len(sublista_str)]:
            return True
    return False


def crear_lista_reparto(num_total, num_div):
    div = num_total / num_div
    sobrantes = num_total - div * num_div
    lista_reparto = []
    for i in xrange(0, sobrantes*(div+1), div+1):
        lista_reparto.append([i, i+div+1])

    for i in xrange(sobrantes*(div+1), num_total, div):
        lista_reparto.append([i, i+div])

    return lista_reparto


def recortar_una_captura(ruta_captura, ruta_destino, ruta_principal, total):

    # Recorta y se encarga de manejar la captura que está en 'ruta_captura'.

    # lado_marco = 450*[(204, 204, 204)]
    lado_marco = 500*[(222, 235, 241)]  # De esta forma, también detecta las capturas tras la actualización.

    imagen = Image.open(ruta_captura)
    pixels_imagen = list(imagen.getdata())
    ancho_imagen = imagen.size[0]
    alto_imagen = imagen.size[1]

    if (ancho_imagen != 540 or alto_imagen != 960):
        # Considero como error que el tamaño de la imagen sea diferente al de las capturas (540x960)
        os.rename(ruta_captura, ruta_principal + '/files/errores/recortar/' + os.path.basename(os.path.normpath(ruta_captura)))

        lock.acquire()
        sys.stdout.write("\033[F")
        print " [%s %% Procesado]" % round((float(contador_exitos_errores[0])/total)*100, 1)
        lock.release()

        return 0

    else:

        filas_pixels_imagen = [pixels_imagen[i*ancho_imagen:i*ancho_imagen+ancho_imagen] for i in range(alto_imagen)]

        # Lista con las filas de imagen donde hay un lado horizontal de marco.
        posibles_posiciones_marco = []

        for i in range(215, 873):  # Como sé a partir de qué pixel pueden aparecer los marcos, agilizo empezando a bucar por el pixel 216 (posición 215).
            if incluido(lado_marco, filas_pixels_imagen[i]):
                posibles_posiciones_marco = posibles_posiciones_marco + [i]

        # Resto las posiciones donde hay marco horizontal, para deducir dónde realmente están situados los marcos.
        a = len(posibles_posiciones_marco)
        dif_posibles_posiciones_marco = [posibles_posiciones_marco[i+1]-posibles_posiciones_marco[i] for i in range(a-1)]

        # El formato de filas_marcos es [[fila_inicio_marco1, fila_fin_marco1], [fila_inicio_marco2, fila_fin_marco2].
        filas_marcos = []

        for i in range(len(dif_posibles_posiciones_marco)):
            if dif_posibles_posiciones_marco[i] > 240:  # Teóricamente debería ser 246, pero para tener un poco de margen, 240.
                filas_marcos.append([posibles_posiciones_marco[i], posibles_posiciones_marco[i+1]])

        # Considero como error que en una captura haya más o menos de 2 marcos (4 barajas).
        if len(filas_marcos) != 2:
            os.rename(ruta_captura, ruta_principal + '/files/errores/recortar/' + os.path.basename(os.path.normpath(ruta_captura)))

            lock.acquire()
            sys.stdout.write("\033[F")
            print " [%s %% Procesado]" % round((float(contador_exitos_errores[0])/total)*100, 1)
            lock.release()

            return 0
        else:
            for i in range(len(filas_marcos)):
                imagen.crop((25, filas_marcos[i][0] + 60, ancho_imagen / 2 - 5, filas_marcos[i][1] - 45)).save(ruta_destino + '/' + os.path.basename(os.path.normpath(ruta_captura)).rstrip('.png') + '[%s].png' % (2 * i + 1), 'PNG')
                imagen.crop((ancho_imagen / 2, filas_marcos[i][0] + 60, ancho_imagen - 30, filas_marcos[i][1] - 45)).save(ruta_destino + '/' + os.path.basename(os.path.normpath(ruta_captura)).rstrip('.png') + '[%s].png' % (2 * i + 2), 'PNG')

            os.rename(ruta_captura, ruta_principal + '/files/capturas_procesadas/' + os.path.basename(os.path.normpath(ruta_captura)))

            lock.acquire()   
            sys.stdout.write("\033[F")
            print " [%s %% Procesado]" % round((float(contador_exitos_errores[0])/total)*100, 1)        
            lock.release()

            return 1


def recortar_thread(primera_captura, ultima_captura, lista_capturas_png):

    ruta_principal = os.path.abspath(os.path.dirname(sys.argv[0]))

    if '/src' in ruta_principal:
        ruta_principal = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]

    ruta_destino = ruta_principal + '/files/capturas_recortadas'

    for i in range(primera_captura, ultima_captura):
        captura = lista_capturas_png[i]
        lock.acquire()
        contador_exitos_errores[0] = contador_exitos_errores[0] + 1
        lock.release()
        ruta_captura = ruta_principal + '/files/capturas_pendientes/' + captura

        if recortar_una_captura(ruta_captura, ruta_destino, ruta_principal, len(lista_capturas_png)) == 1:
            lock.acquire()
            contador_exitos_errores[1] = contador_exitos_errores[1] + 1
            lock.release()
        else:
            lock.acquire()
            contador_exitos_errores[2] = contador_exitos_errores[2] + 1
            lock.release()


def recortar_main():

    ruta_capturas_pendientes = os.path.abspath(os.path.dirname(sys.argv[0])).rsplit('/', 1)[0] + '/files/capturas_pendientes'

    lista_archivos = os.listdir(ruta_capturas_pendientes)

    # Las capturas son imágenes con formato .png
    lista_capturas_png = [i for i in lista_archivos if imghdr.what(ruta_capturas_pendientes + '/' + i) == 'png']
    lista_no_png = [i for i in lista_archivos if imghdr.what(ruta_capturas_pendientes + '/' + i) != 'png']

    # Muevo todos los archivos que no sean .png a /errores/no_png
    ruta_principal = os.path.abspath(os.path.dirname(sys.argv[0]))

    if '/src' in ruta_principal:
        ruta_principal = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]

    for i in lista_no_png:
        os.rename(ruta_capturas_pendientes + '/' + i, ruta_principal + '/files/errores/no_png/' + i)

    contador_exitos_errores[0] = 0
    contador_exitos_errores[1] = 0
    contador_exitos_errores[2] = 0

    if len(lista_capturas_png) != 0:

        cpus = elegir_cantidad_cpus()

        os.system('clear')
        print " RECORTAR\n\n\n"

        if cpus < len(lista_capturas_png):
            lista_reparto = crear_lista_reparto(len(lista_capturas_png), cpus)
        else:
            lista_reparto = crear_lista_reparto(len(lista_capturas_png), len(lista_capturas_png))

        if cpus >= len(lista_capturas_png):
            pool = Pool(processes=len(lista_capturas_png))
            for i in range(len(lista_capturas_png)):
                pool.apply_async(recortar_thread, [lista_reparto[i][0], lista_reparto[i][1], lista_capturas_png])
        else:
            pool = Pool(processes=cpus)
            for i in range(cpus):
                pool.apply_async(recortar_thread, [lista_reparto[i][0], lista_reparto[i][1], lista_capturas_png])

        pool.close()
        pool.join()

        exitos = int(contador_exitos_errores[1])
        errores = int(contador_exitos_errores[2])

        print('\n')
        print(' \x1b[2A\x1b[2K'*2)
        print(' [100.0 % Procesado]\n')
        print(' %s %s %s con éxito. %s %s.' % ('Recortada' if exitos == 1 else 'Recortadas', exitos, 'captura' if exitos == 1 else 'capturas', errores, 'error' if errores == 1 else 'errores'))

#################################################

# Si el programa es llamado directamente y no desde otro programa habiendo previamente sido importado.
if __name__ == "__main__":
    recortar_main()
