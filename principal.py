# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Principal                                  ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2009                                    ##
  ##                                             ##
    ###############################################

"""
"""

from __future__ import print_function

debuging = False
prefix = "    principal."

import logging

import locale
locale.setlocale(locale.LC_ALL, '')


import sys

from PyQt4 import QtCore, QtGui
import principal_ui

try:
    import agents
    import agentsFilters
except:
    pass

import about
# import imprimir


class Form(QtGui.QMainWindow):
    """ """

    @property
    def layoutZoom(self):
        """ """
        return float(self._screenGeometry.width()) / (5000 - self._screenGeometry.height()) * 4

    _castSelected = None
    def castSelected_get(self):
        """ """
        return self._castSelected
    def castSelected_set(self, value):
        """ """
        self._castSelected = value
    castSelected = property(castSelected_get, castSelected_set)


    _eventRouter = None
    @property
    def eventRouter(self):
        return self


    def status(self):
        """ """
        return self._status

    def setStatus(self, value):
        """ """
        self._status = value

    def __init__(self, *args, **kwds):
        """principal.Form.__init__()"""

        self.app = kwds.pop('app')

        QtGui.QMainWindow.__init__(self, *args)

        self.ui = principal_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self._screenGeometry = QtGui.QDesktopWidget().screenGeometry()

        self.setWindowTitle(QtGui.QApplication.translate("Admiros", self.app.name, None, QtGui.QApplication.UnicodeUTF8))
        self.setWindowIcon(QtGui.QIcon(":/icon.png"))

        self.setStatus('initializing...')



        # d = QtGui.QDateTimeEdit()
        # d.setDisplayFormat('dd MMM yyyy')
        
        # d.setDate(QtCore.QDate(2014,1,1))
        
        # print(d.textFromDateTime(QtCore.QDateTime(2014, 2,2, 3, 3)))
        

        # f=t



        ##---  HOLDER LOGO  ---
        pixmap = QtGui.QPixmap('logo.png')

        if pixmap.isNull():
            self.ui.holderLogoFR.hide()
        else:
            height = pixmap.size().height()
            if height > 50:
                height = 50

            self.ui.holderLogoLA.setPixmap(pixmap.scaledToHeight(height))

        self.ui.tabWidget.clear()
        self.ui.tabWidget.hide()

        self.ui.contentFR.hide()

        ## Acción Agregar
        self.aAgregar = QtGui.QAction("&Agregar", self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/Plus'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.aAgregar.setIcon(icon)
        self.connect(self.aAgregar, QtCore.SIGNAL("triggered()"), self.add)

        ## Acción Modificar
        self.aModificar = QtGui.QAction("Modificar", self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/Redo'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.aModificar.setIcon(icon)
        self.connect(self.aModificar, QtCore.SIGNAL("triggered()"), self.edit)

        ## Acción Eliminar
        self.aEliminar = QtGui.QAction("Eliminar", self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/Minus'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.aEliminar.setIcon(icon)
        self.connect(self.aEliminar, QtCore.SIGNAL("triggered()"), self.eliminar)

        ## Acción Mostrar detalles
        self.aMostrarDetalles = QtGui.QAction("Mostrar Detalles", self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/Magnifier'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.aMostrarDetalles.setIcon(icon)
        # self.connect(self.aMostrarDetalles, QtCore.SIGNAL("triggered()"), self.mostrarDetalles)
        self.connect(self.aMostrarDetalles, QtCore.SIGNAL("triggered()"), self.showDetails)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)

        ##---  AGENTS  ---
        if self.app.hasAgents:
            self.ui.agentsBU = QtGui.QPushButton(self.ui.tabsFR)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(4)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.agentsBU.sizePolicy().hasHeightForWidth())
            self.ui.agentsBU.setSizePolicy(sizePolicy)
            self.ui.agentsBU.setMinimumSize(QtCore.QSize(0, 30))
            self.ui.agentsBU.setStyleSheet("border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:1 solid #D0E0C0; border-top-left-radius:6px; border-top-right-radius:26px; color:#605040; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFCE8, stop:1 #F4ECC8); ")
            self.ui.agentsBU.setText("Agentes")
            self.connect(self.ui.agentsBU, QtCore.SIGNAL("clicked()"), self.agentsReview)

            ## TABLA DE CONSULTA DE AGENTES
            self.ui.agentsReviewTA = QtGui.QTableWidget(self.ui.mainSlider)
            self.ui.agentsReviewTA.setStyleSheet("background-color:#0000C8;")

            self.ui.agentsReviewTA.setFrameShape(QtGui.QFrame.NoFrame)
            self.ui.agentsReviewTA.setAlternatingRowColors(True)
            self.ui.agentsReviewTA.setShowGrid(False)
            self.ui.agentsReviewTA.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.ui.agentsReviewTA.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.ui.agentsReviewTA.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            self.ui.agentsReviewTA.setWordWrap(False)
            self.ui.agentsReviewTA.hide()

            labels = [u'Nombre', u'Teléfono', u'Fax', u'RFC', u'Lugar', u'Nacimiento']
            self.ui.agentsReviewTA.setColumnCount(len(labels))
            self.ui.agentsReviewTA.setHorizontalHeaderLabels(labels)

            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(1)
            sizePolicy.setHeightForWidth(self.ui.agentsReviewTA.sizePolicy().hasHeightForWidth())

            self.ui.agentsReviewTA.setSizePolicy(sizePolicy)
            self.ui.agentsReviewTA.hide()

            self.connect(self.ui.agentsReviewTA, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.mostrarMenu)
            self.connect(self.ui.agentsReviewTA, QtCore.SIGNAL("selectionChanged()"), self.agentSelected)
            self.connect(self.ui.agentsReviewTA, QtCore.SIGNAL("doubleClicked(QModelIndex)"), self.mostrarDetalles)

            self.agentsReviewMenu = QtGui.QMenu(self)
            self.agentsReviewMenu.addAction(self.aModificar)
            self.agentsReviewMenu.addAction(self.aMostrarDetalles)
            self.agentsReviewMenu.addAction(self.aEliminar)
            self.agentsReviewMenu.addAction(self.aAgregar)

            ## Agents Filters
            self.ui.agentsFiltersFR = agentsFilters.Form(self, app=self.app)
            self.connect(self, QtCore.SIGNAL('agentsFilterChanged(QString)'), self.agentsUpdate)

            ## Agent Select
            self.ui.agentSelectLYFR = QtGui.QFrame(self.ui.mainSlider)

            self.ui.agentSelectLYFRLY = QtGui.QHBoxLayout(self.ui.agentSelectLYFR)
            self.ui.agentSelectLYFRLY.setSpacing(0)
            self.ui.agentSelectLYFRLY.setContentsMargins(0, 0, 0, 6)

            self.ui.agentSelectSpacerFR = QtGui.QFrame(self.ui.agentSelectLYFR)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.agentSelectSpacerFR.sizePolicy().hasHeightForWidth())
            self.ui.agentSelectSpacerFR.setSizePolicy(sizePolicy)

            self.ui.agentSelectLYFRLY.addWidget(self.ui.agentSelectSpacerFR)

            self.ui.agentSelectFR = QtGui.QFrame(self.ui.agentSelectLYFR)
            # agentSelectFR.resize(401, 30)
            self.ui.agentSelectFR.setStyleSheet("QFrame{border:2 solid #FFC864; background-color:#FFFFFF; border-top-left-radius:5; border-bottom-left-radius:5; border-top-right-radius:3; border-bottom-right-radius:3;}")
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(2)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.agentSelectFR.sizePolicy().hasHeightForWidth())
            self.ui.agentSelectFR.setSizePolicy(sizePolicy)

            self.ui.agentSelectFRLY = QtGui.QHBoxLayout(self.ui.agentSelectFR)
            self.ui.agentSelectFRLY.setSpacing(0)
            # self.ui.agentSelectFRLY.setMargin(0)
            self.ui.agentSelectFRLY.setContentsMargins(2, 2, 2, 2)

            self.ui.agentLA = QtGui.QLabel(self.ui.agentSelectFR)

            self.ui.agentLA.setFont(font)

            self.ui.agentLA.setStyleSheet("color:#905008; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFCF0, stop:.3 #FFF098); border:0; border-top-left-radius: 3px; border-bottom-left-radius: 3px;")
            self.ui.agentLA.setMargin(6)
            self.ui.agentLA.setText("Agente")

            self.ui.agentSelectFRLY.addWidget(self.ui.agentLA)

            self.ui.agentCB = QtGui.QComboBox(self.ui.agentSelectFR)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.agentCB.sizePolicy().hasHeightForWidth())
            self.ui.agentCB.setSizePolicy(sizePolicy)
            self.ui.agentCB.setStyleSheet("color:#502000;")
            self.ui.agentCB.setFrame(False)

            font.setPointSize(12)

            self.ui.agentCB.setFont(font)
            # self.ui.agentCB.setContentsMargins(0,0,0,6)

            self.connect(self.ui.agentCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.filterAgentSelected)

            self.ui.agentSelectFRLY.addWidget(self.ui.agentCB)

            self.ui.agentSelectLYFRLY.addWidget(self.ui.agentSelectFR)

            self.ui.agentSelectSpacer2FR = QtGui.QFrame(self.ui.agentSelectLYFR)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(1)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.agentSelectSpacer2FR.sizePolicy().hasHeightForWidth())
            self.ui.agentSelectSpacer2FR.setSizePolicy(sizePolicy)

            self.ui.agentSelectLYFRLY.addWidget(self.ui.agentSelectSpacer2FR)

        ## TIPOS DE CAMBIO

        ## REPORTES

        if self.app.hasAgents:
            self.ui.mainSlider.addWidget(self.ui.agentsFiltersFR)

        # self.ui.mainSlider.addWidget(self.ui.taReviewClientes)
        # self.ui.pagesLY.insertWidget(2, self.ui.taReviewPolizas)
        # self.ui.mainSlider.addWidget(self.ui.taReviewSiniestros)
        # self.ui.mainSlider.addWidget(self.ui.newsTE)
        if self.app.hasAgents:
            self.ui.mainSlider.addWidget(self.ui.agentsReviewTA)
            self.ui.mainSlider.addWidget(self.ui.agentSelectLYFR)

        self.connect(self.ui.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.tabChanged)

        # self.ui.tabsLY.insertWidget(3, self.ui.newsBU)

        ## Botón Salir
        self.connect(self.ui.pbSalir, QtCore.SIGNAL("clicked()"), self.close)

        shClose = QtGui.QShortcut(QtGui.QKeySequence("Alt+c"), self)
        self.connect(shClose, QtCore.SIGNAL('activated()'), self.close)

        ## Boton Imprimir
        self.connect(self.ui.pbPrint, QtCore.SIGNAL("clicked()"), self.print_)

        shPrint = QtGui.QShortcut(QtGui.QKeySequence("Alt+i"), self)
        self.connect(shPrint, QtCore.SIGNAL('activated()'), self.print_)

        ## Botón Herramientas
        self.connect(self.ui.pbHerramientas, QtCore.SIGNAL("clicked()"), self.tools_show)

        shHerramientas = QtGui.QShortcut(QtGui.QKeySequence("Alt+h"), self)
        self.connect(shHerramientas, QtCore.SIGNAL('activated()'), self.tools_show)

        ## Boton Info
        self.connect(self.ui.pbInfo, QtCore.SIGNAL("clicked()"), self.about)

        ## Boton Agregar
        self.connect(self.ui.pbAgregar, QtCore.SIGNAL("clicked()"), self.add)

        ## Boton Modificar
        self.connect(self.ui.pbModificar, QtCore.SIGNAL("clicked()"), self.edit)

        ## Boton Eliminar
        self.connect(self.ui.pbEliminar, QtCore.SIGNAL("clicked()"), self.eliminar)

        self.connect(self, QtCore.SIGNAL('update(QString)'), self.update)
        # self.connect(self, QtCore.SIGNAL('renewPolicy(int)'), self.policyRenew)
        # self.connect(self, QtCore.SIGNAL('renewedHiddenChanged(int)'), self.updatePolizas)
        # self.connect(self, QtCore.SIGNAL('changedTabText(QWidget, QString)'), self.changeTabText)
        self.connect(self, QtCore.SIGNAL('changedTiposCambio()'), self.changedTiposCambio)
        self.connect(self, QtCore.SIGNAL('closeTab(QWidget, QString)'), self.closeTab)
        # self.connect(self, QtCore.SIGNAL('policiesChanged(int)'), self.policiesChanged)
        self.connect(self, QtCore.SIGNAL('sinistersChanged(int)'), self.sinistersChanged)
        self.connect(self, QtCore.SIGNAL('changedProtectionMode()'), self.changedProtectionMode)
        self.connect(self, QtCore.SIGNAL('updateDataStatus()'), self.updateDataStatus)

        if self.app.hasAgents:
            self.ui.tabsLY.insertWidget(3, self.ui.agentsBU)
            self.connect(self, QtCore.SIGNAL('agentsChanged(int)'), self.agentsChanged)

        self.widgets = {}
        self.reviews = {}

        self.tabButtons = {}

        self.stocks = {}
        
        self.info = ""

        self.setStatus('normal')

        # print  "principal.Form.__init__() -- end"


    def cast_add(self, module):
        # print("""principal.Form.cast_add()""")
        
        self.ui.mainSlider.addWidget(module.form)

        self.tabButtons[module.name] = QtGui.QPushButton(self.ui.tabsFR)
        self.tabButtons[module.name].setText(module.titles[1])
        self.tabButtons[module.name].name = module.name
        self.tabButtons[module.name].form = module.form

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabButtons[module.name].sizePolicy().hasHeightForWidth())
        self.tabButtons[module.name].setSizePolicy(sizePolicy)

        self.tabButtons[module.name].setMinimumSize(QtCore.QSize(0, 30))

        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.tabButtons[module.name].setFont(font)

        self.tabButtons[module.name].setStyleSheet("border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:0; border-top-left-radius:6px; border-top-right-radius:26px; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFFFF, stop:1 #FFFCEC); ")
        self.ui.tabsLY.insertWidget(0, self.tabButtons[module.name])

        self.connect(self.tabButtons[module.name], QtCore.SIGNAL("clicked()"), self.cast_show)

        self.cast_show(module.form)
        
        # print("""principal.Form.cast_add() - END""")


    def cast_show(self, form=None):
        """ """
        font0 = QtGui.QFont()
        font0.setPointSize(9)
        font0.setBold(False)

        font1 = QtGui.QFont()
        font1.setPointSize(11)
        font1.setBold(True)

        if not form:
            form = self.sender().form

        self.ui.mainSlider.showWidget(form)

        for name in self.tabButtons:
            # print(3221, name, self.tabButtons[name].form, form)
            if self.tabButtons[name].form == form:
                self.castSelected = name
                
                self.tabButtons[name].setStyleSheet("border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:0; border-top-left-radius:6px; border-top-right-radius:26px; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFFFF, stop:1 {});".format(self.tabButtons[name].form.style[0]))
                self.tabButtons[name].setFont(font1)
                self.ui.mainSlider.setStyleSheet("QFrame#mainSlider{{background-color:{}; border-left:1 solid #B0C0A0; border-right:1 solid #B0C0A0;}}".format(self.tabButtons[name].form.style[0]))
                if self.app.module[name].form.hasExtras:
                    self.app.module[name].form.extras.show()
            else:
                self.tabButtons[name].setStyleSheet("border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:1 solid #D0E0C0; border-top-left-radius:6px; border-top-right-radius:26px; color:#605040; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFCE8, stop:1 #F4ECC8);")
                self.tabButtons[name].setFont(font0)
                if self.app.module[name].form.hasExtras:
                    self.app.module[name].form.extras.hide()

        self.updateDataStatus()


    def restoreSize(self, size=None):
        # print("""principal.Form.restoreSize()""")
        try:
            if size:
                center = QtCore.QSize(self.app.desktop().screenGeometry().width()/2, self.app.desktop().screenGeometry().height()/2)

                self.setGeometry(center.width()-size.width()/2, center.height()-size.height()/2, size.width(), size.height())

                # print type(self.app.desktop().screenGeometry())
                # geometry = size
                # self.setGeometry(geometry.width()/2-*.15, geometry.height()*.15, geometry.width()*.70, geometry.height()*.70)
            else:
                if self.frameState():
                    self.restoreGeometry(QtCore.QByteArray().fromBase64(self.frameState()))
                else:
                    geometry = self.app.desktop().screenGeometry()
                    self.setGeometry(geometry.width() * .15, geometry.height() * .15, geometry.width() * .70, geometry.height() * .70)
                    self.frameState_set(self.windowState() ^ QtCore.Qt.WindowMaximized)
        except:
            raise
        
        # print("""principal.Form.restoreSize() - END""")


    def about(self):
        form = about.Form(u'Información del sistema', app=self.app)
        form.exec_()


    def add(self, cast=None):
        """principal.Form.add(what={})""".format(cast)

        if not cast:
            cast = self.castSelected

        if cast == 'agentes':
            self.agentAdd()

        elif cast == "policy" or cast == "customer" or cast == "claim":
            key = '{}a'.format(cast[:2])

            ## Check if reviewForm exists
            if key not in self.reviews.keys():
                self.reviews[key] = self.app.module[cast].review()
                self.reviews[key].init()

            ## Check if reviewTab exists
            if self.ui.tabWidget.indexOf(self.reviews[key].form) < 0:
                """ Si no existe el tab en el tabwidget, se agrega """
                gender = 'aoo'['aeo'.index(self.app.module[cast].titles[0][-1:])]
                index = self.ui.tabWidget.addTab(self.reviews[key].form, u"{} nuev{}".format(self.app.module[cast].titles[0], gender))
                self.ui.tabWidget.setCurrentIndex(index)

            self.reviews[key].form.convert('add')

        """principal.Form.add() -- END"""


    def agentAdd(self):
        # print "principal.agentAdd()"
        if not u'aa' in self.widgets.keys():
            self.widgets['aa'] = agents.FormReview(app=self.app, mode=u'add')

        if self.ui.tabWidget.indexOf(self.widgets['aa']) < 0:
            index = self.ui.tabWidget.addTab(self.widgets['aa'], u"Agente nuevo")
            self.ui.tabWidget.setCurrentIndex(index)
        else:
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(self.widgets['pa']))


    def agentsChanged(self, *args):
        # print "principal.Form.agentsChanged()"
        self.update(u'agentes')


    def agentsLoad(self):
        # print "principal.Form.agentsLoad()"
        self.setStatus(u'clearing')
        self.ui.agentCB.clear()
        self.ui.agentCB.addItem('Todos', 0)
        agents = self.app.model.getMany('agents')
        for agent in agents:
            self.ui.agentCB.addItem('{} {}'.format(agent['names'], agent['names2']), agent['agent_id'])
        self.setStatus(u'normal')


    def agentsReview(self):
        self.toggle("agentes")


    def agentSelected(self):
        self.updateDataStatus()


    def filterAgentSelected(self):
        if self.status() == u'normal':
            self.update(self.selected())
            self.update('polizas')
            self.update('clientes')
            self.update('siniestros')


    def agentsUpdate(self, filter=None):
        # print "principal.Form.agentsUpdate(%s)" % filter
        if self.status() == u'normal':

            self.ui.agentsReviewTA.setSortingEnabled(False)
            self.ui.agentsReviewTA.setRowCount(0)

            if filter:
                agents = self.app.model.getMany("agents", filters={'nombres LIKE': "%s OR " % filter, 'apellidos LIKE': "%s OR " % filter, 'rfc LIKE': "%s OR " % filter}, order=['agent_id'])
            else:
                agents = self.app.model.getMany("agents", order=['agent_id'])

            for row, agent in enumerate(agents):
                self.ui.agentsReviewTA.insertRow(0)

                try:
                    col = 0
                    item = QtGui.QTableWidgetItem("%s %s" % (agent['names'], agent['names2']))
                    item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
                    item.setData(1000, QtCore.QVariant(agent['agent_id']))
                    self.ui.agentsReviewTA.setItem(0, 0, item)

                    col = 1
                    item = QtGui.QTableWidgetItem(agent['phone1'])
                    item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
                    self.ui.agentsReviewTA.setItem(0, 1, item)

                    col = 2
                    item = QtGui.QTableWidgetItem(agent['phone3'])
                    item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
                    self.ui.agentsReviewTA.setItem(0, 2, item)

                    col = 3
                    item = QtGui.QTableWidgetItem(agent['rfc'])
                    item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
                    self.ui.agentsReviewTA.setItem(0, 3, item)

                    col = 4
                    item = QtGui.QTableWidgetItem(agent['place'])
                    item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
                    self.ui.agentsReviewTA.setItem(0, 4, item)

                    col = 5

                    if agent['birthdate'] == '1990-01-01':
                        date = ''
                    else:
                        date = QtCore.QDate().fromString(agent['birthdate'], "yyyy-MM-dd").toString("dd MMM yyyy")
                    item = QtGui.QTableWidgetItem(date)
                    item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))
                    self.ui.agentsReviewTA.setItem(0, 5, item)

                except:
                    logging.getLogger('system').error((u"Form.agentsUpdate()").encode('utf8'))
                    logging.getLogger('system').error((u"    col %s" % col).encode('utf8'))
                    logging.getLogger('system').error(sys.exc_info())
                    logging.getLogger('system').error(sys.exc_info()[2])
                    try:
                        logging.getLogger('system').error(agent)
                    except:
                        logging.getLogger('system').error(sys.exc_info())

            self.ui.agentsReviewTA.resizeColumnToContents(0)
            self.ui.agentsReviewTA.horizontalHeader().setResizeMode(4, QtGui.QHeaderView.Stretch)
            self.ui.agentsReviewTA.horizontalHeader().setResizeMode(5, QtGui.QHeaderView.Stretch)

            self.ui.agentsReviewTA.setSortingEnabled(True)

            self.ui.agentsReviewTA.sortItems(0, QtCore.Qt.AscendingOrder)

            self.agentsLoad()


    def tabChanged(self):
        if self.ui.tabWidget.count()==0:
            self.ui.tabWidget.hide()
        elif self.ui.tabWidget.count()==1:
            self.ui.tabWidget.show()
            self.ui.tabWidget.tabBar().hide()
        else:
            self.ui.tabWidget.tabBar().show()

    def changedCurrentItemSiniestro(self, item0, item1):
        f=g
        if item0 and item1:
            if item0.row() != item1.row() and item0.row() == self.ui.taReviewSiniestros.editing:
                self.ui.taReviewSiniestros.editing = None
                for index in range(3):
                    item = self.ui.taReviewSiniestros.item(item0.row(), index)
                    item.setFlags(item.flags().__xor__(QtCore.Qt.ItemIsEditable))


    # def changeTabText(self, widget, text):
        # pass
        # self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(widget), text)



    def changedTiposCambio(self):
        self.update('polizas')

    def closeEvent(self, event):
        """ """
        self.frameState_set(self.saveGeometry().toBase64())


    def closeTab(self, widget, key):
        self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(widget))
        if key[:2] == 'po' or key[:2] == 'cu' or key[:2] == 'cl':
            controller = self.reviews.pop(unicode(key))
            del controller
        else:
            frame = self.widgets.pop(unicode(key))
            del frame
        self.updateDataStatus()


    def edit(self, key=None):
        # print("""principal.Form.edit()""")
        # print(self.castSelected)

        if self.castSelected == "siniestros":
            if not self.ui.taReviewSiniestros.selectedIndexes():
                result = QtGui.QMessageBox.information(self, u"%s" % self.app.name, u"Seleccione el Siniestro que quiere MODIFICAR", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            else:
                siniestro_id = self.ui.taReviewSiniestros.selectedIndexes()[0].data(1000).toInt()[0]
                siniestro = self.app.model.get("siniestros", siniestro_id=siniestro_id)

                if not [x for x in range(self.ui.tabWidget.count()) if self.ui.tabWidget.tabText(x)==u'Modifica %s' % siniestro['clave']]:
                    if not u'se' in self.windows.keys():
                        self.widgets['se'] = siniestros.FormReview(app=self.app, mode=u'edit')
                        self.widgets['se'].setData(siniestro)
                    if self.ui.tabWidget.indexOf(self.widgets['se']) < 0:
                        index = self.ui.tabWidget.addTab(self.widgets['se'], u"Modifica %s" % siniestro['clave'])
                        self.ui.tabWidget.setCurrentIndex(index)


        if not key:
            
            if self.app.module[self.castSelected].form.hasSelection:
                
                id = self.app.module[self.castSelected].form.selectedId
                key = '{}{}'.format(self.castSelected[:2], id)
                ## Check if reviewForm exists
                if key not in self.reviews.keys():
                    
                    self.reviews[key] = self.app.module[self.castSelected].review(id=id)
                    self.reviews[key].init()
                    

                ## Check if reviewTab exists
                if self.ui.tabWidget.indexOf(self.reviews[key].form) < 0:
                    
                    self.reviews[key].form.setData(id=id)
                    
                    index = self.ui.tabWidget.addTab(self.reviews[key].form, self.reviews[key].form.tabText())
                    
                    self.ui.tabWidget.setCurrentIndex(index)
                    
            else:
                
                result = QtGui.QMessageBox.information(self, self.app.fullName, u"Seleccione la {} que quiere MODIFICAR".format(self.castSelected), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        
        self.reviews[key].form.convert('edit')

        if self.castSelected == "clientes":
            f=g
            if not self.ui.taReviewClientes.selectedIndexes():
                result = QtGui.QMessageBox.information(self, u"%s" % self.app.name, u"Seleccione el CLIENTE que quiere MODIFICAR", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            else:
                # cliente_id = self.ui.taReviewClientes.model().data(self.ui.taReviewClientes.model().index(self.ui.taReviewClientes.selectedIndexes()[0].row(), 0, QtCore.QModelIndex())).toInt()[0]
                cliente_id = self.ui.taReviewClientes.item(self.ui.taReviewClientes.currentRow(), 0).data(1000).toInt()[0]

                cliente = self.app.model.get("clientes", cliente_id=cliente_id)

                if not [x for x in range(self.ui.tabWidget.count()) if self.ui.tabWidget.tabText(x)==u"Modifica %s %s" % (cliente['nombres'], cliente['apellidos'])]:

                    if not u'ce' in self.widgets.keys():
                        self.widgets['ce'] = clientes.FormReview(app=self.app, mode=u'edit')

                    if self.ui.tabWidget.indexOf(self.widgets['ce']) < 0:
                        self.widgets['ce'].setData(cliente)
                        index = self.ui.tabWidget.addTab(self.widgets['ce'], u"Modifica %s %s" % (cliente['nombres'], cliente['apellidos']))
                        self.ui.tabWidget.setCurrentIndex(index)


        self.updateDataStatus()

        # print("""principal.Form.edit() - END""")


    def eliminar(self):

        module = self.app.module[self.castSelected]

        castName = module.titles[0]

        gender = 'aoo'['aeo'.index(module.titles[0][-1:])]

        if gender == u'a':
            article = u'la '
        elif gender == u'o':
            article = u'el '

        key = '{}{}'.format(module.name[:2], module.form.selectedId)

        idTitle = module.idTitle

        # SOLICITAR RECONSIDERACION
        result = QtGui.QMessageBox.warning(self, u"{} - Eliminar {}".format(self.app.name, castName), u"¿Realmente quieres ELIMINAR {}{} {}?".format(article, castName, idTitle), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if result == QtGui.QMessageBox.Yes:

            module.delete(module.form.selectedId)

            logging.getLogger('system').info((u"Eliminaste {}{} {}".format(article, castName, idTitle)).encode('utf8') )

            module.form.update()
            self.updateDataStatus()
            result = QtGui.QMessageBox.information(self, u"{} - Eliminar {}".format(self.app.name, castName), u"{}{} {} ha sido ELIMINAD{}".format(article, castName, idTitle, gender.upper()), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        return


    def form_add(self, widget):
        """principal.Form.form_add()"""
        ## Included for basiq compatibility
        pass


    def tools_set(self, form):
        if debuging: print("\n{}Form.tools_set()".format(prefix))
        
        self.ui.tools = form
        
        # self.container.addWidget(self.ui.tools)
        
        if not u'to' in self.widgets.keys():
            self.widgets['to'] = self.ui.tools        

        if debuging: print("{}Form.tools_set() - END\n".format(prefix))


    def tools_addForm(self, form, title):
        if debuging: print("\n{}Form.tools_addForm()".format(prefix))
        
        self.ui.tools.add(form, title)
        
        if debuging: print("{}Form.tools_addForm() - END".format(prefix))
        
        return


        exists = not not [x for x in range(self.ui.tools.ui.tabWidget.count()) if self.ui.tools.ui.tabWidget.tabText(x) == itemTitle]
        # exists = not not [x for x in range(self.options().ui.tabWidget.count()) if self.options().ui.tabWidget.tabText(x) == itemTitle]

        if not exists:
            # form.init()
            # self.options().ui.tabWidget.addTab(form, itemTitle)
            self.ui.tools.ui.tabWidget.addTab(form, itemTitle)



    def tools_show(self):
        """ """
        if u'to' not in self.widgets.keys():
            self.widgets['to'] = self.ui.tools        
            # print(self.ui.tools)
            
        if self.ui.tabWidget.indexOf(self.widgets['to']) < 0:
            index = self.ui.tabWidget.addTab(self.widgets['to'], self.widgets['to'].ui.title.text())
            self.ui.tabWidget.setCurrentIndex(index)
        else:
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(self.widgets['to']))
        return


    def init(self):
        """principal.Form.init()"""

        self.setStatus("pos initializing...")

        self.cnt = {}

        self.setStatus(u'normal')

        if self.app.hasAgents:
            self.update('agentes')

        # print  "principal.Form.init() -- end"


    def print_(self):
        """ """
        self.setCursor(QtCore.Qt.WaitCursor)

        if self.castSelected == "policy":
            self.app.module[self.castSelected].printList()

        elif self.castSelected == "claim":
            self.app.module[self.castSelected].printList()

        # self.ui.frReportes.loadReports()

        self.setCursor(QtCore.Qt.ArrowCursor)


    def showDetails(self):

        id = self.app.module[self.castSelected].form.selectedId
        key = '{}{}'.format(self.castSelected[:2], id)
        if key not in self.reviews.keys():
            self.reviews[key] = self.app.module[self.castSelected].review(id=id)
            self.reviews[key].init()
        
        tabIndex = self.ui.tabWidget.indexOf(self.reviews[key].form)

        if tabIndex < 0:

            self.reviews[key].form.setData(id=id)

            """ Si no existe el tab en el tabwidget, se agrega """
            tabIndex = self.ui.tabWidget.addTab(self.reviews[key].form, self.reviews[key].form.tabText())

        self.ui.tabWidget.setCurrentIndex(tabIndex)

        self.reviews[key].form.convert('view')


    def mostrarDetalles(self):
        """ """
        #~ print "principal.Form.mostrarDetalles()", self.selected()
        f=g
        ## Agents
        if self.selected() == "agentes":
            id = self.ui.agentsReviewTA.item(self.ui.agentsReviewTA.currentRow(), 0).data(1000).toInt()[0]

            agent = self.app.model.get("agents", agent_id=id)

            key = "c%s" % id

            if key not in self.widgets.keys():
                self.widgets[key] = agents.FormReview(app=self.app, mode=u'view')
                self.widgets[key].setData(agent)

            if self.ui.tabWidget.indexOf(self.widgets[key]) < 0:
                """ Si no existe el tab en el tabwidegt, se agrega """
                index = self.ui.tabWidget.addTab(self.widgets[key], "%s %s" % (agent['nombres'], agent['apellidos']))

                self.ui.tabWidget.setCurrentIndex(index)


        ## Pólizas
        elif self.selected() == "polizas":
            id = self.ui.taReviewPolizas.item(self.ui.taReviewPolizas.currentRow(), 0).data(1000).toInt()[0]
            if 'p{}'.format(id) not in self.reviews.keys():
                self.reviews['p{}'.format(id)] = polizas.instanceController(self, id=id, app=self.app)
                self.reviews['p{}'.format(id)].init()

            self.reviews['p{}'.format(id)].showDetails()

        ## CLIENTES
        elif self.selected() == "clientes":
            id = self.ui.taReviewClientes.item(self.ui.taReviewClientes.currentRow(), 0).data(1000).toInt()[0]

            cliente = self.app.model.get("clientes", cliente_id=id)

            key = "c%s" % id

            if key not in self.widgets.keys():
                self.widgets[key] = clientes.FormReview(app=self.app, mode=u'view')
                self.widgets[key].setData(cliente)

            if self.ui.tabWidget.indexOf(self.widgets[key]) < 0:
                """ Si no existe el tab en el tabwidegt, se agrega """
                index = self.ui.tabWidget.addTab(self.widgets[key], "%s %s" % (cliente['nombres'], cliente['apellidos']))

                self.ui.tabWidget.setCurrentIndex(index)


        ## SINIESTRO
        elif self.selected() == "siniestros":
            id = self.ui.taReviewSiniestros.item(self.ui.taReviewSiniestros.currentRow(), 0).data(1000).toInt()[0]

            siniestro = self.app.model.get("siniestros", siniestro_id=id)

            key = "s%s" % id

            if key not in self.widgets.keys():
                self.widgets[key] = siniestros.FormReview(app=self.app, mode=u'view')
                self.widgets[key].setData(siniestro)

            if self.ui.tabWidget.indexOf(self.widgets[key]) < 0:
                """ Si no existe el tab en el tabwidegt, se agrega """
                index = self.ui.tabWidget.addTab(self.widgets[key], "%s" % siniestro['clave'])

                self.ui.tabWidget.setCurrentIndex(index)


    def mostrarMenu(self, pos):
        if self.selected() == "agentes":
            pos = self.ui.agentsReviewTA.mapToGlobal(pos)
            self.agentsReviewMenu.popup(pos)

        elif self.selected() == "polizas":
            pos = self.ui.taReviewPolizas.mapToGlobal(pos)
            self.menuReviewPolizas.popup(pos)

        elif self.selected() == "clientes":
            pos = self.ui.taReviewClientes.mapToGlobal(pos)
            self.menuReviewClientes.popup(pos)


    def newsReview(self):
        self.toggle("mensajes")


    # def policiesChanged(self, *args):
        # f=g
        # self.update('polizas')



    def sinistersChanged(self, *args):
        self.update('siniestros')


    def reviewExists(self, text):
        ## Checks tabWidget, could check reviews dict too
        exists = [index for index in range(self.ui.tabWidget.count()) if self.ui.tabWidget.tabText(index) == text]
        return not not exists


    def changedProtectionMode(self):
         self.updateDataStatus()


    def toggle(self, what):
        # print "toggle('%s')" % what

        font0 = QtGui.QFont()
        font0.setPointSize(8)
        font0.setBold(False)

        font1 = QtGui.QFont()
        font1.setPointSize(11)
        font1.setBold(True)

        style0 = """border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:1 solid #D0E0C0; border-top-left-radius:6px; border-top-right-radius:26px; color:#605040; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFCE8, stop:1 #F4ECC8);"""

        style1 = """border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:0; border-top-left-radius:6px; border-top-right-radius:26px; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFFFF, stop:1 #FFFCEC);"""

        if self.app.hasAgents:
            self.ui.agentsBU.setFont(font0)
            self.ui.agentsBU.setStyleSheet(style0)
            self.ui.agentsFiltersFR.hide()
            self.ui.agentsReviewTA.hide()
            self.ui.agentSelectLYFR.show()

        self.ui.newsBU.setFont(font0)
        self.ui.newsBU.setStyleSheet(style0)
        self.ui.newsTE.hide()

        # self.ui.policiesBU.setFont(font0)
        # self.ui.policiesBU.setStyleSheet(style0)
        # self.ui.taReviewPolizas.hide()

        # self.ui.sinistersBU.setFont(font0)
        # self.ui.sinistersBU.setStyleSheet(style0)
        # self.ui.taReviewSiniestros.hide()

        # self.ui.paritiesBU.setFont(font0)
        # self.ui.paritiesBU.setStyleSheet(style0)

        self.setCursor(QtCore.Qt.WaitCursor)

        # self.ui.frReportes.hide()

        self.setSelected(what)

        if what == "agentes":
            self.ui.agentsBU.setFont(font1)
            self.ui.agentsBU.setStyleSheet("""border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:0; border-top-left-radius:6px; border-top-right-radius:26px; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFFFF, stop:1 #FFF098);""")
            self.ui.agentsReviewTA.show()
            self.ui.agentsFiltersFR.show()
            self.ui.pbEliminar.setText(u"Eliminar\nAgente")
            self.ui.pbModificar.setText(u"Modificar\nAgente")
            self.ui.pbAgregar.setText(u"Agregar\nAgente")
            self.ui.agentSelectLYFR.hide()

            self.ui.mainSlider.setStyleSheet("QFrame#mainSlider{background-color:#FFF098; border-left:1 solid #B0C0A0; border-right:1 solid #B0C0A0;};")

        elif what == "mensajes":
            self.ui.newsBU.setFont(font1)
            self.ui.newsBU.setStyleSheet("""border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:0; border-top-left-radius:6px; border-top-right-radius:26px; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFFFF, stop:1 #FAFFF4);""")
            self.ui.mainSlider.setStyleSheet("QFrame#mainSlider{background-color:#FAFFF4; border-left:1 solid #B0C0A0; border-right:1 solid #B0C0A0;}")
            self.ui.newsTE.show()
            text = unicode(open("{}\\admiros.log".format(self.app.appDataLocation), 'r').read(), 'utf8')
            text = text[text.find('>>'):].split('\n')
            text.reverse()
            text = '\n'.join(text)
            text = ''.join([x.replace('INFO', '').replace('>', '  ') for x in text.split('>>') if 'DEBUG' not in x and 'WARNING' not in x and 'CRITICAL' not in x and 'ERROR' not in x and not ('INFO' in x and 'refused' in x) and x != ''])
            self.ui.newsTE.setText(text)
            self.ui.pbEliminar.setText(u"Eliminar\nMensaje")
            self.ui.pbModificar.setText(u"Modificar\nMensaje")
            self.ui.pbAgregar.setText(u"Agregar\nMensaje")
            if self.app.hasAgents:
                self.ui.agentSelectLYFR.hide()

            '''
        elif what == "policies":
            self.app.controllers[what]

            # self.ui.rbPolizas.setFont(font1)
            self.ui.policiesBU.setFont(font1)
            self.ui.policiesBU.setStyleSheet("""border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:0; border-top-left-radius:6px; border-top-right-radius:26px; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFFFF, stop:1 #D0E0FF);""")
            self.ui.taReviewPolizas.show()
            self.ui.frReportes.show()
            self.ui.pbEliminar.setText(u"Eliminar\nPóliza")
            self.ui.pbModificar.setText(u"Modificar\nPóliza")
            self.ui.pbAgregar.setText(u"Agregar\nPóliza")

            self.ui.mainSlider.setStyleSheet("QFrame#mainSlider{background-color:#D0E0FF; border-left:1 solid #B0C0A0; border-right:1 solid #B0C0A0;}")

        elif what == "siniestros":
            self.ui.sinistersBU.setFont(font1)
            self.ui.sinistersBU.setStyleSheet("""border:1 solid #B0C0A0; border-top:1 solid #D0E0C0; border-bottom:0; border-top-left-radius:6px; border-top-right-radius:26px; background-color:qlineargradient(x1:0, y1:0, x2:0, y2:.3, stop:0 #FFFFFF, stop:1 #E4E0E0);""")
            self.ui.taReviewSiniestros.show()
            self.ui.pbEliminar.setText(u"Eliminar\nSiniestro")
            self.ui.pbModificar.setText(u"Modificar\nSiniestro")
            self.ui.pbAgregar.setText(u"Agregar\nSiniestro")

            self.ui.mainSlider.setStyleSheet("QFrame#mainSlider{background-color:#E4E0E0; border-left:1 solid #B0C0A0; border-right:1 solid #B0C0A0;}")
            '''

        self.updateDataStatus()

        self.setCursor(QtCore.Qt.ArrowCursor)


    def update(self, what):
        """principal.Form.update()"""
        if what == u'agentes':
            self.agentsUpdate()

        # if what == u'clientes':

            # self.updateClientes()

        # elif what == u'polizas':
            # f=g
            # self.app.module['policy'].updatePolizas()
            # self.updatePolizas()

        elif what == u'siniestros':
            self.updateSiniestros()




    def updateDataStatus(self):
        # print("principal.Form.updateDataStatus()")

        self.ui.pbAgregar.setEnabled(True)
        self.ui.pbAgregar.setToolTip(u"")
        self.aAgregar.setEnabled(True)

        self.ui.pbModificar.setEnabled(True)
        self.ui.pbModificar.setToolTip(u"")
        self.aModificar.setEnabled(True)

        self.ui.pbEliminar.show()
        self.ui.pbEliminar.setEnabled(True)
        self.ui.pbEliminar.setToolTip("")
        self.aEliminar.setEnabled(True)

        self.ui.pbPrint.show()
        self.ui.pbPrint.setEnabled(True)
        self.ui.pbPrint.setToolTip(QtGui.QApplication.translate("MainWindow", u"[Alt+i] Presione este botón y la lista que aparece en la consulta\nse guardará en un archivo pdf que además podrá imprimir.", None, QtGui.QApplication.UnicodeUTF8))

        if self.app.isProtected:
            self.ui.pbEliminar.setEnabled(False)
            self.ui.pbEliminar.setToolTip(u"Admiros está funcionando en modo protegido\nPuedes cambiar el modo en Herramientas")
            self.aEliminar.setEnabled(False)

            self.ui.pbModificar.setEnabled(False)
            self.ui.pbModificar.setToolTip(u"Admiros está funcionando en modo protegido\nPuedes cambiar el modo en Herramientas")
            self.aModificar.setEnabled(False)

        else:

            isEmpty = False
            hasSelection = False

            module = self.app.module[self.castSelected]

            if module.name == "policy" or module.name == "customer" or module.name == "claim":

                isEmpty = module.form.isEmpty
                hasSelection = module.form.hasSelection

                # if rowCount:
                    # if not self.ui.filtersFR.isEnabled():
                        # self.ui.pbPrint.setEnabled(False)
                        # self.ui.pbPrint.setToolTip(u"Listado vacío")

            elif self.castSelected == "agente":
                isEmpty = not self.ui.agentsReviewTA.rowCount()
                hasSelection = self.ui.agentsReviewTA.selectedIndexes()

            elif self.castSelected == "mensaje":
                isEmpty = True

            castName = module.titles[0]
            castNamePlural = module.titles[1]

            gender = 'aoo'['aeo'.index(castName[-1:])]

            if gender == u'a':
                article = u'la '
                numeral = u'una '
            elif gender == u'o':
                article = u'el '
                numeral = u'un '


            if isEmpty:
                self.ui.pbModificar.setEnabled(False)
                self.ui.pbModificar.setToolTip(u"No hay {} capturad{}s".format(castNamePlural, gender))
                self.aModificar.setEnabled(False)

                self.ui.pbEliminar.setEnabled(False)
                self.ui.pbEliminar.setToolTip(u"No hay {} capturad{}s".format(castNamePlural, gender))
                self.aEliminar.setEnabled(False)

                self.ui.pbPrint.setEnabled(False)
                self.ui.pbPrint.setToolTip(u"Listado vacío")

            elif not hasSelection:
                self.ui.pbModificar.setEnabled(False)
                self.ui.pbModificar.setToolTip(u"Selecciona {}{} que quieres modificar".format(article, castName))
                self.aModificar.setEnabled(False)

                self.ui.pbEliminar.setEnabled(False)
                self.ui.pbEliminar.setToolTip(u"Selecciona {}{} que quieres eliminar".format(article, castName))
                self.aEliminar.setEnabled(False)

            elif hasSelection:
                if '{}e'.format(module.name[:2]) in self.reviews.keys():
                    self.ui.pbModificar.setEnabled(False)
                    self.ui.pbModificar.setToolTip(u"Sólo puedes modificar {}{} a la vez".format(numeral, castName))
                    self.aModificar.setEnabled(False)
                    self.aModificar.setToolTip(u"Sólo puedes modificar {}{} la vez".format(numeral, castName))

                key = '{}{}'.format(module.name[:2], module.form.selectedId)

                # VALIDAR QUE NO ESTE EN USO EN OTRO LADO
                if self.reviewExists(key):
                    self.ui.pbEliminar.setEnabled(False)
                    self.ui.pbEliminar.setToolTip(u"{}{} seleccionad{} NO se puede ELIMINAR, porque está ocupad{} en otro proceso".format(article, castName, gender, gender))
                    self.aEliminar.setEnabled(False)
                    self.aEliminar.setToolTip(u"{}{} seleccionad{} NO se puede ELIMINAR, porque está ocupad{} en otro proceso".format(article, castName, gender, gender))

                # VALIDAR EL ESTADO DE LA INSTANCIA
                elif not module.selectionIsErasable():
                    self.ui.pbEliminar.setEnabled(False)
                    self.ui.pbEliminar.setToolTip(u"{}{} seleccionad{} NO se puede ELIMINAR, porque está VIGENTE".format(article, castName, gender))
                    self.aEliminar.setEnabled(False)
                    self.aEliminar.setToolTip(u"{}{} seleccionad{} NO se puede ELIMINAR, porque está VIGENTE".format(article, castName, gender))
                    
        # print("principal.Form.updateDataStatus() - END")


    def frameState(self):
        # print("""principal.Form.frameState()""")
        # print("""    """, self.app.config.pull('layout', 'windowState'))
        return self.app.config.pull('layout', 'windowState')

    def frameState_set(self, value):
        # print("""principal.Form.frameState_set()""")
        # print("""    """, value)
        self.app.config.push('layout', 'windowstate', value)





if __name__ == "__main__":
    print ("principal.py has no test routine")


'''
  Interactions

  Customers change    Update:     Policy's Customers ComboBox
                                Sinister's Customers ComboBox

  Policies change     Update:     Sinister's policies ComboBox

  Sinisters change    Update:

'''