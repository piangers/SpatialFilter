# -*- coding: utf-8 -*-

def classFactory(iface):


    from .SpatialFilter import SpatialFilter
    return SpatialFilter(iface)
