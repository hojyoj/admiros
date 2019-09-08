# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Módulo holder                              ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2008                                    ##
  ##                                             ##
    ###############################################

"""
Contiene una clase que define la ventana de diálogo que captura los datos de
la empresa.
"""

from PyQt4 import QtCore, QtGui

import holder_ui


class Form(QtGui.QDialog):

    def mode(self):
        return self._mode

    def setMode(self, value):
        self._previousMode = self._mode
        self._mode = value


    def __init__(self, *args, **kwds):

        self.app = kwds.pop('app')
        self._mode = ""

        if args:
            label = args[0]
        else:
            label = u"Holder"


        QtGui.QDialog.__init__(self)


        self.ui = holder_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("%s" % self.app.name)
        # self.setWindowIcon(QtGui.QIcon(":/logo.png"))

        self.mensajes = u''

        self.ui.titleLA.setText(label)

        ## Nombre comercial
        self.ui.frNombreComercial_layout.hide()
        # self.ui.edNombreComercial.setEmptyAllowed(False)
        # self.connect(self.ui.edNombreComercial, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)

        ## Razón social
        self.ui.laRepresentante.hide()
        self.ui.edRazonSocial.setSymbols(" '.-")
        self.ui.edRazonSocial.setEmptyAllowed(False)
        self.connect(self.ui.edRazonSocial, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)

        ## Apellidos
        self.ui.edNombre2.setSymbols(" '-")

        self.connect(self.ui.edNombre2, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)

        ## RFC
        self.ui.edRFC.setEmptyAllowed(False)
        self.connect(self.ui.edRFC, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)

        ## Calle
        self.ui.edCalle.setEmptyAllowed(True)
        self.ui.edCalle.setSymbols(' #.,-')
        self.connect(self.ui.edCalle, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)

        ## Colonia
        self.ui.edColonia.setEmptyAllowed(True)
        self.ui.edColonia.setSymbols(' .')
        self.connect(self.ui.edColonia, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)

        ## Código postal
        self.ui.edCodigoPostal.setAllowedLengths(5, 5)
        self.ui.edCodigoPostal.setOnlyNumbers(True)
        self.ui.edCodigoPostal.setEmptyAllowed(True)
        self.ui.edCodigoPostal.setMessagePrefix(u"Codigo postal")
        self.connect(self.ui.edCodigoPostal, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)

        font = QtGui.QFont()
        font.setPointSize(9)
        font.setWeight(75)
        font.setBold(True)

        ## Lugar
        self.ui.cbLugar.lineEdit().setFont(font)
        self.ui.cbLugar.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.ui.cbLugar.setContentsMargins(3, 3, 3, 3)

        self.connect(self.ui.cbLugar, QtCore.SIGNAL('currentIndexChanged(int)'), self.lugarChanged)
        self.connect(self.ui.cbLugar, QtCore.SIGNAL('lostFocus()'), self.lugarLostFocus)
        self.loadPlaces()

        # completer = QtGui.QCompleter([], self.ui.edLugar)
        # completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # self.ui.edLugar.setCompleter(completer)
        # self.ui.edLugar.setEmptyAllowed(False)
        # self.ui.edLugar.setAllowedLengths(3, 25)
        # self.connect(self.ui.edLugar, QtCore.SIGNAL('downArrowPressed()'), self.muestraLugares)
        # self.connect(self.ui.edLugar, QtCore.SIGNAL('textEdited(QString)'), self.updateDataStatus)
        # self.connect(self.ui.edLugar, QtCore.SIGNAL('returnPressed()'), self.lugarCapturado)
        # self.connect(self.ui.edLugar.completer(), QtCore.SIGNAL('activated(QString)'), self.updateDataStatus)
        # self.cargaLugares()

        ## Aceptar
        self.ui.boAceptar.setIconSize(QtCore.QSize(32,32))
        self.ui.boAceptar.setText(u"&Aceptar")
        self.ui.boAceptar.setDefault(True)
        self.connect(self.ui.boAceptar, QtCore.SIGNAL('clicked()'), self.save)

        ## Cancelar
        self.ui.boCancelar.setIconSize(QtCore.QSize(32,32))
        self.connect(self.ui.boCancelar, QtCore.SIGNAL('clicked()'), self.cancel)

        self.updateDataStatus()

        self.ui.edNombreComercial.setFocus()

        self.setTabOrder(self.ui.edNombreComercial, self.ui.edRazonSocial)
        self.setTabOrder(self.ui.edRazonSocial, self.ui.edNombre2)
        self.setTabOrder(self.ui.edNombre2, self.ui.edRFC)
        self.setTabOrder(self.ui.edRFC, self.ui.edCalle)
        self.setTabOrder(self.ui.edCalle, self.ui.edColonia)
        self.setTabOrder(self.ui.edColonia, self.ui.edCodigoPostal)
        self.setTabOrder(self.ui.edCodigoPostal, self.ui.cbLugar)
        self.setTabOrder(self.ui.cbLugar, self.ui.boAceptar)


    def add(self):
        self.setMode('add')

        self.clear()

        self.updateDataStatus()

        self.ui.edNombreComercial.setFocus()    # Put at the end

        self.show()


    def cancel(self):
        self.reject()


    def loadPlaces(self):
        places = self.app.model.getMany("variables", {'tipo':u'lugar'}, order=('nombre',))
        self.ui.cbLugar.clear()
        for place in places:
            self.ui.cbLugar.addItem(place['nombre'], QtCore.QVariant(place['variable_id']))


    def clear(self):
        self.ui.edNombreComercial.clear()
        self.ui.edRazonSocial.clear()
        self.ui.edNombre2.clear()
        self.ui.edRFC.clear()
        self.ui.edCalle.clear()
        self.ui.edColonia.clear()
        self.ui.edCodigoPostal.clear()
        self.ui.cbLugar.setEditText("")


    def datos(self):
        datos = {}
        if self.mode() == 'modificar':
            datos['id'] = self.id

        datos['nombre'] = "%s %s" % (unicode(self.ui.edRazonSocial.text()), unicode(self.ui.edNombre2.text()))
        datos['referencia'] = unicode(self.ui.edRFC.text())

        datos['valor'] = "%s %s" % (unicode(self.ui.edCalle.text()), unicode(self.ui.edColonia.text()))

        datos['valor2'] = unicode(self.ui.cbLugar.currentText())

        datos['tipo'] = u'holder'

        return datos


    def isValid(self):
        valid = True
        self.mensajes = u""

        if self.ui.frNombreComercial_layout.isVisible():
            if not self.ui.edNombreComercial.isValid():
                valid = False
                self.mensajes += u"El nombre comercial %s\n" % self.ui.edNombreComercial.message()

        if not self.ui.edRazonSocial.isValid():
            valid = False
            self.mensajes += u"El nombre %s\n" % self.ui.edRazonSocial.message()

        if not self.ui.edNombre2.isValid():
            valid = False
            self.mensajes += u"El apellido %s\n" % self.ui.edNombre2.message()

        if self.ui.edNombre2.isEmpty():
            self.ui.edRFC.setPersonality(self.ui.edRFC.MORAL)
        else:
            self.ui.edRFC.setPersonality(self.ui.edRFC.FISICA)

        if not self.ui.edRFC.isValid():
            valid = False
            if self.ui.edRFC.isEmpty():
                self.mensajes += u"Falta el RFC\n"
            else:
                self.mensajes += u"Error en el RFC\n%s\n" % self.ui.edRFC.message()

        if not self.ui.edCalle.isValid():
            valid = False
            self.mensajes += u"La calle %s\n" % self.ui.edCalle.message()

        if not self.ui.edColonia.isValid():
            valid = False
            self.mensajes += u"La colonia %s\n" % self.ui.edColonia.message()

        if not self.ui.edCodigoPostal.isValid():
            valid = False
            self.mensajes += u"El código postal %s\n" % self.ui.edCodigoPostal.message()

        self.mensajes = self.mensajes.rstrip(u"\n")

        return valid



    def lugarChanged(self, index):
        self.updateDataStatus()


    def lugarLostFocus(self):
        self.ui.cbLugar.setCurrentIndex(self.ui.cbLugar.findText(self.ui.cbLugar.currentText(), QtCore.Qt.MatchStartsWith))


    def modifica(self, datos):
        self.clear()

        self.setMode('modificar')

        self.id = datos.id
        self.setDatos(datos)

        self.updateDataStatus()

        self.ui.edNombreComercial.setFocus()    # Put at the end

        self.show()


    def save(self):
        datos = self.datos()

        if self.mode() == 'add':
            self.app.model.add("variables", datos)

        elif self.mode() == 'modificar':
            self.app.model.modificar("variables", datos)

        QtGui.QDialog.accept(self)


    def setDatos(self, rol):
        self.ui.edNombreComercial.setText(rol.comentarios)
        self.ui.edRazonSocial.setText(rol.entidad.nombre)
        self.ui.edNombre2.setText(rol.entidad.nombre2)
        self.ui.edRFC.setText(rol.entidad.rfc)
        self.ui.edRFC.setTipo(rol.entidad.personalidad)

        if rol.direcciones:
            self.ui.edCalle.setText(rol.direcciones[0].calle)
            self.ui.edColonia.setText(rol.direcciones[0].areanominal)
            self.ui.edCodigoPostal.setText(rol.direcciones[0].areapostal)
            self.ui.cbLugar.setCurrentIndex(self.ui.cbLugar.findData(QtCore.QVariant(rol.direcciones[0].lugar.id)))


    def updateDataStatus(self):
        if self.isValid():
            self.ui.boAceptar.setEnabled(True)
        else:
            self.ui.boAceptar.setEnabled(False)
        self.ui.boAceptar.setToolTip(self.mensajes)


