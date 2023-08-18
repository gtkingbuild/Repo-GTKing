# -*- coding: utf-8 -*-

import time

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, jsontools


espera = config.get_setting('servers_waiting', default=6)


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('/api/source/', '/f/')

    page_url = page_url.replace('/fembeder.com/', '/www.fembed.com/').replace('/divload.com/', '/www.fembed.com/').replace('/ilovefembed.best/', '/www.fembed.com/').replace('/myurlshort.live/', '/www.fembed.com/')
    page_url = page_url.replace('/jplayer.club/', '/www.fembed.com/').replace('/fembedisthebest.rest/', '/www.fembed.com/').replace('/pelispng.online/', '/www.fembed.com/')
    page_url = page_url.replace('/embedsito.com/', '/www.fembed.com/').replace('/mrdhan.com/', '/www.fembed.com/').replace('/dutrag.com/', '/www.fembed.com/').replace('/fplayer.info/', '/www.fembed.com/')

    if 'fembed.com' in page_url:
        page_url = page_url.replace('/fembed.com/', '/www.fembed.com/')
        page_url = page_url.replace('/www.fembed.com/', '/vanfem.com/')

    elif 'fembed.live' in page_url:
        page_url = page_url.replace('/www.fembed.live/', '/vanfem.com/').replace('/fembed.live/', '/vanfem.com/')
    elif 'fembed.net' in page_url:
        page_url = page_url.replace('/www.fembed.net/', '/vanfem.com/').replace('/fembed.net/', '/vanfem.com/')
    elif 'feurl.com' in page_url:
        page_url = page_url.replace('/www.feurl.com/', '/vanfem.com/').replace('/feurl.com/', '/vanfem.com/')
    elif 'femax20.com' in page_url:
        page_url = page_url.replace('/www.femax20.com/', '/vanfem.com/').replace('/femax20.com/', '/vanfem.com/')
    elif 'fcdn.stream' in page_url:
        page_url = page_url.replace('/www.fcdn.stream/', '/vanfem.com/').replace('/fcdn.stream/', '/vanfem.com/')
    elif 'fembad.org' in page_url:
        page_url = page_url.replace('/www.fembad.org/', '/vanfem.com/').replace('/fembad.org/', '/vanfem.com/')

    elif 'owodeuwu.xyz' in page_url:
        page_url = page_url.replace('/www.owodeuwu.xyz/', '/vanfem.com/').replace('/owodeuwu.xyz/', '/vanfem.com/')

    elif 'hlshd.xyz' in page_url:
        page_url = page_url.replace('/www.hlshd.xyz/', '/vanfem.com/').replace('/hlshd.xyz/', '/vanfem.com/')

    vid = scrapertools.find_single_match(page_url, "/(?:v|f)/([A-z0-9_-]+)")
    if not vid: return video_urls

    dom = scrapertools.find_single_match(page_url, "(https://[^/]+)")

    post = 'r=&d=feurl.com'

    data = httptools.downloadpage('https://www.fembed.com/api/source/' + vid, post=post).data

    try:
        data = jsontools.load(data)

        if 'data' not in data or 'success' not in data: return 'Vídeo no encontrado'

        if not data['success']:
            if not dom: return 'Vídeo no encontrado o eliminado'

            platformtools.dialog_notification('Cargando Fembed', 'Espera requerida de %s segundos' % espera)
            time.sleep(int(espera))

            post = {'r': '', 'd': dom.replace('https://', '')}
            data = httptools.downloadpage(dom +'/api/source/'+ vid, post=post).data

            try:
                data = jsontools.load(data)

                if 'data' not in data or 'success' not in data: return 'Vídeo no encontrado'

                if not data['success']: return 'Vídeo no encontrado o eliminado'
            except:
                return video_urls

        for videos in data['data']:
            if 'file' in videos:
                url = videos['file'] if videos['file'].startswith('http') else dom + videos['file']

                url = url.replace('\\/', '/')

                if '/redirector?' in url:
                    resp = httptools.downloadpage(url, follow_redirects=False)

                    if 'location' in resp.headers: url = resp.headers['location']

                if url:
                    # ~ 20/2/2023
                    url = url.replace('https', 'http')

                    ua = httptools.get_user_agent()
                    headers = httptools.default_headers.copy()
                    header_str = "&".join(["%s=%s" % (x, y) for x, y in list(headers.items()) if x!='User-Agent'])
                    url += "|User-Agent=%s&verifypeer=false&%s" % (ua, header_str)

                    lbl = videos['label'] if 'label' in videos and videos['label'] else 'mp4'

                    video_urls.append([lbl, url])
    except:
        pass

    return video_urls
