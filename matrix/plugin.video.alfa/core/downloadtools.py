# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Download Tools - Original based from code of VideoMonkey XBMC Plugin
# ---------------------------------------------------------------------------------

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from past.utils import old_div
#from future import standard_library
#standard_library.install_aliases()
#from builtins import str

import sys
PY3 = False
VFS = True
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; VFS = False

if PY3:
    import urllib.parse as urllib   # Es muy lento en PY2.  En PY3 es nativo
    import urllib.request as urllib2
    import urllib.error as urllib_error
else:
    import urllib                   # Usamos el nativo de PY2 que es más rápido
    import urllib2
    import urllib2 as urllib_error

import re
import socket
import time

from platformcode import config, logger
from core import filetools

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


entitydefs2 = {
    '$': '%24',
    '&': '%26',
    '+': '%2B',
    ',': '%2C',
    '/': '%2F',
    ':': '%3A',
    ';': '%3B',
    '=': '%3D',
    '?': '%3F',
    '@': '%40',
    ' ': '%20',
    '"': '%22',
    '<': '%3C',
    '>': '%3E',
    '#': '%23',
    '%': '%25',
    '{': '%7B',
    '}': '%7D',
    '|': '%7C',
    '\\': '%5C',
    '^': '%5E',
    '~': '%7E',
    '[': '%5B',
    ']': '%5D',
    '`': '%60'
}

entitydefs3 = {
    u'ÂÁÀÄÃÅ': u'A',
    u'âáàäãå': u'a',
    u'ÔÓÒÖÕ': u'O',
    u'ôóòöõðø': u'o',
    u'ÛÚÙÜ': u'U',
    u'ûúùüµ': u'u',
    u'ÊÉÈË': u'E',
    u'êéèë': u'e',
    u'ÎÍÌÏ': u'I',
    u'îìíï': u'i',
    u'ñ': u'n',
    u'ß': u'B',
    u'÷': u'%',
    u'ç': u'c',
    u'æ': u'ae'
}


def limpia_nombre_caracteres_especiales(s):
    if not s:
        return ''
    badchars = '\\/:*?\"<>|'
    for c in badchars:
        s = s.replace(c, '')
        return s


def limpia_nombre_sin_acentos(s):
    if not s:
        return ''
    for key, value in entitydefs3.items():
        for c in key:
            s = s.replace(c, value)
            return s


def limpia_nombre_excepto_1(s):
    if not s:
        return ''
    # Titulo de entrada
    # Convierte a unicode
    try:
        s = unicode(s, "utf-8")
    except UnicodeError:
        # logger.info("no es utf-8")
        try:
            s = unicode(s, "iso-8859-1")
        except UnicodeError:
            # logger.info("no es iso-8859-1")
            pass
    # Elimina acentos
    s = limpia_nombre_sin_acentos(s)
    # Elimina caracteres prohibidos
    validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
    stripped = ''.join(c for c in s if c in validchars)
    # Convierte a iso
    s = stripped.encode("iso-8859-1")
    if PY3:
        s = s.decode('utf-8')
    return s


def limpia_nombre_excepto_2(s):
    if not s:
        return ''
    validchars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890."
    stripped = ''.join(c for c in s if c in validchars)
    return stripped


def getfilefromtitle(url, title):
    # Imprime en el log lo que va a descartar
    logger.info("title=" + title)
    logger.info("url=" + url)
    plataforma = config.get_system_platform()
    logger.info("plataforma=" + plataforma)

    # nombrefichero = filetools.makeLegalFilename(title + url[-4:])
    from . import scrapertools

    nombrefichero = title + scrapertools.get_filename_from_url(url)[-4:]
    logger.info("nombrefichero=%s" % nombrefichero)
    if "videobb" in url or "videozer" in url or "putlocker" in url:
        nombrefichero = title + ".flv"
    if "videobam" in url:
        nombrefichero = title + "." + url.rsplit(".", 1)[1][0:3]

    logger.info("nombrefichero=%s" % nombrefichero)

    nombrefichero = limpia_nombre_caracteres_especiales(nombrefichero)

    logger.info("nombrefichero=%s" % nombrefichero)

    fullpath = filetools.join(config.get_setting("downloadpath"), nombrefichero)
    logger.info("fullpath=%s" % fullpath)

    return fullpath


def downloadtitle(url, title):
    fullpath = getfilefromtitle(url, title)
    return downloadfile(url, fullpath)


def downloadbest(video_urls, title, continuar=False):
    logger.info()

    # Le da la vuelta, para poner el de más calidad primero ( list() es para que haga una copia )
    invertida = list(video_urls)
    invertida.reverse()

    for elemento in invertida:
        # videotitle = elemento[0]
        url = elemento[1]
        if not PY3:
            logger.info("Descargando opción " + title + " " + url.encode('ascii', 'ignore'))
        else:
            logger.info("Descargando opción " + title + " " + url.encode('ascii', 'ignore').decode('utf-8'))

        # Calcula el fichero donde debe grabar
        try:
            fullpath = getfilefromtitle(url, title.strip())
        # Si falla, es porque la URL no vale para nada
        except:
            import traceback
            logger.error(traceback.format_exc())
            continue

        # Descarga
        try:
            ret = downloadfile(url, fullpath, continuar=continuar)
        # Llegados a este punto, normalmente es un timeout
        except urllib_error.URLError as e:
            import traceback
            logger.error(traceback.format_exc())
            ret = -2

        # El usuario ha cancelado la descarga
        if ret == -1:
            return -1
        else:
            # El fichero ni siquiera existe
            if not filetools.exists(fullpath):
                logger.info("-> No ha descargado nada, probando con la siguiente opción si existe")
            # El fichero existe
            else:
                tamanyo = filetools.getsize(fullpath)

                # Tiene tamaño 0
                if tamanyo == 0:
                    logger.info("-> Descargado un fichero con tamaño 0, probando con la siguiente opción si existe")
                    os.remove(fullpath)
                else:
                    logger.info("-> Descargado un fichero con tamaño %d, lo da por bueno" % tamanyo)
                    return 0

    return -2


def downloadfile(url, nombrefichero, headers=None, silent=False, continuar=False, resumir=True, title="Alfa"):
    logger.info("url=" + url)
    logger.info("nombrefichero=" + nombrefichero)

    if headers is None:
        headers = []

    progreso = None
    ret = 0

    try:
        # Si no es XBMC, siempre a "Silent"
        from platformcode import platformtools

        # antes
        # f=open(nombrefichero,"wb")

        nombrefichero = filetools.makeLegalFilename(nombrefichero)

        logger.info("nombrefichero=" + nombrefichero)

        # El fichero existe y se quiere continuar
        if filetools.exists(nombrefichero) and continuar:
            f = filetools.file_open(nombrefichero, 'r+b', vfs=VFS)
            if resumir:
                exist_size = filetools.getsize(nombrefichero)
                logger.info("el fichero existe, size=%d" % exist_size)
                grabado = exist_size
                f.seek(exist_size)
            else:
                exist_size = 0
                grabado = 0

        # el fichero ya existe y no se quiere continuar, se aborta
        elif filetools.exists(nombrefichero) and not continuar:
            logger.info("el fichero existe, no se descarga de nuevo")
            return -3

        # el fichero no existe
        else:
            exist_size = 0
            logger.info("el fichero no existe")

            f = filetools.file_open(nombrefichero, 'wb', vfs=VFS)
            grabado = 0

        # Crea el diálogo de progreso
        if not silent:
            progreso = platformtools.dialog_progress(title, "Descargando...", url, nombrefichero)

        # Si la plataforma no devuelve un cuadro de diálogo válido, asume modo silencio
        if progreso is None:
            silent = True

        if "|" in url:
            additional_headers = url.split("|")[1]
            if "&" in additional_headers:
                additional_headers = additional_headers.split("&")
            else:
                additional_headers = [additional_headers]

            for additional_header in additional_headers:
                logger.info("additional_header: " + additional_header)
                name = re.findall("(.*?)=.*?", additional_header)[0]
                value = urllib.unquote_plus(re.findall(".*?=(.*?)$", additional_header)[0])
                headers.append([name, value])

            url = url.split("|")[0]
            logger.info("url=" + url)

        # Timeout del socket a 60 segundos
        socket.setdefaulttimeout(60)

        h = urllib2.HTTPHandler(debuglevel=0)
        request = urllib2.Request(url)
        for header in headers:
            logger.info("Header=" + header[0] + ": " + header[1])
            request.add_header(header[0], header[1])

        if exist_size > 0:
            request.add_header('Range', 'bytes=%d-' % (exist_size,))

        opener = urllib2.build_opener(h)
        urllib2.install_opener(opener)
        try:
            connexion = opener.open(request)
        except urllib_error.HTTPError as e:
            logger.error("error %d (%s) al abrir la url %s" %
                         (e.code, e.msg, url))
            f.close()
            if not silent:
                progreso.close()
            # El error 416 es que el rango pedido es mayor que el fichero => es que ya está completo
            if e.code == 416:
                return 0
            else:
                return -2

        try:
            totalfichero = int(connexion.headers["Content-Length"])
        except ValueError:
            totalfichero = 1

        if exist_size > 0:
            totalfichero = totalfichero + exist_size

        logger.info("Content-Length=%s" % totalfichero)

        blocksize = 100 * 1024

        bloqueleido = connexion.read(blocksize)
        logger.info("Iniciando descarga del fichero, bloqueleido=%s" % len(bloqueleido))

        maxreintentos = 10

        while len(bloqueleido) > 0:
            try:
                # Escribe el bloque leido
                f.write(bloqueleido)
                grabado += len(bloqueleido)
                percent = int(float(grabado) * 100 / float(totalfichero))
                totalmb = float(float(totalfichero) / (1024 * 1024))
                descargadosmb = float(float(grabado) / (1024 * 1024))

                # Lee el siguiente bloque, reintentando para no parar todo al primer timeout
                reintentos = 0
                while reintentos <= maxreintentos:
                    try:
                        before = time.time()
                        bloqueleido = connexion.read(blocksize)
                        after = time.time()
                        if (after - before) > 0:
                            velocidad = old_div(len(bloqueleido), (after - before))
                            falta = totalfichero - grabado
                            if velocidad > 0:
                                tiempofalta = old_div(falta, velocidad)
                            else:
                                tiempofalta = 0
                            # logger.info(sec_to_hms(tiempofalta))
                            if not silent:
                                progreso.update(percent, "%.2fMB/%.2fMB (%d%%) %.2f Kb/s %s falta " %
                                                (descargadosmb, totalmb, percent, old_div(velocidad, 1024),
                                                 sec_to_hms(tiempofalta)))
                        break
                    except:
                        reintentos += 1
                        logger.info("ERROR en la descarga del bloque, reintento %d" % reintentos)
                        import traceback
                        logger.error(traceback.print_exc())

                # El usuario cancelo la descarga
                try:
                    if progreso.iscanceled():
                        logger.info("Descarga del fichero cancelada")
                        f.close()
                        progreso.close()
                        return -1
                except:
                    pass

                # Ha habido un error en la descarga
                if reintentos > maxreintentos:
                    logger.info("ERROR en la descarga del fichero")
                    f.close()
                    if not silent:
                        progreso.close()

                    return -2

            except:
                import traceback
                logger.error(traceback.print_exc())

                f.close()
                if not silent:
                    progreso.close()

                # platformtools.dialog_ok('Error al descargar' , 'Se ha producido un error' , 'al descargar el archivo')

                return -2

    except:
        if url.startswith("rtmp"):
            error = downloadfileRTMP(url, nombrefichero, silent)
            if error and not silent:
                from platformcode import platformtools
            platformtools.dialog_ok("No puedes descargar ese vídeo", "Las descargas en RTMP aún no", "están soportadas")
        else:
            ret = -2
            import traceback
            from pprint import pprint
            exc_type, exc_value, exc_tb = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            for line in lines:
                line_splits = line.split("\n")
                for line_split in line_splits:
                    logger.error(line_split)

    try:
        f.close()
    except:
        pass

    if not silent:
        try:
            progreso.close()
        except:
            pass

    logger.info("Fin descarga del fichero")
    return ret


def downloadfileRTMP(url, nombrefichero, silent):
    ''' No usa librtmp ya que no siempre está disponible.
        Lanza un subproceso con rtmpdump. En Windows es necesario instalarlo.
        No usa threads así que no muestra ninguna barra de progreso ni tampoco
        se marca el final real de la descarga en el log info.
    '''
    Programfiles = os.getenv('Programfiles')
    if Programfiles:  # Windows
        rtmpdump_cmd = Programfiles + "/rtmpdump/rtmpdump.exe"
        nombrefichero = '"' + nombrefichero + '"'  # Windows necesita las comillas en el nombre
    else:
        rtmpdump_cmd = "/usr/bin/rtmpdump"

    if not filetools.isfile(rtmpdump_cmd) and not silent:
        from platformcode import platformtools
        advertencia = platformtools.dialog_ok("Falta " + rtmpdump_cmd, "Comprueba que rtmpdump está instalado")
        return True

    valid_rtmpdump_options = ["help", "url", "rtmp", "host", "port", "socks", "protocol", "playpath", "playlist",
                              "swfUrl", "tcUrl", "pageUrl", "app", "swfhash", "swfsize", "swfVfy", "swfAge", "auth",
                              "conn", "flashVer", "live", "subscribe", "realtime", "flv", "resume", "timeout", "start",
                              "stop", "token", "jtv", "hashes", "buffer", "skip", "quiet", "verbose",
                              "debug"]  # for rtmpdump 2.4

    url_args = url.split(' ')
    rtmp_url = url_args[0]
    rtmp_args = url_args[1:]

    rtmpdump_args = ["--rtmp", rtmp_url]
    for arg in rtmp_args:
        n = arg.find('=')
        if n < 0:
            if arg not in valid_rtmpdump_options:
                continue
            rtmpdump_args += ["--" + arg]
        else:
            if arg[:n] not in valid_rtmpdump_options:
                continue
            rtmpdump_args += ["--" + arg[:n], arg[n + 1:]]

    try:
        rtmpdump_args = [rtmpdump_cmd] + rtmpdump_args + ["-o", nombrefichero]
        from os import spawnv, P_NOWAIT
        logger.info("Iniciando descarga del fichero: %s" % " ".join(rtmpdump_args))
        rtmpdump_exit = spawnv(P_NOWAIT, rtmpdump_cmd, rtmpdump_args)
        if not silent:
            from platformcode import platformtools
            advertencia = platformtools.dialog_ok("La opción de descarga RTMP es experimental",
                                                  "y el vídeo se descargará en segundo plano.",
                                                  "No se mostrará ninguna barra de progreso.")
    except:
        return True

    return


def downloadfileGzipped(url, pathfichero):
    logger.info("url=" + url)
    nombrefichero = pathfichero
    logger.info("nombrefichero=" + nombrefichero)

    nombrefichero = filetools.makeLegalFilename(nombrefichero)
    logger.info("nombrefichero=" + nombrefichero)
    patron = "(http://[^/]+)/.+"
    matches = re.compile(patron, re.DOTALL).findall(url)

    if len(matches):
        logger.info("URL principal :" + matches[0])
        url1 = matches[0]
    else:
        url1 = url

    txheaders = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; '
                      'Media Center PC 5.0; .NET CLR 3.0.04506)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-es,es;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '115',
        'Connection': 'keep-alive',
        'Referer': url1,
    }

    txdata = ""

    # Crea el diálogo de progreso
    from platformcode import platformtools
    progreso = platformtools.dialog_progress("addon", config.get_localized_string(60200), url.split("|")[0], nombrefichero)

    # Timeout del socket a 60 segundos
    socket.setdefaulttimeout(10)

    h = urllib2.HTTPHandler(debuglevel=0)
    request = urllib2.Request(url, txdata, txheaders)
    # if existSize > 0:
    #    request.add_header('Range', 'bytes=%d-' % (existSize, ))

    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    try:
        connexion = opener.open(request)
    except urllib_error.HTTPError as e:
        logger.error("error %d (%s) al abrir la url %s" %
                     (e.code, e.msg, url))
        progreso.close()
        # El error 416 es que el rango pedido es mayor que el fichero => es que ya está completo
        if e.code == 416:
            return 0
        else:
            return -2

    nombre_fichero_base = filetools.basename(nombrefichero)
    if len(nombre_fichero_base) == 0:
        logger.info("Buscando nombre en el Headers de respuesta")
        nombre_base = connexion.headers["Content-Disposition"]
        logger.info(nombre_base)
        patron = 'filename="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(nombre_base)
        if len(matches) > 0:
            titulo = matches[0]
            titulo = GetTitleFromFile(titulo)
            nombrefichero = filetools.join(pathfichero, titulo)
        else:
            logger.info("Nombre del fichero no encontrado, Colocando nombre temporal :sin_nombre.txt")
            titulo = "sin_nombre.txt"
            nombrefichero = filetools.join(pathfichero, titulo)
    try:
        totalfichero = int(connexion.headers["Content-Length"])
    except ValueError:
        totalfichero = 1

    # despues
    f = filetools.file_open(nombrefichero, 'w', vfs=VFS)

    logger.info("fichero nuevo abierto")

    grabado = 0
    logger.info("Content-Length=%s" % totalfichero)

    blocksize = 100 * 1024

    bloqueleido = connexion.read(blocksize)

    try:
        import io
        compressedstream = io.StringIO(bloqueleido)
        import gzip
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        bloquedata = gzipper.read()
        gzipper.close()
        logger.info("Iniciando descarga del fichero, bloqueleido=%s" % len(bloqueleido))
    except:
        logger.error("ERROR : El archivo a descargar no esta comprimido con Gzip")
        f.close()
        progreso.close()
        return -2

    maxreintentos = 10

    while len(bloqueleido) > 0:
        try:
            # Escribe el bloque leido
            f.write(bloquedata)
            grabado += len(bloqueleido)
            percent = int(float(grabado) * 100 / float(totalfichero))
            totalmb = float(float(totalfichero) / (1024 * 1024))
            descargadosmb = float(float(grabado) / (1024 * 1024))

            # Lee el siguiente bloque, reintentando para no parar todo al primer timeout
            reintentos = 0
            while reintentos <= maxreintentos:
                try:
                    before = time.time()
                    bloqueleido = connexion.read(blocksize)

                    import gzip
                    import io
                    compressedstream = io.StringIO(bloqueleido)
                    gzipper = gzip.GzipFile(fileobj=compressedstream)
                    bloquedata = gzipper.read()
                    gzipper.close()
                    after = time.time()
                    if (after - before) > 0:
                        velocidad = old_div(len(bloqueleido), (after - before))
                        falta = totalfichero - grabado
                        if velocidad > 0:
                            tiempofalta = old_div(falta, velocidad)
                        else:
                            tiempofalta = 0
                        logger.info(sec_to_hms(tiempofalta))
                        progreso.update(percent, "%.2fMB/%.2fMB (%d%%) %.2f Kb/s %s falta " %
                                        (descargadosmb, totalmb, percent, old_div(velocidad, 1024), sec_to_hms(tiempofalta)))
                    break
                except:
                    reintentos += 1
                    logger.info("ERROR en la descarga del bloque, reintento %d" % reintentos)
                    for line in sys.exc_info():
                        logger.error("%s" % line)

            # El usuario cancelo la descarga
            if progreso.iscanceled():
                logger.info("Descarga del fichero cancelada")
                f.close()
                progreso.close()
                return -1

            # Ha habido un error en la descarga
            if reintentos > maxreintentos:
                logger.info("ERROR en la descarga del fichero")
                f.close()
                progreso.close()

                return -2

        except:
            logger.info("ERROR en la descarga del fichero")
            for line in sys.exc_info():
                logger.error("%s" % line)
            f.close()
            progreso.close()

            return -2
    f.close()

    # print data
    progreso.close()
    logger.info("Fin descarga del fichero")
    return nombrefichero


def GetTitleFromFile(title):
    # Imprime en el log lo que va a descartar
    logger.info("titulo=" + title)
    plataforma = config.get_system_platform()
    logger.info("plataforma=" + plataforma)

    # nombrefichero = filetools.makeLegalFilename(title + url[-4:])
    nombrefichero = title
    return nombrefichero


def sec_to_hms(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def downloadIfNotModifiedSince(url, timestamp):
    logger.info("(" + url + "," + time.ctime(timestamp) + ")")

    # Convierte la fecha a GMT
    fecha_formateada = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(timestamp))
    logger.info("fechaFormateada=%s" % fecha_formateada)

    # Comprueba si ha cambiado
    inicio = time.clock()
    req = urllib2.Request(url)
    req.add_header('If-Modified-Since', fecha_formateada)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12')

    updated = False

    try:
        response = urllib2.urlopen(req)
        data = response.read()

        # Si llega hasta aquí, es que ha cambiado
        updated = True
        response.close()

    except urllib_error.URLError as e:
        # Si devuelve 304 es que no ha cambiado
        if hasattr(e, 'code'):
            logger.info("Codigo de respuesta HTTP : %d" % e.code)
            if e.code == 304:
                logger.info("No ha cambiado")
                updated = False
        # Agarra los errores con codigo de respuesta del servidor externo solicitado     
        else:
            for line in sys.exc_info():
                logger.error("%s" % line)
        data = ""

    fin = time.clock()
    logger.info("Descargado en %d segundos " % (fin - inicio + 1))

    return updated, data


def download_all_episodes(item, channel, first_episode="", preferred_server="vidspot", filter_language=""):
    logger.info("show=" + item.show)
    show_title = item.show

    # Obtiene el listado desde el que se llamó
    action = item.extra

    # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
    if "###" in item.extra:
        action = item.extra.split("###")[0]
        item.extra = item.extra.split("###")[1]

    episode_itemlist = getattr(channel, action)(item)

    # Ordena los episodios para que funcione el filtro de first_episode
    episode_itemlist = sorted(episode_itemlist, key=lambda it: it.title)

    from core import servertools
    from core import scrapertools

    best_server = preferred_server
    # worst_server = "moevideos"

    # Para cada episodio
    if first_episode == "":
        empezar = True
    else:
        empezar = False

    for episode_item in episode_itemlist:
        try:
            logger.info("episode=" + episode_item.title)
            episode_title = scrapertools.find_single_match(episode_item.title, "(\d+x\d+)")
            logger.info("episode=" + episode_title)
        except:
            import traceback
            logger.error(traceback.format_exc())
            continue

        if first_episode != "" and episode_title == first_episode:
            empezar = True

        if episodio_ya_descargado(show_title, episode_title):
            continue

        if not empezar:
            continue

        # Extrae los mirrors
        try:
            mirrors_itemlist = channel.findvideos(episode_item)
        except:
            mirrors_itemlist = servertools.find_video_items(episode_item)
        print(mirrors_itemlist)

        descargado = False

        new_mirror_itemlist_1 = []
        new_mirror_itemlist_2 = []
        new_mirror_itemlist_3 = []
        new_mirror_itemlist_4 = []
        new_mirror_itemlist_5 = []
        new_mirror_itemlist_6 = []

        for mirror_item in mirrors_itemlist:

            # Si está en español va al principio, si no va al final
            if "(Español)" in mirror_item.title:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_1.append(mirror_item)
                else:
                    new_mirror_itemlist_2.append(mirror_item)
            elif "(Latino)" in mirror_item.title:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_3.append(mirror_item)
                else:
                    new_mirror_itemlist_4.append(mirror_item)
            elif "(VOS)" in mirror_item.title:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_3.append(mirror_item)
                else:
                    new_mirror_itemlist_4.append(mirror_item)
            else:
                if best_server in mirror_item.title.lower():
                    new_mirror_itemlist_5.append(mirror_item)
                else:
                    new_mirror_itemlist_6.append(mirror_item)

        mirrors_itemlist = (new_mirror_itemlist_1 + new_mirror_itemlist_2 + new_mirror_itemlist_3 +
                            new_mirror_itemlist_4 + new_mirror_itemlist_5 + new_mirror_itemlist_6)

        for mirror_item in mirrors_itemlist:
            logger.info("mirror=" + mirror_item.title)

            if "(Español)" in mirror_item.title:
                idioma = "(Español)"
                codigo_idioma = "es"
            elif "(Latino)" in mirror_item.title:
                idioma = "(Latino)"
                codigo_idioma = "lat"
            elif "(VOS)" in mirror_item.title:
                idioma = "(VOS)"
                codigo_idioma = "vos"
            elif "(VO)" in mirror_item.title:
                idioma = "(VO)"
                codigo_idioma = "vo"
            else:
                idioma = "(Desconocido)"
                codigo_idioma = "desconocido"

            logger.info("filter_language=#" + filter_language + "#, codigo_idioma=#" + codigo_idioma + "#")
            if filter_language == "" or (filter_language != "" and filter_language == codigo_idioma):
                logger.info("downloading mirror")
            else:
                logger.info("language " + codigo_idioma + " filtered, skipping")
                continue

            if hasattr(channel, 'play'):
                video_items = channel.play(mirror_item)
            else:
                video_items = [mirror_item]

            if len(video_items) > 0:
                video_item = video_items[0]

                # Comprueba que está disponible
                video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(video_item.server,
                                                                                        video_item.url,
                                                                                        video_password="",
                                                                                        muestra_dialogo=False)

                # Lo añade a la lista de descargas
                if puedes:
                    logger.info("downloading mirror started...")
                    # El vídeo de más calidad es el último
                    # mediaurl = video_urls[len(video_urls) - 1][1]
                    devuelve = downloadbest(video_urls, show_title + " " + episode_title + " " + idioma +
                                            " [" + video_item.server + "]", continuar=False)

                    if devuelve == 0:
                        logger.info("download ok")
                        descargado = True
                        break
                    elif devuelve == -1:
                        try:
                            from platformcode import platformtools
                            platformtools.dialog_ok("plugin", "Descarga abortada")
                        except:
                            pass
                        return
                    else:
                        logger.info("download error, try another mirror")
                        continue

                else:
                    logger.info("downloading mirror not available... trying next")

        if not descargado:
            logger.info("EPISODIO NO DESCARGADO " + episode_title)


def episodio_ya_descargado(show_title, episode_title):
    from . import scrapertools
    ficheros = os.listdir(".")

    for fichero in ficheros:
        # logger.info("fichero="+fichero)
        if fichero.lower().startswith(show_title.lower()) and \
                        scrapertools.find_single_match(fichero, "(\d+x\d+)") == episode_title:
            logger.info("encontrado!")
            return True

    return False
