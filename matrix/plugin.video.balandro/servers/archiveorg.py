# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if 'archive.org/download/' in page_url:
        url = httptools.downloadpage(page_url, follow_redirects=False, only_headers=True).headers.get('location', '')
        if url: video_urls.append(['mp4', url])
        return video_urls

    data = httptools.downloadpage(page_url).data

    subtitles = ''
    # ~ try:
        # ~ bloque = scrapertools.find_single_match(data, '"tracks":(\[.*?\])')
        # ~ if bloque:
            # ~ data_json = jsontools.load(bloque)
            # ~ if 'file' in data_json[0]:
                # ~ subtitles = data_json[0]['file']
                # ~ if subtitles.startswith('/'): subtitles = 'https://archive.org' + subtitles
    # ~ except:
        # ~ pass

    try:
        bloque = scrapertools.find_single_match(data, '"sources":(\[.*?\])')
        if not bloque: return video_urls

        data_json = jsontools.load(bloque)
        try:
            lista = sorted(data_json, key=lambda x: (x['height'], x['width']))
        except:
            lista = data_json

        for vid in lista:
            if 'file' not in vid: continue
            url = vid['file']
            if url.startswith('/'): url = 'https://archive.org' + url

            tit = ''
            if 'type' in vid: tit = vid['type']
            if 'label' in vid: tit += ' %s' % vid['label']
            if 'width' in vid and 'height' in vid: tit += ' %sx%s' % (vid['width'], vid['height'])
            if tit == '': tit = url[-4:]

            video_urls.append([tit, url, 0, subtitles])
    except:
        pass

    return video_urls
