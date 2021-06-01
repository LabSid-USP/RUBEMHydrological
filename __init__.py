# coding=utf-8
"""
/***************************************************************************
 **RUBEM Hydrological
                A Rainfall rUnoff Balance Enhanced Model wizard
 **Description
                             -------------------
        begin                : **2021
        copyright            : **Laboratório de Sistemas de Suporte a 
                             :   Decisões Aplicados à Engenharia Ambiental e 
                             :   de Recursos Hídricos (LabSid) PHA-EPUSP
        email                : **rubem.hydrological@labsid.eng.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'rubem.hydrological@labsid.eng.br'
__date__ = '2021-05-19'
__copyright__ = 'Copyright 2021, LabSid'

def classFactory(iface):
    from .rubem_hydrological import RUBEMHydrological
    return RUBEMHydrological(iface)
