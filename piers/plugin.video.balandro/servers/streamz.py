# -*- coding: utf-8 -*-

import os

from platformcode import logger, config
from core import httptools, scrapertools, filetools, jsontools

from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    path_server = os.path.join(config.get_runtime_path(), 'servers', 'streamz.json')
    data = filetools.read(path_server)
    dict_server = jsontools.load(data)

    try:
       notes = dict_server['notes']
    except: 
       notes = ''

    if "out of service" in notes.lower(): return 'Fuera de Servicio'

    data = httptools.downloadpage(page_url).data

    if "<b>File not found, sorry!</b" in data:
        return "Archivo inexistente ó eliminado"

    try:
       pack = scrapertools.find_single_match(data, 'p,a,c,k,e,d.*?</script>')

       unpacked = jsunpack.unpack(pack).replace("\\", "" )
       url = scrapertools.find_single_match(unpacked, "src:'([^']+)'")

       if url:
           url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')

           if url:
               if not '/issue.mp4' in url:
                   url += "|User-Agent=%s" % httptools.get_user_agent()
                   video_urls.append(['mp4', url])
    except:
       pass

    return video_urls
