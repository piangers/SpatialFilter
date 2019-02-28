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
            
        # Save reference to the QGIS interface   
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BGTImport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        self.actions = []
        self.menu = self.tr(u'&Batch Vector Layer Saver')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BatchVectorLayerSaver')
        self.toolbar.setObjectName(u'SpatialFiler')

       
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BatchVectorLayerSaver', message)
        
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
       
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.coordinates = []
        icon_path = ':/plugins/SpatialFilter/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'SpatialFiler'),
            callback=self.initSignals,
            parent=self.iface.mainWindow())
            
        self.previousMapTool = self.iface.mapCanvas().mapTool()
        self.myMapTool = QgsMapToolEmitPoint( self.iface.mapCanvas() )
        self.isEditing = 0

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&SpatialFiler'),
                action)
            self.iface.removeToolBarIcon(self.action)
        # remove the toolbar
        del self.toolbar

    
    def initVariables(self):
        

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

        
       

    def initSignals(self):
        self.action.toggled.connect(self.RubberBand)
        self.myMapTool.canvasClicked.connect( self.mouseClick )

    def RubberBand(self, bolean):
        if bolean:
            self.myRubberBand = QgsRubberBand( self.iface.mapCanvas(), QGis.Polygon )
            color = QColor(78, 97, 114)
            color.setAlpha(190)
            self.myRubberBand.setColor(color)
            self.myRubberBand.setFillColor(QColor(255, 0, 0, 40))
            self.myRubberBand.setBorderColor(QColor(255, 0, 0, 200))
            
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
            self.myRubberBand.addPoint( QgsPointXY(currentPos) )
            self.coordinates.append( QgsPointXY(currentPos) )
            self.isEditing = 1
            
        elif clickedButton == Qt.RightButton and self.myRubberBand.numberOfVertices() > 2:
            self.isEditing = 0

            # create feature and set geometry.
                    
            poly = QgsFeature() 
            geomP = self.myRubberBand.asGeometry()
            poly.setGeometry(geomP)
            g=geomP.exportToWkt() # Get WKT coordenates.

            canvas=self.iface.mapCanvas()

            c = canvas.mapRenderer().destinationCrs().authid() # Get EPSG.
            rep = c.replace("EPSG:","") 

            vlyr = QgsVectorLayer("?query=SELECT geom_from_wkt('%s') as geometry&geometry=geometry:3:%s"%(g,rep), "Polygon_Reference", "virtual")
            
            QgsMapLayerRegistry.instance().addMapLayer(vlyr)

            self.myRubberBand.reset(QGis.Polygon)
 
            string = U"st_intersects(geom,st_geomfromewkt('SRID="+rep+";"+g+"'))"
             
            layers = self.iface.mapCanvas().layers()
            
            for layer in layers:
                try:
                    layer.setSubsetString(string)
                except Exception:
                    pass
            
            self.myRubberBand.reset(QGis.Polygon)
            self.disconnect()
            self.unChecked()

    def mouseMove( self, currentPos ):
        if self.isEditing == 1:
            self.myRubberBand.movePoint(QgsPointXY(currentPos))



		
	
