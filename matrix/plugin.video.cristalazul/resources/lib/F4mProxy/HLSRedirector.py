"""
Simple HTTP Live Streaming client.

References:
    http://tools.ietf.org/html/draft-pantos-http-live-streaming-08

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.

Last updated: July 22, 2012
MODIFIED BY shani to make it work with F4mProxy
"""

# from Crypto.Cipher import AES
'''
from crypto.cipher.aes      import AES
from crypto.cipher.cbc      import CBC
from crypto.cipher.base     import padWithPadLen
from crypto.cipher.rijndael import Rijndael
from crypto.cipher.aes_cbc import AES_CBC
'''

import binascii 
import codecs
import os
import random
import time
import traceback

import requests
import six

from six.moves import http_cookiejar
from six.moves import queue
from six.moves import urllib_parse
from six.moves import urllib_request
import xbmc


LOGNOTICE = xbmc.LOGNOTICE if six.PY2 else xbmc.LOGINFO
decoder_hex = codecs.getdecoder("hex_codec")

debug = True


def LOG(*args):
    if debug:
        mensaje = 'HLSREDIR log:'
        for arg in args:
            try:
                temp = '{}'.format(arg)
                mensaje = '{} {}'.format(mensaje, six.ensure_str(temp))
            except Exception as e:
                mensaje = '{} {}'.format(mensaje, e)
        xbmc.log(mensaje, LOGNOTICE)


gproxy = None
gauth = None
nsplayer = False
callbackDRM = None
USEDec = None

try:
    from Cryptodome.Cipher import AES
    USEDec = 1  # 1==crypto 2==local, local pycrypto
    LOG ('using Cryptodome.Cipher')
except:
    pass

if not USEDec:
    try:
        from Crypto.Cipher import AES
        AES = AESDecrypter()
        USEDec = 1
        LOG ('using Crypto.Cipher')
    except:
        pass

if not USEDec:
    try:
        from decrypter import AESDecrypter
        AES = AESDecrypter()
        USEDec = 2
        LOG ('using decrypter medium')
    except:
        pass
    
if not USEDec:
    try:
        from resources.lib.F4mProxy.f4mUtils import python_aes
        USEDec = 3
        LOG ('using python_aes slower')
    except:
        pass

iv = None
key = None
value_unsafe = '%+&;#'
VALUE_SAFE = ''.join(chr(c) for c in range(33, 127) if chr(c) not in value_unsafe)

SUPPORTED_VERSION = 3

cookieJar = http_cookiejar.LWPCookieJar()
clientHeader = None

    
class HLSRedirector():
    global cookieJar
    """
    A downloader for f4m manifests or AdobeHDS.
    """

    def __init__(self):
        self.init_done = False
        
    def sendVideoPart(self, URL, file, chunk_size=4096):
        for chunk in download_chunks(URL):
            send_back(chunk, file) 
        return

    def init(self, out_stream, url, proxy=None, use_proxy_for_chunks=True, g_stopEvent=None, maxbitrate=0, auth='', callbackpath="", callbackparam=""):
        global clientHeader, gproxy, gauth
        try:
            self.init_done = False
            self.init_url = url
            clientHeader = None
            self.status = 'init'
            self.proxy = proxy
            self.auth = auth
            self.callbackpath = callbackpath
            self.callbackparam = callbackparam
            if self.auth == None or self.auth == 'None' or self.auth == '':
                self.auth = None
            if self.auth:
                gauth = self.auth

            if self.proxy and len(self.proxy) == 0:
                self.proxy = None
            gproxy = self.proxy
            self.use_proxy_for_chunks = use_proxy_for_chunks
            self.out_stream = out_stream
            if g_stopEvent:
                g_stopEvent.clear()
            self.g_stopEvent = g_stopEvent
            self.maxbitrate = maxbitrate
            if '|' in url:
                sp = url.split('|')
                url = sp[0]
                clientHeader = sp[1]
                LOG (clientHeader)
                clientHeader = urllib_parse.parse_qsl(clientHeader)
                LOG ('header recieved now url and headers are', url, clientHeader)
            self.status = 'init done'
            self.url = url
            return True
        except Exception as e:
            LOG('Error en HLSREDIR init:', e)
            #===================================================================
            # traceback.print_exc()
            #===================================================================
            self.status = 'finished'
        return False
        
    def keep_sending_video(self, dest_stream, segmentToStart=None, totalSegmentToSend=0):
        try:
            self.status = 'download Starting'
            downloadInternal(self.url, dest_stream, self.maxbitrate, self.g_stopEvent, self.callbackpath, self.callbackparam)
        except Exception as e:
            LOG ('keep_sending_video Error:', e)
            traceback.print_exc()
        LOG ('setting finished')
        self.status = 'finished'


def getUrl(url, timeout=15, returnres=False, stream=False):
    global cookieJar
    global clientHeader
    global nsplayer

    try:
        post = None
        LOG ('url', url)
        session = requests.Session()
        session.cookies = cookieJar

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:42.0) Gecko/20100101 Firefox/42.0 Iceweasel/42.0'}

        if clientHeader:
            for n, v in clientHeader:
                headers[n] = v
        if nsplayer:
            LOG ('nsplayer is true')
            headers['User-Agent'] = binascii.b2a_hex(os.urandom(20))[:32]
        LOG ('nsplayer', nsplayer, headers)
        proxies = {}
        LOG ('gproxy', gproxy)
        if gproxy:
            proxies = {"http": "http://" + gproxy}
        LOG ('proxies', proxies)
        if post:
            LOG ('POST ', url, post)
            req = session.post(url, headers=headers, data=post, proxies=proxies, verify=False, timeout=timeout, stream=stream)
        else:
            LOG ('GET ', url)
            req = session.get(url, headers=headers, proxies=proxies, verify=False, timeout=timeout, stream=stream)

        req.raise_for_status()
        if returnres:
            return req
        else:
            return req.text

    except Exception as e:
        LOG ('Error in getUrl Error:', e)
        #=======================================================================
        # traceback.print_exc()
        #=======================================================================
        raise
        return None


def download_chunks(URL, chunk_size=4096, enc=None):
    conn = getUrl(URL, returnres=True, stream=True)
    chunk_size = chunk_size * 4
    for chunk in conn.iter_content(chunk_size=chunk_size):
        yield chunk
    conn.close()

    
def download_file(URL):
    return b''.join(download_chunks(URL))


def validate_m3u(conn):
    ''' make sure file is an m3u, and returns the encoding to use. '''
    return 'utf8'


def gen_m3u(url, skip_comments=True):
    global cookieJar

    conn = getUrl(url, returnres=True)
    redirurl = None
    if conn.history:
        LOG ('history')
        redirurl = conn.url
    enc = validate_m3u(conn)
    if redirurl:
        yield 'f4mredirect:' + redirurl
    for line in conn.iter_lines():  # .split('\n'):
        line = six.ensure_str(line)
        line = line.rstrip('\r\n')
        if not line:
            # blank line
            continue
        elif line.startswith('#EXT'):
            # tag
            yield line
        elif line.startswith('#'):
            # comment
            if skip_comments:
                continue
            else:
                yield line
        else:
            # media file
            yield line


def parse_m3u_tag(line):
    if ':' not in line:
        return line, []
    tag, attribstr = line.split(':', 1)
    attribs = []
    last = 0
    quote = False
    for i, c in enumerate(attribstr + ','):
        if c == '"':
            quote = not quote
        if quote:
            continue
        if c == ',':
            attribs.append(attribstr[last:i])
            last = i + 1
    return tag, attribs


def parse_kv(attribs, known_keys=None):
    d = {}
    for item in attribs:
        k, v = item.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"')
        if known_keys is not None and k not in known_keys:
            raise ValueError("unknown attribute %s" % k)
        d[k] = v
    return d


def handle_basic_m3u(url):
    global iv
    global key
    global USEDec
    global gauth
    global callbackDRM

    seq = 1
    enc = None
    nextlen = 5
    duration = 5
    targetduration = 5
    aesdone = False
    redirurl = url
    HOST_NAME = '127.0.0.1'
    PORT_NUMBER = 55333
    vod = False
    for line in gen_m3u(url):
        if not line.startswith('#EXT'):
            if 1 == 1:  # not line.startswith('http'):
                line = urllib_parse.urljoin(url, line)
                newurl = 'sendvideopart?' + urllib_parse.urlencode({'url': line})
                line = 'http://' + HOST_NAME + (':%s/' % str(PORT_NUMBER)) + newurl  # #shoud read from config
        yield line + '\n'


def player_pipe(queue, control, file):
    while 1:
        block = queue.get(block=True)
        if block is None: return
        file.write(block)
        file.flush()

        
def send_back(data, file):
    file.write(data)
    # file.flush()

        
def downloadInternal(url, file, maxbitrate=0, stopEvent=None , callbackpath="", callbackparam="", testing=False):
    global key
    global iv
    global USEDec
    global cookieJar
    global clientHeader
    global nsplayer
    global callbackDRM
    if stopEvent and stopEvent.isSet():
        return False
    dumpfile = None
    # dumpfile=open('c:\\temp\\myfile.mp4',"wb")
    variants = []
    variant = None
    veryfirst = True
    # url check if requires redirect
    redirurl = url
    utltext = ''
    try:
        print ('going for url  ', url)
        res = getUrl(url, returnres=True)
        LOG ('here ', res)
        if res.history:
            LOG ('history is', res.history)
            redirurl = res.url
            url = redirurl
        utltext = res.text
        res.close()
        if testing:
            return True
    except Exception as e:
        LOG ('Error in downloadInternal Error:', e)
        #=======================================================================
        # traceback.print_exc()
        #=======================================================================
    LOG ('redirurl', redirurl)
    if 'EXT-X-STREAM-INF' in utltext:
        try:
            for line in gen_m3u(redirurl):
                if line.startswith('#EXT'):
                    tag, attribs = parse_m3u_tag(line)
                    if tag == '#EXT-X-STREAM-INF':
                        variant = attribs
                elif variant:
                    variants.append((line, variant))
                    variant = None
            LOG ('variants', variants)
            if len(variants) == 0:
                url = redirurl
            if len(variants) == 1:
                url = urllib_parse.urljoin(redirurl, variants[0][0])
            elif len(variants) >= 2:
                LOG ("More than one variant of the stream was provided.")

                choice = -1
                lastbitrate = 0
                LOG ('maxbitrate', maxbitrate)
                for i, (vurl, vattrs) in enumerate(variants):
                    LOG (i, vurl,)
                    for attr in vattrs:
                        key, value = attr.split('=')
                        key = key.strip()
                        value = value.strip().strip('"')
                        if key == 'BANDWIDTH':
                            LOG ('Max bitrate: {}'.format(maxbitrate))
                            LOG ('bitrate %.2f kbps' % (int(value) / 1024.0))
                            if int(value) <= int(maxbitrate) and int(value) > lastbitrate:
                                choice = i
                                lastbitrate = int(value)
                                LOG ('Agregado')
                            if key == 'PROGRAM-ID':
                                LOG ('program %s' % value,)
                            if key == 'CODECS':
                                LOG ('codec %s' % value,)
                            if key == 'RESOLUTION':
                                LOG ('resolution %s' % value,)
                        else:
                            LOG ("unknown STREAM-INF attribute %s" % key)
                            # raise ValueError("unknown STREAM-INF attribute %s"%key)
                if choice == -1:
                    choice = 0
                # choice = int(raw_input("Selection? "))
                LOG ('choose %d' % choice)
                LOG ('Redrurl {}'.format(redirurl))
                url = urllib_parse.urljoin(redirurl, variants[choice][0])
        except:

            raise

    for chunk in handle_basic_m3u(url):
        send_back(six.ensure_binary(chunk), file)
  
