

import sys, os
import base64
import hashlib
import datetime



def _hwid(index=0):
    return int(float.fromhex(ifaces()[index].replace(':', '')[:4]))


def ifaces():
    try:
        if sys.platform == 'win32':
            ifaces = [x.split(':')[1].strip().replace('-',':') for x in os.popen("ipconfig /all") if x.lstrip().startswith('Physical Address') or ('Direcci' in x and 'sica' in x)]
        else:
            ifaces = [x.split()[4] for x in os.popen("/sbin/ifconfig") if ' Link' in x and ' HWaddr' in x]
    except:
        logging.error((u"@access.Form.__init__() ifaces\n    %s\n    %s" % (ifaces, sys.exc_info()[1])).encode('utf8'))
    return ifaces


def isValid(id, key):
    """km.isValid()"""

    date = datetime.datetime.today()
    oneDay = datetime.timedelta(days=1)
    days = 0
    a = 1984
    index = 0

    id = hashlib.sha1("%s" % id).hexdigest().replace('a','').replace('b','').replace('c','').replace('d','').replace('e','').replace('f','')[:4]

    while index < len(ifaces()) and a != key:

        hwidTmp = int(float.fromhex(ifaces()[index].replace(':', '')[:4]))

        while days < 1100 and a != key:
            hwid = hashlib.sha1("%s"%hwidTmp).hexdigest().replace('a','').replace('b','').replace('c','').replace('d','').replace('e','').replace('f','')[:4]
            lifeEnd = date.strftime("%Y%m%d")

            x = hashlib.sha1("%s%s%s%s" % (hwid, id, 2, lifeEnd)).hexdigest().replace('a','').replace('b','').replace('c','').replace('d','').replace('e','').replace('f','')
            a = "%s-%s-%s" % (x[:4], x[4:8], x[8:12])

            date = date + oneDay
            days += 1

        days = 0
        index += 1

    return a == key


def encode(id, v, s):
    hwid = _hwid()
    return base64.b32encode(
    ("%s%s%s%s" % (
    hashlib.sha1("%s"%hwid).hexdigest().replace('a','').replace('b','').replace('c','').replace('d','').replace('e','').replace('f','')[:4],
    hashlib.sha1("%s"%id).hexdigest().replace('a','').replace('b','').replace('c','').replace('d','').replace('e','').replace('f','')[:4],
    "%s" % v,
    "%s" % s)
    )[::-1]
    ).rstrip('==').rstrip('=')


def decode(data):
    padding = '===='
    x = base64.b32decode(data + padding[:4-len(data) % 4])[::-1]
    hwid = x[:4]
    id   = x[4:8]
    v    = x[8:9]
    s    = x[9:]
    return hwid, id, v, s


def scramble(a, b):
    return "".join([x for i,x in enumerate("%s%s" % (a,b)) if not (i%3)])


def reEncode(data, lifeend):
    hwid, id, v, s = decode(data)
    x = hashlib.sha1("%s%s%s%s" % (hwid, id, v, lifeend.strftime("%Y%m%d"))).hexdigest().replace('a','').replace('b','').replace('c','').replace('d','').replace('e','').replace('f','')
    x = "%s-%s-%s" % (x[:4], x[4:8], x[8:12])
    return x

