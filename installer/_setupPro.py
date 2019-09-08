# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Setup                                      ##
 ##                                              ##
 ##   Admiros Pro                                ##
 ##                                              ##
 ##   by Críptidos Digitales                     ##
 ##   GPL (c)2012                                ##
  ##                                             ##
    ###############################################

"""
"""

# Sacado del 4.19 del python cookbook

import sys, os, fnmatch
from distutils.core import setup
import py2exe

sys.path.append("..")
import Admiros.admirosPro as admirosPro


def listFiles(root, patterns='*', recurse=0, return_folders=0):
    """ Expand patterns from semicolon-separated string to list """
    pattern_list = patterns.split(';')

    """ Collect input and output arguments into one bunch """
    class Bunch:
        def __init__(self, **kwds):
            self.__dict__.update(kwds)

    arg = Bunch(recurse=recurse, pattern_list=pattern_list, return_folders=return_folders, results=[])

    def visit(arg, dirname, files):
        """ Append to arg.results all relevant files (and perhaps folders) """
        for name in files:
            fullname = os.path.normpath(os.path.join(dirname, name))
            if arg.return_folders or os.path.isfile(fullname):
                for pattern in arg.pattern_list:
                    if fnmatch.fnmatch(name, pattern):
                        arg.results.append(fullname)
                        break

        """ Block recursion if recursion was disallowed """
        if not arg.recurse:
            files[:] = []

    os.path.walk(root, visit, arg)
    return arg.results


def filterFiles(root, patterns='*', recurse=0, return_folders=0):
    archivos = listFiles(root, patterns, recurse, return_folders)
    filtered = []
    estosDirectoriosNo = ('CVS', 'DIST', 'BUILD', 'ATICO', 'RESOURCES', '.svn')
    for archivo in archivos:
        omit = False
        for directorio in estosDirectoriosNo:
            if directorio in archivo.upper():
                omit = True
        if not omit:
            filtered.append(archivo)
    return filtered


app = admirosPro.MyApp([])

setup(
    name = u"{}".format(app.info['name']),
    version = u"{}".format(app.info['version']),
    windows = [
        u"../admirosPro.py",
        {"icon_resources": [(0, "../files/icon.ico")],
        "script": "../admirosPro.py"
        }
    ],
    data_files = [
        ('imageformats', ['C:\\Python27/Lib/site-packages/PyQt4/plugins/imageformats/qico4.dll']),
        ('', filterFiles('.', '*.png')),
        ('documentos', filterFiles('../documentos', '*.txt')),
    ],
    options = {
        "py2exe": {
            "ascii": True,
            "includes": ["sip", "encodings.utf_8", "PyQt4.QtSql"],
            "excludes": ['calendar', 'difflib', 'doctest', '_ssl', 'inspect', 'optparse', 'pdb', 'pickle', 'PIL', 'pyreadline', 'unittest'],
            "dll_excludes": ["QtCore4.dll", "QtGui4.dll", "QtNetwork4.dll", "MSVCP90.dll", "w9xpopen.exe", "secur32.dll", "shfolder.dll"],
            "bundle_files": 1
        }
    },
    zipfile = None
)

