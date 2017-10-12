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
from operator import itemgetter
from PIL import Image, ImageFont, ImageDraw
from multiprocessing import Lock, Array, Pool, cpu_count
from Tkinter import Tk
from tkFileDialog import asksaveasfilename

# NOTA: 
# Para ejecutar este programa en algunos ordenadores, hace falta añadir las dos siguientes lineas:

# reload(sys)
# sys.setdefaultcoding('utf8')

#################################################


contador_exitos_errores = Array('i', 1)
lock = Lock()

ruta_principal = os.path.abspath(os.path.dirname(sys.argv[0]))

if '/src' in ruta_principal:
    ruta_principal = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]


ruta_cartas_modelo = ruta_principal + '/files/cartas_modelo'

lista_cartas_modelo = os.listdir(ruta_cartas_modelo)


#################################################


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
        print " IDENTIFICAR\n"

    return cpus


def mitad_izquierda(pixels_imagen, ancho_imagen, alto_imagen):

    pixels_imagen_izquierda = []

    for i in range(alto_imagen):
        pixels_imagen_izquierda.append(pixels_imagen[i*ancho_imagen:i*ancho_imagen+(ancho_imagen/2)])

    pixels_imagen_izquierda = [i for j in pixels_imagen_izquierda for i in j]

    return pixels_imagen_izquierda


def mitad_derecha(pixels_imagen, ancho_imagen, alto_imagen):

    pixels_imagen_derecha = []

    for i in range(alto_imagen):
        pixels_imagen_derecha.append(pixels_imagen[(i*ancho_imagen)+(ancho_imagen/2):(i*ancho_imagen)+(ancho_imagen/2)+(ancho_imagen-ancho_imagen/2)])

    pixels_imagen_derecha = [i for j in pixels_imagen_derecha for i in j]

    return pixels_imagen_derecha


def mitad_superior(pixels_imagen, ancho_imagen, alto_imagen):

    pixels_imagen_superior = []

    pixels_imagen_superior.append(pixels_imagen[0:ancho_imagen*(alto_imagen/2)])

    pixels_imagen_superior = [i for j in pixels_imagen_superior for i in j]

    return pixels_imagen_superior


def mitad_inferior(pixels_imagen, ancho_imagen, alto_imagen):

    pixels_imagen_inferior = []

    pixels_imagen_inferior.append(pixels_imagen[ancho_imagen*(alto_imagen-alto_imagen/2):])

    pixels_imagen_inferior = [i for j in pixels_imagen_inferior for i in j]

    return pixels_imagen_inferior


def adjuntar_medias_imagen(lista_cartas, pixels_imagen, nombre_carta):

    media_R = 0
    media_G = 0
    media_B = 0

    for i in range(len(pixels_imagen)):
        media_R = media_R + pixels_imagen[i][0]
        media_G = media_G + pixels_imagen[i][1]
        media_B = media_B + pixels_imagen[i][2]

    media_R = media_R / len(pixels_imagen)
    media_G = media_G / len(pixels_imagen)
    media_B = media_B / len(pixels_imagen)

    lista_cartas.append([media_R, media_G, media_B, nombre_carta])


def escribir_archivo_VOSviewer(nombre_archivo, lista):

    f = open(nombre_archivo, 'a')

    for i in lista:
        f.write('AU  - %s\n' % i)

    f.write('ER  -\n\n')
    f.close()


def agrupar_archivos_VOSviewer(nombre_archivo_VOSviewer):

    archivos = os.listdir(ruta_principal + '/files/tmp/identificar')
    archivos_txt = sorted([i for i in archivos if i.endswith('.txt')])

    with open(nombre_archivo_VOSviewer, 'w') as archivo_VOSviewer:
        for nombre_archivo in archivos_txt:
            with open(ruta_principal + '/files/tmp/identificar' + '/' + nombre_archivo) as archivo_entrada:
                for linea in archivo_entrada:
                    archivo_VOSviewer.write(linea)

    archivo_VOSviewer.close()

    # Arreglo los nombres para que salgan mejor en VOSviewer
    f1 = open(nombre_archivo_VOSviewer, 'r')
    f2 = open(nombre_archivo_VOSviewer + '.tmp', 'w')
    for linea in f1:
        nueva_linea = linea.replace('verdugo_1', 'verdugo').replace('verdugo_2', 'verdugo').replace('_', ' ')
        f2.write(nueva_linea)
    f1.close()
    f2.close()

    os.remove(nombre_archivo_VOSviewer)
    os.rename(nombre_archivo_VOSviewer + '.tmp', nombre_archivo_VOSviewer)


def borrar_archivos_VOSviewer_tmp():

    for i in os.listdir(ruta_principal + '/files/tmp/identificar'):

        os.remove(ruta_principal + '/files/tmp/identificar' + '/' + i)


def crear_lista_reparto(num_total, num_div):

    div = num_total / num_div
    sobrantes = num_total - div * num_div
    lista_reparto = []
    for i in xrange(0, sobrantes*(div+1), div+1):
        lista_reparto.append([i, i+div+1])

    for i in xrange(sobrantes*(div+1), num_total, div):
        lista_reparto.append([i, i+div])

    return lista_reparto


def repartir_cartas(lista_reparto, lista_barajas):

    lista_barajas_repartidas = []
    
    for i in range(len(lista_reparto)):

        lista_barajas_repartidas.append(lista_barajas[lista_reparto[i][0]: lista_reparto[i][1]])

    return lista_barajas_repartidas


def identificar_carta(carta):

    ruta_barajas = ruta_principal + '/files/tmp/cartas'

    datos_comparaciones = []

    cartas_identificar_mitad_izq = []
    cartas_identificar_mitad_dcha = []
    cartas_identificar_mitad_sup = []
    cartas_identificar_mitad_inf = []

    imagen = Image.open(ruta_barajas + '/' + carta)
    pixels_imagen = list(imagen.getdata())

    ancho_imagen = imagen.size[0]
    alto_imagen = imagen.size[1]

    izq_tmp = mitad_izquierda(pixels_imagen, ancho_imagen, alto_imagen)
    dcha_tmp = mitad_derecha(pixels_imagen, ancho_imagen, alto_imagen)
    sup_tmp = mitad_superior(pixels_imagen, ancho_imagen, alto_imagen)
    inf_tmp = mitad_inferior(pixels_imagen, ancho_imagen, alto_imagen)

    adjuntar_medias_imagen(cartas_identificar_mitad_izq, izq_tmp, carta)
    adjuntar_medias_imagen(cartas_identificar_mitad_dcha, dcha_tmp, carta)
    adjuntar_medias_imagen(cartas_identificar_mitad_sup, sup_tmp, carta)
    adjuntar_medias_imagen(cartas_identificar_mitad_inf, inf_tmp, carta)

    # Calculo la diferencia entre los valores medios de los modelos y la carta a identificar
    # me quedo con la que tenga los valores menores

    for x in range(len(cartas_modelo_mitad_izq)):

        a = cartas_identificar_mitad_izq[0][0]-cartas_modelo_mitad_izq[x][0]
        b = cartas_identificar_mitad_izq[0][1]-cartas_modelo_mitad_izq[x][1]
        c = cartas_identificar_mitad_izq[0][2]-cartas_modelo_mitad_izq[x][2]

        d = cartas_identificar_mitad_dcha[0][0]-cartas_modelo_mitad_dcha[x][0]
        e = cartas_identificar_mitad_dcha[0][1]-cartas_modelo_mitad_dcha[x][1]
        f = cartas_identificar_mitad_dcha[0][2]-cartas_modelo_mitad_dcha[x][2]

        g = cartas_identificar_mitad_sup[0][0]-cartas_modelo_mitad_sup[x][0]
        h = cartas_identificar_mitad_sup[0][1]-cartas_modelo_mitad_sup[x][1]
        ii = cartas_identificar_mitad_sup[0][2]-cartas_modelo_mitad_sup[x][2]

        j = cartas_identificar_mitad_inf[0][0]-cartas_modelo_mitad_inf[x][0]
        k = cartas_identificar_mitad_inf[0][1]-cartas_modelo_mitad_inf[x][1]
        l = cartas_identificar_mitad_inf[0][2]-cartas_modelo_mitad_inf[x][2]

        # Cuanto menor sea el error, más se parecen las imágenes entre sí

        error = (a**2 + b**2 + c**2)**0.5+(d**2 + e**2 + f**2)**0.5+(g**2 + h**2 + ii**2)**0.5+(j**2 + k**2 + l**2)**0.5

        datos_comparaciones.append([error, cartas_modelo_mitad_izq[x][3]])

    datos_comparaciones = sorted(datos_comparaciones, key=itemgetter(0))

    return datos_comparaciones[0][1]


def borrar_cartas_baraja(lista_cartas):

    for carta in lista_cartas:

        os.remove(ruta_principal + '/files/tmp/cartas/' + carta)


def recortar_cartas_baraja(baraja):

    ruta_baraja = ruta_principal + '/files/capturas_recortadas/' + baraja
    ruta_cartas_recortadas = ruta_principal + '/files/tmp/cartas'

    lista_cartas = []
    baraja_imagen = Image.open(ruta_baraja)

    baraja_imagen.crop((13, 24, 50, 53)).save(ruta_cartas_recortadas + '/' + baraja.rstrip('.png') + '[1].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[1].png')
    baraja_imagen.crop((71, 24, 108, 53)).save(ruta_cartas_recortadas + '/' + baraja.rstrip('.png') + '[2].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[2].png')
    baraja_imagen.crop((129, 24, 166, 53)).save(ruta_cartas_recortadas + '/' + baraja.rstrip('.png') + '[3].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[3].png')
    baraja_imagen.crop((187, 24, 224, 53)).save(ruta_cartas_recortadas + '/' + baraja.rstrip('.png') + '[4].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[4].png')

    baraja_imagen.crop((13, 92, 50, 121)).save(ruta_cartas_recortadas + '/' + baraja.rstrip('.png') + '[5].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[5].png')
    baraja_imagen.crop((71, 92, 108, 121)).save(ruta_cartas_recortadas + '/' + baraja.rstrip('.png') + '[6].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[6].png')
    baraja_imagen.crop((129, 92, 166, 121)).save(ruta_cartas_recortadas + '/'+baraja.rstrip('.png') + '[7].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[7].png')
    baraja_imagen.crop((187, 92, 224, 121)).save(ruta_cartas_recortadas + '/'+baraja.rstrip('.png') + '[8].png', 'PNG')
    lista_cartas.append(baraja.rstrip('.png') + '[8].png')

    return lista_cartas


def identificar_thread(lista_barajas, nombre_archivo_VOSviewer_tmp):
    
    for baraja in lista_barajas:

        lista_cartas = recortar_cartas_baraja(baraja)
        lista_cartas_identificadas = []
        ruta_baraja = ruta_principal + '/files/capturas_recortadas/' + baraja

        for carta in lista_cartas:

            lista_cartas_identificadas.append(identificar_carta(carta))

        if len(lista_cartas_identificadas) == 8:

            img = Image.open(ruta_baraja)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("fonts-japanese-gothic.ttf", 12)
            draw.text((12, 0), lista_cartas_identificadas[0], (0, 0, 0), font=font)
            draw.text((65, 0), lista_cartas_identificadas[1], (0, 0, 0), font=font)
            draw.text((118, 0), lista_cartas_identificadas[2], (0, 0, 0), font=font)
            draw.text((190, 0), lista_cartas_identificadas[3], (0, 0, 0), font=font)

            draw.text((12, 68), lista_cartas_identificadas[4], (0, 0, 0), font=font)
            draw.text((65, 68), lista_cartas_identificadas[5], (0, 0, 0), font=font)
            draw.text((118, 68), lista_cartas_identificadas[6], (0, 0, 0), font=font)
            draw.text((190, 68), lista_cartas_identificadas[7], (0, 0, 0), font=font)
            img.save(ruta_baraja)

            escribir_archivo_VOSviewer(nombre_archivo_VOSviewer_tmp, lista_cartas_identificadas)

            lock.acquire()
            contador_exitos_errores[0] = contador_exitos_errores[0] + 1
            sys.stdout.write("\033[F")
            print " [%s %% Procesado]" % round((float(contador_exitos_errores[0])/len(os.listdir(ruta_principal + '/files/capturas_recortadas/')))*100, 1)            
            lock.release()

        else: 

            print ' Error en la identificación de las cartas en %s' % baraja

        borrar_cartas_baraja(lista_cartas)


def identificar_main():

    # Para no mostrar la ventana de Tk
    Tk().withdraw()

    nombre_archivo_VOSviewer = asksaveasfilename(defaultextension='.txt')

    if nombre_archivo_VOSviewer == () or nombre_archivo_VOSviewer == '':
        raise SystemExit

    # Voy a aislar las cartas de cada una de las barajas que he recortado con recortar_capturas.py
    ruta_barajas = ruta_principal + '/files/capturas_recortadas'
    lista_barajas = os.listdir(ruta_barajas)

    # Las barajas son imágenes con formato .png
    lista_todas_barajas_png = [i for i in lista_barajas if imghdr.what(ruta_barajas + '/' + i) == 'png']
    lista_no_png = [i for i in lista_barajas if imghdr.what(ruta_barajas + '/' + i) != 'png']

    # Muevo todos los archivos que no sean .png a /errores/no_png
    for i in lista_no_png:
        os.rename(ruta_barajas + '/' + i, ruta_principal + '/files/errores/no_png/' + i)

    if len(lista_todas_barajas_png) != 0:

        # Número de CPU's que voy a usar
        cpus = elegir_cantidad_cpus()

        os.system('clear')
        print " IDENTIFICAR\n\n\n"

        if cpus < len(lista_todas_barajas_png):
            # Lista estilo [['carta_1', 'carta_2'], ['carta_3', 'carta_4'], ... ]
            lista_barajas_repartidas = repartir_cartas(crear_lista_reparto(len(lista_todas_barajas_png), cpus), lista_todas_barajas_png)
        else:
            # Lista estilo [['carta_1', 'carta_2'], ['carta_3', 'carta_4'], ... ]
            lista_barajas_repartidas = repartir_cartas(crear_lista_reparto(len(lista_todas_barajas_png), len(lista_todas_barajas_png)), lista_todas_barajas_png)

        if cpus >= len(lista_barajas_repartidas):
            pool = Pool(processes=len(lista_barajas_repartidas))
            for i in range(len(lista_barajas_repartidas)):
                pool.apply_async(identificar_thread, [lista_barajas_repartidas[i], ruta_principal + '/files/tmp/identificar/' + nombre_archivo_VOSviewer.rsplit('/', 1)[1].rstrip('.txt') + str(i) + '.txt'])
        else:
            pool = Pool(processes=cpus)
            for i in range(cpus):
                pool.apply_async(identificar_thread, [lista_barajas_repartidas[i], ruta_principal + '/files/tmp/identificar/' + nombre_archivo_VOSviewer.rsplit('/', 1)[1].rstrip('.txt') + str(i) + '.txt'])

        pool.close()
        pool.join()

        lock.acquire()
        contador_exitos_errores[0] = 0
        lock.release()

        print '\n Identificadas %s cartas.' % (8*len(os.listdir(ruta_principal + '/files/capturas_recortadas/')))

        agrupar_archivos_VOSviewer(nombre_archivo_VOSviewer)
        borrar_archivos_VOSviewer_tmp()
        

#################################################


# Calculo los valores medios de todas la cartas que tengo como referencia  

cartas_modelo_mitad_izq = []
cartas_modelo_mitad_dcha = []
cartas_modelo_mitad_sup = []
cartas_modelo_mitad_inf = []

for i in lista_cartas_modelo:

    imagen = Image.open(ruta_cartas_modelo + '/' + i)
    pixels_imagen = list(imagen.getdata())

    ancho_imagen = imagen.size[0]
    alto_imagen = imagen.size[1]

    izq_tmp = mitad_izquierda(pixels_imagen, ancho_imagen, alto_imagen)
    dcha_tmp = mitad_derecha(pixels_imagen, ancho_imagen, alto_imagen)
    sup_tmp = mitad_superior(pixels_imagen, ancho_imagen, alto_imagen)
    inf_tmp = mitad_inferior(pixels_imagen, ancho_imagen, alto_imagen)

    adjuntar_medias_imagen(cartas_modelo_mitad_izq, izq_tmp, i)
    adjuntar_medias_imagen(cartas_modelo_mitad_dcha, dcha_tmp, i)
    adjuntar_medias_imagen(cartas_modelo_mitad_sup, sup_tmp, i)
    adjuntar_medias_imagen(cartas_modelo_mitad_inf, inf_tmp, i)


# Si el programa es llamado directamente y no desde otro programa habiendo previamente sido importado.
if __name__ == "__main__":  

    identificar_main()