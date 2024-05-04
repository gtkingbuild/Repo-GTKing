# -*- coding: utf-8 -*-

import random, re, base64


from core import httptools, scrapertools
from platformcode import config, logger, platformtools


color_exec  = config.get_setting('notification_exec_color', default='cyan')


def plus_proxies(proxies, max_proxies):
    logger.info()

    if config.get_setting('proxies_vias', default=False): tplus = config.get_setting('proxies_tplus')
    else:
        tipos_plus = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]

        tplus = random.choice(tipos_plus)

    proxies_plus = []

    url_provider = ''

    if tplus == 0: url_provider = 'https://openproxy.space/list/http'
    elif tplus == 1: url_provider = 'https://openproxy.space/list/socks4'
    elif tplus == 2: url_provider = 'https://openproxy.space/list/socks5'

    elif tplus == 3: url_provider = 'https://vpnoverview.com/privacy/anonymous-browsing/free-proxy-servers/'

    elif tplus == 4: url_provider = 'https://proxydb.net/?protocol=http'
    elif tplus == 5: url_provider = 'https://proxydb.net/?protocol=https'
    elif tplus == 6: url_provider = 'https://proxydb.net/?protocol=socks4'
    elif tplus == 7: url_provider = 'https://proxydb.net/?protocol=socks5'

    elif tplus == 8: url_provider = 'https://www.netzwelt.de/proxy/index.html'

    elif tplus == 9: url_provider = 'https://www.proxy-list.download/HTTP'
    elif tplus == 10: url_provider = 'https://www.proxy-list.download/HTTPS'
    elif tplus == 11: url_provider = 'https://www.proxy-list.download/SOCKS4'
    elif tplus == 12: url_provider = 'https://www.proxy-list.download/SOCKS5'

    elif tplus == 13: url_provider = 'https://www.freeproxy.world'
    elif tplus == 14: url_provider = 'https://www.freeproxy.world/?type=&anonymity'

    elif tplus == 15: url_provider = 'https://hidemyna.me/en/proxy-list/'

    elif tplus == 16: url_provider = 'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1'

    elif tplus == 17: url_provider = 'https://proxyservers.pro/'

    elif tplus == 18: url_provider = 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'

    elif tplus == 19: url_provider = 'https://www.proxyscan.io/download?type=http'
    elif tplus == 20: url_provider = 'https://www.proxyscan.io/download?type=https'

    elif tplus == 21: url_provider = 'https://api.openproxylist.xyz/http.txt'
    elif tplus == 22: url_provider = 'https://api.openproxylist.xyz/socks4.txt'
    elif tplus == 23: url_provider = 'https://api.openproxylist.xyz/socks5.txt'

    elif tplus == 24: url_provider = 'https://www.proxy-list.download/api/v1/get?type=socks4'
    elif tplus == 25: url_provider = 'https://www.proxy-list.download/api/v1/get?type=socks5'

    elif tplus == 26: url_provider = 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt'

    elif tplus == 27: url_provider = 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt'

    elif tplus == 28: url_provider = 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt'

    elif tplus == 29: url_provider = 'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt'

    elif tplus == 30: url_provider = 'https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt'

    elif tplus == 31: url_provider = 'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt'

    elif tplus == 32: url_provider = 'https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt'

    elif tplus == 33: url_provider = 'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt'

    elif tplus == 34: url_provider = 'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt'

    elif tplus == 35: url_provider = 'https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt'

    elif tplus == 36: url_provider = 'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt'

    elif tplus == 37: url_provider = 'https://lamt3012.wixsite.com/porxy/proxy-list'

    if url_provider:
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    if tplus == 0 or tplus == 1 or tplus == 2:
        el_provider = '[B][COLOR %s] Openproxy[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        block = scrapertools.find_single_match(str(resp.data), 'count:(.*?)active:')

        enlaces = scrapertools.find_multiple_matches(str(block), '"(.*?)"')

        if enlaces:
            for prox in enlaces:
                 proxies_plus.append(prox)

    elif tplus == 3:
        el_provider = '[B][COLOR %s] Vpnoverview[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td><strong>(.*?)</strong></td><td>(.*?)</td>')

        for prox, port in enlaces:
            prox = prox.strip()
            port = port.strip()

            if not prox or not port: continue

            proxies_plus.append(prox + ':' + port)

    elif tplus == 4 or tplus == 5 or tplus == 6 or tplus == 7:
        el_provider = '[B][COLOR %s] Proxydb[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<a href=.*?">(.*?)</a>')

        for prox in enlaces:
            proxies_plus.append(prox)

    elif tplus == 8:
        el_provider = '[B][COLOR %s] Netzwelt[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), 'rel="nofollow">(.*?)</a></td><td>(.*?)</td>')

        for prox, port in enlaces:
            prox = prox.strip()
            port = port.strip()

            if not prox or not port: continue

            proxies_plus.append(prox + ':' + port)

    elif tplus == 9 or tplus == 10 or tplus == 11 or tplus == 12:
        el_provider = '[B][COLOR %s] Proxy-list.download[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        resp.data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', resp.data)

        block = scrapertools.find_single_match(str(resp.data), '<tbody id="tabli"(.*?)</tbody>')

        enlaces = scrapertools.find_multiple_matches(str(block), '<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>')

        for prox, puerto in enlaces:
            if puerto: proxies_plus.append(prox + ':' + puerto)

    elif tplus == 13 or tplus == 14:
        el_provider = '[B][COLOR %s] Freeproxy[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        resp.data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', resp.data)

        if '<td class="show-ip-div">' in str(resp.data): enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td class="show-ip-div">(.*?)</td>.*?<a href=".*?">(.*?)</a>')
        else: enlaces = scrapertools.find_multiple_matches(str(resp.data), '<a href=".*?">(.*?)</a>')

        for prox, puerto in enlaces:
            if puerto: proxies_plus.append(prox + ':' + puerto)

    elif tplus == 15:
        el_provider = '[B][COLOR %s] Hidemyna[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        block = scrapertools.find_single_match(str(resp.data), '<tbody>(.*?)</tbody>')

        enlaces = scrapertools.find_multiple_matches(str(block), '<tr><td>(.*?)</td><td>(.*?)</td>')

        for prox, port in enlaces:
            prox = prox.strip()
            port = port.strip()

            if not prox or not port: continue

            proxies_plus.append(prox + ':' + port)

    elif tplus == 16:
        el_provider = '[B][COLOR %s] Proxyservers[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), 'td><img src=".*?<td>(.*?)</td>.*?<td>(.*?)</td>')

        for prox, port in enlaces:
            prox = prox.strip()
            port = port.strip()

            if not prox or not port: continue

            proxies_plus.append(prox + ':' + port)

    elif tplus == 17:
        el_provider = '[B][COLOR %s] Proxylistplus[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        chash = scrapertools.find_single_match(str(resp.data), "var chash\s*=\s*'([^']+)")

        def decode_puerto(t, e):
            a = []; r = []
            for n in range(0, len(t), 2): a.append(int('0x' + t[n:n+2], 16))
            for n in range(len(e)): r.append(ord(e[n]))
            for n, val in enumerate(a): a[n] = val ^ r[n % len(r)]
            for n, val in enumerate(a): a[n] = chr(val)
            return ''.join(a)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '(\d+\.\d+\.\d+\.\d+)</a>\s*</td>\s*<td><span class="port" data-port="([^"]+)')

        for prox, puerto in enlaces:
            proxies_plus.append(prox + ':' + decode_puerto(puerto, chash))

    elif tplus == 19 or tplus == 20:
        el_provider = '[B][COLOR %s] Proxyscan-D[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        if len(resp.data) > 0:
            if not '<h1>Server Error</h1>':
                enlaces = resp.data.split()

                for prox in enlaces:
                    proxies_plus.append(prox)

    elif tplus == 21 or tplus == 22 or tplus == 23:
        el_provider = '[B][COLOR %s] Openproxylist[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

        for prox in enlaces:
            proxies_plus.append(prox)

    elif tplus == 24 or tplus == 25:
        el_provider = '[B][COLOR %s] Proxy-list.download[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

        for prox in enlaces:
            proxies_plus.append(prox)

    elif tplus == 18 or tplus == 26 or tplus == 27 or tplus == 28 or tplus == 29 or tplus == 30 or tplus == 31 or tplus == 32 or tplus == 33 or tplus == 34 or tplus == 35 or tplus == 36:
        if tplus == 18: el_provider = '[B][COLOR %s] TheSpeedX/PROXY-List[/B][/COLOR]' % color_exec
        elif tplus == 26: el_provider = '[B][COLOR %s] Monosans[/B][/COLOR]' % color_exec
        elif tplus == 27: el_provider = '[B][COLOR %s] Jetkai[/B][/COLOR]' % color_exec
        elif tplus == 28: el_provider = '[B][COLOR %s] Sunny9577[/B][/COLOR]' % color_exec
        elif tplus == 29: el_provider = '[B][COLOR %s] Proxy4parsing[/B][/COLOR]' % color_exec
        elif tplus == 30: el_provider = '[B][COLOR %s] Hendrikbgr[/B][/COLOR]' % color_exec
        elif tplus == 31: el_provider = '[B][COLOR %s] Rdavydov[/B][/COLOR]' % color_exec
        elif tplus == 32: el_provider = '[B][COLOR %s] Aslisk[/B][/COLOR]' % color_exec
        elif tplus == 33: el_provider = '[B][COLOR %s] Rdavydov Socks4[/B][/COLOR]' % color_exec
        elif tplus == 34: el_provider = '[B][COLOR %s] Hookzof[/B][/COLOR]' % color_exec
        elif tplus == 35: el_provider = '[B][COLOR %s] ManuGMG[/B][/COLOR]' % color_exec
        elif tplus == 36: el_provider = '[B][COLOR %s] Rdavydov Socks5[/B][/COLOR]' % color_exec

        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

        for prox in enlaces:
            proxies_plus.append(prox)

    if tplus == 37:
        el_provider = '[B][COLOR %s] Lamt3012[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

        block = scrapertools.find_single_match(str(resp.data), '>DOWNLOAD(.*?)>Country<')

        enlaces = scrapertools.find_multiple_matches(str(block), '(.*?)<')

        if enlaces:
            for prox in enlaces:
                 if not ':' in enlaces: continue

                 proxies_plus.append(prox)

    # ~ si no se obtuvo ninguno
    if not proxies_plus:
        if not tplus == 3:
            url_provider = 'https://vpnoverview.com/privacy/anonymous-browsing/free-proxy-servers/'
            resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

            el_provider = '[B][COLOR %s] Vpnoverview[/B][/COLOR]' % color_exec
            platformtools.dialog_notification('Plus ' + str(tplus), 'Vía' + el_provider)

            enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td><strong>(.*?)</strong></td><td>(.*?)</td>')

            for prox, port in enlaces:
                prox = prox.strip()
                port = port.strip()

                if not prox or not port: continue

                proxies_plus.append(prox + ':' + port)


    if proxies_plus: proxies = proxies + proxies_plus

    return proxies


def z_xroxy(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.xroxy.com/proxylist.htm'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), "'View this Proxy details'>(.*?)<.*?Select proxies with port number.*?>(.*?)</a>")

    if enlaces:
        for prox, port in enlaces:
            prox = prox.strip()
            port = port.strip()

            if not prox or not port: continue

            proxies.append(prox + ':' + port)
    else:
        el_provider = '[B][COLOR %s] Proxylist.to[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Xroxy', 'Vía' + el_provider)

        url_provider = 'https://proxylist.to/'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td class="t_ip">(.*?)</td>.*?<td class="t_port">(.*?)</td>')

        for prox, port in enlaces:
            prox = prox.strip()
            port = port.strip()

            if not prox or not port: continue

            proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_proxy_daily(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxy-daily.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Free Http/Https Proxy List.*?freeProxyStyle">(.*?)</div>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_proxy_list_org(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxy-list.org/spanish/index.php'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<li class="proxy"><script.*?' + "'(.*?)'")

    for prox in enlaces:
        prox = base64.b64decode(prox)

        if "b'" in str(prox): prox = scrapertools.find_single_match(str(prox), "b'(.*?)'")

        if prox: proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_proxyhub(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.proxyhub.me/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr><td>(.*?)</td><td>(.*?)</td>')

    if enlaces:
        for prox, port in enlaces:
            if not prox or not port: continue

            if prox: proxies.append(prox + ':' + port)
    else:
        el_provider = '[B][COLOR %s] TheSpeedX.proxy-list-s4[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Proxyhub', 'Vía' + el_provider)

        url_provider = 'https://github.com/TheSpeedX/PROXY-List/blob/master/socks4.txt'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        block = scrapertools.find_single_match(str(resp.data), '"rawLines":(.*?)"stylingDirectives"')

        enlaces = scrapertools.find_multiple_matches(block, '"(.*?)"')

        for prox in enlaces:
            proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_proxyranker(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxyranker.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td>(.*?)</td>.*?<span title="Proxy port">(.*?)</span>.*?</tr>')

    for prox, port in enlaces:
        if not prox or not port: continue

        if prox: proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_echolink(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.echolink.org/proxylist.jsp'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr class="normal-row">.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>')

    for prox, port in enlaces:
        prox = prox.replace('&nbsp;', '').strip()
        port = port.replace('&nbsp;', '').strip()

        if not prox or not port: continue

        proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_free_proxy_list_anon(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://free-proxy-list.net/anonymous-proxy.html'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue

        proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_free_proxy_list_uk(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://free-proxy-list.net/uk-proxy.html'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue

        proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_github(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_squidproxyserver(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://squidproxyserver.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr><td>(.*?)</td><td>(.*?)</td>')

    for prox, port in enlaces:
        if not prox or not port: continue

        proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_socks(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.socks-proxy.net/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Updated at(.*?)</div>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox:
            if '-' in prox: continue
            elif not ':' in prox: continue

        proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_opsxcq(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_free_proxy_list_com(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://free-proxy-list.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td class=""><a href=.*?title="(.*?)"')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies


def z_coderduck(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    el_provider = '[B][COLOR %s] Pdfcoffee[/B][/COLOR]' % color_exec
    platformtools.dialog_notification('Z-Coderduck', 'Vía' + el_provider)

    url_provider = 'https://pdfcoffee.com/proxy-listtxt-4-pdf-free.html'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), '<p class="d-block text-justify">(.*?)</p>')

    if block:
        block = block + ' '
        enlaces = scrapertools.find_multiple_matches(block, '(.*?) ')

        for prox in enlaces:
            proxies.append(prox)

    else:
        # ~ 13/9/2022 no devuelve proxies
        url_provider = 'https://www.coderduck.com/free-proxy-list'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr>.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>')

        for prox, port in enlaces:
            if not prox or not port: continue

            prox = prox.replace("' + '", '').strip()

            if prox: proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = plus_proxies(proxies, max_proxies)

    return proxies

