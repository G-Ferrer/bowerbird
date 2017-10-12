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

ruta_principal = os.path.abspath(os.path.dirname(sys.argv[0]))

if '/src' in ruta_principal:
        ruta_principal = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]

# Lista de las cartas (la modifico para que cartas que puedan tener dos versiones, aparezcan sólo una vez en la lista).
# También le doy formato a los elementos de la lista (les quito las barras)

lista_cartas = os.listdir(ruta_principal + '/files/cartas_modelo')

# Busco las cartas de verdugo_1 y verdugo_2, borro una y la otra la sustituyo por verdugo sólo
if 'verdugo_1' in lista_cartas:
    lista_cartas[lista_cartas.index('verdugo_1')] = 'verdugo'

if 'verdugo_2' in lista_cartas:
    del lista_cartas[lista_cartas.index('verdugo_2')]

# Sustituyo las barras bajas por espacios
for i in range(len(lista_cartas)):
    lista_cartas[i] = lista_cartas[i].replace('_', ' ')


def imprimir_lista_cartas():

    print " LISTA DE CARTAS\n"

    for x, y in enumerate(lista_cartas):
        print " %s >> %s" % (x, y)

    print '\n'
    raw_input(" Pulse enter para salir...")
    raise SystemExit

imprimir_lista_cartas()
