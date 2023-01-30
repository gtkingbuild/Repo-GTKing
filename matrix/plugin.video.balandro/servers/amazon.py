# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if data.code == 404:
        return 'El archivo no existe o ha sido borrado'

    if 'ShareId does not exists' in data:
        return 'El archivo no existe o ha sido borrado'

    jdata = jsontools.load(data)
    folderid = jdata['nodeInfo']['id']
    shareId = jdata['shareId']

    url = "https://www.amazon.com/drive/v1/nodes/%s/children?resourceVersion=V2&ContentType=JSON&limit=200&asset=ALL&tempLink=true&shareId=%s" % (folderid, shareId)

    serversdata = httptools.downloadpage(url).data

    url = jsontools.load(serversdata)['data'][0]['tempLink']
    if url:
        video_urls.append(['mp4', url])

    return video_urls
