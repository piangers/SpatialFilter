# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.gui import *
from qgis.core import *
from SpatialFilter import resources_rc  
import os


class SpatialFilter():
    

    def __init__(self, iface):
        self.iface = iface
		
    def initGui(self): 
		
        # cria uma ação que iniciará a configuração do plugin 
        
        self.initVariables()
        self.initSignals()
        
        
    def initVariables(self):
        self.coordinates = []

        # Criação da action e da toolbar

        self.toolbar = self.iface.addToolBar("Filtro Espacial")
        path = self.iface.mainWindow()
        icon_path = ':/plugins/SpatialFilter/icon.png'
        self.action = QAction (QIcon (icon_path),u"Filtra o espaco de aquisição.", path)
        self.action.setObjectName ("Spatial Filter.")
        self.action.setStatusTip(None)
        self.action.setWhatsThis(None)
        self.action.setCheckable(True)
        self.toolbar.addAction(self.action)

        self.previousMapTool = self.iface.mapCanvas().mapTool()
        self.myMapTool = QgsMapToolEmitPoint( self.iface.mapCanvas() )
        self.isEditing = 0
       

    def initSignals(self):
        self.action.toggled.connect(self.RubberBand)
        self.myMapTool.canvasClicked.connect( self.mouseClick )

    def RubberBand(self, bolean):
        if bolean:
            self.myRubberBand = QgsRubberBand( self.iface.mapCanvas(), QgsWkbTypes.PolygonGeometry )
            color = QColor(78, 97, 114)
            color.setAlpha(190)
            self.myRubberBand.setColor(color)
            self.myRubberBand.setFillColor(QColor(255, 0, 0, 40))
            #self.myRubberBand.setBorderColor(QColor(255, 0, 0, 200))
            
            # Set MapTool
            self.iface.mapCanvas().setMapTool( self.myMapTool )
            self.iface.mapCanvas().xyCoordinates.connect( self.mouseMove )
        else:
            self.disconnect()

    def disconnect(self):

        self.iface.mapCanvas().unsetMapTool(self.myMapTool)
        try:
            self.iface.mapCanvas().xyCoordinates.disconnect (self.mouseMove)
        except:
            pass

        try:
            self.myRubberBand.reset()
        except:
            pass

    def unChecked(self):
        self.action.setCheckable(False)
        self.action.setCheckable(True)

    def unload(self):
        self.disconnect()

    def mouseClick( self, currentPos, clickedButton ):
        if clickedButton == Qt.LeftButton:# and myRubberBand.numberOfVertices() == 0: 
            self.myRubberBand.addPoint( QgsPointXY(currentPos))
            self.coordinates.append( QgsPointXY(currentPos))
            self.isEditing = 1
            
        elif clickedButton == Qt.RightButton and self.myRubberBand.numberOfVertices() > 2:
            self.isEditing = 0

            # create feature and set geometry.
                    
            poly = QgsFeature() 
            geomP = self.myRubberBand.asGeometry()
            poly.setGeometry(geomP)
            g = geomP.asWkt() # Get WKT coordenates.

            canvas=self.iface.mapCanvas()

            c = canvas.mapSettings().destinationCrs().authid() # Get EPSG.
            rep = c.replace("EPSG:","")
  
            vlyr = QgsVectorLayer("?query=SELECT geom_from_wkt('%s') as geometry&geometry=geometry:3:%s"%(g,rep), "Polygon_Reference", "virtual")
            
            QgsProject.instance().addMapLayer(vlyr)

            self.myRubberBand.reset(QgsWkbTypes.PolygonGeometry)

            string = U"st_intersects(geom,st_geomfromewkt('SRID="+rep+";"+g+"'))"
            
            layers = self.iface.mapCanvas().layers()
            
            for layer in layers:
                try:
                    layer.setSubsetString(string)
                except Exception:
                    pass
            
            self.myRubberBand.reset(QgsWkbTypes.PolygonGeometry)
            self.disconnect()
            self.unChecked()

    def mouseMove( self, currentPos ):
        if self.isEditing == 1:
            self.myRubberBand.movePoint(QgsPointXY(currentPos))
