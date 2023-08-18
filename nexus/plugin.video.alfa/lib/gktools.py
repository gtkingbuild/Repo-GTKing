# -*- coding: utf-8 -*-

'''
gktools son un conjunto de funciones para ayudar a resolver enlaces a videos con "protección GK".
Lo de protección gk dudo que exista, le he llamado así pq los primeros ejemplos vistos se eran gkpluginsphp y gkpedia.

Características "GK" :
- Utiliza una cookie __cfduid
- Calcula un token criptográfico en función de un texto y una clave
- El texto se saca del html (por ejemplo de meta name="google-site-verification", pero puede ser más complejo)
- La clave para encriptar se calcula en js ofuscados que carga el html 
- Se llama a otra url con una serie de parámetros, como el token, y de allí se obtienen los videos finales.

Howto:
1- descargar página
2- extraer datos y calcular los necesarios
3- descargar segunda página con el token calculado
4- extraer videos

El paso 2 es con diferencia el más variable y depende mucho de cada web/servidor!
Desofuscando los js se pueden ver los datos propios que necesita cada uno 
(el texto a encriptar, la clave a usar, la url dónde hay que llamar y los parámetros)

Ver ejemplos en el código de los canales animeyt y pelispedia


Created for Alfa-addon by Alfa Developers Team 2018
'''
from __future__ import division
from __future__ import absolute_import

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


from builtins import hex
from builtins import range
from .past.utils import old_div
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import os, base64, json, hashlib
from core import httptools
from core import scrapertools
from platformcode import logger
from .aadecode import decode as aadecode

# Descarga página y captura la petición de cookie
# -----------------------------------------------
def get_data_and_cookie(item, ck_name='__cfduid'):

    headers = {'Referer': item.referer}
    resp = httptools.downloadpage(item.url, headers=headers, cookies=False)
    # ~ with open('gk_play1.html', 'w') as f: f.write(resp.data); f.close()

    ck_value = ''
    if ck_name != '':
        for h in resp.headers:
            ck = scrapertools.find_single_match(resp.headers[h], '%s=([^;]*)' % ck_name)
            if ck:
                ck_value = ck
                break

    return resp.data, ck_value


# Descarga página usando una cookie concreta
# ------------------------------------------
def get_data_with_cookie(url, ck_value='', referer='', ck_name='__cfduid'):

    headers = {'Cookie': ck_name+'='+ck_value}
    if referer != '': headers['referer'] = referer
    data = httptools.downloadpage(url, headers=headers, cookies=False).data
    # ~ with open('gk_play2.html', 'w') as f: f.write(data); f.close()

    return data


# Descarga json usando una cookie concreta
# ----------------------------------------
def get_data_json(url, post, ck_value='', referer='', ck_name='__cfduid'):

    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': ck_name+'='+ck_value}
    if referer != '': headers['referer'] = referer

    data = httptools.downloadpage(url, post=post, headers=headers, cookies=False).data
    # ~ with open('gk_play3.html', 'w') as f: f.write(data); f.close()

    return data


# Obtiene link de una llamada javascript Play() o de la url
# ---------------------------------------------------------
def get_play_link_id(data, url):

    playparms = scrapertools.find_single_match(data, 'Play\("([^"]*)","([^"]*)","([^"]*)"')
    if playparms:
        link = playparms[0]
        subtitle = '' if playparms[1] == '' or playparms[2] == '' else playparms[2] + playparms[1] + '.srt'
    else:
        subtitle = ''
        link = scrapertools.find_single_match(data, 'Play\("([^"]*)"')
        if not link:
            link = scrapertools.find_single_match(url, 'id=([^;]*)')

    return link, subtitle


# Extraer enlaces a videos de datos json
# --------------------------------------
def extraer_enlaces_json(data, referer, subtitle=''):
    itemlist = []

    # Ejemplos:
    # {"Animeyt":[{"file":"https:\/\/storage.googleapis.com\/my-project-yt-195318.appspot.com\/slow.mp4","type":"mp4","label":"1080p"}]}
    # {"link":[{"link":"http:\/\/video8.narusaku.tv\/static\/720p\/2.1208982.2039540?md5=B64FKYNbFuWvxkGcSbtz2Q&expires=1528839657","label":"720p","type":"mp4"},{"link":"http:\/\/video5.narusaku.tv\/static\/480p\/2.1208982.2039540?md5=yhLG_3VghEUSd5YlCXOTBQ&expires=1528839657","label":"480p","type":"mp4","default":true},{"link":"http:\/\/video3.narusaku.tv\/static\/360p\/2.1208982.2039540?md5=vC0ZJkxRwV1rVBdeF7D4iA&expires=1528839657","label":"360p","type":"mp4"},{"link":"http:\/\/video2.narusaku.tv\/static\/240p\/2.1208982.2039540?md5=b-y_-rgrLMW7hJwFQSD8Tw&expires=1528839657","label":"240p","type":"mp4"}]}
    # {"link":"https:\/\/storage.googleapis.com\/cloudflare-caching-pelispedia.appspot.com\/cache\/16050.mp4","type":"mp4"}
    # {"Harbinger":[{"Harbinger":"...","type":"...","label":"..."}], ...}

    data = data.replace('"Harbinger"', '"file"')

    # Intentar como json
    # ------------------
    try:
        json_data = json.loads(data)
        enlaces = analizar_enlaces_json(json_data)
        for enlace in enlaces:
            url = enlace['link'] if 'link' in enlace else enlace['file']
            if not url.startswith('http'): url = aadecode(base64.b64decode(url)) # necesario para "Harbinger"
            if not url.startswith('http'): url = decode_rijndael(url) # post-"Harbinger" en algunos casos
            tit = ''
            if 'type' in enlace: tit += '[%s]' % enlace['type']
            if 'label' in enlace: tit += '[%s]' % enlace['label']
            if tit == '': tit = '.mp4'
            
            itemlist.append([tit, corregir_url(url, referer), 0, subtitle])

    # Sino, intentar como texto
    # -------------------------
    except:
        matches = scrapertools.find_multiple_matches(data, '"link"\s*:\s*"([^"]*)"\s*,\s*"label"\s*:\s*"([^"]*)"\s*,\s*"type"\s*:\s*"([^"]*)"')
        if matches:
            for url, lbl, typ in matches:
                itemlist.append(['[%s][%s]' % (typ, lbl), corregir_url(url, referer), 0, subtitle])
        else:
            url = scrapertools.find_single_match(data, '"link"\s*:\s*"([^"]*)"')
            if url:
                itemlist.append(['.mp4', corregir_url(url, referer), 0, subtitle])


    return itemlist


# Función recursiva que busca videos en un diccionario
# ----------------------------------------------------
def analizar_enlaces_json(d):
    itemlist = []
    found = {}
    for k, v in d.items():
        if k in ['file','link','type','label'] and not isinstance(v, list):
            found[k] = v
        
        if isinstance(v, list):
            for l in v:
                if isinstance(l, dict): itemlist += analizar_enlaces_json(l)

    if 'file' in found or 'link' in found:
        itemlist.append(found)

    return itemlist


# Correcciones en las urls finales obtenidas
# ------------------------------------------
def corregir_url(url, referer):
    url = url.replace('\/', '/')
    if 'chomikuj.pl/' in url: url += "|Referer=%s" % referer
    return url



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Conversion tipo hexa que hay en el js
# -------------------------------------
def toHex(txt):
    ret = ''
    for i in range(len(txt)):
        ret += str(hex(ord(txt[i]))).replace('x','')[-2:]
    return ret


# Subrutinas de encriptación
# --------------------------

def md5_dominio(url): # sutorimux/kubechi
    h = hashlib.md5(urlparse.urlparse(url).netloc)
    return h.hexdigest()


def transforma_gsv(gsv, valor):
    llista = list(range(256))
    a = 0
    for i in range(256):
        a = (a + llista[i] + ord(gsv[i % len(gsv)]) ) % 256
        b = llista[i]
        llista[i] = llista[a]
        llista[a] = b

    ret = ''
    a = 0; b= 0
    for i in range(len(valor)):
        a = (a + 1) % 256
        b = (b + llista[a]) % 256
        c = llista[a]
        llista[a] = llista[b]
        llista[b] = c
        ret += chr(ord(valor[i]) ^ llista[(llista[a] + llista[b]) % 256])
    
    return base64.b64encode(ret)



# Codificar/Decodificar con Rijndael
# ----------------------------------

def encode_rijndael(msg, IV, key):
    from . import rijndael
    return rijndael.cbc_encrypt(msg, IV, key)


def decode_rijndael(txt, preIV='b3512f4972d314da9', key='3e1a854e7d5835ab99d99a29afec8bbb'):
    from . import rijndael
    msg = base64.b64decode(txt[:-15])
    IV = preIV + txt[-15:]
    deco = rijndael.cbc_decrypt(msg, IV, key)
    return deco.replace(chr(0), '')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Generar un token válido a partir de un texto y una clave
# --------------------------------------------------------

# gsv: google-site-verification, obtenido de '<meta name="google-site-verification" content="([^"]*)"'
# pwd: Password
def generar_token(gsv, pwd):
    txt = obtener_cripto(pwd, gsv)
    # ~ logger.info('Texto pre token %s' % txt)

    _0x382d28 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

    valors = [0, 0, 0]
    cicle = 0
    retorn = ''
    for ch in txt:
        valors[cicle] = ord(ch)
        cicle += 1
        if cicle == 3:
            primer = _0x382d28[valors[0] >> 0x2]
            segon  = _0x382d28[((valors[0] & 0x3) << 0x4) | (valors[1] >> 0x4)]
            tercer = _0x382d28[((valors[1] & 0xf) << 0x2) | (valors[2] >> 0x6)]
            quart  = _0x382d28[valors[2] & 0x3f]
            retorn += primer + segon + tercer + quart
            
            valors = [0, 0, 0]
            cicle = 0

    return retorn


def obtener_cripto(password, plaintext):
    salt = os.urandom(8)

    paddingLength = len(plaintext) % 16
    if paddingLength == 0:
        paddedPlaintext = plaintext
    else:
        dif = 16 - paddingLength
        paddedPlaintext = plaintext + chr(dif)*dif
 
    kdf = evpKDF(password, salt)
    iv = kdf['iv']

    try: # Intentar con librería AES del sistema
        from .Crypto.Cipher import AES
        cipherSpec = AES.new(kdf['key'], AES.MODE_CBC, iv)
    except: # Si falla intentar con librería del addon 
        from . import jscrypto
        cipherSpec = jscrypto.new(kdf['key'], jscrypto.MODE_CBC, iv)
    ciphertext = cipherSpec.encrypt(paddedPlaintext)

    return json.dumps({'ct': base64.b64encode(ciphertext), 'iv': iv.encode("hex"), 's': salt.encode("hex")}, sort_keys=True, separators=(',', ':'))


def evpKDF(passwd, salt, key_size=8, iv_size=4, iterations=1, hash_algorithm="md5"):
    target_key_size = key_size + iv_size
    derived_bytes = ""
    number_of_derived_words = 0
    if PY3:
        passwd = bytes(list(ord(x) for x in passwd))
    block = None
    hasher = hashlib.new(hash_algorithm)
    while number_of_derived_words < target_key_size:
        if block is not None:
            hasher.update(block)

        hasher.update(passwd)
        hasher.update(salt)
        block = hasher.digest()
        hasher = hashlib.new(hash_algorithm)

        for i in range(1, iterations):
            hasher.update(block)
            block = hasher.digest()
            hasher = hashlib.new(hash_algorithm)

        if PY3:
            derived_bytes += "".join(chr(x) for x in block[0: min(len(block), (target_key_size - number_of_derived_words) * 4)])
        else:
            derived_bytes += block[0: min(len(block), (target_key_size - number_of_derived_words) * 4)]

        number_of_derived_words += old_div(len(block),4)

    return {
        "key": derived_bytes[0: key_size * 4],
        "iv": derived_bytes[key_size * 4:]
    }
