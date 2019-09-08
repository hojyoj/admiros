# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Interfases de manejo de pólizas            ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2008                                    ##
  ##                                             ##
    ###############################################

"""
"""

# import logging
# logger = logging.getLogger("reportes")


from PyQt4 import QtCore, QtGui

import agentsFilters_ui





class Form(QtGui.QFrame):

    @property
    def eventRouter(self):
        return self._app.form


    def status(self):
        return self._status

    def setStatus(self, value):
        self._status = value


    def __init__(self, *args, **kwds):

        self._app = kwds.pop('app')


        QtGui.QFrame.__init__(self, *args)


        self.ui = agentsFilters_ui.Ui_Frame()
        self.ui.setupUi(self)

        self.setStatus('initializing...')

        #~ self.ui.filterED.setInputMask(">")
        #~ self.ui.filterED.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Z][A-Z1-9_]+"), self))
        self.connect(self.ui.filterED, QtCore.SIGNAL('textEdited(QString)'), self.filterChanged)

        self.setStatus('normal')


    def filterChanged(self, text):
        pos = self.ui.filterED.cursorPosition()
        self.ui.filterED.setText(self.ui.filterED.text().toUpper())
        self.ui.filterED.setCursorPosition(pos)
        self.eventRouter.emit(QtCore.SIGNAL('agentsFilterChanged(QString)'), text)


