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


def visualizar_main():
    
    print ' - Descargar VOSViewer (www.vosviewer.com) y ejecutarlo.'
    print ' - En la pestaña "File" pulsar en "Create...".'
    print ' - Seleccionar la opción "Create a map based on bibliographic data".'
    print ' - Ir a la pestaña "RIS" y pulsar sobre el botón "...".'
    print ' - En "Archivos de tipo" cambiar a "All files (*.*)" y seleccionar el archivo creado en el paso de "Identificar Cartas".'
    print ' - Pulsar "Finish".'
    print ' - Para una mejor visualización es recomendable activar "Black background", "Colored lines" y cambiar el número de líneas a 500.\n'

    #################################################

# Si el programa es llamado directamente y no desde otro programa habiendo previamente sido importado.
if __name__ == "__main__":  

    visualizar_main()