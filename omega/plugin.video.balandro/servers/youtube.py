# s-*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    PY3 = False

    import urllib
    import urlparse
else:
    PY3 = True

    import urllib.parse as urllib
    import urllib.parse as urlparse


import xbmc, re

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, servertools

from core import jsontools as json


web_yt = 'https://www.youtube.com'

# ~ https://tyrrrz.me/blog/reverse-engineering-youtube


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    headers = {}

    headers['Cookie'] = 'domain=.youtube.com; name=c_locale; value=0; expires=1'

    ini_page_url = page_url

    if not page_url.startswith("http"): page_url = web_yt + '/watch?v=%s' % page_url

    page_url = servertools.normalize_url('youtube', page_url)

    data = httptools.downloadpage(page_url, headers = headers).data

    if "File was deleted" in data or 'El vídeo no está disponible' in data:
        return 'Archivo inexistente ó eliminado'

    video_id = scrapertools.find_single_match(page_url, '(?:v=|embed/)([A-z0-9_-]{11})')

    video_urls = extract_videos(video_id, ini_page_url)

    return video_urls


def remove_additional_ending_delimiter(data):
    pos = data.find("};")
    if pos != -1:
        data = data[:pos + 1]
    return data

def normalize_url(url):
    if url[0:2] == "//":
        url = "https:" + url
    return url


def extract_flashvars(data):
    assets = 0
    flashvars = {}
    found = False

    if 'ytInitialPlayerResponse' in data:
        aux = scrapertools.find_single_match(data, 'var ytInitialPlayerResponse = (\{.*?\});')
        if aux: flashvars['player_response'] = aux
    else:
        for line in data.split("\n"):
            if line.strip().find(";ytplayer.config = ") > 0:
                found = True
                p1 = line.find(";ytplayer.config = ") + len(";ytplayer.config = ") - 1
                p2 = line.rfind(";")
                if p1 <= 0 or p2 <= 0: continue
                data = line[p1 + 1:p2]
                break

        data = remove_additional_ending_delimiter(data)

        if found:
            data = json.load(data)
            if assets: flashvars = data["assets"]
            else: flashvars = data["args"]

        for k in ["html", "css", "js"]:
            if k in flashvars:
                flashvars[k] = normalize_url(flashvars[k])

    return flashvars


def label_from_itag(itag):
    fmt_value = {
        5: "240p h263 flv",
        6: "240p h263 flv",
        18: "360p h264 mp4",
        22: "720p h264 mp4",
        26: "???",
        33: "???",
        34: "360p h264 flv",
        35: "480p h264 flv",
        36: "3gpp",
        37: "1080p h264 mp4",
        38: "4K h264 mp4",
        43: "360p vp8 webm",
        44: "480p vp8 webm",
        45: "720p vp8 webm",
        46: "1080p vp8 webm",
        59: "480p h264 mp4",
        78: "480p h264 mp4",
        82: "360p h264 3D",
        83: "480p h264 3D",
        84: "720p h264 3D",
        85: "1080p h264 3D",
        100: "360p vp8 3D",
        101: "480p vp8 3D",
        102: "720p vp8 3D"
    }

    if not itag or itag not in fmt_value: return None
    return fmt_value[itag]


js_signature = None
js_signature_checked = False

def obtener_js_signature(youtube_page_data):
    global js_signature, js_signature_checked

    js_signature_checked = True
    urljs = scrapertools.find_single_match(youtube_page_data, '"assets":.*?"js":\s*"([^"]+)"').replace("\\", "")
    if not urljs: urljs = scrapertools.find_single_match(youtube_page_data, '"([^"]+base\.js)"').replace("\\", "")
    if urljs:
        if not re.search(r'https?://', urljs): urljs = urlparse.urljoin(web_yt, urljs)
        data_js = httptools.downloadpage(urljs).data

        funcname = scrapertools.find_single_match(data_js, '\.sig\|\|([A-z0-9$]+)\(')
        if not funcname: funcname = scrapertools.find_single_match(data_js, '["\']signature["\']\s*,\s*([A-z0-9$]+)\(')
        if not funcname: funcname = scrapertools.find_single_match(data_js, '([A-z0-9$]+)\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\);\w+\.')
        if not funcname:
            # No se puede decodificar este vídeo
            logger.info("check-youtube: %s" % 'Youtube signature not found')
            return

        from lib.jsinterpreter import JSInterpreter
        jsi = JSInterpreter(data_js)
        js_signature = jsi.extract_function(funcname)
    else:
        logger.info('Check-Youtube no detectada js_signature')


def extract_from_player_response(params, youtube_page_data=''):
    video_urls = []

    try:
        pr = json.load(params['player_response'])

        if not 'streamingData' in pr: raise()
        if not 'formats' in pr['streamingData']: raise()

        for vid in sorted(pr['streamingData']['formats'], key=lambda x: (x['height'], x['mimeType'])):
            if not 'url' in vid and not 'cipher' in vid and not 'signatureCipher' in vid: continue

            if not 'url' in vid:
                if not youtube_page_data: continue

                aux = vid['cipher'] if 'cipher' in vid else vid['signatureCipher']
                v_url = urllib.unquote(scrapertools.find_single_match(aux, 'url=([^&]+)'))
                v_sig = urllib.unquote(scrapertools.find_single_match(aux, 's=([^&]+)'))

                if not js_signature and not js_signature_checked: obtener_js_signature(youtube_page_data)

                if not js_signature: continue

                vid['url'] = v_url + '&sig=' + urllib.quote(js_signature([v_sig]), safe='')

            lbl = ''
            if 'itag' in vid: lbl = label_from_itag(vid['itag'])
            if not lbl and 'qualityLabel' in vid: lbl = vid['qualityLabel']
            if not lbl: lbl = '?'

            video_urls.append([lbl, vid['url']])
    except:
        pass

    return video_urls


def import_libs(module):
    import os, xbmcaddon
    from core import filetools

    path = os.path.join(xbmcaddon.Addon(module).getAddonInfo("path"))
    addon_xml = filetools.read(filetools.join(path, "addon.xml"))

    if addon_xml:
        require_addons = scrapertools.find_multiple_matches(addon_xml, '(<import addon="[^"]+"[^\/]+\/>)')
        require_addons = list(filter(lambda x: not 'xbmc.python' in x and 'optional="true"' not in x, require_addons))

        for addon in require_addons:
            addon = scrapertools.find_single_match(addon, 'import addon="([^"]+)"')
            if xbmc.getCondVisibility('System.HasAddon("%s")' % (addon)):
                import_libs(addon)
            else:
                xbmc.executebuiltin('InstallAddon(%s)' % (addon))
                import_libs(addon)

        lib_path = scrapertools.find_multiple_matches(addon_xml, 'library="([^"]+)"')
        for lib in list(filter(lambda x: not '.py' in x, lib_path)):
            sys.path.append(os.path.join(path, lib))


def extract_videos(video_id, ini_page_url):
    youtube_page_data = ''

    url =  web_yt + '/get_video_info?c=TVHTML5&cver=7.20201028&html5=1&video_id=%s&eurl=https://youtube.googleapis.com/v/%s&ssl_stream=1' % (video_id, video_id)

    data = httptools.downloadpage(url).data

    video_urls = []

    if not data or "<h1>We're sorry" in data:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")') and xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
            color_exec = config.get_setting('notification_exec_color', default='cyan')
            el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
            el_srv += ('ResolveUrl / YouTube[/B][/COLOR]')

            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    video_urls.append(['mp4', resuelto])
                    return video_urls

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
            except:
                import traceback
                logger.error(traceback.format_exc())
                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        elif xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
            try:
                import_libs('plugin.video.youtube')

                import youtube_resolver
                page_url = ini_page_url

                items = youtube_resolver.resolve(ini_page_url)

                for item in list(filter(lambda x: not 'opus' in x.get('title') and not 'webm' in x.get('title'), items)):
                    if '/manifest.googlevideo.com/' in item['url']: continue
                    elif "'dash/audio': True" in str(item): continue

                    video_urls.append([item['title'], item['url']])

            except:
                # YouTubeExceptions: Sign in to confirm your age or private video
                import traceback
                logger.error(traceback.format_exc())

        else:
            color_exec = config.get_setting('notification_exec_color', default='cyan')
            el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
            el_srv += ('ResolveUrl / YouTube[/B][/COLOR]')
            platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        return video_urls


    if PY3 and isinstance(data, bytes):
        data = data.decode('utf-8')

    params = dict(urlparse.parse_qsl(data))

    if params.get('hlsvp'):
        video_urls.append(["LIVE .m3u8", params['hlsvp']])
        return video_urls

    if params.get('player_response'):
        video_urls = extract_from_player_response(params)
        if len(video_urls) > 0: return video_urls

    if params.get('dashmpd') and platformtools.is_mpd_enabled():
        if params.get('use_cipher_signature', '') != 'True': video_urls.append(['mpd HD', params['dashmpd'], 0, '', True])

    youtube_page_data = httptools.downloadpage(web_yt + '/watch?v=%s' % video_id).data

    params = extract_flashvars(youtube_page_data)

    if params.get('player_response'):
        video_urls = extract_from_player_response(params, youtube_page_data)
        if len(video_urls) > 0: return video_urls

    if not params.get('url_encoded_fmt_stream_map'):
        params = dict(urlparse.parse_qsl(data))

    if params.get('url_encoded_fmt_stream_map'):
        data_flashvars = params["url_encoded_fmt_stream_map"].split(",")
        for url_desc in data_flashvars:
            url_desc_map = dict(urlparse.parse_qsl(url_desc))

            if not url_desc_map.get("url") and not url_desc_map.get("stream"): continue
            try:
                lbl = label_from_itag(int(url_desc_map["itag"]))
                if not lbl: continue

                if url_desc_map.get("url"): url = urllib.unquote(url_desc_map["url"])
                elif url_desc_map.get("conn") and url_desc_map.get("stream"):
                    url = urllib.unquote(url_desc_map["conn"])
                    if url.rfind("/") < len(url) - 1: url += "/"
                    url += urllib.unquote(url_desc_map["stream"])
                elif url_desc_map.get("stream") and not url_desc_map.get("conn"): url = urllib.unquote(url_desc_map["stream"])

                if url_desc_map.get("sig"): url += "&signature=" + url_desc_map["sig"]
                elif url_desc_map.get("s"):
                    sig = url_desc_map["s"]

                    if not js_signature and not js_signature_checked: obtener_js_signature(youtube_page_data)

                    if not js_signature: continue

                    url += "&sig=" + urllib.quote(js_signature([sig]), safe='')

                url = url.replace(",", "%2C")
                video_urls.append([lbl, url])
            except:
                import traceback
                logger.info(traceback.format_exc())

        video_urls.reverse()

    if not video_urls:
        if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")') and xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
            color_exec = config.get_setting('notification_exec_color', default='cyan')
            el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
            el_srv += ('ResolveUrl / YouTube[/B][/COLOR]')

            try:
                import_libs('script.module.resolveurl')

                import resolveurl
                page_url = ini_page_url
                resuelto = resolveurl.resolve(page_url)

                if resuelto:
                    video_urls.append(['mp4', resuelto])
                    return video_urls

                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)
            except:
                import traceback
                logger.error(traceback.format_exc())
                platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

        elif xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
            try:
                import_libs('plugin.video.youtube')

                import youtube_resolver
                page_url = ini_page_url

                items = youtube_resolver.resolve(page_url)

                for item in list(filter(lambda x: not 'opus' in x.get('title') and not 'webm' in x.get('title'), items)):
                    if '/manifest.googlevideo.com/' in item['url']: continue
                    elif "'dash/audio': True" in str(item): continue

                    video_urls.append([item['title'], item['url']])

            except:
                # YouTubeExceptions: Sign in to confirm your age or private video
                import traceback
                logger.error(traceback.format_exc())

        else:
            color_exec = config.get_setting('notification_exec_color', default='cyan')
            el_srv = ('Sin respuesta en [B][COLOR %s]') % color_exec
            el_srv += ('ResolveUrl / YouTube[/B][/COLOR]')
            platformtools.dialog_notification(config.__addon_name, el_srv, time=3000)

    return video_urls
