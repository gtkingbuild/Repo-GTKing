# -*- coding: utf-8 -*-

from platformcode import logger
from core import httptools, scrapertools

from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "<b>File not found, sorry!</b" in data:
        return "El fichero no existe o ha sido borrado"

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
