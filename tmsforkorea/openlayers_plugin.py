# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2009-11-30
copyright            : (C) 2009 by Pirmin Kalberer, Sourcepole
email                : pka at sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import (QSettings, QTranslator)
from qgis.PyQt.QtWidgets import (QApplication, QLineEdit, QInputDialog,
                                 QAction, QMenu)
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsCoordinateTransform, Qgis, QgsProject,
                       QgsPluginLayerRegistry, QgsLayerTree, QgsMapLayer,
                       QgsRasterLayer, QgsMessageLog)

from . import resources_rc
from .about_dialog import AboutDialog
from .openlayers_overview import OLOverview
from .openlayers_layer import OpenlayersLayer
from .openlayers_plugin_layer_type import OpenlayersPluginLayerType
from .weblayers.weblayer_registry import WebLayerTypeRegistry
#from .weblayers.google_maps import (OlGooglePhysicalLayer,
#                                    OlGoogleStreetsLayer, OlGoogleHybridLayer,
#                                    OlGoogleSatelliteLayer)
#from .weblayers.osm import (OlOpenStreetMapLayer,
#                            OlOSMHumanitarianDataModelLayer)
#from .weblayers.osm_thunderforest import (OlOpenCycleMapLayer,
#                                          OlOCMLandscapeLayer,
#                                          OlOCMPublicTransportLayer,
#                                          OlOCMOutdoorstLayer,
#                                          OlOCMTransportDarkLayer,
#                                          OlOCMSpinalMapLayer,
#                                          OlOCMPioneerLayer,
#                                          OlOCMMobileAtlasLayer,
#                                          OlOCMNeighbourhoodLayer)
#from .weblayers.bing_maps import (OlBingRoadLayer, OlBingAerialLayer,
#                                  OlBingAerialLabelledLayer)
#from .weblayers.apple_maps import OlAppleiPhotoMapLayer
#from .weblayers.osm_stamen import (OlOSMStamenTonerLayer,
#                                   OlOSMStamenTonerLiteLayer,
#                                   OlOSMStamenWatercolorLayer,
#                                   OlOSMStamenTerrainLayer)
#from .weblayers.wikimedia_maps import (WikimediaLabelledLayer,
#                                       WikimediaUnLabelledLayer)

import os.path
import time
# TMS for Korea 2014-09-19
from .weblayers.vworld_maps import (OlVWorldStreetLayer,
                                    OlVWorldGrayLayer,
                                    OlVWorldHybridLayer,
                                    OlVWorldSatelliteLayer)
from .weblayers.daum_maps import (OlDaumStreetLayer,
                                  OlDaumHybridLayer,
                                  OlDaumSatelliteLayer,
                                  OlDaumPhysicalLayer,
                                  OlDaumCadstralLayer)
from .weblayers.naver_maps import (OlNaverStreetLayer,
                                   OlNaverHybridLayer,
                                   OlNaverSatelliteLayer,
                                   OlNaverPhysicalLayer,
                                   OlNaverCadastralLayer)
from .weblayers.olleh_maps import (OlOllehStreetLayer,
                                   OlOllehHybridLayer,
                                   OlOllehSatelliteLayer,
                                   OlOllehPhysicalLayer,
                                   OlOllehCadstralLayer)
from .weblayers.ngii_maps import (OlNgiiStreetLayer,
                                  OlNgiiBlankLayer,
                                  OlNgiiEnglishLayer,
                                  OlNgiiHighDensityLayer,
                                  OlNgiiColorBlindLayer)




class OpenlayersPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Keep a reference to all OL layers to avoid GC
        self._ol_layers = []
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, "i18n",
                                  "openlayers_{}.qm".format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
    

        self._olLayerTypeRegistry = WebLayerTypeRegistry(self)
        self.olOverview = OLOverview(iface, self._olLayerTypeRegistry)
        self.dlgAbout = AboutDialog()
        self.pluginLayerRegistry = QgsPluginLayerRegistry()

    def initGui(self):
        self._olMenu = QMenu("TMS for Korea")
        self._olMenu.setIcon(QIcon(":/plugins/tmsforkorea/openlayers.png"))

        # Overview
        self.overviewAddAction = QAction(QApplication.translate(
            "OpenlayersPlugin", "OpenLayers Overview"),
                                         self.iface.mainWindow())
        self.overviewAddAction.setCheckable(True)
        self.overviewAddAction.setChecked(False)
        self.overviewAddAction.toggled.connect(self.olOverview.setVisible)
        self._olMenu.addAction(self.overviewAddAction)

        self._actionAbout = QAction("Terms of Service / About",
                                    self.iface.mainWindow())
        self._actionAbout.triggered.connect(self.dlgAbout.show)
        self._olMenu.addAction(self._actionAbout)
        self.dlgAbout.finished.connect(self._publicationInfoClosed)
        # OpenLayers plugin layers
        """

        self._olLayerTypeRegistry.register(OlGooglePhysicalLayer())
        self._olLayerTypeRegistry.register(OlGoogleStreetsLayer())
        self._olLayerTypeRegistry.register(OlGoogleHybridLayer())
        self._olLayerTypeRegistry.register(OlGoogleSatelliteLayer())

        self._olLayerTypeRegistry.register(OlOpenStreetMapLayer())
        self._olLayerTypeRegistry.register(OlOpenCycleMapLayer())
        self._olLayerTypeRegistry.register(OlOCMLandscapeLayer())
        self._olLayerTypeRegistry.register(OlOCMPublicTransportLayer())

        # ID 8-10 was Yahoo
        self._olLayerTypeRegistry.register(OlOSMHumanitarianDataModelLayer())

        self._olLayerTypeRegistry.register(OlOCMOutdoorstLayer())
        self._olLayerTypeRegistry.register(OlOCMTransportDarkLayer())

        self._olLayerTypeRegistry.register(OlBingRoadLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLabelledLayer())

        # Order from here on is free. Layers 0-14 should keep order for
        # compatibility with OL Plugin < 2.3

        self._olLayerTypeRegistry.register(OlOCMSpinalMapLayer())
        self._olLayerTypeRegistry.register(OlOCMPioneerLayer())
        self._olLayerTypeRegistry.register(OlOCMMobileAtlasLayer())
        self._olLayerTypeRegistry.register(OlOCMNeighbourhoodLayer())

        self._olLayerTypeRegistry.register(OlOSMStamenTonerLayer())
        self._olLayerTypeRegistry.register(OlOSMStamenTonerLiteLayer())
        self._olLayerTypeRegistry.register(OlOSMStamenWatercolorLayer())
        self._olLayerTypeRegistry.register(OlOSMStamenTerrainLayer())

        self._olLayerTypeRegistry.register(OlAppleiPhotoMapLayer())

        self._olLayerTypeRegistry.register(WikimediaLabelledLayer())
        self._olLayerTypeRegistry.register(WikimediaUnLabelledLayer())
        """
        

        # TMS for Korea 2014-09-19
        self._olLayerTypeRegistry.register(OlDaumStreetLayer())
        self._olLayerTypeRegistry.register(OlDaumHybridLayer())
        self._olLayerTypeRegistry.register(OlDaumSatelliteLayer())
        self._olLayerTypeRegistry.register(OlDaumPhysicalLayer())
        self._olLayerTypeRegistry.register(OlDaumCadstralLayer())
        
        self._olLayerTypeRegistry.register(OlNaverStreetLayer())
        self._olLayerTypeRegistry.register(OlNaverHybridLayer())
        self._olLayerTypeRegistry.register(OlNaverSatelliteLayer())
        self._olLayerTypeRegistry.register(OlNaverPhysicalLayer())
        self._olLayerTypeRegistry.register(OlNaverCadastralLayer())
        
        self._olLayerTypeRegistry.register(OlOllehStreetLayer())
        self._olLayerTypeRegistry.register(OlOllehHybridLayer())
        self._olLayerTypeRegistry.register(OlOllehSatelliteLayer())
        self._olLayerTypeRegistry.register(OlOllehPhysicalLayer())
        self._olLayerTypeRegistry.register(OlOllehCadstralLayer())
        
        self._olLayerTypeRegistry.register(OlVWorldStreetLayer())
        self._olLayerTypeRegistry.register(OlVWorldGrayLayer())
        self._olLayerTypeRegistry.register(OlVWorldHybridLayer())
        self._olLayerTypeRegistry.register(OlVWorldSatelliteLayer())
        
        self._olLayerTypeRegistry.register(OlNgiiStreetLayer())
        self._olLayerTypeRegistry.register(OlNgiiBlankLayer())
        self._olLayerTypeRegistry.register(OlNgiiEnglishLayer())
        self._olLayerTypeRegistry.register(OlNgiiHighDensityLayer())
        self._olLayerTypeRegistry.register(OlNgiiColorBlindLayer())
        

        for group in self._olLayerTypeRegistry.groups():
            groupMenu = group.menu()
            for layer in self._olLayerTypeRegistry.groupLayerTypes(group):
                layer.addMenuEntry(groupMenu, self.iface.mainWindow())
            self._olMenu.addMenu(groupMenu)

        # add action for API key dialogs
        for action in self._olMenu.actions():
            if action.text() == "Google Maps":
                self._actionGoogleMapsApiKey = QAction(
                    "Set API key", self.iface.mainWindow())
                self._actionGoogleMapsApiKey.triggered.connect(
                    self.showGoogleMapsApiKeyDialog)
                action.menu().addAction(self._actionGoogleMapsApiKey)
            if action.text() == "OSM/Thunderforest":
                self._actionThunderforestApiKey = QAction(
                    "Set API key", self.iface.mainWindow())
                self._actionThunderforestApiKey.triggered.connect(
                    self.showThunderforestApiKeyDialog)
                action.menu().addAction(self._actionThunderforestApiKey)

        # Create Web menu, if it doesn't exist yet
        self.iface.addPluginToWebMenu("_tmp", self._actionAbout)
        self._menu = self.iface.webMenu()
        self._menu.addMenu(self._olMenu)
        self.iface.removePluginWebMenu("_tmp", self._actionAbout)

        # Register plugin layer type
        self.pluginLayerType = OpenlayersPluginLayerType(
            self.iface, self.setReferenceLayer, self._olLayerTypeRegistry)

        self.pluginLayerRegistry.addPluginLayerType(
            self.pluginLayerType)

        QgsProject.instance().readProject.connect(self.projectLoaded)
        QgsProject.instance().projectSaved.connect(self.projectSaved)

    def unload(self):
        self.iface.webMenu().removeAction(self._olMenu.menuAction())

        self.olOverview.setVisible(False)
        del self.olOverview

        # Unregister plugin layer type
        self.pluginLayerRegistry.removePluginLayerType(
            OpenlayersLayer.LAYER_TYPE)

        QgsProject.instance().readProject.disconnect(self.projectLoaded)
        QgsProject.instance().projectSaved.disconnect(self.projectSaved)

    def addLayer(self, layerType):
        if layerType.hasXYZUrl():
            # create XYZ layer
            layer, url = self.createXYZLayer(layerType,
                                             layerType.displayName)
        else:
            # create OpenlayersLayer
            layer = OpenlayersLayer(self.iface, self._olLayerTypeRegistry)
            layer.setName(layerType.displayName)
            layer.setLayerType(layerType)

        if layer.isValid():
            coordRefSys = layerType.coordRefSys(self.canvasCrs())
            self.setMapCrs(coordRefSys)
            QgsProject.instance().addMapLayer(layer)

            # store xyz config into qgis settings
            if layerType.hasXYZUrl():
                settings = QSettings()
                settings.beginGroup('qgis/connections-xyz')
                settings.setValue("%s/authcfg" % (layer.name()), '')
                settings.setValue("%s/password" % (layer.name()), '')
                settings.setValue("%s/referer" % (layer.name()), '')
                settings.setValue("%s/url" % (layer.name()), url)
                settings.setValue("%s/username" % (layer.name()), '')
                # specify max/min or else only a picture of the map is saved
                # in settings
                settings.setValue("%s/zmax" % (layer.name()), '18')
                settings.setValue("%s/zmin" % (layer.name()), '0')
                settings.endGroup()
                # reload connections to update Browser Panel content
                self.iface.reloadConnections()

            self._ol_layers += [layer]

            # last added layer is new reference
            self.setReferenceLayer(layer)

            if not layerType.hasXYZUrl():
                msg = "Printing and rotating of Javascript API " \
                      "based layers is currently not supported!"
                self.iface.messageBar().pushMessage(
                    "OpenLayers Plugin", msg, level=Qgis.MessageLevel(1),
                    duration=5)

    def setReferenceLayer(self, layer):
        self.layer = layer

    def removeLayer(self, layerId):
        if self.layer is not None:
            if self.layer.id() == layerId:
                self.layer = None
            # TODO: switch to next available OpenLayers layer?

    def canvasCrs(self):
        mapCanvas = self.iface.mapCanvas()
        crs = mapCanvas.mapSettings().destinationCrs()
        return crs

    def setMapCrs(self, coordRefSys):
        mapCanvas = self.iface.mapCanvas()
        # On the fly
        canvasCrs = self.canvasCrs()
        if canvasCrs != coordRefSys:
            coordTrans = QgsCoordinateTransform(canvasCrs, coordRefSys,
                                                QgsProject.instance())
            extMap = mapCanvas.extent()
            extMap = coordTrans.transform(extMap, QgsCoordinateTransform.ForwardTransform)
            mapCanvas.setDestinationCrs(coordRefSys)
            mapCanvas.freeze(False)
            mapCanvas.setExtent(extMap)

    def projectLoaded(self):
        # replace old OpenlayersLayer with XYZ layer(OL plugin <= 1.3.6)
        rootGroup = self.iface.layerTreeView().layerTreeModel().rootGroup()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.PluginLayer and layer.pluginLayerType() == OpenlayersLayer.LAYER_TYPE:
                if layer.layerType.hasXYZUrl():
                    # replace layer
                    xyzLayer, url = self.createXYZLayer(layer.layerType,
                                                        layer.name())
                    if xyzLayer.isValid():
                        self.replaceLayer(rootGroup, layer, xyzLayer)

    def _hasOlLayer(self):
        for layer in QgsProject.instance().mapLayers().values():
            if layer.customProperty('ol_layer_type'):
                return True
        return False

    def _publicationInfo(self):
        cloud_info_off = QSettings().value("Plugin-OpenLayers/cloud_info_off",
                                           defaultValue=False, type=bool)
        day = 3600*24
        now = time.time()
        lastInfo = QSettings().value("Plugin-OpenLayers/cloud_info_ts",
                                     defaultValue=0.0, type=float)
        if lastInfo == 0.0:
            lastInfo = now-20*day  # Show first time after 10 days
            QSettings().setValue("Plugin-OpenLayers/cloud_info_ts", lastInfo)
        days = (now-lastInfo)/day
        if days >= 30 and not cloud_info_off:
            self.dlgAbout.tabWidget.setCurrentWidget(
                self.dlgAbout.tab_publishing)
            self.dlgAbout.show()
            QSettings().setValue("Plugin-OpenLayers/cloud_info_ts", now)

    def _publicationInfoClosed(self):
        QSettings().setValue("Plugin-OpenLayers/cloud_info_off",
                             self.dlgAbout.cb_publishing.isChecked())

    def projectSaved(self):
        if self._hasOlLayer():
            self._publicationInfo()

    def createXYZLayer(self, layerType, name):
        # create XYZ layer with tms url as uri
        provider = 'wms'
        url = "type=xyz&url=" + layerType.xyzUrlConfig()
        layer = QgsRasterLayer(url, name, provider,
                               QgsRasterLayer.LayerOptions())
        layer.setCustomProperty('ol_layer_type', layerType.layerTypeName)
        return layer, layerType.xyzUrlConfig()

    def replaceLayer(self, group, oldLayer, newLayer):
        index = 0
        for child in group.children():
            if QgsLayerTree.isLayer(child):
                if child.layerId() == oldLayer.id():
                    # insert new layer
                    QgsProject.instance().addMapLayer(newLayer, False)
                    newLayerNode = group.insertLayer(index, newLayer)
                    newLayerNode.setVisible(child.isVisible())

                    # remove old layer
                    QgsProject.instance().removeMapLayer(
                        oldLayer.id())

                    msg = "Updated layer '%s' from old \
                     OpenLayers Plugin version" % newLayer.name()
                    self.iface.messageBar().pushMessage(
                        "OpenLayers Plugin", msg, level=Qgis.MessageLevel(0))
                    QgsMessageLog.logMessage(
                        msg, "OpenLayers Plugin", QgsMessageLog.INFO)

                    # layer replaced
                    return True
            else:
                if self.replaceLayer(child, oldLayer, newLayer):
                    # layer replaced in child group
                    return True

            index += 1

        # layer not in this group
        return False

    def showGoogleMapsApiKeyDialog(self):
        apiKey = QSettings().value("Plugin-OpenLayers/googleMapsApiKey")
        newApiKey, ok = QInputDialog.getText(
            self.iface.mainWindow(), "API key",
            "Enter your Google Maps API key", QLineEdit.Normal, apiKey)
        if ok:
            QSettings().setValue("Plugin-OpenLayers/googleMapsApiKey",
                                 newApiKey)

    def showThunderforestApiKeyDialog(self):
        apiKey = QSettings().value("Plugin-OpenLayers/thunderforestApiKey")
        newApiKey, ok = QInputDialog.getText(
            self.iface.mainWindow(), "API key",
            "Enter your API key (<a href=\"https://thunderforest.com/pricing/\">https://thunderforest.com</a>)", QLineEdit.Normal, apiKey)
        if ok:
            QSettings().setValue("Plugin-OpenLayers/thunderforestApiKey",
                                 newApiKey)
