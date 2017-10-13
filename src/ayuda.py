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


def menu_ayuda():

    eleccion = ''

    while eleccion != '1' and eleccion != '2' and eleccion != '3' and eleccion != '4' and eleccion != '0':

        os.system('clear')

        print " AYUDA DE BOWERBIRD\n"
        print " 1. Ayuda Recortar Capturas"
        print " 2. Ayuda Identificar Capturas"
        print " 3. Ayuda Procesar Datos"
        print " 4. Sobre Bowerbird"
        print "\n 0. Salir"

        eleccion = raw_input(" >>  ")
        eleccion = eleccion.lower()
    
    if eleccion == '1':
        os.system('clear')
        print " AYUDA RECORTAR CAPTURAS\n"
        print ' Recorta las barajas de las capturas de pantalla'
        print ' que haya en la carpeta capturas_pendientes\n'
        raw_input(" Pulse enter para volver...")
        menu_ayuda()
    elif eleccion == '2':
        os.system('clear')
        print " AYUDA IDENTIFICAR CAPTURAS\n"
        print ' Identifica las cartas que hay en las barajas'
        print ' recortadas anteriormente y crea un archivo de texto'
        print ' que sirve como archivo de entrada para VOSviewer\n'
        raw_input(" Pulse enter para volver...")
        menu_ayuda()
    elif eleccion == '3':
        os.system('clear')
        print " AYUDA PROCESAR DATOS\n"
        print ' Procesa los datos de las capturas identificadas'
        print ' y muestra información como las 10 cartas más'
        print ' usadas y las 3 barajas más usadas\n'
        raw_input(" Pulse enter para volver...")
        menu_ayuda()
    elif eleccion == '4':
        os.system('clear')
        print " SOBRE BOWERBIRD\n"
        print ' BowerBird es un programa que permite obtener datos del'
        print ' uso de cartas y barajas de Clash Royale a partir de'
        print ' capturas de pantalla de TV Royale. También facilita'
        print ' la visualización de los datos con VOSViewer (www.vosviewer.com).\n'
        print ' Contacto: gferrergithub@gmail.com\n'
        raw_input(" Pulse enter para volver...")
        menu_ayuda()
    elif eleccion == '0':
        raise SystemExit

##############
menu_ayuda()
