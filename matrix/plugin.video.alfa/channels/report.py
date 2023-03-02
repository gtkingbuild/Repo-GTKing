# -*- coding: utf-8 -*-
# -*- Report module -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
import os
import sys
import random
import traceback
import re

from platformcode import config
from platformcode import logger
from platformcode import platformtools
from platformcode import envtal
from core.item import Item
from core import jsontools
from core import httptools
from core import scrapertools
from core import filetools
from channelselector import get_thumb

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if not PY3:
    import urllib  # Usamos el nativo de PY2 que es más rápido
    import urlparse
    from core import proxytools
else:
    import urllib.parse as urlparse  # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
    from core import proxytools_py3 as proxytools


def mainlist(item):
    logger.info()

    if not config.get_setting("debug"):
        config.set_setting("debug", True)
    if not config.get_setting("report_started", default=False):
        msg = "Por favor reproduzca el problema y vuelva a esta sección"
        platformtools.dialog_ok("Alfa - Reporte de errores", msg)
        config.set_setting("report_started", True)
        return
    else:
        itemlist = []
        thumb_next = get_thumb("next.png")
        item = report_send(item)
    
        # Se devuelve control con item.url actualizado, así aparecerá en el menú la URL del informe
        if item.url:
            from lib.generictools import call_browser
            browser, res = call_browser(item, lookup=True)
            titles = {'report_title': 'Ha terminado de generar el informe de fallo,',
                      'report_text': '[COLOR limegreen]Repórtelo en el Foro de Alfa: [/COLOR][COLOR yellow](pinche para usar [I]%s[/I])[/COLOR]' % browser,
                      'forum': '**- [COLOR yellow] https://alfa-addon.com/foros/ayuda.12/ [/COLOR] -**',
                      'log': '**- LOG: [COLOR gold]%s[/COLOR] -**' % item.url}
            urls = {'forum': 'https://alfa-addon.com/foros/ayuda.12/',
                    'log': item.url,
                    'log_one_use': item.url}
            actions = {'browser': 'call_browser',
                       'browser_one_use': 'call_browser'}

            if not browser:
                titles['report_title'] = 'Repórtelo en el Foro de Alfa: '
                urls['forum'] = ''
                actions['browser'] = ''

            if item.one_use:
                urls['log_one_use'] = ''
                actions['browser_one_use'] = ''

            itemlist.append(
                Item(
                    channel = item.channel,
                    folder = False,
                    text_color = 'limegreen',
                    thumbnail = thumb_next,
                    title = titles['report_title']
                )
            )

            itemlist.append(
                Item(
                    action = actions['browser'],
                    channel = 'setting',
                    folder = False,
                    thumbnail = thumb_next,
                    title = titles['report_text'],
                    url = urls['forum']
                )
            )

            itemlist.append(
                Item(
                    action = actions['browser'],
                    channel = 'setting',
                    folder = False,
                    thumbnail = thumb_next,
                    title = titles['forum'],
                    unify = False,
                    url = urls['forum']
                )
            )

            itemlist.append(
                Item(
                    action = actions['browser_one_use'],
                    channel = 'setting',
                    folder = False,
                    thumbnail = thumb_next,
                    title = titles['log'],
                    unify = False,
                    url = urls['log_one_use']
                )
            )
            
            if item.one_use:
                itemlist.append(
                    Item(
                        channel = item.channel,
                        folder = False,
                        text_color = 'orange',
                        thumbnail = thumb_next,
                        title = 'NO ACCEDA al INFORME: se BORRARÁ',
                    )
                )
                itemlist.append(
                    Item(
                        channel = item.channel,
                        folder = False,
                        text_color = 'orange',
                        thumbnail = thumb_next,
                        title = 'ya que es de un solo uso',
                    )
                )
        
        return itemlist


def report_send(item, description=False, fatal=False):

    try:
        requests_status = True
        import requests
    except:
        requests_status = False
        logger.error(traceback.format_exc())

    # Esta función realiza la operación de upload del LOG.  El tamaño del archivo es de gran importacia porque
    # los servicios de "pastebin" gratuitos tienen limitaciones, a veces muy bajas.
    # Hay un servicio, File.io, que permite subida directa de "archivos binarios" a través de la función "request"
    # Esto aumenta drásticamente la capacidad del envío del log, muy por encima de lo necesitado
    # Por ello es necesario contar con una lista de servicios "pastebin" que puedan realizar la operación de upload,
    # ya sea por capacidad disponible o por disponibilidad.
    # Para poder usar los servidores "pastebin" con un código común, se ha creado un diccionario con los servidores
    # y sus características.  En cada entrada se recogen las peculiaridades de cada servidor, tanto para formar
    # la petición consu POST como para la forma de recibir el código del upload en la respuesta (json, header, regex
    # en datos,...).
    # Al iniciar este método se aleatoriza la lista de servidores "pastebin" para evitar que todos los usuarios hagan
    # uploads contra el mismo servidor y puedan ocasionar sobrecargas.
    # Se lee el arcivo de log y se compara su tamaño con la capacidad del servidor (parámetro 10 de cada entrada
    # (empezando desde 0), expresado en MB, hasta que se encuentra uno capacitado. Si el upload falla se sigue intentado
    # con los siguientes servidores que tengan la capacidad requerida.
    # Si no se encuentra ningún servidor disponible se pide al usuario que lo intente más tarde, o que suba el log
    # directamente en el foro.  Si es un problema de tamaño, se le pide que reicinie Kodi y reproduzca el fallo, para
    # que el LOG sea más pequeño.

    pastebin_list = {
        'hastebin': {
            'active': True,
            'host': 'https://hastebin.com/',
            'api_suffix': 'documents',
            'filename': 'random',
            'post_data_1': '',
            'post_data_2': '',
            'method': 'data',
            'response_type': 'json',
            'response_key': 'key',
            'tag': '',
            'max_size_mb': 0.29,
            'timeout': 10,
            'random_headers': True,
            'host_return': 'raw/',
            'host_return_tail': '',
            'headers': ''
        },
        'dpaste': {
            'active': True,
            'host': 'http://dpaste.com/',
            'api_suffix': 'api/v2/',
            'filename': 'random',
            'post_data_1': 'content=',
            'post_data_2': '&syntax=text&title=%s&poster=alfa&expiry_days=7',
            'method': 'headers',
            'response_type': '',
            'response_key': '',
            'tag': 'location',
            'max_size_mb': 0.23,
            'timeout': 15,
            'random_headers': True,
            'host_return': '',
            'host_return_tail': '.txt',
            'headers': ''
        },
        'ghostbin': {
            'active': True,
            'host': 'https://ghostbin.com/',
            'api_suffix': 'new',
            'filename': 'random',
            'post_data_1': 'lang=text&text=',
            'post_data_2': '&expire=2d&password=&title=%s',
            'method': 'data',
            'response_type': 'regex',
            'response_key': '<h4\s*style=[^>]+>[^<]*(?:<[^>]+>)?\s*<a\s*href="\/?([^"]+)"',
            'tag': '',
            'max_size_mb': 99.9,
            'timeout': 15,
            'random_headers': True,
            'host_return': '',
            'host_return_tail': '',
            'headers': ''
        },
        'write.as': {
            'active': True,
            'host': 'https://write.as/',
            'api_suffix': 'api/posts',
            'filename': 'random',
            'post_data_1': 'body=',
            'post_data_2': '&title=%s',
            'method': 'data',
            'response_type': 'json',
            'response_key': 'data',
            'tag': 'id',
            'max_size_mb': 0.018,
            'timeout': 15,
            'random_headers': True,
            'host_return': '',
            'host_return_tail': '',
            'headers': ''
        },
        'controlc': {
            'active': False,
            'host': 'https://controlc.com/',
            'api_suffix': 'index.php?act=submit',
            'filename': 'random',
            'post_data_1': 'input_text=',
            'post_data_2': '&subdomain=&antispam=1&website=&timestamp=&paste_password=&code=0&paste_title=%s',
            'method': 'data',
            'response_type': 'regex',
            'response_key': '<h3>\s*<a\s*href="([^"]+)"',
            'tag': '',
            'max_size_mb': 99.0,
            'timeout': 5,
            'random_headers': True,
            'host_return': '',
            'host_return_tail': '',
            'headers': ''
        },
        'bpaste': {
            'active': True,
            'host': 'https://bpa.st/',
            'api_suffix': '',
            'filename': 'random',
            'post_data_1': 'code=',
            'post_data_2': '&lexer=text&expiry=1week',
            'method': 'data',
            'response_type': 'regex',
            'response_key': 'View\s*<a\s*href="[^*]+/(.*?)">raw<\/a>',
            'tag': '',
            'max_size_mb': 0.25,
            'timeout': 15,
            'random_headers': True,
            'host_return': 'raw/',
            'host_return_tail': '',
            'headers': ''
        },
        'dumpz': {
            'active': False,
            'host': 'https://dumpz.org/',
            'api_suffix': 'api/dump',
            'filename': 'random',
            'post_data_1': 'code=',
            'post_data_2': '&lexer=text&comment=%s&password=',
            'method': 'headers',
            'response_type': '',
            'response_key': '',
            'tag': 'location',
            'max_size_mb': 0.99,
            'timeout': 15,
            'random_headers': True,
            'host_return': '',
            'host_return_tail': '',
            'headers': ''
        },
        'file.io': {
            'active': True,
            'host': 'https://file.io/',
            'api_suffix': '',
            'filename': 'random',
            'post_data_1': '',
            'post_data_2': 'expires=1w',
            'method': 'requests',
            'response_type': 'json',
            'response_key': 'key',
            'tag': '',
            'max_size_mb': 99.0,
            'timeout': 30,
            'random_headers': True,
            'host_return': '',
            'host_return_tail': '',
            'headers': ''
        },
        'uploadfiles': {
            'active': False,
            'host': 'https://up.ufile.io/v1/upload',
            'api_suffix': '',
            'filename': 'random',
            'post_data_1': '',
            'post_data_2': '',
            'method': 'curl',
            'response_type': 'json',
            'response_key': 'url',
            'tag': '',
            'max_size_mb': 99.0,
            'timeout': 30,
            'random_headers': True,
            'host_return': None,
            'host_return_tail': '',
            'headers': {'Referer': 'https://ufile.io/'}
        },
        'anonfiles': {
            'active': True,
            'host': 'https://api.anonfiles.com/upload',
            'api_suffix': 'upload',
            'filename': 'random',
            'post_data_1': '',
            'post_data_2': '',
            'method': 'requests',
            'response_type': 'json',
            'response_key': 'data',
            'tag': 'file,url,short',
            'max_size_mb': 99.0,
            'timeout': 30,
            'random_headers': False,
            'host_return': None,
            'host_return_tail': '',
            'headers': ''
        },
    }

    pastebin_list_last = ['ghostbin', 'hastebin', 'file.io']  # Estos servicios los dejamos los últimos
    pastebin_one_use = ['file.io']  # Servidores de un solo uso y se borra
    pastebin_dir = []
    paste_file = {}
    paste_params = ()
    paste_post = ''
    status = False
    msg = 'Servicio no disponible.  Inténtelo más tarde'

    # De cada al futuro se permitira al usuario que introduzca una breve descripción del fallo que se añadirá al LOG
    if description:
        description = platformtools.dialog_input('', 'Introduzca una breve descripción del fallo')

    # Escribimos en el log algunas variables de Kodi y Alfa que nos ayudarán en el diagnóstico del fallo
    proxytools.logger_disp(debugging=True)
    environment = envtal.list_env()

    if not environment['log_path']:
        if filetools.exists(filetools.join("special://logpath/", 'kodi.log')):
            environment['log_path'] = str(filetools.join("special://logpath/", 'kodi.log'))
        else:
            environment['log_path'] = str(filetools.join("special://logpath/", 'xbmc.log'))
        environment['log_size_bytes'] = str(filetools.getsize(environment['log_path']))
        environment['log_size'] = str(round(float(environment['log_size_bytes']) / (1024 * 1024), 3))

    # Se lee el archivo de LOG
    log_path = environment['log_path']
    if filetools.exists(log_path):
        log_size_bytes = int(environment['log_size_bytes'])  # Tamaño del fichero en Bytes
        log_size = float(environment['log_size'])  # Tamaño del fichero en MB
        log_data = filetools.read(log_path)  # Datos del archivo
        if not log_data:  # Algún error?
            platformtools.dialog_notification('No se puede leer el log de Kodi',
                                              'Comuniquelo directamente en el Foro de Alfa')
            return
    else:  # Log no existe o path erroneo?
        platformtools.dialog_notification('LOG de Kodi no encontrado', 'Comuniquelo directamente en el Foro de Alfa')
        return

    # Si se ha introducido la descripción del fallo, se inserta la principio de los datos del LOG
    log_title = '***** DESCRIPCIÓN DEL FALLO *****'
    if description:
        log_data = '%s\n%s\n\n%s' % (log_title, description, log_data)

    # Se aleatorizan los nombre de los servidores "pastebin"
    for label_a, value_a in list(pastebin_list.items()):
        if label_a not in pastebin_list_last:
            pastebin_dir.append(label_a)
    random.shuffle(pastebin_dir)
    pastebin_dir.extend(pastebin_list_last)  # Estos servicios los dejamos los últimos

    # pastebin_dir = ['ghostbin']                                         # Para pruebas de un servicio
    # log_data = 'TEST PARA PRUEBAS DEL SERVICIO'

    # Se recorre la lista de servidores "pastebin" hasta localizar uno activo, con capacidad y disponibilidad
    for paste_name in pastebin_dir:
        paste_service = pastebin_list[paste_name]

        if not paste_service['active']:  # Si no esta activo el servidor, pasamos
            continue
        if paste_service['method'] == 'requests' and not requests_status:  # Si "requests" no esta activo, pasamos
            continue

        paste_host = paste_service['host']  # URL del servidor "pastebin"
        paste_sufix = paste_service['api_suffix']  # sufijo del API para el POST
        paste_title = ''

        if paste_service['filename'] == 'random':
            paste_title = "LOG" + str(random.randrange(1, 999999999))  # Título del LOG

        paste_post1 = paste_service['post_data_1']  # Parte inicial del POST
        paste_post2 = paste_service['post_data_2']  # Parte secundaria del POST
        paste_type = paste_service['method']  # Tipo de downloadpage: REQUESTS, DATA o HEADERS
        paste_resp = paste_service['response_type']  # Tipo de respuesta: JSON o datos con REGEX
        paste_resp_key = paste_service['response_key']  # Si es JSON, etiqueta primaria con la CLAVE
        paste_url = paste_service['tag']  # Etiqueta primaria para HEADER y sec. para JSON
        paste_file_size = paste_service['max_size_mb']  # Capacidad en MB del servidor

        if paste_file_size > 0:  # Si es 0, la capacidad es ilimitada
            if log_size > paste_file_size:  # Verificación de capacidad y tamaño
                msg = 'Archivo de log demasiado grande.  Reinicie Kodi y reinténtelo'
                continue

        paste_timeout = paste_service['timeout']  # Timeout para el servidor
        paste_random_headers = paste_service['random_headers']  # Utiliza RANDOM headers para despistar el srv?
        paste_host_return = paste_service['host_return']  # Parte de url para componer la clave para usuario
        paste_host_return_tail = paste_service['host_return_tail']  # Sufijo de url para componer la clave para usuario
        paste_headers = {}
        if paste_service['headers']:  # Headers requeridas por el servidor
            paste_headers.update(paste_service['headers'])

        if paste_name in pastebin_one_use:
            pastebin_one_use_msg = '[COLOR red]NO ACCEDA al INFORME: se BORRARÁ[/COLOR]'
            item.one_use = True
        else:
            pastebin_one_use_msg = ''

        try:
            # Se crea el POST con las opciones del servidor "pastebin"
            # Se trata el formato de "requests"
            if paste_type in ['requests', 'curl']:
                paste_file = {'file': (paste_title + '.log', log_data)}

                if paste_post1:
                    paste_file.update(paste_post1)

                if paste_post2:
                    if '%s' in paste_post2:
                        paste_params = paste_post2 % (paste_title + '.log', log_size_bytes)

                    else:
                        paste_params = paste_post2

            # Se trata el formato de downloads
            else:
                # log_data = 'Test de Servidor para ver su viabilidad (áéíóúñ¿?)'
                if paste_name in ['hastebin']:  # Hay algunos servicios que no necesitan "quote"
                    paste_post = log_data

                else:
                    paste_post = urllib.quote_plus(log_data)  # Se hace un "quote" de los datos del LOG

                if paste_post1:
                    paste_post = '%s%s' % (paste_post1, paste_post)

                if paste_post2:
                    if '%s' in paste_post2:
                        paste_post += paste_post2 % paste_title

                    else:
                        paste_post += paste_post2

            # Se hace la petición en downloadpage con HEADERS o DATA, con los parámetros del servidor
            if paste_type in ['data', 'headers']:
                data = httptools.downloadpage(paste_host + paste_sufix, post=paste_post,
                                              timeout=paste_timeout, random_headers=paste_random_headers,
                                              headers=paste_headers)
                data = data.data if paste_type == 'data' else data.headers

            # Si la petición es con formato REQUESTS, se realiza aquí
            elif paste_type == 'requests':
                # data = requests.post(paste_host, params=paste_params, files=paste_file,
                #            timeout=paste_timeout)
                data = httptools.downloadpage(paste_host, params=paste_params, file=log_data,
                                              file_name=paste_title + '.log', timeout=paste_timeout,
                                              random_headers=paste_random_headers, headers=paste_headers)

            elif paste_type == 'curl':
                paste_sufix = '/create_session'
                data_post = {'file_size': len(log_data)}
                data = httptools.downloadpage(paste_host + paste_sufix, params=paste_params,
                                              ignore_response_code=True, post=data_post, timeout=paste_timeout,
                                              alfa_s=True,
                                              random_headers=paste_random_headers, headers=paste_headers).data
                data = jsontools.load(data)
                if not data.get("fuid", ""):
                    logger.error("fuid: %s" % str(data))
                    raise
                fuid = data["fuid"]

                paste_sufix = '/chunk'
                log_data_chunks = log_data
                i = 0
                chunk_len = 1024
                while len(log_data_chunks) > 0:
                    i += 1
                    chunk = log_data_chunks[:chunk_len]
                    log_data_chunks = log_data_chunks[chunk_len:]
                    data_post = {'fuid': fuid, 'chunk_index': i}
                    data = httptools.downloadpage(paste_host + paste_sufix, params=paste_params, file=chunk,
                                                  alfa_s=True,
                                                  ignore_response_code=True, post=data_post, timeout=paste_timeout,
                                                  CF_test=False,
                                                  random_headers=paste_random_headers, headers=paste_headers).data
                    if not 'successful' in data:
                        logger.error("successful: %s" % str(data))
                        raise

                data = {}
                paste_sufix = '/finalise'
                data_post = {'fuid': fuid, 'total_chunks': i, 'file_name': paste_title + '.log', 'file_type': 'doc'}
                resp = httptools.downloadpage(paste_host + paste_sufix, params=paste_params,
                                              ignore_response_code=True, post=data_post, timeout=paste_timeout,
                                              random_headers=paste_random_headers, headers=paste_headers)
                if not resp.data:
                    logger.error("resp.content: %s" % str(resp.data))
                    raise
                data['data'] = resp.data
                data = type('HTTPResponse', (), data)

        except:
            msg = 'Inténtelo más tarde'
            logger.error('Fallo al guardar el informe. ' + msg)
            logger.error(traceback.format_exc())
            continue

        # Se analiza la respuesta del servidor y se localiza la clave del upload para formar la url a pasar al usuario
        if data:
            paste_host_resp = paste_host
            if paste_host_return == None:  # Si devuelve la url completa, no se compone
                paste_host_resp = ''
                paste_host_return = ''

            # Respuestas a peticiones REQUESTS
            key = ''
            if paste_type in ['requests', 'curl']:  # Respuesta de petición tipo "requests"?
                if paste_resp == 'json':  # Respuesta en formato JSON?
                    if paste_resp_key in data.data:
                        key = jsontools.load(data.data)[paste_resp_key]
                        if paste_url and key:  # hay etiquetas adicionales?
                            try:
                                for key_part in paste_url.split(','):
                                    key = key[key_part]  # por cada etiqueta adicional
                            except:
                                key = ''
                        if key:
                            item.url = "%s%s%s" % (paste_host_resp + paste_host_return, key,
                                                   paste_host_return_tail)
                    if not key:
                        logger.error('ERROR en formato de retorno de datos. data.data=' +
                                     str(data.data))
                        continue

            # Respuestas a peticiones DOWNLOADPAGE
            elif paste_resp == 'json':  # Respuesta en formato JSON?
                if paste_resp_key in data:
                    if not paste_url:
                        key = jsontools.load(data)[paste_resp_key]  # con una etiqueta
                    else:
                        key = jsontools.load(data)[paste_resp_key][paste_url]  # con dos etiquetas anidadas
                    item.url = "%s%s%s" % (paste_host_resp + paste_host_return, key,
                                           paste_host_return_tail)
                else:
                    logger.error('ERROR en formato de retorno de datos. data=' + str(data))
                    continue
            elif paste_resp == 'regex':  # Respuesta en DATOS, a buscar con un REGEX?
                key = scrapertools.find_single_match(data, paste_resp_key)
                if key:
                    item.url = "%s%s%s" % (paste_host_resp + paste_host_return, key,
                                           paste_host_return_tail)
                else:
                    logger.error('ERROR en formato de retorno de datos. data=' + str(data))
                    continue
            elif paste_type == 'headers':  # Respuesta en HEADERS, a buscar en "location"?
                if paste_url in data:
                    item.url = data[paste_url]  # Etiqueta de retorno de la clave
                    item.url = urlparse.urljoin(paste_host_resp + paste_host_return,
                                                item.url + paste_host_return_tail)
                else:
                    logger.error('ERROR en formato de retorno de datos. response.headers=' +
                                 str(data))
                    continue
            else:
                logger.error('ERROR en formato de retorno de datos. paste_type=' +
                             str(paste_type) + ' / DATA: ' + data)
                continue

            status = True  # Operación de upload terminada con éxito
            logger.info('Reporte de error creado con exito: ' + str(item.url))  # Se guarda la URL del informe a usuario
            if fatal:  # De uso futuro, para logger.crash
                platformtools.dialog_notification('Reporte de error creado con exito',
                                        'Repórtelo en el foro agregando ERROR FATAL y esta URL: ')
            else:  # Se pasa la URL del informe a usuario
                platformtools.dialog_notification('Reporte de error creado con exito',
                                        'Repórtelo en el foro agregando una descripcion del fallo y esta URL: ')

            break  # Operación terminado, no seguimos buscando

    if not status and not fatal:  # Operación fracasada...
        platformtools.dialog_notification('Fallo al guardar el informe', msg)  # ... se notifica la causa
        logger.error('Fallo al guardar el informe. ' + msg)

    channel_custom = os.path.join(config.get_runtime_path(), 'channels', 'custom.py')
    if not filetools.exists(channel_custom):
        config.set_setting("debug", False)

    config.set_setting("report_started", False)

    return item
