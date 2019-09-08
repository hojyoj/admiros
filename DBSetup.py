# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Database Initialization                    ##
 ##                                              ##
 ##                                              ##
 ##   for Admiros                                ##
 ##   by Críptidos Digitales                     ##
 ##   (c)2008                                    ##
  ##                                             ##
    ###############################################

"""
"""

from __future__ import print_function

import sys
import logging

import km

from PyQt4 import QtCore


def createTableAgents(cur):
    print ("\n    DBSetup.createTableAgents()")
    cur.execute("DROP TABLE IF EXISTS agents")
    cur.execute("""CREATE TABLE agents (
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
        )"""
    )
    print ("    DBSetup.createTableAgents() - Succeded")


def createTableAttributes(cur):
    print ("\n    DBSetup.createTableAttributes()")
    try:
        cur.execute("DROP TABLE IF EXISTS attributes")
        cur.execute("""CREATE TABLE attributes (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            code    INTEGER,
            category  TEXT,
            name    TEXT,
            value   TEXT DEFAULT '',
            reference TEXT DEFAULT '',
            cast_   TEXT DEFAULT ''
            )"""
        )
        print ("    DBSetup.createTableAttributes() - Succeded")
    except:
        print ("    CREATE TABLE attributes failed")
        print (sys.exc_info())


def createTablePolizas(cur):
    print ("\n    DBSetup.createTablePolizas()")
    cur.execute("DROP TABLE IF EXISTS polizas")
    cur.execute("""CREATE TABLE polizas (
        poliza_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id    INTEGER REFERENCES agents,
        cliente_id  INTEGER REFERENCES clientes,
        aseguradora_id  INTEGER REFERENCES rols,
        folio       TEXT,
        tiposeguro_id   INTEGER REFERENCES variables (referencia),
        fecharegistro   TEXT,
        iniciocobertura TEXT,
        terminocobertura TEXT,
        tipopago_id INTEGER REFERENCES variables,
        prima       TEXT,
        descuento1  TEXT DEFAULT '',
        descuento2  TEXT DEFAULT '',
        cargo1      TEXT DEFAULT '',
        cargo2      TEXT DEFAULT '',
        gasto1      TEXT DEFAULT '',
        gasto2      TEXT DEFAULT '',
        impuesto    TEXT DEFAULT '',
        monto       TEXT,
        moneda_id   INTEGER REFERENCES variables,
        paridad     TEXT DEFAULT '',
        status_id   INTEGER REFERENCES variables,
        comentario  TEXT DEFAULT ''
        )"""
    )
    print ("    DBSetup.createTablePolizas() - Succeded")


def createTableClientes(cur):
    print ("\n    DBSetup.createTableClientes()")
    cur.execute("DROP TABLE IF EXISTS clientes")
    cur.execute("""CREATE TABLE clientes (
        curp        TEXT DEFAULT '',
        rfc         TEXT DEFAULT '',
        agent_id    INTEGER REFERENCES agents,
        cliente_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombres     TEXT,
        apellidos   TEXT DEFAULT '',
        fecharegistro TEXT DEFAULT '',
        fechanacimiento TEXT DEFAULT '',
        genero      TEXT DEFAULT '',
        estadocivil TEXT DEFAULT '',
        conyuge     TEXT DEFAULT '',
        hijos       TEXT DEFAULT '',
        lugar       TEXT DEFAULT '',
        estado      INTEGER REFERENCES estados,
        ciudad      INTEGER REFERENCES ciudades,
        colonia     TEXT DEFAULT '',
        codigopostal TEXT DEFAULT '',
        calle       TEXT DEFAULT '',
        interior    TEXT DEFAULT '',
        telefono1   TEXT DEFAULT '',
        telefono2   TEXT DEFAULT '',
        telefono3   TEXT DEFAULT '',
        telefono4   TEXT DEFAULT '',
        email       TEXT DEFAULT ''
        )"""
    )
    print ("    DBSetup.createTableClientes() - Succeded")


def createTableEstados(cur):
    print ("\n    DBSetup.createTableEstados()")
    cur.execute("DROP TABLE IF EXISTS estados")
    cur.execute("""CREATE TABLE estados (
        estado_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre      TEXT,
        alias       TEXT
        )"""
    )
    print ("    DBSetup.createTableEstados() - Succeded")


def createTableMonedas(cur):
    print ("\n    DBSetup.createTableMonedas()")
    cur.execute("DROP TABLE IF EXISTS monedas")
    cur.execute("""CREATE TABLE monedas (
        moneda_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre      TEXT,
        multiplo    REAL
        )"""
    )
    print ("    DBSetup.createTableMonedas() - Succeded")


def createTablePagos(cur):
    print ("\n    DBSetup.createTablePagos()")
    cur.execute("DROP TABLE IF EXISTS pagos")
    cur.execute("""CREATE TABLE pagos (
        pago_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        referencia  TEXT DEFAULT '',
        poliza_id   INTEGER REFERENCES polizas,
        fecha       TEXT,
        monto       TEXT,
        moneda      INTEGER REFERENCES variables,
        multiplo    TEXT DEFAULT '',
        fecha2      TEXT DEFAULT '',
        monto2      TEXT DEFAULT '',
        moneda2     INTEGER REFERENCES variables,
        multiplo2   TEXT DEFAULT ''
        )"""
    )
    print ("    DBSetup.createTablePagos() - Succeded")


def createTableCiudades(cur):
    print ("\n    DBSetup.createTableCiudades()")
    cur.execute("DROP TABLE IF EXISTS ciudades")
    cur.execute("""CREATE TABLE ciudades (
        ciudad_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre      TEXT,
        estado_id   INTEGER REFERENCES estados
        )"""
    )
    print ("    DBSetup.createTableCiudades() - Succeded")


def createTableColonias(cur):
    print ("\n    DBSetup.createTableColonias()")    
    cur.execute("DROP TABLE IF EXISTS colonias")
    cur.execute("""CREATE TABLE colonias (
        colonia_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre      TEXT,
        ciudad_id   INTEGER REFERENCES ciudades
    )""")
    print ("    DBSetup.createTableColonias() - Succeded")


def createViewPolizas(cur):
    print ("\n    DBSetup.createViewPolizas()")
    # cur.execute("DROP VIEW IF EXISTS polizas")
    cur.execute("""CREATE VIEW vpolizas AS SELECT
    
        poliza_id, folio, 
        polizas.fecharegistro AS fecharegistro, 
        (iniciocobertura || ' - ' || terminocobertura) AS cobertura, 
        terminocobertura, 
        julianday(terminocobertura) AS terminocobertura2, 
        datetime(terminocobertura) AS terminocobertura3,
        
        paridad, monto, comentario,
        prima, descuento1, cargo1, cargo2, gasto1,
        
        clientes.cliente_id AS cliente_id, (clientes.nombres ||' '|| clientes.apellidos) AS cliente_nombre, clientes.telefono1 AS cliente_telefonos,
        
        agents.agent_id AS agent_id, (agents.names ||' '|| agents.names2) AS agent_name,
        
        status.referencia AS status_id, status.nombre AS status_nombre, status.subtipo AS status_subtipo,
        
        tipos.referencia AS tiposeguro_id, tipos.nombre AS tiposeguro_nombre,
        
        currencies.variable_id AS moneda_id, currencies.nombre AS moneda_nombre,
        
        slices.variable_id AS tipopago_id, slices.nombre AS tipopago_nombre
        
        
        FROM polizas
        LEFT JOIN agents ON polizas.agent_id = agents.agent_id
        LEFT JOIN clientes ON polizas.cliente_id = clientes.cliente_id
        LEFT JOIN attributes AS currencies ON polizas.moneda_id = currencies.id
        LEFT JOIN attributes AS slices ON polizas.tipopago_id = slices.id
        LEFT JOIN attributes AS status ON polizas.status_id = status.reference AND status.category = 'status'
        LEFT JOIN attributes AS tipos ON polizas.tiposeguro_id = tipos.reference AND tipos.category = 'tiposeguro'
        """)
    print ("\n    DBSetup.createViewPolizas() - Succeded")


def create(db):
    print ("""    DBSetup.create()""")

    try:
        cur = db.cursor()

        createTableAttributes(cur)
        createTableAgents(cur)
        createTablePolizas(cur)
        createTableClientes(cur)
        createTablePagos(cur)
        createTableEstados(cur)
        createTableCiudades(cur)
        createTableColonias(cur)
        createTableSiniestros(cur)
        db.commit()

        try:
            createViewPolizas(cur)
            db.commit()
        except:
            logging.getLogger('system').critical(u"    No pude recrear vPolizas")
            raise

        cur.close()

    except:
        print ("    DBSetup.create() skipped")
        logging.getLogger('system').critical(u"DBSetup.create()\n    %s" % sys.exc_info()[1])
        raise


def init(db):
    print ("""    DBSetup.init()""")

    try:
        cur = db.cursor()

        estados = ((u"Aguascalientes", u"Ags."), (u"Baja California", u"B.C."),
        (u"Baja California Sur", u"B.C.S."),
        (u"Campeche", u"Camp"), (u"Chiapas", u"Chis."), 
        (u"Chihuahua", u"Chih"), (u"Coahuila", u"Coah"),
        (u"Colima", u"Col."),
        (u"Distrito Federal", u"D.F."), (u"Durango", u"Dgo."), 
        (u"Estado de México", u"Edo. Mex."),
        (u"Guanajuato", u"Gto."), (u"Guerrero", u"Gro."), 
        (u"Hidalgo", u"Hgo."), (u"Jalisco", u"Jal."),
        (u"Michoacán", u"Mich."), (u"Morelos", u"Mor."),
        (u"Nayarit", u"Nay."), (u"Nuevo León", u"N.L."),
        (u"Oaxaca", "uOax."), (u"Puebla", u"Pue."), (u"Querétaro", u"Qro"), 
        (u"Quintana Roo", u"QRoo"),
        (u"San Luis Potosí", u"S.L.P."),
        (u"Sinaloa", u"Sin."), (u"Sonora", u"Son."), (u"Tabasco", u"Tab."), 
        (u"Tamaulipas", u"Tamps"),
        (u"Tlaxcala", u"Tlax."), (u"Veracruz", u"Ver"), (u"Yucatán", u"Yuc."), 
        (u"Zacatecas", u"Zac"))

        cur.executemany(u"INSERT INTO estados (nombre, alias) VALUES (?, ?)", estados)
        db.commit()

        df = db.get("estados", alias="D.F.")
        jal = db.get("estados", alias="Jal.")
        sin = db.get("estados", alias="Sin.")
        ciudades = []
        ciudades.append((u"Guadalajara", jal['estado_id']))
        ciudades.append((u"México", df['estado_id']))
        ciudades.append((u"Los Mochis", sin['estado_id']))
        cur.executemany(u"INSERT INTO ciudades (nombre, estado_id) VALUES (?, ?)", ciudades)
        db.commit()

        status = (
            ('status', u"Pagada", 0, 1),
            ('status', u"Pendiente de pago", 1, 1),
            ('status', u"Renovada", 2, 0),
            ('status', u"Expirada", 3, 0),
            ('status', u"Cancelada", 4, 0),
            ('status', u"No pagada", 5, 0),
            ('status', u"Cotizacion", 7, 0),
            ('status', u"Temprana", 8, 1))
        cur.executemany(u"""INSERT INTO variables (tipo, nombre, referencia, subtipo) VALUES (?, ?, ?, ?)""", status)

        ## LUGARES
        lugares = [
            (u'lugar', u'Acapulco, Gro.'),
            (u'lugar', u'Aguascalientes, Ags.'),
            (u'lugar', u'Campeche, Camp.'),
            (u'lugar', u'Cd. Juarez, Chih.'),
            (u'lugar', u'Cd. Obregón, Son.'),
            (u'lugar', u'Cd. Victoria, Tamps.'),
            (u'lugar', u'Chetumal, QRoo.'),
            (u'lugar', u'Chihuahua, Chih.'),
            (u'lugar', u'Chilpancingo, Gro.'),
            (u'lugar', u'Colima, Col.'),
            (u'lugar', u'Culiacán, Sin.'),
            (u'lugar', u'Cuernavaca, Mor.'),
            (u'lugar', u'Durango, Dgo.'),
            (u'lugar', u'Guadalajara, Jal.'),
            (u'lugar', u'Guanajuato, Gto.'),
            (u'lugar', u'Guasave, Sin.'),
            (u'lugar', u'Hermosillo, Son.'),
            (u'lugar', u'Jalapa, Ver.'),
            (u'lugar', u'La Paz, B.C.S.'),
            (u'lugar', u'Los Mochis, Sin.'),
            (u'lugar', u'Mazatlán, Sin.'),
            (u'lugar', u'Mérida, Yuc.'),
            (u'lugar', u'Mexicali, B.C.'),
            (u'lugar', u'México, D.F.'),
            (u'lugar', u'Monterrey, N.L.'),
            (u'lugar', u'Morelia, Mich.'),
            (u'lugar', u'Navojoa, Son.'),
            (u'lugar', u'Nogales, Son.'),
            (u'lugar', u'Oaxaca, Oax.'),
            (u'lugar', u'Pachuca, Hgo.'),
            (u'lugar', u'Puebla, Pue.'),
            (u'lugar', u'Queretaro, Qro.'),
            (u'lugar', u'Saltillo, Coah.'),
            (u'lugar', u'San Luis Potosí, S.L.P.'),
            (u'lugar', u'Tepic, Nay.'),
            (u'lugar', u'Tijuana, B.C.'),
            (u'lugar', u'Tlaxcala, Tlax.'),
            (u'lugar', u'Toluca, Edo.Mex.'),
            (u'lugar', u'Tuxtla Gutierrez, Chis.'),
            (u'lugar', u'Villahermosa, Tab.'),
            (u'lugar', u'Veracruz, Ver.'),
            (u'lugar', u'Zacatecas, Zac.')
            ]
        cur.executemany(u"""INSERT INTO variables (tipo, nombre) VALUES (?, ?)""", lugares)

        tiposPoliza = ((1, u"Autos", u''), (2, u"Vida", u'exento'), (3, u"Gastos médicos", u''), (4, u"Daños", u''), (5, u"Equipo de contratista", u''), (6, u"Accidentes escolares", u''))
        cur.executemany(u"INSERT INTO variables (tipo, referencia, nombre, subtipo) VALUES ('tiposeguro', ?, ?, ?)", tiposPoliza)
        db.commit()

        tiposPago = (("Anual", "A", 12), ("Semestral", "S", 6), ("Trimestral", "T", 3), ("Mensual", "M", 1))
        cur.executemany(u"""INSERT INTO variables (tipo, nombre, valor2, valor) VALUES ('tipopago', ?, ?, ?)""", tiposPago)
        db.commit()

        monedas = (("Pesos", '', 1.0, 'M.N.'), ("Dolares", 'exenta', 12.35, 'USD'))
        cur.executemany(u"""INSERT INTO variables (tipo, nombre, subtipo, valor, valor2) VALUES ('moneda', ?, ?, ?, ?)""", monedas)
        db.commit()

        generales = (("proteccion", "1"), ('rutaDocumentos', 'documentos'), ('backupPath', ''), ('IVA', '16'), ('IVAOld', '15'), ("runCount", '0'), ("showTips", '1'), ("renewedHidden", '2'))
        cur.executemany(u"""INSERT INTO variables (tipo, nombre, valor) VALUES ('general', ?, ?)""", generales)
        db.commit()

        cur.execute(u"""INSERT INTO variables (tipo, nombre, valor, valor2) VALUES ('general', 'programa', 'semanal', ?)""", (str(QtCore.QDate().currentDate().toString('yyyy-MM-dd')),))

        eventos = ((u'Expiración', 1), (u'Cobros', 2), (u'Pagos', 3))
        cur.executemany(u"INSERT INTO variables (tipo, nombre, referencia) VALUES ('eventoReporte', ?, ?)", eventos)
        db.commit()

        date1 = "%s-01" % QtCore.QDate().currentDate().toString("yyyy-MM")
        date2 = "%s-%s" % (QtCore.QDate().currentDate().toString("yyyy-MM"), QtCore.QDate().currentDate().daysInMonth())
        date3 = "01%s" % QtCore.QDate.currentDate().toString("MMMyy")
        date4 = "%s%s" % (QtCore.QDate().currentDate().daysInMonth(), QtCore.QDate.currentDate().toString("MMMyy"))

        vencimiento = db.get("variables", tipo=u'eventoReporte', referencia=1)
        cobro = db.get("variables", tipo=u'eventoReporte', referencia=2)
        pago = db.get("variables", tipo=u'eventoReporte', referencia=3)

        reportes = [
            (u'reportePólizas', u'Todas las pólizas', u''),
            (u'reportePólizas', u'Sólo pólizas Activas', u'Status -11'),
            (u'reportePólizas', u'Expiración Mes actual', u'Evento 1 TM'),
            (u'reportePólizas', u'Expiración Mes próximo', u'Evento 1 NM'),
            (u'reportePólizas', u'Cobros del Mes actual', u'Evento 2 TM Status 0, 1, 3, 5'),
            (u'reportePólizas', u'Pagos del Mes actual', u'Evento 3 TM Status 0, 1, 3, 5')]
        cur.executemany(u"""INSERT INTO variables (tipo, nombre, valor) VALUES (?, ?, ?)""", reportes)

        db.modificar('variables', {'subtipo':u'default'}, {'variable_id':db.get('variables', tipo=u'reportePólizas', nombre=u'Sólo pólizas Activas')['variable_id']})

        db.commit()

        cur.close()

    except:
        print ("    DB.Setup.init() Skipped")
        logging.getLogger('system').critical(u"DBSetup.init()\n    %s" % sys.exc_info()[1])


""" changelog

version 2
    Primera versión en la que se incluye el registro version en variables


"""