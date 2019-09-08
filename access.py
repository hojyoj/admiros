# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Access                                     ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2010                                    ##
  ##                                             ##
    ###############################################

"""
Contains the class that defines the dialog that captures the system authentication data.

"""

import logging

import sys
import datetime
from PyQt4 import QtCore, QtGui

import access_ui
import km



class Controller():

    __username = None
    @property
    def username(self):
        return self.__username


    def __init__(self, *args, **kwds):

        self._mode = kwds.pop('mode', u'Normal')

        self.app = args[0]

        kwds['cnt'] = self

        self.form = Form(**kwds)
        self.form.setMode(self.mode)

    # @property
    # def mainForm(self):
        # return self.form

    @property
    def mode(self):         ## Normal, Remoto, Recovery
        return self._mode

    def checkValidity(self, data):
        if self.app.model.connect(0, **data):
            self.__username = data['u']
            return self.__username is None

    def exec_(self):
        result = self.form.exec_()
        if result == QtGui.QDialog.Accepted:        # El usuario es valido
            self.form.destroy()
            return True


class Form(QtGui.QDialog):

    def __init__(self, *args, **kwds):

        self.app = kwds.pop('app')

        if args:
            self.__label = args[0]
        else:
            self.__label = u"Access"


        QtGui.QDialog.__init__(self)

        self.ui = access_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle(self.app.name)
        # self.setWindowIcon(QtGui.QIcon(":/logo.png"))

        self.ui.titleLB.setText(self.label)

        self.resize(325, 500)

        # self.ui.logoLB.setText("{}".format(self.app.mainForm.layoutZoom()))
        self.ui.logoLB.setStyleSheet("background-image:url(:/logo)")

        ## System Code
        self.ui.systemCodeLB.setText(QtGui.QApplication.translate("Dialog", "Clave del sistema", None, QtGui.QApplication.UnicodeUTF8))
        self.ui.systemCodeED.setText(u"")
        self.ui.systemCodeED.setMessagePrefix(u"System code")
        self.connect(self.ui.systemCodeED, QtCore.SIGNAL('textEdited(QString)'), self.updateStatus)

        ## Install Code
        self.ui.installCodeLB.setText(QtGui.QApplication.translate("Dialog", "Clave de instalación", None, QtGui.QApplication.UnicodeUTF8))
        self.ui.installCodeED.setSymbols('-')
        self.ui.installCodeED.setText(u"")
        self.ui.installCodeED.setMessagePrefix(u"Install code")
        self.connect(self.ui.installCodeED, QtCore.SIGNAL('textEdited(QString)'), self.updateStatus)

        ## Accept
        self.ui.acceptBU.setIconSize(QtCore.QSize(32,32))
        self.connect(self.ui.acceptBU, QtCore.SIGNAL('clicked()'), self.acceptClicked)

        ## Cancel
        self.ui.cancelBU.setIconSize(QtCore.QSize(32,32))
        self.connect(self.ui.cancelBU, QtCore.SIGNAL('clicked()'), self.cancel)

        self.setTabOrder(self.ui.systemCodeED, self.ui.installCodeED)
        self.setTabOrder(self.ui.installCodeED, self.ui.cancelBU)
        self.setTabOrder(self.ui.cancelBU, self.ui.acceptBU)

        self.status = 0
        self.tries = 3

        self.filename = ''

        self.updateStatus()

        self.ui.systemCodeED.setFocus()

        self.ui.systemCodeED.setText(km.encode(self.app.model.getAttribute(category='holder')['reference'], 2, datetime.datetime.today().strftime("%M%S")))

        self.ui.systemCodeED.selectAll()


    def acceptClicked(self):
        # print("""access.Form.acceptClicked()""")

        state = 11011

        self.tries -= 1

        try:
            if self.app.model.getAttribute(category=u'general', name=u'key'):
                state = 11013

                if self.app.model.getAttribute(category=u'general', name=u'key')['reference'] and datetime.datetime.strptime('{}'.format(self.app.model.getAttribute(category=u'general', name=u'key')['reference']), "%d%m%Y") + datetime.timedelta(days=30) > datetime.datetime.now():
                    state = 11015
                    # self.app.model.modificar('variables', {'valor2':unicode(self.ui.installCodeED.text())}, {'tipo':u'general', 'nombre':u'key'})
                    keyRec = self.app.model.getAttribute(category=u'general', name=u'key')
                    self.app.model.set('attributes', code=keyRec['code'], value=unicode(self.ui.installCodeED.text()))
                else:
                    state = 11017
                    # self.app.model.modificar('variables', {'referencia':datetime.datetime.now().strftime("%d%m%Y"), 'valor':unicode(self.ui.installCodeED.text())}, {'tipo':u'general', 'nombre':u'key'})
                    keyRec = self.app.model.getAttribute(category=u'general', name=u'key')
                    self.app.model.set('attributes', code=keyRec['code'], value=unicode(self.ui.installCodeED.text()), reference=datetime.datetime.now().strftime("%d%m%Y"))
            else:
                state = 11019
                # self.app.model.add("variables", {'referencia':datetime.datetime.now().strftime("%d%m%Y"), 'tipo':u'general', 'nombre':u'key', 'valor':unicode(self.ui.installCodeED.text())})
                self.app.model.set('attributes', category=u'general', name=u'key', value=unicode(self.ui.installCodeED.text()), reference=datetime.datetime.now().strftime("%d%m%Y"))

            if not self.app.model.locked():
                state = 11021
                # logging.getLogger('system').warning(u"access.Form.acceptClicked() - Install key accepted".encode('utf8'))
                logging.getLogger('system').warning(u"Install key accepted".encode('utf8'))
                self.accept()
                return
            else:
                state = 11023
                logging.getLogger('system').info((u"Install key refused : {}".format(self.ui.installCodeED.text()).encode('utf8')))

            if self.tries:
                result = QtGui.QMessageBox.information(self, u"{}".format(self.app.name), u"La clave no es válida, intente de nuevo", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            else:
                result = QtGui.QMessageBox.information(self, u"{}".format(self.app.name), u"Lo siento, llame al administrador para obtener una clave válida e intente de nuevo", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        except:
            raise
            logging.getLogger('system').error((u"access.Form.acceptClicked() - {}".format(sys.exc_info()[1])).encode('utf8'))
            self.tries = 0

        if not self.tries:
            self.done(state)

        # print("""access.Form.acceptClicked() - END""")


    def cancel(self):
        self.reject()


    def isValid(self):
        valida = True
        self.mensajes = ""

        if not self.ui.systemCodeFR_layout.isHidden():
            if not self.ui.systemCodeED.isValid():
                valida = False
                self.mensajes += u"{}\n".format(self.ui.systemCodeED.message())

        if not self.ui.installCodeFR_layout.isHidden():
            # self.ui.passwordED.setExternalValidation(True, u"")
            if not self.ui.installCodeED.isValid():
                valida = False
                self.mensajes += u"{}\n".format(self.ui.installCodeED.message())
            # if not model.testPassword("%s" % self.ui.passwordED.text()):
                # valida = False
                # self.mensajes += u"La contraseña actual no es válida\n"
                # self.ui.passwordED.setExternalValidation(False, u"Esta no es la contraseña actual\n")

        self.mensajes.rstrip(u'\n')

        return valida


    @property
    def label(self):
        return self.__label


    def setData(self, *args):
        self.ui.installCodeED.setText(args[0])


    def updateStatus(self, *args):
        if self.isValid():
            self.ui.acceptBU.setEnabled(True)
            self.ui.acceptBU.setToolTip(u"")
        else:
            self.ui.acceptBU.setEnabled(False)
            self.ui.acceptBU.setToolTip(self.mensajes)

