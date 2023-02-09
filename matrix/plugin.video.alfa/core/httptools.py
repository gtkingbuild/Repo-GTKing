# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# httptools
# --------------------------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
    import http.cookiejar as cookielib
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido
    import urlparse
    import cookielib

import inspect
import os
import time
import requests
import json
import re
import base64
import ast
import traceback

from core.jsontools import to_utf8
from core import scrapertools
from platformcode import config, logger
from platformcode.logger import WebErrorException
from threading import Lock
from collections import OrderedDict

## Obtiene la versión del addon
__version = config.get_addon_version()
__platform = config.get_system_platform()

cookies_lock = Lock()

cj = cookielib.MozillaCookieJar()
ficherocookies = os.path.join(config.get_data_path(), "cookies.dat")

# Headers por defecto, si no se especifica nada
default_headers = OrderedDict()
# default_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) Chrome/79.0.3945.117"

ver = config.get_setting("chrome_ua_version")
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36" % ver

default_headers["User-Agent"] = ua
#default_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
default_headers["Accept-Charset"] = "UTF-8"
default_headers["Accept-Encoding"] = "gzip"

# Tiempo máximo de espera para downloadpage, si no se especifica nada
HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = config.get_setting('httptools_timeout', default=15)
if HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT == 0: HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = None
    
# Uso aleatorio de User-Agents, si no se especifica nada
HTTPTOOLS_DEFAULT_RANDOM_HEADERS = False

# Se activa desde Test
TEST_ON_AIR = False

# Se activa cuando se actualiza la Videoteca
VIDEOLIBRARY_UPDATE = False

patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?[\w|\-\d]+\.(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+))(?:\/|\?|$)'
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?([\w|\-\d]+\.(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+))(?:\/|\?|$)'

retry_alt_default = True

BLACK_LIST_DOMAINS = ['www.alliance4creativity.com', 'alliance4creativity.com']

SUCCESS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
REDIRECTION_CODES = [300, 301, 302, 303, 304, 307, 308]
PROXY_CODES = [305, 306, 407]
NOT_FOUND_CODES = [400, 404, 406, 409, 410, 421, 423, 451]
CLOUDFLARE_CODES = [429, 503, 403, 401]

# Lista de dominios que necesitan CloudScraper
CF_LIST = list()
CS_stat = False

""" CACHING Cookies (save) and CF list"""
alfa_caching = False
alfa_cookies = ''
alfa_CF_list = []

try:
    import xbmcgui
    window = xbmcgui.Window(10000)  # Home
    alfa_caching = bool(window.getProperty("alfa_caching"))
except:
    alfa_caching = False
    alfa_cookies = ''
    alfa_CF_list = []
    logger.error(traceback.format_exc())

""" Setting SSL TLS version for those webs that require it.  Set 'set_tls' = True in downloadpage call or SET_TLS = True for all webs
    For SSL versions older than "1.1.1", you may use 'set_tls_min' = True in downloadpage call to avoid SSl_TLS set """
try:
    SET_TLS = False
    ssl_version = ''
    ssl_version_min = ''
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        if PY3:
            ssl_high = ssl.PROTOCOL_TLSv1_2
        else:
            ssl_high = ssl.PROTOCOL_TLSv1_1
    except:
        ssl_high = ssl.PROTOCOL_TLS_CLIENT
    
    ssl_ver = str(ssl.OPENSSL_VERSION)
    ssl_ver_list = scrapertools.find_single_match(ssl_ver, '(\d+\.\d+\.\d+)').split('.')
    min_ssl_ver = [1, 1, 1]
    if int(ssl_ver_list[0]) > int(min_ssl_ver[0]):
        ssl_version = ssl_version_min = ssl_high
    elif len(ssl_ver_list) >= 3:
        for i, ver in enumerate(ssl_ver_list):
            if int(ver) < min_ssl_ver[i]:
                ssl_version = ssl.PROTOCOL_TLSv1_1
                break
        else:
            ssl_version = ssl_version_min = ssl_high
    else:
        ssl_version = ssl.PROTOCOL_TLSv1_1
    if not PY3 and __platform not in ['android', 'atv2', 'windows', 'xbox']:
        ssl_version = ''

    class TLSHttpAdapter(requests.adapters.HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False):
            self.poolmanager = requests.packages.urllib3.poolmanager.PoolManager(num_pools=connections,
                                                                                 maxsize=maxsize,
                                                                                 block=block,
                                                                                 assert_hostname=False,
                                                                                 ssl_version=ssl_version)
except:
    ssl_version = ''
    logger.error(traceback.format_exc())


def get_user_agent(quoted=False):
    # Devuelve el user agent global para ser utilizado cuando es necesario para la url.
    
    resp = default_headers["User-Agent"]
    if quoted:
        resp = urllib.quote(default_headers["User-Agent"])
    
    return resp


def get_cookie(url, name, follow_redirects=False):
    if follow_redirects:
        try:
            headers = requests.head(url, headers=default_headers).headers
            url = headers['location']
        except Exception:
            pass
        
    domain = obtain_domain(url, sub=True, point=True)

    for cookie in cj:
        if cookie.name == name and domain in cookie.domain:
            return cookie.value
    return False


def get_url_headers(url, forced=False, dom=False):

    domain = urlparse.urlparse(url)[1]
    sub_dom = scrapertools.find_single_match(domain, '\.(.*?\.\w+)')
    if sub_dom and not 'google' in url:
        domain = sub_dom
    if dom:
        domain = dom
    domain_cookies = cj._cookies.get("." + domain, {}).get("/", {})
    domain_cookies.update(cj._cookies.get("www." + domain, {}).get("/", {}))

    if ("|" in url or not "cf_clearance" in domain_cookies) and not forced:
        return url

    headers = dict()
    cf_ua = config.get_setting('cf_assistant_ua', None)
    if cf_ua and cf_ua != 'Default':
        default_headers["User-Agent"] = cf_ua
    headers["User-Agent"] = default_headers["User-Agent"]
    headers["Cookie"] = "; ".join(["%s=%s" % (c.name, c.value) for c in list(domain_cookies.values())])

    return url + "|" + "&".join(["%s=%s" % (h, urllib.quote(headers[h])) for h in headers])


def set_cookies(dict_cookie, clear=True, alfa_s=False):
    """
    Guarda una cookie especifica en cookies.dat
    @param dict_cookie: diccionario de  donde se obtienen los parametros de la cookie
        El dict debe contener:
        name: nombre de la cookie
        value: su valor/contenido
        domain: dominio al que apunta la cookie
        opcional:
        expires: tiempo de vida en segundos, si no se usa agregara 1 dia (86400s)
    @type dict_cookie: dict

    @param clear: True = borra las cookies del dominio, antes de agregar la nueva (necesario para cloudproxy, cp)
                  False = desactivado por defecto, solo actualiza la cookie
    @type clear: bool
    """
    
    #Se le dara a la cookie un dia de vida por defecto
    expires_plus = dict_cookie.get('expires', 86400)
    ts = int(time.time())
    expires = ts + expires_plus

    name = dict_cookie.get('name', '')
    value = dict_cookie.get('value', '')
    domain = dict_cookie.get('domain', '')

    #Borramos las cookies ya existentes en dicho dominio (cp)
    if clear:
        try:
            cj.clear(domain)
        except Exception:
            pass

    ck = cookielib.Cookie(version=0, name=name, value=value, port=None, 
                    port_specified=False, domain=domain, 
                    domain_specified=False, domain_initial_dot=False,
                    path='/', path_specified=True, secure=False, 
                    expires=expires, discard=True, comment=None, comment_url=None, 
                    rest={'HttpOnly': None}, rfc2109=False)
    
    cj.set_cookie(ck)
    save_cookies()


def load_cookies(alfa_s=False):
    global alfa_cookies
    cookies_lock.acquire()
    if os.path.isfile(ficherocookies):
        if not alfa_s: logger.info("Leyendo fichero cookies")
        try:
            cj.load(ficherocookies, ignore_discard=True)
            if alfa_caching:
                alfa_cookies = cj
                window.setProperty("alfa_cookies", str(alfa_cookies))
        except Exception:
            if not alfa_s: logger.info("El fichero de cookies existe pero es ilegible, se borra")
            os.remove(ficherocookies)
    cookies_lock.release()


def save_cookies(alfa_s=False):
    global alfa_cookies
    if alfa_caching:
        alfa_cookies = window.getProperty("alfa_cookies")
    if alfa_cookies != str(cj):
        cookies_lock.acquire()
        if not alfa_s: logger.info("Guardando cookies...")
        cj.save(ficherocookies, ignore_discard=True)
        if alfa_caching:
            alfa_cookies = cj
            window.setProperty("alfa_cookies", str(alfa_cookies))
        cookies_lock.release()


load_cookies()


def load_CF_list(domain='', **opt):
    global alfa_CF_list, CF_LIST

    try:
        CF_LIST_PATH = os.path.join(config.get_runtime_path(), "resources", "CF_Domains.txt")
        if not alfa_CF_list or not alfa_caching:
            if os.path.exists(CF_LIST_PATH):
                with open(CF_LIST_PATH, "rb") as CF_File:
                   _CF_LIST = config.decode_var(CF_File.read().splitlines())
                CF_LIST = list()
                CF_LIST += [CF_domain for CF_domain in _CF_LIST if CF_domain]
                if alfa_caching:
                   alfa_CF_list = CF_LIST
                   window.setProperty("alfa_CF_list", str(alfa_CF_list))
        elif alfa_caching:
            import ast
            CF_LIST = ast.literal_eval(window.getProperty("alfa_CF_list"))
    except:
        if alfa_caching: window.setProperty("alfa_CF_list", "")
        if os.path.exists(CF_LIST_PATH): os.remove(CF_LIST_PATH)
        CF_LIST = list()

    if domain in CF_LIST and 'CF' in opt and not opt['CF']:
        save_CF_list(domain, **opt)

    return CF_LIST


def save_CF_list(domain, **opt):
    global alfa_CF_list, CF_LIST
    
    CF_LIST_PATH = os.path.join(config.get_runtime_path(), "resources", "CF_Domains.txt")
    
    # Si el dominio está en CF_LIST y opt['CF']=False, se borra de la lista
    if domain and domain in CF_LIST and 'CF' in opt and not opt['CF']:
        CF_LIST.remove(domain)
        if alfa_caching:
           alfa_CF_list = CF_LIST
           window.setProperty("alfa_CF_list", str(alfa_CF_list))
        buffer = ''
        for dom in CF_LIST:
            if not dom: continue
            buffer += "%s\n" % dom
        with open(CF_LIST_PATH, "w") as CF_File:
            CF_File.write(buffer)
        domain = ''
    
    # Dominios que necesitan Cloudscraper. AÑADIR dominios de canales sólo si es necesario
    if domain:
        with open(CF_LIST_PATH, "a") as CF_File:
            CF_File.write("%s\n" % domain)
        if alfa_caching:
           alfa_CF_list += [domain]
           window.setProperty("alfa_CF_list", str(alfa_CF_list))


def random_useragent(browser='chrome'):
    """
    Python Method that generates fake user agents with a locally saved DB ('cloudscraper', 'user_agent', 'browsers.json').
    This is useful for webscraping, and testing programs that identify devices based on the user agent.
    """
    try:
        import random

        UserAgentPath = os.path.join(config.get_runtime_path(), 'lib', 'cloudscraper', 'user_agent', 'browsers.json')
        if os.path.exists(UserAgentPath):
            with open(UserAgentPath, "r") as uap:
                json_ua = json.loads(uap.read())
                platform_ua = __platform.replace('raspberry', 'linux').replace('osx', 'darwin')\
                                        .replace('xbox', 'windows').replace('tvos', 'ios')\
                                        .replace('atv2', 'android').replace('unknown', 'windows')
                if json_ua and (platform_ua in json_ua['user_agents']['desktop'] or platform_ua in json_ua['user_agents']['mobile']):
                    if platform_ua in json_ua['user_agents']['desktop']:
                        browser_json = json_ua['user_agents']['desktop'][platform_ua].get(browser, [])
                    else:
                        browser_json = json_ua['user_agents']['mobile'][platform_ua].get(browser, [])

                    UserAgentIem = random.choice(browser_json).strip()
                    logger.debug('Found %s' % UserAgentIem)
                    if UserAgentIem:
                        return UserAgentIem

    except:
        logger.error(traceback.format_exc())

    logger.debug('NOT Found, default %s' % default_headers["User-Agent"])
    return default_headers["User-Agent"]


def channel_proxy_list(url, forced_proxy=None):

    try:
        proxy_channel_bloqued_str = base64.b64decode(config.get_setting
                ('proxy_channel_bloqued')).decode('utf-8')
        proxy_channel_bloqued = dict()
        proxy_channel_bloqued = ast.literal_eval(proxy_channel_bloqued_str)
    except Exception:
        logger.debug('Proxytools no inicializado correctamente')
        try:
            logger.debug('Bloqued: ' + str(proxy_channel_bloqued_str))
        except Exception:
            pass
        return False

    if not url.endswith('/'):
        url += '/'

    domain = obtain_domain(url, sub=True)
    if proxy_channel_bloqued.get(domain, ''):
        if forced_proxy and forced_proxy not in ['Total', 'ProxyDirect', 'ProxyCF', 'ProxyWeb']:
            if forced_proxy in proxy_channel_bloqued[domain]:
                return True
            else:
                return False
        if forced_proxy:
            return True
        if not 'OFF' in proxy_channel_bloqued[domain]:
            return True

    return False


def check_proxy(url, **opt):

    proxy_data = dict()
    proxy_data['dict'] = {}
    proxy_data['url'] = url
    proxy_data['headers_proxy'] = {}
    proxy_data['post_proxy'] = None
    proxy_data['proxy__test'] = opt.get('proxy__test', '')
    proxy_data['proxy'] = opt.get('proxy', True)
    proxy_data['proxy_web'] = opt.get('proxy_web', False)
    proxy_data['proxy_addr_forced'] = opt.get('proxy_addr_forced', None)
    proxy_data['forced_proxy'] = opt.get('forced_proxy', None)
    proxy_data['force_proxy_get'] = opt.get('force_proxy_get', False)
    proxy_data['forced_proxy_opt'] = opt.get('forced_proxy_opt', '') or opt.get('canonical', {}).get('forced_proxy_opt', '')
    proxy_data['forced_proxy_ifnot_assistant'] = opt.get('forced_proxy_ifnot_assistant', '')
    proxy_data['proxy_retries'] = opt.get('proxy_retries', 1)

    if (proxy_data['proxy'] or proxy_data['proxy_web']) and (proxy_data['forced_proxy'] or proxy_data['proxy_addr_forced'] \
                            or channel_proxy_list(url, forced_proxy=proxy_data['forced_proxy'])):
        if not PY3: from . import proxytools
        else: from . import proxytools_py3 as proxytools
        # Returns: {'addr': , 'CF_addr': , 'web_name': , 'log': }
        proxy_data, opt = proxytools.get_proxy_addr(url, forced_proxy_m=proxy_data['forced_proxy'], proxy_data=proxy_data, **opt)
        url = proxy_data['url']
        proxy_data['stat'] = proxy_data.get('stat', '').replace(',P', ', P')

        if not PY3 and proxy_data.get('dict', {}).get('https', ''):
            proxy_data['dict']['https'] = str('http://'+ proxy_data['dict']['https'])
    
    return url, proxy_data, opt


def proxy_stat(url, proxy_data, **opt):
    if not proxy_data.get('stat', ''): return ''
    
    retry = ''
    if proxy_data.get('proxy__test', '') == 'retry': 
        retry = 'retry'
    elif channel_proxy_list(url):
        try:
            proxy_white_list_str = base64.b64decode(config.get_setting('proxy_white_list')).decode('utf-8')
            proxy_white_list = dict()
            proxy_white_list = ast.literal_eval(proxy_white_list_str)
            if not proxy_white_list.get(obtain_domain(url, sub=True), ''):
                retry = 'retry'
        except Exception:
            logger.debug('Proxytools no inicializado correctamente')
            logger.error(traceback.format_exc())
            
    
    if 'Proxy Direct' in proxy_data['stat']: return 'ProxyDirect:%s:%s' % (proxy_data.get('log', ''), retry)
    if 'Proxy CF' in proxy_data['stat']: return 'ProxyCF:%s:%s' % (proxy_data.get('log', ''), retry)
    if 'Proxy Web' in proxy_data['stat']: return 'ProxyWeb:%s:%s' % (proxy_data.get('web_name', ''), retry)
    
    return ''


def proxy_post_processing(url, proxy_data, response, **opt):

    opt['out_break'] = False
    data = ''
    if response['data']:
        data = response['data'][:500]
        if PY3 and isinstance(data, bytes):
            data = "".join(chr(x) for x in bytes(data))

    try:
        if response["code"] in NOT_FOUND_CODES:
            opt['proxy_retries'] = -1
        elif response["code"] not in SUCCESS_CODES+REDIRECTION_CODES and opt.get('forced_proxy_opt', '') == 'ProxyJSON':
            opt['forced_proxy_opt'] = 'ProxyCF'
            opt['forced_proxy'] = opt['forced_proxy_opt']

        if ', Proxy Web' in proxy_data.get('stat', ''):
            if not PY3: from . import proxytools
            else: from . import proxytools_py3 as proxytools
            
            if not ('application' in response['headers'].get('Content-Type', '') \
                        or 'javascript' in response['headers'].get('Content-Type', '') \
                        or 'image' in response['headers'].get('Content-Type', '')):
                response = proxytools.restore_after_proxy_web(response, proxy_data, **opt)
                data = response['data'][:500]
            
            if data.startswith('ERROR') or response["code"] in REDIRECTION_CODES:
                if response["code"] in SUCCESS_CODES+[666]: 
                    response["code"] = 666
                    if not opt.get('post_cookie', False):
                        url_domain = obtain_domain(url, scheme=True)
                        forced_proxy_temp = 'ProxyWeb:' + proxy_data['web_name']
                        data_domain = downloadpage(url_domain, alfa_s=True, ignore_response_code=True, headers=opt.get('headers', {}), 
                                                   CF_test=opt.get('CF_test', False), post_cookie=True, forced_proxy=forced_proxy_temp, 
                                                   proxy_retries_counter=0)
                        if data_domain.code in SUCCESS_CODES:
                            url = opt['url_save']
                            opt['post'] = opt['post_save']
                            opt['forced_proxy'] = forced_proxy_temp
                            return response, url, opt
                elif response["code"] in REDIRECTION_CODES and response['headers'].get('location', ''):
                    response['sucess'] = True
                if data.startswith('ERROR') or (response["code"] in REDIRECTION_CODES and not response['sucess']):
                    proxy_data['stat'] = ', Proxy Direct'
                    opt['forced_proxy'] = 'ProxyDirect'
                    url = opt['url_save']
                    opt['post'] = opt['post_save']
                    response['sucess'] = False
        elif response["code"] in REDIRECTION_CODES:
            response['sucess'] = True

        if proxy_data.get('stat', '') and not response['sucess'] and \
                opt.get('proxy_retries_counter', 0) <= opt.get('proxy_retries', 1) and \
                opt.get('count_retries_tot', 5) > 1:
            if not PY3: from . import proxytools
            else: from . import proxytools_py3 as proxytools
            
            if ', Proxy Direct' in proxy_data.get('stat', '') or ', Proxy CF' in proxy_data.get('stat', ''):
                if ', Proxy Direct' in proxy_data.get('stat', ''): proxy_init = 'ProxyDirect'
                if ', Proxy CF' in proxy_data.get('stat', ''): proxy_init = 'ProxyCF'
                proxytools.get_proxy_list_method(proxy_init=proxy_init,
                                                 error_skip=proxy_data['addr'] or proxy_data['CF_addr'], url_test=url, 
                                                 post_test=opt['post_save'], **opt)
                url = opt['url_save']
            
            elif ', Proxy Web' in proxy_data.get('stat', ''):
                if channel_proxy_list(opt['url_save'], forced_proxy=proxy_data['web_name']) \
                                      or channel_proxy_list(opt['url_save'], forced_proxy='ProxyCF'):
                    opt['forced_proxy'] = 'ProxyCF'
                    url = opt['url_save']
                    opt['post'] = opt['post_save']
                    opt['CF'] = True
                    if opt.get('proxy_retries_counter', 0):
                        opt['proxy_retries_counter'] -= 1
                    else:
                        opt['proxy_retries_counter'] = -1
                    proxytools.get_proxy_list_method(proxy_init='ProxyCF', url_test=url, 
                                                     post_test=opt['post_save'], **opt)
                else:
                    proxytools.get_proxy_list_method(proxy_init='ProxyWeb',
                                                     error_skip=proxy_data['web_name'], **opt)
                    url = opt['url_save']
                    opt['post'] = opt['post_save']

        else:
            opt['out_break'] = True
    except Exception:
        logger.error(traceback.format_exc())
        opt['out_break'] = True

    return response, url, opt


def blocking_error(url, req, proxy_data, **opt):

    if opt.get('canonical_check', False): return False
    code = str(req.status_code) or ''
    data = ''
    if req.content: data = req.content[:5000]
    canonical = opt.get('canonical', {})
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))
    resp = False

    if '104' in code or '10054' in code or ('404' in code and 'Object not found' in data \
                     and '.torrent' not in url) \
                     or ('502' in code and ('Por causas ajenas' in data or 'Contenido bloqueado' in data)) \
                     or ('sslcertverificationerror') in code.lower() \
                     or ('certificate verify failed') in code.lower() \
                     or (opt.get('check_blocked_IP', False) and 'Please wait while we try to verify your browser...' in data):
        resp = True

        if opt.get('check_blocked_IP', False):
            opt['proxy'] = True
            opt['forced_proxy'] = 'ProxyCF'
            opt['ignore_response_code'] = True
        
        if opt.get('check_blocked_IP', False) and 'Please wait while we try to verify your browser...' in data:
            opt['retry_alt'] = False
            if not opt.get('check_blocked_IP_save', {}):
                opt['check_blocked_IP_save'] = {}
                opt['check_blocked_IP_save']['data'] = req.content
                opt['check_blocked_IP_save']['code'] = req.status_code
            
            logger.debug('ERROR 99: IP bloqueada por la Web "%s".  Recupenrando...' % req.url)
            domain = obtain_domain(req.url, sub=True)
            domains = [domain]
            if domain in base64.b64decode(config.get_setting('proxy_channel_bloqued')).decode('utf-8'):
                try:
                    pCFa = base64.b64decode(config.get_setting('proxy_CF_addr')).decode('utf-8')
                    pCFl_str = base64.b64decode(config.get_setting('proxy_CF_list')).decode('utf-8')
                    pCFl = ast.literal_eval(pCFl_str)
                except:
                    pCFa = ''
                    pCFl = []
                pCFl = []
                if not pCFl:
                    if canonical.get('host_alt', []):
                        if not PY3: from . import proxytools
                        else: from . import proxytools_py3 as proxytools
                        for domain in [canonical['host']]+canonical['host_alt']:
                            if not domain: continue
                            domains += [obtain_domain(domain, sub=True)]
                        proxytools.add_domain_retried(domains, proxy__type=opt.get('forced_proxy', 
                                                      opt.get('forced_proxy_retry', '') or 'ProxyCF'), delete=True)
                    resp = False
                elif pCFa in pCFl: 
                    pCFl.remove(pCFa)
                    config.set_setting('proxy_CF_addr', base64.b64encode(str(pCFl[0] if len(pCFl) > 0 else '').encode('utf-8')).decode('utf-8'))
                    config.set_setting('proxy_CF_list', base64.b64encode(str(pCFl).encode('utf-8')).decode('utf-8'))
            else:
                if not PY3: from . import proxytools
                else: from . import proxytools_py3 as proxytools
                
                if not proxy_data.get('stat', ''):
                    for host in canonical.get('host_alt', []):
                        domains += [obtain_domain(host, sub=True)]
                proxytools.add_domain_retried(domains, proxy__type=opt.get('forced_proxy', 
                                              opt.get('forced_proxy_retry', '') or 'ProxyCF'), delete=True)
            
    elif data:
        for _code in SUCCESS_CODES+REDIRECTION_CODES:
            if str(_code) in code:
                code = ''
                break
        if code:
            data = re.sub(r"\n|\r|\t|\s{2,}", "", data)
            proxy = proxy_stat(opt.get('url_save', ''), proxy_data, **opt)
            if proxy and 'ProxyWeb' in proxy: url += ' / %s' % opt.get('url_save', '')
            try:
                logger.error('Error: %s, Url: %s, Datos: %s' % (code, url, data[:500]))
            except:
                logger.error('Error: %s, Url: %s, Datos: NULL' % (code, url))
    
    return resp


def canonical_quick_check(url, **opt):
    if not opt.get('canonical', {}) or '//127.0.0.1' in url or '//192.168.' in url or '//10.' in url \
                                    or '//176.' in url or '//localhost' in url:
        return url
    canonical = opt.get('canonical', {})
    
    alfa_s = True
    if not canonical.get('alfa_s', alfa_s): logger.info(url, force=True)

    url_host = scrapertools.find_single_match(url, patron_host).rstrip('/') + '/'
    if url_host and url_host in canonical.get('host_black_list', []) and canonical.get('host_alt', []):
        url = url.replace(url_host, canonical['host_alt'][0])

    if 'btdig' in canonical.get('host', '') and canonical.get('channel', ''):
        if canonical['host'] in url and canonical.get('host_alt', []):
            url = url.replace(canonical['host'], canonical['host_alt'][0])
        canonical['host'] = ''
        config.set_setting("current_host", canonical['host'], channel=canonical['channel'])
    
    return url


def canonical_check(url, response, req, **opt):
    
    if opt.get('canonical_check', False): return response
    if not response['data']: return response
    if isinstance(response['data'], dict): return response
    if '//127.0.0.1' in url or '//192.168.' in url or '//10.' in url or '//176.' in url or '//localhost' in url: return response
    
    alfa_s = True
    if not opt.get('canonical', {}).get('alfa_s', alfa_s): logger.info(url, force=True)
    
    canonical_host = ''
    data = ''
    if response['data']: data = response['data'][:250000]
    
    canonical = opt.get('canonical', {})
    canonical_new = False
    canonical_new_alt = []
    
    if canonical.get('host', '') and canonical.get('channel', '') and ('hideproxy' in canonical['host'] \
                                 or 'webproxy' in canonical['host'] or 'hidester' in canonical['host'] \
                                 or 'hide' in canonical['host'] or 'croxyproxy' in canonical['host'] \
                                 or '__cpo=' in canonical['host'] or 'btdig' in canonical['host']):
        config.set_setting("current_host", '', channel=canonical['channel'])
        canonical['host'] = ''
    
    if 'btdig' in url: return response
    
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))
    data = re.sub(r"\n|\r|\t|(<!--.*?-->)", "", data).replace("'", '"')
    if data.startswith('{'): return response
    
    patterns = ['href="?([^"|\s*]+)["|\s*]\s*rel="?canonical"?', 
                'rel="?canonical"?\s*href="?([^"|>]+)["|>|\s*]']
    if canonical.get('pattern_forced', ''):
        if isinstance(canonical['pattern_forced'], list):
            patterns = canonical['pattern_forced']
        else:
            patterns = [str(canonical['pattern_forced'])]
    elif canonical.get('pattern', ''):
        if isinstance(canonical['pattern'], list):
            patterns += canonical['pattern']
        else:
            patterns += [str(canonical['pattern'])]
    
    for pattern in patterns:
        canonical_host = str(scrapertools.find_single_match(data, pattern).rstrip())
        if len(canonical_host) < 8: canonical_host = ''
        if canonical_host:
            canonical_host = canonical_host.replace('\\', '')
            if canonical_host and not canonical_host.startswith('http') and canonical_host.startswith('//'):
                canonical_host = 'https:%s' % canonical_host
            if canonical_host and ('hideproxy' in canonical_host \
                              or 'webproxy' in canonical_host or 'hidester' in canonical_host \
                              or 'hide' in canonical_host or 'croxyproxy' in canonical_host \
                              or '__cpo=' in canonical_host or 'btdig' in canonical_host):
                canonical_host = ''
                continue
            canonical_host = scrapertools.find_single_match(canonical_host, patron_host)
            if canonical_host:
                break
    
    #if not canonical_host and (canonical.get('pattern', '') or canonical.get('pattern_forced', '')):
    #    logger.error('PATRÓN: %s / \nDATOS: %s' % (patterns, data[:3000]))
    if canonical_host:
        if not canonical_host.endswith('/'):
            canonical_host += '/'
        response['canonical'] = canonical_host
    if canonical.get('host', '') and canonical.get('host_black_list', []) and canonical.get('host_alt', []) \
                                 and canonical['host'] in canonical['host_black_list']:
        if not canonical_host or canonical_host in canonical['host_black_list']:
            canonical_host = canonical['host_alt'][0]
            response['canonical'] = canonical_host

    if response['sucess'] and response['canonical'] and canonical.get('channel', '') \
                          and (canonical.get('host', '') or canonical.get('host_alt', [])):
        if response['canonical'] != canonical.get('host', '') and response['canonical'] \
                          not in canonical.get('host_black_list', []):
            if response['canonical'] in url:
                canonical_new = response['canonical']
            else:
                host_list = [str(response['canonical'])]
                if canonical.get('host', '') and canonical['host'] not in canonical.get('host_black_list', []) \
                                             and canonical['host'] not in host_list:
                    if not isinstance(canonical['host'], list):
                        host_list += [str(canonical['host'])]
                    else:
                        host_list += canonical['host']
                if canonical.get('host_alt', []):
                    if isinstance(canonical['host_alt'], list):
                        for host_elem in canonical['host_alt']:
                            if host_elem not in host_list:
                                host_list += [str(host_elem)]
                    elif canonical['host_alt'] not in host_list:
                        host_list += [str(canonical['host_alt'])]

                for url_alt in host_list:
                    url_alt_ver = url_alt
                    if canonical.get('host_verification', ''):
                        if '%' in canonical['host_verification']:
                            url_alt_ver = canonical['host_verification'] % url_alt_ver
                        else:
                            url_alt_ver = canonical['host_verification']
                        
                    page = downloadpage(url_alt_ver, ignore_response_code=True, timeout=5, 
                                        CF=canonical.get('CF', False), retry_alt=False, 
                                        post=canonical.get('post', None), 
                                        referer=canonical.get('referer', None), 
                                        headers=canonical.get('headers', None), 
                                        CF_test=canonical.get('CF_test', False),
                                        alfa_s=canonical.get('alfa_s', alfa_s),
                                        forced_proxy_opt=canonical.get('forced_proxy_opt', ''), 
                                        canonical_check=True, url_save=opt.get('url_save', ''), 
                                        session_verify=opt.get('session_verify', False), 
                                        forced_proxy_ifnot_assistant=opt.get('forced_proxy_ifnot_assistant', ''))
                    if page.sucess:
                        if page.proxy__ and not response['proxy__']:
                            canonical_new_alt += [url_alt]
                            continue
                        canonical_new = url_alt
                        break
                else:
                    if canonical_new_alt and canonical.get('host', '') and canonical['host'] in canonical.get('host_black_list', []):
                        canonical_new = canonical_new_alt[0]
                    else:
                        canonical_new = ''
            
            if canonical_new and canonical_new != canonical.get('host', ''):
                logger.info('Canal: %s: Host "%s" cambiado a CANONICAL: %s - %s' % \
                    (canonical['channel'].capitalize(), canonical.get('host', ''), \
                    response['canonical'], canonical_new if canonical_new != response['canonical'] else ""), force=True)
                
                url, response = reset_canonical(canonical_new, url, response, **opt)

    return response


def retry_alt(url, req, response_call, proxy_data, **opt):
    logger.info(opt.get('canonical', {}).get('host_alt', []), force=True)
    
    channel = None
    canonical = opt.get('canonical', {})
    if not canonical.get('host_alt', []) or not canonical.get('channel', []):
        return url, response_call
    
    host_a = scrapertools.find_single_match(url, patron_host)
    if not host_a:
        return url, response_call
    
    logger.error('ERROR 98: Web "%s" caída, reintentando...' % host_a)
    config.set_setting('current_host', '', channel=canonical['channel'])        # Reseteamos el dominio
    
    try:
        channel = __import__('channels.%s' % canonical['channel'], None,
                             None, ["channels.%s" % canonical['channel']])
    except:
        logger.error(traceback.format_exc())
    
    for host_b in canonical['host_alt']:
        if host_b.rstrip('/') in url:
            continue
        host = host_b

        url_final = url.replace(host_a, host.rstrip('/'))
        
        opt['count_retries_tot'] = 1
        if proxy_data.get('stat', '') and not 'Proxy Web' in proxy_data.get('stat', '') and not TEST_ON_AIR:
            opt['count_retries_tot'] = 2
        opt['retry_alt'] = False
        opt['ignore_response_code'] = True
        
        response = downloadpage(url_final, **opt)
        
        if response.sucess:
            url = url_final
            if not response.host:
                url, response = reset_canonical(host_b, url, response, **opt)
            else:
                host = response.host
            break
    else:
        logger.error("ERROR 97: Webs caídas, ninguna Web alternativa encontrada")
        return url, response_call

    logger.info("INFO: Web activa encontrada: %s " % host, force=True)
    
    return url, response


def reset_canonical(canonical_new, url, response, **opt):
    
    canonical = opt.get('canonical', {})
    
    if not isinstance(response, dict):
        response.host = canonical_new
        if not url.startswith('magnet'):
            response.url_new = url.replace(scrapertools.find_single_match(url, patron_host), canonical_new.rstrip('/'))
    else:
        response['host'] = canonical_new
        if not url.startswith('magnet'):
            response['url_new'] = url.replace(scrapertools.find_single_match(url, patron_host), canonical_new.rstrip('/'))
    opt['canonical']['host'] = canonical_new
    config.set_setting("current_host", canonical_new, channel=canonical['channel'])
    
    try:
        channel = __import__('channels.%s' % canonical['channel'], None,
                             None, ["channels.%s" % canonical['channel']])
        channel.host = canonical_new
    except:
        logger.error(traceback.format_exc())
        
    return url, response


def downloadpage(url, **opt):
    """
        Abre una url y retorna los datos obtenidos

        @param url: url que abrir.
        @type url: str
        @param post: Si contiene algun valor este es enviado mediante POST.
        @type post: str (datos json), dict
        @param headers: Headers para la petición, si no contiene nada se usara los headers por defecto.
        @type headers: dict, list
        @param timeout: Timeout para la petición.
        @type timeout: int
        @param follow_redirects: Indica si se han de seguir las redirecciones.
        @type follow_redirects: bool
        @param cookies: Indica si se han de usar las cookies.
        @type cookies: bool
        @param replace_headers: Si True, los headers pasados por el parametro "headers" sustituiran por completo los headers por defecto.
                                Si False, los headers pasados por el parametro "headers" modificaran los headers por defecto.
        @type replace_headers: bool
        @param add_host: Indica si añadir el header Host al principio, como si fuese navegador común.
                         Desactivado por defecto, solo utilizarse con webs problemáticas (da problemas con proxies).
        @type add_host: bool
        @param add_referer: Indica si se ha de añadir el header "Referer" usando el dominio de la url como valor.
        @type add_referer: bool
        @param referer: Si se establece, agrega el header "Referer" usando el parámetro proporcionado como valor.
        @type referer: str
        @param only_headers: Si True, solo se descargarán los headers, omitiendo el contenido de la url.
        @type only_headers: bool
        @param random_headers: Si True, utiliza el método de seleccionar headers aleatorios.
        @type random_headers: bool
        @param ignore_response_code: Si es True, ignora el método para WebErrorException para error como el error 404 en veseriesonline, pero es un data funcional
        @type ignore_response_code: bool
        @param hide_infobox: Si es True, no muestra la ventana de información en el log cuando hay una petición exitosa (no hay un response_code de error).
        @type hide_infobox: bool
        @param soup: Si es True, establece un elemento BeautifulSoup en el atributo soup de HTTPResponse
        @type soup: bool
        @return: Resultado de la petición
        @rtype: HTTPResponse

                Parametro             | Tipo     | Descripción
                ----------------------|----------|-------------------------------------------------------------------------------
                HTTPResponse.sucess:  | bool     | True: Peticion realizada correctamente | False: Error al realizar la petición
                HTTPResponse.code:    | int      | Código de respuesta del servidor o código de error en caso de producirse un error
                HTTPResponse.error:   | str      | Descripción del error en caso de producirse un error
                HTTPResponse.headers: | dict     | Diccionario con los headers de respuesta del servidor
                HTTPResponse.data:    | str      | Respuesta obtenida del servidor
                HTTPResponse.json:    | dict     | Respuesta obtenida del servidor en formato json
                HTTPResponse.soup:    | bs4/None | Objeto BeautifulSoup, si se solicita. None de otra forma
                HTTPResponse.time:    | float    | Tiempo empleado para realizar la petición
                HTTPResponse.canonical:| str     | Dirección actual de la página descargada
                HTTPResponse.proxy__: | str      | Si la página se descarga con proxy, datos del proxy usado: proxy-type:addr:estado
    """
    global CF_LIST, CS_stat
    
    if 'api.themoviedb' in url: opt['hide_infobox'] = True

    if not opt.get('alfa_s', False) and not opt.get('hide_infobox', False):
        logger.info()
    url = str(url)

    # Evitamos escribir en el log si es un actualización de Videoteca, a menos que se fuerce con opt['hide_infobox'] = False
    if VIDEOLIBRARY_UPDATE and not 'hide_infobox' in opt:
        opt['hide_infobox'] = True
    
    # Si es una petición de un módulo involucrado en una búsqueda global en cancelación, se devuelve el control sin más
    if opt.get('canonical', {}).get('global_search_cancelled', False) or (config.GLOBAL_SEARCH_CANCELLED \
                                and opt.get('canonical', {}).get('global_search_active', False)):
        return global_search_canceled(url, **opt)
    
    # Reintentos para errores 403, 503
    if 'retries_cloudflare' not in opt: opt['retries_cloudflare'] = opt.get('canonical', {}).get('retries_cloudflare', 0)
    if 'CF' not in opt and 'CF_stat' in opt.get('canonical', {}): opt['CF'] = opt['canonical']['CF_stat']
    if 'cf_assistant' not in opt and 'cf_assistant' in opt.get('canonical', {}): opt['cf_assistant'] = opt['canonical']['cf_assistant']
    if 'session_verify' not in opt and 'session_verify' in opt.get('canonical', {}): opt['session_verify'] = opt['canonical']['session_verify']
    if not "session_verify_save" in opt: opt["session_verify_save"] = opt["session_verify"] if "session_verify" in opt else None
    
    # Preparando la url
    if not PY3:
        url = urllib.quote(url.encode('utf-8'), safe="%/:=&?~#+!$,;'@()*[]")
    else:
        url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    url = url.strip()
    url = canonical_quick_check(url, **opt)
    domain = urlparse.urlparse(url)[1]

    if domain in BLACK_LIST_DOMAINS:
        response = build_response()
        response['code'] = 404
        logger.error('Domain in BLACK LIST: %s' % domain)
        return type('HTTPResponse', (), response)

    # Dominios que necesitan Cloudscraper
    CF_LIST = load_CF_list(domain, **opt)

    # Cargando Cookies
    load_cookies(opt.get('alfa_s', False) or opt.get('hide_infobox', False))

    # Cargando UA
    cf_ua = config.get_setting('cf_assistant_ua', None)

    # Headers por defecto, si no se especifica nada
    req_headers = OrderedDict()
    if opt.get('add_host', False):
        req_headers['Host'] = obtain_domain(url)
    req_headers.update(default_headers.copy())

    if opt.get('add_referer', False):
        req_headers['Referer'] = "/".join(url.split("/")[:3])

    if isinstance(opt.get('referer'), str) and '://' in opt.get('referer'):
        req_headers['Referer'] = opt.get('referer')

    # Headers pasados como parametros
    if opt.get('headers', None) is not None:
        if not opt.get('replace_headers', False):
            req_headers.update(dict(opt['headers']))
        else:
            req_headers = dict(opt('headers'))

    if opt.get('random_headers', False) or HTTPTOOLS_DEFAULT_RANDOM_HEADERS:
        req_headers['User-Agent'] = random_useragent()

    opt['proxy_retries_counter'] = 0
    opt['url_save'] = opt.get('url_save', '') or url
    opt['post_save'] = opt.get('post', None)
    if opt.get('forced_proxy_opt', None) and channel_proxy_list(url):
        if opt['forced_proxy_opt'] in ['ProxyCF', 'ProxyDirect']:
            if 'cliver' not in url:
                opt['forced_proxy_opt'] = 'ProxyJSON'
            else:
                opt['forced_proxy'] = opt['forced_proxy_opt']
        elif opt['forced_proxy_opt'] in ['ProxyCF|FORCE', 'ProxyDirect|FORCE']:
            opt['forced_proxy'] = opt['forced_proxy_opt'].split('|')[0]
        else:
            opt['forced_proxy'] = opt['forced_proxy_opt']

    if opt.get('canonical', {}).get('forced_proxy_ifnot_assistant', '') or opt.get('forced_proxy_ifnot_assistant', ''):
        opt['forced_proxy_ifnot_assistant'] = opt.get('canonical', {}).get('forced_proxy_ifnot_assistant', '') \
                                              or opt.get('forced_proxy_ifnot_assistant', '')
        opt['ignore_response_code'] = True

    response = {}
    
    while opt['proxy_retries_counter'] <= opt.get('proxy_retries', 1):
        response = {}
        info_dict = []
        payload = dict()
        files = {}
        file_name_ = ''
        opt['proxy_retries_counter'] += 1
        domain = urlparse.urlparse(url)[1]

        if (domain in CF_LIST or opt.get('CF', False)) and opt.get('CF_test', True) \
                              and opt.get('cloudscraper_active', True):         # Está en la lista de CF o viene en la llamada
            from lib.cloudscraper import create_scraper
            session = create_scraper(user_url=url, user_opt=opt)                # El dominio necesita CloudScraper
            if 'session_verify' not in opt:
                opt['session_verify'] = True
            elif not opt['session_verify'] and not ssl_version:
                opt['session_verify'] = True
            session.verify = opt['session_verify']
            CS_stat = True
            if cf_ua and cf_ua != 'Default' and get_cookie(url, 'cf_clearance'):
                req_headers['User-Agent'] = cf_ua
        else:
            session = requests.session()
            session.verify = opt.get('session_verify', False)
            CS_stat = False

        # Conectar la versión de SSL TLS con la sesión
        if url.startswith('https:') and ssl_version and (opt.get('set_tls', False) or opt.get('canonical', {}).get('set_tls', False) or SET_TLS):
            if not opt.get('set_tls_min', False) and not opt.get('canonical', {}).get('set_tls_min', False) \
                                                  or ((opt.get('set_tls_min', False) or opt.get('canonical', {}).get('set_tls_min', False)) \
                                                  and ssl_version_min):
                session.mount(url.rstrip('/'), TLSHttpAdapter())
                opt['set_tls_OK'] = True

        if opt.get('cookies', True):
            session.cookies = cj
        
        if not opt.get('keep_alive', True):
            #session.keep_alive =  opt['keep_alive']
            req_headers['Connection'] = "close"

        # Prepara la url en caso de necesitar proxy, o si se envía "proxy_addr_forced" desde el canal
        url, proxy_data, opt = check_proxy(url, **opt)
        if proxy_data.get('dict', {}):
            session.proxies = proxy_data['dict']
            #if opt["session_verify_save"] is None: session.verify = opt['session_verify'] = False
        if opt.get('headers_proxy', {}):
            req_headers.update(dict(opt['headers_proxy']))

        session.headers = req_headers.copy()

        inicio = time.time()
        
        if opt.get('timeout', None) is None and HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT is not None: 
            opt['timeout'] = HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT
        if opt['timeout'] == 0:
            opt['timeout'] = None

        if len(url) > 0:
            try:
                if opt.get('post', None) is not None or opt.get('file', None) is not None or opt.get('files', {}):
                    if opt.get('post', None) is not None:
                        ### Convert string post in dict
                        try:
                            json.loads(opt['post'])
                            payload = opt['post']
                        except Exception:
                            if not isinstance(opt['post'], dict):
                                post = urlparse.parse_qs(opt['post'], keep_blank_values=1)
                                payload = dict()

                                for key, value in list(post.items()):
                                    try:
                                        payload[key] = value[0]
                                    except Exception:
                                        payload[key] = ''
                            else:
                                payload = opt['post']

                    ### Verifies 'file' and 'file_name' options to upload a buffer or a file
                    if opt.get('files', {}):
                        files = opt['files']
                        file_name_ = opt.get('file_name', 'File Object')
                    elif opt.get('file', None) is not None:
                        if len(opt['file']) < 256 and os.path.isfile(opt['file']):
                            if opt.get('file_name', None) is None:
                                path_file, opt['file_name'] = os.path.split(opt['file'])
                            files = {'file': (opt['file_name'], open(opt['file'], 'rb'))}
                            file_name_ = opt['file']
                        else:
                            files = {'file': (opt.get('file_name', 'Default'), opt['file'])}
                            file_name_ = opt.get('file_name', 'Default') + ', Buffer de memoria'

                    info_dict = fill_fields_pre(url, proxy_data, file_name_, **opt)
                    if opt.get('only_headers', False):
                        ### Makes the request with HEAD method
                        req = session.head(url, allow_redirects=opt.get('follow_redirects', True),
                                          timeout=opt.get('timeout', None), params=opt.get('params', {}))
                    else:
                        ### Makes the request with POST method
                        req = session.post(url, data=payload, allow_redirects=opt.get('follow_redirects', True),
                                          files=files, timeout=opt.get('timeout', None), params=opt.get('params', {}))
                
                elif opt.get('only_headers', False):
                    info_dict = fill_fields_pre(url, proxy_data, file_name_, **opt)
                    ### Makes the request with HEAD method
                    req = session.head(url, allow_redirects=opt.get('follow_redirects', True),
                                      timeout=opt.get('timeout', None), params=opt.get('params', {}))
                else:
                    info_dict = fill_fields_pre(url, proxy_data, file_name_, **opt)
                    ### Makes the request with GET method
                    req = session.get(url, allow_redirects=opt.get('follow_redirects', True),
                                      timeout=opt.get('timeout', None), params=opt.get('params', {}))

            except Exception as e:
                req = requests.Response()
                req.status_code = response_code = str(e)
                block = blocking_error(url, req, proxy_data, **opt)
                canonical = opt.get('canonical', {})
                
                if block and opt.get('retry_alt', retry_alt_default) and opt.get('proxy__test', '') != 'retry' \
                                                                     and not proxy_data.get('stat', ''):
                    url_host = scrapertools.find_single_match(url, patron_host)
                    url_host = url_host  + '/' if url_host and not url_host.endswith('/') else ''
                    if canonical.get('host_alt', []) and canonical.get('host_black_list', []) \
                                                     and url_host != canonical['host_alt'][0] \
                                                     and url_host in canonical['host_black_list']:
                        url_alt = url.replace(url_host, canonical['host_alt'][0])
                        if not opt.get('alfa_s', False): logger.error('Error: %s in url: %s - Reintentando con %s' \
                                                                       % (response_code, url, url_alt))
                        opt['proxy__test'] = 'retry'
                        return downloadpage(url_alt, **opt)

                if not opt.get('ignore_response_code', False) and not proxy_data.get('stat', '') and not block:
                    
                    if opt.get('retry_alt', retry_alt_default) and opt.get('canonical', {}).get('host_alt', []) \
                                and len(opt['canonical']['host_alt']) > 1 \
                                and opt.get('canonical', {}).get('channel', []):
                        url, response = retry_alt(url, req, {}, proxy_data, **opt)
                        if not isinstance(response, dict) and response.host:
                            return response

                    if opt.get('canonical', {}).get('channel', ''):
                        config.set_setting("current_host", '', channel=opt['canonical']['channel'])
                        opt['canonical']['host'] = ''
                    
                    response = build_response()
                    response['time_elapsed'] = time.time() - inicio
                    info_dict.append(('Success', 'False'))
                    response['code'] = req.status_code
                    info_dict.append(('Response code', response['code']))
                    info_dict.append(('Finalizado en', response['time_elapsed']))
                    if not opt.get('alfa_s', False):
                        show_infobox(info_dict, force=True)
                        logger.error(traceback.format_exc(1))
                    return type('HTTPResponse', (), response)
        
        else:
            response = build_response()
            response['time_elapsed'] = time.time() - inicio
            return type('HTTPResponse', (), response)
        
        response = build_response()
        response_code = req.status_code
        response['data'] = req.content
        response['proxy__'] = proxy_stat(opt['url_save'], proxy_data, **opt)

        canonical = opt.get('canonical', {})
        
        block = blocking_error(url, req, proxy_data, **opt)


        # Retries if host changed but old host in error
        if block and opt.get('retry_alt', retry_alt_default) and opt.get('proxy__test', '') != 'retry' and not proxy_data.get('stat', ''):
            url_host = scrapertools.find_single_match(url, patron_host)
            url_host = url_host  + '/' if url_host and not url_host.endswith('/') else ''
            
            if canonical.get('host_alt', []) and canonical.get('host_black_list', []) \
                                             and url_host != canonical['host_alt'][0] \
                                             and url_host in canonical['host_black_list']:
                url_alt = url.replace(url_host, canonical['host_alt'][0])
                if not opt.get('alfa_s', False): logger.error('Error: %s in url: %s - Reintentando con %s' % (response_code, url, url_alt))
                opt['proxy__test'] = 'retry'
                return downloadpage(url_alt, **opt)
        
        # Retries blocked domain with proxy
        if block and opt.get('retry_alt', retry_alt_default) and opt.get('proxy__test', '') != 'retry' \
                 and not proxy_data.get('stat', '') and opt.get('proxy_retries', 1):
            if not opt.get('alfa_s', False): logger.error('Error: %s in url: %s - Reintentando' % (response_code, url))
            forced_proxy_web = 'ProxyWeb:croxyproxy.com' if not opt.get('CF', False) else 'ProxyWeb:hidester.com'
            opt['forced_proxy'] = opt.get('forced_proxy', '') or opt.get('forced_proxy_retry', '') \
                                                              or opt.get('forced_proxy_ifnot_assistant', '') \
                                                              or forced_proxy_web
            if 'ProxyWeb' in opt['forced_proxy']: 
                opt['proxy_web'] = True
            else:
                opt['proxy'] = True
            #opt['proxy'] = opt.get('proxy', False) or False
            #if not opt['proxy']: opt['proxy_web'] = opt.get('proxy_web', False) or True
            opt['CF_test'] = False
            opt['proxy_retries'] = 1 if PY3 and not TEST_ON_AIR else 0
            opt['proxy__test'] = 'retry'
            return downloadpage(url, **opt)
        
        # Retries blocked proxied IPs with more proxy
        if block and opt.get('check_blocked_IP', False) and opt.get('proxy__test', '') != 'retry' \
                 and not proxy_data.get('stat', '') and opt.get('proxy_retries', 1):
            if not opt.get('alfa_s', False): logger.error('Error: %s en IP bloqueada: %s - Reintentando' % (response_code, url))
            opt['proxy_retries'] = 1 if PY3 and not TEST_ON_AIR else 0
            opt['proxy__test'] = 'retry'
            return downloadpage(url, **opt)

        # Retries Cloudflare errors
        if req.headers.get('Server', '').startswith('cloudflare') and response_code in CLOUDFLARE_CODES \
                        and (not opt.get('CF', False) or opt['retries_cloudflare'] > 0) and opt.get('CF_test', True) \
                        and not opt.get('check_blocked_IP_save', {}):
            domain = urlparse.urlparse(opt['url_save'])[1]
            if (domain not in CF_LIST and opt['retries_cloudflare'] >= 0) or opt['retries_cloudflare'] > 0:
                if not '__cpo=' in url and domain not in CF_LIST:
                    CF_LIST += [domain]
                    save_CF_list(domain, **opt)
                opt['proxy_retries'] = 1 if PY3 and not TEST_ON_AIR else 0 if opt['retries_cloudflare'] < 1 else 1
                logger.debug("CF retry... for domain: %s, Retry: %s" % (domain, opt['retries_cloudflare']))
                if opt['retries_cloudflare'] > 0: time.sleep(1)
                opt['retries_cloudflare'] -= 1
                if not "CF_save" in opt: opt["CF_save"] = opt["CF"] if "CF" in opt else None
                if opt["CF_save"] is None: opt["CF"] = False if opt['retries_cloudflare'] > 0 else True
                return downloadpage(opt['url_save'], **opt)
        
        if req.headers.get('Server', '') == 'Alfa' and response_code in CLOUDFLARE_CODES \
                        and not opt.get('cf_v2', False) and opt.get('CF_test', True):
            opt["cf_v2"] = True
            if not PY3: opt['proxy_retries'] = 0
            if opt['retries_cloudflare'] > 0: time.sleep(1)
            opt['retries_cloudflare'] -= 1
            logger.debug("CF Assistant retry... for domain: %s" % urlparse.urlparse(url)[1])
            return downloadpage(url, **opt)

        # Si hay bloqueo "cf_v2" y no hay Alfa Assistant, se reintenta con Proxy
        if opt.get('forced_proxy_ifnot_assistant', '') \
                           and ('Detected a Cloudflare version 2' in str(response_code) or response_code in CLOUDFLARE_CODES) \
                           and opt.get('proxy__test', '') != 'retry':
            if opt.get('cf_v2', False):
                response['code'] = response_code
                response['headers'] = req.headers
                info_dict, response = fill_fields_post(url, info_dict, req, response, req_headers, inicio, **opt)
                show_infobox(info_dict, force=True)
            
            opt['proxy_retries'] = 1 if PY3 and not TEST_ON_AIR else 0
            opt['proxy__test'] = 'retry'
            if not PY3: from . import proxytools
            else: from . import proxytools_py3 as proxytools
            domain = obtain_domain(url, sub=True)
            opt['forced_proxy'] = opt.get('forced_proxy_ifnot_assistant', '')
            proxytools.add_domain_retried(domain, proxy__type=opt['forced_proxy'])
            return downloadpage(url, **opt)

        try:
            response['encoding'] = str(req.encoding).lower() if req.encoding and req.encoding is not None else None

            if opt.get('encoding') and opt.get('encoding') is not None:
                encoding = opt["encoding"]
            else:
                encoding = response['encoding']

            if not encoding:
                encoding = 'utf-8'

            if PY3 and isinstance(response['data'], bytes) and encoding is not None \
                    and ('text/' in req.headers.get('Content-Type', '') \
                        or 'json' in req.headers.get('Content-Type', '') \
                        or 'xml' in req.headers.get('Content-Type', '')):
                response['data'] = response['data'].decode(encoding)

        except Exception:
            logger.error(traceback.format_exc(1))

        try:
            if PY3 and isinstance(response['data'], bytes) \
                    and not ('application' in req.headers.get('Content-Type', '') \
                    or 'javascript' in req.headers.get('Content-Type', '') \
                    or 'image' in req.headers.get('Content-Type', '')):
                response['data'] = "".join(chr(x) for x in bytes(response['data']))

        except Exception:
            logger.error(traceback.format_exc(1))

        try:
            if 'text/' in req.headers.get('Content-Type', '') \
                        or 'json' in req.headers.get('Content-Type', '') \
                        or 'xml' in req.headers.get('Content-Type', ''):
                response['data'] = response['data'].replace('&Aacute;', 'Á').replace('&Eacute;', 'É')\
                      .replace('&Iacute;', 'Í').replace('&Oacute;', 'Ó').replace('&Uacute;', 'Ú')\
                      .replace('&Uuml;', 'Ü').replace('&iexcl;', '¡').replace('&iquest;', '¿')\
                      .replace('&Ntilde;', 'Ñ').replace('&ntilde;', 'n').replace('&uuml;', 'ü')\
                      .replace('&aacute;', 'á').replace('&eacute;', 'é').replace('&iacute;', 'í')\
                      .replace('&oacute;', 'ó').replace('&uacute;', 'ú').replace('&ordf;', 'ª')\
                      .replace('&ordm;', 'º')

        except Exception:
            logger.error(traceback.format_exc(1))

        response['url'] = req.url

        if not response['data']:
            response['data'] = ''

        try:
            if 'bittorrent' not in req.headers.get('Content-Type', '') \
                        and 'octet-stream' not in req.headers.get('Content-Type', '') \
                        and 'zip' not in req.headers.get('Content-Type', '') \
                        and opt.get('json_to_utf8', True):
                response['json'] = to_utf8(req.json())

            else:
                response['json'] = dict()

        except Exception:
            response['json'] = dict()
        response['code'] = response_code
        response['headers'] = req.headers
        response['cookies'] = req.cookies
        response['sucess'] = True if response['code'] in SUCCESS_CODES else False

        if not response['sucess'] and opt.get('retry_alt', retry_alt_default) \
                                  and opt.get('canonical', {}).get('host_alt', []) \
                                  and len(opt['canonical']['host_alt']) > 1 \
                                  and opt.get('canonical', {}).get('channel', []):
            url, response = retry_alt(url, req, response, proxy_data, **opt)
            if not isinstance(response, dict) and response.host:
                response.time_elapsed = time.time() - inicio
                return response

        if opt.get('cookies', True):
            save_cookies(alfa_s=opt.get('alfa_s', False))

        is_channel = inspect.getmodule(inspect.currentframe().f_back)
        is_channel = scrapertools.find_single_match(str(is_channel), "<module '(channels).*?'")
        if is_channel and isinstance(response_code, int):
            if not opt.get('ignore_response_code', False) and not proxy_data.get('stat', ''):
                if response_code > 399:
                    info_dict, response = fill_fields_post(url, info_dict, req, response, req_headers, inicio, **opt)
                    show_infobox(info_dict, force=True)
                    response = canonical_check(opt['url_save'], response, req, **opt)
                    raise WebErrorException(urlparse.urlparse(url)[1])

        info_dict, response = fill_fields_post(url, info_dict, req, response, req_headers, inicio, **opt)
        if not opt.get('alfa_s', False):
            if not response['sucess'] or opt.get("hide_infobox") is None:
                show_infobox(info_dict, force=True)
            elif not opt.get("hide_infobox"):
                show_infobox(info_dict)

        # Si hay error del proxy, refresca la lista y reintenta el numero indicada en proxy_retries
        response, url, opt = proxy_post_processing(url, proxy_data, response, **opt)
        response = canonical_check(opt['url_save'], response, req, **opt)
        
        response['soup'] = None
        if opt.get("soup", False):
            try:
                from bs4 import BeautifulSoup
                response["soup"] = BeautifulSoup(response['data'], "html5lib", from_encoding=opt.get('encoding', response['encoding']))

            except Exception:
                logger.error("Error creando sopa")
                logger.error(traceback.format_exc())
        
        response['time_elapsed'] = time.time() - inicio

        # Si proxy ordena salir del loop, se sale
        if opt.get('out_break', False):
            if opt.get('check_blocked_IP', False) and not response['sucess']:
                if opt.get('canonical', {}).get('host_alt', []):
                    if not PY3: from . import proxytools
                    else: from . import proxytools_py3 as proxytools
                    domains = []
                    for domain in [opt['canonical']['host']]+opt['canonical']['host_alt']:
                        if not domain: continue
                        domains += [obtain_domain(domain, sub=True)]
                    proxytools.add_domain_retried(domains, proxy__type=opt.get('forced_proxy', 
                                                  opt.get('forced_proxy_retry', '') or 'ProxyCF'), delete=True)
                if opt.get('check_blocked_IP_save', {}):
                    response['data'] = opt['check_blocked_IP_save']['data']
                    if PY3 and isinstance(response['data'], bytes):
                        response['data'] = "".join(chr(x) for x in bytes(response['data']))
                    response_code = response["code"] = opt['check_blocked_IP_save']['code']
                    response['sucess'] = True
            break

    if not response:
        response = build_response()

    return type('HTTPResponse', (), response)


def show_infobox(info_dict, force=False):
    logger.info()
    from textwrap import wrap

    box_items_kodi = {'r_up_corner': u'\u250c',
                      'l_up_corner': u'\u2510',
                      'center': u'\u2502',
                      'r_center': u'\u251c',
                      'l_center': u'\u2524',
                      'fill': u'\u2500',
                      'r_dn_corner': u'\u2514',
                      'l_dn_corner': u'\u2518',
                      }

    box_items = {'r_up_corner': '+',
                 'l_up_corner': '+',
                 'center': '|',
                 'r_center': '+',
                 'l_center': '+',
                 'fill': '-',
                 'r_dn_corner': '+',
                 'l_dn_corner': '+',
                 }

    width = 60
    version = 'Alfa: %s' % __version
    if config.is_xbmc():
        box = box_items_kodi
    else:
        box = box_items

    logger.info('%s%s%s' % (box['r_up_corner'], box['fill'] * width, box['l_up_corner']), force=force)
    logger.info('%s%s%s' % (box['center'], version.center(width), box['center']), force=force)
    logger.info('%s%s%s' % (box['r_center'], box['fill'] * width, box['l_center']), force=force)

    count = 0
    for key, value in info_dict:
        count += 1
        text = '%s: %s' % (key, value)

        if len(text) > (width - 2):
            text = wrap(text, width)
        else:
            text = text.ljust(width, ' ')
        if isinstance(text, list):
            for line in text:
                if len(line) < width:
                    line = line.ljust(width, ' ')
                logger.info('%s%s%s' % (box['center'], line, box['center']), force=force)
        else:
            logger.info('%s%s%s' % (box['center'], text, box['center']), force=force)
        if count < len(info_dict):
            logger.info('%s%s%s' % (box['r_center'], box['fill'] * width, box['l_center']), force=force)
        else:
            logger.info('%s%s%s' % (box['r_dn_corner'], box['fill'] * width, box['l_dn_corner']), force=force)
    return


def fill_fields_pre(url, proxy_data, file_name_, **opt):
    info_dict = []
    
    try:
        info_dict.append(('Timeout', opt['timeout']))
        info_dict.append(('URL', url))
        info_dict.append(('Dominio', '%s - Verify: %s' % (urlparse.urlparse(url)[1], opt.get('session_verify', False))))
        if CS_stat:
            info_dict.append(('Dominio_CF', True))
        if not opt.get('CF_test', True):
            info_dict.append(('CF_test', False))
        if not opt.get('keep_alive', True):
            info_dict.append(('Keep Alive', opt.get('keep_alive', True)))
        if opt.get('cf_v2', False):
            info_dict.append(('CF v2 Assistant', opt.get('cf_v2', False)))
        if opt.get('post', None) is not None or opt.get('files', None):
            info_dict.append(('Peticion', 'POST' + proxy_data.get('stat', '')))
        elif opt.get('only_headers', False):
            info_dict.append(('Peticion', 'HEAD' + proxy_data.get('stat', '')))
        else:
            info_dict.append(('Peticion', 'GET' + proxy_data.get('stat', '')))
        info_dict.append(('Descargar Pagina', not opt.get('only_headers', False)))
        info_dict.append(('BeautifulSoup', opt.get("soup", False)))
        if opt.get('files', {}) and not isinstance(opt.get('files'), (tuple, dict)):
            info_dict.append(('Objeto fichero', opt.get('files', {})))
        elif file_name_: 
            info_dict.append(('Fichero para Upload', file_name_))
        if opt.get('params', {}): info_dict.append(('Params', opt.get('params', {})))
        if opt.get('set_tls_OK', False): info_dict.append(('SSL_TLS_version:', ssl_version))
        info_dict.append(('Usar cookies', opt.get('cookies', True)))
        info_dict.append(('Fichero de cookies', ficherocookies))

    except Exception:
        logger.error(traceback.format_exc(1))
    
    return info_dict
    
    
def fill_fields_post(url, info_dict, req, response, req_headers, inicio, **opt):
    try:
        if isinstance(response["data"], str) and \
                        ('Hotlinking directly to proxied pages is not permitted.' in response["data"] \
                        or '<h3>Something is wrong</h3>' in response["data"]):
            response["code"] = 666
        cf_clearance = get_cookie(str(url), 'cf_clearance')
        cf_clearance = 'cf_clearance=%s' % cf_clearance if cf_clearance else ''
        info_dict.append(('Cookies', '%s %s' % (str(req.cookies), cf_clearance)))
        info_dict.append(('Data Encoding', req.encoding))
        info_dict.append(('Response code', response['code']))

        if response['code'] in SUCCESS_CODES:
            info_dict.append(('Success', 'True'))
            response['sucess'] = True
        else:
            info_dict.append(('Success', 'False'))
            response['sucess'] = False

        info_dict.append(('Response data length', 0 if not response['data'] else len(response['data'])))

        info_dict.append(('Request Headers', ''))
        for header in req_headers:
            info_dict.append(('- %s' % header, req_headers[header]))

        info_dict.append(('Response Headers', ''))
        for header in response['headers']:
            info_dict.append(('- %s' % header, response['headers'][header]))
        url_new = None
        if not response['proxy__'] and opt.get('url_save', '') and opt['url_save'] != response['url']:
            url_new = response['url']
        if not response['proxy__'] and opt.get('url_save', '') and response['url_new'] and opt['url_save'] != response['url_new']:
            url_new = response['url_new']
        if url_new:
            info_dict.append(('- New URL', url_new))
        info_dict.append(('Finalizado en', time.time() - inicio))
    except Exception:
        logger.error(traceback.format_exc(1))
    
    return info_dict, response


def global_search_canceled(url, **opt):
    logger.info(url)
    
    response = build_response()
    response = {}
    response['code'] = 777

    raise Exception(type('HTTPResponse', (), response))


def obtain_domain(url, sub=False, point=False, scheme=False):
    url_org = url

    if url and len(url) > 1:
        url = urlparse.urlparse(url).netloc
        if sub:
            split_lst = url.split(".")
            if len(split_lst) > 2:
                if not point:
                    split_lst[0] += '.'
                url = url.replace(split_lst[0], "")
        if scheme:
            url = '%s://%s' % (urlparse.urlparse(url_org).scheme, url)

    return url
    

def build_response(HTTPResponse=False):
    
    response = {}
    
    response['data'] = ''
    response['encoding'] = None
    response['sucess'] = False
    response['code'] = ''
    response['soup'] = None
    response['json'] = dict()
    response['proxy__'] = ''
    response['canonical'] = ''
    response['host'] = ''
    response['url'] = ''
    response['url_new'] = ''
    response['headers'] = {}
    response['cookies'] = ''
    response['time_elapsed'] = 0
    
    return type('HTTPResponse', (), response) if HTTPResponse else response