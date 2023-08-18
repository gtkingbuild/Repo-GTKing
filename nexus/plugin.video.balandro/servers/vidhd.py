# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if 'File Not Found' in data or 'File is no longer available' in data:
        return 'El archivo ha sido eliminado o no existe'

    if 'sources: [{file:"' in str(data):
        new_data = data
    else:
        keys = ['op',  'id',  'fname', 'hash']
        post = {'usr_login': '', 'referer': '', 'imhuman': 'Proceed to video'}

        for k in keys:
            post[k] = scrapertools.find_single_match(data, 'input type="hidden" name="%s" value="([^"]+)"' % k)

        new_data = httptools.downloadpage(page_url.replace('.html', ''), post=post, headers={'Referer': page_url}).data

    vid_info = scrapertools.find_multiple_matches(new_data, r'{(file:.*?)}')
    subtitulo = scrapertools.find_single_match(new_data, r'tracks:\s*\[{file:"([^"]+)"')

    for info in vid_info:
        url = scrapertools.find_single_match(info, r'file:"([^"]+)"')
        label = scrapertools.find_single_match(info, r'label:"([^"]+)"')

        if url == subtitulo: continue

        extension = scrapertools.get_filename_from_url(url)[-4:]

        video_urls.append([extension, url])

    return video_urls
