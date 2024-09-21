# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    unicode = str

    from urllib.parse import unquote
else:
    from urllib import unquote


import xbmc, re, base64, random

from platformcode import logger

from core import jsontools


class EstructuraInicial(object):
    def __init__(self, data):
        self.data = data

        self.funcion = ''
        self.lista = []

        self.detectado, self.msg = self._detectar_estructura()

        if self.detectado:
            matches = re.compile("(%s\('([^']*)',\s*'([^']*)'\))" % self.funcion).findall(self.data)

            for i, match in enumerate(matches):
                x = self.unhex(match[2]) if match[2][:2] == '\\x' else match[2]
                valor = self._resolver_funcion(int(match[1], 16), x)

                if "'" not in valor:
                    self.data = self.data.replace(match[0], "'"+valor+"'")
                elif '"' not in valor:
                    self.data = self.data.replace(match[0], '"'+valor+'"')
                else:
                    logger.info('Problema cometes no previst 1')
                    return

            matches = re.compile("(%s\(\\\\'(.*?)\\\\',\s*\\\\'(.*?)\\\\'\))" % self.funcion).findall(self.data)

            for i, match in enumerate(matches):
                x = self.unhex(match[2]) if match[2][:2] == '\\x' else match[2]
                valor = self._resolver_funcion(int(match[1], 16), x)

                if "'" not in valor:
                    self.data = self.data.replace(match[0], "\\'"+valor+"\\'")
                elif '"' not in valor:
                    self.data = self.data.replace(match[0], '\\"'+valor+'\\"')
                else:
                    logger.info('Problema cometes no previst 2')
                    return

            matches = re.compile("(%s\('([^']*)'\))" % self.funcion).findall(self.data)
            for i, match in enumerate(matches):
                valor = self._resolver_funcion(int(match[1], 16), '')

                if "'" not in valor:
                    self.data = self.data.replace(match[0], "'"+valor+"'")
                elif '"' not in valor:
                    self.data = self.data.replace(match[0], '"'+valor+'"')
                else:
                    logger.info('Problema cometes no previst 3')
                    return

            matches = re.compile("(%s\(\\\\'(.*?)\\\\'\))" % self.funcion).findall(self.data)
            for i, match in enumerate(matches):
                valor = self._resolver_funcion(int(match[1], 16), '')

                if "'" not in valor:
                    self.data = self.data.replace(match[0], "\\'"+valor+"\\'")
                elif '"' not in valor:
                    self.data = self.data.replace(match[0], '\\"'+valor+'\\"')
                else:
                    logger.info('Problema cometes no previst 4')
                    return

    def _detectar_estructura(self):
        m = re.search('var (\w*)\s*=\s*\[(.*?)\];', self.data)
        if not m: return False, ''

        nombre = m.group(1)
        self.lista  = m.group(2).split(',')

        for i, v in enumerate(self.lista): self.lista[i] = v.strip()[1:-1]

        if self.lista[0][:2] == '\\x':
            for i, v in enumerate(self.lista): self.lista[i] = self.unhex(v)

        self.data = self.data.replace(m.group(0), '')

        m = re.search('\(function\(.*?}\(%s,\s*([^\)]*)\)\);' % nombre, self.data, flags=re.DOTALL)
        if not m: return False, ''

        numero = int(m.group(1), 0)

        self.data = self.data.replace(m.group(0), '')

        for x in range(numero): self.lista.append(self.lista.pop(0))

        m = re.search('var (\w*)\s*=\s*function\s*\(\s*[^,]*,\s*[^\)]*\)\s*\{.*?\}\s*else\{\s*\w*\s*=\s*\w*;\s*\}\s*return \w*;\s*\};', self.data)
        if not m: return False, ''

        self.funcion = m.group(1).strip()

        self.novedad = ''
        if '=(0x3+_0x' in m.group(0): self.novedad = '1'
        if "=(0x3+Math['pow'](0x7c,0x0)+_0x" in m.group(0): self.novedad = '2'

        self.data = self.data.replace(m.group(0), '')

        return True, ''

    def _resolver_funcion(self, num, s=''):
        r = str(self.lista[num])

        r = base64.b64decode(r)
        x = ''

        for y in range(len(r)):
            x += '%' + ( '00' + hex(ord(r[y]))[2:] )[-2:]

        r = unicode(urllib.unquote(x), 'utf8')

        if s == '': return r

        t = range(256)

        if self.novedad == '1':
            for y in range(256): t[y] = (3 + y) % 256
        elif self.novedad == '2':
            for y in range(256): t[y] = (4 + y) % 256

        u = 0; w = ''

        for y in range(256):
            u = (u + t[y] + ord(s[(y % len(s))]) ) % 256;
            v = t[y]
            t[y] = t[u]
            t[u] = v

        A = 0; u = 0

        for y in range(len(r)):
            A = (A + 1) % 256
            u = (u + t[A]) % 256
            v = t[A]
            t[A] = t[u]
            t[u] = v
            w += unichr( ord(r[y]) ^ t[(t[A] + t[u]) % 256] )

        return w.encode('utf8')


    def unhex(self, txt):
        return re.sub("\\\\x[a-f0-9][a-f0-9]", lambda m: m.group()[2:].decode('hex'), txt)


def custom_unhex(txt):
    return re.sub('\\\\x([a-fA-F0-9][a-fA-F0-9])', lambda patron2: str(chr(int(patron2.group(1), 16))), txt)


def obfs(data, key, n=126):
    logger.info()

    if isinstance(data, bytes): data = data.decode('utf-8', 'strict')

    chars = list(data)

    for i in range(0, len(chars)):
        c = ord(chars[i])

        if c <= n:
            number = (ord(chars[i]) + key) % n
            chars[i] = chr(number)

    return "".join(chars)


def hdfull_providers(data):
    logger.info()

    data = custom_unhex(data)

    m = re.search('var\s*(\w*)\s*=\s*\[(.*?)\];', data)
    if not m: return ''

    nombre = m.group(1)
    lista  = m.group(2).split(',')

    for i, v in enumerate(lista):
        lista[i] = v.strip()[1:-1]

    data = re.sub("%s\[(\d+)\]" % nombre, lambda m: '"' + lista[int(m.group(1))] + '"', data)

    pt = re.compile('p\[(\d+)\]\s*=\s*\{"t":"([^"]*)').findall(data)
    if not pt: pt = re.compile('p\[(\d+)\]\s*=\s*\{\'t\':"([^"]*)').findall(data)

    dpt = dict(pt)

    if len(dpt) == 0: return hdfull_providers_01(data)

    pl = re.compile('p\[(\d+)\]\s*=\s*\{.*?"l":.*?return ([^}]*)', flags=re.DOTALL).findall(data)
    if not pl: pl = re.compile('p\[(\d+)\]\s*=\s*\{.*?\'l\':.*?return ([^}]*)', flags=re.DOTALL).findall(data)

    dpl = dict(pl)

    if len(dpl) == 0: return hdfull_providers_01(data)

    p = {}

    for num in dpl:
        t = dpt[num] if num in dpt else ''

        l = re.sub("(_0x[a-zA-Z0-9]+)", '_code_', dpl[num])
        p[num] = [t, l]

    return p


def hdfull_providers_01(data):
    logger.info()

    matches = re.compile("(var \w+\s*=\s*\[.*?\];\(function\(.*?)\n").findall(data)

    if not matches: return ''

    net = EstructuraInicial(matches[0])

    if not net.detectado: return ''

    net.data = re.sub("p\[0x([a-f0-9]+)\]", lambda m: 'p[' + str(int(m.group(1), 16)) + ']', net.data)

    pt = re.compile("p\[(\d+)\]\['t'\]\s*=\s*'([^']*)'").findall(net.data)

    dpt = dict(pt)

    pl = re.compile("p\[(\d+)\]\['l'\]\s*=.*?return ([^;]*);", flags=re.DOTALL).findall(net.data)

    dpl = dict(pl)

    p = {}

    for num in dpl:
        t = dpt[num] if num in dpt else ''

        l = re.sub("(_0x[a-f0-9]+)", '_code_', dpl[num])
        p[num] = [t, l]

    return p


def uptostream_sumes(data):
    matches = re.findall("('([^']*)'\s*\+\s*'([^']*)')[^.]+", data, re.DOTALL)

    while matches:
        for tot, val1, val2 in matches:
            data = data.replace(tot, "'%s%s'" % (val1, val2))

        matches = re.findall("('([^']*)'\s*\+\s*'([^']*)')[^.]+", data, re.DOTALL)

    return data


def uptostream_valors_directes(func, codi, data):
    m1 = re.findall("('[^']+'):('[^']+')", codi, re.DOTALL)

    for nom, valor in m1:
        data = data.replace("%s[%s]" % (func, nom), valor)

    return data


def uptostream_funcio_simple(func, codi, data):
    m1 = re.findall("('[^']+'):function\((\w+)\)\{return (\w+)\(\);\},", codi, re.DOTALL)

    for nom, p1, p2 in m1:
        if p1 == p2:
            data = re.sub("%s\[%s\]\(([^\)]+)\)" % (func, nom), '\\1()', data)

    return data


def uptostream_funcio_doble(func, codi, data):
    m1 = re.findall("('[^']+'):function\((\w+),(\w+)\)\{return (\w+)(\+|===|!==)(\w+);\},", codi, re.DOTALL)

    for nom, p1, p2, p3, op, p4 in m1:
        if p1 == p3 and p2 == p4:
            data = re.sub("%s\[%s\]\(([^,]+),([^\)]+)\)" % (func, nom), lambda m: m.group(1) + op + m.group(2), data)

    return data


def uptostream_ifs_fake(data):
    m1 = re.findall("(if\('([^']+)'(===|!==)'([^']+)'\)\{return\s*('[^']+');\}else\{return\s*('[^']+');\})", data, re.DOTALL)

    for tot, p1, op, p2, v1, v2 in m1:
        if op == '===': cumple = (p1 == p2)
        else: cumple = (p1 != p2)

        data = data.replace(tot, 'return ' + (v1 if cumple else v2) + ';')

    return data


def uptostream_funcions(data):
    m1 = re.findall("var (\w+)=\(\)=>\{return\s*('[^']+');\};", data, re.DOTALL)

    for nom, valor in m1:
        data = data.replace(nom+'()', valor)

    m1 = re.findall("var (\w+)=function\(\)\{return\s*('[^']+');\};", data, re.DOTALL)

    for nom, valor in m1:
        data = data.replace(nom+'()', valor)

    m1 = re.findall("function (\w+)\(\)\{return\s*('[^']+');\}", data, re.DOTALL)

    for nom, valor in m1:
        data = data.replace(nom+'()', valor)

    return data


def uptostream_pilla_valor(data, valor):
    aux = re.findall("\['%s'\]=(\w+);" % valor, data, re.DOTALL)

    if not aux: return ''

    aux = re.findall("var %s='([^']+)';" % aux[0], data, re.DOTALL)

    if not aux: return ''

    return aux[0]


def decode_video_uptostream(data):
    logger.info()

    matches = re.compile("(var \w+\s*=\s*\[.*?\];\(function\(.*?)\n").findall(data)
    if not matches: matches = re.compile("(var \w+\s*=\s*\[.*?\];\(function\(.*)$").findall(data)

    if not matches:
        logger.info('Uptostream not detected 1')

        patron = decode_video_uptostream_01(data)
        if patron: return patron
        return '', ''

    net = EstructuraInicial(matches[0])
    if not net.detectado:
        logger.info('Uptostream not detected 2')
        return '', ''

    data = net.data

    data = uptostream_sumes(data)

    for i in range(10):
        ant = data

        matches = re.findall('(var (\w+)=\{(.*?)\};)', data, re.DOTALL)

        for tot, func, codi in matches:
            data = uptostream_valors_directes(func, codi, data)
            data = uptostream_funcio_simple(func, codi, data)
            data = uptostream_funcio_doble(func, codi, data)

            if func+'[' not in data:
                data = data.replace(tot, '')

        data = uptostream_ifs_fake(data)

        if ant == data: break

    for i in range(10):
        ant = data

        data = uptostream_funcions(data)
        data = uptostream_sumes(data)

        if ant == data: break

    url = uptostream_pilla_valor(data, 'src').replace('\\/', '/')
    lbl = uptostream_pilla_valor(data, 'label')
    lang = uptostream_pilla_valor(data, 'lang')

    if lang and 'unknown' not in lang: lbl += ' (lang: ' + lang + ')'
    if not lbl: lbl = 'mp4'

    return lbl, url


def decode_video_uptostream_01(data):
    logger.info()

    from lib import js2py

    patron = jsontools.load(data)
    sources = patron.get('data').get('sources')

    parte = js2py.EvalJs({'atob': lambda formato: base64.b64decode('{}'.format(formato)).decode('utf-8')})

    parte.execute(sources)
    patron = parte.sources

    return patron


def rshift(val, n):
    return val>>n if val >= 0 else (val+0x100000000)>>n


def get_sucuri_cookie(data):
    matches = re.findall("S='([^']+)", data, flags=re.DOTALL)

    if not matches: return '', ''

    S = matches[0]
    A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    r = ''
    l = 0
    U = 0

    for i in range(len(S)):
        c = A.find(S[i])
        U = (U << 6) + c
        l += 6

        while l >= 8:
            l -= 8
            a = rshift(U, l) & 0xff
            r += chr(a)

    nomvar = r[0]

    r = r.replace('location.reload();', '')
    r = r.replace("';path=/;max-age=86400'", "''")
    r = r.replace('\n', ' ')
    r = r.replace('+ %s' % nomvar, ' ')
    r = re.sub('\.charAt\(([0-9]+)\)', lambda m: '['+m.group(1)+']', r)
    r = re.sub('String\.fromCharCode\(([0-9x]+)\)', lambda m: 'chr('+m.group(1)+')', r)
    r = re.sub('\.slice\(([0-9]+),\s*([0-9]+)\)', lambda m: '['+m.group(1)+':'+m.group(2)+']', r)
    r = re.sub('\.substr\(([0-9]+),\s*([0-9]+)\)', lambda m: '['+m.group(1)+':'+str( int(m.group(1)) + int(m.group(2)) )+']', r)
    r = r.replace('?', 'x')
    r = r.replace('@', 'y')

    res = r.split(';document.cookie=')

    try:
        e = eval (res[0].replace('%s=' % nomvar, ''))
        ck = eval (res[1].split("+ '';")[0])
    except:
        e = ''
        ck = ''

    return ck.replace('=', ''), e

