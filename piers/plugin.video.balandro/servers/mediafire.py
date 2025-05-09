# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "Invalid or Deleted File" in data or "Well, looks like we" in data:
        return "Archivo inexistente ó eliminado"
    elif "File Removed for Violation" in data:
        return "Archivo eliminado por infracción"

    matches = scrapertools.find_multiple_matches(data, "DownloadButtonAd-startDownload gbtnSecondary.*?href='([^']+)'")
    if not matches: matches = scrapertools.find_multiple_matches(data, 'Download file.*?href="([^"]+)"')

    if not matches:
         match = scrapertools.find_single_match(str(data), 'window.location.href =' + ".*?'(.*?)'")

         if match:
             if '.rar' in match or '.zip' in match:
                 return "El archivo está en formato comprimido"

             video_urls = [[match[-4:], match]]
             return video_urls

    if len(matches) > 0:
        video_urls.append([matches[0][-4:], matches[0]])

    return video_urls
