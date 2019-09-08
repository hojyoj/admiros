# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Administrador de Seguros                   ##
 ##   admiros                                    ##
 ##                                              ##
 ##                                              ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2009                                    ##
  ##                                             ##
    ###############################################

""" Control de Cartera para el vendedor de Seguros

    Manejo de   Compañías aseguradoras
                Clientes
                Pólizas
                    Cálculo de monto y fechas de pago
                Siniestros
    Creación de reportes en pantalla y en archivo pdf, imprimibles por
        este medio

    Documentación.
    Este sistema no maneja gran variedad de datos, por lo que la interfase
        tiene diseño simplista, no se maneja un menú tradicional, las
        opciones disponibles son accesadas mediante botones mostrados
        estratégicamente, dando primera importancia a la intuitividad.
    Se busca accesibilidad de manera que los datos puedan ser llamados con
        un sólo gesto.
    Se busca pertinencia a la hora de mostrar los datos, de manera que se
        pueda tener visible los datos que se requieran para cualquier
        consulta sin tener que cambiar de ventanas.
    Esta filosofía puede generar confusión al principio en algunas
        opciones para usuarios de interfases tradicionales, para estos
        casos se incluye un ayudante que deseablemente eliminará cualquier
        duda que se tenga, es por esto que no existe documentación externa.
"""

from __future__ import print_function

__appName__ = u"Admiros"
__alias__   = u"admiros"
__version__ = "1.4.13"
__license__ = u"GPL (c) 2009-2014"

__description__ = """Admiros es el Control de Cartera\npara el vendedor de Seguros.\n\n\nEstá basado en la interfase "Clean Comfort"\ncuyas virtudes son\nComodidad y Sencillez de uso.\n\n\nSu uso es fácil y ágil gracias a\nlas indicaciones que se muestran oportunamente.\n\n\nContáctanos en dev@criptidosdigitales.com\n"""
__author__  = "Jorge Hojyo"
__copyright__ = "Copyright 2009, Críptidos Digitales"
__credits__ = ["Juan Algara", "Luis Fernando Castillo"]
__maintainer__ = "Jorge Hojyo"
__email__   = "hojyoj@criptidosdigitales.com"

__status__  = "rc"

__fullName__ = u'Administrador de Seguros Admiros'
__company__  = u'Críptidos Digitales'

import ctypes
import errno
import os
import sys
import socket
import traceback
import shutil

from decimal import Decimal

import logging
import logging.handlers

import datetime

import ftplib

from PyQt4 import QtCore, QtGui

import db

from basiq import utilities
import access
import principal
import holder
import tips

import locale

## Required by py2exe
try:
    import basiq
    from basiq import sqlite
    import documents
    import persons
    import claim
    import customer
    import news
    import policy

    # import zipfile
    import cfd
except:
    pass


## STATE VALUES
IDLE, BUSY, BLOCKED = [100, 103, 105]



class App(QtGui.QApplication):

    ## ( Internal error code, Error message, User error messsage, Exception )
    errors = {'00000':('00000', u'No Error', u'', None),
             '01100':('01100', u'General Database Error', u'', None),
             '01111':('01111', u'Database is locked', u'', None)
            }

    def __init__(self, *args):
        # print("App.__init__()")
        
        self._state = [IDLE]
        self._error = []

        QtGui.QApplication.__init__(self, *args)

        self.state = BUSY

        self.initPaths()
        
        self.initLogging()


        ## ERRORS BEFORE THIS POINT CANNOT BE REPORTED
        ## Logging is required for reporting
        ## Paths are required for logging
        
        try:
            self.splash = QtGui.QSplashScreen(QtGui.QPixmap(":/splashLogo.png"), QtCore.Qt.WindowStaysOnTopHint)
            
            self.splash.show()
            
            self.initConfig()

            self.initDB()

            ## ---  Controller  -------
            self.mainForm = principal.Form(app=self)
            self.master = self.mainForm
            self.eventRouter = self.mainForm

            self.modules_load()

        except Exception as e:
            self.error = [e, sys.exc_info()[2]]

        self.setQuitOnLastWindowClosed(True)
        
        self.state_reset()

        # print("\nApp.__init__() - END")


    @property
    def alias(self):
        return __alias__

    @property
    def description(self):
        return __description__

    __license__ = __license__
    @property
    def license(self):
        return self.__license__

    __name__ = __appName__
    @property
    def name(self):
        return self.__name__


    def error_get(self):
        if self._error:
            return self._error[0]
        else:
            return None
    def error_set(self, value):
        self._error.append(value)
    error = property(error_get, error_set)

    def error_pull(self):
        if self._error:
            return self._error.pop(0)
        else:
            return None


    def state_get(self):
        return self._state[-1]
    def state_set(self, value):
        self._state.append(value)
    state = property(state_get, state_set)
    def state_reset(self):
        self._state.pop()


    _splash = None
    # def splash_isOK(self):
        # return not not self._splash
    def splash_get(self):
        return self._splash
    def splash_set(self, splash):
        self._splash = splash
    splash = property(splash_get, splash_set)

    def splash_show(self):
        if self._splash:
            self._splash.show()
    def splash_hide(self):
        if self._splash:
            self._splash.hide()

    _email = None
    def getEmail_isOK(self):
        return self._email == u'OK'
    def setEmail_isOK(self, value):
        if value:
            self._email = u'OK'
        else:
            self._email = u'error'
    email_isOK = property(getEmail_isOK, setEmail_isOK)


    _distribution = None        # Temporal, must implement BASIC/TALLER behaviour
    @property
    def distribution_isBasic(self):
        return True

    _hasAgents = False


    def init(self):
        # print("""\nApp.init()""")
        
        # self.master = self.mainForm
        
        ## RESPALDO PROGRAMADO
        programa = self.model.getAttribute(category="general", name="programa")
        periodo = programa['value']
        ultimo = programa['reference']

        if periodo == 'mensual':
            if QtCore.QDate().fromString(ultimo, 'yyyy-MM-dd').addMonths(1) < QtCore.QDate().currentDate():
                self.backup()
        elif periodo == 'semanal':
            if QtCore.QDate().fromString(ultimo, 'yyyy-MM-dd').addDays(7) < QtCore.QDate().currentDate():
                self.backup()
        elif periodo == 'diario':
            if QtCore.QDate().fromString(ultimo, 'yyyy-MM-dd').addDays(1) < QtCore.QDate().currentDate():
                self.backup()

        self.displayMessage(u"Inicializando ...")

        self.models_init()
        
        self.applyDefaults()
        
        self.modules_init()
        
        self.masters_init()
        
        # print("""App.init() - END""")


    def applyDefaults(self):
        # print("""App.applyDefaults()""")
        try:
            versionData = self.model.getAttribute(category='system', name='defaultsVersion')
            versionData['value'] = int(versionData['value'])
        except:
            print ("        Setting defaults data")
            versionData = {'code':30003, 'category':'system', 'name':'defaultsVersion', 'value':0}
            
        if versionData['value'] < 1:

            registros = [
                [u'documentKind',   u'default', u'13517']
                ]

            for registro in registros:
                data = {'category':registro[0], 'name':registro[1], 'value':registro[2]}
                attr = self.model.getAttribute(category=registro[0], name=registro[1])
                if attr:
                    data['code'] = attr['code']
                
                self.model.set('attributes', **data)
                
                
            ## HOLDER DATA
            holder = self.model.getAttribute(category='holder')
            
            personality = self.model.getAttribute(category='personality', name=u'física')
            
            address = {'street':u'Río Presidio Nte.', 'site_number':801, 'areaname':'Skally'}
            person = {'name':'Luis Fernando', 'name2':'Castillo Alvarez', 'rfc':'CAAL681029S8A', 'personality_code':personality['code']}
            
            rol = {'kind_code':30521, 'person':person, 'addresses':[address]}
            
            self.model.setRol(**rol)
            
            self.holder = self.model.getFullRol(kind_code=30521)
        

        versionData['value'] = 1
        self.model.set('attributes', **versionData)
        # print ("    admiros.applyDefaults        Applied version {}".format(versionData['value']))


        if versionData['value'] > 1:
            print (u"        LA VERSION DE LA CONFIGURACION DE DEFAULTS ES MÁS RECIENTE QUE LA REQUERIDA {{})\nTAL VEZ EL SISTEMA NO FUNCIONE ADECUADAMENTE".format(versionData['value']))
                
        # print("""App.applyDefaults() - END""")

    
    def systemMessages_check(self):
        for name in reversed([x[1] for x in sorted([(self.module[x].displayOrder, x) for x in self.module.keys()])]):
            try:
                self.module[name].systemMessages_check()
            except:
                ## Mmmm
                pass


    def masters_init(self):
        # print("""\n    App.masters_init()""")
        self.master.init()
        
        for name in self.module.keys():
            # print("""       """, name)
            self.module[name].master_init()
        # print("""    App.masters_init() - END""")
        

    def modules_load(self):
        # print("\n    App.modules_load()")
        
        self.module = {}
        
        for module in [
            {'name':'tools', 'capture_mode':2},
            {'name':'documents'},
            {'name':'persons', 'capture_mode':0},
            {'name':'policy'}, 
            {'name':'customer'}, 
            {'name':'claim'}, 
            {'name':'news'}, 
            {'name':'products', 'capture_mode':0}, 
            {'name':'cfd', 'capture_mode':2}
            ]:
            
            tmp = module.copy()
            name = tmp.pop('name')
            
            try:
                exec('import {}'.format(name))
            except:
                temp = sys.exc_info() 
                try:
                    exec('from basiq import {}'.format(name))
                except:
                    logging.getLogger('system').error(u"ERROR @ App.modules_load()\n    {}\n    {}".format(sys.exc_info()[1], temp[1]).encode('utf8'))
                    
                    raise
            
            subModules = tmp.pop('modules', [])
            
            if tmp:
                controller = eval('{}.Controller(self, self, modules=subModules, **tmp)'.format(name))
            else:
                try:
                    eval('{}'.format(name))
                    controller = eval('{}.Controller(self, self, modules=subModules)'.format(name))
                except:
                    print (sys.exc_info())
                    

            self.module[name] = controller
            
        # print("    App.modules_load() - END")


    def modules_init(self):
        # print("""\n    App.modules_init()""")
        
        for name in reversed([x[1] for x in sorted([(self.module[x].displayOrder, x) for x in self.module.keys()])]):
            # print("       ", name)
            self.module[name].init()
            
        # print("""\n    App.modules_init() - END""")


    def models_init(self):
        # print("""\n    App.models_init()""")
        # print(sorted([(self.module[x].initOrder, x) for x in self.module.keys()]))
        # for name in reversed([x[1] for x in sorted([(self.module[x].initOrder, x) for x in self.module.keys()])]):
        
        for name in [x[1] for x in sorted([(self.module[x].initOrder, x) for x in self.module.keys()])]:
            # print(432, name)
            self.module[name].model_init()
        # print("""    App.models_init() - END""")


    def displayMessage(self, message):
        # print("""App.displayMessage()""")
        if self.splash:
            # print(6667, message.encode('utf8'))
            self.splash.showMessage(message, QtCore.Qt.AlignCenter)
        # print("""App.displayMessage() - END""")


    def preInit(self):
        # print("""\nApp.preInit()""")

        self.splash.showMessage(u"Cargando {} {}".format(app.name, app.version), QtCore.Qt.AlignCenter)
        
        
        
        # self.splash.show()
        
        ## Data recovery not necessary in this version
        # utilities.arrangeData(self, 'CS', 'appData')
        
        #! Define Backup procedure when applying data recovery
        

        if not self.model.init():
            app.splash.hide()
            QtGui.QMessageBox.critical(app.mainForm, u"{} - {}".format(app.name, u"Error"), u"{}".format(u"Error al accesar la Base de Datos"), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            app.processEvents()
            return False
        else:
            
            self.model.incRunCount()

            # self.holder = self.model.getAttribute(category=u'holder')
            # self.holder = self.model.getFullRol(kind_code=30521)
            try:
                self.holder = self.model.getFullRol(kind_code=30521)
            except:
                self.holder = self.model.getAttribute(category=u'holder')
                

            if not self.holder:
                holderX = holder.Form(u"Datos del Agente", app=self)
                holderX.add()

                self.splash.hide()
                result = holderX.exec_()
                self.splash.show()

                if not result:
                    QtGui.QMessageBox.critical(app.mainForm, u"{} - {}".format(app.name, u"Error"), u"{}".format(u"Error al capturar Agente"), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return False
                else:
                    self.holder = self.model.getAttribute(category=u'holder')

            """
            logging.getLogger('').removeHandler(self.emailLoggingHandler)
            self.emailLoggingHandler = logging.handlers.SMTPHandler('smtp.gmail.com', 'cdpublic01@gmail.com', ('hojyoj@gmail.com'), 'Error Report from {} {}'.format(self.alias, self.holder['nombre']), ('cdpublic01@gmail.com', 'cdpublic01'), ())
            self.emailLoggingHandler.setLevel(logging.ERROR)
            logging.getLogger('').addHandler(self.emailLoggingHandler)
            """


            self.IVA = Decimal(self.model.getAttribute(category='general', name='IVA')['value'])
            self.IVAOld = Decimal(self.model.getAttribute(category='general', name='IVAOld')['value'])

        # print("""App.preInit() - END\n""")
        
        return True


    @property
    def hasAgents(self):
        return self._hasAgents


    def backup(self):
        # print "App.backup()"
        date = QtCore.QDateTime().currentDateTime()
        dst = '{}\\CS__{}-{}-{}_{}{}{}'.format(self.appDataLocation, str(date.date().year()), str(date.date().month()).zfill(2), str(date.date().day()).zfill(2), str(date.time().hour()).zfill(2), str(date.time().minute()).zfill(2), str(date.time().second()).zfill(2))

        shutil.copyfile('{}\\CS'.format(self.appDataLocation), dst)
        
        self.model.set('attributes', code=self.model.getAttribute(category='general', name='programa')['code'], reference=u'{}'.format(str(QtCore.QDate().currentDate().toString('yyyy-MM-dd'))))
        
        self.eventRouter.emit(QtCore.SIGNAL('changedBackups()'))


    def initConfig(self):
        self.config = utilities.ConfigParser(filename=os.path.join(self.appDataLocation, "config.cfg"))


    def initPaths(self):
        
        ## CS
        
        """
        path = self.getAttribute(category='system', dataPath ...
        
        pufff, this don't work, don't know where is CS to access attributes
        
        Must use upload-download of CS to external web server.
        
        DB must contain autentication data for each machine.
        
        Autentication period must be equal for all machines.
        
        """
        
        ## Get App Data/Config folder
        if sys.platform == 'darwin':
            self.appDataLocation = os.path.expanduser(os.path.join("~",
                "Library", "Application Support", self.alias))
        elif sys.platform == 'win32':
            if os.environ.has_key('APPDATA'):
                self.appDataLocation = os.path.join(os.environ['APPDATA'], self.alias)
            elif os.environ.has_key('USERPROFILE'):
                self.appDataLocation = os.path.join(os.environ['USERPROFILE'], 'Application Data', self.alias)
            elif os.environ.has_key('HOMEDIR') and os.environ.has_key('HOMEPATH'):
                self.appDataLocation = os.path.join(os.environ['HOMEDIR'], os.environ['HOMEPATH'], self.alias)
            else:
                self.appDataLocation = os.path.join(os.path.expanduser("~"), self.alias)
        else:
            # pretty much has to be unix
            self.appDataLocation = os.path.expanduser(os.path.join("~", '.{}'.format(self.alias)))

        ## Get User data folder
        if sys.platform == 'darwin':
            pass
        elif sys.platform == 'win32':
            buffer_ = ctypes.create_unicode_buffer(300)
            ctypes.windll.shell32.SHGetFolderPathW(0, 0x0005, 0, 0, buffer_)
            self.userDataLocation = buffer_.value
        else:
            self.userDataLocation = os.path.expanduser('~')


        ## Create folder Admiros in App Data/Config folder
        try:
            os.makedirs(self.appDataLocation)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise

        ## Create folder admiros in User Data/Config folder
        try:
            os.makedirs(self.userDataLocation)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise


    def initDB(self):
        # print("""App.initDB()""")
        
        self.model = db.Handler(app=self, engine='sqlite')
        
        # print("""App.initDB() - END""")


    def initLogging(self):
        # print("""App.initLogging()""")
        
        try:
            
            ## Setting up system logging to admiros.sys.log        
            self.systemLog = logging.handlers.RotatingFileHandler(os.path.join(self.appDataLocation,'admiros.sys.log'), maxBytes=200000, backupCount=1)
            self.systemLog.setLevel(logging.DEBUG)
            self.systemLog.setFormatter(logging.Formatter(">%(levelname)s - %(asctime)s - v{} - %(message)s".format(self.version)))
            logging.getLogger('system').addHandler(self.systemLog)
            
            self.system_tbLog = logging.handlers.RotatingFileHandler(os.path.join(self.appDataLocation,'admiros.sys.log'), maxBytes=200000, backupCount=1)
            self.system_tbLog.setLevel(logging.DEBUG)
            self.system_tbLog.setFormatter(logging.Formatter(""))
            logging.getLogger('system_tb').addHandler(self.system_tbLog)
            
            ## Setting up general logging to admiros.log
            # logging.basicConfig(filename=os.path.join(self.appDataLocation, 'admiros.log'), level=logging.ERROR, format=">>%(levelname)s>%(asctime)s>%(message)s", datefmt='%d-%b-%Y')
            self.dataLog = logging.FileHandler(os.path.join(self.appDataLocation, 'admiros.log'))
            self.dataLog.setFormatter(logging.Formatter("%(levelname)s - %(asctime)s - %(message)s"))
            logging.getLogger('data').addHandler(self.dataLog)
            logging.getLogger('data').setLevel(logging.DEBUG)

            ## Setting up general logging to stdout
            self.console = logging.StreamHandler(sys.stdout)
            self.console.setLevel(logging.WARNING)
            logging.getLogger('').addHandler(self.console)

            ## Setting up error logging to email
            
            # self.emailLoggingHandler = logging.handlers.SMTPHandler('smtp.gmail.com', 'cdpublic01@gmail.com', ('hojyoj@gmail.com'), 'Error Report from {}{} {}'.format(self.alias, self.version, 'holder unknown'), ('cdpublic01@gmail.com', 'cdpublic01'), ())
            # self.emailLoggingHandler.setLevel(logging.ERROR)
            # logging.getLogger('').addHandler(self.emailLoggingHandler)

        except Exception as e:
            
            logging.getLogger('system').error(u"ERROR @ App.initLogging()\n    {}".format(sys.exc_info()[1]).encode('utf8'))
            
            self.error = [e, sys.exc_info()[2]]


    def stopLogging(self):
        self.systemLog.close()
        self.system_tbLog.close()
        self.dataLog.close()
        self.console.close()
        
    
    def logging_stop(self, which='all'):
        if which == 'all' or which == 'data':
            self.dataLog.close()
            datalogger = logging.getLogger('data').removeHandler(self.dataLog)
    
    
    def logging_start(self, which='all'):
        if which == 'all' or which == 'data':        
            logging.getLogger('data').addHandler(self.dataLog)
    
    
    
    def isProtected_get(self):
        record = self.model.getAttribute(category="general", name="proteccion")
        return not not int(record['value'])
    def isProtected_set(self, value):
        if value in [False, 0, None, '']:
            value = '0'
        else:
            value = '1'
        attr = self.model.getAttribute(category="general", name="proteccion")
        self.model.set('attributes', code=attr['code'], value=value)
    isProtected = property(isProtected_get, isProtected_set)


    def sendInfo(self):
        sendInfo()
        

    def showMessage(self, kind, line1, line2='', alignment=None):
        
        if self.splash.isVisible():
            # QSplashScreen.showMessage (self, QString message, int alignment = Qt.AlignLeft, QColor color = Qt.black)
            self.splash.showMessage(line1, alignment)
        else:
            if kind == 'INFO':
                QtGui.QMessageBox.information(self.mainForm, u"{} - {}".format(self.name, line1), u"{}".format(line2), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

            elif kind == 'WARNING':
                QtGui.QMessageBox.warning(self.mainForm, u"{} - {}".format(self.name, line1), u"{}".format(line2), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

            elif kind == 'ERROR':
                QtGui.QMessageBox.critical(self.mainForm, u"{} - {}".format(self.name, line1), u"{}".format(line2), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

                self.mainForm.setCursor(QtCore.Qt.WaitCursor)
                logging.getLogger('system').error(("    {}".format(self.model.lastMessage())).encode('utf8'))
                self.mainForm.setCursor(QtCore.Qt.ArrowCursor)


    def tipsActive(self):
        if not self.model.getAttributes(category=u'general', name=u'showTips'):
            self.model.set('attributes', category=u'general', name=u'showTips', value='1')
        return not not self.model.getAttribute(category=u'general', name=u'showTips')['value'] == '1'


    __version__ = __version__
    @property
    def version(self):
        return self.__version__



def my_excepthook(type, value, tback):
    # print("my_excepthook()")
    # print(type, value, tback)
    
    logging.getLogger('system').error(value)
    logging.getLogger('system_tb').warning("".join(traceback.format_tb(tback)))
    
    # logging.getLogger('system').error(locale.localeconv())

    sendInfo()
    

def sendInfo():
    
    try:
        session = ftplib.FTP()
        session.connect("criptidosdigitales.com")
        # logging.warning('Connected to ftp')
    except:
        logging.getLogger('system').error('Failed to connect to ftp')
    else:
        app.showMessage('WARNING', u"Reporting ...", "This could take long,\n\nplease be patient", alignment=QtCore.Qt.AlignCenter)
        
        try:
            user = app.model.getAttribute(category='user')
        except:
            user = {'name':'lcastillo', 'value':'654321'}
        
        try:
            session.login(user['name'], user['value'])
        except:
            logging.getLogger('system').error('Failed to login to ftp')
        else:

            dirname = "{}{}{}".format(socket.gethostname()[:4], 
                utilities.iface()[5:9], datetime.datetime.now().strftime('%Y%m%d_%H%M'))
            
            session.mkd(dirname)
            session.cwd(dirname)
            
            try:
                logFile = os.path.join(app.appDataLocation,'admiros.sys.log')
                file = open(logFile, 'r')
                session.storbinary('STOR {}'.format(os.path.basename(logFile)), file)
                file.close()
            except:
                logging.getLogger('system').error('Failed to send admiros.sys.log')
            finally:
                
                cs = os.path.join(app.appDataLocation, 'CS')                
                file = open(cs, 'rb')
                session.storbinary('STOR {}'.format(os.path.basename(cs)), file)
                file.close()

                # zipcs = os.path.join(app.appDataLocation, 'CS.zip')
                
                # zip = zipfile.ZipFile(zipcs, "w")
                # zip.write(cs, os.path.basename(cs), zipfile.ZIP_DEFLATED)
                # zip.close()
                
                # file = open(zipcs, 'r')
                # session.storbinary('STOR {}'.format(os.path.basename(zipcs)), file)
                # file.close()
                
                cfg = os.path.join(app.appDataLocation, 'config.cfg')
                file = open(cfg, 'r')
                session.storbinary('STOR {}'.format(os.path.basename(cfg)), file)
                file.close()
                
                log = os.path.join(app.appDataLocation, 'admiros.log')
                file = open(log, 'r')
                session.storbinary('STOR {}'.format(os.path.basename(log)), file)
                file.close()
                
                logging.getLogger('system').info('Sent debug package')    
        
        session.close()
    


sys.excepthook = my_excepthook

f = open(os.devnull, 'w')
sys.stderr = f


if __name__ == "__main__":

    app = App(sys.argv)

    # if app.error:
        # error = app.error_pull()
        # my_excepthook(type(error[0]), error[0], error[1])
        # sys.exit(-101010)

    result = app.preInit()    

    app.mainForm.restoreSize(QtCore.QSize(400, 300))

    app.mainForm.show()
        
    app.processEvents()

    if result:
        
        app.showMessage('INFO', u"Autentificando ...", alignment=QtCore.Qt.AlignCenter)

        if app.model.locked():
            
            app.splash.hide()

            resultQt = QtGui.QMessageBox.warning(None, u"%s - Acceso denegado" % app.name, u"Probablemente la clave de instalación ha vencido\n\n¿Desea capturar una nueva Clave de instalación?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

            if resultQt == QtGui.QMessageBox.Yes:
                accessForm = access.Form(u"Acceso al sistema", app=app)
                result = accessForm.exec_()
            else:
                result = 11011

            app.splash.show()

        if result:
            
            if not app.model.locked():
                app.init()
                
                app.splash.finish(None)
            
                app.tips = tips.Form(app.mainForm, app=app)
                
                if app.tipsActive():
                    app.tips.show()
                else:
                    app.tips.hide()
                
                app.mainForm.restoreSize()

                app.mainForm.ui.contentFR.show()

                app.systemMessages_check()
                
                result = app.exec_()
            
        else:
            
            app.splash.show()
            app.showMessage(u"Cerrando ...", QtCore.Qt.AlignCenter)
            result = 1001
            logging.getLogger('system').warning(u"Access intent failed".encode('utf8'))
            app.splash.finish(None)

    else:
        app.splash.show()
        app.showMessage(u"Cerrando ...", QtCore.Qt.AlignCenter)
        logging.getLogger('system').error((u"{}".format(app.model.lastMessage())).encode('utf8'))
        app.splash.finish(None)

    sys.exit(result)



"""
  ~~~~~~  KNOWN ISSUES ~~~~        

    06.16   Renovación de póliza no pone bien el tipo de pago.

    06.14   No imprime clientes
        
    02.19   Report Manager - Client selection not working

        2014  

    06.27   Adaptation to basiq interfase not finished

        2013

    08.01   Policy report by Number doesnt show policies with status
          renovada when renovada hidden checked
    07.30   Many messages that should be logged are not
    07.26   No se calcula correctamente el IVA en el total de monto de
          pólizas
    07.26   Registro de pago con poliza_id=None provoca exception en
          reportes

        2012

    14.06.19  FIXED   14.06.18    No permision to execute Admiros (change .exe.log file)


  ~~~~~~  WISHES    ~~~~~~~
    2014.06.26    Implementar el uso en dos máquinas.
                    Reconocimiento de dos claves de acceso
                    Movimiento de archivos a medio de transporte
                        Internet : Servidor FTP
                        Fisico : USB, SD
                        
    2014.06.19    Access CS data in dropbox folder (check initPaths for info)
                Limpieza de datos de pólizas (Eliminación por grupos)
                Add option to enable/disable news tab
    2014.06.16    Fix format of messages date 
                Agregar el filtro En el mes anterior en los reportes
    2014.06.13    Delete Aseguradora
    2014.03.26    Access documents from MyDocuments/Admiros folder
    2014.02.07    DONE    Debug info package sender
    2014.01.20    Add periods of days to policy
    
        2014
    
    2013.07.10    Better localization of customer on policyReview

    07.20   Encapsulate objects like policy, customer, etc.
    07.15   Can print customers

        2013

    11.26   Can delete Cliente
    07.30   Implement cleaning tool
            Remove Cancelled policies
            Remove Renewed policies
    07.28   Implement detection of mispelling in data
    07.27   Posibility to delete groups of policies

        2012


  ~~~~~~  CHANGELOG  ~~~~~~
  
        v1.4.13
    08.06   Added Debug Button to General Tools, to send files to developer.
    08.05   Started Policy and payments code cleanup.
    08.04   Policies of kind VIDA shouldn't include IVA   
  
        v1.4.12
    07.14   Added Fixing routine for policy's aseguradora_id wrong code
  
        v1.4.11
    07.13   Fixed client_id sql error in policies_get
            Fixed CDNumberEdit decimal limits usage.
  
        v1.4.7
    07.03   Added check in _setup.py for production version
            version 5 of policy db now removes uncoded insurer
  
        v1.4.6
    06.25   Improved context menu stylesheets
            Added status background to CDLineEdit
            Cleaned filesystem to atico
    06.24   Added check and fix or warning for policy tiposeguro_id error.
            Added new status CERRADA for expired policies not renewed.
            Removed or fixed report format records.

        v1.4.5
    06.20   Activated policy error checking
            Implemented inclusion of CS in instalator
            Removed News tab

        v1.4.4
    06.19   Redirected stderr to blackhole to avoid py2exe access
                to .exe.log
            Send exceptions to .sys.log at appData folder
            
        v.1.4.3
    06.19   Fixed policiesStatus_update not checking expirada
            Disabled arrangeData call
    06.18   Added 'en lo que va del año ' to period option at
                report filters
            Added 'Pólizas expiradas' report format to list and
                made it default
   
        v1.4.2
    06.15   Fixed many bugs introduced when migrating from admiros
                model to basiq model, and adapting cfd as tool.
    06.16   Fixed systemMessages_check at policy now checks only
                records containing 'policy'
  
        v1.4.1
    06.05   Changed Added logging lines to utilities.arrangeData
   
        v1.4
    05.30   Se incluye el archivo CS
    05.29   Changed Added cfd module, and required modules tools, 
                persons, products.
    05.10   Changed Added datos de facturación de aseguradoras.
            Changed Added States and Places recordes to variables.


    1.3.30  05.13 Changed Activated ftp Error sending
  
    1.3.29  05.09 Changed Added app version to logging output to .exe.log
  
    1.3.28  05.08 Fixed   Policy - PaymentsCnt - Added policyStatus_calculate()
                Fixed   Policy - Now validates Aseguradora field is not empty
                Fixed   Policy - Numero field now shows validation messages
                            correctly
                Fixed   Policy - Payments - Now validates correctly unmodified
                            values
                Changed Policy - Changed default status for new policy from
                            Cotizacion to Pendiente de pago
                Changed Policy - Save button now shows OK on tooltip instead
                            of nothing
  
  
    1.3.27  03.26         Changed splash image reference to splashLogo.png,
                        accesed from resources.
                        Resources for Designer now accesed from basiq/files,
                        logos still accesed from root folder
  
    1.3.26  03.25 Fixed   Protection mode - Now accesed by app.isProtected
                        DB registry has value '0' or '1'
                        isProtected converts to False or True
                Fixed   Restore size - Relocated calls, now set in app main
                        instance setup
                Fixed   Model.set() - Couldn't update without _id field
                
    1.3.25                
  
    1.3.24  02.19 Fixed   Policy - Review - updateVigencia not Working
  
    1.3.23  02.18         Tried to add cfd module, py2exe prevented it
                            Added encodings.ascii, inspect, lxml.etree,
                            lxml._elementpath, gzip to includes
                            Added MSVCR80.dll to dll_excludes
                            Couldnt find workaroundfor _chilkat.pyd
  
    1.3.22        Fixed   Bugs at policy capture
  
    1.3.21  02.04 Fixed   CDLabel initialText attribute referenced as
                        function.
                Fixed   DB based toggle attributes trying to apply int
                        function to ''.
                Fixed   Migrated pdf creation from reportlab to QPainter
                Fixed   Separated logging for system data and process data
                Changed Implemented Debug package sending at exception
                
    1.3.20  08.23         Invalid data in policy register now catched and
                        showed.
                        Fixed bug in pagos policy report
    1.3.19  08.15         Added support for share of db by 2 computers
                        Restored ssl module in installer (_setup.py)
                        Restored bundle mode (changed icons to pngs)
    1.3.18  08.14         Fixed db initialization on new install
    1.3.17  08.13         added admiros.exe.log file to installer
    1.3.16  07.22 Fixed   application of exent charges was doubled.
    1.3.15  07.22 Fixed   misfixed in 1.3.13, discount (and others) capture
                        misbehaviour introduced in v1.3.10
    1.3.14  07.20 Fixed   renovation misbehaviour introduced in v1.3.13

    1.3.13  07.20 Fixed   discount (and others) capture misbehaviour
                        introduced in v1.3.10
                        Protected Mode now affects discount and expenses
                        fields.

    1.3.12  07.19 Fixed   renovation misbehaviour on expired policies
                        introduced in v1.3.10.
                        Protection mode acts now on button for removing
                        report format.
                        Button Eliminar now prechecks inability causes.

    1.3.11  07.15         Packaging of print routines by cast
                            Added publishing modules
                Added   wrapping of long customers name in pdf reports.
                Added   icon.ico and logo.png images for resources.qrc
                        handling

    1.3.10  07.09         Packaging by cast policy, customer, claim, news
                Added   Second Policy review form layout
                Fixed   Eliminar & Modificar main buttons, remove report
                        kind button didn't work due to payments registry
                        errors at database (policy_id = None)
                Fixed - Total calculus was buggy

    1.3.9   06.27 Fixed - @ policy capture, payments did not save changes
                        for kind vida

        2013

    1.3.8.1 10.16 Fixed - In policy capture, company selector omited rows.
                Fixed - In policy capture, payments date not working.
                Added - In policy capture, validity check for number, type
                        and company combination already existing.
                        Introduced method confirm()
                Fixed - In policy capture, vigenciaED displaying unwanted
                        trailing dot
                Fixed - In policy capture, payments not showing dates when
                        first choosing vigency longer than one year

    1.3.8 10.12   Fixed - RFC capture of Customer not working for Moral
                        person

    1.3.6 09.07           Removed class Controller
                        Removed class Session
                        Removed subrepos cdWidgets
                        Moved installer creation files to installer folder

    1.3.5 08.03   Fixed - Startup Windows Layout
        08.03   Fixed - Redefined Message Handling
        08.03   Added - Connect to database now tests database is locked
        08.01   Fixed - Delete policy not deleting payments
        08.01   Fixed - Reports with period and event selection not working

    1.3.4 07.30   Reactivated email logging
        07.30   Fixed - Authentication behaviour
        07.30   Added - Option to hide renewed policies.
        07.28   Fixed - Add customer at policy capture does not filli name
                        at customer selector
        07.26   Fixed - Report Cobros en el mes now shows wrong data

        07.26   Fixed - Cambio de valor de paridad no recalcula

    1.3.3   07.26 Fixed - Payments bug for new policies
                Added - Close shown policies before adding renewal

    1.3.0         Added - Backup capabilities
    1.3.0         Added - Event Display capabilities

    1.3.0 06.11   Added - Agent Package [Disabled on standard version]
        2012


  ~~~~~~  TEST SCENARIOS  ~~~~~~
    06.05  v1.4  Installed but never executed (CS in Program Files)
                 - Old CS at Roaming        =
                 - no CS at Roaming         = No problem
                 - Old CS at roaming opened =
               
  


  ~~~~~~  Established behaviour  ~~~~~~
  
    05.08 Introduction of CFDI
        Used cfdi capture in options section against standard behaviour
        of using Manager and Capture on mainview.
        Only companies used as cfdi's customer. Against implementing roles.
        
        
  
  
        2014

    07.30   MESSAGE HANDLING
        Level   INFO    Display     log to admiros.log
                WARNING Display     log to admiros.log
                ERROR   Display     log to admiros.log  log to email cdpublic01@gmail.com
                CRITICAL            log to admiros.log  log to email cdpublic01@gmail.com

    La opción de eliminar formato de reporte se desactiva para el formato
    default.

    ~~  Protected Mode  ~~~~
    Prevents removal of saved report formats by hidding button.
    Prevents removal of policies by disabling Button Eliminar and Action
    Eliminar.
    Makes difficult to modify policies by disabling Button Modifica and
    Action Modificar, Button Modificar in Policy Details Form is left
    enabled.


        2012


  ~~~~~~  ERROR CODES  ~~~~~~

    Access    11000

    11011     Access intent failed
    11013     Retrieving data
    11015     Setting alternate key
    11017     Setting primary key
    11019     Setting virgin primary key
    11021     Key tested valid
    11023     Key tested not valid



  ~~~~~~  TO INSTALL DB FILE (CS) ON DESTINY MACHINE  ~~~~~~
  
    Put
        utilities.arrangeData(self, 'CS', 'appData')
    in
        preInit()
    Update last saved program attribute to current date


  ~~~~~~  TO INTERCEPT EXCEPTION HANDLING  ~~~~~~
  
    Add (uncomment line 690)
        sys.excepthook = my_excepthook
    to
        app's global namespace
    
    
  ~~~~~~  TO SEND DEBUG INFO TO FTP  ~~~~~~
  
    Use
        session = ftplib.FTP()
    in
        my_excepthook(type, value, tback)


  ~~~~~~  DIFF IN production and dev versions
          Code settup for production version  ~~~~~~
  
    Production:
        Uncomment  sys.excepthook = my_excepthook
        Comment out    utilities.arrangeData(self, 'CS', 'appData') @ preInit()
    
    When using    utilities.arrangeData    copy    CS file    to main folder
                                    and add entry to _setup.py
  
  
"""


