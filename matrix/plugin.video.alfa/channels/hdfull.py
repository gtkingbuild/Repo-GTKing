# -*- coding: utf-8 -*-

from builtins import chr
from builtins import range
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urlparse
    from lib import alfaresolver_py3 as alfaresolver
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido
    import urlparse
    from lib import alfaresolver

import base64
import re
import xbmcgui
import json as json_fn
import traceback

from core import httptools
from core import jsontools
from core import scrapertools
from core import servertools, tmdb
from core.item import Item
from platformcode import config, logger, help_window
from channels import autoplay
from channels import filtertools
from platformcode import platformtools
from channelselector import get_thumb

# https://dominioshdfull.com/

host = 'https://hdfull.store/'
assistant = config.get_setting('assistant_version', default='')
if assistant: 
    assistant_copy = assistant.split('.')
    assistant = tuple((int(assistant_copy[0]), int(assistant_copy[1]), int(assistant_copy[2])))
    if assistant < (1, 3, 91) or httptools.channel_proxy_list(host): assistant = tuple()

canonical = {
             'channel': 'hdfull', 
             'host': host if assistant else 'https://hdfull.org/', 
             'host_alt': [host if assistant else 'https://hdfull.org/'], 
             'host_verification': '%slogin', 
             'host_black_list': ['https://hdfull.store/' if not assistant else 'https://hdfull.org/', 
                                 'https://hdfull.life/', 'https://hdfull.digital/', 'https://hdfull.work/', 
                                 'https://hdfull.video/', 'https://hdfull.cloud/', 'https://hdfull.wtf/', 
                                 'https://hdfull.fun/', 'https://hdfull.lol/', 'https://hdfull.one/', 
                                 'https://new.hdfull.one/', 'https://hdfull.top/', 'https://hdfull.bz/'],
             'set_tls': True, 'set_tls_min': False, 'retries_cloudflare': 1, 'expires': 365*24*60*60, 
             'forced_proxy_ifnot_assistant': 'ProxyCF', 'CF_if_NO_assistant': False, 
             'CF_stat': True if assistant else False, 'session_verify': True if assistant else False, 
             'CF_if_assistant': True if assistant else False, 
             'preferred_proxy_ip': '', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host

_silence = config.get_setting('silence_mode', channel=canonical['channel'])
show_langs = config.get_setting('show_langs', channel=canonical['channel'])
unify = config.get_setting('unify')
__modo_grafico__ = config.get_setting('modo_grafico', channel=canonical['channel'])

IDIOMAS = {'lat': 'LAT', 'spa': 'CAST', 'esp': 'CAST', 'sub': 'VOSE', 'espsub': 'VOSE', 'engsub': 'VOS', 'eng': 'VO'}
list_language = list(set(IDIOMAS.values()))
list_quality = ['HD1080', 'HD720', 'HDTV', 'DVDRIP', 'RHDTV', 'DVDSCR']
list_servers = ['clipwatching', 'gamovideo', 'vidoza', 'vidtodo', 'openload', 'uptobox']

""" CACHING HDFULL PARAMETERS """
account = config.get_setting("logged", channel=canonical['channel'])
try:
    user_ = urllib.quote_plus(config.get_setting('hdfulluser', channel=canonical['channel'], default=''))
    pass_ = urllib.quote_plus(config.get_setting('hdfullpassword', channel=canonical['channel'], default=''))
except:
    from core import filetools
    setting = filetools.read(filetools.join(config.get_data_path(), 'settings_channels', 'hdfull_data.json'), silent=True)
    if setting:
        setting = base64.b64encode(setting.encode('utf-8')).decode('utf-8')
    else:
        setting = 'VACIO'
    logger.error('Type: User: %s; Password: %s; %s' % (str(type(config.get_setting('hdfulluser', 
                                                       channel=canonical['channel'], default=''))), 
                                                       str(type(config.get_setting('hdfullpassword', 
                                                       channel=canonical['channel'], default=''))), setting))
    user_ = ''
    pass_ = ''
    account = False
    config.set_setting('hdfulluser', user_, channel=canonical['channel'])
    config.set_setting('hdfullpassword', pass_, channel=canonical['channel'])
    config.set_setting('logged', account, channel=canonical['channel'])
credentials_req = True
js_url = urlparse.urljoin(host, "templates/hdfull/js/jquery.hdfull.view.min.js")
data_js_url = urlparse.urljoin(host, "js/providers.js")
patron_sid = "<input\s*type='hidden'\s*name='__csrf_magic'\s*value=\"([^\"]+)\"\s*\/>"
window = None
proxy__ = ''

try:
    window = xbmcgui.Window(10000)
    user_status = json_fn.loads(window.getProperty("hdfull_user_status"))
    sid = window.getProperty("hdfull_sid")
    js_data = window.getProperty("hdfull_js_data")
    data_js = window.getProperty("hdfull_data_js")
    just_logout = window.getProperty("hdfull_just_logout")
    preferred_proxy_ip = window.getProperty("hdfull_preferred_proxy_ip")
except:
    user_status = {}
    sid = ''
    js_data = ''
    data_js = ''
    just_logout = ''
    preferred_proxy_ip = ''
    window.setProperty("hdfull_user_status", json_fn.dumps(user_status))
    window.setProperty("hdfull_sid", sid)
    window.setProperty("hdfull_js_data", js_data)
    window.setProperty("hdfull_data_js", data_js)
    window.setProperty("hdfull_just_logout", str(just_logout))
    window.setProperty("hdfull_preferred_proxy_ip", str(preferred_proxy_ip))


def check_login_status(data):
    global account, sid
    
    if not isinstance(data, str):
        return account
    if not data:
        return False
    
    _logged = 'id="header-signout" href="/logout"'
    
    if _logged in data:
        account = True
        if scrapertools.find_single_match(data, patron_sid):
            sid = urllib.quote(scrapertools.find_single_match(data, patron_sid))
            if window: window.setProperty("hdfull_sid", sid)
        if not config.get_setting("logged", channel=canonical['channel']):
            config.set_setting("logged", account, channel=canonical['channel'])
        return account
    
    account = False
    config.set_setting("logged", account, channel=canonical['channel'])
    sid = ''
    if window: window.setProperty("hdfull_sid", sid)
    
    return account

def verify_credentials(force_login=True, force_check=True):
    global account, credentials_req, user_, pass_, sid, user_status

    credentials = True if user_ and pass_ else False
    if not credentials:
        account = False
        config.set_setting("logged", account, channel=canonical['channel'])
        sid = ''
        if window: window.setProperty("hdfull_sid", sid)
        user_status = {}
        if window: window.setProperty("hdfull_user_status", json_fn.dumps(user_status))
        logger.info('NO LOGIN credentials', force=True)
        
        if credentials_req and force_check:
            help_window.show_info('hdfull_login', wait=True)
            settingCanal(Item)

            try:
                user_ = urllib.quote_plus(config.get_setting('hdfulluser', channel=canonical['channel'], default=''))
                pass_ = urllib.quote_plus(config.get_setting('hdfullpassword', channel=canonical['channel'], default=''))
            except:
                from core import filetools
                setting = filetools.read(filetools.join(config.get_data_path(), 'settings_channels', 'hdfull_data.json'), silent=True)
                if setting:
                    setting = base64.b64encode(setting.encode('utf-8')).decode('utf-8')
                else:
                    setting = 'VACIO'
                logger.error('Type: User: %s; Password: %s; %s' % (str(type(config.get_setting('hdfulluser', 
                                                                   channel=canonical['channel'], default=''))), 
                                                                   str(type(config.get_setting('hdfullpassword', 
                                                                   channel=canonical['channel'], default=''))), setting))
                user_ = ''
                pass_ = ''
                account = False
                config.set_setting('hdfulluser', user_, channel=canonical['channel'])
                config.set_setting('hdfullpassword', pass_, channel=canonical['channel'])
                config.set_setting('logged', account, channel=canonical['channel'])

            credentials = True if user_ and pass_ else False
            if credentials and force_login: login()
            
            if not credentials:
                if not _silence:
                    platformtools.dialog_notification("Falta usuario o contraseña", 
                                                      "Revise sus datos en la configuración del canal",
                                                      sound=False)
                credentials_req = False
                logger.info('NO credentials for LOGIN', force=True)

    return credentials

def check_user_status(reset=False, hide_infobox=True):
    global user_status

    if reset:
        user_status = {}
        if window: window.setProperty("hdfull_user_status", json_fn.dumps(user_status))
        logger.info('User_Status RESETEADO', force=True)
    if not user_status and account:
        if window: window.setProperty("hdfull_user_status", json_fn.dumps({}))

        user_status = agrupa_datos(urlparse.urljoin(host, 'a/status/all'), json=True, hide_infobox=hide_infobox, 
                                   force_check=False, force_login=False, cf_no_blacklist=True)
        if user_status:
            if window: window.setProperty("hdfull_user_status", json_fn.dumps(user_status))
            logger.info('User_Status DESCARGADO', force=True)
        else:
            logger.error('User_Status ERROR en DESCARGA')
    
    return user_status

def login(data='', alfa_s=False, force_check=True, retry=False):
    global sid, account

    if data:
        sid = urllib.quote(scrapertools.find_single_match(data, patron_sid))
        if window: window.setProperty("hdfull_sid", sid)
    
    logger.info('Data: %s; SID: %s; Account: %s; Check: %s; Retry: %s' \
                % (True if data else False, True if sid else False, account, force_check, retry), force=True)

    if not data or not sid or not account:
        data = agrupa_datos(urlparse.urljoin(host, 'login'), referer=False, force_check=False, 
                            force_login=False, hide_infobox=True if not retry else None, cf_no_blacklist=True)
        sid = urllib.quote(scrapertools.find_single_match(data, patron_sid))
        if window: window.setProperty("hdfull_sid", sid)

    if check_login_status(data):
        check_user_status()
        logger.info('LOGGED IN', force=True)
        return True
    elif not verify_credentials(force_login=False, force_check=force_check):
        return False
    else:
        host_alt = host
        sid = urllib.quote(scrapertools.find_single_match(data, patron_sid))
        if window: window.setProperty("hdfull_sid", sid)
        if not sid:
            if not retry:
                if proxy__:
                    if 'ProxyWeb' in page.proxy__: 
                        preferred_proxy_ip = ''
                        if window: window.setProperty("hdfull_preferred_proxy_ip", str(preferred_proxy_ip))
                    else:
                        config.set_setting('proxy_addr', '')
                        config.set_setting('proxy_CF_addr', '')
                logout(Item())
                logger.error('NO SID: RETRY: %s' % str(data))
                return login(force_check=force_check, retry=True)
            logger.error('NO SID: %s' % str(data))
            return False
        post = '__csrf_magic=%s&username=%s&password=%s&action=login' % (sid, user_, pass_)
        
        new_data = agrupa_datos(urlparse.urljoin(host, 'a/login'), post=post, referer=urlparse.urljoin(host, 'login'), 
                                force_check=False, json=True, force_login=False, hide_infobox=True if not retry else None, 
                                cf_no_blacklist=True if data else False, retries_cloudflare=1)

        if host not in host_alt:
            logger.info('Cambio de HOST: de %s a %s', (host, host_alt))
            return login(alfa_s=alfa_s, force_check=force_check)

        if isinstance(new_data, dict) and new_data.get("status", "") == "OK":
            sid = ''
            if window: window.setProperty("hdfull_sid", sid)
            new_data = agrupa_datos(urlparse.urljoin(host, 'login'), referer=False, force_check=False, 
                                    force_login=False, hide_infobox=True, cf_no_blacklist=True)
            if scrapertools.find_single_match(data, patron_sid):
                sid = urllib.quote(scrapertools.find_single_match(data, patron_sid))
                if window: window.setProperty("hdfull_sid", sid)
                account = True
                if not config.get_setting("logged", channel=canonical['channel']):
                    config.set_setting("logged", account, channel=canonical['channel'])
                logger.info('Just LOGGED', force=True)
                check_user_status(reset=True)
                return True
        
        logger.info('Error on LOGIN: %s' % str(new_data), force=True)
        if not _silence:
            platformtools.dialog_notification("No se pudo realizar el login",
                                             "Revise sus datos en la configuración del canal",
                                             sound=False)
        return False

def logout(item):
    global just_logout, account, user_status, sid, js_data, data_js, user_, pass_
    logger.info('LOGGED OFF', force=True)
    
    # Logoff en la web
    data = agrupa_datos(urlparse.urljoin(host, 'logout'), referer=host, force_check=False, force_login=False, 
                        hide_infobox=True, cf_no_blacklist=True, retries_cloudflare=1)
    
    # Borramos cookies de hdfull
    domain = urlparse.urlparse(host).netloc
    dict_cookie = {"domain": domain, 'expires': 0}
    httptools.set_cookies(dict_cookie)
    dict_cookie = {"domain": '.'+domain, 'expires': 0}
    httptools.set_cookies(dict_cookie)

    account = False
    config.set_setting("logged", account, channel=canonical['channel'])
    user_status = {}
    sid = ''
    js_data = ''
    data_js = ''
    just_logout = True
    if window:
        window.setProperty("hdfull_user_status", json_fn.dumps(user_status))
        window.setProperty("hdfull_sid", sid)
        window.setProperty("hdfull_js_data", js_data)
        window.setProperty("hdfull_data_js", data_js)
        window.setProperty("hdfull_just_logout", str(just_logout))

    # Avisamos, si nos dejan
    if not _silence:
        platformtools.dialog_notification("Deslogueo completo", 
                                          "Verifique su cuenta",
                                          sound=False,)
    if item.refresh: platformtools.itemlist_refresh()

    return item

def agrupa_datos(url, post=None, referer=True, json=False, proxy=True, forced_proxy=None, 
                 proxy_retries=1, force_check=False, force_login=True, alfa_s=False, hide_infobox=False, 
                 timeout=10, cf_no_blacklist=False, retries_cloudflare=canonical.get('retries_cloudflare', 0)):
    global account, sid, user_status, preferred_proxy_ip, proxy__
    forced_proxy_retry = canonical.get('forced_proxy_ifnot_assistant', '') or 'ProxyCF'

    if host_save != host: url = url.replace(host_save, host)
    
    headers = {'Referer': host}
    if 'episodes' in url or 'buscar' in url:
        headers['Referer'] += 'episodios'
    
    if not referer:
        headers.pop('Referer')
    # if cookie:
    #     headers.update('Cookie:' 'language=es')
    if isinstance(referer, str):
        headers.update({'Referer': referer})
    
    if preferred_proxy_ip:
        canonical['preferred_proxy_ip'] = preferred_proxy_ip

    page = httptools.downloadpage(url, post=post, headers=headers, ignore_response_code=True, timeout=timeout, 
                                  canonical=canonical, proxy=proxy, forced_proxy=forced_proxy, hide_infobox=hide_infobox, 
                                  proxy_retries=proxy_retries, alfa_s=alfa_s, forced_proxy_retry=forced_proxy_retry, 
                                  cf_no_blacklist=cf_no_blacklist, retries_cloudflare=retries_cloudflare)

    if page.proxy__:
        if 'ProxyWeb' in page.proxy__: 
            preferred_proxy_ip = canonical['preferred_proxy_ip'] = page.proxy__.split('|')[2] \
                                 if page.code in httptools.SUCCESS_CODES + httptools.REDIRECTION_CODES else ''
            if window: window.setProperty("hdfull_preferred_proxy_ip", str(preferred_proxy_ip))
        else:
            canonical['CF_if_NO_assistant'] = False
    if page.sucess and page.host and host_save not in page.host:
        account = False
        config.set_setting("logged", account, channel=canonical['channel'])
        sid = ''
        if window: window.setProperty("hdfull_sid", sid)
        user_status = {}
        if window: window.setProperty("hdfull_user_status", json_fn.dumps(user_status))
        url = page.url_new
        return agrupa_datos(url, post=post, referer=referer, proxy=proxy, forced_proxy=forced_proxy, 
                            proxy_retries=proxy_retries, json=json, force_check=force_check, 
                            force_login=True, alfa_s=alfa_s, hide_infobox=hide_infobox, timeout=timeout, 
                            retries_cloudflare=retries_cloudflare, cf_no_blacklist=cf_no_blacklist)

    if not page.sucess:
        preferred_proxy_ip = canonical['preferred_proxy_ip'] = ''
        if window: window.setProperty("hdfull_preferred_proxy_ip", str(preferred_proxy_ip))
        account = False
        config.set_setting("logged", account, channel=canonical['channel'])
        config.set_setting("current_host", '', channel=canonical['channel'])
        sid = ''
        if window: window.setProperty("hdfull_sid", sid)
        user_status = {}
        if window: window.setProperty("hdfull_user_status", json_fn.dumps(user_status))
        return {} if json else ''

    if json:
        return page.json
    
    if (page.data or (not page.data and not post)) and not 'application' in page.headers['Content-Type'] and not check_login_status(page.data):
        res = False
        if force_login and not 'login' in url and not 'logout' in url:
            res = login(page.data)
        if not res:
            return {} if json else page.data
        else:
            return agrupa_datos(url, post=post, referer=referer, proxy=proxy, forced_proxy=forced_proxy, 
                                proxy_retries=proxy_retries, json=json, force_check=force_check, 
                                force_login=False, alfa_s=alfa_s, hide_infobox=hide_infobox, timeout=timeout, 
                                retries_cloudflare=retries_cloudflare, cf_no_blacklist=cf_no_blacklist)
    
    data = page.data
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))
    ## Agrupa los datos
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|<!--.*?-->', '', data)
    data = re.sub(r'\s+', ' ', data)
    data = re.sub(r'>\s<', '><', data)
    
    return data


def mainlist(item):
    logger.info()
    global just_logout
    
    itemlist = []
    
    verify_credentials(force_login=True)
    check_user_status(reset=True)
    #logger.debug('%s, %s, %s, %s' % (just_logout, account, sid, user_status))
    if not just_logout and (not account or not sid or not user_status): login()
    if just_logout:
        just_logout = ''
        if window: window.setProperty("hdfull_just_logout", str(just_logout))

    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, action="menupeliculas", title="Películas", url=host,
                         thumbnail=get_thumb('movies', auto=True), text_bold=True))
    itemlist.append(Item(channel=item.channel, action="menuseries", title="Series", url=host,
                         thumbnail=get_thumb('tvshows', auto=True), text_bold=True))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar...",
                         thumbnail=get_thumb('search', auto=True), text_bold=True))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)
    
    if not account:
        itemlist.append(Item(channel=item.channel,  action="", url="", 
                        title="[COLOR gold]Registrate en %s y luego habilita tu cuenta[/COLOR]" % host,
                        thumbnail=get_thumb("setting_0.png")))
        itemlist.append(Item(channel=item.channel,  action="settingCanal", url="", text_bold=True,
                        title="[COLOR dodgerblue]Habilita tu cuenta para activar los items de usuario...[/COLOR]",
                        thumbnail=get_thumb("setting_0.png")))
    else:
        itemlist.append(Item(channel=item.channel, action="",  url="",
                             title="", folder=False,
                             thumbnail=get_thumb("setting_0.png")))
        
        itemlist.append(Item(channel=item.channel, action="settingCanal",  url="",
                             title="[COLOR greenyellow][B]Configurar Canal[/B][/COLOR]",
                             thumbnail=get_thumb("setting_0.png"), folder=False))

        itemlist.append(Item(channel=item.channel, action="logout", url="", folder=False, refresh=True, 
                             title="[COLOR steelblue][B]Desloguearse[/B][/COLOR]",
                             plot="Para cambiar de usuario", thumbnail=get_thumb("back.png")))
    return itemlist


def settingCanal(item):
    
    platformtools.show_channel_settings()
    if account: platformtools.itemlist_refresh()
    
    return item


def menupeliculas(item):
    logger.info()
    
    itemlist = []

    itemlist.append(
        Item(channel=item.channel, action="fichas", title="Películas Estreno",
             url=urlparse.urljoin(host, "peliculas-estreno"),
             text_bold=True, thumbnail=get_thumb('premieres', auto=True)))
    
    itemlist.append(
        Item(channel=item.channel, action="fichas", title="Últimas Películas",
             url=urlparse.urljoin(host, "peliculas"), text_bold=True,
             thumbnail=get_thumb('last', auto=True)))
    
    itemlist.append(
        Item(channel=item.channel, action="fichas", title="Películas Actualizadas",
             url=urlparse.urljoin(host, "peliculas-actualizadas"), text_bold=True,
             thumbnail=get_thumb('updated', auto=True)))
   
    itemlist.append(
        Item(channel=item.channel, action="fichas", title="Rating IMDB",
             url=urlparse.urljoin(host, "peliculas/imdb_rating"),
             text_bold=True, thumbnail=get_thumb('recomended', auto=True)))
    
    itemlist.append(
        Item(channel=item.channel, action="generos", title="Películas por Género",
             url=host, text_bold=True, type='peliculas',
             thumbnail=get_thumb('genres', auto=True)))
    
    # itemlist.append(
    #     Item(channel=item.channel, action="fichas", title="ABC",
    #          url=urlparse.urljoin(host, "peliculas/abc"), text_bold=True,
    #          thumbnail=get_thumb('alphabet', auto=True)))
    
    if account:
        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR orange][B]Vistas[/B][/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=movies&action=seen&start=-28&limit=28"),
                             thumbnail=item.thumbnail))

        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR orange][B]Favoritos[/B][/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=movies&action=favorite&start=-28&limit=28"),
                             thumbnail=item.thumbnail))
        
        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR dodgerblue][B]Pendientes[/B][/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=movies&action=pending&start=-28&limit=28"),
                             thumbnail=item.thumbnail))
        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR dodgerblue][B]Recomendadas[/B][/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=movies&action=recommended&start=-28&limit=28"),
                             thumbnail=item.thumbnail))
    return itemlist


def menuseries(item):
    logger.info()
    
    itemlist = []

    itemlist.append(
        Item(channel=item.channel, action="novedades_episodios", title="Episodios Estreno",
             url=urlparse.urljoin(host, "a/episodes?action=premiere&start=-24&limit=24&elang=ALL"), text_bold=True,
             thumbnail=get_thumb('newest', auto=True)))
    itemlist.append(
        Item(channel=item.channel, action="novedades_episodios", title="Últimos Emitidos",
             url=urlparse.urljoin(host, "a/episodes?action=latest&start=-24&limit=24&elang=ALL"), text_bold=True,
             thumbnail=get_thumb('new episodes', auto=True)))

    itemlist.append(
        Item(channel=item.channel, action="novedades_episodios", title="Episodios Anime",
             url=urlparse.urljoin(host, "a/episodes?action=anime&start=-24&limit=24&elang=ALL"), text_bold=True,
             thumbnail=get_thumb('anime', auto=True)))
    itemlist.append(
        Item(channel=item.channel, action="novedades_episodios", title="Episodios Actualizados",
             url=urlparse.urljoin(host, "a/episodes?action=updated&start=-24&limit=24&elang=ALL"), text_bold=True,
             thumbnail=get_thumb('updated', auto=True)))
    itemlist.append(
        Item(channel=item.channel, action="fichas", title="Últimas series",
             url=urlparse.urljoin(host, "series"), text_bold=True,
             thumbnail=get_thumb('last', auto=True)))
    itemlist.append(
        Item(channel=item.channel, action="fichas", title="Rating IMDB", 
             url=urlparse.urljoin(host, "series/imdb_rating"), text_bold=True,
             thumbnail=get_thumb('recomended', auto=True)))
    itemlist.append(
        Item(channel=item.channel, action="generos", title="Series por Género",
             url=host, text_bold=True, type='series',
             thumbnail=get_thumb('genres', auto=True)))
    
    itemlist.append(
        Item(channel=item.channel, action="series_abc", title="A-Z",
             text_bold=True, thumbnail=get_thumb('alphabet', auto=True)))

    #Teniendo el listado alfabetico esto sobra y necesita paginación
    #itemlist.append(Item(channel=item.channel, action="listado_series", title="Listado de todas las series",
    #                     url=host + "series/list", text_bold=True))

    if account:
        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR orange]Siguiendo[/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=shows&action=following&start=-28&limit=28"), text_bold=True,
                             thumbnail=item.thumbnail))

        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR orange]Para Ver[/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=shows&action=watch&start=-28&limit=28"), text_bold=True,
                             thumbnail=item.thumbnail))

        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR dodgerblue]Favoritas[/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=shows&action=favorite&start=-28&limit=28"), text_bold=True,
                             thumbnail=item.thumbnail))

        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR dodgerblue]Pendientes[/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=shows&action=pending&start=-28&limit=28"), text_bold=True,
                             thumbnail=item.thumbnail))

        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR dodgerblue]Recomendadas[/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=shows&action=recommended&start=-28&limit=28"), text_bold=True,
                             thumbnail=item.thumbnail))
                             
        itemlist.append(Item(channel=item.channel, action="items_usuario",
                             title="[COLOR dodgerblue]Finalizadas[/COLOR]",
                             url=urlparse.urljoin(host, "a/my?target=shows&action=seen&start=-28&limit=28"), text_bold=True,
                             thumbnail=item.thumbnail))
    
    return itemlist


def search(item, texto):
    logger.info()
    
    try:
        if not account or not sid or not user_status: login()
        if not sid: return []
        item.extra = '__csrf_magic=%s&menu=search&query=%s' % (sid, texto)
        item.title = "Buscar..."
        item.url = urlparse.urljoin(host, "buscar")
        item.texto = texto
        
        return fichas(item)
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def series_abc(item):
    logger.info()

    itemlist = []
    page = config.get_setting('pagination_abc', channel=canonical['channel'])
    page = 0 if page else ''
    az = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for l in az:
        itemlist.append(
            Item(channel=item.channel, action='fichas', title=l, 
                 url= urlparse.urljoin(host, "series/abc/%s" %  l.replace('#', '9')),
                 thumbnail=item.thumbnail, page=page, text_bold=True))

    return itemlist


def items_usuario(item):
    logger.info()
    
    itemlist = []
    contentType = 'movie'
    
    ## Carga estados
    status = check_user_status()
    
    ## Fichas usuario
    url = item.url.split("?")[0]
    post = item.url.split("?")[1]
    old_start = scrapertools.find_single_match(post, 'start=([^&]+)&')
    limit = scrapertools.find_single_match(post, 'limit=(\d+)')
    start = "%s" % (int(old_start) + int(limit))
    post = post.replace("start=" + old_start, "start=" + start)
    next_page = url + "?" + post
    
    ## Carga las fichas de usuario
    fichas_usuario = agrupa_datos(url, post=post, json=True)
    if host_save != host: next_page = next_page.replace(host_save, host)
    
    for ficha in fichas_usuario:
        plot_extend = ''
        title= ''
        infoLabels = item.infoLabels
        try:
            if ficha.get('title', {}) and isinstance(ficha.get('title', {}), dict):
                title = ficha.get('title', {}).get('es', '').strip() or ficha.get('title', {}).get('en', '').strip()
            elif ficha.get('show_title', {}) and isinstance(ficha.get('show_title', {}), dict):
                title = ficha.get('show_title', {}).get('es', '').strip() or ficha.get('show_title', {}).get('en', '').strip()
            else:
                title = ''
        except:
            title = 'Error en FICHA de usuario, Title'
            logger.error('%s: %s en %s' % (title, str(ficha), str(fichas_usuario)))
            itemlist.append(Item(channel=item.channel, action='', title=title + ' - Enviar LOG'))
            continue
        try:
            if not PY3: title = title.encode('utf-8')
        except:
            pass
        show = title
        thumbnail = urlparse.urljoin(host, "thumbs/" + (ficha.get('thumbnail', '') or ficha.get('thumb', '')))
        thumbnail += '|User-Agent=%s' % httptools.get_user_agent()
        try:
            url = urlparse.urljoin(host, 'serie/' + ficha['permalink']) + "###" + ficha['id'] + ";1"
            action = "seasons"
            contentType = 'tvshow'
            str_ = get_status(status, 'shows', ficha['id'])
            if "show_title" in ficha:
                action = "findvideos"
                contentType = 'episode'
                serie = ''
                if ficha.get('show_title', {}) and isinstance(ficha.get('show_title', {}), dict):
                    serie = ficha.get('show_title', {}).get('es', '').strip() or ficha.get('show_title', {}).get('en', '').strip()
                if serie: show = serie
                temporada = ficha['season']
                episodio = ficha['episode']
                serie = "[COLOR whitesmoke]" + serie + "[/COLOR]"
                if len(episodio) == 1: episodio = '0' + episodio
                try:
                    title = temporada + "x" + episodio + " - " + serie + ": " + title
                except:
                    title = temporada + "x" + episodio + " - " + serie.decode('iso-8859-1') + ": " + title.decode(
                        'iso-8859-1')
                url = urlparse.urljoin(host, 'serie/' + ficha[
                    'permalink'] + '/temporada-' + temporada + '/episodio-' + episodio) + "###" + ficha['id'] + ";3"
                if str_ != "": 
                    title += str_
                    plot_extend = str_
                else:
                    plot_extend = '[COLOR orange](Siguiendo)[/COLOR]'
                try:
                    infoLabels.update({'season': int(temporada), 'episode': int(episodio), 'playcount': 1 if 'Visto' in str_ else 0})
                except:
                    infoLabels.update({'season': 1, 'episode': 1, 'playcount': 1 if 'Visto' in str_ else 0})
                infoLabels = scrapertools.episode_title(title, infoLabels)
                infoLabels['tvshowtitle'] = show
            
            else:
                if str_ != "": 
                    title += str_
                    plot_extend = str_
            
            itemlist.append(
                    Item(channel=item.channel, action=action, title=title, plot_extend=plot_extend, 
                        url=url, thumbnail=thumbnail, contentType=contentType, infoLabels=infoLabels, 
                        contentSerieName=show, text_bold=True))
        except:
            infoLabels.update({'year': '-'})
            url = urlparse.urljoin(host, 'pelicula/' + ficha.get('perma', '')) + "###" + ficha.get('id', 0) + ";2"
            str_ = get_status(status, 'movies', ficha.get('id', 0))
            if str_ != "": 
                title += str_
                plot_extend = str_
                plot_extend = plot_extend.replace('[COLOR blue](Visto)[/COLOR]', '')
                infoLabels['playcount'] = 1 if 'Visto' in str_ else 0
            
            itemlist.append(
                Item(channel=item.channel, action="findvideos", title=title, plot_extend=plot_extend, 
                     contentTitle=show, url=url, thumbnail=thumbnail, contentType=contentType, 
                     text_bold=True, infoLabels=infoLabels))
    
    if len(itemlist) >= int(limit):
        itemlist.append(
            Item(channel=item.channel, action="items_usuario", title=">> Página siguiente", url=next_page, text_bold=True))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    
    return itemlist


'''def listado_series(item):
    logger.info()
    itemlist = []
    data = agrupa_datos(item.url)
    patron = '<div class="list-item"><a href="([^"]+)"[^>]+>([^<]+)</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        url = scrapedurl + "###0;1"
        itemlist.append(
            Item(channel=item.channel, action="seasons", title=scrapedtitle, contentTitle=scrapedtitle, url=url,
                 contentSerieName=scrapedtitle, contentType="tvshow"))
    return itemlist'''


def fichas(item):
    logger.info()
    
    itemlist = []
    or_matches = ""
    textoidiomas=''

    ## Carga estados
    status = check_user_status()
    
    if host_save != host: item.url = item.url.replace(host_save, host)

    if item.title == "Buscar...":
        data = agrupa_datos(item.url, post=item.extra)
        s_p = scrapertools.find_single_match(data, '<h3 class="section-title">(.*?)<div id="footer-wrapper">').split(
            '<h3 class="section-title">')
        if len(s_p) == 1:
            data = s_p[0]
            if 'Lo sentimos</h3>' in s_p[0]:
                return [Item(channel=item.channel, title="[COLOR gold]HDFull:[/COLOR] [COLOR aqua]" + item.texto.replace('%20',
                                                                                       ' ') + "[/COLOR] sin resultados")]
        else:
            data = s_p[0] + s_p[1]
    elif 'series/abc' in item.url:
        data = agrupa_datos(item.url, referer=item.url)
    else:
        data = agrupa_datos(item.url)
    if host_save != host: item.url = item.url.replace(host_save, host)

    data = re.sub(
        r'<div class="span-6[^<]+<div class="item"[^<]+' + \
        '<a href="([^"]+)"[^<]+' + \
        '<img.*?src="([^"]+)".*?' + \
        '<div class="left"(.*?)</div>' + \
        '<div class="right"(.*?)</div>.*?' + \
        'title="([^"]+)".*?' + \
        'onclick="setFavorite.\d, (\d+),',
        r"'url':'\1';'image':'\2';'langs':'\3';'rating':'\4';'title':\5;'id':'\6';",
        data
    )
    patron = "'url':'([^']+)';'image':'([^']+)';'langs':'([^']+)';'rating':'([^']+)';'title':([^;]+);'id':'([^']+)';"
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    if item.page != '':
        or_matches = matches
        matches = matches[item.page:item.page + 40]
    
    for scrapedurl, scrapedthumbnail, scrapedlangs, scrapedrating, scrapedtitle, scrapedid in matches:

        infoLabels = dict()
        plot_extend = ''
        thumbnail = scrapedthumbnail.replace('tthumb/130x190', 'thumbs')
        thumbnail += '|User-Agent=%s' % httptools.get_user_agent()
        language = ''
        title = scrapedtitle.strip()
        show = title

        # Valoración
        if scrapedrating != ">" and not unify:
            valoracion = re.sub(r'><[^>]+>(\d+)<b class="dec">(\d+)</b>', r'\1,\2', scrapedrating)
            title += " [COLOR greenyellow](%s)[/COLOR]" % valoracion
        
        # Idiomas
        if scrapedlangs != ">":
            textoidiomas, language = extrae_idiomas(scrapedlangs)

            if show_langs:
                title += " [COLOR darkgrey]%s[/COLOR]" % textoidiomas
        
        url = urlparse.urljoin(item.url, scrapedurl)
        
        # Acción para series/peliculas
        if "/serie" in url or "/tags-tv" in url:
            action = "seasons"
            url += "###" + scrapedid + ";1"
            type = "shows"
            contentType = "tvshow"
        else:
            action = "findvideos"
            url += "###" + scrapedid + ";2"
            type = "movies"
            contentType = "movie"
            infoLabels['year']= '-'
        
        # items usuario en titulo (visto, pendiente, etc)
        if account:
            str_ = get_status(status, type, scrapedid)
            if str_ != "": 
                title += str_
                plot_extend = str_
                plot_extend = plot_extend.replace('[COLOR blue](Visto)[/COLOR]', '')
                infoLabels['playcount'] = 1 if 'Visto' in str_ else 0

        # Muesta tipo contenido tras busqueda
        if item.title == "Buscar...":
            bus = host[-4:]
            #Cuestiones estéticas (TODO probar unify)
            c_t = "darkgrey" 
            
            tag_type = scrapertools.find_single_match(url, '%s([^/]+)/' %bus)
            if tag_type == 'pelicula':
                c_t = "steelblue"
            title += " [COLOR %s](%s)[/COLOR]" % (c_t, tag_type.capitalize())

        if "/serie" in url or "/tags-tv" in url:
            itemlist.append(
                Item(channel=item.channel, action=action, title=title, url=url, plot_extend=plot_extend, 
                     contentSerieName=show, text_bold=True, contentType=contentType,
                     language=language, infoLabels=infoLabels, thumbnail=thumbnail,
                     context=filtertools.context(item, list_language, list_quality)))
        else:
            itemlist.append(
                Item(channel=item.channel, action=action, title=title, url=url, plot_extend=plot_extend, 
                     text_bold=True, contentTitle=show, contentType=contentType, 
                     language=language, infoLabels=infoLabels, thumbnail=thumbnail))
    
    ## Paginación
    next_page_url = scrapertools.find_single_match(data, '<a\s*href="([^"]+)">.raquo;</a>')
    if next_page_url:
        itemlist.append(Item(channel=item.channel, action="fichas", title=">> Página siguiente",
                             url=urlparse.urljoin(item.url, next_page_url), text_bold=True))
        
        itemlist.append(Item(channel=item.channel, action="get_page_num", title=">> Ir a Página...",
                             url=urlparse.urljoin(item.url, next_page_url), text_bold=True,
                             thumbnail=get_thumb('add.png'), text_color='turquoise'))

    elif item.page:
        if item.page + 40 < len(or_matches):
            itemlist.append(item.clone(page=item.page + 40, title=">> Página siguiente",
                                       text_bold=True, text_color="blue"))
    
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    
    return itemlist


def seasons(item):
    logger.info()
    
    id = "0"
    itemlist = []
    infoLabels = item.infoLabels
    
    ## Carga estados
    status = check_user_status()
    
    url_targets = item.url
    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        item.url = item.url.split("###")[0]
    
    data = agrupa_datos(item.url, force_check=False, force_login=False)
    if host_save != host: 
        item.url = item.url.replace(host_save, host)
        url_targets= url_targets.replace(host_save, host)
    
    if account:
        str_ = get_status(status, "shows", id)
        infoLabels['mediatype'] = 'season'
        #TODO desenredar todo el lio este
        if str_ != "" and item.category != "Series" and "XBMC" not in item.title:
            platformtools.itemlist_refresh()
            title = str_.replace('steelblue', 'darkgrey').replace('[COLOR orange](Siguiendo)[/COLOR]', '[COLOR blue](Abandonar)[/COLOR]').replace('Siguiendo', 'Abandonar')

            itemlist.append(Item(channel=item.channel, action="set_status__", title=title, url=url_targets,
                                 thumbnail=item.thumbnail, contentSerieName=item.contentSerieName, 
                                 infoLabels=infoLabels, folder=True))
        elif item.category != "Series" and "XBMC" not in item.title:
            
            title = " [COLOR steelblue][B]( Seguir )[/B][/COLOR]"
            itemlist.append(Item(channel=item.channel, action="set_status__", title=title, url=url_targets,
                                 thumbnail=item.thumbnail, contentSerieName=item.contentSerieName, 
                                 infoLabels=infoLabels, folder=True))
        
    sid = scrapertools.find_single_match(data, "<\s*script\s*>var\s*sid\s*=\s*'\s*(\d+)\s*'")
    
    patron = 'itemprop="season".*?<a\s*href=\'.*?/temporada-(\d+).*?'
    patron += 'alt="([^"]+)"\s*src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    matches = find_hidden_seasons(item, matches, sid)
    if not matches:
        logger.debug('PATRON: %s' % patron)
        logger.debug('DATA: %s' % data)

    for ssid, scrapedtitle, scrapedthumbnail in matches:
        plot_extend = ''
        if ssid == '0':
            scrapedtitle = "Especiales"
        thumbnail = scrapedthumbnail.replace('tthumb/130x190', 'thumbs')
        thumbnail += '|User-Agent=%s' % httptools.get_user_agent()
        infoLabels['mediatype'] = 'season'
        if str_: plot_extend = str_
        
        itemlist.append(
                Item(channel=item.channel, action="episodesxseason", title=scrapedtitle,
                     url=item.url, thumbnail=thumbnail, sid=sid, text_bold=True, plot_extend=plot_extend, 
                     contentSerieName=item.contentSerieName, contentSeason=ssid, 
                     infoLabels=infoLabels, contentType='season'))

    if config.get_videolibrary_support() and len(itemlist) > 0:
        infoLabels['mediatype'] = 'tvshow'
        itemlist.append(Item(channel=item.channel, title="[COLOR greenyellow]Añadir esta serie a la videoteca[/COLOR]",
                             action="add_serie_to_library", url=item.url, text_bold=True, extra="episodios",
                             contentSerieName=item.contentSerieName, infoLabels=infoLabels
                             ))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if item.library_playcounts and item.action == 'get_seasons':                # Es actualización background de videoteca
        if not account or not sid or not user_status: login(force_check=False)
    else:
        if not account or not sid or not user_status: login()
    
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()
    
    itemlist = []
    url = urlparse.urljoin(host, "a/episodes")
    sid = item.sid
    ssid = item.contentSeason

    #si hay cuenta
    status = check_user_status()
    
    post = "action=season&start=0&limit=0&show=%s&season=%s" % (sid, ssid)
    #episodes = httptools.downloadpage(url, post=post).json
    episodes = agrupa_datos(url, post=post, json=True, force_check=False, force_login=False)
    
    for episode in episodes:

        title = ''
        plot_extend = ''
        infoLabels = item.infoLabels.copy()
        language = episode.get('languages', '')
        temporada = episode.get('season', '1')
        episodio = episode.get('episode', '0')

        #Fix para thumbs
        thumb = episode.get('thumbnail', '')
        if not thumb:
            thumb = episode['show'].get('thumbnail', '')
        ua = httptools.get_user_agent()
        thumbnail = urlparse.urljoin(host, "thumbs/%s|User-Agent=%s" % (thumb, ua))
        
        try:
            infoLabels['season'] = int(temporada)
            infoLabels['episode'] = int(episodio)
        except:
            infoLabels['season'] = 1
            infoLabels['episode'] = 1

        if len(episodio) == 1: episodio = '0' + episodio
        
        #Idiomas
        texto_idiomas, langs = extrae_idiomas(language, list_language=True)

        if language != "[]" and show_langs and not unify:
            idiomas = "[COLOR darkgrey]%s[/COLOR]" % texto_idiomas
        
        else:
            idiomas = ""
        
        if episode.get('title', {}) and isinstance(episode.get('title', {}), dict):
            title = episode['title'].get('es', '') or episode['title'].get('en', '')
        infoLabels = scrapertools.episode_title(title, infoLabels)
        if not title: title = "Episodio " + episodio
        
        serie = item.contentSerieName
        
        title = '%sx%s: [COLOR greenyellow]%s[/COLOR] %s' % (temporada, episodio, title.strip(), idiomas)
        if account:
            str_ = get_status(status, 'episodes', episode['id'])
            if str_ != "":
                title += str_
            infoLabels.update({'playcount': 1 if 'Visto' in str_ else 0})
        
        url = urlparse.urljoin(host, 'serie/' + episode[
            'permalink'] + '/temporada-' + temporada + '/episodio-' + episodio) + "###" + episode['id'] + ";3"
        
        itemlist.append(item.clone(action="findvideos", title=title, url=url, plot_extend=item.plot_extend, 
                             contentType="episode", language=langs, text_bold=True,
                             infoLabels=infoLabels, thumbnail=thumbnail))

    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    return itemlist


def novedades_episodios(item):
    logger.info()
    
    itemlist = []
    ## Carga estados
    status = check_user_status()
    
    ## Episodios
    url = item.url.split("?")[0]
    post = item.url.split("?")[1]
    old_start = scrapertools.find_single_match(post, 'start=([^&]+)&')
    start = "%s" % (int(old_start) + 24)
    post = post.replace("start=" + old_start, "start=" + start)
    next_page = url + "?" + post
    episodes = agrupa_datos(url, post=post, json=True)
    if host_save != host: next_page = next_page.replace(host_save, host)

    for episode in episodes:
        
        title_from_channel = ''
        # Fix para thumbs
        thumb = episode['show'].get('thumbnail', '')
        if not thumb:
            thumb = episode.get('thumbnail', '')
        ua = httptools.get_user_agent()
        thumbnail = urlparse.urljoin(host, "thumbs/%s|User-Agent=%s" % (thumb, ua))
        
        temporada = episode['season']
        episodio = episode['episode']
        #if len(episodio) == 1: episodio = '0' + episodio
        
        # Idiomas
        language = episode.get('languages', '[]')
        texto_idiomas, langs = extrae_idiomas(language, list_language=True)
        
        if language != "[]" and show_langs and not unify:
            idiomas = "[COLOR darkgrey]%s[/COLOR]" % texto_idiomas
        
        else:
            idiomas = ""

        # Titulo serie en español, si no hay, en inglés
        cont_en = episode['show']['title'].get('en', '').strip()
        contentSerieName = episode['show'].get('es', cont_en).strip()


        if episode['title']:
            try:
                title = episode['title']['es'].strip()
            except:
                try:
                    title = episode['title']['en'].strip()
                except:
                    title = ''
        title_from_channel = title
        if len(title) == 0: title = "Episodio " + episodio
        
        title = '%s %sx%s: [COLOR greenyellow]%s[/COLOR] %s' % (contentSerieName,
                 temporada, episodio, title, idiomas)

        str_ = ''
        if account:
            str_ = get_status(status, 'episodes', episode['id'])
            if str_ != "": title += str_

        url = urlparse.urljoin(host, 'serie/' + episode[
            'permalink'] + '/temporada-' + temporada + '/episodio-' + episodio) + "###" + episode['id'] + ";3"
        try:
            temporada = int(temporada)
            episodio = int(episodio)
        except:
            temporada = 1
            episodio = 1
        
        infoLabels={'season': temporada, 'episode': episodio, 'playcount': 1 if 'Visto' in str_ else 0}
        infoLabels = scrapertools.episode_title(title_from_channel, infoLabels)
        
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, 
                 infoLabels=infoLabels, 
                 contentSerieName=contentSerieName, url=url, thumbnail=thumbnail, 
                 contentType="episode", language=langs, text_bold=True,
                 ))
    
    if len(itemlist) == 24:
        itemlist.append(
            Item(channel=item.channel, action="novedades_episodios", title=">> Página siguiente", 
                url=next_page, text_bold=True))

    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    
    return itemlist


def generos(item):
    logger.info()
    
    itemlist = []
    
    data = agrupa_datos(item.url)
    if host_save != host: item.url = item.url.replace(host_save, host)
    tipo = '(?:series|tv-shows)'
    if item.type == 'peliculas':
        tipo = '(?:peliculas|movies)'

    data = scrapertools.find_single_match(data, 
        '<li class="dropdown"><a href="/%s"(.*?)</ul>' % tipo)
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for scrapedurl, scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = item.thumbnail
        plot = ""
        itemlist.append(Item(channel=item.channel, action="fichas", title=title,
                             url=url, text_bold=True, thumbnail=thumbnail))
    return itemlist


def findvideos(item):
    logger.info()
    global js_data, data_js
    
    itemlist = []
    it1 = []
    it2 = []
    str_ = ''
    title = ''
    
    if not account or not sid or not user_status: login()

    ## Carga estados
    status = check_user_status(reset=True)
    
    url_targets = item.url

    ## Vídeos
    id = ""
    type = ""
    calidad = ""
    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        item.url = item.url.split("###")[0]

    if type == "2" and status and item.category != "Cine":
        str_ = get_status(status, "movies", id)
        title = " [COLOR orange][B]( Agregar a Favoritos )[/B][/COLOR]"
    elif type == "3" and status and item.category != "Series" and "XBMC" not in item.title:
        str_ = get_status(status, "episodes", id)
    if str_ or title:
        if "Favorito" in str_:
            title = " [COLOR darkgrey][B]( Quitar de Favoritos )[/B][/COLOR]"
        elif "Visto" in str_:
            title = str_

        it1.append(Item(channel=item.channel, action="set_status__", title=title, url=url_targets,
                        infoLabels=item.infoLabels, language=item.language, folder=True, unify=False))

        if not 'playcount' in item.infoLabels: item.infoLabels['playcount'] = 1 if 'Visto' in str_ else 0
        item.plot_extend = item.plot_extend.replace('[COLOR blue](Visto)[/COLOR]', '')
    
    if not js_data or not data_js:
        window.setProperty("hdfull_js_data", '')
        window.setProperty("hdfull_data_js", '')
        
        js_data = agrupa_datos(js_url, hide_infobox=True)
        if js_data:
            if window: window.setProperty("hdfull_js_data", js_data)
            logger.info('Js_data DESCARGADO', force=True)
        else:
            logger.error('Js_data ERROR en DESCARGA')
        
        data_js = agrupa_datos(data_js_url, hide_infobox=True)
        if data_js:
            if window: window.setProperty("hdfull_data_js", data_js)
            logger.info('Data_js DESCARGADO', force=True)
        else:
            logger.error('Data_js ERROR en DESCARGA')
    
    provs = alfaresolver.jhexdecode(data_js)
    
    if host_save != host: item.url = item.url.replace(host_save, host)
    data = agrupa_datos(item.url, force_check=True, force_login=True)
    if host_save != host: 
        item.url = item.url.replace(host_save, host)
        url_targets = url_targets.replace(host_save, host)
    try:
        data_decrypt = jsontools.load(alfaresolver.obfs(data, js_data))
    except:
        logger.error(traceback.format_exc())
        return []
    
    infolabels = item.infoLabels
    year = scrapertools.find_single_match(data, '<span>Año:\s*</span>.*?(\d{4})')
    infolabels["year"] = year
    matches = []
    
    for match in data_decrypt:
        if match['provider'] in provs:
            try:
                embed = provs[match['provider']]['t']
                url = provs[match['provider']]['d'] % match['code']
                matches.append([match['lang'], match['quality'], url, embed])
            except:
                pass

    for idioma, calidad, url, embed in matches:
        if embed == 'd':
            option = "Descargar"
            option1 = 2
        else:
            option = "Ver"
            option1 = 1

        idioma = IDIOMAS.get(idioma.lower(), idioma)
        if not PY3:
            calidad = unicode(calidad, "utf8").upper().encode("utf8")
        title = option + ": %s [COLOR greenyellow](" + calidad + ")[/COLOR] [COLOR darkgrey](" + idioma + ")[/COLOR]"
        plot = item.plot
        if not item.plot:
            plot = scrapertools.find_single_match(data,
                                            '<meta property="og:description" content="([^"]+)"')
            plot = scrapertools.htmlclean(plot)
            plot = re.sub('^.*?y latino', '', plot)
        fanart = scrapertools.find_single_match(data, '<div style="background-image.url. ([^\s]+)')
        if account:
            url += "###" + id + ";" + type
        it2.append(
            Item(channel=item.channel, action="play", title=title, url=url,
                 plot=plot, fanart=fanart, contentSerieName=item.contentSerieName, 
                 infoLabels=item.infoLabels, language=idioma, plot_extend=item.plot_extend, 
                 contentType=item.contentType, tipo=option, tipo1=option1,
                 quality=calidad))

    it2 = servertools.get_servers_itemlist(it2, lambda i: i.title % i.server.capitalize())
    it2.sort(key=lambda it: (it.tipo1, it.language, it.server))
    for item in it2:
        if "###" not in item.url:
            item.url += "###" + id + ";" + type
    itemlist.extend(it1)
    itemlist.extend(it2)

    ## 2 = película
    if type == "2" and item.category != "Cine":
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="greenyellow",
                                 action="add_pelicula_to_library", url=url_targets, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle, infoLabels=item.infoLabels, quality=calidad,
                                 ))
    
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    
    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        item.url = item.url.split("###")[0]
        post = "target_id=%s&target_type=%s&target_status=1" % (id, type)
        
        data = agrupa_datos(urlparse.urljoin(host, "a/status"), post=post, hide_infobox=True)
        check_user_status(reset=True)
    
    devuelve = servertools.findvideosbyserver(item.url, item.server)
    
    if devuelve:
        item.url = devuelve[0][1]
    else:
        devuelve = servertools.findvideos(item.url, True)
        if devuelve:
            item.url = devuelve[0][1]
            item.server = devuelve[0][2]
    item.thumbnail = item.contentThumbnail
    item.contentTitle = item.contentTitle
    
    return [item]


def extrae_idiomas(bloqueidiomas, list_language=False):
    logger.info()
    
    language=[]
    textoidiomas = ''
    orden_idiomas = {'CAST': 0, 'LAT': 1, 'VOSE': 2, 'VOS': 3, 'VO': 4}
    
    if not list_language:
        patronidiomas = '([a-z0-9]+).png"'
        idiomas = re.compile(patronidiomas, re.DOTALL).findall(bloqueidiomas)
    else:
        idiomas = bloqueidiomas
    #Orden y diccionario
    for w in idiomas:
        i = IDIOMAS.get(w.lower(), w)
        language.insert(orden_idiomas.get(i, 0), i)
    
    for idioma in language:
        textoidiomas += "[%s] " % idioma
    
    return textoidiomas, language

def set_status__(item):
    
    if item.contentTitle:
        agreg = "Pelicula %s" % item.contentTitle
    else:
        agreg = "Serie %s" % item.contentSerieName
    if "###" in item.url:
        id = item.url.split("###")[1].split(";")[0]
        type = item.url.split("###")[1].split(";")[1]
        # item.url = item.url.split("###")[0]
    if "Abandonar" in item.title:
        title = "[COLOR darkgrey][B]Abandonando %s[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=" + id + "&target_type=" + type + "&target_status=0"
    elif "Visto" in item.title:
        title = "[COLOR darkgrey][B]No Vista %s[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=" + id + "&target_type=" + type + "&target_status=0"
    elif "Seguir" in item.title:
        title = "[COLOR orange][B]Siguiendo %s[/B][/COLOR]"
        path = "/a/status"
        post = "target_id=" + id + "&target_type=" + type + "&target_status=3"
    elif "Agregar a Favoritos" in item.title:
        title = "[COLOR orange][B]%s agregada a Favoritos[/B][/COLOR]"
        path = "/a/favorite"
        post = "like_id=" + id + "&like_type=" + type + "&like_comment=&vote=1"
    elif "Quitar de Favoritos" in item.title:
        title = "[COLOR darkgrey][B]%s eliminada de Favoritos[/B][/COLOR]"
        path = "/a/favorite"
        post = "like_id=" + id + "&like_type=" + type + "&like_comment=&vote=-1"
    else:
        title = "[COLOR darkgrey][B]%s eliminada de Favoritos[/B][/COLOR]"
        path = "/a/favorite"
        post = "like_id=" + id + "&like_type=" + type + "&like_comment=&vote=-1"
    
    data = agrupa_datos(urlparse.urljoin(host, path), post=post, hide_infobox=True)
    check_user_status(reset=True)
    title = title % item.contentTitle
    platformtools.dialog_ok(item.contentTitle, title)
    
    return

def get_status(status, type, id):
    
    if not status:
        return ""
    
    if type == 'shows':
        state = {'0': '', '1': 'Finalizada', '2': 'Pendiente', '3': 'Siguiendo', '4': 'Para ver', '5': 'Favoritos'}
    else:
        state = {'0': '', '1': 'Visto', '2': 'Pendiente', '3': 'Recomendadas'}
    
    str_ = str1 = str2 = ""
    try:
        if id in status['favorites'][type]:
            str1 = "[COLOR orange](Favorito)[/COLOR]"
    except:
        str1 = ""
    try:
        if id in status['status'][type]:
            str2 = state[status['status'][type][id]]
            if str2: 
                if 'Siguiendo' in str2:
                    str2 = "[COLOR orange](" + state[status['status'][type][id]] + ")[/COLOR]"
                else:
                    str2 = "[COLOR blue](" + state[status['status'][type][id]] + ")[/COLOR]"
    except:
        str2 = ""
    
    if str1 or str2:
        str_ = ' ' + str1 + str2

    return str_

def get_page_num(item):
    
    from platformcode import platformtools
    
    heading = 'Introduzca nº de la Página'
    page_num = platformtools.dialog_numeric(0, heading, default="")
    item.url = re.sub(r'\d+$', page_num, item.url)
    if page_num:
        return fichas(item)

def find_hidden_seasons(item, matches, sid):
    
    if not matches: 
        return matches
    
    try:
        try:
            web = int(matches[-1][0])
        except:
            web = 1
            logger.error('Web: %s)' % matches)
        try:
            if not item.infoLabels['number_of_seasons']:
                tmdb.set_infoLabels(item, True)
            tmdb_season = int(item.infoLabels['number_of_seasons'])
        except:
            tmdb_season = web
        high_season = 0

        season_name = scrapertools.find_single_match(matches[-1][1], '([^$]+\s+)\d+')
        thumb = matches[-1][2]
        
        url = urlparse.urljoin(host, "a/episodes")
        post = "action=lastest&start=0&limit=1&elang=ALL&show=%s" % sid
        data = agrupa_datos(url, post=post, json=True, force_check=False, force_login=False, alfa_s=True)
        if data and isinstance(data, list):
            try:
                high_season = int(data[0].get('season', 0))
            except:
                high_season = 0
        logger.info('Web: %s, Latest: %s, Tmdb: %s' % (web, high_season, tmdb_season))
        
        if not high_season:
            try:
                if matches and item.infoLabels['tmdb_id'] and item.infoLabels['number_of_seasons'] \
                           and int(item.infoLabels['number_of_seasons']) > int(matches[-1][0]):

                    for high_season in reversed(range(tmdb_season+1)):
                        if high_season <= web:
                            return matches
                        
                        post = "action=season&start=0&limit=0&show=%s&season=%s" % (sid, high_season)
                        data = agrupa_datos(url, post=post, json=True, force_check=False, force_login=False, alfa_s=True)
                        if data and isinstance(data, list):
                            break
                else:
                    return matches
            except:
                logger.error(traceback.format_exc())
                return matches

        for i in range(web+1, high_season+1):
            matches.append((str(i), season_name+str(i), thumb))
    except:
        logger.error(traceback.format_exc())
    
    return matches
