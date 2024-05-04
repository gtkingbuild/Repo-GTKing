# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('supervideo.tv/emb.html?','supervideo.tv/e/')

    video_urls = get_video_url_embed(page_url, url_referer)
    if not type(video_urls) == list: return video_urls

    if len(video_urls) == 0:
        video_urls = get_video_url_download(page_url, url_referer)
        
    return video_urls


def get_video_url_embed(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if 'supervideo.tv/e/' not in page_url:
        page_url = page_url.replace('supervideo.tv/','supervideo.tv/e/')

    data = httptools.downloadpage(page_url).data

    if '<title>404 Not Found</title>' in data:
        return 'Archivo inexistente ó eliminado'

    packed = scrapertools.find_multiple_matches(data, "(?s)eval(.*?)\s*</script>")
    for pack in packed:
        try:
            data = jsunpack.unpack(pack)
        except:
            data = ''

        if 'sources:[' in data: break

    bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')

    matches = scrapertools.find_multiple_matches(bloque, '\{(.*?)\}')

    for vid in matches:
        url = scrapertools.find_single_match(vid, 'file:"([^"]+)')
        if not url: continue
        lbl = scrapertools.find_single_match(vid, 'label:"([^"]+)')
        if not lbl: lbl = url[-4:]
        video_urls.append([lbl, url+'|Referer=https://supervideo.tv/'])

    try:
        video_urls = sorted(video_urls, key=lambda x: 0 if x[0] == 'm3u8' else int(x[0].replace('p','')) )
    except:
        pass

    return video_urls


def get_video_url_download(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if 'supervideo.tv/e/' in page_url:
        page_url = page_url.replace('supervideo.tv/e/','supervideo.tv/')

    data = httptools.downloadpage(page_url).data

    if '<title>404 Not Found</title>' in data:
        return 'Archivo inexistente ó eliminado'

    if 'download_video(' not in data:
        post = {
            'op': scrapertools.find_single_match(data, '<input type="hidden" name="op" value="([^"]+)'),
            'usr_login': scrapertools.find_single_match(data, '<input type="hidden" name="usr_login" value="([^"]+)'),
            'id': scrapertools.find_single_match(data, '<input type="hidden" name="id" value="([^"]+)'),
            'fname': scrapertools.find_single_match(data, '<input type="hidden" name="fname" value="([^"]+)'),
            'referer': scrapertools.find_single_match(data, '<input type="hidden" name="referer" value="([^"]+)'),
            'hash': scrapertools.find_single_match(data, '<input type="hidden" name="hash" value="([^"]+)'),
        }

        if post['id'] and post['hash']:
            data = httptools.downloadpage(page_url, post=post).data

    matches = scrapertools.find_multiple_matches(data, "download_video\('([^']+)','([^']+)','([^']+)'\)\">([^<]+)</a></td><td>([^<]+)")

    if not matches:
        matches = scrapertools.find_multiple_matches(data, "download_video\('([^']+)','([^']+)','([^']+)'\)\">.*? class=\"downloadbox__quality\">([^<]+)</b><span class=\"downloadbox__size\">([^<]+)")

    for a, b, c, titulo, desc in matches:
        if b == 'l' and len(video_urls) > 1: continue # descartar low si ya hay original y normal
        
        data = httptools.downloadpage('https://supervideo.tv/dl?op=download_orig&id=%s&mode=%s&hash=%s' % (a, b, c)).data

        url = scrapertools.find_single_match(data, ' href="([^"]+)">Direct Download Link</a>')
        if not url: url = scrapertools.find_single_match(data, 'btn_direct-download" href="([^"]+)')

        if not url:
            post = {'op': 'download_orig', 'id': a, 'mode': b, 'hash': c}
            data = httptools.downloadpage('https://supervideo.tv/dl', post=post).data
            
            url = scrapertools.find_single_match(data, '<a href="([^"]+)">Direct Download Link</a>')
            if not url: url = scrapertools.find_single_match(data, 'btn_direct-download" href="([^"]+)')

        if url:
            video_urls.append(["%s - %s" % (titulo.replace(' quality', '').strip(), desc.strip()), url])

    video_urls.reverse()
    return video_urls
