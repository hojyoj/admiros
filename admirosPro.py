# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Administrador de Seguros Promotoría        ##
 ##   admirosPro                                 ##
 ##                                              ##
 ##                                              ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2012                                    ##
  ##                                             ##
    ###############################################

""" Control de Cartera para el Promotor de Seguros

    Manejo de compañías aseguradoras
    Manejo de agentes
    Manejo de clientes
    Manejo de pólizas
        Cálculo de monto y fechas de pago
    Manejo de siniestros
    Creación de reportes en pantalla y en archivo pdf, imprimibles por este
        medio

    Documentación.
    Este sistema no maneja gran variedad de datos, por lo que la interfase
        tiene diseño simplista, no se maneja un menú tradicional, las opciones
        disponibles son accesadas mediante botones mostrados estratégicamente,
        dando primera importancia a la intuitividad.
    Se busca accesibilidad de manera que los datos puedan ser llamados con un
        sólo gesto.
    Se busca pertinencia a la hora de mostrar los datos, de manera que se pueda
        tener visible los datos que se requieran para cualquier consulta sin
        tener que cambiar de ventanas.
    Esta filosofía puede generar confusión al principio en algunas opciones
        para usuarios de interfases tradicionales, para estos casos se incluye
        un ayudante que deseablemente eliminará cualquier duda que se tenga,
        es por esto que la documentación externa disponible es inexistente.
"""

__author__ = "Jorge Hojyo"
__copyright__ = "Copyright 2009, Críptidos Digitales"
__credits__ = ["Juan Algara", "Luis Fernando Castillo"]
__license__ = u"GPL (c) 2009"
__version__ = "1.0"
__maintainer__ = "Jorge Hojyo"
__email__ = "hojyoj@criptidosdigitales.com"

__status__ = "Release Candidate"


import logging
import logging.handlers

import errno, os, sys, shutil, ctypes

from decimal import Decimal
import db

from PyQt4 import QtCore, QtGui

import polizas

import utilities
import access
import principal
import holder
import tips


class MyApp(QtGui.QApplication):

    ## ( Internal error code, Error message, User error messsage, Exception )
    error = {'00000':('00000', u'No Error', u'', None),
             '01100':('01100', u'General Database Error', u'', None),
             '01111':('01111', u'Database is locked', u'', None)
            }

    _hasAgents = True
    import agents

    def __init__(self,  *args):

        QtGui.QApplication.__init__(self, *args)

        self.info = {'version':__version__, 'name':u'AdmirosPro', 'fullName':u'Administrador de Seguros Admiros Promotoría', 'title':u"AdmirosPro", 'author':__author__, 'company':u"Críptidos Digitales", 'license':__license__, 'alias':u"admirospro", 'about':"""AdmirosPro es el Control de Cartera\npara el Promotor de Seguros.\n\n\nEstá basado en la interfase "Clean Comfort"\ncuyas virtudes son\nSimplicidad y Comodidad de uso.\n\n\nSu uso es fácil y ágil gracias a\nlas indicaciones que se muestran oportunamente.\n\n\nContáctanos en dev@criptidosdigitales.com\n"""}

        self.initDataLocation()

        self.initLogging()

        self.initConfig()

        self.initDB()

        self.form = principal.Form(app=self)
        self.eventRouter = self.form

        self.setQuitOnLastWindowClosed(True)


    @property
    def hasAgents(self):
        return self._hasAgents


    def backup(self):
        # print "MyApp.backup()"
        date = QtCore.QDateTime().currentDateTime()
        dst = '{}\\CS__{}-{}-{}_{}{}{}'.format(self.appDataLocation, str(date.date().year()), str(date.date().month()).zfill(2), str(date.date().day()).zfill(2), str(date.time().hour()).zfill(2), str(date.time().minute()).zfill(2), str(date.time().second()).zfill(2))

        shutil.copyfile('{}\\CS'.format(self.appDataLocation), dst)

        self.model.modificar("variables", {'valor2':u'{}'.format(str(QtCore.QDate().currentDate().toString('yyyy-MM-dd')))}, {'tipo':u'general', 'nombre':u'programa'})

        self.eventRouter.emit(QtCore.SIGNAL('changedBackups()'))


    def init(self, splash=None):
        ## RESPALDO PROGRAMADO
        programa = self.model.get("variables", {'tipo':"general", 'nombre':"programa"})
        periodo = programa['valor']
        ultimo = programa['valor2'] 

        if periodo == 'mensual':
            if QtCore.QDate().fromString(ultimo, 'yyyy-MM-dd').addMonths(1) < QtCore.QDate().currentDate():
                self.backup()
        elif periodo == 'semanal':
            if QtCore.QDate().fromString(ultimo, 'yyyy-MM-dd').addDays(7) < QtCore.QDate().currentDate():
                self.backup()
        elif periodo == 'diario':
            if QtCore.QDate().fromString(ultimo, 'yyyy-MM-dd').addDays(1) < QtCore.QDate().currentDate():
                self.backup()

        ## CAMBIOS DE STATUS DE POLIZA POR FECHA
        splash.showMessage(u"Actualizando Status de pólizas", QtCore.Qt.AlignCenter)
        polizas.policiesStatus_update(self)

        self.form.init()


    def preInit(self, splash=None):
        # print "admiros.preInit()"
        if self.model.check():

            self.holder = self.model.get("variables", {'tipo':u'holder'})

            if not self.holder:
                holderX = holder.Form(u"Datos del Agente", app=self)
                holderX.add()

                splash.hide()
                result = holderX.exec_()
                splash.show()

                if result:
                    self.holder = self.model.get("variables", {'tipo':u'holder'})
                else:
                    return

            logging.getLogger('').removeHandler(self.emailLoggingHandler)
            self.emailLoggingHandler = logging.handlers.SMTPHandler('smtp.gmail.com', 'cdpublic01@gmail.com', ('hojyoj@gmail.com'), 'Error Report from {} {}'.format(self.info['name'], self.holder['nombre']), ('cdpublic01@gmail.com', 'cdpublic01'), ())
            self.emailLoggingHandler.setLevel(logging.ERROR)
            logging.getLogger('').addHandler(self.emailLoggingHandler)

            self.model.incRunCount()

            self.IVA = Decimal(self.model.get("variables", {'tipo':'general', 'nombre':'IVA'})['valor'])
            self.IVAOld = Decimal(self.model.get("variables", {'tipo':'general', 'nombre':'IVAOld'})['valor'])

            return True
        else:
            return False


    def initConfig(self):
        self.config = utilities.ConfigParser(filename="{}\\config.cfg".format(self.appDataLocation))


    def initDataLocation(self):
        ## Get App Data/Config folder
        if sys.platform == 'darwin':
            self.appDataLocation = os.path.expanduser(os.path.join("~", "Library", "Application Support", self.info['name']))
        elif sys.platform == 'win32':
            if os.environ.has_key('APPDATA'):
                self.appDataLocation = os.path.join(os.environ['APPDATA'], self.info['name'])
            elif os.environ.has_key('USERPROFILE'):
                self.appDataLocation = os.path.join(os.environ['USERPROFILE'], 'Application Data', self.info['name'])
            elif os.environ.has_key('HOMEDIR') and os.environ.has_key('HOMEPATH'):
                self.appDataLocation = os.path.join(os.environ['HOMEDIR'], os.environ['HOMEPATH'], self.info['name'])
            else:
                self.appDataLocation = os.path.join(os.path.expanduser("~"), self.info['name'])
        else:
            # pretty much has to be unix
            self.appDataLocation = os.path.expanduser(os.path.join("~", '.{}'.format(self.info['name'])))

        ## Get User data folder
        if sys.platform == 'darwin':
            pass
        elif sys.platform == 'win32':
            buffer = ctypes.create_unicode_buffer(300)
            ctypes.windll.shell32.SHGetFolderPathW(0, 0x0005, 0, 0, buffer)
            self.userDataLocation = buffer.value
        else:
            self.userDataLocation = os.path.expanduser('~')

        ## Create folder admirosPro in App Data/Config folder
        try:
            os.makedirs(self.appDataLocation)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise

        ## Create folder admirosPro in User Data/Config folder
        try:
            os.makedirs(self.userDataLocation)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise


    def initDB(self):
        self.model = db.Handler(app=self)


    def initLogging(self):
        ## Setting up general logging to admiros.log
        logging.basicConfig(filename='{}\\admiros.log'.format(self.appDataLocation), level=logging.INFO, format= ">>%(levelname)s>%(asctime)s>%(message)s", datefmt='%d-%b-%Y')

        ## Setting up general logging to stdout
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.WARNING)
        logging.getLogger('').addHandler(console)

        ## Setting up error logging to email
        self.emailLoggingHandler = logging.handlers.SMTPHandler('smtp.gmail.com', 'cdpublic01@gmail.com', ('hojyoj@gmail.com'), 'Error Report from {}{} {}'.format(self.info['name'], self.info['version'], 'holder unknown'), ('cdpublic01@gmail.com', 'cdpublic01'), ())
        self.emailLoggingHandler.setLevel(logging.ERROR)
        logging.getLogger('').addHandler(self.emailLoggingHandler)


    def showMessage(self, kind, line1, line2=''):
        if kind == 'INFO':
            QtGui.QMessageBox.information(self.form, u"{} - {}".format(self.info['name'], line1), u"{}".format(line2), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        elif kind == 'WARNING':
            QtGui.QMessageBox.warning(self.form, u"{} - {}".format(self.info['name'], line1), u"{}".format(line2), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        elif kind == 'ERROR':
            QtGui.QMessageBox.critical(self.form, u"{} - {}".format(self.info['name'], line1), u"{}".format(line2), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

            self.form.setCursor(QtCore.Qt.WaitCursor)
            logging.error(("{}".format(self.model.lastMessage())).encode('utf8'))
            self.form.setCursor(QtCore.Qt.ArrowCursor)


    def tipsActive(self):
        if not self.model.get('variables', {'tipo':u'general', 'nombre':u'showTips'}):
            self.model.set('variables', tipo=u'general', nombre=u'showTips', valor='1')
        return not not self.model.get('variables', {'tipo':u'general', 'nombre':u'showTips'})['valor']


    def updatePoliciesStatus(self):
        # print "MyApp.updatePoliciesStatus()"
        """ Busca cambios de status de pólizas
                de Pagada a Pendiente de Pago
                de Pagada a Impago
                de Pendiente de pago a expirada
            0: Pagada
            1: Pendiente de pago
            2: Renovada
            3: Expirada
            4: Cancelada
            5: No pagada
            # 6: Renovable
            # 7: Cotizacion
        """

        policies = self.app.model.getMany("polizas")

        #Status:
        pagada   = self.app.model.get("variables", {'tipo':'status', 'referencia':0})
        pendiente = self.app.model.get("variables", {'tipo':'status', 'referencia':1})
        renovada = self.app.model.get("variables", {'tipo':'status', 'referencia':2})
        expirada = self.app.model.get("variables", {'tipo':'status', 'referencia':3})
        cancelada = self.app.model.get("variables", {'tipo':'status', 'referencia':4})
        nopagada = self.app.model.get("variables", {'tipo':'status', 'referencia':5})

        fechaActual = QtCore.QDate().currentDate()

        for index, policy in enumerate(policies):

            if policy['status_id'] == pagada['referencia']:

                pagos = self.app.model.getMany("pagos", {'poliza_id':policy['poliza_id']}, order=('fecha',))
                found = False
                index = len(pagos)

                while not found and index:
                    index -= 1
                    pago = pagos[index]

                    fecha = QtCore.QDate().fromString(pago['fecha'], 'yyyy-MM-dd')

                    if fecha < fechaActual:

                        ## Sólo se checa el primer pago emitido en el pasado
                        if not pago['fecha2'] or pago['fecha2'] == u'2000-01-01':
                            if fecha <= fechaActual <= fecha.addDays(30):
                                self.app.model.modificar("polizas", {'status_id':pendiente['referencia']}, {'poliza_id':policy['poliza_id']})
                                logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], pagada['nombre'], pendiente['nombre'])).encode('utf8'))
                            elif fecha.addDays(30) < fechaActual:
                                self.app.model.modificar("polizas", {'status_id':nopagada['referencia']}, {'poliza_id':policy['poliza_id']})
                                logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], pagada['nombre'], nopagada['nombre'])).encode('utf8'))

                        found = True

                ## Si aun es PAGADA
                if policy['status_id'] == pagada['referencia']:
                    expiration = QtCore.QDate().fromString(policy['terminocobertura'], 'yyyy-MM-dd')
                    if 0 <= expiration.daysTo(fechaActual) <= 30:
                        self.app.model.modificar("polizas", {'status_id':expirada['referencia']}, {'poliza_id':policy['poliza_id']})
                        logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], pagada['nombre'], expirada['nombre'])).encode('utf8'))
                    elif 30 <= expiration.daysTo(fechaActual):
                        self.app.model.modificar("polizas", {'status_id':cancelada['referencia']}, {'poliza_id':policy['poliza_id']})
                        logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], pagada['nombre'], cancelada['nombre'])).encode('utf8'))

            # elif policy['status_id'] == expirada['referencia']:
                # expiration = QtCore.QDate().fromString(policy['terminocobertura'], 'yyyy-MM-dd')
                # if 30 <= expiration.daysTo(fechaActual):
                    # self.db.modificar("polizas", {'status_id':cancelada['referencia']}, {'poliza_id':policy['poliza_id']})
                    # logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], expirada['nombre'], cancelada['nombre'])).encode('utf8'))

            elif policy['status_id'] == pendiente['referencia']:

                pagos = self.app.model.getMany("pagos", {'poliza_id':policy['poliza_id']}, order=('fecha',))
                found = False
                index = len(pagos)
                while not found and index:
                    index -= 1
                    pago = pagos[index]
                    fecha = QtCore.QDate().fromString(pago['fecha'], 'yyyy-MM-dd')
                    if fecha < fechaActual:
                        if not pago['fecha2'] or pago['fecha2'] == u'2000-01-01':
                            if fecha.addDays(30) < fechaActual:
                                self.app.model.modificar("polizas", {'status_id':nopagada['referencia']}, {'poliza_id':policy['poliza_id']})
                                logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], pendiente['nombre'], nopagada['nombre'])).encode('utf8'))
                        found = True

            """
            elif policy['status_id'] == nopagada['referencia']:
                pagos = self.db.getMany("pagos", {'poliza_id':policy['poliza_id']}, order=('fecha',))
                found = False
                index = len(pagos)
                while not found and index:
                    index -= 1
                    pago = pagos[index]
                    fecha = QtCore.QDate().fromString(pago['fecha'], 'yyyy-MM-dd')
                    if fecha < fechaActual:
                        if not pago['fecha2'] or pago['fecha2'] == u'2000-01-01':
                            if fecha <= fechaActual <= fecha.addDays(30):
                                self.db.modificar("polizas", {'status_id':pendiente['referencia']}, {'poliza_id':policy['poliza_id']})
                                logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], nopagada['nombre'], pendiente['nombre'])).encode('utf8'))
                        else:
                            fecha2 = QtCore.QDate().fromString(pago['fecha2'], 'yyyy-MM-dd')
                            if fecha.addDays(-35) < fecha2 < fecha.addDays(35):
                                self.db.modificar("polizas", {'status_id':pagada['referencia']}, {'poliza_id':policy['poliza_id']})
                                logging.info((u"Póliza %s cambió de %s a %s" % (policy['folio'], nopagada['nombre'], pagada['nombre'])).encode('utf8'))
                        found = True
            """


if __name__ == "__main__":

    app = MyApp(sys.argv)

    print dir()
    f=g

    splash = QtGui.QSplashScreen(QtGui.QPixmap(":/logo.png"), QtCore.Qt.WindowStaysOnTopHint)
    splash.showMessage(u"Cargando {} {}".format(app.info['name'], app.info['version']), QtCore.Qt.AlignCenter)
    splash.show()

    app.processEvents()

    result = app.preInit(splash)

    app.form.show()

    app.processEvents()

    if result:

        if app.model.locked():

            splash.hide()

            resultQt = QtGui.QMessageBox.warning(None, u"%s - Acceso denegado" % app.info['name'], u"Probablemente la clave de instalación ha vencido\n\n¿Desea capturar una nueva Clave de instalación?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

            if resultQt == QtGui.QMessageBox.Yes:
                accessForm = access.Form(u"Acceso al sistema", app=app)
                result = accessForm.exec_()
                splash.show()
                logging.warning(u"Install key accepted".encode('utf8'))
            else:
                result = 0

        if result:
            if not app.model.locked():

                app.init(splash)

                splash.finish(None)

                # logging.info(u"Successful access".encode('utf8'))
                app.tips = tips.Form(app.form, app=app)
                if app.tipsActive():
                    app.tips.show()
                else:
                    app.tips.hide()

                app.form.ui.contentFR.show()
                app.form.restoreSize()

                result = app.exec_()
        else:
            splash.showMessage(u"Cerrando ...", QtCore.Qt.AlignCenter)
            splash.show()
            result = 1001
            logging.warning(u"Access intent failed".encode('utf8'))
            splash.finish(None)

    else:
        splash.hide()
        QtGui.QMessageBox.critical(app.form, u"{} - {}".format(app.info['name'], u"Error"), u"{}".format(u"Error al accesar la Base de Datos"), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        app.processEvents()
        splash.showMessage(u"Cerrando ...", QtCore.Qt.AlignCenter)
        splash.show()
        logging.error((u"{}".format(app.model.lastMessage())).encode('utf8'))
        splash.finish(None)

    sys.exit(result)


"""
CHANGELOG

1.3.0               Added backup capabilities
1.3.0               Added Event Display capabilities

1.3.0   2012 06 11  Added Agent Package [Disabled on standard version]

"""