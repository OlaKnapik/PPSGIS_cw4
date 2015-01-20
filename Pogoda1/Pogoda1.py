# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pogoda1
                                 A QGIS plugin
 pobieranie danych o pogodzie
                              -------------------
        begin                : 2015-01-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Knapsiu
        email                : lalala@op.pl
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,QVariant
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *
import resources_rc
from Pogoda1_dialog import Pogoda1Dialog
import os.path
import json, urllib
import time, calendar
from sgmllib import SGMLParser


class Pogoda1:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Pogoda1_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = Pogoda1Dialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pogoda1')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Pogoda1')
        self.toolbar.setObjectName(u'Pogoda1')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Pogoda1', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Pogoda1/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Pogoda1'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pogoda1'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
		
            #warstwa z wojewodztwami
			warstwa=os.path.join("c:/Users/Ola/.qgis2/python/plugins/Pogoda1/shapes/admin_region_teryt_woj.shp")
			woj=QgsVectorLayer(warstwa,"Wojewodztwa","ogr")
			woj.startEditing()
			
			#dodanie kolumn
			kolumny=["temp","t_max","t_min", "press","humi","w_speed","w_direc","cloud"]
			for i in kolumny:
				if woj.dataProvider().fieldNameIndex(i)==-1:
					woj.dataProvider().addAttributes([QgsField(i,QVariant.Double)])
			woj.updateFields()

			#dane
			dane_pogoda=os.path.join("c:/Users/Ola/.qgis2/python/plugins/Pogoda1/woj.json")

			link="http://api.openweathermap.org/data/2.5/group?units=metric&id="
			wojewodztwaID=[3337493,3337497,3337492,858790,3337495,858785,858787,3337498,3337500,3337494,858789,858791,3337499,3337496,3337495,858785,858787,858788,858786]
			
			for id in wojewodztwaID:
				link=link+str(wojewodztwaID)+","
			
			t_teraz=calendar.timegm(time.gmtime())
			
			try:
				plik=open(dane_pogoda,'r')
			except IOError:
				plik=open(dane_pogoda,'w+')
			dane=plik.read()
			plik.close()
			
			try:
				dane3=json.loads(dane)
				if 'data' in dane3:
					t_dane=dane3['data']
				else:
					t_dane=0
			except ValueError:
				t_dane=0
						
			if t_teraz-t_dane>60:
				plik2=open(dane_pogoda,'w+')
				odp=urllib.urlopen(link)
				dane2=json.loads(odp.read())
				odp.close()
				plik2.write(json.dumps(dane2,plik2))
				plik2.close()
			else:
				dane2=dane3
			
			#aktualizacja
			woj.startEditing()
			pogoda=dane2['list']
			wartosci2=[]
			for i in range(0,len(pogoda)):
				temp=pogoda[i]['main']['temp']
				temp_max=pogoda[i]['main']['temp_max']
				temp_min=pogoda[i]['main']['temp_min']
				cis=pogoda[i]['main']['pressure']
				wilg=pogoda[i]['main']['humidity']
				predkosc_w=pogoda[i]['wind']['speed']
				kier_w=pogoda[i]['wind']['deg']
				chmury=pogoda[i]['clouds']['all']
				wartosci=[temp, temp_max, temp_min, cis, wilg, predkosc_w, kier_w,chmury]
				wartosci2.append(wartosci)
			it=-1
			for element in woj.getFeatures():
				it=it+1
				for k in xrange(0, len(kolumny)):
						element.setAttribute(kolumny[k],wartosci2[it][k])
				woj.updateFeature(element)
			woj.commitChanges()
			QgsMapLayerRegistry.instance().addMapLayer(woj)	
			woj.updateExtents()
			pass
