# -*- coding: utf-8 -*-

import re, base64

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    # ~ packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    packed = scrapertools.find_single_match(data, "eval\((function\(p,a,c,k.*?)\)\s*</script>")
    if not packed: return video_urls
    data = jsunpack.unpack(packed)

    # ~ sources:[{"label":"HD","type":"video/mp4","file":"https://d-8.files.im:182/files/6/viwv5zocvgfbcu/video.mp4"}]
    if 'sources:' in data:
        bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')

        matches = scrapertools.find_multiple_matches(bloque, '\{(.*?)\}')
        for vid in matches:
            url = scrapertools.find_single_match(vid, '"file":\s*"([^"]+)')
            lbl = scrapertools.find_single_match(vid, '"label":\s*"([^"]+)')
            if not lbl: lbl = url[-4:]
            video_urls.append([lbl, url+'|Referer=https://files.im/'])

        if len(video_urls) > 0: return video_urls

    matches1 = scrapertools.find_multiple_matches(data, '(\w+|\$)=~\[\];((?:\w+|\$)=\{.*?\)\(\)\)\(\);)')
    for js in matches1:
        nom = js[0]
        if nom == '$': 
            nom = 'xxx'
            jsaux = js[1].replace('$.', 'xxx.') # pq dóna problemes fer eval en python d'una variable amb nom $
        else:
            jsaux = js[1]

        codi = scrapertools.find_single_match(jsaux, "%s\.\$\(%s\.\$\((.*?)\)\(\)\)\(\);" % (nom, nom))

        codi = codi.replace(nom, 'estructura')
        codi = codi.replace('(![]+"")', '"false"')
        codi = codi.replace('(!![]+"")', '"true"')
        codi = re.sub('\.([$_]+)', lambda m: '["'+m.group(1)+'"]', codi) # Canviar estructura.___ per estructura["___"]
        codi = re.sub('\[(estructura\["[$_]+"\])\]', lambda m: '[int('+m.group(1)+')]', codi) # Els índexs com enters. Ex: (!""+"")[fa46i.__$] => "false"[int(...)]

        codi = codi.replace('\\\\', '\\')

        estructura = {}
        valors = ["0","f","1","a","2","b","d","3","e","4","5","c","6","7","8","9",]
        matches = scrapertools.find_multiple_matches(js[1], "([_\$]+):")
        for i, val in enumerate(matches):
            # ~ logger.info('i= %s  val= %s' % (i, val))
            if val not in estructura: estructura[val] = valors[i]

        estructura["$_"] = "constructor"
        estructura["_$"] = "o"
        estructura["$$"] = "return"
        estructura["__"] = "t"
        estructura["_"] = "u"

        try:
            contingut = eval(codi)
            xurro = eval(contingut.replace('return"', '"'))
        except:
            xurro = ''

        # ~ sources: [{"label":"HD", "type": "video/mp4", "file": "https://d-8.files.im:182/files/7/ttygjbgkikr9oq/video.mp4"}]

        bloque = scrapertools.find_single_match(xurro, 'sources:\s*\[(.*?)\]')

        matches = scrapertools.find_multiple_matches(bloque, '\{(.*?)\}')
        for vid in matches:
            url = scrapertools.find_single_match(vid, '"file":\s*"([^"]+)')
            lbl = scrapertools.find_single_match(vid, '"label":\s*"([^"]+)')
            if not lbl: lbl = url[-4:]
            video_urls.append([lbl, url+'|Referer=https://files.im/'])

    return video_urls
