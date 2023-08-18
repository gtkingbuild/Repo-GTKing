# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    PY3 = True

    import urllib3

else:
    PY3 = False

    import urllib2


import time, random

from platformcode import logger, config, platformtools
from core import scrapertools


import ssl
ssl._create_default_https_context = ssl._create_unverified_context


try:
    import requests
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    existe_script = True
except:
    existe_script = False


color_alert = config.get_setting('notification_alert_color', default='red')


# ~ useragent = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
useragent = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.171 Safari/537.36"


ver_stable_chrome = config.get_setting("ver_stable_chrome", default=True)
if ver_stable_chrome:
    cfg_last_ver_chrome = config.get_setting('chrome_last_version', default='')
    if not cfg_last_ver_chrome == '':
        chrome_version = cfg_last_ver_chrome
        useragent = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36" % chrome_version


default_headers = dict()
default_headers["User-Agent"] = useragent
default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
default_headers["Accept-Charset"] = "UTF-8"
default_headers["Accept-Encoding"] = "gzip"

headers = default_headers


def read(url, channel):
    logger.info()

    if not existe_script:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Falta script.module.requests[/COLOR][/B]' % color_alert)
        return ''

    if not url: return ''

    # ~ Sin proxies
    if not channel:
        data = read_data(url, headers)

        if not data:
            espera = 3
            platformtools.dialog_notification('Requests', 'Espera requerida de %s segundos' % espera)
            time.sleep(int(espera))

            data = read_data(url, headers)

        return data


    # ~ Con proxies
    proxies = config.get_setting('proxies', channel, default='').replace(' ', '')

    # ~ Si los proxies estan separados por ; orden aleatorio
    if ';' in proxies:
        proxies = proxies.replace(',', ';').split(';')
        random.shuffle(proxies)
    else:
        proxies = proxies.split(',')

    if len(proxies) == 0: proxies = ['']

    source = ''

    if proxies:
         for n, proxy in enumerate(proxies):
             px = {'http': proxy, 'https': proxy}

             source = read_proxy(url, px, headers)

             if source: break

             espera = 5
             platformtools.dialog_notification(channel.capitalize(), 'Espera requerida de %s segundos' % espera)
             time.sleep(int(espera))

             source = read_proxy(url, px, headers)

    return source


def read_proxy(url, px, headers):
    source = ''

    try:
        source = requests.Session()
        source = requests.get(url, headers=headers, proxies=px, verify=False, timeout=30).content
    except:
        source = read_proxy2(url, px, headers)

    if source: 
        if '<title>Please Wait... | Cloudflare</title>' in str(source):
            platformtools.dialog_notification(config.__addon_name, 'Verificando [B][COLOR %s]reCAPTCHA[/COLOR][/B]' % color_alert)
            source = read_proxy2(url, px, headers)

        elif '<title>You are being redirected...</title>' in str(source) or '<title>Just a moment...</title>' in str(source):
            platformtools.dialog_notification(config.__addon_name, 'Verificando [B][COLOR %s]Protection[/COLOR][/B]' % color_alert)
            source = read_proxy2(url, px, headers)

        if '<title>Just a moment...</title>' in str(source):
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
            source = ''

        return source

    new_url = scrapertools.find_single_match(source, 'window.location.href.*?"(.*?)"')

    if new_url:
        try:
           source = requests.Session()
           source = requests.get(new_url, headers=headers, proxies=px, verify=False, timeout=30).content
        except:
           logger.error('[COLOR red]Error read proxy location[/COLOR]')
           source = ''

    return source


def read_proxy2(url, px, headers):
    data = ''

    try:
        if not headers: headers = {'User-Agent': 'Mozilla/5.0'}

        req = requests.request('GET', url, headers=headers, proxies=px)

        resp = scrapertools.find_single_match(str(req), '<Response(.*?)>')
        resp = resp.replace('[', '').replace(']', '').strip()
        if not resp: return data

        if not resp == '200': return data

        if PY3:
            _proxy = scrapertools.find_single_match(str(px), "'http': '(.*?)'")

            if not _proxy: return data

            Proxy = urllib3.ProxyManager("http://" + _proxy)
            r = Proxy.request('GET', url)
            data = r.data.decode('utf-8')

        else:
            _proxy = urllib2.ProxyHandler(px)
            opener = urllib2.build_opener(_proxy)
            urllib2.install_opener(opener)

            sock = urllib2.urlopen(url) 
            htmlSource = sock.read()                            
            sock.close()
            data = htmlSource

    except:
        logger.error('[COLOR red]Error read proxy2[/COLOR]')
        data = ''

    return data 


def read_data(url, headers):
    data = ''

    try:
        data = requests.Session()
        data = requests.get(url, headers=headers, verify=False, timeout=30).content
    except:
        data = read_data2(url, headers)

    if data:
        if '<title>Please Wait... | Cloudflare</title>' in str(data):
            platformtools.dialog_notification(config.__addon_name, 'Verificando [B][COLOR %s]reCAPTCHA[/COLOR][/B]' % color_alert)
            data = read_data2(url, headers)

        elif '<title>You are being redirected...</title>' in str(data) or '<title>Just a moment...</title>' in str(data):
            platformtools.dialog_notification(config.__addon_name, 'Verificando [B][COLOR %s]Protection[/COLOR][/B]' % color_alert)
            data = read_data2(url, headers)

        if '<title>Just a moment...</title>' in str(data):
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
            data = ''

        return data

    new_url = scrapertools.find_single_match(data, 'window.location.href.*?"(.*?)"')

    if new_url:
        try:
           data = requests.Session()
           data = requests.get(new_url, headers=headers, verify=False, timeout=30).content
        except:
           logger.error('[COLOR red]Error read data location[/COLOR]')
           data = ''

    return data


def read_data2(url, headers):
    data = ''

    try:
        if not headers: headers={'User-Agent': 'Mozilla/5.0'}

        req = requests.request('GET', url, headers=headers)

        resp = scrapertools.find_single_match(str(req), '<Response(.*?)>')
        resp = resp.replace('[', '').replace(']', '').strip()
        if not resp: return data

        if not resp == '200': return data

        if PY3:
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            data = r.data.decode('utf-8')
        else:
            sock = urllib2.urlopen(url) 
            htmlSource = sock.read()                            
            sock.close()
            data = htmlSource

    except:
        logger.error('[COLOR red]Error read data2[/COLOR]')
        data = ''

    return data

