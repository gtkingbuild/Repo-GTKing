# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools, servertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    vid = scrapertools.find_single_match(page_url, "embedy.cc/embed/([A-z0-9=]+)")
    if vid:
        data = httptools.downloadpage('https://embedy.cc/video.get/', post={'video':vid}, headers={'Referer': page_url}).data
        try:
            data_json = jsontools.load(data)
            for n in data_json['response']:
                for f in data_json['response'][n]['files']:
                    video_urls.append([f, data_json['response'][n]['files'][f]])
        except:
            pass

    if len(video_urls) == 0:
        data = httptools.downloadpage(page_url).data
        url = scrapertools.find_single_match(data, '<iframe.*? src="([^"]+)')

        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo' and servidor != 'embedy': 
            url = servertools.normalize_url(servidor, url)
            server_module = __import__('servers.%s' % servidor, None, None, ["servers.%s" % servidor])
            return server_module.get_video_url(url)

    return video_urls
