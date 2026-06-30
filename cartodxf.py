# -*- coding: utf-8 -*-
"""
cartodxf.py  —  Plugin principal CartoDXF
"""
import os

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .cartodxf_dialog import CartoDXFDialog


class CartoDXFPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'icon.png')
        icon = QIcon(icon_path) if os.path.isfile(icon_path) else QIcon()
        self.action = QAction(icon, 'CartoDXF', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu('&CartoDXF', self.action)

    def unload(self):
        self.iface.removePluginVectorMenu('&CartoDXF', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        dlg = CartoDXFDialog(self.iface)
        dlg.exec()
