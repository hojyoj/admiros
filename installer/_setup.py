# -*- coding: utf-8 -*-

 ###############################################
 ##                                             ##
 ##   Setup                                      ##
 ##                                              ##
 ##   Admiros                                    ##
 ##                                              ##
 ##   by Críptidos Digitales                     ##
 ##   GPL (c)2008                                ##
  ##                                             ##
    ###############################################

"""
"""

# Sacado del 4.19 del python cookbook

import sys, os, fnmatch
from distutils.core import setup
import py2exe

sys.path.append("..")
import Admiros.admiros as admiros


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


app = admiros.App([])

try:
    ## Raise exception if excepthook is deactivated
    file('../admiros.py').read().index('\nsys.excepthook')


    icons = [x for x in filterFiles('../', '*.png') if 'logo.png' not in x and 'icon.png' not in x]

    setup(
        name = u"{}".format(app.name),
        version = u"{}".format(app.version),
        windows = [
            u"../admiros.py",
            {
            "icon_resources": [(0, "../icon.ico")],
            "script": "../admiros.py"
            }
        ],
        data_files = [
            ('imageformats', ['C:\\Python27/Lib/site-packages/PyQt4/plugins/imageformats/qico4.dll', 'C:\\Python27/Lib/site-packages/PyQt4/plugins/imageformats/qjpeg4.dll']),
            ('', ['C:\\Python27/Lib/site-packages/PyQt4/QtCore4.dll', 'C:\\Python27/Lib/site-packages/PyQt4/QtGui4.dll']),

            ('', icons),
            
            # ('', ['../CS']),

            ('documentos', filterFiles('../documentos', '*.txt'))
            # , ('', ['../admiros.exe.log'])
        ],
        options = {
            "py2exe": {
                "optimize": 2,
                "ascii": True,
                "includes": ["sip", "encodings.utf_8", "encodings.ascii", "PyQt4.QtSql", "inspect"],
                "excludes": ['difflib', 'doctest', 'optparse', 'pdb', 'pickle', 'PIL', 'pydoc', 'pyreadline', "_ssl", 'Tkinter', 'unittest', 'agents'],
                # Do not exclude : calendar
                "dll_excludes": ['API-MS-Win-Core-LocalRegistry-L1-1-0.dll', 'MPR.dll', 'MSWSOCK.DLL', 'POWRPROF.dll', 'profapi.dll', 'QtCore4.dll', 'QtGui4.dll', "QtNetwork4.dll", "MSVCR80.dll", "MSVCP90.dll", "secur32.dll", "shfolder.dll", 'userenv.dll', "w9xpopen.exe", 'wtsapi32.dl'],
                'packages': ["lxml"]
                # "bundle_files": 1
            }
        },
        zipfile = None
    )

except:
    print ('Error')
    print ('\nOlvidaste activar exceptHook y desviar stderr?')


'''
  ~~~~~~

  1.4   Include CS file to replace damaged one


'''
