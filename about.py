# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   About                                      ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2009                                    ##
  ##                                             ##
    ###############################################

"""
This module contents only the form that displays the information of the main application
Calls PyQt4 libraries and the pyuic4 generated module created with Qt's Designer
"""

from __future__ import print_function

from PyQt4 import QtGui

import access

import about_ui


class Form(QtGui.QDialog):
    """ Contiene la gui y funcionalidad del diálogo de información de la aplicación"""

    def __init__(self,  *args,  **kwds):

        self.app = kwds.pop('app')

        if args:
            label = args[0]
        else:
            label = u"Access"

        QtGui.QDialog.__init__(self)

        self.ui = about_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self.resize(400, 600)

        self.setWindowTitle(QtGui.QApplication.translate("Admiros", u"%s" % self.app.name, None, QtGui.QApplication.UnicodeUTF8))
        # self.setWindowIcon(QtGui.QIcon(":/logo.png"))

        self.ui.titleLA.setText(label)

        self.ui.logoLA.setText("")
        self.ui.logoLA.setStyleSheet("background-image:url(:/logo)")

        self.ui.versionLA.setText(u"v %s" % self.app.version)

        self.ui.infoLA.setText(QtGui.QApplication.translate("Dialog", self.app.description, None, QtGui.QApplication.UnicodeUTF8))

        self.ui.licenseLA.setText(u"(c) 2009-2012 Críptidos Digitales\nTodos los derechos reservados")

        self.ui.contributorsLA.hide()
        self.ui.contributor1LA.hide()
        self.ui.contributor2LA.hide()

        ## Key
        self.ui.keyFR.hide()

        self.ui.tabWidget.setCurrentIndex(0)


    def closeEvent(self, event):
        self.app.config.push('layout', 'aboutwindowstate', self.saveGeometry().toBase64())


    def setText(self, text):
        self.ui.infoLA.setText(text)


    def showKeyManager(self):
        accessForm = access.Form(u"Acceso al sistema", app=self.app)
        result = accessForm.exec_()

