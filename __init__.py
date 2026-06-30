# -*- coding: utf-8 -*-
def classFactory(iface):
    from .cartodxf import CartoDXFPlugin
    return CartoDXFPlugin(iface)
