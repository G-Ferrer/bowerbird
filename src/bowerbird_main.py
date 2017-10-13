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
import time
from subprocess import call
import recortar_capturas
import identificar_capturas
import procesar_datos
import visualizar_datos

ruta_principal = os.path.abspath(os.path.dirname(sys.argv[0]))

if '/src' in ruta_principal:
    ruta_principal = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]


def menu_principal():
    os.system('clear')

    print ' ======================='
    print '        BOWERBIRD'
    print ' =======================\n'
    print " 1. Recortar Capturas"
    print " 2. Identificar Cartas"
    print " 3. Procesar Datos"
    print " 4. Visualizar Datos con VOSViewer"

    if os.path.exists(ruta_principal + '/src/config.py'):
        print " 5. Configuración"
        if os.path.exists(ruta_principal + '/src/ayuda.py'):
            print " 6. Ayuda"
    else:
        if os.path.exists(ruta_principal + '/src/ayuda.py'):
            print " 5. Ayuda"

    print "\n 0. Salir"

    eleccion = raw_input(" >>  ")
    menu_ejecucion(eleccion)


def comprobacion_carpetas_y_archivos():
    # Comprueba que existan todos los archivos y carpetas necesarios para el funcionamiento del programa.
    # En el caso de que no existieran, y pudieran ser reemplazados, los crea.

    os.system('clear')

    if not os.path.exists(ruta_principal + '/files'):
        os.makedirs(ruta_principal + '/files')
    if not os.path.exists(ruta_principal + '/files/capturas_pendientes'):
        os.makedirs(ruta_principal + '/files/capturas_pendientes')
    if not os.path.exists(ruta_principal + '/files/capturas_recortadas'):
        os.makedirs(ruta_principal + '/files/capturas_recortadas')
    if not os.path.exists(ruta_principal + '/files/errores'):
        os.makedirs(ruta_principal + '/files/errores')
    if not os.path.exists(ruta_principal + '/files/resultados_procesado_datos'):
        os.makedirs(ruta_principal + '/files/resultados_procesado_datos')
    if not os.path.exists(ruta_principal + '/files/errores/identificar'):
        os.makedirs(ruta_principal + '/files/errores/identificar')
    if not os.path.exists(ruta_principal + '/files/errores/no_png'):
        os.makedirs(ruta_principal + '/files/errores/no_png')
    if not os.path.exists(ruta_principal + '/files/errores/recortar'):
        os.makedirs(ruta_principal + '/files/errores/recortar')
    if not os.path.exists(ruta_principal + '/files/tmp'):
        os.makedirs(ruta_principal + '/files/tmp')
        os.makedirs(ruta_principal + '/files/tmp/cartas')
        os.makedirs(ruta_principal + '/files/tmp/identificar')
    if not os.path.exists(ruta_principal + '/files/tmp/cartas'):
        os.makedirs(ruta_principal + '/files/tmp/cartas')
    if not os.path.exists(ruta_principal + '/files/tmp/identificar'):
        os.makedirs(ruta_principal + '/files/tmp/identificar')
    if not os.path.exists(ruta_principal + '/files/tmp/procesar'):
        os.makedirs(ruta_principal + '/files/tmp/procesar')
    if not os.path.exists(ruta_principal + '/src/ayuda.py'):
        print ' No se encuentra %s/src/ayuda.py\n' % ruta_principal
        time.sleep(3)
    if not os.path.exists(ruta_principal + '/src'):
        print ' No se encuentra %s/src\n' % ruta_principal
        raw_input(" Pulse enter para salir...")
        raise SystemExit
    if not os.path.exists(ruta_principal + '/src/recortar_capturas.py'):
        print ' No se encuentra %s/src/recortar_capturas.py\n' % ruta_principal
        raw_input(" Pulse enter para salir...")
        raise SystemExit
    if not os.path.exists(ruta_principal + '/src/identificar_capturas.py'):
        print ' No se encuentra %s/src/identificar_capturas.py\n' % ruta_principal
        raw_input(" Pulse enter para salir...")
        raise SystemExit
    if not os.path.exists(ruta_principal + '/src/procesar_datos.py'):
        print ' No se encuentra %s/src/procesar_datos.py\n' % ruta_principal
        raw_input(" Pulse enter para salir...")
        raise SystemExit
    if not os.path.exists(ruta_principal + '/src/visualizar_datos.py'):
        print ' No se encuentra %s/src/visualizar_datos.py\n' % ruta_principal
        raw_input(" Pulse enter para salir...")
        raise SystemExit
    if not os.path.exists(ruta_principal + '/src/imprimir_lista_cartas.py'):
        print ' No se encuentra %s/src/imprimir_lista_cartas.py\n' % ruta_principal
        raw_input(" Pulse enter para salir...")
        raise SystemExit
    if not os.path.exists(ruta_principal + '/src/fuerza_bruta_thread.c'):
        print ' No se encuentra %s/src/fuerza_bruta_thread.c\n' % ruta_principal
        raw_input(" Pulse enter para salir...")
        raise SystemExit
    if not os.path.exists(ruta_principal + '/src/fuerza_bruta_thread'):
        print ' No se encuentra %s/src/fuerza_bruta_thread\n' % ruta_principal
        print ' Compilar con gcc fuerza_bruta_thread.c -o fuerza_bruta_thread\n'
        raw_input(" Pulse enter para salir...")
        raise SystemExit


def menu_ejecucion(eleccion):
    os.system('clear')

    eleccion = eleccion.lower()

    try:
        acciones_menu_principal[eleccion]()
    except KeyError:
        menu_principal()


def recortar():
    print " RECORTAR\n"

    recortar_capturas.recortar_main()

    raw_input(" Pulse enter para volver...")
    menu_ejecucion('9')


def identificar():
    print " IDENTIFICAR\n"

    identificar_capturas.identificar_main()

    raw_input(" Pulse enter para volver...")
    menu_ejecucion('9')


def procesar():
    print " PROCESAR DATOS\n"

    procesar_datos.procesar_main()

    raw_input(" Pulse enter para volver...")
    menu_ejecucion('9')


def configuracion():
    print " CONFIGURACIÓN\n"

    print " En construcción..."

    raw_input(" Pulse enter para volver...")
    menu_ejecucion('9')


def ayuda():
    comando_ayuda = 'python \"%s\"' % (ruta_principal + '/src/ayuda.py')
    call(['gnome-terminal', '-e', comando_ayuda])

    menu_ejecucion('9')


def visualizar():
    print " VISUALIZAR DATOS CON VOSVIEWER\n"

    visualizar_datos.visualizar_main()

    raw_input(" Pulse enter para volver...")
    menu_ejecucion('9')


def atras():
    menu_principal()
 

def salir():
    raise SystemExit


acciones_menu_principal = {
    'menu_principal': menu_principal,
    '1': recortar,
    '2': identificar,
    '3': procesar,
    '4': visualizar,
    '9': atras,
    '0': salir,
}

# =======================
#    PROGRAMA PINCIPAL
# =======================

if __name__ == "__main__":
    comprobacion_carpetas_y_archivos()

    if os.path.exists(ruta_principal + '/src/config.py'):
        acciones_menu_principal['5'] = configuracion
        if os.path.exists(ruta_principal + '/src/ayuda.py'):
            acciones_menu_principal['6'] = ayuda
    else:
        if os.path.exists(ruta_principal + '/src/ayuda.py'):
            acciones_menu_principal['5'] = ayuda

    menu_principal()
