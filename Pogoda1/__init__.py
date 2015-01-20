# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pogoda1
                                 A QGIS plugin
 pobieranie danych o pogodzie
                             -------------------
        begin                : 2015-01-20
        copyright            : (C) 2015 by Knapsiu
        email                : lalala@op.pl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Pogoda1 class from file Pogoda1.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Pogoda1 import Pogoda1
    return Pogoda1(iface)
