# -*- coding: utf-8 -*-

import os

from core import httptools, scrapertools, jsontools
from platformcode import config, logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    vid = scrapertools.find_single_match(page_url, 'id=([A-z0-9]+)')
    if not vid: return video_urls

    data = httptools.downloadpage('https://www.zembed.to/vl/' + vid).data

    try:
        cache_path = os.path.join(config.get_data_path(), 'cache')
        if not os.path.exists(cache_path): os.makedirs(cache_path)

        data_json = jsontools.load(data)

        for q in ["360p", "480p", "720p", "1080p", "2048p"]:
            if q not in data_json: continue
            txt = generar_m3u8(data_json[q])

            file_local = os.path.join(cache_path, 'temp-%s.m3u8' % q)
            with open(file_local, 'wb') as f: f.write(txt); f.close()

            video_urls.append(['m3u8 '+q, file_local])
    except:
        pass

    return video_urls


def generar_m3u8(e):
    txt = "#EXTM3U\n"
    txt += "#EXT-X-VERSION:5\n"
    txt += "#EXT-X-TARGETDURATION:%s\n" % e['td']
    txt += "#EXT-X-MEDIA-SEQUENCE:0\n"

    for l in range(len(e['data'][0])):
        txt += "#EXTINF:%s\n" % e['data'][0][l]
        txt += "#EXT-X-BYTERANGE:%s\n" % e['data'][1][l]

        r = e['data'][1][l].split("@")
        txt += "https://www.zembed.to/drive/hls/" + e['md5'] + "/" + e['md5'] + str(l) + ".html?ch=" + e['md5'] + "-chunk-" + e['data'][2][l] + ".txt&s=" + r[1] + "&l=" + r[0] + "\n"

    txt += "#EXT-X-ENDLIST\n"
    return txt
