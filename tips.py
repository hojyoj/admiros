# -*- coding: utf-8 -*-

 ##############################################
 ##                                            ##
 ##                     Tips                    ##
 ##                                             ##
 ##                                             ##
 ##              from Basiq Series              ##
 ##            by Críptidos Digitales           ##
 ##                 GPL (c)2008                 ##
  ##                                            ##
    ##############################################

""" Contiene la clase que define la ventana de diálogo que muestra los tips del sistema.
"""

from PyQt4 import QtCore, QtGui

import tips_ui



class Form(QtGui.QDialog):
    """ Contiene la gui y funcionalidad del diálogo de tips de la aplicación"""

    @property
    def currentIndex(self):
        return self.__currentIndex


    @property
    def eventRouter(self):
        return self.app.mainForm



    def __init__(self,  *args,  **kwds):

        self.app = kwds.pop('app')


        QtGui.QDialog.__init__(self,  *args)


        self.ui = tips_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle(u"%s - Tips" % self.app.name)
        self.setWindowIcon(QtGui.QIcon(":/logo.png"))

        self.ui.chMostrarTips.setChecked(self.app.tipsActive())
        self.connect(self.ui.chMostrarTips, QtCore.SIGNAL('stateChanged(int)'), self.toggleShowTips)

        self.connect(self.ui.boSiguiente, QtCore.SIGNAL('clicked()'), self.next)
        self.connect(self.ui.boAnterior, QtCore.SIGNAL('clicked()'), self.previous)
        self.connect(self.ui.boCerrar, QtCore.SIGNAL('clicked()'), self.exit)

#        try:
#            session.config.pull('layout', 'tipsWindowState')
#            self.restoreGeometry(QtCore.QByteArray().fromBase64(session.config.pull('layout', 'tipsWindowState')))
#        except:
#            geometry = app.screenGeometry
#            self.setGeometry(geometry.width() * .3, geometry.height() * .3, geometry.width() * .40, geometry.height() * .40)

        self.ui.stack.removeWidget(self.ui.stack.widget(0))

        font = QtGui.QFont()
        font.setFamily("Microsoft Sans Serif")
        font.setPointSize(9 * self.app.mainForm.layoutZoom)
        font.setWeight(75)
        font.setBold(True)

        font2 = QtGui.QFont()
        font2.setFamily("Microsoft Sans Serif")
        font2.setPointSize(8 * self.app.mainForm.layoutZoom)
        font2.setWeight(75)
        font2.setBold(True)


        textEdit = QtGui.QTextEdit()
        textEdit.setReadOnly(True)
        textEdit.setHtml(QtGui.QApplication.translate("Dialog", "<b>AL EJECUTAR EL SISTEMA POR PRIMERA VEZ</b><br><br>Puedes empezar a capturar pólizas directamente.<br><br>Podrás capturar datos de clientes sobre la marcha.<br><br>", None, QtGui.QApplication.UnicodeUTF8))
        self.ui.stack.addWidget(textEdit)

        textEdit = QtGui.QTextEdit()
        textEdit.setReadOnly(True)
        textEdit.setHtml(QtGui.QApplication.translate("Dialog", '<b>PERSONALIZA ADMIROS</b><br><br>Puedes mostrar tu logo en la ventana principal.<br><br>1. Copia la imagen al folder donde instalaste Admiros<br>&nbsp;&nbsp;&nbsp;&nbsp;normalmente es C:\Archivos de programa\Admiros<br>&nbsp;&nbsp;&nbsp;&nbsp;La imagen debe estar en formato PNG.<br><br>2. Cámbiale el nombre al archivo a "logo.png".<br><br>3. La próxima vez que abras Admiros verás tu logo.<br>', None, QtGui.QApplication.UnicodeUTF8))
        self.ui.stack.addWidget(textEdit)

        textEdit = QtGui.QTextEdit()
        textEdit.setReadOnly(True)
        textEdit.setHtml(QtGui.QApplication.translate("Dialog", '<b>RESPALDOS</b><br><br>El sistema realiza respaldos automáticamente cada semana.<br><br>Puedes cambiar el periodo a diario o mensual<br><br>1. Abre la ventana de herramientas<br>&nbsp;&nbsp;&nbsp;&nbsp;(presiona el icono <img src=":/Tools.png" width="24" /> en la barra inferior)<br><br>2. Presiona el botón Respaldos <img src=":/Recycle.png" width="24" /> en la barra superior.<br><br>3. En el recuadro inferior (Programación), haz clic en el periodo que prefieras.<br>', None, QtGui.QApplication.UnicodeUTF8))
        self.ui.stack.addWidget(textEdit)


        '''
        label = QtGui.QLabel(QtGui.QApplication.translate("Dialog", "AL EJECUTAR EL SISTEMA POR PRIMERA VEZ.\n\nInicie capturando los datos de los Proveedores .\n\n"
"Capture despues los datos de los productos (Vea la información para captura de Productos).\n"
"\n"
"Después podrá capturar Ordenes de compra y Compras, esto cargará existencias en el sistema.\n"
"\n"
"Ahora podrá capturar ventas, los datos de cliente se pueden capturar en ese momento, o si los tiene archivados los puede capturar antes en el sistema.", None, QtGui.QApplication.UnicodeUTF8))
        label.setStyleSheet("background-color:#FFFFFF;")
        label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        label.setWordWrap(True)
        label.setMargin(6)
        label.setFont(font)
        '''

        '''
        label = QtGui.QLabel(QtGui.QApplication.translate("Dialog", """CAPTURA DE PRODUCTOS\n\nEl código y nombre de producto que se captura son de uso interno.\n\nSi también desea usar el código y nombre de producto que usa el proveedor para las órdenes de compra y compras, puede capturar esos datos marcando el cuadrito que dice "Habilitar" en el recuadro que dice "Datos segun proveedor" en la ventana de captura de productos.\n\nCada producto tendrá los datos internos y podrá tener los datos de cada proveedor que tenga de ese mismo producto\n\nSi no desea usar los datos de proveedor, puede usar los datos internos solamente.""", None, QtGui.QApplication.UnicodeUTF8))
        label.setStyleSheet("background-color:#FFFFFF;")
        label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        label.setWordWrap(True)
        label.setMargin(6)
        label.setFont(font2)
        self.ui.stack.addWidget(label)



        label = QtGui.QLabel(QtGui.QApplication.translate("Dialog", """Los documentos que genera el sistema se guardan en el folder "Documentos" que se crea en el directorio de instalación del sistema.\n\nPuede cambiar esta ubicación en la seccion de Herramientas.\n""", None, QtGui.QApplication.UnicodeUTF8))
        label.setStyleSheet("background-color:#FFFFFF;")
        label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        label.setWordWrap(True)
        label.setMargin(6)
        label.setFont(font)
        self.ui.stack.addWidget(label)
        '''


        self.__currentIndex = 0
        self.ui.stack.setCurrentIndex(self.currentIndex)
        self.ui.laIndex.setText("%s/%s" % (self.currentIndex+1, self.ui.stack.count()))

        '''
        label = QtGui.QLabel(QtGui.QApplication.translate("Dialog", "VENTAS\n\n"
"El comprobante de venta puede cambiarse entre Factura y Remisión\n"
"\n"
"Por default, se debe capturar el dato de Pago, puede cambiar este comportamiento en el modulo Herramientas.\n"
"\n"
"\n"
"\n"
"", None, QtGui.QApplication.UnicodeUTF8))
        label.setStyleSheet("background-color:#FFFFFF;")
        label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        label.setWordWrap(True)
        label.setMargin(6)
        label.setFont(font)
        self.ui.stack.addWidget(label)

        label = QtGui.QLabel(QtGui.QApplication.translate("Dialog", "El botón Informacion proporciona tips de acuerdo a la actividad que se esté ejecutando.\n"
"\n"
"Sólo coloque el cursor sobre el botón, no lo presione.", None, QtGui.QApplication.UnicodeUTF8))
        label.setStyleSheet("background-color:#FFFFFF;")
        label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        label.setWordWrap(True)
        label.setMargin(6)
        label.setFont(font)
        self.ui.stack.addWidget(label)

        self.__currentIndex = 0
        self.ui.stack.setCurrentIndex(self.currentIndex)
        self.ui.laIndex.setText("%s/%s" % (self.currentIndex+1, self.ui.stack.count()))

        label = QtGui.QLabel(QtGui.QApplication.translate("Dialog", "Los botones se mostrarán deshabilitados cuando la acción que ejecutan no puede efectuarse porque los datos no están completos o están incorrectos.\n", None, QtGui.QApplication.UnicodeUTF8))
        label.setStyleSheet("background-color:#FFFFFF;")
        label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        label.setWordWrap(True)
        label.setMargin(6)
        label.setFont(font)
        self.ui.stack.addWidget(label)

        self.__currentIndex = 0
        self.ui.stack.setCurrentIndex(self.currentIndex)
        self.ui.laIndex.setText("%s/%s" % (self.currentIndex+1, self.ui.stack.count()))
        '''

#    def closeEvent(self, event):
#        session.config.push('layout', 'tipsWindowState', self.saveGeometry().toBase64())
#

    def exit(self):
        self.close()


    def previous(self):
        if self.currentIndex > 0:
            self.__currentIndex -= 1
        else:
            self.__currentIndex = self.ui.stack.count() - 1
        self.ui.stack.setCurrentIndex(self.currentIndex)
        self.ui.laIndex.setText("%s/%s" % (self.currentIndex+1, self.ui.stack.count()))


    def next(self):
        if self.currentIndex+2 > self.ui.stack.count():
            self.__currentIndex = 0
        else:
            self.__currentIndex += 1
        self.ui.stack.setCurrentIndex(self.currentIndex)
        self.ui.laIndex.setText("%s/%s" % (self.currentIndex+1, self.ui.stack.count()))


    def toggleShowTips(self, state):
        #~ print "tips.Form.toggleShowTips()", state
        if state == QtCore.Qt.Checked:
            value = u"1"
        else:
            value = u"0"
        attr = self.app.model.getAttribute(category=u'general', name=u'showTips')
        self.app.model.set('attributes', code=attr['code'], value=value)
        
        self.eventRouter.emit(QtCore.SIGNAL('showTipsChanged()'))

