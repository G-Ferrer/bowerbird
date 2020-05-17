
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


// gcc -o <nombrePrograma> <nombrePrograma.c>
// ./<nombre_ejecutable> comb_inicial comb_final(no incluida) num_filas num_columnas valores_matriz
// Ej: ./<nombre_ejecutable> 10 15 4 3 1 2 3 4 5 6 7 8 9 10 11 12

// BUG: si ncxb = 2 o ncxb = ncartas sale error.

#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <errno.h>
#include <limits.h>
#include <string.h>
#include <stdint.h>


///////////////////////////////////////////////////////////////////////////////

typedef struct {
    int baraja[8];
    uint64_t puntuacion_acumulada;
} MejorBaraja;

typedef struct {
    MejorBaraja *array;
    size_t used;
    size_t size;
} Array;

///////////////////////////////////////////////////////////////////////////////

void *NuevaMatriz(size_t nfilas, size_t ncolumnas);
void ImprimirMatriz(size_t nfilas, size_t ncolumnas, uint64_t matriz[nfilas][ncolumnas]);
void ImportarMatriz(char *valores[], size_t nfilas, size_t ncolumnas, uint64_t matriz[nfilas][ncolumnas]);

void Str2Uint64_t(const char *str, uint64_t *int_convertido, int *error);
void Str2int(const char *str, int *int_convertido, int *error);

uint64_t bincoeff(int n, int k);
int combo_at(int pick[], int n, int k, uint64_t index);
int next_combo(int pick[], int n, int k);

unsigned factorial(unsigned n);
unsigned combs_x_y(unsigned x, unsigned y);

void initArray(Array *a, size_t initialSize);
void insertArray(Array *a, int *baraja_add, uint64_t puntuacion_acumulada_add);
void freeArray(Array *a);
void copiarArray(Array *a, Array *b);
void imprimirArray(Array *arr);

///////////////////////////////////////////////////////////////////////////////

void *NuevaMatriz(size_t nfilas, size_t ncolumnas)
{ 
    return malloc (sizeof(uint64_t[nfilas][ncolumnas]));
}


void ImprimirMatriz(size_t nfilas, size_t ncolumnas, uint64_t matriz[nfilas][ncolumnas])
{
    // Imprime la matriz por pantalla

    size_t i, j;

    putchar('\n');

    for (i = 0; i < nfilas; ++i) 
    {
        for (j = 0; j < ncolumnas ; ++j) 
        {
            printf("%" PRIu64 "\t", matriz[i][j]);
        }

    putchar('\n');
    }

    putchar('\n');
}


void ImportarMatriz(char *valores[], size_t nfilas, size_t ncolumnas, uint64_t matriz[nfilas][ncolumnas])
{
    // Construye la matriz a partir de los parámetros de llamada al programa

    size_t i, j;
    uint64_t contador = 0;

    uint64_t int_convertido;
    int error;

    printf("\n");

    for (i = 0; i < nfilas; ++i) 
    {
        for (j = 0; j < ncolumnas ; ++j) 
        {
            Str2Uint64_t(valores[contador], &int_convertido, &error);

            if (error == 0)
            {
                matriz[i][j] = int_convertido;
                contador++;
            }

            else
            {
                printf("Problema al importar la matriz\n");
                exit(0);
            }
        }
    }

    putchar('\n');
}


void Str2Uint64_t(const char *str, uint64_t *int_convertido, int *error) 
{
    // Convierte un string en un uint64_t, si se puede.
    // Si se ha conseguido, error = 0. En caso contrario, error = 1.
    // El resultado, se guarda en int_convertido.

    *int_convertido = 0;
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
    *int_convertido = sl;
}


void Str2int(const char *str, int *int_convertido, int *error) 
{
    // Convierte un string en un uint64_t, si se puede.
    // Si se ha conseguido, error = 0. En caso contrario, error = 1.
    // El resultado, se guarda en int_convertido.

    *int_convertido = 0;
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
    const int sl = strtol(str, &end, 10);

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
    *int_convertido = sl;
}


uint64_t bincoeff(int n, int k)
{
    uint64_t c = 1;
    int i = 0;
 
    if (k > n / 2) k = n - k;
 
    while (i++ < k) c = c * n-- / i;
 
    return c;
}
 

int combo_at(int pick[], int n, int k, uint64_t index)
{
    int p = 0;
    int i;
 
    if (k > n) return 0;
 
    for (i = 0; i < k; i++) 
    {
        int nn = n - 1;
        int kk = n - k + i;
        uint64_t end = bincoeff(nn, kk);
        int pp = 0;
 
        while (index >= end) 
        {
            if (kk == 0) 
            {
                printf("<index:" "%"PRIu64 ">\n", index);
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


int next_combo(int pick[], int n, int k)
{
    int m = k;
    int nk = n - k;
 
    if (k > n) return 0;
 
    if (pick[m - 1] + 1 < n) 
    {
        pick[m - 1]++;
        return 1;
    }
 
    while (--m > 0 && pick[m] == nk + m) {}
    if (m == 0 && pick[0] == nk) return 0;
 
    pick[m++]++;
    while (m < k) 
    {
        pick[m] =  pick[m - 1] + 1;
        m++;
    }
 
    return 1;
}


unsigned factorial(unsigned n)
{
    if (n == 1)
        return 1;

    else
        return n * factorial(n - 1);
}


unsigned combs_x_y(unsigned x, unsigned y)
{
    if (x < y)
    {
        printf("Error al calcular el número de combinaciones\n");
        exit(0);
    }

    return (factorial(x)/(factorial(y)*factorial(x-y)));
}


void initArray(Array *a, size_t initialSize)
{
    a->array = (MejorBaraja *)malloc(initialSize * sizeof(MejorBaraja));
    a->used = 0;
    a->size = initialSize;
}

 
void insertArray(Array *a, int *baraja_add, uint64_t puntuacion_acumulada_add)
{
    // a->used is the number of used entries, because a->array[a->used++] updates a->used only *after* the array has been accessed.
    // Therefore a->used can go up to a->size 
  
    if (a->used == a->size) 
    {
        a->size *= 2;
        a->array = (MejorBaraja *)realloc(a->array, a->size * sizeof(MejorBaraja));
    }
 
    int i;

    for (i = 0; i < 8; i++)
    {
        a->array[a->used].baraja[i] = baraja_add[i];
    }

    a->array[a->used].puntuacion_acumulada = puntuacion_acumulada_add;
    a->used++;
}


void freeArray(Array *a)
{
    free(a->array);
    a->array = NULL;
    a->used = a->size = 0;
}


void copiarArray(Array *a, Array *b)
{
    // Copia los datos del Array a al Array b

    freeArray(b);
    initArray(b, a->used);
    memmove(b->array, a->array, a->used * sizeof(a->array[0]));
    b->used = a->used;
}


void imprimirArray(Array *arr)
{
    size_t i, j;

    if (arr->used > 0)
    {

        printf("Puntuación acumulada: %" PRIu64 "\n", arr->array->puntuacion_acumulada);
        printf("Número de barajas: %zu\n\n", arr->used);
        printf("\n");

    for (i = 0; i < arr->used; i++)
    {

        printf("[");

        for (j = 0; j < 8; j++)
        {
            if (j) printf(", ");
            printf("%d", arr->array[i].baraja[j]);
        }

        printf("]\n");
    }

        putchar('\n');
        putchar('\n');
  }
}

///////////////////////////////////////////////////////////////////////////////

int main(int argc, char *argv[])
{
    // argv[0] = nombre del programa
    // argv[1] = combinación inicial
    // argv[2] = combinación final
    // argv[3] = número de filas
    // argv[4] = número de columnas
    // argv[5 en adelante] = elementos de la matriz

    // El número de filas y columnas debe coincidir con el número de cartas.

    uint64_t comb_inicial;
    uint64_t comb_final;
    size_t  nfilas, ncolumnas;

    int int_convertido;
    uint64_t int64_convertido;

    Array lista_mejores_barajas_1;
    Array lista_mejores_barajas_2;
    Array lista_mejores_barajas_3;

    // Inicializo la lista con 5 posiciones, por ejemplo.
    initArray(&lista_mejores_barajas_1, 5);
    initArray(&lista_mejores_barajas_2, 5);
    initArray(&lista_mejores_barajas_3, 5);

    int error;

    // Leo y guardo la combinación inicial. Salgo en caso de error.
    Str2Uint64_t(argv[1], &int64_convertido, &error);
    if (error == 0)
    {
        comb_inicial = int64_convertido;
    }

    else
    {
        printf("Problema al importar la combinación inicial\n");
        exit(0);
    }

    //Leo y guardo la combinación final. Salgo en caso de error.
    Str2Uint64_t(argv[2], &int64_convertido, &error);
    if (error == 0)
    {
        comb_final = int64_convertido;
    }

    else
    {
        printf("Problema al importar la combinación final\n");
        exit(0);
    }

    // Compruebo que puedo importar la matriz, y que ésta cumple los requisitos de funcionamiento del programa.
    if (argc > 5)
    {

        // Leo y guardo el número de filas de la matriz. Salgo en caso de error.
        Str2int(argv[3], &int_convertido, &error);
        if (error == 0)
        {
            nfilas = int_convertido;
        }

        else
        {
            printf("Problema al importar el número de filas\n");
            exit(0);
        }

        //Leo y guardo el número de columnas de la matriz. Salgo en caso de error.
        Str2int(argv[4], &int_convertido, &error);
        if (error == 0)
        {
          ncolumnas = int_convertido;
        }

        else
        {
          printf("Problema al importar el número de columnas\n");
          exit(0);
        }

        // Compruebo que el número de filas y columnas concuerda con el número de elementos proporcionados para formar la matriz.
        if ((nfilas*ncolumnas)%(argc-5) != 0 || nfilas == 0 || ncolumnas == 0)
        {
            printf("El número de filas y columnas no concuerda con el número de elementos en la matriz\n");
            exit(0);
        }

        // Para este programa en concreto, la matriz debe ser cuadrada (nfilas = ncolumnas).
        if (nfilas != ncolumnas)
        {
            printf("La matriz no es cuadrada\n");
            exit(0);
        }
    }

    else
    {
        printf("Se requieren parámetros de entrada:\n");
        printf("./<nombre_ejecutable> comb_inicial comb_final num_filas num_columnas valores_matriz\n");
        printf("p.ej: ./<nombre_ejecutable> 10 15 3 3 4 7 9 3 1 2 4 7 2\n");
        exit(0);
    }

    // Puntero a un array de ncolumnas elementos del tipo uint64_t
    uint64_t (*matriz)[ncolumnas] = NuevaMatriz(nfilas, ncolumnas);

    // Importo y guardo la matriz.
    ImportarMatriz(argv + 5, nfilas, ncolumnas, matriz);

    /////////////////////////////////////

    size_t ncartas = nfilas;

    // Número de cartas por baraja.
    size_t ncxb = 8;

    // Código que identifica unívocamente cada baraja generada.
    // Cada uno de los dígitos del código, indica qué carta forma parte de la baraja.
    int cod_baraja[ncxb];
    int okay;

    if (ncartas < ncxb)
    {
        printf("El número de cartas por baraja (%zu) no puede ser mayor al número de cartas totales (%zu)\n", ncxb, ncartas);
        exit(0);
    }

    /////////////////

    // Creo estas variables para conseguir la lista de combinaciones de 2 en 2 de las cartas de cada baraja.
    // Lo hago así para sólo generar esta lista una vez y no una vez por cada baraja.
    int okay_2;
    int comb_inicial_2 = 0;

    // Número de combinaciones de dos en dos de las cartas de cada baraja.
    unsigned ncombs_ncxb_2 = combs_x_y(ncxb, 2);

    // Lista temporal para ir guardando las combinaciones generadas.
    int combs_ncxb_2_tmp[2]; 

    // Lista con el doble de elementos de ncombs_ncxb_2 (cogeré de dos en dos los elementos para calcular la
    // puntuación acumulada de cada baraja).
    int combs_ncxb_2[2*ncombs_ncxb_2];

    okay_2 = combo_at(combs_ncxb_2_tmp, ncxb, 2, comb_inicial_2);

    int desplz = 0;

    while (okay_2 && comb_inicial_2 < ncombs_ncxb_2) 
    {
        
        int i;

        for (i = 0; i < 2; i++) 
        {
            combs_ncxb_2[i + 2*desplz] = combs_ncxb_2_tmp[i];
        }

        desplz++;

        okay_2 = next_combo(combs_ncxb_2_tmp, ncxb, 2);
        comb_inicial_2++;
    }

    /////////////////

    // NOTA: el número de cartas debe ser igual o mayor al número de cartas por baraja.

    okay = combo_at(cod_baraja, ncartas, ncxb, comb_inicial);

    while (okay && comb_inicial < comb_final) 
    {
        int i;
        int adelanto_pos = 0;
        uint64_t puntuacion_acumulada = 0;

        for (i = 0; i < ncombs_ncxb_2; i++)
        { 
            puntuacion_acumulada = puntuacion_acumulada + matriz[cod_baraja[combs_ncxb_2[2*adelanto_pos]]][cod_baraja[combs_ncxb_2[2*adelanto_pos+1]]];
            adelanto_pos++;
        }

        // Compruebo si hay alguna lista sin iniciar.

        if (lista_mejores_barajas_1.used == 0)
        {
            insertArray(&lista_mejores_barajas_1, cod_baraja, puntuacion_acumulada);
        }

        else if (lista_mejores_barajas_2.used == 0)
        {
            insertArray(&lista_mejores_barajas_2, cod_baraja, puntuacion_acumulada);
        }

        else if (lista_mejores_barajas_3.used == 0)
        {
            insertArray(&lista_mejores_barajas_3, cod_baraja, puntuacion_acumulada);
        }

        // Compruebo si hay alguna lista en la que coincida la puntuación acumulada.

        else if (puntuacion_acumulada == lista_mejores_barajas_1.array->puntuacion_acumulada)
        {
            insertArray(&lista_mejores_barajas_1, cod_baraja, puntuacion_acumulada);
        }

        else if (puntuacion_acumulada == lista_mejores_barajas_2.array->puntuacion_acumulada)
        {
            insertArray(&lista_mejores_barajas_2, cod_baraja, puntuacion_acumulada);
        }

        else if (puntuacion_acumulada == lista_mejores_barajas_3.array->puntuacion_acumulada)
        {
            insertArray(&lista_mejores_barajas_3, cod_baraja, puntuacion_acumulada);
        }

        // Compruebo el resto de condiciones.

        else if (puntuacion_acumulada < lista_mejores_barajas_1.array->puntuacion_acumulada)
        {
            copiarArray(&lista_mejores_barajas_2, &lista_mejores_barajas_3);
            copiarArray(&lista_mejores_barajas_1, &lista_mejores_barajas_2);
            lista_mejores_barajas_1.used = 0;
            insertArray(&lista_mejores_barajas_1, cod_baraja, puntuacion_acumulada);
        }

        else if (puntuacion_acumulada > lista_mejores_barajas_1.array->puntuacion_acumulada && puntuacion_acumulada < lista_mejores_barajas_2.array->puntuacion_acumulada)
        {
            copiarArray(&lista_mejores_barajas_2, &lista_mejores_barajas_3);
            lista_mejores_barajas_2.used = 0;
            insertArray(&lista_mejores_barajas_2, cod_baraja, puntuacion_acumulada);
        }

        else if (puntuacion_acumulada > lista_mejores_barajas_1.array->puntuacion_acumulada && puntuacion_acumulada > lista_mejores_barajas_2.array->puntuacion_acumulada && puntuacion_acumulada < lista_mejores_barajas_3.array->puntuacion_acumulada)
        {
            lista_mejores_barajas_3.used = 0;
            insertArray(&lista_mejores_barajas_3, cod_baraja, puntuacion_acumulada);
        }

        okay = next_combo(cod_baraja, ncartas, ncxb);
        comb_inicial++;
    }

    imprimirArray(&lista_mejores_barajas_1);
    imprimirArray(&lista_mejores_barajas_2);
    imprimirArray(&lista_mejores_barajas_3);

    /////////////////////////////////////

    // Imprimo la matriz por pantalla.
    // ImprimirMatriz(nfilas, ncolumnas, matriz);

    // Libero el espacio ocupado por la matriz.
    free(matriz);

    freeArray(&lista_mejores_barajas_1);
    freeArray(&lista_mejores_barajas_2);
    freeArray(&lista_mejores_barajas_3);

    return 0;
}
