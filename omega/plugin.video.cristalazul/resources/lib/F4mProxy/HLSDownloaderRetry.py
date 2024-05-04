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

import array
import binascii
import codecs
import io
import os
import random
import re
import struct
import sys
import time
import traceback

import requests
import six
import xbmc

from six.moves import http_cookiejar
from six.moves import queue
from six.moves import urllib_parse
from six.moves import urllib_request


LOGNOTICE = xbmc.LOGNOTICE if six.PY2 else xbmc.LOGINFO
decoder_hex = codecs.getdecoder("hex_codec")

debug = False


def LOG(*args):
    if debug:
        mensaje = 'HLSRETRY log:'
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


class HLSDownloaderRetry():
    global cookieJar
    """
    A downloader for f4m manifests or AdobeHDS.
    """

    def __init__(self):
        self.init_done = False

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
            LOG('Error en HLSRETRY init:', e)
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

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

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


def getUrlold(url, timeout=20, returnres=False):
    global cookieJar
    global clientHeader
    try:
        post = None

        cookie_handler = urllib_request.HTTPCookieProcessor(cookieJar)
        openner = urllib_request.build_opener(cookie_handler, urllib_request.HTTPBasicAuthHandler(), urllib_request.HTTPHandler())

        if post:
            req = urllib_request.Request(url, post)
        else:
            req = urllib_request.Request(url)

        ua_header = False
        if clientHeader:
            for n, v in clientHeader:
                req.add_header(n, v)
                if n == 'User-Agent':
                    ua_header = True

        if not ua_header:
            req.add_header('User-Agent', 'AppleCoreMedia/1.0.0.12B411 (iPhone; U; CPU OS 8_1 like Mac OS X; en_gb)')

        # req.add_header('X-Playback-Session-Id','9A1E596D-6AB6-435F-85D1-59BDD0E62D24')
        if gproxy:
            req.set_proxy(gproxy, 'http')
        response = openner.open(req)

        if returnres:
            return response
        data = response.read()

        return data

    except Exception as e:
        LOG ('Error in getUrlold Error:', e)
        #=======================================================================
        # traceback.print_exc()
        #=======================================================================
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
    vod = False
    LOG ('INIT handle_basic_m3u')
    for line in gen_m3u(url):
        LOG ('For Line handle_basic_m3u')
        if line.startswith('f4mredirect:'):
            redirurl = line.split('f4mredirect:')[1]
            continue
        if line.startswith('#EXT'):
            tag, attribs = parse_m3u_tag(line)
            if tag == '#EXTINF':
                duration = float(attribs[0])
            elif tag == '#EXT-X-TARGETDURATION':
                assert len(attribs) == 1, "too many attribs in EXT-X-TARGETDURATION"
                targetduration = int(attribs[0])
                pass
            elif tag == '#EXT-X-MEDIA-SEQUENCE':
                assert len(attribs) == 1, "too many attribs in EXT-X-MEDIA-SEQUENCE"
                seq = int(attribs[0])
            elif tag == '#EXT-X-KEY':
                attribs = parse_kv(attribs, ('METHOD', 'URI', 'IV'))
                assert 'METHOD' in attribs, 'expected METHOD in EXT-X-KEY'
                if attribs['METHOD'] == 'NONE':
                    LOG ('MTHOD NONEEE')
                    assert 'URI' not in attribs, 'EXT-X-KEY: METHOD=NONE, but URI found'
                    assert 'IV' not in attribs, 'EXT-X-KEY: METHOD=NONE, but IV found'
                    enc = None
                elif attribs['METHOD'] == 'AES-128':
                    LOG ('MTHOD AES-128')
                    if not aesdone:
                        LOG ('not aesdone')
                        # aesdone=False there can be multple aes per file
                        assert 'URI' in attribs, 'EXT-X-KEY: METHOD=AES-128, but no URI found'
                        # from Crypto.Cipher import AES
                        codeurl = attribs['URI'].strip('"')

                        if gauth:
                            LOG ('gauth')
                            currentaesUrl = codeurl
                            codeurl = gauth

                            if codeurl.startswith("LSHex$"):
                                codeurl = decode_hex(codeurl.split('LSHex$')[1])
                                LOG ('code is ', codeurl.encode("hex"))
                            if codeurl.startswith("LSDRMCallBack$"):
                                codeurlpath = codeurl.split('LSDRMCallBack$')[1]
                                codeurl = 'LSDRMCallBack$' + currentaesUrl
                                if codeurlpath and len(codeurlpath) > 0 and callbackDRM == None:
                                    LOG ('callback', codeurlpath)
                                    import importlib
                                    import os
                                    foldername = os.path.sep.join(codeurlpath.split(os.path.sep)[:-1])
                                    urlnew = ''
                                    if foldername not in sys.path:
                                        sys.path.append(foldername)
                                    try:
                                        callbackfilename = codeurlpath.split(os.path.sep)[-1].split('.')[0]
                                        callbackDRM = importlib.import_module(callbackfilename)
                                        LOG ('LSDRMCallBack imported')
                                    except Exception as e:
                                        LOG ('Error in handle_basic_m3u codeurlpath Error:', e)
                                        #=======================================
                                        # traceback.print_exc()
                                        #=======================================

                        elif not codeurl.startswith('http'):
                            LOG ('not http')
                            codeurl = urllib_parse.urljoin(url, codeurl)

                        # key = download_file(codeurl)
                        # assert len(key) == 16, 'EXT-X-KEY: downloaded key file has bad length'
                        if 'IV' in attribs:
                            LOG ('IV')
                            LOG (type(attribs['IV']))
                            LOG (attribs['IV'])
                            assert attribs['IV'].lower().startswith('0x'), 'EXT-X-KEY: IV attribute has bad format'
                            iv = decode_hex(attribs['IV'][2:].zfill(32))
                            assert len(iv) == 16, 'EXT-X-KEY: IV attribute has bad length'
                        else:
                            LOG ('NOT IV')
                            iv = '\0' * 8 + struct.pack('>Q', seq)
                        enc = (codeurl, iv)
                        # if not USEDec==3:
                        #    enc = AES.new(key, AES.MODE_CBC, iv)
                        # else:
                        #    ivb=array.array('B',iv)
                        #    keyb= array.array('B',key)
                        #    enc=python_aes.new(keyb, 2, ivb)
                        # enc = AES_CBC(key)
                        # print key
                        # print iv
                        # enc=AESDecrypter.new(key, 2, iv)
                else:
                    LOG ('MTHOD Desconocido')
                    assert False, 'EXT-X-KEY: METHOD=%s unknown' % attribs['METHOD']
            elif tag == '#EXT-X-PROGRAM-DATE-TIME':
                assert len(attribs) == 1, "too many attribs in EXT-X-PROGRAM-DATE-TIME"
                # TODO parse attribs[0] as ISO8601 date/time
                pass
            elif tag == '#EXT-X-ALLOW-CACHE':
                # XXX deliberately ignore
                pass
            elif tag == 'EXT-X-PLAYLIST-TYPE:VOD':
                vod = True
                pass
                # EXT-X-PLAYLIST-TYPE:VOD
            elif tag == '#EXT-X-ENDLIST':
                assert not attribs
                yield None
                return
            elif tag == '#EXT-X-STREAM-INF':
                raise ValueError("don't know how to handle EXT-X-STREAM-INF in basic playlist")
            elif tag == '#EXT-X-DISCONTINUITY':
                assert not attribs
                LOG ("[warn] discontinuity in stream")
            elif tag == '#EXT-X-VERSION':
                assert len(attribs) == 1
                if int(attribs[0]) > SUPPORTED_VERSION:
                    LOG ("[warn] file version %s exceeds supported version %d; some things might be broken" % (attribs[0], SUPPORTED_VERSION))
            # else:
            #    raise ValueError("tag %s not known"%tag)
        else:
            if not line.startswith('http'):
                line = urllib_parse.urljoin(redirurl, line)
            yield (seq, enc, duration, targetduration, line, vod)
            seq += 1


def player_pipe(queue, control, file):
    while 1:
        block = queue.get(block=True)
        if block is None:
            return
        file.write(block)
        file.flush()


def send_back(data, file):
    LOG ('send_back')
    file.write(data)
    LOG ('send_back write ok')
    file.flush()
    LOG ('send_back flush ok')


def downloadInternal(url, file, maxbitrate=0, stopEvent=None, callbackpath="", callbackparam="", testing=False):
    global key
    global iv
    global USEDec
    global cookieJar
    global clientHeader
    global nsplayer
    global callbackDRM
    LOG ('downloadInternal stopEvent', stopEvent.isSet())
    if stopEvent and stopEvent.isSet():
        return False
    dumpfile = None
    #===========================================================================
    # dumpfile=open('myfile.mp4',"wb")
    #===========================================================================
    variants = []
    variant = None
    veryfirst = True
    # url check if requires redirect
    redirurl = url
    utltext = ''
    try:
        LOG ('going for url  ', url)
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

    LOG ('final url', url)
    last_seq = -1
    targetduration = 5
    changed = 0

    fails = 0
    maxfails = 5
    nsplayer = False
    LOG ('inside HLS RETRY')
    try:

        # file.write(b'FLV\x01')
        # file.write(b'\x01')
        # file.write(b'\x00\x00\x00\x09')
        # FLV File body
        # file.write(b'\x00\x00\x00\x09')
        while 1 == 1:  # thread.isAlive():

            reconnect = False
            vod = False
            if fails > maxfails:
                # stopEvent.set()
                break
            if stopEvent and stopEvent.isSet():
                return False
            try:
                LOG ('GET medialist')
                medialist = list(handle_basic_m3u(url))
                LOG ('OK medialist')
                if len(medialist) == 0:
                    LOG ('empty m3u8')
                    raise Exception('empty m3u8')
                LOG ('medialist...')
                LOG (medialist)
                if testing:
                    return True
            except Exception as inst:
                LOG ('here in exp', inst)
                LOG (fails)
                fails += 1
                if testing and fails > 6:
                    return False
                if testing == False and '403' in repr(inst).lower() and callbackpath and len(callbackpath) > 0:
                    LOG ('callback')
                    import importlib
                    import os
                    foldername = os.path.sep.join(callbackpath.split(os.path.sep)[:-1])

                    urlnew = ''
                    if foldername not in sys.path:
                        sys.path.append(foldername)
                    try:
                        callbackfilename = callbackpath.split(os.path.sep)[-1].split('.')[0]
                        callbackmodule = importlib.import_module(callbackfilename)
                        urlnew, cjnew = callbackmodule.f4mcallback(callbackparam, 1, inst, cookieJar, url, clientHeader)
                    except Exception as e:
                        LOG ('Error in callbackfilename Error:', e)
                        #=======================================================
                        # traceback.print_exc()
                        #=======================================================
                    if urlnew and len(urlnew) > 0 and urlnew.startswith('http'):
                        LOG ('got new url', url)
                        url = urlnew
                        cookieJar = cjnew
                        continue
                    else:
                        return
                if '403' in repr(inst).lower() or '401' in repr(inst).lower():
                    if fails in [1, 4, 5, 10, 15, 19]:
                        nsplayer = True
                    else:
                        nsplayer = False
                    LOG ('nsplayer', nsplayer)
                    xbmc.sleep(1000)
                continue

            nsplayer = False
            playedSomething = False
            if medialist == None:
                return

               # choose to start playback three files from the end, since this is a live stream
               # medialist = medialist[-6:]
            # print 'medialist',medialist
            addsomewait = False
            lastKeyUrl = ""
            lastkey = None
            playedduration = 0
            st = time.time()
            for media in medialist:

                if stopEvent and stopEvent.isSet():
                    return False
                if media is None:
                    # send_back('G'+chr(254)+chr(255)+('\0'*1), file)
                    # queue.put(None, block=True)

                    if stopEvent:
                        LOG ('set events')
                        stopEvent.set()
                    return False
                seq, encobj, duration, targetduration, media_url, vod = media

                if seq > last_seq:
                    # print 'downloading.............',url

                    enc = None
                    if encobj:

                        codeurl, iv = encobj
                        if codeurl != lastKeyUrl:
                            if codeurl.startswith('http'):
                                key = download_file(codeurl)
                            elif codeurl.startswith('LSDRMCallBack$'):
                                key = callbackDRM.DRMCallback(codeurl.split('LSDRMCallBack$')[1], url)
                            else:
                                key = codeurl
                            codeurl = lastKeyUrl
                        else:
                            key = lastkey
                        lastkey = key
                        if not USEDec == 3:
                            LOG ('enc  USEDec=3')
                            enc = AES.new(key, AES.MODE_CBC, iv)
                        else:
                            LOG ('enc  NOT USEDec')
                            ivb = array.array('B', iv)
                            keyb = array.array('B', key)
                            enc = python_aes.new(keyb, 2, ivb)
                        # enc=AESDecrypter.new(key, 2, iv)
                    try:
                        data = None
                        try:
                            LOG ('downloading', urllib_parse.urljoin(url, media_url))
                            # for chunk in
                            # download_chunks(urllib_parse.urljoin(url,
                            # media_url)):
                            for chunk in download_chunks(media_url):
                                if stopEvent and stopEvent.isSet():
                                    return False
                                LOG ('sending chunk', len(chunk))
                                LOG ('Type chunk', type(chunk))
                                if enc:
                                    if not USEDec == 3:
                                        chunk = enc.decrypt(chunk)
                                    else:
                                        LOG ('creando chunkb')
                                        chunkb = array.array('B', chunk)
                                        LOG ('chunkb ok')
                                        LOG ('decryp chunkb')
                                        #=======================================
                                        # chunk = enc.decrypt(chunkb)
                                        #=======================================
                                        chunk = enc.decrypt(chunkb)
                                        LOG ('decryp chunkb ok')
                                        LOG ('join chunk')
                                        if six.PY2:
                                            chunk = "".join(map(chr, chunk))
                                        LOG ('join chunk ok')
                                LOG ('sendback')
                                if b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a" in chunk:
                                    chunk = chunk.replace(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", b"\xff\xff\xff\xff\xff\xff\xff\xff")
                                send_back(chunk, file)
                                LOG ('sendback OK')
                                data = "send"
                            playedduration += duration
                            addsomewait = True

                        except Exception as inst:
                            LOG ('xxxx', repr(inst))
                            if 'forcibly closed' in repr(inst):
                                LOG ('returning')
                                return False
                        if stopEvent and stopEvent.isSet():
                            return False

                        # chunk in download_chunks(urllib_parse.urljoin(url,
                        # media_url),enc=encobj):
                        if data and len(data) > 0:

                            # if not veryfirst:
                            #    if dumpfile: dumpfile.write(chunk)
                            #    #queue.put(chunk, block=True)
                            #    send_back(data,file)
                            #    #print '3. chunk available %d'%len(chunk)
                            veryfirst = False
                            last_seq = seq
                            changed = 1
                            playedSomething = True
                            fails = 0
                            maxfails = 20
                        else:
                            reconnect = True
                            fails += 1
                            break
                    except:
                        pass

            if vod:
                return True
            if playedSomething == 1:
                # initial minimum reload delay
                timetowait = int(targetduration - (time.time() - st))
                if (timetowait) > 0:
                    LOG ('sleeping because targetduration', timetowait)
                    for t in range(0, timetowait):
                        xbmc.sleep(1000)
                        LOG ('sleeep for 1sec', t)
                        if stopEvent and stopEvent.isSet():
                            return False

            if not playedSomething:
                xbmc.sleep(3000 + (3000 if addsomewait else 0))

    except:

        raise


def decode_hex(hexe):
    if six.PY2:
        return hexe.decode('hex')
    if six.PY3:
        return decoder_hex(hexe)[0]
