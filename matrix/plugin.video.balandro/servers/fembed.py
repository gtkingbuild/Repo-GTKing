# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    dom = scrapertools.find_single_match(page_url, "(https://[^/]+)")

    page_url = page_url.replace('/api/source/', '/f/')

    page_url = page_url.replace('/fembeder.com/', '/www.fembed.com/').replace('/divload.com/', '/www.fembed.com/').replace('/ilovefembed.best/', '/www.fembed.com/').replace('/myurlshort.live/', '/www.fembed.com/')
    page_url = page_url.replace('/jplayer.club/', '/www.fembed.com/').replace('/fembedisthebest.rest/', '/www.fembed.com/').replace('/pelispng.online/', '/www.fembed.com/')
    page_url = page_url.replace('/embedsito.com/', '/www.fembed.com/').replace('/mrdhan.com/', '/www.fembed.com/').replace('/dutrag.com/', '/www.fembed.com/').replace('/fplayer.info/', '/www.fembed.com/')

    if 'fembed.com' in page_url:
        page_url = page_url.replace('/fembed.com/', '/www.fembed.com/')
    elif 'fembed.live' in page_url:
        page_url = page_url.replace('/www.fembed.live/', '/diasfem.com/').replace('/fembed.live/', '/diasfem.com/')
    elif 'fembed.net' in page_url:
        page_url = page_url.replace('/www.fembed.net/', '/diasfem.com/').replace('/fembed.net/', '/diasfem.com/')
    elif 'feurl.com' in page_url:
        page_url = page_url.replace('/www.feurl.com/', '/diasfem.com/').replace('/feurl.com/', '/diasfem.com/')
    elif 'femax20.com' in page_url:
        page_url = page_url.replace('/www.femax20.com/', '/diasfem.com/').replace('/femax20.com/', '/diasfem.com/')
    elif 'fcdn.stream' in page_url:
        page_url = page_url.replace('/www.fcdn.stream/', '/diasfem.com/').replace('/fcdn.stream/', '/diasfem.com/')
    elif 'fembad.org' in page_url:
        page_url = page_url.replace('/www.fembad.org/', '/diasfem.com/').replace('/fembad.org/', '/diasfem.com/')

    elif 'owodeuwu.xyz' in page_url:
        page_url = page_url.replace('/www.owodeuwu.xyz/', '/diasfem.com/').replace('/owodeuwu.xyz/', '/diasfem.com/')

    elif 'hlshd.xyz' in page_url:
        page_url = page_url.replace('/www.hlshd.xyz/', '/diasfem.com/').replace('/hlshd.xyz/', '/diasfem.com/')

    vid = scrapertools.find_single_match(page_url, "/(?:v|f)/([A-z0-9_-]+)")
    if not vid: return video_urls

    post = 'r=&d=feurl.com'

    data = httptools.downloadpage('https://www.fembed.com/api/source/' + vid, post=post).data

    try:
        data = jsontools.load(data)

        if 'data' not in data or 'success' not in data: return 'Vídeo no encontrado'

        if not data['success']:
            if not dom: return 'Vídeo no encontrado o eliminado'

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

                if '/redirector?' in url:
                    resp = httptools.downloadpage(url, follow_redirects=False)
                    if 'location' in resp.headers:
                        url = resp.headers['location']

                lbl = videos['label'] if 'label' in videos and videos['label'] else 'mp4'
                video_urls.append([lbl, url])
    except:
        pass

    return video_urls
