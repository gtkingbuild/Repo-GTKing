# -*- coding: utf-8 -*-

import base64


from core import httptools, scrapertools
from platformcode import config, logger, platformtools


color_exec  = config.get_setting('notification_exec_color', default='cyan')


def z_xroxy(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.xroxy.com/proxylist.htm'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, "'View this Proxy details'>(.*?)<.*?Select proxies with port number.*?>(.*?)</a>")

    for prox, port in enlaces:
        prox = prox.strip()
        port = port.strip()

        if not prox or not port: continue

        proxies.append(prox + ':' + port)

    return proxies


def z_proxy_daily(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxy-daily.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(resp.data, 'Free Http/Https Proxy List.*?freeProxyStyle">(.*?)</div>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    return proxies


def z_proxy_list_org(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxy-list.org/spanish/index.php'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '<li class="proxy"><script.*?' + "'(.*?)'")

    for prox in enlaces:
        prox = base64.b64decode(prox)

        if "b'" in str(prox): prox = scrapertools.find_single_match(str(prox), "b'(.*?)'")

        if prox: proxies.append(prox)

    return proxies


def z_proxyhub(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.proxyhub.me/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    if not resp.data: resp = httptools.downloadpage(url_provider, raise_weberror=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '<tr><td>(.*?)</td><td>(.*?)</td>')

    for prox, port in enlaces:
        if not prox or not port: continue

        if prox: proxies.append(prox + ':' + port)

    return proxies


def z_proxyranker(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxyranker.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '<td>(.*?)</td>.*?<span title="Proxy port">(.*?)</span>.*?</tr>')

    for prox, port in enlaces:
        if not prox or not port: continue

        if prox: proxies.append(prox + ':' + port)

    return proxies


def z_echolink(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'http://www.echolink.org/proxylist.jsp'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '<tr class="normal-row">.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>')

    for prox, port in enlaces:
        prox = prox.replace('&nbsp;', '').strip()
        port = port.replace('&nbsp;', '').strip()

        if not prox or not port: continue

        proxies.append(prox + ':' + port)

    return proxies


def z_free_proxy_list_anon(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://free-proxy-list.net/anonymous-proxy.html'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    block = scrapertools.find_single_match(resp.data, 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue

        proxies.append(prox)

    return proxies


def z_free_proxy_list_uk(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://free-proxy-list.net/uk-proxy.html'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    block = scrapertools.find_single_match(resp.data, 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue

        proxies.append(prox)

    return proxies


def z_squidproxyserver(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://squidproxyserver.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '<tr><td>(.*?)</td><td>(.*?)</td>')

    for prox, port in enlaces:
        if not prox or not port: continue

        proxies.append(prox + ':' + port)

    return proxies


def z_socks(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.socks-proxy.net/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(resp.data, 'Updated at(.*?)</div>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox:
            if '-' in prox: continue
            elif not ':' in prox: continue

        proxies.append(prox)

    return proxies


def z_opsxcq(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    return proxies


def z_free_proxy_list_com(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://free-proxy-list.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '<td class=""><a href=.*?title="(.*?)"')

    for prox in enlaces:
        proxies.append(prox)

    return proxies


def z_coderduck(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    el_provider = '[B][COLOR %s] Pdfcoffee[/B][/COLOR]' % color_exec
    platformtools.dialog_notification('Z-Coderduck', 'Vía' + el_provider)

    url_provider = 'https://pdfcoffee.com/proxy-listtxt-4-pdf-free.html'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(resp.data, '<p class="d-block text-justify">(.*?)</p>')

    if block:
        block = block + ' '
        enlaces = scrapertools.find_multiple_matches(block, '(.*?) ')

        for prox in enlaces:
            proxies.append(prox)

        if proxies: return proxies

    # ~ 13/9/2022 no devuelve proxies
    url_provider = 'https://www.coderduck.com/free-proxy-list'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(resp.data, '<tr>.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>')

    for prox, port in enlaces:
        if not prox or not port: continue

        prox = prox.replace("' + '", '').strip()

        if prox: proxies.append(prox + ':' + port)

    return proxies

