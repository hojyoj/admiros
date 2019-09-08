# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Agent management interface                 ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2011                                    ##
  ##                                             ##
    ###############################################

"""
"""

from PyQt4 import QtCore, QtGui

import agentReview_ui




class FormReview(QtGui.QFrame):

    def mode(self):
        return self._mode

    def setMode(self, value):
        self._previousMode = self._mode
        self._mode = value

    @property
    def previousMode(self):
        return self._previousMode


    def editMessages(self):
        return self._editMessages

    def setEditMessages(self, value):
        self._editMessages = value


    def validityMessages(self):
        return self._validityMessages

    def setValidityMessages(self, value):
        self._validityMessages = value

    @property
    def owner(self):
        return self.app.form


    def status(self):
        return self._status

    def setStatus(self, value):
        self._status = value


    def __init__(self, *args, **kwds):

        self._previousMode = u''
        self._mode = kwds.pop('mode')

        self.app = kwds.pop('app')
        self.eventRouter = self.app.form

        QtGui.QFrame.__init__(self,  *args)

        self.ui = agentReview_ui.Ui_Frame()
        self.ui.setupUi(self)

        self.setStatus(u'initializing')

        font = QtGui.QFont()
        font.setPointSize(9)
        font.setWeight(75)
        font.setBold(True)

        self.ui.laGenerales.setOrientation(u'up')

        ## Nombre
        self.ui.nombreED.setEmptyAllowed(False)
        self.ui.nombreED.setSymbols(" '.,-")
        self.connect(self.ui.nombreED, QtCore.SIGNAL('textEdited(QString)'), self.updateStatus)

        ## Apellidos
        self.ui.apellidosED.setEmptyAllowed(True)
        self.ui.apellidosED.setSymbols(" '-")
        self.connect(self.ui.apellidosED, QtCore.SIGNAL('textEdited(QString)'), self.updateRfcStatus)

        ## RFC
        self.ui.rfcED.setEmptyAllowed(True)

        self.ui.rfcLA.setText("")
        self.connect(self.ui.rfcED, QtCore.SIGNAL('textEdited(QString)'), self.updateStatus)

        ## Fechas
        self.connect(self.ui.nacimientoDA, QtCore.SIGNAL('dateChanged(QDate)'), self.updateStatus)
        self.connect(self.ui.altaDA, QtCore.SIGNAL('dateChanged(QDate)'), self.updateStatus)

        # Familia
        # self.ui.laFamilia.setOrientation(u'up')

        ## Dirección
        self.ui.laDireccion.setOrientation(u'up')

        self.ui.calleED.setEmptyAllowed(True)
        self.ui.calleED.setSymbols(' #./')
        self.connect(self.ui.calleED, QtCore.SIGNAL(u'textChanged(QString)'), self.updateStatus)

        self.ui.coloniaED.setEmptyAllowed(True)
        self.ui.coloniaED.setSymbols(' .')
        self.connect(self.ui.coloniaED, QtCore.SIGNAL(u'textChanged(QString)'), self.updateStatus)

        self.ui.lugarCB.lineEdit().setFont(font)
        self.ui.lugarCB.completer().setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.connect(self.ui.lugarCB, QtCore.SIGNAL('currentIndexChanged(int)'), self.updateStatus)
        self.connect(self.ui.lugarCB, QtCore.SIGNAL('editTextChanged(QString)'), self.lugarEdited)
        self.connect(self.ui.lugarCB, QtCore.SIGNAL('lostFocus()'), self.lugarLostFocus)
        self.loadLugares()

        self.ui.codigoPostalED.setEmptyAllowed(True)
        self.ui.codigoPostalED.setAllowedLengths(5, 5)
        self.connect(self.ui.codigoPostalED, QtCore.SIGNAL(u'textChanged(QString)'), self.updateStatus)

        ## Contacto
        self.ui.laContacto.setOrientation(u'up')

        self.ui.telefonosED.setEmptyAllowed(True)
        self.ui.telefonosED.setSymbols(" ()-.,")
        self.connect(self.ui.telefonosED, QtCore.SIGNAL(u'textChanged(QString)'), self.updateStatus)

        self.ui.faxED.setEmptyAllowed(True)
        self.ui.faxED.setSymbols(" ()-.,")
        self.connect(self.ui.faxED, QtCore.SIGNAL(u'textChanged(QString)'), self.updateStatus)

        self.ui.emailED.setEmptyAllowed(True)
        self.ui.emailED.setSymbols(" @-_.")
        self.ui.emailED.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)"), self))
        self.connect(self.ui.emailED, QtCore.SIGNAL(u'textChanged(QString)'), self.updateStatus)

        ## Cancel
        self.ui.cancelBU.setText(u"Cancelar captura de Agente")
        self.connect(self.ui.cancelBU, QtCore.SIGNAL('clicked()'), self.cancel)

        ## Save
        self.ui.acceptBU.setText(u"Guardar datos de Agente")
        self.connect(self.ui.acceptBU, QtCore.SIGNAL('clicked()'), self.save)

        ## Close
        self.connect(self.ui.closeBU, QtCore.SIGNAL('clicked()'), self.close)

        ## Edit
        self.connect(self.ui.editBU, QtCore.SIGNAL('clicked()'), self.edit)

        self.connect(self.eventRouter, QtCore.SIGNAL('agentsChanged(int)'), self.reload)

        self.old = None

        self.setStatus(u'normal')

        self.convert(self.mode())


    def cancel(self):
        if self.previousMode != self.mode():
            self.setData(self.old)
            self.convert(self.previousMode)
            self.eventRouter.emit(QtCore.SIGNAL(u'changedTabText(QWidget, QString)'), self, self.oldTabText)
        else:
            if self.mode() == u'add':
                self.eventRouter.emit(QtCore.SIGNAL(u'closeTab(QWidget, QString)'), self, u'aa')
            elif self.mode() == u'edit':
                self.eventRouter.emit(QtCore.SIGNAL(u'closeTab(QWidget, QString)'), self, u'ae')


    def close(self):
        self.eventRouter.emit(QtCore.SIGNAL(u'closeTab(QWidget, QString)'), self, "a%s" % self.old['agent_id'])



    def clear(self):
        self.ui.nombreED.setText("", initialToo=True)
        self.ui.apellidosED.setText("", initialToo=True)
        self.ui.rfcED.setText("", initialToo=True)
        self.updateRfcStatus()
        self.ui.nacimientoDA.setDate(QtCore.QDate().fromString("1990-01-01", "yyyy-MM-dd"))
        self.ui.altaDA.setDate(QtCore.QDate().currentDate())
        self.ui.calleED.setText("", initialToo=True)
        self.ui.coloniaED.setText("", initialToo=True)
        self.ui.codigoPostalED.setText("", initialToo=True)
        self.ui.lugarCB.setCurrentIndex(-1)
        self.ui.telefonosED.setText("", initialToo=True)
        self.ui.faxED.setText("", initialToo=True)
        self.ui.emailED.setText("", initialToo=True)


    def convert(self, mode):
#        print "convert()", mode

        def editsSetVisible(value):
            self.ui.nameLabelLA.setVisible(value)
            self.ui.nombreED.setVisible(value)
            self.ui.name2LabelLA.setVisible(value)
            self.ui.apellidosED.setVisible(value)
            self.ui.rfcED.setVisible(value)
            self.ui.nacimientoDA.setVisible(value)
            self.ui.altaDA.setVisible(value)
            self.ui.calleED.setVisible(value)
            self.ui.coloniaED.setVisible(value)
            self.ui.lugarCB.setVisible(value)
            self.ui.codigoPostalED.setVisible(value)
            self.ui.telefonosED.setVisible(value)
            self.ui.faxED.setVisible(value)
            self.ui.emailED.setVisible(value)
            self.ui.buttonsFR_edit.setVisible(value)

        def labelsSetVisible(value):
            self.ui.nameLabelLA.setVisible(not value)
            self.ui.nombreLA.setVisible(value)
            self.ui.name2LabelLA.setVisible(not value)
            self.ui.apellidosLA.setVisible(value)
            self.ui.rfcLA.setVisible(value)
            self.ui.nacimientoLA.setVisible(value)
            self.ui.altaLA.setVisible(value)
            self.ui.calleLA.setVisible(value)
            self.ui.coloniaLA.setVisible(value)
            self.ui.lugarLA.setVisible(value)
            self.ui.codigoPostalLA.setVisible(value)
            self.ui.telefonosLA.setVisible(value)
            self.ui.faxLA.setVisible(value)
            self.ui.emailLA.setVisible(value)
            self.ui.buttonsFR_view.setVisible(value)

        if mode == u'add':
            self.setMode(mode)
            self.ui.title.setText(u'Agente Nuevo')

            self.clear()

            editsSetVisible(True)
            labelsSetVisible(False)

            self.updateStatus()

        elif mode == u'view':
            self.setMode(mode)

            self.ui.title.setText(u'Detalles de Agente')

            editsSetVisible(False)
            labelsSetVisible(True)

        elif mode == u'edit':
            self.setMode(mode)

            self.ui.title.setText(u'Modificación de Agente')

            editsSetVisible(True)
            labelsSetVisible(False)

            self.updateStatus()


    def edit(self):
#        print "agents.FormReview.edit()"

        index = [x for x in range(self.owner.ui.tabWidget.count()) if self.owner.ui.tabWidget.tabText(x)==u"Modifica %s %s" % (self.old['nombres'], self.old['apellidos'])]
        if not index:
            self.convert(u'edit')
            self.oldTabText = self.owner.ui.tabWidget.tabText(self.owner.ui.tabWidget.currentIndex())
            self.owner.emit(QtCore.SIGNAL(u'changedTabText(QWidget, QString)'), self, u"Modifica %s %s" % (self.old['nombres'], self.old['apellidos']))
        else:
            self.owner.ui.tabWidget.setCurrentIndex(index[0])


    def isValid(self):
#        print "agents.FormReview.isValid()"

        isValid = True
        messages = u""

        if not self.ui.nombreED.isValid():
            isValid = False
            if self.ui.nombreED.isEmpty():
                messages += u"Falta el nombre\n"
            else:
                messages += u"Error en el Nombre\n"

        if not self.ui.apellidosED.isValid():
            isValid = False
            messages += u"Error en los Apellidos\n"

        # if self.ui.apellidosED.isEmpty:
            # self.ui.rfcED.setTipo(self.ui.rfcED.MORAL)
        # else:
            # self.ui.rfcED.setTipo(self.ui.rfcED.FISICA)

        if self.ui.nacimientoDA.date() > self.ui.altaDA.date():
            isValid = False
            messages += u"La fecha de nacimiento debe ser menor a la de alta "

        if not self.ui.rfcED.isValid():
            isValid = False
            messages += u"Error en el RFC\n"

        if not self.ui.calleED.isValid():
            isValid = False
            messages += u"Error en la calle\n"

        if not self.ui.coloniaED.isValid():
            isValid = False
            messages += u"Error en la colonia\n"

        if not self.ui.codigoPostalED.isValid():
            isValid = False
            messages += u"El código postal %s\n" % self.ui.codigoPostalED.message()

        if not self.ui.telefonosED.isValid():
            isValid = False
            if self.ui.telefonosED.isEmpty():
                messages += u"Falta el teléfono\n"
            else:
                messages += u"Error en teléfonos\n"

        if not self.ui.emailED.isEmpty():
            if self.ui.emailED.validator().validate(self.ui.emailED.text(),0)[0] in [QtGui.QValidator.Invalid, QtGui.QValidator.Intermediate]:
                isValid = False
                messages += u"Error en el email"
                self.ui.emailED.setExternalValidation(False, u"Error en el email")
            else:
                self.ui.emailED.setExternalValidation(True, u"")

        self.setValidityMessages(messages.rstrip('\n'))

        return isValid


    def loadLugares(self):
        self.ui.lugarCB.clear()

        lugares = self.app.model.getMany(u'variables', {'tipo':u'lugar'})

        for lugar in lugares:
            self.ui.lugarCB.addItem(lugar['nombre'], QtCore.QVariant(lugar['variable_id']))


    def lugarEdited(self):
        if self.ui.lugarCB.findText(self.ui.lugarCB.currentText(), QtCore.Qt.MatchStartsWith) == -1:
            self.ui.lugarCB.setStyleSheet("color:#305010; background-color:#FFFF60; border:1 solid orange;")
        else:
            self.ui.lugarCB.setStyleSheet("color:#305010; background-color:#FFFFFF; border:1 solid orange;")
        self.updateStatus()


    def lugarLostFocus(self):
        if self.ui.lugarCB.findText(self.ui.lugarCB.currentText(), QtCore.Qt.MatchStartsWith) == -1:
            self.ui.lugarCB.setStyleSheet("color:#305010; background-color:#FFFF60; border:1 solid orange;")
        else:
            self.ui.lugarCB.setStyleSheet("color:#305010; background-color:#FFFFFF; border:1 solid orange;")
            self.ui.lugarCB.setCurrentIndex(self.ui.lugarCB.findText(self.ui.lugarCB.currentText(), QtCore.Qt.MatchStartsWith))
        self.updateStatus()


    def modifiedData(self):
        data = {}
        message = u""

        if self.ui.nombreED.isModified():
            data['names'] = unicode(self.ui.nombreED.text())
            message += u"Se cambió el nombre\n"

        if self.old:
            if self.ui.apellidosED.isModified():
                data['names2'] = unicode(self.ui.apellidosED.text())
                message += u"Apellidos modificados\n"

            if self.ui.rfcED.isModified():
                data['rfc'] = unicode(self.ui.rfcED.text())
                message += u"RFC modificado\n"

            if self.old['birthdate'] is not None:
                if self.old['birthdate'] != unicode(self.ui.nacimientoDA.date().toString("yyyy-MM-dd")):
                    data['birthdate'] = unicode(self.ui.nacimientoDA.date().toString("yyyy-MM-dd"))
                    message += u"Se cambió la fecha de nacimiento\n"

            if self.old['span'] is not None:
                if self.old['span'] != unicode(self.ui.altaDA.date().toString("yyyy-MM-dd")):
                    data['span'] = unicode(self.ui.altaDA.date().toString("yyyy-MM-dd"))
                    message += u"Se cambió la fecha de registro\n"

            if self.old['place'].lower() != unicode(self.ui.lugarCB.currentText()).lower():
                data['place'] = unicode(self.ui.lugarCB.currentText())
                message += u"Se cambió el lugar\n"

        else:
            data['names2'] = unicode(self.ui.apellidosED.text())

            data['birthdate'] = unicode(self.ui.nacimientoDA.date().toString("yyyy-MM-dd"))
            data['span'] = unicode(self.ui.altaDA.date().toString("yyyy-MM-dd"))

            data['rfc'] = unicode(self.ui.rfcED.text())

            data['place'] = unicode(self.ui.lugarCB.currentText())

        if self.ui.calleED.isModified():
            data['street'] = unicode(self.ui.calleED.text())
            message += u"Se cambió la calle\n"

        if self.ui.coloniaED.isModified():
            data['cityarea'] = unicode(self.ui.coloniaED.text())
            message += u"Se cambió la colonia\n"

        if self.ui.codigoPostalED.isModified():
            data['postcode'] = unicode(self.ui.codigoPostalED.text())
            message += u"Se cambió el código postal\n"

        if self.ui.telefonosED.isModified():
            data['phone1'] = unicode(self.ui.telefonosED.text())
            message += u"Se modificó el teléfono\n"

        if self.ui.faxED.isModified():
            data['phone3'] = unicode(self.ui.faxED.text())
            message += u"Se modificó el fax\n"

        if self.ui.emailED.isModified():
            data['email'] = unicode(self.ui.emailED.text())
            message += u"Se modificó el email\n"

        self.setEditMessages(message.rstrip('\n'))

        return data


    def reload(self, *args):
        print "agents.FormReview.reload()"
        if self.mode() == u'view':
            agent = self.app.model.get("agents", {'agent_id':self.old['agent_id']})
            self.setData(agent)


    def save(self):
        if self.mode() == "add":
            data = self.modifiedData()

            if 'place' in data.keys():
                place = self.app.model.get(u'variables', {'tipo':u'lugar', 'nombre':data['place']})
                if not place:
                    self.app.model.add(u'variables', {'tipo':u'lugar', 'nombre':data['place']})

            result = self.app.model.add("agents", data)

            id = self.app.model.get("agents", data)['agent_id']

            self.eventRouter.emit(QtCore.SIGNAL(u'agentsChanged(int)'), id)
            self.eventRouter.emit(QtCore.SIGNAL(u'closeTab(QWidget, QString)'), self, u'aa')

        elif self.mode() == "edit":
            data = self.modifiedData()

            if data != {}:
                result = self.app.model.modificar("agents", data, {'agent_id':self.old['agent_id']})

            if self.previousMode != self.mode():
                self.convert(self.previousMode)
                self.eventRouter.emit(QtCore.SIGNAL(u'changedTabText(QWidget, QString)'), self, self.oldTabText)
            else:
                self.eventRouter.emit(QtCore.SIGNAL(u'closeTab(QWidget, QString)'), self, u'ae')

            self.eventRouter.emit(QtCore.SIGNAL(u'agentsChanged(int)'), -1)


    def setData(self, data):
        print "agents.FormReview.setData()", data

        previousStatus = self.status()
        self.setStatus(u'settingData')

        self.old = data

        self.ui.nombreLA.setText(data['names'])
        self.ui.nombreED.setInitialText(data['names'], currentToo=True)

        self.ui.apellidosLA.setText(data['names2'])
        self.ui.apellidosED.setInitialText(data['names2'], currentToo=True)

        if data['rfc']:
            self.ui.rfcLA.setText(data['rfc'])
            self.ui.rfcED.setInitialText(data['rfc'], currentToo=True)
        else:
            self.ui.rfcLA.setText('')
            self.ui.rfcED.setInitialText('', currentToo=True)

        self.ui.nacimientoLA.setText(QtCore.QDate().fromString(data['birthdate'], "yyyy-MM-dd").toString('dd MMM yyyy'))
        if data['birthdate'] is not None:
            self.ui.nacimientoDA.setDate(QtCore.QDate().fromString(data['birthdate'], "yyyy-MM-dd"))
        self.ui.altaLA.setText(QtCore.QDate().fromString(data['span'], "yyyy-MM-dd").toString('dd MMM yyyy'))
        if data['span'] is not None:
            self.ui.altaDA.setDate(QtCore.QDate().fromString(data['span'], "yyyy-MM-dd"))

        if data['street'] is None:
            self.ui.calleLA.setText('')
            self.ui.calleED.setInitialText('', currentToo=True)
        else:
            self.ui.calleLA.setText(data['street'])
            self.ui.calleED.setInitialText(data['street'], currentToo=True)

        if data['cityarea'] is None:
            self.ui.coloniaLA.setText('')
            self.ui.coloniaED.setInitialText('', currentToo=True)
        else:
            self.ui.coloniaLA.setText(data['cityarea'])
            self.ui.coloniaED.setInitialText(data['cityarea'], currentToo=True)

        if data['postcode']:
            self.ui.codigoPostalLA.setText(data['postcode'])
            self.ui.codigoPostalED.setInitialText(data['postcode'], currentToo=True)
        else:
            self.ui.codigoPostalLA.setText(u'')
            self.ui.codigoPostalED.setInitialText(u'', currentToo=True)

        self.ui.lugarCB.setCurrentIndex(self.ui.lugarCB.findData(data['agent_id']))
        self.ui.lugarCB.setEditText(data['place'])
        self.ui.lugarLA.setText(self.ui.lugarCB.currentText())

        if data['phone1']:
            self.ui.telefonosLA.setText(data['phone1'])
            self.ui.telefonosED.setInitialText(data['phone1'], currentToo=True)
        else:
            self.ui.telefonosLA.setText('')
            self.ui.telefonosED.setInitialText('', currentToo=True)

        if data['phone3']:
            self.ui.faxLA.setText(data['phone3'])
            self.ui.faxED.setInitialText(data['phone3'], currentToo=True)
        else:
            self.ui.faxLA.setText(u'')
            self.ui.faxED.setInitialText(u'', currentToo=True)

        if data['email']:
            self.ui.emailLA.setText(data['email'])
            self.ui.emailED.setInitialText(data['email'], currentToo=True)
        else:
            self.ui.emailLA.setText(u'')
            self.ui.emailED.setInitialText(u'', currentToo=True)

        self.setStatus(previousStatus)

        self.updateStatus()


    def updateRfcStatus(self, *args):
        if self.ui.apellidosED.isEmpty():
            self.ui.rfcED.setPersonality(self.ui.rfcED.MORAL)
            # self.ui.familyFR_layout.setEnabled(False)
        else:
            self.ui.rfcED.setPersonality(self.ui.rfcED.FISICA)
            self.ui.spacerFR1.show()
            # self.ui.familyFR_layout.show()
            # self.ui.familyFR_layout.setEnabled(True)


    def updateStatus(self, *args):
#        print "agents.FormReview.updateStatus()", args
        if self.status() == u'normal':
            if self.isValid():
                if self.mode() == u'add':
                    self.ui.acceptBU.setEnabled(True)
                    self.ui.acceptBU.setToolTip(u"")
                elif self.mode() == u'edit':
                    if self.modifiedData():
                        self.ui.acceptBU.setEnabled(True)
                        self.ui.acceptBU.setToolTip(self.editMessages())
                    else:
                        self.ui.acceptBU.setEnabled(False)
                        self.ui.acceptBU.setToolTip(u" No hay cambios")
            else:
                self.ui.acceptBU.setEnabled(False)
                self.ui.acceptBU.setToolTip(self.validityMessages())


if __name__ == "__main__":
    print "agents.py has no test routine"
