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
import shutil
import time
from math import factorial
from itertools import combinations, islice
from Tkinter import Tk
from tkFileDialog import askopenfilename
from multiprocessing import Lock, Pool, cpu_count
from subprocess import call


#################################################

lock = Lock()

ruta_principal = os.path.abspath(os.path.dirname(sys.argv[0]))

if '/src' in ruta_principal:
        ruta_principal = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]

num_cartas_por_baraja = 8

#################################################

# Coloco estas variables aquí en vez de dentro de una función para simplificar el paso de las mismas entre funciones.

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

#################################################

def matriz_2D_a_1D(matriz):
    yield len(matriz)
    cols = max(len(i) for i in matriz)
    yield cols
    for i in matriz:
        for j in i:
            yield j
        for j in range(0, cols - len(i)):
            yield 0


def menu_procesado_datos():
    os.system('clear')
    print " PROCESAR DATOS\n\n"

    print " 1. Top 10 cartas"
    print " 2. Mejor baraja (fuerza bruta)"
    print " 3. Lista de cartas"
    print "\n 0. Salir"

    eleccion = raw_input(" >>  ")
    menu_ejecucion_procesado(eleccion)


def menu_ejecucion_procesado(eleccion):
    os.system('clear')

    eleccion = eleccion.lower()

    try:
        acciones_menu_procesado[eleccion]()
    except KeyError:
        menu_procesado_datos()


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


def crear_lista_reparto(num_total, num_div):

    div = num_total / num_div
    sobrantes = num_total - div * num_div
    lista_reparto = []
    for i in xrange(0, sobrantes*(div+1), div+1):
        lista_reparto.append([i, i+div+1])

    for i in xrange(sobrantes*(div+1), num_total, div):
        lista_reparto.append([i, i+div])

    return lista_reparto


def borrar_archivos_tmp():

    os.remove(ruta_principal + '/files/tmp/tmp.txt')


def borrar_archivos_procesado_tmp():

    for i in os.listdir(ruta_principal + '/files/tmp/procesar'):

        os.remove(ruta_principal + '/files/tmp/procesar' + '/' + i)


def salir():
    
    borrar_archivos_tmp()
    raise SystemExit


def hacer_matriz_simetrica(matriz):

    matriz_traspuesta = map(list, zip(*matriz))

    matriz_simetrica = []

    for i in zip(matriz, matriz_traspuesta):
        matriz_simetrica.append([sum(x) for x in zip(i[0], i[1])])

    return matriz_simetrica


def top_10():

    # Calcula las 10 cartas más usadas.
    # Si varias cartas se usan la misma cantidad de veces, las mete dentro de la misma posición.

    # Lista con el número de veces que se repite cada carta
    lista_conteo = [0] * len(lista_cartas)

    # Cuento el número de veces que aparece cada carta
    archivo_2 = open(ruta_principal + '/files/tmp/tmp.txt')

    for i in archivo_2:
        pos = lista_cartas.index(i.rstrip())
        lista_conteo[pos] = lista_conteo[pos] + 1

    archivo_2.close()

    lista_conteo_ordenado = []

    for i in range(len(lista_cartas)):
        lista_conteo_ordenado.append([lista_cartas[i], lista_conteo[i]])

    # Ordeno de mayor a menor número de coincidencias
    lista_conteo_ordenado.sort(key=lambda x: x[1])
    lista_conteo_ordenado = list(reversed(lista_conteo_ordenado))

    # Imprimo las 10 cartas más usadas. En el caso de que algunas de las cartas se usen la misma cantidad de veces,
    # las muestro dentro del mismo puesto

    num_total_barajas = 0

    for nombre, cant in lista_conteo_ordenado:
        num_total_barajas = num_total_barajas + cant

    num_total_barajas = float(num_total_barajas)/num_cartas_por_baraja

    print '\n'
    print ' TOP 10 CARTAS'
    print '\n'
    print ' %s >> %s  (%s %%)' % (lista_conteo_ordenado[0][0], lista_conteo_ordenado[0][1], round((lista_conteo_ordenado[0][1]/num_total_barajas)*100,1))
    cuenta_top_10_cartas = 1

    for i in range(1, len(lista_conteo_ordenado)):

        if lista_conteo_ordenado[i][1] < lista_conteo_ordenado[i-1][1] and cuenta_top_10_cartas < 10:
            print '\n'
            print ' %s >> %s  (%s %%)' % (lista_conteo_ordenado[i][0], lista_conteo_ordenado[i][1], round((lista_conteo_ordenado[i][1]/num_total_barajas)*100,1))
            cuenta_top_10_cartas = cuenta_top_10_cartas + 1

        elif lista_conteo_ordenado[i][1] == lista_conteo_ordenado[i-1][1] and cuenta_top_10_cartas < 10:
                print ' %s >> %s  (%s %%)' % (lista_conteo_ordenado[i][0], lista_conteo_ordenado[i][1], round((lista_conteo_ordenado[i][1]/num_total_barajas)*100,1))

    print '\n'


def top_10_a_archivo(ruta_guardar_archivo):

    # Calcula las 10 cartas más usadas.
    # Si varias cartas se usan la misma cantidad de veces, las mete dentro de la misma posición.

    # Lista con el número de veces que se repite cada carta
    lista_conteo = [0] * len(lista_cartas)

    # Cuento el número de veces que aparece cada carta
    archivo_2 = open(ruta_principal + '/files/tmp/tmp.txt')

    for i in archivo_2:
        pos = lista_cartas.index(i.rstrip())
        lista_conteo[pos] = lista_conteo[pos] + 1

    archivo_2.close()

    lista_conteo_ordenado = []

    for i in range(len(lista_cartas)):
        lista_conteo_ordenado.append([lista_cartas[i], lista_conteo[i]])

    # Ordeno de mayor a menor número de coincidencias
    lista_conteo_ordenado.sort(key=lambda x: x[1])
    lista_conteo_ordenado = list(reversed(lista_conteo_ordenado))

    # Imprimo las 10 cartas más usadas. En el caso de que algunas de las cartas se usen la misma cantidad de veces,
    # las muestro dentro del mismo puesto

    num_total_barajas = 0

    for nombre, cant in lista_conteo_ordenado:
        num_total_barajas = num_total_barajas + cant

    num_total_barajas = float(num_total_barajas)/num_cartas_por_baraja    

    with open(ruta_guardar_archivo, "w+") as archivo:

        archivo.write('\n')
        archivo.write(' TOP 10 CARTAS')
        archivo.write('\n\n')
        archivo.write(' %s >> %s  (%s %%)' % (lista_conteo_ordenado[0][0], lista_conteo_ordenado[0][1], round((lista_conteo_ordenado[0][1]/num_total_barajas)*100,1)))
        cuenta_top_10_cartas = 1

        for i in range(1, len(lista_conteo_ordenado)):

            if lista_conteo_ordenado[i][1] < lista_conteo_ordenado[i-1][1] and cuenta_top_10_cartas < 10:
                archivo.write('\n\n')
                archivo.write(' %s >> %s  (%s %%)' % (lista_conteo_ordenado[i][0], lista_conteo_ordenado[i][1], round((lista_conteo_ordenado[i][1]/num_total_barajas)*100,1)))
                cuenta_top_10_cartas = cuenta_top_10_cartas + 1

            elif lista_conteo_ordenado[i][1] == lista_conteo_ordenado[i-1][1] and cuenta_top_10_cartas < 10:
                    archivo.write(' %s >> %s  (%s %%)' % (lista_conteo_ordenado[i][0], lista_conteo_ordenado[i][1], round((lista_conteo_ordenado[i][1]/num_total_barajas)*100,1)))

        archivo.write('\n')


def menu_top_10():

    top_10()

    raw_input(" Pulse enter para volver...")
    menu_ejecucion_procesado('9')


def mejor_baraja_fuerza_bruta_thread_C(comb_inicial, comb_final, matriz_relaciones_simetrica, num_thread, ruta_carpeta_resultados):

    llamar_programa_c = []

    # Ruta ejecutable
    ruta_ejecutable = ruta_principal + '/src/fuerza_bruta_thread'
    llamar_programa_c.append(ruta_ejecutable)

    # Combinacion inicial
    llamar_programa_c.append(str(comb_inicial))

    # Combinarcion final
    llamar_programa_c.append(str(comb_final))

    # Numero de filas, columnas y elementos de la matriz
    for i in matriz_2D_a_1D(matriz_relaciones_simetrica):
        llamar_programa_c.append(str(i))

    nombre_archivo_resultados = ruta_carpeta_resultados + '/resulado_thread_' + num_thread + '.txt'

    with open(nombre_archivo_resultados, "w+") as output:
        call(llamar_programa_c, stdout=output)


def mejor_baraja_fuerza_bruta_main():

    print ' MEJOR BARAJA (FUERZA BRUTA)\n'

    lista_barajas = []

    archivo_2 = open(ruta_principal + '/files/tmp/tmp.txt')

    # Lista con todas las cartas. La tengo que subdividir en grupos de 8 (num_cartas_por_baraja)
    with archivo_2 as f:
        lista_lineas = f.read().splitlines()

    for i in range(len(lista_lineas)/num_cartas_por_baraja):
        lista_barajas.append(lista_lineas[i*num_cartas_por_baraja:(i*num_cartas_por_baraja)+num_cartas_por_baraja])

    # Hago las combinaciones sin repetición de 8 (num_cartas_por_baraja) elementos tomados de 2 en 2 (esta operación se hace en cada baraja)
    lista_relaciones_cartas = []

    for i in range(len(lista_barajas)):
        lista_relaciones_cartas.append(list(combinations(lista_barajas[i], 2)))

    # Inicializo la matriz de relaciones
    matriz_relaciones = [[0]*len(lista_cartas)]

    for i in range(len(lista_cartas)):
        matriz_relaciones.append([0]*len(lista_cartas))

    # Determino los valores de la matriz de relaciones
    for i in range(len(lista_relaciones_cartas)):

        for j in range(len(lista_relaciones_cartas[0])):

            pos_tmp = []

            pos_tmp.append(lista_cartas.index(lista_relaciones_cartas[i][j][0]))
            pos_tmp.append(lista_cartas.index(lista_relaciones_cartas[i][j][1]))

            pos_tmp.sort()

            pos_1_tmp = pos_tmp[0]
            pos_2_tmp = pos_tmp[1]

            matriz_relaciones[pos_1_tmp][pos_2_tmp] = matriz_relaciones[pos_1_tmp][pos_2_tmp] + 1

    cartas = []

    matriz_relaciones_simetrica = hacer_matriz_simetrica(matriz_relaciones)

    for i in range(len(lista_cartas)):

        cartas.append(i)

    combinacion_total_barajas = factorial(len(lista_cartas))/(factorial(num_cartas_por_baraja)*factorial(len(lista_cartas)-num_cartas_por_baraja))

    # Número de CPU's que voy a usar
    cpus = elegir_cantidad_cpus()

    print ' Esto puede llevar un rato (10 minutos en un i7 usando 5 núcleos) \n\n'

    if cpus < len(cartas):
        # Lista estilo [['comb_inicial_1', 'comb_final_1'], ['comb_inicial_2', 'comb_final_2'], ... ]
        lista_comb_repartidas = crear_lista_reparto(combinacion_total_barajas, cpus)
    else:
        # Lista estilo [['comb_inicial_1', 'comb_final_1'], ['comb_inicial_2', 'comb_final_2'], ... ]
        lista_comb_repartidas = crear_lista_reparto(combinacion_total_barajas, len(cartas))

    hora_inicio = time.strftime("%d-%m-%y") + '_' + time.strftime("%H:%M:%S")
    ruta_carpeta_resultados = ruta_principal + '/files/resultados_procesado_datos/' + time.strftime("%d-%m-%y") + '_' + time.strftime("%H:%M:%S")
    os.makedirs(ruta_carpeta_resultados)

    if cpus >= len(cartas):
        pool = Pool(processes=len(cartas))
        for i in range(len(lista_comb_repartidas)):
            pool.apply_async(mejor_baraja_fuerza_bruta_thread_C, [lista_comb_repartidas[i][0], lista_comb_repartidas[i][1], matriz_relaciones_simetrica, str(i), ruta_carpeta_resultados])
    else:
        pool = Pool(processes=cpus)
        for i in range(cpus):
            pool.apply_async(mejor_baraja_fuerza_bruta_thread_C, [lista_comb_repartidas[i][0], lista_comb_repartidas[i][1], matriz_relaciones_simetrica, str(i), ruta_carpeta_resultados])

    pool.close()
    pool.join()

    hora_fin = time.strftime("%d-%m-%y") + '_' + time.strftime("%H:%M:%S")

    ruta_final = ruta_carpeta_resultados + '---' + hora_fin

    shutil.copytree(ruta_carpeta_resultados, ruta_final)
    shutil.rmtree(ruta_carpeta_resultados)

    with open(ruta_final + '/lista_cartas_' + hora_inicio + '.txt', "w+") as salida:
        for i, j in enumerate(lista_cartas):
            salida.write("%s >> %s\n" % (i, j))

    top_10_a_archivo(ruta_final + '/top_10_' + hora_inicio + '.txt')

    borrar_archivos_procesado_tmp()

    print " Procesadas %s combinaciones de cartas\n" % combinacion_total_barajas
    print " Resultados guardados en: %s\n" % ruta_final


def menu_mejor_baraja_fuerza_bruta():

    mejor_baraja_fuerza_bruta_main()

    raw_input(" Pulse enter para volver...")
    menu_ejecucion_procesado('9')


def imprimir_lista_cartas():

    comando_lista_cartas = 'python \"%s\"' % (ruta_principal + '/src/imprimir_lista_cartas.py')
    call(['gnome-terminal', '-e', comando_lista_cartas])

    menu_ejecucion_procesado('9')


acciones_menu_procesado = {
    '1': menu_top_10,
    '2': menu_mejor_baraja_fuerza_bruta,
    '3': imprimir_lista_cartas,
    '9': menu_procesado_datos,
    '0': salir,
}


def procesar_main():

    # Para no mostrar la ventana de Tk.
    Tk().withdraw()

    ruta_archivo_VOSviewer = askopenfilename(filetypes = ((".txt files", "*.txt"), ("all files", "*.*")))

    if ruta_archivo_VOSviewer == () or ruta_archivo_VOSviewer == '' or ruta_archivo_VOSviewer == None:
        raise SystemExit

    #################################################

    # Abro el archivo de texto que sería la entrada de VOSviewer
    archivo_1 = open(ruta_archivo_VOSviewer)

    # Creo un archivo en blanco
    archivo_2 = open(ruta_principal + '/files/tmp/tmp.txt', 'w')

    # Elimino los primeros caracteres de cada línea, de forma que sólo queda el nombre de la carta.
    # A partir de ahora todo lo leo desde el archivo_2
    for i in archivo_1:
        archivo_2.write(i[6:])

    archivo_1.close()
    archivo_2.close()

    menu_procesado_datos()

    #################################################

# Si el programa es llamado directamente y no desde otro programa habiendo previamente sido importado.
if __name__ == "__main__":  

    procesar_main()
