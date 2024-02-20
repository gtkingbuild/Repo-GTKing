# -*- coding: utf-8 -*-

import random

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, jsontools


try:
   from lib.megaserver import Client
except:
   from lib.megaserver2 import Client


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if page_url:
        try:
            url_id = page_url.split('#')[1]
            file_id = url_id.split('!')[1]
        except:
            file_id = ''

        if file_id:
            get = ''
            post = {'a': 'g', 'g': 1, 'p': file_id}

            if '/#F!' in page_url:
                get = '&n=' + file_id
                post = {'a': 'f', 'c': 1, 'r': 0}

            nro = random.randint(0, 0xFFFFFFFF)

            api = 'https://g.api.mega.co.nz/cs?id=%d%s' % (nro, get)
            resp = httptools.downloadpage(api, post=jsontools.dump([post]))

            if resp.data == '[-18]': return 'Temporalmente No disponible'
            elif resp.data == '[-17]': return 'Excedida su cuota de transferiencia permitida'
            elif resp.data == '[-16]': return 'Cuenta baneada'
            elif resp.data == '[-15]': return 'Sesión expirada o inválida'
            elif resp.data == '[-14]': return 'Error al desencriptar'
            elif resp.data == '[-13]': return 'Archivo incompleto'
            elif resp.data == '[-13]': return 'Acceso restringido'
            elif resp.data == '[-9]': return 'Archivo NO encontrado'
            elif resp.data == '[-6]': return 'Cuenta eliminada'
            elif resp.data == '[-4]': return 'Excedida cuota transferiencia. Intentelo más tarde'
            else:
               if '[-' in resp.data: return 'Vídeo con algún problema desconocido'

    page_url = page_url.replace('/embed#!', '/embed#')
    page_url = page_url.replace('/embed/', '/embed#')

    page_url = page_url.replace('/file/', '/embed#')

    page_url = page_url.replace('/embed#', '/#!')

    try:
       c = Client(url=page_url, is_playing_fnc=platformtools.is_playing)
       files = c.get_files()
    except:
       color_exec = config.get_setting('notification_exec_color', default='cyan')
       el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
       el_srv += ('Mega[/B][/COLOR]')
       platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
       return video_urls

    if len(files) > 5:
        media_url = c.get_play_list()
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:], media_url])
    else:
        for f in files:
            media_url = f["url"]
            video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:], media_url])

    if len(video_urls) == 1:
        if '.zip ' in str(video_urls):
            return "El archivo está en formato comprimido"

    return video_urls