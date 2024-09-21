# -*- coding: utf-8 -*-

import re

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    if 'okru.link/v2' in page_url:
        v = scrapertools.find_single_match(page_url, "t=([\w\.]+)")

        headers = {"Content-Type" : "application/x-www-form-urlencoded", "Origin" : page_url}
        post = {"video" : v}

        data = httptools.downloadpage("https://apizz.okru.link/decoding", post = post, headers = headers).data

        if '<p>Por causas ajenas a' in data or '>Por causas ajenas a' in data:
            return 'Servidor Bloqueado por su Operadora'

        elif str(data) == '{"status":"decoding"}':
            return 'Archivo Bloqueado por su Operadora'

        video = scrapertools.find_single_match(data,'"url":"(.*?)"')

        if video:
            video = video.replace('\\/', '/')

            video_urls.append(['mp4', video])

        return video_urls

    elif 'okru.link/embed' in page_url:
         v = scrapertools.find_single_match(page_url, "t=(\w+)")

         data = httptools.downloadpage("https://okru.link/details.php?v=" + v).data

         if '<p>Por causas ajenas a' in data or '>Por causas ajenas a' in data:
             return 'Servidor Bloqueado por su Operadora'

         elif str(data) == '{"status":"decoding"}':
             return 'Archivo Bloqueado por su Operadora'

         video = scrapertools.find_single_match(data,'"file":"(.*?)"')

         if video:
             video = video.replace('\\/', '/')

             video_urls.append(['mp4', video])

         return video_urls

    elif 'okru.link' in page_url:
         v = scrapertools.find_single_match(page_url, "t=(\w+)")

         data = httptools.downloadpage("https://okru.link/details.php?v=" + v).data

         if '<p>Por causas ajenas a' in data or '>Por causas ajenas a' in data:
             return 'Servidor Bloqueado por su Operadora'

         elif str(data) == '{"status":"decoding"}':
             return 'Archivo Bloqueado por su Operadora'

         video = scrapertools.find_single_match(str(data), '"file":"(.*?)"')
         video = video.replace('\\/', '/')

         if video: video_urls.append(['mp4', video])

         return video_urls

    elif '/embed.html' in page_url or  '/embed_vf.html' in page_url:
       if '/embed.html' in page_url: new_page_url = page_url.replace('/embed.html?t=', '/details.php?v=')
       else: new_page_url = page_url.replace('/v2/embed_vf.html?t=', '/details.php?v=')

       post = scrapertools.find_single_match(new_page_url, "v=(.*?)$")

       if post:
           data = httptools.downloadpage(new_page_url, post = {'v': post}).data

           video = scrapertools.find_single_match(data, '"file":"(.*?)"')
           video = video.replace('\\/', '/')

           if video: video_urls.append(['mp4', video])

           return video_urls

    data = httptools.downloadpage(page_url).data

    if "copyrightsRestricted" in data or "COPYRIGHTS_RESTRICTED" in data or "copyrights_rstricted" in data or "limited_access" in data or "LIMITED_ACCESS" in data:
        return 'Archivo eliminado Violación Copyright'
    elif 'author of this video has not been found or is blocked' in data:
        return 'Autor del vídeo inexistente ó bloqueado'
    elif 'Access to this video is restricted' in data:
        return 'El acceso al vídeo está Restringido'
    elif 'src="/captcha.asd.js?v=' in data:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
    elif "notFound" in data:
        return 'Archivo inexistente ó eliminado'

    data = scrapertools.decodeHtmlentities(data).replace('\\', '')

    for tipo, url in re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"', data, re.DOTALL):
        url = url.replace("%3B", ";").replace("u0026", "&")

        video_urls.append([tipo, url])

    return video_urls
