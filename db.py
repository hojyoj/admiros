# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Database access core                       ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2008                                    ##
  ##                                             ##
    ###############################################

"""
This module interfases Database Access for sqlite motor
It is version 1.0 branch that will implement only basic access
For detailed access look at version 2.0 branch

Due to connection handling, the application must use only one instance of this module
"""

from __future__ import print_function

import logging

import sys
import traceback
from decimal import Decimal
import datetime
from PyQt4 import QtCore

from sqlite3 import dbapi2 as adapter

import km
import DBSetup



class Handler():
    """ """

    _firstRun = False
    _lastMessage = None

    def __init__(self, **kwds):
        """ """
        self.app = kwds.pop('app', None)
        
        self.engine = kwds.pop('engine', None)
        
        exec("from basiq import {}".format(self.engine))
        self.sql = eval("{}".format(self.engine))

        # self._conn = [None, None]
        self._conn = None


    def add(self, table, data):
        """ """
        try:
            command = "INSERT INTO %s " % table
            colsT = "( "
            valuesT = "VALUES ( "
            for valor in data:
                if data[valor] is not None:
                    colsT += u"%s, " % valor
                    if type(data[valor]) in [str, unicode]:
                        if "'" in data[valor]:
                            valuesT += u'"%s", ' % data[valor]
                        else:
                            valuesT += u"'%s', " % data[valor]
                    elif type(data[valor]) == list:
                        temp = (u"%s" % data[valor]).replace('[', '{').replace(']', '}').replace("'", '"')
                        temp = u"'%s', " % temp
                        valuesT += temp
                    else:
                        valuesT += u"%s, " % data[valor]
                else:
                    colsT += u"%s, " % valor
                    valuesT += "null, "

            if data:
                command += u'%s ) %s ) ' % ( colsT.rstrip( ", " ), valuesT.rstrip( ", " ) )
            else:
                command += u'DEFAULT VALUES '

            # print  command.encode('utf8')

            cur = self._conn.cursor()
            result = cur.execute(command)
            
            id = cur.lastrowid
            
            cur.close()

            self._conn.commit()
            
            return id

        except:
            logging.getLogger('system').error(u"Handler.add()")
            logging.getLogger('system').error(u"    %s" % command.encode('utf8'))
            logging.getLogger('system').error(u"    %s" % sys.exc_info()[1])
            raise


    def commit(self):
        """ """
        self._conn.commit()


    def connect(self):
        """db.Handler.connect()"""
        self._conn = adapter.connect(database="{}\\CS".format(self.app.appDataLocation))
        self._conn.row_factory = dict_factory
        return


    def disconnect(self):
        """ """
        self._conn.disconnect()


    def createDb(self):
        """db.Handler.create()"""
        import DBSetup
        DBSetup.create(self)
        self._firstRun = True
        # print  "db.Handler.create() -- FIN"


    def cursor(self):
        """ """
        return self._conn.cursor()


    def disconnect(self):
        """ """
        self._conn.close()


    def execute(self, command, **kwds):
        """ """
        
        ## basiq compatibility
        giveCursor = kwds.pop('giveCursor', False)
        
        cur = self.cursor()
        cur.execute(command)
        # cur.close()
        # self.commit()
        
        if giveCursor:
            return cur
        else:
            cur.close()


    def getOne(self, table, **filters):
        
        prep = table
        
        if table is 'variables':
            table = 'attributes'
            if 'variable_id' in filters:
                filters['code'] = filters.pop('variable_id')
            if 'tipo' in filters:
                filters['category'] = filters.pop('tipo')
            if 'subtipo' in filters:
                filters['cast_'] = filters.pop('subtipo')
            if 'nombre' in filters:
                filters['name'] = filters.pop('nombre')
            if 'valor' in filters:
                filters['value'] = filters.pop('valor')
            if 'referencia' in filters:
                filters['reference'] = filters.pop('referencia')        

        result = self.get(table, **filters)

        if prep is 'variables':
            result['valor'] = result['value']
            result['referencia'] = result['reference']

        return result

        
        if table is 'attributes':
            table = 'variables'
            
            if 'code' in filters:
                filters['variable_id'] = filters.pop('code')                
            if 'category' in filters:
                filters['tipo'] = filters.pop('category')
                if filters['tipo'] is 'place':
                    filters['tipo'] = 'lugar'
            if 'name' in filters:
                filters['nombre'] = filters.pop('name')
            if 'cast_' in filters:
                filters['subtipo'] = filters.pop('cast_')
                
            result = self.get(table, **filters)
            
            result['code'] = result.pop('variable_id')                
            result['category'] = result.pop('tipo')
            if result['category'] is 'lugar':
                result['category'] = 'place'
            result['name'] = result.pop('nombre')
            result['value'] = result.pop('valor')
            result['reference'] = result.pop('referencia')
            result['cast_'] = result.pop('subtipo')
            result.pop('valor2')
            return result
        else:
            return self.get(table, **filters)


    def get(self, table, **filters):
        """ Crea el commando SQL para extraer un renglón a partir de los argumentos.  """
        """"db.Handler.get()""", table, filters
        
        if table is 'variables':
            # print('===========>>>>>>>>')
            if 'variable_id' in filters:
                if filters['variable_id'] == 55:
                    f=g
        
        try:
            command = "SELECT * FROM %s " % table
            filtersText = ""
            for filter in filters:
                if type(filters[filter]) in (str, unicode):
                    if "'" in filters[filter]:
                        filters[filter] = filters[filter].replace("'", "''")
                    if " LIKE" in filter.upper():
                        filtersText += "%s '%s%%' AND " % (filter, filters[filter])
                    else:
                        filtersText += "%s='%s' AND " % (filter, filters[filter])
                elif type(filters[filter]) in (list,):
                    temp = ("%s" % filters[filter]).replace("[", "{").replace("]","}").replace("'", '"')
                    filtersText += "%s='%s' AND " % (filter, temp)
                elif filters[filter] == None:
                    filtersText += "%s is null AND " % filter
                else:
                    filtersText += "%s=%s AND " % (filter, filters[filter])
            if filtersText: command += "WHERE %s " % filtersText.rstrip("AND ")

            # print(command.encode('utf8'))

            cur = self._conn.cursor()
            cur.execute(command)
            result = cur.fetchone()
            cur.close()
            
            return result
            
        except Exception as e:
            #! Logging should no ocurr here, set it up in the method calling this
            # logging.getLogger('system').error("ERROR @ Handler.get()")
            # logging.getLogger('system').error("    Command: {}".format(command.encode('utf8')))
            # logging.getLogger('system').error("    info: {}".format(sys.exc_info()[1]))
            raise e


    def getAll(self, table, **filters):
        if table is 'attributes':
            table = 'variables'
            
            if 'code' in filters:
                filters['variable_id'] = filters.pop('code')                
            if 'category' in filters:
                filters['tipo'] = filters.pop('category')
                if filters['tipo'] is 'place':
                    filters['tipo'] = 'lugar'
            if 'name' in filters:
                filters['nombre'] = filters.pop('name')
            if 'cast_' in filters:
                filters['subtipo'] = filters.pop('cast_')
                
            
            results = self.getMany(table, filters=filters)
            
            for result in results:
                result['code'] = result.pop('variable_id')                
                result['category'] = result.pop('tipo')
                if result['category'] is 'lugar':
                    result['category'] = 'place'
                result['name'] = result.pop('nombre')
                result['value'] = result.pop('valor')
                result['reference'] = result.pop('referencia')
                result['cast_'] = result.pop('subtipo')
                result.pop('valor2')
            return results
        else:
            return self.getMany(table, **filters)


    def getMany(self, table, filters="", order="", count=0, cursor=None):
        # print("""db.Handler.getMany()""")
        # print(table)
        # print(filters)
        # print(order)
        # print(count)
        # print(cursor)
        try:
            orderText = ""
            if 'order' in filters:
                orderText = filters.pop('order')
            else:
                for item in order:
                    orderText += "{}, ".format(item)
            
            command = "SELECT * FROM {} ".format(table)
            filtersText = ""
            for filter in filters:
                if ' LIKE' in filter.upper():
                    if 'OR ' in filters[filter]:
                        operator = "OR "
                        filters[filter] = filters[filter].rstrip('OR ')
                    else:
                        operator = "AND "
                    filtersText += "UPPER({}) LIKE '{}%%' {} ".format(filter.rstrip('LIKE'), filters[filter].upper(), operator)
                elif type(filters[filter]) in (str, unicode):
                    if '!=' in filters[filter]:
                        filtersText += u"{}!='{}' AND ".format(filter, filters[filter].strip('!=').strip())
                    elif '<' in filter or '>' in filter:
                        filtersText += u"{}'{}' AND ".format(filter, filters[filter].strip())
                    else:
                        filtersText += u"{}='{}' AND ".format(filter, filters[filter])
                elif type(filters[filter]) in (list,):
                    temp = ("{}".format(filters[filter])).replace("[", "{").replace("]","}").replace("'", '"')
                    filtersText += "{}='{}' AND ".format(filter, temp)
                elif filters[filter] == None:
                    filtersText += "{} is null AND ".format(filter)
                else:
                    filtersText += "{}={} AND ".format(filter, filters[filter])
            # orderText = ""
            # for item in order:
                # orderText += "{}, ".format(item)
            if filtersText:
                command += u"WHERE {} ".format(filtersText.rstrip("AND ").rstrip("OR "))
            if orderText:
                command += u"ORDER BY {}".format(orderText.rstrip(", "))

            # print(11011, command.encode('utf8'))
            
            # print(cursor)

            if not cursor:
                cursor = self._conn.cursor()
                cursor.execute(command)
                
                if not count:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchmany(count)
                cursor.close()
            else:
                cursor.execute(command)
                if not count:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchmany(count)

            return result
        except:
            print (sys.exc_info())
            f=g
            logging.getLogger('system').error("Handler.getMany()")
            logging.getLogger('system').error("    %s" % command.encode('utf8'))
            logging.getLogger('system').error("    %s" % sys.exc_info()[1])
            raise

        # print("""db.Handler.getMany() - END""")


    def incRunCount(self):
        """ """
        runCountZero = self.getAttribute(category='general', name='runCount')
        if runCountZero is None:
            # self.add("attributes", {'tipo':'general', 'nombre':'runCount', 'valor':'1'})
            self.set("attributes", {'tipo':'general', 'nombre':'runCount'}, valor='1')
            runCount = 1
        else:
            runCount = int(runCountZero['value'])

        # self.modificar("attributes", {'valor':'%s' % (runCount+1)}, {'tipo':'general', 'nombre':'runCount'})
        runCountAtt = self.getAttribute(category='general', name='runCount')
        
        self.set('attributes', code=runCountAtt['code'], value="{}".format(runCount+1))

    
    def init(self):
        # print("""    db.Handler.init()""")
        
        ## Trying to connect
        try:
            # print("""        Trying to connect ...""")
            self.connect()
            #! Should message if database was created
            # print('connected')
        except:
            ## Processing connection failure
            
            ## Trying to fix connection problem
            
            ## Connection not achieved, log message
            logging.getLogger('system').error(u"db.Handler.init()")
            logging.getLogger('system').error(u"    %s" % sys.exc_info()[1])
            ## Exit init() method
            return False
            
        ## Connection achived
        
        ## Testing data access
        try:
            # print("""        Testing data access ...""")
            try:
                versionData = self.getAttribute(category='general', name='version')
            except:
                versionData = self.get('variables', tipo='general', nombre='version')
                versionData['value'] = int(versionData['valor'])
                versionData['code'] = versionData['variable_id']
        except:
            ## Trying to fix data access
            
            ## If missing table, asuming no tables, new database
            if sys.exc_info()[1].message == 'no such table: attributes':
                ## Trying to create tables
                try:
                    DBSetup.create(self)
                except:
                    ## Tables creation failed
                    
                    ## Trying to fix tables creation
                    
                    ## Tables creation not achieved, log message
                    logging.getLogger('system').error(u"ERROR @ db.Handler.init()")
                    logging.getLogger('system').error(u"    %s" % sys.exc_info()[1])
                    ## Exit init() method
                    return False
                
                ## Trying to fill tables
                try:
                    DBSetup.init(self)
                    versionData = self.getAttribute(category='general', name='version')
                    versionData['value'] = int(versionData['value'])
                    
                    # self.set('variables', variable_id=versionData['variable_id'], valor='11')
                    self.set('attributes', id=versionData['id'], value='11')
                    version = 11
                except:
                    ## Table filling failed
                    
                    ## Trying to fix tables filling
                    
                    ## Tables filling not achieved, log message
                    logging.getLogger('system').error(u"db.Handler.init()")
                    logging.getLogger('system').error(u"    %s" % sys.exc_info()[1])
                    ## Exit init() method
                    raise
                    
                ## Trying to set key for new installation
                try:
                    if self.app.model.getAttribute(category='holder'):
                        
                        key = km.reEncode(km.encode(self.app.model.getAttribute(category='holder')['reference'], 2, datetime.datetime.today().strftime("%M%S")), datetime.datetime.today() + datetime.timedelta(days=30))

                        self.add("attributes", {'tipo': u'general', 'nombre': u'key', 'valor': km.reEncode(km.encode(self.app.model.get("attributes", tipo='holder')['referencia'], 2, datetime.datetime.today().strftime("%M%S")), datetime.datetime.today() + datetime.timedelta(days=30))})
                except:
                    ## Key setting failed, show message
                    logging.getLogger('system').error(u"ERROR @ db.Handler.init()")
                    logging.getLogger('system').error(u"    %s" % sys.exc_info()[1])
                    ## Exit init() method
                    raise
        
        ## Data access achieved

        ## Trying to apply patches
        try:
            # print("""        Trying to apply patches ...""")
            if versionData['value'] < 1:
                DBSetup.init(self)
                self.set('variables', variable_id=versionData['variable_id'], valor='13')
                
            if versionData['value'] < 14:

                cursor = self.cursor()
                cursor.execute("DELETE FROM variables WHERE tipo='general' AND nombre='version'")
                cursor.execute("INSERT INTO variables (tipo, nombre, valor) VALUES ('general', 'version', 14)")
                self.commit()
                
                try:
                    print ("    CREATING TABLE attributes ...       ",)
                    cursor.execute("""CREATE TABLE attributes (
                        id          {},
                        cast_       TEXT,
                        code        INTEGER UNIQUE,
                        category    TEXT,
                        name        TEXT,
                        value       TEXT DEFAULT '',
                        reference   TEXT DEFAULT '',

                        rstatus     TEXT DEFAULT 'active',
                        rspanstart  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        rspanend    TIMESTAMP,
                        ruser       INTEGER
                    )""".format(self.sql.sequence))
                    print ("    Succeded")
                except:
                    print ("== Failed")
                    print (sys.exc_info())
                    raise
                
                try:
                    print ("    COPYING TABLE variables ...",)
                    cursor = self.cursor()
                    cursor.execute("SELECT * FROM variables")
                    variables = cursor.fetchall()
                    self.commit()
                    for variable in variables:
                        # print(variable)
                        if variable['tipo'] is not 'lugar':
                            command = u"""INSERT INTO attributes (
                            cast_, code, category, name, value, reference
                            ) VALUES ('{}', {}, '{}', '{}', '{}', '{}')
                            """.format(variable['subtipo'], variable['variable_id'], variable['tipo'], variable['nombre'], variable['valor'], variable['referencia'])
                            cursor.execute(command)
                    self.commit()
                    cursor.close()
                    print ("    Succeded")
                except:
                    print ("== Failed")
                    print (sys.exc_info())
                    raise
                
                vars = self.getMany('variables', {'tipo':'tipopago'})
                for var in vars:
                    self.set('attributes', code=var['variable_id'], reference=var['valor2']) 
                
                vars = self.getMany('variables', {'tipo':'moneda'})
                for var in vars:
                    self.set('attributes', code=var['variable_id'], reference=var['valor2'])
                # var = self.getAttribute(category='moneda', name='Dolares')
                # self.set('attributes', code=['code'], reference='exenta')
                
                var = self.get('variables', tipo='general', nombre='programa')
                
                self.set('attributes', code=var['variable_id'], reference=var['valor2'])

                self.set('attributes', cast_=u'system', category=u'user', name=u'lcastillo', value=u'654321')
                
                
                registros = [
                [20101, u'state', u'Aguascalientes',      u'Ags.'],
                [20102, u'state', u'Baja California',     u'B.C.'],
                [20103, u'state', u'Baja California Sur', u'B.C.S'],
                [20104, u'state', u'Campeche',            u'Camp.'],
                [20105, u'state', u'Coahuila',            u'Coah.'],
                [20106, u'state', u'Colima',              u'Col.'],
                [20107, u'state', u'Chiapas',             u'Chis.'],
                [20108, u'state', u'Chihuahua',           u'Chih.'],
                [20109, u'state', u'Distrito Federal',    u'D.F.'],
                [20110, u'state', u'Durango',             u'Dgo.'],
                [20111, u'state', u'Guanajuato',          u'Gto.'],
                [20112, u'state', u'Guerrero',            u'Gro.'],
                [20113, u'state', u'Hidalgo',             u'Hgo.'],
                [20114, u'state', u'Jalisco',             u'Jal.'],
                [20115, u'state', u'México',              u'Mex.'],
                [20116, u'state', u'Michoacán',           u'Mich.'],
                [20117, u'state', u'Morelos',             u'Mor.'],
                [20118, u'state', u'Nayarit',             u'Nay.'],
                [20119, u'state', u'Nuevo León',          u'N.L.'],
                [20120, u'state', u'Oaxaca',              u'Oax.'],
                [20121, u'state', u'Puebla',              u'Pue.'],
                [20122, u'state', u'Querétaro',           u'Qro.'],
                [20123, u'state', u'Quintana Roo',        u'QRoo.'],
                [20124, u'state', u'San Luis Potosí',     u'S.L.P.'],
                [20125, u'state', u'Sinaloa',             u'Sin.'],
                [20126, u'state', u'Sonora',              u'Son.'],
                [20127, u'state', u'Tabasco',             u'Tab.'],
                [20128, u'state', u'Tamaulipas',          u'Tmps.'],
                [20129, u'state', u'Tlaxcala',            u'Tlax.'],
                [20130, u'state', u'Veracruz',            u'Ver.'],
                [20131, u'state', u'Yucatán',             u'Yuc.'],
                [20132, u'state', u'Zacatecas',           u'Zac.'],
                
                [21201, u'place', u'Acapulco',      u'', u'20112'],
                [21401, u'place', u'Aguascalientes', u'', u'20101'],
                [21601, u'place', u'Campeche',      u'', u'20104'],
                [21801, u'place', u'Cd. Juarez',    u'', u'20108'],
                [22001, u'place', u'Cd. Obregón',   u'Cajeme', u'20126'],
                [22201, u'place', u'Cd. Victoria',  u'', u'20128'],
                [22401, u'place', u'Chetumal',      u'', u'20123'],
                [22601, u'place', u'Chihuahua',     u'Chihuahua', u'20108'],
                [22801, u'place', u'Chilpancingo',  u'Chilpancingo de los Bravo', u'20112'],
                [23001, u'place', u'Colima',        u'', u'20106'],
                [23201, u'place', u'Culiacán',      u'', u'20125'],
                [23401, u'place', u'Cuernavaca',    u'', u'20117'],
                [23601, u'place', u'Durango',       u'', u'20110'],
                [23801, u'place', u'Guadalajara',   u'', u'20114'],
                [24001, u'place', u'Guanajuato',    u'', u'20111'],
                [24201, u'place', u'Guasave',       u'', u'20125'],
                [24401, u'place', u'Hermosillo',    u'', u'20126'],
                [24501, u'place', u'Huixquilucan',  u'Huixquilucan', u'20115'],
                [24601, u'place', u'Jalapa',        u'', u'20130'],
                [24801, u'place', u'La Paz',        u'La Paz', u'20103'],
                [24901, u'place', u'León',          u'León', u'20111'],
                [25001, u'place', u'Los Mochis',    u'Ahome', u'20125'],
                [25201, u'place', u'Mazatlán',      u'', u'20125'],
                [25401, u'place', u'Mérida',        u'', u'20131'],
                [25601, u'place', u'Mexicali',      u'', u'20102'],
                [25801, u'place', u'México',        u'', u'20109'],
                [26001, u'place', u'Monterrey',     u'', u'20119'],
                [26201, u'place', u'Morelia',       u'', u'20116'],
                [26401, u'place', u'Navojoa',       u'', u'20126'],
                [26601, u'place', u'Nogales',       u'', u'20126'],
                [26801, u'place', u'Oaxaca',        u'', u'20120'],
                [27001, u'place', u'Pachuca',       u'Pachuca de Soto', u'20113'],
                [27201, u'place', u'Puebla',        u'', u'20121'],
                [27401, u'place', u'Queretaro',     u'Querétaro', u'20122'],
                [27601, u'place', u'Saltillo',      u'', u'20105'],
                [27801, u'place', u'San Luis Potosí', u'', u'20124'],
                [27901, u'place', u"San Pedro Garza García", u'San Pedro Garza García', u'20119'],
                [28001, u'place', u'Tepic',         u'', u'20118'],
                [28201, u'place', u'Tijuana',       u'', u'20102'],
                [28401, u'place', u'Tlaxcala',      u'', u'20129'],
                [28601, u'place', u'Toluca',        u'Toluca', u'20115'],
                [28801, u'place', u'Tuxtla Gutierrez', u'', u'20107'],
                [29001, u'place', u'Villahermosa',  u'', u'20127'],
                [29201, u'place', u'Veracruz',      u'', u'20130'],
                [29401, u'place', u'Zacatecas',     u'', u'20132'],
                
                [10051, u'taxes',        u'IVA',        u'general, default',    u'16.00::D', 'system'],
                [10053, u'taxes',        u'IEPS',       u'special,',    u'3.72::D', 'system'],
                [13017, u'system',       u'canEditDate', u'',   u'1',   'sale'],
                [13021, u'system',       u'useOwnCode', u'',    u'1',   'sale'],
                [13023, u'system',       u'useUniversalCode', u'', u'0', 'sale'],
                [13025, u'system',       u'useAuxiliaryCode', u'', u'0', 'sale'],
                [13027, u'system',       u'useLine',    u'',    u'0',   'sale'],
                
                # [13213, u'rolKind', u'salesman', employee['code'], u''],
                # [13214, u'rolKind', u'default salesman', u'',      u''],
                # [13215, u'rolKind', u'customer',        u'',    u'5', 'sale'],
                # [13216, u'rolKind', u'default customer', u'',      u''],
                
                [13500, u'documentKind', u'default',    u'',    u'13517', 'sale'],
                [13517, u'documentKind', u'invoice',    u'-1',  u'0',   'sale']
                
                # [30539, u'rolKInd', u'insurer',         u'',    u'',    'system']
                
                ]
                
                for registro in registros:
                    # print(registro)
                    
                    if len(registro) is 4:
                        data = {'code':registro[0], 'reference':registro[3], 'category':registro[1], 'name':registro[2]}
                    elif len(registro) is 5:
                        data = {'code':registro[0], 'reference':registro[3], 'category':registro[1], 'name':registro[2], 'value':registro[4]}
                    elif len(registro) is 6:
                        data = {'code':registro[0], 'reference':registro[3], 'category':registro[1], 'name':registro[2], 'value':registro[4], 'cast_':registro[5]}
                        
                    self.set('attributes', **data)
                
                
                ## databaseVersion
                versionData = self.getAttribute(category='general', name='version')
                
                self.set('attributes', code=versionData['code'], value='14')
                version = 14
                
                print ("            Applied version {}".format(version))
                


            if versionData['value'] < 0:
                self.set('variables', {'code':30522, 'tipo':'rolKind', 'nombre':'employee'})
                
                
                
                ## Adding rols, addresses tables for cfdi purposes
                
                cursor = self.cursor()
                cursor.execute("DROP TABLE IF EXISTS rols")
                cursor.execute("""CREATE TABLE rols (
                    curp        TEXT DEFAULT '',
                    rfc         TEXT DEFAULT '',
                    agent_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    names       TEXT,
                    names2      TEXT DEFAULT '',
                    span        TEXT DEFAULT '',
                    birthdate   TEXT DEFAULT '',
                    gender      TEXT DEFAULT '',
                    civilstatus TEXT DEFAULT '',
                    conyuge     TEXT DEFAULT '',
                    children    TEXT DEFAULT '',
                    place       TEXT DEFAULT '',
                    countryarea INTEGER REFERENCES countryareas,
                    city        INTEGER REFERENCES cities,
                    cityarea    TEXT DEFAULT '',
                    postcode    TEXT DEFAULT '',
                    street      TEXT DEFAULT '',
                    interior    TEXT DEFAULT '',
                    phone1      TEXT DEFAULT '',
                    phone2      TEXT DEFAULT '',
                    phone3      TEXT DEFAULT '',
                    phone4      TEXT DEFAULT '',
                    email       TEXT DEFAULT ''
                )""")
                
            
        except:
            ## Error in patch applying, log message
            logging.getLogger('system').error(u"ERROR @ db.Handler.init()")
            logging.getLogger('system').error(u"    %s" % sys.exc_info()[1])
            ## Exit init() method
            raise
        
        ## Init process completed
            
        # print("""    db.Handler.init() - END""")
        
        return True


    def initDB(self):
        """db.Handler.init()"""
        import DBSetup
        DBSetup.init(self)
        # print  "db.Handler.init() -- FIN"


    def isValid(self):
        """db.isValid()"""
        cur = self._conn.cursor()
        try:
            cur.execute("SELECT * FROM polizas")
            cur.close()
            return True
        except:
            cur.close()
            return False


    def lastMessage(self):
        """ """
        return self._lastMessage

    def locked(self):
        # print("""        db.locked()""")

        key = self.getAttribute(category=u'general', name=u'key')
        
        #~ logging.getLogger('system').warning('locked()')
        if key:
            if km.isValid(self.getAttribute(category='holder')['reference'], key['value']):
                # print("""        db.locked() - END""")
                
                return 0
            # elif key['valor2']:
                # if km.isValid(self.get("variables", tipo='holder')['referencia'], key['valor2']):
                    # return 0
            else:
                logging.getLogger('system').warning("invalid key")
                
        # print("""        db.locked() - END""")
        return 1


    def makeFiltersText(self, **filters):
        # print("""baseModel.Model.makeFiltersText()""")
        filtersText = ""
        for filter in filters.keys():
            if filter == "#":
                filtersText += "{} AND ".format(filters[filter])
            elif ' in' in filter:
                filtersText += ("{}{} AND ".format(filter, filters[filter])).replace('[', '(').replace(']', ')')
            elif ' LIKE' in filter.upper():
                filtersText += "UPPER({}) LIKE '{}%%' AND ".format(filter.upper().rstrip('LIKE'), filters[filter].upper())
            elif type(filters[filter]) in (str,):
                filtersText += "{}='{}' AND ".format(filter, filters[filter].replace("'", "''"))
            elif type(filters[filter]) in [datetime.datetime, datetime.date]:
                if '>' in filter or '<' in filter:
                    filtersText += "{} '{}' AND ".format(filter, filters[filter])
                else:
                    filtersText += "{}='{}' AND ".format(filter, filters[filter])
            elif type(filters[filter]) in (list, ):
                temp = ("{}".format(filters[filter])).replace("[", "(").replace("]",")").replace("'", '"')
                
                
                # temp = ("{}".format(filters[filter])).replace("[", "{").replace("]","}").replace("'", '"')
                filtersText += "{} in {} AND ".format(filter, temp)
            elif filters[filter] == None:
                filtersText += "{} is null AND ".format(filter)
            else:
                try:
                    if type(filters[filter]) in [unicode]:
                        filtersText += u"{}='{}' AND ".format(filter, filters[filter])
                        # filtersText += u"{}='{}' AND ".format(filter, filters[filter].replace("'", "''"))
                    else:
                        filtersText += "{}={} AND ".format(filter, filters[filter])
                except:
                    filtersText += "{}={} AND ".format(filter, filters[filter])
                    # filtersText += "{}={} AND ".format(filter, filters[filter])
                    
        return filtersText.rstrip("AND ")


    def modificar(self, table, fields, filters="", cursor=None):
        """ Returns error code """
        # print  'modificar()', table, fields, filters, cursor
        command = None

        if filters == u"":
            filters = {}
        try:
            command = u"UPDATE %s " % table
            fieldsText = ""
            for field in fields:
                if type(fields[field]) in (str, unicode):
                    if "'" in fields[field]:
                        fields[field] = fields[field].replace("'", "''")
                    fieldsText += u"%s='%s', " % (field, fields[field])
                elif fields[field] == None:
                    fieldsText += u"%s=null, " % field
                else:
                    fieldsText += "%s=%s, " % (field, fields[field])

            if fieldsText:
                command += "SET %s " % fieldsText.rstrip(", ")

            filtersText = ""
            for filter in filters:
                filtersText += u"%s='%s' AND " % (filter, filters[filter])

            if filtersText:
                command += u"WHERE %s " % filtersText.rstrip("AND ")

            # print(command)

            if not cursor:
                cursor = self._conn.cursor()
                cursor.execute(command)
                cursor.close()
            else:
                cursor.execute(command)

            self._conn.commit()
            
            self._lastMessage = self.app.errors['00000']

        except adapter.Error, e:
            self._lastMessage = self.app.errors['01100'] + ("command: {}".format(command.encode('utf8')), (sys.exc_info()[0], sys.exc_info()[1], traceback.format_tb(sys.exc_info()[2])))

            # logging.getLogger('system').error("{} - Handler.modificar()".format(messagePrefix))
            # logging.getLogger('system').error("    %s" % command.encode('utf8'))
            # logging.getLogger('system').error("    %s" % sys.exc_info()[1])
            raise


    def remove(self, table, **filters):
        try:
            command = u"DELETE FROM {} ".format(table)
            filtersText = ""
            for filter in filters:
                if type(filters[filter]) in (str, unicode):
                    filtersText += u"{}='{}' AND ".format(filter, filters[filter])
                else:
                    filtersText += "{}={} AND ".format(filter, filters[filter])
            if filtersText:
                command += u"WHERE {} ".format(filtersText.rstrip('AND '))

            # print(command.encode('utf8'))
            cursor = self._conn.cursor()
            result = cursor.execute(command)
            cursor.close()

            self._conn.commit()

            return result
        except:
            logging.getLogger('system').error("Handler.remove()")
            logging.getLogger('system').error("    {}".format(command.encode('utf8')))
            logging.getLogger('system').error("    {}".format(sys.exc_info()[1]))
            raise

    # def set(self, table, filters={}, **data):
    def set(self, table, **data):
        # print("""db.set()""")
        # print(123123, table, data)
        
        if table is 'attributes':
            # print('--------', data)
            if 'variable_id' in data:
                data['code'] = data.pop('variable_id')
            if 'tipo' in data:
                data['category'] = data.pop('tipo')
            # if 'tipo' in filters:
                # filters['category'] = filters.pop('tipo')
            if 'subtipo' in data:
                data['cast_'] = data.pop('subtipo')
            if 'nombre' in data:
                data['name'] = data.pop('nombre')
            # if 'nombre' in filters:
                # filters['name'] = filters.pop('nombre')
            if 'valor' in data:
                data['value'] = data.pop('valor')
            if 'referencia' in data:
                data['reference'] = data.pop('referencia')

        existent = None
        
        if 'id' in data.keys():
            idKey = 'id'
        elif 'code' in data.keys():
            # existent = self.get(table, code=data['code'])
            idKey = 'code'
            # id = data.pop(idKey)
        else:
            idKey0 = [x for x in data.keys() if x[-3:]=='_id' and x[:3]==table[:3]]

            if idKey0:
                idKey = idKey0[0]
                # id = data[idKey]
                # existent = self.get(table, **{idKey: id})
                # if existent:
                    # data.pop(idKey)
            else:
                idKey = None
        
        if idKey:
            existent = self.get(table, **{idKey:data[idKey]})
        else:
            existent = None

        # print(11103, idKey, existent)
        
        if existent:
            id = data.pop(idKey)
            
        
            command = """UPDATE {} SET """.format(table)
            pairsText = ""
            
            ## Creación de filtersText
            filtersText = ''
            # for filter in filters:
                # if type(filters[filter]) in [str, unicode, datetime.datetime, Decimal]:
                    # filtersText += u"{}='{}' AND ".format(filter, filters[filter].replace("'", "''"))
                # else:
                    # filtersText += "{}={} AND ".format(filter, filters[filter])
                
            for key in data.keys():
                if type(data[key]) in [str, unicode, datetime.datetime, Decimal]:
                    pairsText += u"{}='{}', ".format(key, data[key])
                elif type(data[key]) in [int]:
                    pairsText += "{}={}, ".format(key, data[key])
            if existent:
                command += u"{} WHERE {}={} ".format(pairsText.rstrip(', '), idKey, id)
            elif filtersText:
                command += u"{} WHERE {}".format(pairsText.rstrip(', '), filtersText.rstrip('AND '))

            # print(command.encode('utf8'))
            # self.execute(command)

        else:
            command = """INSERT INTO {} """.format(table)
            fieldsText = ""
            valuesText = ""
            for key in data.keys():
                if type(data[key]) in [str, unicode, datetime.datetime]:
                    fieldsText += "{}, ".format(key)
                    valuesText += u"'{}', ".format(data[key])
                elif data[key] is None:
                    fieldsText += "{}, ".format(key)
                    valuesText += "Null, "
                else:
                    fieldsText += "{}, ".format(key)
                    valuesText += "{}, ".format(data[key])
            command = u"{} ({}) VALUES ({})".format(command, fieldsText.rstrip(", "), valuesText.rstrip(", "))

        # print(command.encode('utf8'))

        self.execute(command)
        
        self.commit()
        
        # print(201)
        if existent:
            # print(202)
            dbData = self.get(table, **{idKey:id})
        else:
            # print(203)
            dbData = self.get(table, **data)
            
        # print(dbData)

        return dbData
        
        """
            Se updataba sólo si se recibía una key terminando en _id.
            Ahora se mantiene ese comportamiento for backward compatibility
            y se agrega el uso de filtros.
        """

    def attribute_get(self, **filters):
        return self.getAttribute(**filters)
        
    def attributes_get(self, **filters):
        return self.getAttributes(**filters)
        

    def getAttribute(self, **filters):
        
        result = self.get('attributes', **filters)
        
        return result
        
        try:
            if 'code' in filters:
                filters['variable_id'] = filters.pop('code')                
            if 'category' in filters:
                filters['tipo'] = filters.pop('category')
                if filters['tipo'] is 'place':
                    filters['tipo'] = 'lugar'
            if 'name' in filters:
                filters['nombre'] = filters.pop('name')
            if 'cast_' in filters:
                filters['subtipo'] = filters.pop('cast_')
                
            result = self.get('variables', **filters)
            
            result['code'] = result.pop('variable_id')                
            result['category'] = result.pop('tipo')
            if result['category'] is 'lugar':
                result['category'] = 'place'
            result['name'] = result.pop('nombre')
            result['value'] = result.pop('valor')
            result['reference'] = result.pop('referencia')
            result['cast_'] = result.pop('subtipo')
            result.pop('valor2')
            
            return result
        except:
            print ("    ", sys.exc_info())
            print ("    ", filters)
            print (result)
            raise


    def getAttributes(self, **data):
        # print("""db.Handler.getAttributes()""")
        # print(313, data)
        
        if 'variable_id' in data:
            data['code'] = data.pop('variable_id')
        if 'tipo' in data:
            data['category'] = data.pop('tipo')
        # if 'tipo' in filters:
            # filters['category'] = filters.pop('tipo')
        if 'subtipo' in data:
            data['cast_'] = data.pop('subtipo')
        if 'nombre' in data:
            data['name'] = data.pop('nombre')
        # if 'nombre' in filters:
            # filters['name'] = filters.pop('nombre')
        if 'valor' in data:
            data['value'] = data.pop('valor')
        if 'referencia' in data:
            data['reference'] = data.pop('referencia')
        
        
        if 'order' in data:
            if type(data['order']) == str:
                if 'nombre' in data['order']:
                    data['order'] = data['order'].replace('nombre', 'name')
            elif type(data['order']) == list:
                data['order'].pop('nombre')
                data['order'].append('name')
        
        results = self.getMany('attributes', filters=data)

        for result in results:
            if type(result['value']) in [str, unicode]:
                if '::D' in result['value']:
                    result['value'] = Decimal(result['value'].replace('::D', ''))
        
        return results
        
            
        if 'code' in filters:
            filters['variable_id'] = filters.pop('code')                
        if 'category' in filters:
            filters['tipo'] = filters.pop('category')
            if filters['tipo'] is 'place':
                filters['tipo'] = 'lugar'
        if 'name' in filters:
            filters['nombre'] = filters.pop('name')
        if 'cast_' in filters:
            filters['subtipo'] = filters.pop('cast_')
            
        # print(filters)
        
        results = self.getMany('variables', filters=filters)
        
        for result in results:
            result['code'] = result.pop('variable_id')                
            result['category'] = result.pop('tipo')
            if result['category'] is 'lugar':
                result['category'] = 'place'
            result['name'] = result.pop('nombre')
            result['value'] = result.pop('valor')
            if type(result['value']) in [str, unicode]:
                if '::D' in result['value']:
                    result['value'] = Decimal(result['value'].replace('::D', ''))
            result['reference'] = result.pop('referencia')
            result['cast_'] = result.pop('subtipo')
            result.pop('valor2')
        return results


    # def tipsActive(self):
        # if not self.get('variables', tipo=u'general', nombre=u'showTips'):
            # self.set('variables', tipo=u'general', nombre=u'showTips', valor='1')
        # return not not self.get('variables', tipo=u'general', nombre=u'showTips')['valor']


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d




def createTable(name, definition):
    f=z
    cur = con.cursor()
    cur.execute("""CREATE TABLE ? (?)""", (name, definition))
    cur.commit()


def setPolizasRow(row):
    f=z
    cur = con.cursor()
    cur.execute("INSERT INTO polizas ( folio, fecha_registro) VALUES (?, ?)", row)
    con.commit()


def getRow(table, keys):
    f=z
    cur = con.cursor()
    cur.execute("SELECT * FROM polizas WHERE folio='1'")
    data = cur.fetchone()
    return data


