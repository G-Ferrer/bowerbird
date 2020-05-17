
/////////////////////////////////////////////////////////////////////////////
//
//    Copyright (C) 2017  Guillermo Ferrer López.
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
/////////////////////////////////////////////////////////////////////////////


// gcc -o <nombrePrograma> <nombrePrograma.c> -fopenmp
// ./<nombre_ejecutable> <archivo.csv>

// NOTA: la constante NUMERO_THREADS_A_USAR establece el número de cpu's del ordenador que se van a utilizar.
// Modificar ambos dígitos. Si se establece un número mayor de cpu's de las que dispone el equipo, automáticamente
// se establece el número máximo disponible.

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <errno.h>
#include <limits.h>
#include <omp.h>


/*
 * Genera las combinaciones en orden lexicográfico de k elementos 
 * escogidos de un conjunto (grupo) con n elementos.
 * 
 * Se puede elegir por qué combinación empezar y hasta cuál llegar
 * indicando la posición que éstas ocupan estando ordenadas
 * lexicográficamente. La numeración de dichas posiciones empieza
 * por la posición 0, no 1. 
 * 
 * Los datos se generan a partir de una matriz guardada en formato .csv
 * Dicha matriz debe ser una MATRIZ CUADRADA (igual número de filas y 
 * de columnas).
 * 
 */


//////////////// DEFINICIÓN DE CONSTANTES Y ESTRUCTURAS ////////////////

#define NUMERO_ELEMENTOS_POR_GRUPO 8  // Número de elementos por grupo
#define NUMERO_THREADS_A_USAR ( 8 <= omp_get_max_threads() ? 8 : omp_get_max_threads() )  // "Operador Ternario"

typedef struct {
    int elementosDelGrupo[NUMERO_ELEMENTOS_POR_GRUPO];
    uint64_t puntuacionDelGrupo;
} MejorGrupo;

////////////////////////////////////////////////////////////////////////


/////////////////////// PROTOTIPOS DE FUNCIONES ////////////////////////

void str2uint64_t(const char *str, uint64_t *intConvertido, int *error);

size_t obtenerNumeroDeFilasMatrizAdyacencia(char rutaArchivoCSV[]);
void *nuevaMatrizAdyacencia(size_t numeroDeFilas, size_t numeroDeColumnas);
void importarMatrizAdyacencia(char rutaArchivoCSV[], size_t numeroDeFilas, size_t numeroDeColumnas, uint64_t matrizAdyacencia[numeroDeFilas][numeroDeColumnas]);
void imprimirMatrizAdyacencia(size_t numeroDeFilas, size_t numeroDeColumnas, uint64_t matrizAdyacencia[numeroDeFilas][numeroDeColumnas]);

uint64_t binCoeff(int n, int k);
int combinationAt(int pick[], int n, int k, uint64_t index);
int nextCombination(int pick[], int n, int k);

void crearListaRepartoGrupos(uint64_t listaRepartoGrupos[], uint64_t numeroDeElementos, uint64_t numeroDeGrupos);
MejorGrupo encontrarElMejorGrupo(uint64_t posicionPrimerGrupo, uint64_t posicionUltimoGrupo, size_t numeroDeFilas, size_t numeroDeColumnas, uint64_t matrizAdyacencia[numeroDeFilas][numeroDeColumnas], int id);

////////////////////////////////////////////////////////////////////////


void str2uint64_t(const char *str, uint64_t *strConvertidoEnUint64_t, int *error) 
{
    // Convierte un string en un uint64_t    
    // Si se consigue con éxito, error = 0. En caso contrario, error = 1    
    // El resultado, se guarda en intConvertido

    *strConvertidoEnUint64_t = 0;
    *error = 0;

    const char *s = str;

    // Borra posibles espacios en blanco delante del número 
    /*while (isspace((unsigned char) *s)) 
    {
        s++;
    }*/

    int sign = *s;

    char *end;
    errno = 0;
    const uint64_t sl = strtoull(str, &end, 10);

    if (end == str) 
    {
        //fprintf(stderr, "%s: not a decimal number\n", str);
        *error = 1;
    } 

    else if ('\0' != *end) 
    {
        //fprintf(stderr, "%s: extra characters at end of input: %s\n", str, end);
        *error = 1;
    } 

    else if (ERANGE == errno) 
    {
        //fprintf(stderr, "%s out of range of type uint64_t\n", str);
        *error = 1;
    } 

    else if (sign == '-') 
    {
        //fprintf(stderr, "%s negative\n", 0);
        //errno = ERANGE;
        *error = 1;
    }

    //return sl;
    *strConvertidoEnUint64_t = sl;
}


size_t obtenerNumeroDeFilasMatrizAdyacencia(char rutaArchivoCSV[])
{
	// Obtiene el número de filas de la matriz de adyacencia guardada en un archivo .csv
	
	// Abrir el archivo .csv donde está guardada la matriz de adyacencia
	// con la que se va a trabajar
	FILE *archivoCSV = fopen(rutaArchivoCSV, "r");
	
	// Si no se puede abrir el archivo
	if (archivoCSV == NULL)
	{
		perror("Error");
		exit(EXIT_FAILURE);
	}	
	
	size_t numeroDeFilas = 0;
    char caracterArchivo;
	
	// Lee los caracteres del archivo y los guarda en la variable caracterArchivo
    for (caracterArchivo = getc(archivoCSV); caracterArchivo != EOF; caracterArchivo = getc(archivoCSV)) 
		
		// Si caracterArchivo es el carácter de salto de línea, se incrementa el contador del número de líneas
        if (caracterArchivo == '\n')
            numeroDeFilas = numeroDeFilas + 1;
            
    fclose(archivoCSV);
    
    return numeroDeFilas;
}


void *nuevaMatrizAdyacencia(size_t numeroDeFilas, size_t numeroDeColumnas)
{ 
    return malloc (sizeof(uint64_t[numeroDeFilas][numeroDeColumnas]));
}


void importarMatrizAdyacencia(char rutaArchivoCSV[], size_t numeroDeFilas, size_t numeroDeColumnas, uint64_t matrizAdyacencia[numeroDeFilas][numeroDeColumnas])
{    
    char buf[BUFSIZ];
    uint64_t filaActual = 0;
    uint64_t columnaActual = 0;
    
    uint64_t strConvertidoEnUint64_t;
    int error = 0;
    
    // Abrir el archivo .csv donde está guardada la matriz de adyacencia
	// con la que se va a trabajar
	FILE *archivoCSV = fopen(rutaArchivoCSV, "r");
	
	// Si no se puede abrir el archivo
	if (archivoCSV == NULL)
	{
		perror("Error");
		exit(EXIT_FAILURE);
	}
    
    while (fgets(buf, BUFSIZ, archivoCSV))
    {
        columnaActual = 0;
        filaActual++;

        char *elementoActual = strtok(buf, ",\n\r\t");
        str2uint64_t(elementoActual, &strConvertidoEnUint64_t, &error);
        
        if (error == 0)
            {
				matrizAdyacencia[filaActual-1][columnaActual] = strConvertidoEnUint64_t;
            }

            else
            {
                printf("Problema al importar la matriz\n");
                exit(0);
            }
        
        while (elementoActual != NULL)
        {            
            str2uint64_t(elementoActual, &strConvertidoEnUint64_t, &error);
            
            if (error == 0)
            {
				matrizAdyacencia[filaActual-1][columnaActual] = strConvertidoEnUint64_t;
            }

            else
            {
                printf("Problema al importar la matriz\n");
                exit(0);
            }
            
            elementoActual = strtok(NULL, ",\n\r\t");

            columnaActual++;            
        }        
    }
    
    fclose(archivoCSV);
}


void imprimirMatrizAdyacencia(size_t numeroDeFilas, size_t numeroDeColumnas, uint64_t matrizAdyacencia[numeroDeFilas][numeroDeColumnas])
{
    // Imprime la matriz de adyacencia por pantalla

    size_t i, j;

    putchar('\n');

    for (i = 0; i < numeroDeFilas; ++i) 
    {
        for (j = 0; j < numeroDeColumnas ; ++j) 
        {
            printf("%" PRIu64 "\t", matrizAdyacencia[i][j]);
        }

    putchar('\n');
    }

    putchar('\n');
}


uint64_t binCoeff(int n, int k)
{
	// Devuelve el coeficiente binomial C(n,k) = n!/(k!*(n-k)!)
		
	// El coeficiente binomial C(n,k) es el número de subconjuntos de k
	// elementos escogidos de un conjunto con n elementos
	
    uint64_t c = 1;
    int i = 0;
 
    if (k > n / 2) k = n - k;
 
    while (i++ < k) c = c * n-- / i;
 
    return c;
}

 
int combinationAt(int pick[], int n, int k, uint64_t index)
{
	// Inicializa el array pick con la primera combinación indicada en
	// main().
	
	// Devuelve 1 si se ha inicializado el array con éxito.
	
    int p = 0;
    int i;
 
    if (k > n) return 0;
 
    for (i = 0; i < k; i++) {
        int nn = n - 1;
        int kk = n - k + i;
        uint64_t end = binCoeff(nn, kk);
        int pp = 0;
 
        while (index >= end) {
            if (kk == 0) {
                //printf("<index:" "%"PRIu64 ">\n", index);
                return 0;
            }
 
            index -= end;
            end = end * kk-- / nn--;
            pp++; 
        }
 
        pick[i] = p + pp++;
        n -= pp;
        p += pp;
    }
 
    return 1;
}
 
 
int nextCombination(int pick[], int n, int k)
{
	// Guarda en el array pick la combinación que le sigue en orden
	// lexicográfico a la que ya tenía guardada.
	
	// Devuelve 1 si se ha generado y guardado la combinación con éxito.
	
    int m = k;
    int nk = n - k;
 
    if (k > n) return 0;
 
    if (pick[m - 1] + 1 < n) {
        pick[m - 1]++;
        return 1;
    }
 
    while (--m > 0 && pick[m] == nk + m) {}
    if (m == 0 && pick[0] == nk) return 0;
 
    pick[m++]++;
    while (m < k) {
        pick[m] =  pick[m - 1] + 1;
        m++;
    }
 
    return 1;
}
 

void crearListaRepartoGrupos(uint64_t listaRepartoGrupos[], uint64_t numeroDeElementos, uint64_t numeroDeGrupos)
{
	if (numeroDeElementos < numeroDeGrupos)
	{
		printf("Reducir el número de threads a un máximo de %" PRIu64 "\n", numeroDeElementos);
		exit(EXIT_FAILURE);
	}
	
	uint64_t i;
	uint64_t intervaloEntero  = numeroDeElementos/numeroDeGrupos;  // Obtendré la parte entera ya que uint64_t es un entero
	
	for (i = 0; i < numeroDeGrupos; i++)
	{
		listaRepartoGrupos[2*i] = i*intervaloEntero;
		listaRepartoGrupos[2*i + 1] = i*intervaloEntero + intervaloEntero;
	}	
	
	listaRepartoGrupos[2*numeroDeGrupos-1] = numeroDeElementos;	
}
 

MejorGrupo encontrarElMejorGrupo(uint64_t posicionPrimerGrupo, uint64_t posicionUltimoGrupo, size_t numeroDeFilas, size_t numeroDeColumnas, uint64_t matrizAdyacencia[numeroDeFilas][numeroDeColumnas], int id)
{
	// Devuelve el mejor grupo y su puntuación de entre todos los grupos
	// que estén en el intervalo [posicionPrimerGrupo, posicionUltimoGrupo[
	
	// Inicializo la variable que guarda el grupo y su puntuación
	MejorGrupo mejorGrupo;
	mejorGrupo.puntuacionDelGrupo = 0;	
	
	// Variable con los índices de las combinaciones de los elementos 
	// de cada grupo tomados de dos en dos. Se guardan en un array
	// de una dimensión, por lo que se cogerán los índices de dos en dos
	uint64_t numeroDeCombinacionesDeDosEnDos = binCoeff(NUMERO_ELEMENTOS_POR_GRUPO,2);
	uint64_t indicesCombinacionesGrupo[2*numeroDeCombinacionesDeDosEnDos];	
	
    //////////////////////////////
        
	int okayDeDosEnDos;
    uint64_t combinacionInicialDeDosEnDos = 0;
    int offset = 0;  // Contador que va a permitir coger los elementos de dos en dos
    int combinacionesDeDosEnDosTemporal[2];  // Lista temporal para ir guardando las combinaciones generada

    okayDeDosEnDos = combinationAt(combinacionesDeDosEnDosTemporal, NUMERO_ELEMENTOS_POR_GRUPO, 2, combinacionInicialDeDosEnDos);

    while (okayDeDosEnDos && combinacionInicialDeDosEnDos < numeroDeCombinacionesDeDosEnDos) 
    {        
        int i;

        for (i = 0; i < 2; i++) 
        {
            indicesCombinacionesGrupo[i + 2*offset] = combinacionesDeDosEnDosTemporal[i];
        }

        offset++;

        okayDeDosEnDos = nextCombination(combinacionesDeDosEnDosTemporal, NUMERO_ELEMENTOS_POR_GRUPO, 2);
        combinacionInicialDeDosEnDos++;
    }
    
    //////////////////////////////
    
    // Array de longitud k donde se guardarán las combinaciones
    int elementosDelGrupo[NUMERO_ELEMENTOS_POR_GRUPO];
    
    // Variable a la que se le asigna el éxito (okay = 1) de la 
    // generación de las combinaciones
    int okay;
    
    // Se genera la primera combinación. 
	// okay = 1 si se ha generado con éxito
    okay = combinationAt(elementosDelGrupo, numeroDeFilas, NUMERO_ELEMENTOS_POR_GRUPO, posicionPrimerGrupo);
    
    // Mientras se haya generado la anterior combinación con éxito 
    // y todavía no se haya generado la última combinación:
    while (okay && posicionPrimerGrupo < posicionUltimoGrupo)
    {
		// Comprobar si la puntuación del grupo es mayor que la del 
		// mejor grupo hasta este momento. Si es así, se guarda
		
		int i, j;
        int offset = 0;
        uint64_t puntuacionDelGrupo = 0;

        for (i = 0;  i < numeroDeCombinacionesDeDosEnDos; i++)
        { 
            puntuacionDelGrupo = puntuacionDelGrupo + matrizAdyacencia[elementosDelGrupo[indicesCombinacionesGrupo[2*offset]]][elementosDelGrupo[indicesCombinacionesGrupo[2*offset+1]]];
            offset++;
        }
        
        if (puntuacionDelGrupo > mejorGrupo.puntuacionDelGrupo)
        {			
			for (j = 0; j < NUMERO_ELEMENTOS_POR_GRUPO; j++)
			{
				mejorGrupo.elementosDelGrupo[j] = elementosDelGrupo[j];
			}
			
			mejorGrupo.puntuacionDelGrupo = puntuacionDelGrupo;
		}
 
		// Se genera la siguiente combinación
        okay = nextCombination(elementosDelGrupo, numeroDeFilas, NUMERO_ELEMENTOS_POR_GRUPO);
        posicionPrimerGrupo++;
    }
    
    /*
    int k;
    
    printf("THREAD: %d; MEJOR GRUPO: [ ", id);		
	for (k = 0; k < NUMERO_ELEMENTOS_POR_GRUPO; k++)
	{
		printf("%d ", mejorGrupo.elementosDelGrupo[k]);
	}			
	printf("]; PUNTUACIÓN: %" PRIu64 ";\n", mejorGrupo.puntuacionDelGrupo);
	*/
    
	return mejorGrupo;
}


int main(int argc, char *argv[])
{
// Abrir archivo .csv y ver las dimensiones de la matriz de adyacencia.
// Como es una matriz cuadrada, el número de columnas será igual al
// número de filas

	// Si no se da la ruta de un archivo al llamar al programa
	if (argc < 2)
	{
		fprintf(stderr, "Uso: ./<nombrePrograma> <archivoCSV.csv>\n");
		exit(EXIT_FAILURE);
	}
	
	size_t numeroDeFilas = obtenerNumeroDeFilasMatrizAdyacencia(argv[1]);
	size_t numeroDeColumnas = numeroDeFilas;
    
    // Puntero a un array de ncolumnas elementos del tipo uint64_t
    uint64_t (*matrizAdyacencia)[numeroDeFilas] = nuevaMatrizAdyacencia(numeroDeFilas, numeroDeColumnas);

    // Importar y guardar la matriz de adyacencia
    importarMatrizAdyacencia(argv[1], numeroDeFilas,numeroDeColumnas, matrizAdyacencia);
    
    // Imprimir la matriz de adyacencia por pantalla.
    //imprimirMatrizAdyacencia(numeroDeFilas, numeroDeColumnas, matrizAdyacencia);
    
    uint64_t posicionUltimoGrupo = binCoeff(numeroDeFilas, NUMERO_ELEMENTOS_POR_GRUPO);
    //uint64_t posicionUltimoGrupo = 1000000000;
    
    uint64_t listaRepartoGrupos[2*NUMERO_THREADS_A_USAR];	
	crearListaRepartoGrupos(listaRepartoGrupos, posicionUltimoGrupo, NUMERO_THREADS_A_USAR);
    
    // Encontrar el mejor grupo en el intervalo [posicionPrimerGrupo, posicionUltimoGrupo[
    // de manera parelela en varios hilos de ejecución
    
    // Cada hilo guarda en una posición el mejor grupo que ha encontrado
    MejorGrupo mejorGrupoDeCadaThread[NUMERO_THREADS_A_USAR];  
    
    #pragma omp parallel num_threads(NUMERO_THREADS_A_USAR)
    {
		int id;
		
		id = omp_get_thread_num();  // Número de identificación del hilo
		
		mejorGrupoDeCadaThread[id] = encontrarElMejorGrupo(listaRepartoGrupos[2*id], listaRepartoGrupos[2*id+1], numeroDeFilas, numeroDeColumnas, matrizAdyacencia, id);
	}
	
	// Seleccionar el mejor grupo del array con el mejor grupo de cada hilo
	int i;
	int idMejorGrupo = 0;
	uint64_t mejorPuntuacion = 0;
	
	for (i = 0; i < NUMERO_THREADS_A_USAR; i++)
	{
		if (mejorGrupoDeCadaThread[i].puntuacionDelGrupo > mejorPuntuacion)
		{
			idMejorGrupo = i;
			mejorPuntuacion = mejorGrupoDeCadaThread[i].puntuacionDelGrupo;
		}
	}
	
	// Imprimir el mejor grupo	
	int j;
    
    printf("\nMEJOR GRUPO: [ ");		
	for (j = 0; j < NUMERO_ELEMENTOS_POR_GRUPO; j++)
	{
		printf("%d ", mejorGrupoDeCadaThread[idMejorGrupo].elementosDelGrupo[j]);
	}			
	printf("]; PUNTUACIÓN: %" PRIu64 ";\n", mejorGrupoDeCadaThread[idMejorGrupo].puntuacionDelGrupo);
	
	// Libero el espacio ocupado por la matriz de adyacencia
    free(matrizAdyacencia);

    return 0;
}

