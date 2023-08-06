# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_headers(url_referer=''):
    h = {}

    # ~ h['Referer'] = url_referer if url_referer else 'https://gamovideo.net/'
    # ~ h['Referer'] = 'https://gamovideo.net/'

    h['Cookie'] = 'sugamun=1; invn=1; pfm=1'

    ff_ver = []
    # ~ ff_ver = [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84]  # (Windows NT 10.0)
    # ~ ff_ver = [78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, ]  # (Windows NT 10.0; Win64; x64; rv:%s.0)
    # ~ ff_ver = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84]  # (Windows NT 10.0) AppleWebKit/537.36
    # ~ ff_ver = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84]  # (Windows NT 6.1)
    # ~ ff_ver = [82, 83, 84]                                              # (X11; Ubuntu; Linux x86_64;
    # ~ ff_ver = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84]  # (iPad; CPU OS 12_2 like Mac OS X) (solo mp4, sin rtmp)

    if ff_ver:
        import random
        ff_rnd = str(random.choice(ff_ver))

        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0) rv:%s.0; Firefox/%s.0' % (ff_rnd, ff_rnd)
        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:%s.0) Gecko/20100101 Firefox/%s.0' % (ff_rnd, ff_rnd)
        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s.0' % ff_rnd
        # ~ h['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s.0' % ff_rnd
        # ~ h['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:%s.0) Gecko/20100101 Firefox/%s.0' % (ff_rnd, ff_rnd)
        # ~ h['User-Agent'] = 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s.0' % ff_rnd

    return h


def normalizar_url(page_url):
    page_url = page_url.replace('%0D', '')

    if 'embed' in page_url:
        vid = scrapertools.find_single_match(page_url, "gamovideo.com/(?:embed-|)([a-z0-9]+)")
        if not vid: vid = scrapertools.find_single_match(page_url, "gamovideo.net/(?:embed-|)([a-z0-9]+)")

        if vid: return "https://gamovideo.net/" + vid

    return page_url


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = normalizar_url(page_url)

    CUSTOM_HEADERS = get_headers(url_referer)

    data = httptools.downloadpage(page_url, headers=CUSTOM_HEADERS).data

    packer = scrapertools.find_single_match(data, "<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
    if packer: data = jsunpack.unpack(packer)

    mp4 = scrapertools.find_single_match(data, ',\{\s*file\s*:\s*"([^"]+)')

    if mp4:
        # ~ resp = httptools.downloadpage(mp4, follow_redirects=False, only_headers=True, headers=CUSTOM_HEADERS)
        # ~ if int(resp.headers['content-length']) < 50000000: # Menos de 50 mb es que no debe ser válido
            # ~ return 'El vídeo no es válido'

        rtmp = scrapertools.find_single_match(data, '\{\s*file\s*:\s*"(rtmp:[^"]+)')
        if rtmp:
            playpath = scrapertools.find_single_match(rtmp, 'mp4:.*$')
            rtmp = rtmp.split(playpath)[0] + ' playpath=' + playpath + ' swfUrl=https://gamovideo.net/player61/jwplayer.flash.swf'
            video_urls.append(["rtmp", rtmp])

        video_urls.append(["mp4", mp4])

    if not video_urls:
        data = httptools.downloadpage('https://gamovideo.net/').data

        work = scrapertools.find_single_match(data, '<div class="main_box_left">.*?<img src="(.*?)".*?</div>')

        if '/wp.png' in work: return '[COLOR cyan]Servidor en mantenimiento[/COLOR]'


    return video_urls
