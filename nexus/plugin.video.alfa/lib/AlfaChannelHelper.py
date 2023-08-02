# -*- coding: utf-8 -*-
# -*- Alfa Channel Helper -*-
# -*- Herramientas genericas para canales BS -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
import time
import base64
import xbmcgui
window = xbmcgui.Window(10000) or None
if not PY3: _dict = dict; from collections import OrderedDict as dict

from channelselector import get_thumb
from core import scrapertools
from core import servertools
from core import jsontools
from core.item import Item
from platformcode import config
from platformcode import logger
from channels import filtertools
from channels import autoplay

DEBUG = False
BTDIGG = 'btdig'
BTDIGG_URL = config.BTDIGG_URL
BTDIGG_LABEL = config.BTDIGG_LABEL
UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
DEFAULT = 'default'
DOMAIN_ALT = 'wolfmax4k'
DOMAIN_ALT_S = 'wolfmax'
IDIOMAS = {'mx': 'Latino', 'dk': 'Latino', 'es': 'Castellano', 'en': 'VOSE', 'gb': 'VOSE', 
           'sub': 'VOSE', 'su': 'VOSE', 'eng': 'VOSE', "subtitulado": "VOSE", "usa": "VOSE", 
           'de': 'VOSE', "español": "Castellano", "espana": "Castellano", 'cas': 'Castellano', 
           "mexico": "Latino", "latino": "Latino", 'lat': 'Latino', 'LAT': 'Latino', 'jp': 'VOSE',
           'spain': 'Castellano', '🇲🇽': 'Latino', '🇪🇸': 'Castellano'}
IDIOMAS_T = {'es': 'CAST', 'la': 'LAT', 'us': 'VOSE', 'ES': 'CAST', 'LA': 'LAT', 'US': 'VOSE', 
             'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VOSE', 'latino': 'LAT', 
             'castellano': 'CAST', 'portugues': 'VOSE', 'sub': 'VOSE', 'spa': 'CAST', 'esp': 'CAST', 
             'espsub': 'VOSE', 'engsub': 'VOS', 'eng': 'VO', 'VOSE': 'VOSE', 'Sub': 'VOSE', 'LAT': 'LAT',
             'Original subtitulado': 'VOS', 'subtitulado en español': 'VOSE', 'espanol': 'CAST', 
             'ingles': 'VO', 'espaniol': 'CAST', 'Frances': 'VOSE'}
IDIOMAS_A = {'Castellano': 'CAST', 'CAST': 'CAST', 'us': 'VOSE', 'US': 'VOSE', 'Version Original': 'VOSE'}
LIST_SERVERS = ['streamtape', 'doodstream', 'okru', 'streamsb', 'streamlare', 'wolfstream', 'voe', 'mega', 'torrent']
LIST_SERVERS_A = ['doodstream', 'vidlox', 'gounlimited', 'verystream', 'aparatcam', 'mangovideo', 'streamtape', 'okru', 'torrent']
LIST_QUALITY_MOVIES = ['BluRay', '1080p', 'HD', 'Rip', 'MicroHD', '720p', '2160p', '4K', '3D', 'RHDTV', 'DVDSCR', 'DVDR', 'CAM', 'Screener']
LIST_QUALITY_MOVIES_A = ['1080p', '720p', 'HD', 'Rip', '2160p', '4K', 'CAM']
LIST_QUALITY_TVSHOW = ['HDTV-720p', 'HDTV', 'WEB-DL 1080p', '4KWebRip']


class AlfaChannelHelper:

    def __init__(self, host, timeout=15, channel='', movie_path="/movies", tv_path="/serie", 
                 movie_action="findvideos", tv_action="seasons", forced_proxy_opt='', 
                 list_language=[], list_quality=[], list_quality_movies=[], list_quality_tvshow=[], 
                 list_servers=[], language=[], idiomas={}, IDIOMAS_TMDB={0: 'es', 1: 'en', 2: 'es,en'}, 
                 actualizar_titulos=True, canonical={}, finds={}, debug=False, url_replace=[]):
        global DEBUG
        DEBUG = debug
        from core import httptools
        from platformcode import unify
        
        self.url = ''
        self.host = host
        self.host_torrent = finds.get('controls', {}).get('host_torrent', self.host)
        self.timeout = timeout
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        self.channel = channel or canonical.get('channel', '')
        if self.channel and canonical and 'host' in canonical and not canonical['host'] and canonical.get('host_alt', []): 
            config.set_setting("current_host", canonical['host_alt'][0], channel=self.channel)
        self.movie_path = movie_path
        self.tv_path = tv_path
        self.movie_action = movie_action
        self.tv_action = tv_action
        self.forced_proxy_opt = forced_proxy_opt
        self.list_language = list_language
        self.list_servers = list_servers or LIST_SERVERS
        self.list_quality_movies = list_quality_movies or LIST_QUALITY_MOVIES
        self.list_quality_tvshow = list_quality_tvshow or LIST_QUALITY_TVSHOW
        self.list_quality = list_quality or self.list_quality_movies + self.list_quality_tvshow
        self.language = language
        self.idiomas = idiomas or IDIOMAS
        self.IDIOMAS_TMDB = IDIOMAS_TMDB
        self.actualizar_titulos = actualizar_titulos
        self.canonical = canonical
        self.finds = finds
        self.profile = self.finds.get('controls', {}).get('profile', DEFAULT)
        self.url_replace = url_replace
        self.Window_IsMedia = True
        self.season_colapse = True
        self.unescape = False
        self.btdigg = False
        self.btdigg_search = False
        self.last_page = 0
        self.curr_page = 0
        self.next_page_url = ''
        self.itemlist = []
        self.color_setting = unify.colors_file[UNIFY_PRESET]
        self.window = window
        self.Comment = None

        self.httptools = httptools
        self.response = self.httptools.build_response(HTTPResponse=True)
        self.response_proxy = self.response.proxy__
        self.response_preferred_proxy_ip = ''
        self.alfa_domain_web_list = jsontools.load(window.getProperty("alfa_domain_web_list")) \
                                                   if window.getProperty("alfa_domain_web_list") else {}
        self.headers = {}
        
        self.SUCCESS_CODES = self.httptools.SUCCESS_CODES
        self.REDIRECTION_CODES = self.httptools.REDIRECTION_CODES
        self.PROXY_CODES = self.httptools.PROXY_CODES
        self.NOT_FOUND_CODES = self.httptools.NOT_FOUND_CODES
        self.CLOUDFLARE_CODES = self.httptools.CLOUDFLARE_CODES
        self.OPENSSL_VERSION = self.httptools.OPENSSL_VERSION
        self.ssl_version = self.httptools.ssl_version
        self.ssl_context = self.httptools.ssl_context
        self.patron_local_torrent = '(?i)(?:(?:\\\|\/)[^\[]+\[\w+\](?:\\\|\/)[^\[]+\[\w+\]_\d+\.torrent|magnet\:)'
        self.TEST_ON_AIR = self.httptools.TEST_ON_AIR
        try:
            self.ASSISTANT_VERSION = config.get_setting('assistant_version', default='').split('.')
            self.ASSISTANT_VERSION = tuple((int(self.ASSISTANT_VERSION[0]), int(self.ASSISTANT_VERSION[1]), int(self.ASSISTANT_VERSION[2])))
        except Exception:
            self.ASSISTANT_VERSION = tuple()

    def create_soup(self, url, **kwargs):
        """
        :param url: url destino
        :param kwargs: parametros que se usan en donwloadpage
        :return: objeto soup o response sino soup
        """
        from lib.generictools import js2py_conversion, check_blocked_IP

        if "soup" not in kwargs: kwargs["soup"] = True
        json = kwargs.pop("json", False)
        if "unescape" in kwargs: self.unescape = kwargs.get("unescape", False)
        kwargs["unescape"] = self.unescape
        if 'headers' not in kwargs and self.headers: 
            kwargs["headers"] = self.headers
        if 'referer' not in kwargs and 'Referer' not in kwargs.get('headers', {}) and 'Referer' not in self.headers \
                                   and "add_referer" not in kwargs: kwargs["add_referer"] = True
        if "ignore_response_code" not in kwargs: kwargs["ignore_response_code"] = True
        if "canonical" not in kwargs: kwargs["canonical"] = self.canonical
        if "forced_proxy_opt" not in kwargs and "forced_proxy_opt" not in kwargs["canonical"] and self.forced_proxy_opt:
            kwargs["forced_proxy_opt"] = self.forced_proxy_opt
        if "timeout" not in kwargs and "timeout" not in kwargs["canonical"]:
            kwargs["timeout"] = self.timeout
        size_js = kwargs.pop('size_js', 10000)
        if 'preferred_proxy_ip' in kwargs or 'preferred_proxy_ip' in kwargs.get('canonical', {}) \
                       or kwargs.get('forced_proxy_ifnot_assistant', '') == 'ProxySSL' \
                       or kwargs.get('canonical', {}).get('forced_proxy_ifnot_assistant', '') == 'ProxySSL':
            self.response_preferred_proxy_ip = window.getProperty("AH_%s_preferred_proxy_ip" % self.channel) \
                                                                  if window else self.response_preferred_proxy_ip
            if 'preferred_proxy_ip' in kwargs and self.response_preferred_proxy_ip:
                kwargs['preferred_proxy_ip'] = self.response_preferred_proxy_ip
            elif kwargs.get('canonical', {}):
                kwargs['canonical']['preferred_proxy_ip'] = self.canonical['preferred_proxy_ip'] = self.response_preferred_proxy_ip
        
        #if DEBUG: logger.debug('KWARGS: %s' % kwargs)
        response = self.httptools.downloadpage(url, **kwargs)

        if response.code in self.httptools.SUCCESS_CODES \
                         and ('text/' in response.headers.get('Content-Type', '') \
                         or 'json' in response.headers.get('Content-Type', '') \
                         or 'xml' in response.headers.get('Content-Type', '') \
                         or 'javascript' in response.headers.get('Content-Type', '')):
                response = js2py_conversion(response.data, url, resp=response, size=size_js, **kwargs)
        
        if response.code in self.httptools.NOT_FOUND_CODES:
            response.data = ''
            if kwargs.get("soup", True):
                response.soup = self.do_soup(response.data, encoding='utf-8')
            elif json:
                response.json = {}

        if kwargs.get("soup", True):
            soup = response.soup or {}
        elif json:
            soup = response.json or {}
            if not soup and response.data:
                soup = response.data
                if not isinstance(soup, _dict):
                    soup = jsontools.load(soup)
                response.json = soup
        else:
            soup = response

        if response.host:
            logger.error('response.host: %s' % response.host)
            self.doo_url = self.doo_url.replace(self.host, response.host)
            self.url = url.replace(self.host, response.host)
            self.host = response.host
        elif response.url and response.url != url:
            if not response.url.startswith('http'):
                logger.error('WRONG response.url: %s / %s' % (url, response.url))
            else:
                if not scrapertools.find_single_match(url, '(page\/\d+\/?)'):
                    self.url = '%s%s' % (response.url, scrapertools.find_single_match(url, '(page\/\d+\/?)'))
                else:
                    self.url = response.url

        self.response = response

        self.alfa_domain_web_list = jsontools.load(window.getProperty("alfa_domain_web_list")) \
                                                   if window.getProperty("alfa_domain_web_list") else {}
        if not self.alfa_domain_web_list.get('croxyproxy.com'):
            self.response_preferred_proxy_ip = ''
            if window: window.setProperty("AH_%s_preferred_proxy_ip" % self.channel, str(self.response_preferred_proxy_ip))
        self.response_proxy = response.proxy__
        if self.response_proxy and 'croxyproxy.com' in self.response_proxy: 
            self.response_preferred_proxy_ip = self.response_proxy.split('|')[2] \
                        if response.code in self.httptools.SUCCESS_CODES + self.httptools.REDIRECTION_CODES else ''
            if 'preferred_proxy_ip' in kwargs:
                kwargs['preferred_proxy_ip'] = self.response_preferred_proxy_ip
            if 'preferred_proxy_ip' in kwargs.get('canonical', {}):
                kwargs['canonical']['preferred_proxy_ip'] = self.canonical['preferred_proxy_ip'] = self.response_preferred_proxy_ip
            if window: window.setProperty("AH_%s_preferred_proxy_ip" % self.channel, str(self.response_preferred_proxy_ip))

        if kwargs.get('check_blocked_IP', False) or kwargs.get('canonical', {}).get('check_blocked_IP', False):
            res, self.itemlist = check_blocked_IP(response.data, self.itemlist or kwargs.get('itemlist', []), 
                                                  url, canonical=self.canonical, verbose=True)

        self.ssl_version = self.httptools.ssl_version
        self.ssl_context = self.httptools.ssl_context

        return soup

    def list_all(self, item, data='', matches_post=None, postprocess=None, generictools=False, 
                 finds={}, **kwargs):
        pass

    def section(self, item, data= '', action="list_all", matches_post=None, postprocess=None, 
                section_list={}, finds={}, **kwargs):
        pass

    def seasons(self, item, data='', action="episodesxseason", matches_post=None, postprocess=None, 
                seasons_search_post=None, generictools=False, seasons_list={}, finds={}, **kwargs):
        pass

    def episodes(self, item, data='', action="findvideos", matches_post=None, postprocess=None, 
                 generictools=False, episodes_list={}, finds={}, **kwargs):
        pass

    def get_video_options(self, item, url, data='', langs=[], matches_post=None, postprocess=None, 
                          verify_links=False, generictools=False, findvideos_proc=False, finds={}, **kwargs):
        pass

    def define_content_type(self, new_item, contentType=''):

        if new_item.infoLabels.get("year", '') and str(new_item.infoLabels["year"]) in new_item.title and len(new_item.title) > 4:
            new_item.title = re.sub("\(|\)|%s" % str(new_item.infoLabels["year"]), "", new_item.title).strip()

        if new_item.contentType == 'episode': 
            new_item.title = re.sub('(?i)\s*temp\w*\s*\d+\s*(?:epi\w*|cap\w*)\s*\d+\s*', '', new_item.title)
            if not new_item.contentSerieName: new_item.contentSerieName = re.sub('\s*\d+x\d+\s*(?:\s*-\s*)?', '', new_item.title)
            new_item.action = self.movie_action
        elif contentType != 'tvshow' and ((self.movie_path in new_item.url and not self.tv_path in new_item.url) \
                                     or new_item.contentType == 'movie'):
            new_item.action = self.movie_action
            new_item.contentTitle = new_item.title.strip()
            if new_item.infoLabels.get("tvshowtitle", ''): del new_item.infoLabels["tvshowtitle"]
            if not new_item.contentType: new_item.contentType = 'movie'
            if not new_item.infoLabels.get("year", ''): new_item.infoLabels["year"] = '-'
        else:
            new_item.action = self.tv_action
            new_item.contentSerieName = new_item.title.strip()
            new_item.contentType = 'tvshow'

        return new_item
    
    def get_color_from_settings(self, label, default='white'):
        
        color = config.get_setting(label)
        if not color:
            return default
        
        color = scrapertools.find_single_match(color, '\](\w+)\[')
        
        return color or default

    def add_video_to_videolibrary(self, item, itemlist, contentType='tvshow'):

        if item.add_videolibrary or item.library_playcounts or item.downloadFilename:
            return itemlist

        item_p = item.clone()
        item_p.quality = ''
        if 'server' in item_p: del item_p.server
        if 'post' in item_p: del item_p.post
        item_p.infoLabels['playcount'] = 0
        actionType = 'pelicula' if contentType == 'movie' else 'season' if contentType == 'season' else 'serie'
        contentTitle = 'pelicula' if contentType == 'movie' else 'temporada' if contentType == 'season' else 'serie'

        if self.Window_IsMedia:
            if len(itemlist) > 0:
                if item_p.action == 'findvideos':
                    itemlist.append(item_p.clone(channel="trailertools", title="**-[COLOR magenta] Buscar Trailer [/COLOR]-**", 
                                                 action="buscartrailer", context=""))
            
            if config.get_videolibrary_support() and len(itemlist) > 0 and item_p.contentChannel != "videolibrary" \
                            and ((item_p.contentType == 'episode' and item_p.url_tvshow) or item_p.action != 'findvideos' \
                            or (item_p.contentType == 'movie' and item_p.action == 'findvideos')):
                item_p.url = self.do_url_replace(item_p.url)
                
                if self.actualizar_titulos:
                    itemlist.append(item_p.clone(title="** [COLOR %s]Actualizar Títulos - vista previa videoteca[/COLOR] **" \
                                                        % self.get_color_from_settings('library_color', default='yellow'), 
                                                 action="actualizar_titulos",
                                                 tmdb_stat=False, 
                                                 from_action=item_p.action, 
                                                 contentType=contentType,
                                                 from_title_tmdb=item_p.title, 
                                                 from_update=True, 
                                                 thumbnail=item_p.infoLabels['temporada_poster'] or item_p.infoLabels['thumbnail']
                                                )
                                   )

                itemlist.append(item_p.clone(title='[COLOR yellow]Añadir esta %s a la videoteca[/COLOR]' % contentTitle, 
                                             url=item_p.url_tvshow or item_p.url,
                                             action="add_%s_to_library" % actionType,
                                             extra="episodios",
                                             contentType=contentType, 
                                             contentSerieName=item_p.contentSerieName,
                                             plot_extend = ''
                                            )
                               )
        return itemlist

    def do_url_replace(self, url, url_replace=[]):

        if url and (url_replace or self.url_replace):

            for url_from, url_to in (url_replace or self.url_replace):
                url = re.sub(url_from, url_to, str(url))

        url = str(url).replace(' ', '%20')
        return url

    def do_quote(self, url, plus=True):
        try:
            if PY3:
                import urllib.parse as urllib
            else:
                import urllib

            if plus:
                return urllib.quote_plus(url)
            else:
                return urllib.quote(url)
        except Exception:
            return ''

    def do_unquote(self, url):
        try:
            if PY3:
                import urllib.parse as urllib
            else:
                import urllib
            
            return urllib.unquote(url)
        except Exception:
            return ''

    def do_urlencode(self, post):
        try:
            if PY3:
                import urllib.parse as urllib
            else:
                import urllib
            
            return urllib.urlencode(post)
        except Exception:
            return ''

    def urljoin(self, domain, url):
        if PY3:
            import urllib.parse as urlparse
        else:
            import urlparse
        
        return urlparse.urljoin(domain, url)

    def obtain_domain(self, url, sub=False, point=False, scheme=False):

        return self.httptools.obtain_domain(url, sub=sub, point=point, scheme=scheme)

    def channel_proxy_list(self, url, forced_proxy=None):

        return self.httptools.channel_proxy_list(url, forced_proxy=forced_proxy)

    def get_cookie(self, url, name, follow_redirects=False):

        return self.httptools.get_cookie(url, name, follow_redirects=False)

    def do_soup(self, data, encoding='utf-8'):
        from bs4 import BeautifulSoup

        return BeautifulSoup(data, "html5lib", from_encoding=encoding)

    def do_actualizar_titulos(self, item):

        from lib.generictools import update_title
        
        item.AHkwargs = {'function': 'list_all' if item.contentType in ['movie', 'tvshow'] \
                                                else 'seasons' if item.contentType in ['season'] else 'episodes'}
        return update_title(item)

    def do_seasons_search(self, item, matches, **AHkwargs):
        
        from lib.generictools import AH_find_seasons
        return AH_find_seasons(self, item, matches, **AHkwargs)

    def convert_url_base64(self, url, host='', referer=None, rep_blanks=True, force_host=False, item=Item()):

        from lib.generictools import convert_url_base64
        return convert_url_base64(url, host, referer, rep_blanks, force_host, item)

    def is_local_torrent(self, url):

        return bool(scrapertools.find_single_match(url, self.patron_local_torrent))

    def find_btdigg_list_all(self, item, matches, channel_alt, **AHkwargs):

        from lib.generictools import AH_find_btdigg_list_all
        return AH_find_btdigg_list_all(self, item, matches, channel_alt, **AHkwargs)

    def find_btdigg_seasons(self, item, matches, domain_alt, **AHkwargs):

        from lib.generictools import AH_find_btdigg_seasons
        return AH_find_btdigg_seasons(self, item, matches, domain_alt, **AHkwargs)

    def find_btdigg_episodes(self, item, matches, domain_alt, **AHkwargs):

        from lib.generictools import AH_find_btdigg_episodes
        return AH_find_btdigg_episodes(self, item, matches, domain_alt, **AHkwargs)

    def find_btdigg_findvideos(self, item, matches, domain_alt, **AHkwargs):

        from lib.generictools import AH_find_btdigg_findvideos
        return AH_find_btdigg_findvideos(self, item, matches, domain_alt, **AHkwargs)

    def check_filter(self, item, itemlist, **AHkwargs):

        return filtertools.check_filter(item, itemlist)

    def verify_infoLabels_keys(self, item, keys, **AHkwargs):
        from core import tmdb

        item_copy = item.clone()

        item_copy.infoLabels['tmdb_id'] = item_copy.infoLabels['tvdb_id'] = item_copy.infoLabels['imdb_id'] = item_copy.infoLabels['plot'] = ''
        if item_copy.infoLabels['tagline']: item_copy.infoLabels['tagline'] = ''
        for key, value in keys.items():
            item_copy.infoLabels[key] = value
        tmdb.set_infoLabels_item(item_copy, True)

        if item_copy.infoLabels['tmdb_id'] or item_copy.infoLabels['tvdb_id'] or item_copy.infoLabels['imdb_id']:
            item.infoLabels['tmdb_id'] = item_copy.infoLabels['tmdb_id']
            item.infoLabels['tvdb_id'] = item_copy.infoLabels['tvdb_id']
            item.infoLabels['imdb_id'] = item_copy.infoLabels['imdb_id']
            item.infoLabels['plot'] = item_copy.infoLabels['plot']
            if item_copy.infoLabels['tagline']: item.infoLabels['tagline'] = item_copy.infoLabels['tagline']
            for key, value in keys.items():
                item.infoLabels[key] = value
            tmdb.set_infoLabels_item(item, True)

    def get_page_num(self, item, **AHkwargs):
        from platformcode.platformtools import dialog_numeric

        try:
            last_page_print = AHkwargs.get('curr_page', int(int(item.last_page) * float(item.page_factor)))
            heading = 'Introduzca nº de la Página: 1 a %s' % last_page_print
            page_num = AHkwargs.get('curr_page', int(dialog_numeric(0, heading, default='')))

            if page_num and page_num > 0 and page_num <= last_page_print:
                finds_controls = self.finds.get('controls', {})
                finds_next_page_rgx = self.finds.get('next_page_rgx') if self.finds.get('next_page_rgx') else [['page\/\d+\/', 'page/%s/']]
                
                item.curr_page = int(page_num / float(item.page_factor))
                item.cnt_tot_match = float(item.curr_page * float(item.page_factor) * finds_controls.get('cnt_tot', 20))
                item.matches = []
                item.title_lista = []
                item.action = 'list_all' if not item.to_action else item.to_action; del item.to_action

                if 'matches_org' not in item:
                    post = item.post or finds_controls.pop('post', None)
                    url_page = item.url
                    url_page_control = 'url'

                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list):
                        if finds_controls['force_find_last_page'][2] == 'post': 
                            url_page = post
                            url_page_control = 'post'
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if url_page_control == 'url':
                            item.url = re.sub(rgx_org, rgx_des % str(item.curr_page), url_page.rstrip('/')).replace('//?', '/?')
                        else:
                            item.post = re.sub(rgx_org, rgx_des % str(item.curr_page), post.rstrip('/')).replace('//?', '/?')

                else:
                    item.matches = item.matches_org[int((page_num - 1) * finds_controls.get('cnt_tot', 20)):]

                channel = __import__('channels.%s' % item.channel, None,
                                     None, ["channels.%s" % item.channel])
                return getattr(channel, item.action)(item)

        except Exception:
            logger.error(traceback.format_exc())

        return

    def unify_custom(self, title, item, elem, **AHkwargs):

        try:
            function = AHkwargs.get('function', '')

            color_setting = self.color_setting
            color_default = 'white'
            text = color_setting.get('movie', color_default)
            stime = color_setting.get('year', color_default)
            quality = color_setting.get('quality', color_default)
            language = color_setting.get('cast', color_default)
            server = color_setting.get('server', color_default)
            canal = color_setting.get('tvshow', color_default)
            views = color_setting.get('rating_3', color_default)
            library = color_setting.get('library', color_default)
            page = color_setting.get('update', color_default)
            star = color_setting.get('rating_3', color_default)
            error = 'red'

            color_tag = '[COLOR %s]%s[/COLOR] '
            title_colored = ''
            
            title = scrapertools.decode_utf8_error(title) or ''
            
            if elem.get('custom'):
                title_colored += color_tag % (color_setting.get(elem.get('custom', ''), color_default), title)

            elif elem.get('page'):
                title_colored += color_tag % (page, title)
                title_colored = re.sub('(\d+)', color_tag.strip() % (text, r'\1'), title_colored)
            
            elif elem.get('play'):
                title_colored += color_tag % (star, elem.get('play'))

            elif function in ['list_all_A']:
                if elem.get('stime'):
                    if isinstance(elem['stime'], int):
                        elem['stime'] = self.convert_time(elem['stime'])
                    else:
                        stime_split = elem['stime'].split(':')
                        elem['stime'] = '%s:%s' % (stime_split[0].zfill(2), stime_split[1].zfill(2)) if len(stime_split) >= 2 else elem['stime']
                    title_colored += color_tag % (stime, elem['stime'])
                title_colored += color_tag % (quality, elem.get('quality').upper()) if elem.get('quality') else ''
                title_colored += color_tag % (canal, '[%s]' % elem.get('canal')) if elem.get('canal') else ''
                title_colored += color_tag % (star, '%s' % elem.get('star')) if elem.get('star') else ''
                title_colored += color_tag % (text if not elem.get('premium', '') else error, title.title())
                title_colored += color_tag % (views, '[%s visitas]' % elem.get('views')) if (elem.get('views') and elem['views'] != '0') else ''

            elif function in ['section_A']:
                title_colored += color_tag % (text, title.title())
                title_colored += color_tag % (text, '(%s)' % str(elem.get('cantidad', '')).replace(',', '.')) if elem.get('cantidad') else ''
                
            elif function in ['get_video_options_A']:
                title_colored += color_tag % (server, '[%s]' % elem.get('server', '').capitalize()) if elem.get('server') else ''
                if not elem.get('server', ''): title_colored += color_tag % (server, '[%s]' % elem.get('title', '').capitalize())
                title_colored += color_tag % (language, '[%s]' % elem.get('language', '')) if elem.get('language') else ''
                title_colored += color_tag % (quality, '[%s]' % elem.get('quality', '')) if elem.get('quality') else ''
                title_colored += color_tag % (text, '[%s]' % elem.get('torrent_info', '')) if elem.get('torrent_info') else ''

        except Exception:
            logger.error(traceback.format_exc())

        #if DEBUG: logger.debug('UNIFY_custom: %s' % title_colored.strip() or title)
        return title_colored.strip() or title

    def get_language_and_set_filter(self, elem, elem_json):

        langs = []
        elem_json['language'] = '*'
        finds_out = self.finds.get('get_language', {})
        finds_lang_rgx = self.finds.get('get_language_rgx', '(?:flags\/|-)(\w+)\.(?:png|jpg|jpeg|webp)')

        try:
            if finds_out:
                lang_list = self.parse_finds_dict(elem, finds_out)
            else:
                lang_list = elem
            if not isinstance(lang_list, list): lang_list = [lang_list]
            for lang in lang_list:
                lang_ = scrapertools.find_single_match(str(lang).lower(), finds_lang_rgx)
                if self.idiomas.get(lang_, ''):
                    if self.idiomas.get(lang_, '') not in langs:
                        langs += [self.idiomas.get(lang_, '')]
                elif lang_ and lang_ not in langs:
                    langs += [lang_]
        except Exception:
            langs = []
        
        langs_out = elem_json['language']
        if langs:
            langs = sorted(langs)
            for lang in langs:
                langs_out += '%s,' % lang
            else:
                elem_json['language'] = langs_out.rstrip(',')
        
        if DEBUG or not langs_out or langs_out == '*': 
            logger.debug('FINDS_get_language: %s; LANGS: %s' % (finds_lang_rgx, langs or lang_list))
            if not langs_out or langs_out == '*': logger.debug('FINDS_get_language: ELEM: %s' % elem)

    def find_quality(self, elem_in, item):
        
        tvshow_type = ['series', 'documentales', 'tvshow', 'season', 'episode']

        if isinstance(elem_in, _dict):
            elem = elem_in.copy()
            c_type = item.c_type or item.contentType
        else:
            elem = {}
            elem['quality'] = elem_in.quality
            elem['title'] = elem_in.title
            elem['url'] = elem_in.url
            elem['language'] = elem_in.language
            c_type = elem_in.contentType

        url = elem['url'].lower().replace(DOMAIN_ALT, DOMAIN_ALT_S) or item.url.lower().replace(DOMAIN_ALT, DOMAIN_ALT_S)
        url_item = item.url.lower().replace(DOMAIN_ALT, DOMAIN_ALT_S)
        quality = elem.get('quality', '').replace('*', '').replace('[]', '')
        if quality in ['720', '720P']: quality = '720p'
        if quality in ['1080', '1080P']: quality = '1080p'

        if c_type in tvshow_type or (elem.get('mediatype', '') and elem['mediatype'] in tvshow_type) or self.tv_path in elem.get('url', ''):
            if '720p' in elem['title'] or '720p' in url or '720p' in elem.get('quality', ''):
                quality = 'HDTV-720p'
            elif '1080p' in elem['title'] or '1080p' in url or '1080p' in elem.get('quality', ''):
                quality = 'WEB-DL 1080p'
            elif '4k' in elem['title'].lower() or '4k' in url or '4k' in elem.get('quality', '').lower() or \
                 '2160p' in elem['title'] or '2160p' in url or '2160p' in elem.get('quality', ''):
                quality = '4KWebRip'
            else:
                quality = 'HDTV'
        else:
            if not quality and ('hd' in url_item or '4k' in url_item or '3d' in url_item \
                           or 'hd' in url or '4k' in url or '3d' in url):
                quality = 'HD'
            elif not quality and ('avi' in elem['title'].lower() or 'avi' in url or 'avi' in elem.get('quality', '').lower()):
                quality = 'BlueRayRip'
            if '720' not in quality and ('720' in elem['title'] or '720' in url or '720' in elem.get('quality', '')):
                quality += 'BluRay-720p' if not quality else ', BluRay-720p'
            if '1080' not in quality and ('1080' in elem['title'] or '1080' in url or '1080' in elem.get('quality', '')):
                quality += 'BluRay-1080p' if not quality else ', BluRay-1080p'
            quality = quality.replace('HD, ', '')

            if (('4k' in url_item and not url_item.startswith('magnet')) or ('4k' in url \
                                          and not url.startswith('magnet'))) and not '4k' in quality.lower():
                quality += ', 4K'
            if (('3d' in url_item and not url_item.startswith('magnet')) or ('3d' in url \
                                          and not url.startswith('magnet'))) and not '3d' in quality.lower():
                quality += ', 3D'
            quality = quality.replace('-', ' ').replace('_', ' ').replace('bluray', 'BluRay').replace('Bluray', 'BluRay').replace('BLURAY', 'BluRay')

        if 'dual' in quality.lower(): quality = re.sub('(?i)\s*dual', '', quality)
        if 'digg' in elem.get('quality', '').lower() and 'digg' not in quality.lower(): quality += BTDIGG_LABEL

        if DEBUG: logger.debug('find_QUALITY: %s' % quality)
        return quality

    def find_language(self, elem_in, item):

        language = []
        
        if isinstance(elem_in, _dict):
            elem = elem_in
            c_type = item.c_type or item.contentType
        else:
            elem = {}
            elem['quality'] = elem_in.quality
            elem['title'] = elem_in.title
            elem['url'] = elem_in.url
            elem['language'] = elem_in.language
            c_type = elem_in.contentType
        
        if not isinstance(elem.get('language'), list): elem['language'] = [elem['language'].replace('*', '')]
        for lang in elem.get('language', []):
            if 'castellano' in elem.get('quality', '').lower() or (('español' in elem.get('quality', '').lower() \
                        or 'espanol' in elem.get('quality', '').lower() or 'spanish' in elem.get('quality', '').lower()) \
                        and not 'latino' in elem.get('quality', '').lower()) \
                        or 'castellano' in elem.get('title', '').lower() or 'cast' in elem.get('url', '').lower() \
                        or 'ca' in lang.lower() or (('esp' in lang.lower() or 'spanish' in lang.lower().lower())\
                        and not 'latino' in lang.lower()) or self.idiomas.get(lang, '') in ['CAST']:
                language += ['CAST']
            if 'latin' in elem.get('title', '').lower() or 'latin' in elem.get('url', '').lower() \
                        or 'lat' in elem.get('url', '').lower() or ('la' in lang.lower() \
                                 and not 'lla' in lang.lower() and not 'ula' in lang.lower()) \
                                 or self.idiomas.get(lang, '') in ['LAT']:
                if 'LAT' not in language: language += ['LAT']
            if 'sub' in elem.get('quality', '').lower() or 'subs. integrados' in elem.get('title', '').lower() \
                        or 'sub forzados' in elem.get('title', '').lower() or 'english' in elem.get('title', '').lower() \
                        or 'subtitle' in elem.get('url', '').lower() or 'english' in elem.get('url', '').lower() \
                        or 'vos' in elem.get('url', '').lower() or 'v.o' in elem.get('url', '').lower()\
                        or 'vos' in elem.get('title', '').lower() \
                        or 'sub' in lang.lower() or 'ing' in lang.lower() or 'eng' in lang.lower() \
                        or 'vo' in lang.lower() or self.idiomas.get(lang, '') in ['VO', 'VOS', 'VOSE']:
                if 'VOSE' not in language and 'DUAL' not in language: language += ['VOSE']
            if 'dual' in elem.get('title', '').lower() or 'dual' in elem.get('quality', '').lower() \
                        or 'dual' in elem.get('url', '').lower() or 'dual' in lang.lower() \
                        or self.idiomas.get(lang, '') in ['DUAL'] or (('CAST' in language or 'LAT' in language) and 'VOSE' in language):
                if 'DUAL' not in language: language += ['DUAL']
                if 'VOSE' in language: language.remove('VOSE')
            if lang and not language and not self.language and not item.language:
                language += ['VOSE']
            if not language and (self.language or item.language):
                language = self.language or item.language

        if DEBUG: logger.debug('find_LANGUAGE: %s' % language)
        return language

    def convert_size(self, size):
        
        if isinstance(size, (str, unicode)): size = size.replace('[COLOR magenta][B]RAR-[/B][/COLOR]', '')
        s = 0
        if not size or size == 0 or size == '0':
            return s

        try:
            size_name = {"M·B": 1, "G·B": 1024, "MB": 1, "GB": 1024}
            size = size.replace('\xa0', ' ')
            if ' ' in size:
                size_list = size.split(' ')
                size = float(size_list[0])
                size_factor = size_name.get(size_list[1], 1)
                s = size * size_factor
        except Exception:
            pass

        if DEBUG: logger.debug('SIZE: %s / %s' % (size, s))
        return s

    def convert_time(self, seconds):
        
        duration = ''

        if isinstance(seconds, (int, float)):
            try:
                hours = int(seconds/3600)
                seconds -= hours*3600
                minutes = int(seconds/60)
                seconds -= minutes*60

                duration = "%s:%s" % (str(minutes).zfill(2), str(seconds).zfill(2))
                if hours:
                    duration = "%s:%s" % (str(hours).zfill(2), duration)
            except Exception:
                logger.error(traceback.format_exc())
        else:
            duration = seconds

        #if DEBUG: logger.debug('TIME: %s / %s' % (seconds, duration))
        return duration

    def manage_torrents(self, item, elem, lang, soup={}, finds={}, **kwargs):

        from lib.generictools import get_torrent_size
        from core import filetools
        if DEBUG: logger.debug('ELEM_IN: %s' % elem)

        finds_controls = finds.get('controls', {})

        self.host_torrent = finds_controls.get('host_torrent', self.host_torrent) or self.host
        host_torrent_referer = finds_controls.get('host_torrent_referer', self.host_torrent)
        FOLDER = config.get_setting("folder_movies") if item.contentType == 'movie' else config.get_setting("folder_tvshows")
        size = ''

        if finds.get('torrent_params', {}):
            torrent_params = finds['torrent_params']
        else:
            torrent_params = {
                              'url': item.url,
                              'torrents_path': None, 
                              'local_torr': item.torrents_path, 
                              'lookup': False, 
                              'force': True, 
                              'data_torrent': True, 
                              'subtitles': True, 
                              'file_list': True, 
                              'find_alt_link_option': False, 
                              'language_alt': [], 
                              'quality_alt': '', 
                              'domain_alt': ''
                              }

        # Puede ser necesario bajar otro nivel para encontrar la página
        if elem.get('url', '') and not 'magnet:' in elem['url'] and not '.torrent' in elem['url']:
            if finds.get('controls', {}).get('url_base64', True):
                elem['url'] = self.convert_url_base64(elem['url'], self.host_torrent, referer=host_torrent_referer, item=item)
            if elem['url'] and not 'magnet:' in elem['url'] and not '.torrent' in elem['url']:
                if host_torrent_referer: kwargs['referer'] = host_torrent_referer
                torrent = self.create_soup(elem['url'], **kwargs)
                if self.response.code in self.REDIRECTION_CODES:
                    elem['url'] = self.response.headers.get('Location', '')
                elif torrent.a:
                    elem['url'] = torrent.a.get('href', '')
        
        # Restauramos urls de emergencia por si es necesario
        local_torr = '%s_torrent_file' % item.channel.capitalize()
        if item.emergency_urls and not item.videolibray_emergency_urls:
            try:                                                                # Guardamos la url ALTERNATIVA
                elem['torrent_alt'] = item.emergency_urls[0][0] if not elem['url'].startswith('magnet') else elem['url']
                if finds.get('controls', {}).get('url_base64', True):
                    elem['torrent_alt'] = self.convert_url_base64(elem['torrent_alt'], self.host_torrent, referer=host_torrent_referer, item=item)
            except Exception:
                item_local.torrent_alt = ''
                item.emergency_urls[0] = []

            if item.armagedon and elem.get('torrent_alt', ''):
                elem['url'] = elem['torrent_alt']                               # Restauramos la url
                if not elem['url'].startswith('http') and not elem['url'].startswith('magnet'):
                    local_torr = filetools.join(config.get_videolibrary_path(), FOLDER, elem['url'])
            if item.armagedon and len(item.emergency_urls[0]) > 1:
                del item.emergency_urls[0][0]

        # Buscamos tamaño en el archivo .torrent
        if not item.videolibray_emergency_urls and not elem['url'].startswith('magnet'):
            torrent_params['url'] = elem['url']
            torrent_params['torrents_path'] = ''
            torrent_params['local_torr'] = local_torr
            if lang not in item.language: torrent_params['language_alt'] = lang
            kwargs['referer'] = host_torrent_referer
            torrent_params = get_torrent_size(torrent_params['url'], torrent_params=torrent_params, 
                                              item=item, **kwargs)              # Tamaño en el .torrent
            size = torrent_params['size']
            elem['url'] = torrent_params['url']
            if torrent_params['torrents_path']: elem['torrents_path'] = torrent_params['torrents_path']

            if 'ERROR' in size and item.emergency_urls and not item.videolibray_emergency_urls:
                item.armagedon = True
                elem['url'] = elem['torrent_alt']                               # Restauramos la url

                torrent_params['size'] = ''
                torrent_params['local_torr'] = local_torr
                kwargs['referer'] = host_torrent_referer
                torrent_params = get_torrent_size(torrent_params['url'], torrent_params=torrent_params, 
                                                  item=item, **kwargs)          # Tamaño en el .torrent
                size = torrent_params['size']
                elem['url'] = torrent_params['url']
                if torrent_params['torrents_path']: elem['torrents_path'] = torrent_params['torrents_path']

        elem['torrent_info'] =  elem.get('torrent_info', '')
        if size:
            elem['size'] = size
            size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                       .replace('Mb', 'M·b').replace('.', ',')
            elem['torrent_info'] += '%s, ' % size                                # Agregamos size
            if elem.get('seeds'):
                elem['torrent_info'] += 'Seeds: %s, ' %  elem['seeds']          # Agregamos seeds
        if elem['url'].startswith('magnet:') and 'magnet' not in elem['torrent_info'].lower():
            elem['torrent_info'] += ' Magnet'
        if elem['torrent_info']:
            elem['torrent_info'] = elem['torrent_info'].strip().strip(',')
            if not item.unify:
                elem['torrent_info'] = '[%s]' % elem['torrent_info']

        # Si tiene contraseña, la guardamos y la pintamos
        if elem.get('password', '') or item.password:
            elem['password'] = item.password = elem.get('password', '') or item.password
            elem['torrent_info'] += " -[COLOR magenta] Contraseña: [/COLOR]'%s'" % elem['password']

        # Guardamos urls de emergencia si se viene desde un Lookup de creación de Videoteca
        if item.videolibray_emergency_urls:
            item.emergency_urls[0].append(elem['url'])                          # guardamos la url: la actualizará videolibrarytools
            item.emergency_urls[1].append(elem)                                 # guardamos el match
            item.emergency_urls[2].append(elem['url'])                          # guardamos la url o magnet inicial
            item.emergency_urls[3].append('#%s#%s' % (elem.get('quality', '') \
                                   or item.quality, elem['torrent_info']))      # Guardamos el torrent_info del .magnet
            if DEBUG: logger.debug('ELEM_OUT_EMER: %s' % elem)
            return elem

        elem['language'] = elem.get('language', item.language)
        if str(elem['language']).startswith('*'):
            elem['title'] = elem.get('title', item.title)
            elem['language'] = self.find_language(elem, item)
        
        elem['quality'] = elem.get('quality', item.quality)
        if str(elem['quality']).startswith('*'):
            elem['title'] = elem.get('title', item.title)
            elem['quality'] = self.find_quality(elem, item)
        if item.armagedon:
            elem['quality'] = '[COLOR hotpink][E][/COLOR] [COLOR limegreen]%s[/COLOR]' % elem['quality']

        # Ahora pintamos el link del Torrent
        elem['title'] = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][%s][/COLOR] '
        elem['title'] += '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' \
                        % (elem['quality'], str(elem['language']), elem['torrent_info'])
        elem['title'] = elem['title'].replace('*', '')

        # Preparamos título y calidad, quitando etiquetas vacías
        elem['title'] = re.sub(r'\s*\[COLOR\s*\w+\]\s*(?:\[\[*\s*\]*\])?\[\/COLOR\]', '', elem['title'])
        elem['title'] = re.sub(r'--|\[\s*\/*\]|\(\s*\/*\)|\|', '', elem['title']).strip()

        elem['quality'] = re.sub(r'\s*\[COLOR\s*\w+\]\s*(?:\[\[*\s*\]*\])?\[\/COLOR\]', '', elem['quality'])
        elem['quality'] = re.sub(r'--|\[\s*\/*\]|\(\s*\/*\)|\|', '', elem['quality']).strip()

        elem['alive'] = ''
        if not size or 'Magnet' in size:
            elem['alive'] = "??"                                                # Calidad del link sin verificar
        elif 'ERROR' in size and 'Pincha' in size:
            elem['alive'] = "ok"                                                # link en error, CF challenge, Chrome disponible
        elif 'ERROR' in size and 'Introduce' in size:
            elem['alive'] = "??"                                                # link en error, CF challenge, ruta de descarga no disponible
            elem['channel'] = 'setting'
            elem['action'] = 'setting_torrent'
            elem['unify'] = False
            elem['folder'] = False
            elem['item_org'] = item.tourl()
        elif 'ERROR' in size:
            elem['alive'] = "no"                                                # Calidad del link en error, CF challenge?
        else:
            elem['alive'] = "ok"                                                # Calidad del link verificada
        if elem['channel'] != 'setting':
            elem['action'] = "play"                                             # Visualizar vídeo
            elem['server'] = "torrent"                                          # Seridor Torrent

        if DEBUG: logger.debug('ELEM_OUT: %s' % elem)
        return elem

    def parse_finds_dict(self, soup, finds, year=False, next_page=False, c_type=''):

        matches = [] if (not year and not next_page) else '-' if year else ''
        matches_init = [] if (not year and not next_page) else '-' if year else ''
        if not finds: 
            return soup
        if not soup: 
            return matches

        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/

        match = soup
        json = {}
        level_ = ''
        block = ''
        f = ''
        tagOR_save = {}
        tagOR_save_all = []

        try:
            for x, (level_, block) in enumerate(finds.items()):
                level = re.sub('\d+', '', level_)
                for y, f in enumerate(block):
                    levels = {'find': [match.find, match.find_all], 
                              'find_all': [match.find, match.find_all], 
                              'find_parent': [match.find_parent, match.find_parents], 
                              'find_parents_all': [match.find_parent, match.find_parents],
                              'find_next_sibling': [match.find_next_sibling, match.find_next_siblings], 
                              'find_next_sibling_all': [match.find_next_sibling, match.find_next_siblings],
                              'find_previous_sibling': [match.find_previous_sibling, match.find_previous_siblings], 
                              'find_previous_siblings_all': [match.find_previous_sibling, match.find_previous_siblings],
                              'find_next': [match.find_next, match.find_all_next], 
                              'find_all_next': [match.find_next, match.find_all_next], 
                              'find_previous': [match.find_previous, match.find_all_previous], 
                              'find_all_previous': [match.find_previous, match.find_all_previous], 
                              'select_one': [match.select_one, match.select], 
                              'select_all': [match.select_one, match.select], 
                              'get_text': [match.get_text, match.get_text]
                              }
                    
                    soup_func = levels[level][0]
                    soup_func_all = levels[level][1]
                    
                    tag = ''
                    tagOR = False
                    attrs = {}
                    string = ''
                    regex = ''
                    argument = []
                    strip = ''
                    split = ''
                    json = {}
                    limit = 0
                    if isinstance(f, _dict):
                        attrs = f.copy()
                        tagOR = match if attrs.get('tagOR', '') else False
                        if tagOR and '_all' in level and match: tagOR_save = match
                        tag = attrs.pop('tagOR', '') or attrs.pop('tag', '')
                        string = attrs.pop('string', '')
                        regex = attrs.pop('@TEXT', '')
                        regex_sub = attrs.pop('@SUB', '')
                        argument = attrs.pop('@ARG', [])
                        if not isinstance(argument, list): argument = [argument]
                        strip = attrs.pop('@STRIP', True)
                        split = attrs.pop('@SPLIT', '')
                        json = attrs.pop('@JSON', {})
                        limit = attrs.pop('@LIM', 0)
                        pos = attrs.pop('@POS', '')
                        if pos: pos = pos[0]
                    else:
                        tag = f
                    if (isinstance(tag, (str, unicode)) and tag == '*') or (isinstance(tag, list) and len(tag) == 1 and tag[0] == '*'): 
                        tag = None

                    if DEBUG: logger.debug('find: %s=%s: %s=%s, %s, %s, %s, %s, %s, [%s]' % (level, [key for key in f if key in ['tagOR', 'tag']], 
                                            tag, attrs, string, regex, argument, str(strip), str(split), pos))
                    if '_all' not in level or ('_all' in level and x < len(finds[level])-1) or ('_all' in level and len(str(pos)) > 0):

                        if '_all' in level and len(str(pos)) > 0:
                            match = soup_func_all(tag, attrs=attrs, string=string, limit=limit)[pos]
                            soup_func = match
                            if DEBUG: logger.debug('Matches[500] (%s/%s): %s' % (len(match) if isinstance(match, list) else 1, 
                                                                                 len(str(match)), str(match)[:500]))

                        if level == 'get_text':
                            match = soup_func(tag or '', strip=strip)
                            if regex:
                                if not isinstance(regex, list): regex = [regex]
                                for reg in regex:
                                    match = scrapertools.find_single_match(str(match), reg)
                            if regex_sub:
                                for reg_org, reg_des in regex_sub:
                                    match = re.sub(reg_org, reg_des, str(match))
                            if split:
                                match = str(match).split(split)
                        elif regex or regex_sub:
                            if len(str(pos)) > 0 or not tag:
                                if argument:
                                    for arg in argument:
                                        if not match.get(arg): continue
                                        match = match.get(arg)
                                        break
                                    else:
                                        match = None
                                else:
                                    match = match.text
                            if len(str(pos)) == 0 or not match:
                                if argument:
                                    for arg in argument:
                                        if not soup_func(tag, attrs=attrs, string=string).get(arg): continue
                                        match = soup_func(tag, attrs=attrs, string=string).get(arg)
                                        break
                                    else:
                                        match = None
                                else:
                                    match = soup_func(tag, attrs=attrs, string=string).text
                            if regex:
                                if not isinstance(regex, list): regex = [regex]
                                for reg in regex:
                                    match = scrapertools.find_single_match(str(match), reg)
                            if regex_sub:
                                for reg_org, reg_des in regex_sub:
                                    match = re.sub(reg_org, reg_des, str(match))
                        elif '_all' in level and len(str(pos)) == 0:
                            match = soup_func_all(tag, attrs=attrs, string=string, limit=limit)
                            if match and argument:
                                matches_int = match[:]
                                match = []
                                for mate in matches_int:
                                    for arg in argument:
                                        if mate.get(arg):
                                            match.append(mate.get(arg))
                            tagOR_save_all.extend(match)
                        elif argument:
                            if len(str(pos)) > 0 or not tag:
                                for arg in argument:
                                    if not match.get(arg): continue
                                    match = match.get(arg)
                                    break
                                else:
                                    match = None
                            else:
                                for arg in argument:
                                    if not soup_func(tag, attrs=attrs, string=string).get(arg): continue
                                    match = soup_func(tag, attrs=attrs, string=string).get(arg)
                                    break
                                else:
                                    match = None
                        else:
                            if len(str(pos)) == 0:
                                match = soup_func(tag, attrs=attrs, string=string)

                    else:
                        match = soup_func_all(tag, attrs=attrs, string=string, limit=limit)
                        if match and argument:
                            matches_int = match[:]
                            match = []
                            for mate in matches_int:
                                for arg in argument:
                                    if mate.get(arg):
                                        match.append(mate.get(arg))
                        tagOR_save_all.extend(match)

                    if DEBUG and x < len(finds)-1: logger.debug('Matches[500] (%s/%s): %s' % (len(match) if isinstance(match, list) else 1, 
                                                                                              len(str(match)), str(match)[:500]))
                    if not match:
                        if tagOR:
                            if '_all' in level:
                                match = tagOR_save
                            else:
                                match = tagOR
                            continue
                        if tagOR_save:
                            if '_all' in level:
                                match = tagOR_save_all
                            else:
                                match = tagOR_save
                            tagOR_save = {}
                            break
                        break
                    if match:
                        if tagOR:
                            if y < len(f)-1:
                                if '_all' in level:
                                    match = tagOR_save
                                else:
                                    tagOR_save = match
                                continue
                            break
                        continue

                if not match: break

            if json:
                try:
                    if DEBUG: logger.debug('Json[500] (%s/%s): "%s" / %s' % (len(match) if isinstance(match, list) else 1, 
                                                                           len(str(match)), str(json), str(match)[:500]))
                    json_all_work = {}
                    json_all = jsontools.load(match)
                    if json_all:
                        match = []
                        if str(json) == 'DEFAULT':
                            json = {}
                            match = json_all
                        elif str(json).endswith('DEFAULT'):
                            key_org, key_des = str(json).split('|')
                            key_org = key_org.split(',')
                            match = json_all
                            for key_org_item in key_org:
                                key_org_item_alt = key_org_item.split('/')
                                for key_org_alt in key_org_item_alt:
                                    if not key_org_alt: continue
                                    if '&' not in key_org_alt:
                                        if match.get(key_org_alt, []):
                                            match = match.get(key_org_alt, [])
                                            break
                                    else:
                                        key_org_item_and = key_org_alt.split('&')
                                        match_and = []
                                        for key_org_and in key_org_item_and:
                                            if not key_org_and: continue
                                            if match.get(key_org_and, []):
                                                match_and.extend(match.get(key_org_and, []))
                                        match = match_and[:]
                        else:
                            json_match = {}
                            if json_match: json = {}
                            for json_field in json:
                                json_all_work = json_all.copy()
                                key_org, key_des = json_field.split('|')
                                key_org = key_org.split(',')
                                for key_org_item in key_org:
                                    json_match[key_des] = json_all_work.get(key_org_item, '')
                                    json_all_work = json_all_work.get(key_org_item, {})
                            match.append(json_match.copy())
                except Exception:
                    match = []
                    logger.error('Json[500] (%s/%s): %s' % (len(json_all_work.keys()), 
                                                            len(str(json_all_work)), str(json_all_work)[:500]))
                    logger.error(traceback.format_exc())
            
            if tagOR_save_all: match = tagOR_save_all
            if DEBUG: logger.debug('Matches[500] (%s/%s): %s' % (len(match) if isinstance(match, list) else 1, 
                                                                 len(str(match)), str(match)[:500]))
            
            matches = matches_init if not match else match
        except Exception:
            logger.error('LEVEL: %s, BLOCK; %s, FUNC: %s, MATCHES-TYPE: %s, MATCHES[500]: %s' \
                         % (level, block, f, str(type(match)), str(match)[:500]))
            matches = matches_init
            logger.error(traceback.format_exc())

        return matches


class CustomChannel(AlfaChannelHelper):
    pass


class DictionaryAllChannel(AlfaChannelHelper):

    def list_all(self, item, data='', matches_post=None, postprocess=None, generictools=None, finds={}, **kwargs):
        logger.info()
        from core import tmdb

        itemlist = list()
        matches = []
        matches_list_all = []
        if not matches_post and item.matches_post: matches_post = item.matches_post

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        if DEBUG: logger.debug('FINDS: %s' % finds)
        finds_out = finds.get('find', {})
        if item.c_type == 'search' and finds.get('search', {}): finds_out = finds.get('search', {})
        finds_next_page = finds.get('next_page', {})
        finds_next_page_rgx = finds.get('next_page_rgx') if finds.get('next_page_rgx') else [['page\/\d+\/', 'page/%s/']]
        finds_last_page = finds.get('last_page', {})
        finds_year = finds.get('year', {})
        finds_season_episode = finds.get('season_episode', {})
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)

        AHkwargs = {'url': item.url, 'soup': item.matches or {}, 'finds': finds, 'kwargs': kwargs, 'function': 'list_all', 
                    'function_alt': kwargs.get('function', '')}
        AHkwargs['matches_post_list_all'] = matches_post or kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)
        matches_post_json_force = kwargs.pop('matches_post_json_force', False)

        # Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
        title_lista = []                                        # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
        if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
            title_lista.extend(item.title_lista)                                # Se usa la lista de páginas anteriores en Item
            del item.title_lista                                                # ... limpiamos
        if 'text_bold' in item: del item.text_bold

        self.curr_page = 1                                                      # Página inicial
        self.last_page = 99999 if (not isinstance(finds_last_page, bool) \
                                   and not finds_controls.get('custom_pagination', False)) \
                                  else 9999 if finds_controls.get('custom_pagination', False) else 0    # Última página inicial
        last_page_print = 1                                                     # Última página inicial, para píe de página
        page_factor = finds_controls.get('page_factor', 1.0 )                   # Factor de conversión de pag. web a pag. Alfa
        self.cnt_tot = 99 if item.extra == 'find_seasons' else finds_controls.get('cnt_tot', 20)    # Poner el num. máximo de items por página
        cnt_tot_ovf = finds_controls.get('page_factor_overflow', 1.3)           # Overflow al num. máximo de items por página
        cnt_match = 0                                                           # Contador de matches procesadas
        cnt_title = 0                                                           # Contador de líneas insertadas en Itemlist
        cnt_tot_match = 0.0                                                     # Contador TOTAL de líneas procesadas de matches
        custom_pagination =  finds_controls.get('custom_pagination', False)     # Paginación controlada por el usuario
        if 'cnt_tot_match' in item:
            cnt_tot_match = float(item.cnt_tot_match)                           # restauramos el contador TOTAL de líneas procesadas de matches
            del item.cnt_tot_match
        if 'curr_page' in item:
            self.curr_page = int(item.curr_page)                                # Si viene de una pasada anterior, lo usamos
            del item.curr_page                                                  # ... y lo borramos
        if 'last_page' in item:
            self.last_page = int(item.last_page)                                # Si viene de una pasada anterior, lo usamos
            del item.last_page                                                  # ... y lo borramos
        if 'page_factor' in item:
            page_factor = float(item.page_factor)                               # Si viene de una pasada anterior, lo usamos
            del item.page_factor                                                # ... y lo borramos
        if 'last_page_print' in item:
            last_page_print = item.last_page_print                              # Si viene de una pasada anterior, lo usamos
            del item.last_page_print                                            # ... y lo borramos
        if 'title' in item.infoLabels:
            del item.infoLabels['title']                                        # ... y lo borramos
        if 'season_search' in item and item.extra != 'find_seasons':
            del item.season_search                                              # ... y lo borramos
        if 'unify' in item:
            del item.unify                                                      # ... y lo borramos

        inicio = time.time()                                                    # Controlaremos que el proceso no exceda de un tiempo razonable
        fin = inicio + finds_controls.get('inicio', 5 if not item.extra == 'find_seasons' else 30)  # Después de este tiempo pintamos (segundos)
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)     # Timeout normal
        timeout_search = timeout * 2                                            # Timeout para búsquedas

        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)

        filter_languages = config.get_setting('filter_languages', item.channel, default=0)
        modo_grafico = config.get_setting('modo_grafico', item.channel, default=True)
        idioma_busqueda = 0
        if not filter_languages: filter_languages = 0

        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)
        #if self.btdigg: self.cnt_tot = finds_controls.get('cnt_tot', 20)

        self.next_page_url = next_page_url = item.url
        episodios = False
        # Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
        while (cnt_title < self.cnt_tot and (self.curr_page <= self.last_page or (self.last_page == 0 and finds_next_page \
                                             and next_page_url and (item.matches or matches))) \
                                        and fin > time.time()) \
                                        or item.matches:
            
            # Descarga la página
            soup = data
            data = ''
            cnt_match = 0                                                       # Contador de líneas procesadas de matches
            if not item.matches and next_page_url:                              # si no viene de una pasada anterior, descargamos
                kwargs.update({'timeout': timeout_search, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
                soup = soup or self.create_soup(next_page_url, **kwargs)

                itemlist = self.itemlist + itemlist
                self.itemlist = []

                if self.url:
                    if DEBUG: logger.debug('self.URL: %s / %s' % (next_page_url, self.url))
                    self.next_page_url = next_page_url = item.url = self.url
                    self.url = ''
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if not scrapertools.find_single_match(item.url, rgx_org): continue
                        item.url = re.sub(rgx_org, rgx_des % str(self.curr_page), item.url.rstrip('/')).replace('//?', '/?')
                if soup:
                    AHkwargs['soup'] = self.response.soup or self.response.json or self.response.data
                    self.curr_page += 1
                    matches_list_all = self.parse_finds_dict(soup, finds_out) if finds_out \
                                       else (self.response.soup or self.response.json or self.response.data)
                    if not isinstance(matches_list_all, (list, _dict)):
                        matches = []
                    if matches_post and matches_list_all:
                        matches = matches_post(item, matches_list_all, **AHkwargs)
                        if custom_pagination:
                            if len(matches) < self.cnt_tot:
                                custom_pagination = False
                                self.last_page = 0

                    if ((self.btdigg and item.extra == 'novedades') or (self.btdigg_search \
                                     and item.c_type == 'search' and item.extra != 'find_seasons')) \
                                     and not item.btdig_in_use:
                        if 'matches' in  AHkwargs: del AHkwargs['matches']
                        matches = self.find_btdigg_list_all(item, matches, finds_controls.get('channel_alt', DOMAIN_ALT), **AHkwargs)

                    if not matches and item.extra != 'continue':
                        logger.error('NO MATCHES: %s' % finds_out)
                        if AHkwargs.get('function_alt', '') == 'find_seasons' or item.c_type in ['search'] or self.last_page in [9999]:
                            self.last_page = 0
                        if not (finds_last_page and self.last_page > 0 and self.last_page not in [9999, 99999] \
                                                and self.curr_page <= self.last_page):
                            if AHkwargs.get('function_alt', '') != 'find_seasons' and item.c_type not in ['search']:
                                logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or section_list)
                            break

            else:
                matches =  AHkwargs['soup'] = item.matches
                if not matches: 
                    custom_pagination = False
                    self.last_page = 0
                    break
                del item.matches
                if matches_post_json_force and matches_post and matches: 
                    matches = matches_post(item, matches, **AHkwargs)
                    if custom_pagination:
                        if len(matches) < self.cnt_tot:
                            custom_pagination = False
                            self.last_page = 0

            AHkwargs['matches'] = matches
            if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))

            # Refrescamos variables posiblemente actualizadas en "matches_post"
            finds = self.finds.copy()
            finds_controls = finds.get('controls', {})
            self.cnt_tot = self.cnt_tot or finds_controls.get('cnt_tot', 20)
            host = finds_controls.get('host', self.host)
            self.doo_url = "%swp-admin/admin-ajax.php" % host
            if AHkwargs.get('url') and AHkwargs['url'] != item.url: self.next_page_url = next_page_url = item.url
            next_page_url = self.next_page_url
            host_referer = finds_controls.get('host_referer', host) or host_referer
            post = item.post or finds_controls.pop('post', None) or post
            headers = item.headers or finds_controls.get('headers', {}) or headers
            url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
            url_base64 = finds_controls.get('url_base64', True)
            modo_grafico = finds_controls.get('modo_grafico', modo_grafico)
            IDIOMAS_TMDB = finds_controls.get('IDIOMAS_TMDB', {}) or self.IDIOMAS_TMDB
            idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', item.channel, default=0)]    # Idioma base para TMDB
            if not idioma_busqueda: idioma_busqueda = 0
            idioma_busqueda_org = idioma_busqueda
            idioma_busqueda_save = ''
            idioma_busqueda_VO = IDIOMAS_TMDB[2]                                # Idioma para VO: Local,VO
            self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
            self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

            # Buscamos la próxima página
            if soup:
                if finds_next_page:
                    next_page_url_save = next_page_url
                    next_page_url = self.parse_finds_dict(soup, finds_next_page, next_page=True, c_type=item.c_type).lstrip('#')
                    if next_page_url_save == next_page_url:
                        next_page_url = ''
                        self.last_page = 0
                    elif next_page_url: 
                        next_page_url = self.urljoin(self.host, next_page_url)
                        self.last_page = 9999 if self.last_page in [0, 9999, 99999] else self.last_page
                    elif not next_page_url: 
                        next_page_url = item.url
                        self.last_page = 0

                elif self.last_page > 0 and not custom_pagination:
                    url_page = item.url
                    url_page_control = 'url'
                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list):
                        if finds_controls['force_find_last_page'][2] == 'post': 
                            url_page = post
                            url_page_control = 'post'
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if scrapertools.find_single_match(url_page, rgx_org): break
                    else:
                        url = item.url.split('?')
                        item.url = url[0].rstrip('/') + finds_next_page_rgx[0][1] % str(self.curr_page)
                        if '?' in item.url and len(url) > 1: url[1] = url[1].replace('?', '&')
                        if len(url) > 1: item.url = '%s?%s' % (item.url, url[1].lstrip('/'))
                    next_page_url = item.url
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if url_page_control == 'url':
                            if not scrapertools.find_single_match(next_page_url, rgx_org): continue
                            next_page_url = re.sub(rgx_org, rgx_des % str(self.curr_page), next_page_url.rstrip('/')).replace('//?', '/?')
                        else:
                            if not scrapertools.find_single_match(post, rgx_org): continue
                            post = re.sub(rgx_org, rgx_des % str(self.curr_page), post.rstrip('/')).replace('//?', '/?')

                self.next_page_url = next_page_url

            if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                    % (str(self.curr_page), str(self.last_page), str(page_factor), str(next_page_url), len(matches)))

            # Buscamos la última página
            if self.last_page == 99999:                                         # Si es el valor inicial, buscamos
                try:
                    self.last_page = int(self.parse_finds_dict(soup, finds_last_page, next_page=True, c_type=item.c_type).lstrip('#'))
                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list) \
                                           and isinstance(finds_controls['force_find_last_page'][0], int) \
                                           and isinstance(finds_controls['force_find_last_page'][1], int):
                        if self.last_page >= finds_controls['force_find_last_page'][0]:
                            url = next_page_url
                            for rgx_org, rgx_des in finds_next_page_rgx:
                                if not scrapertools.find_single_match(url, rgx_org): continue
                                url = re.sub(rgx_org, rgx_des % str(finds_controls['force_find_last_page'][1]), 
                                             url.rstrip('/')).replace('//?', '/?')
                            soup_last_page = self.create_soup(url, hide_infobox=True, **kwargs)
                            self.last_page = int(self.parse_finds_dict(soup_last_page, finds_last_page, next_page=True, 
                                                                  c_type=item.c_type).lstrip('#'))
                    page_factor = float(len(matches)) / float(self.cnt_tot)
                except Exception:
                    self.last_page = 0
                    last_page_print = int((float(len(matches)) / float(self.cnt_tot)) + 0.999999)

                if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                        % (str(self.curr_page), str(self.last_page), str(page_factor), str(next_page_url), len(matches)))

            if item.matches_org is True: item.matches_org = matches[:]
            for elem in matches:
                new_item = Item()
                new_item.infoLabels = item.infoLabels.copy()
                if new_item.infoLabels['plot']: del new_item.infoLabels['plot']
                cnt_match += 1

                new_item.channel = item.channel
                new_item.category = new_item.channel.capitalize()

                new_item.url = elem.get('url', '')
                if not new_item.url: continue
                new_item.url = self.urljoin(self.host, new_item.url)
                
                new_item.title = elem.get('title', '')
                for clean_org, clean_des in finds.get('title_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.title, clean_org):
                            new_item.title = scrapertools.find_single_match(new_item.title, clean_org).strip()
                            break
                    else:
                        new_item.title = re.sub(clean_org, clean_des, new_item.title).strip()
                # Slugify, pero más light
                new_item.title = scrapertools.htmlclean(new_item.title).strip()
                new_item.title = new_item.title.replace("á", "a").replace("é", "e").replace("í", "i")\
                                               .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                                               .replace("ï¿½", "ñ").replace("Ã±", "ñ")
                new_item.title = scrapertools.decode_utf8_error(new_item.title).strip()
                if not new_item.title: continue

                if elem.get('thumbnail', ''): 
                    elem['thumbnail'] = elem['thumbnail'] if elem['thumbnail'].startswith('http') \
                                                             else 'https:' + elem['thumbnail'] if elem['thumbnail'].startswith('//') \
                                                             else self.urljoin(self.host, elem['thumbnail'])
                    if ('tmdb' in elem['thumbnail'] or 'imdb' in elem['thumbnail']) and '=http' in elem['thumbnail']:
                        elem['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem['thumbnail']), '=(.*?)[&|$]')
                    new_item.thumbnail = elem['thumbnail']

                if elem.get('quality', ''):
                    new_item.quality = elem['quality']
                    for clean_org, clean_des in finds.get('quality_clean', []):
                        if clean_des is None:
                            if scrapertools.find_single_match(new_item.quality, clean_org):
                                new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                                break
                        else:
                            new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
                if str(elem.get('quality', '')).startswith('*'):
                    elem['quality'] = new_item.quality
                    new_item.quality = self.find_quality(elem, item)

                # Salvo que venga la llamada desde Episodios, se filtran las entradas para evitar duplicados de Temporadas
                if isinstance(finds_controls.get('duplicates', False), list) and \
                             (item.c_type == 'documentales' or self.tv_path in new_item.url \
                              or (finds_controls.get('dup_movies', False) and self.movie_path in new_item.url)) \
                              and item.c_type != 'episodios' and item.extra != 'find_seasons':
                    url_list = new_item.url
                    if finds_controls.get('dup_list', '') == 'title':
                        url_list = scrapertools.slugify(new_item.title)
                        if finds_controls.get('btdigg_quality_control') and new_item.quality:
                            url_list += ' [%s]' % new_item.quality.replace(BTDIGG_LABEL, '')

                    for dup_org, dup_des in finds_controls['duplicates']:
                        if self.tv_path in new_item.url:
                            url_list = re.sub(dup_org, dup_des, url_list).rstrip('/')
                    if url_list in title_lista:                                 # Si ya hemos procesado el título, lo ignoramos
                        if DEBUG: logger.debug('DUPLICADO %s' % url_list)
                        continue
                    else:
                        if DEBUG: logger.debug('AÑADIDO %s' % url_list)
                        title_lista += [url_list]                               # La añadimos a la lista de títulos

                if elem.get('language', self.language):
                    new_item.language = elem.get('language', self.language)
                    if not isinstance(new_item.language, list):
                        for clean_org, clean_des in finds.get('language_clean', []):
                            if clean_des is None:
                                if scrapertools.find_single_match(new_item.language, clean_org):
                                    new_item.language = scrapertools.find_single_match(new_item.language, clean_org).strip()
                                    break
                            else:
                                new_item.language = re.sub(clean_org, clean_des, new_item.language).strip()
                if '*' in str(elem.get('language', '')):
                    elem['language'] = new_item.language
                    new_item.language = self.find_language(elem, item)

                if 'CAST' in str(new_item.language) or 'LAT' in str(new_item.language) or 'DUAL' in str(new_item.language):
                    idioma_busqueda_save = idioma_busqueda
                if 'VO' in str(new_item.language) and not idioma_busqueda_save:
                    idioma_busqueda = idioma_busqueda_VO

                if elem.get('extra', ''): new_item.extra =  elem['extra']
                if elem.get('title_subs', []): new_item.title_subs =  elem['title_subs']; generictools = True
                if elem.get('plot', ''): new_item.contentPlot =  elem['plot']
                if elem.get('broadcast', ''): new_item.broadcast = elem['broadcast']
                if elem.get('plot_extend', ''): new_item.plot_extend =  elem['plot_extend']
                if 'plot_extend_show' in elem: new_item.plot_extend_show = elem['plot_extend_show']
                if elem.get('info', ''): new_item.info =  elem['info']
                if finds_controls.get('mediatype', ''): new_item.contentType = finds_controls['mediatype']
                if finds_controls.get('action', ''): new_item.action = finds_controls['action']
                if elem.get('action', ''): new_item.action = elem['action']
                if elem.get('btdig_in_use', ''): new_item.btdig_in_use =  elem['btdig_in_use']
                if elem.get('imdb_id', ''): new_item.infoLabels['imdb_id'] =  elem['imdb_id']
                if elem.get('tmdb_id', ''): new_item.infoLabels['tmdb_id'] =  elem['tmdb_id']
                if elem.get('tvdb_id', ''): new_item.infoLabels['tvdb_id'] =  elem['tvdb_id']
                if elem.get('playcount', 0): new_item.infoLabels['playcount'] =  elem['playcount']
                if 'unify' in elem: new_item.unify = elem['unify']
                new_item.season_search = '*%s' % elem.get('season_search', '')

                try:
                    new_item.infoLabels['year'] = int(elem['year'])
                except Exception:
                    new_item.infoLabels['year'] = '-'

                if item.c_type == 'episodios' or elem.get('mediatype', '') == 'episode':
                    new_item.contentType = 'episode'
                    new_item.contentSeason = int(elem.get('season', '1') or '1')
                    new_item.contentEpisodeNumber = int(elem.get('episode', '1') or '1')
                    if elem.get('title_episode', '') and new_item.title: new_item.contentSerieName = new_item.title
                    new_item.title = '%sx%s - %s' % (new_item.contentSeason, new_item.contentEpisodeNumber, 
                                                     elem.get('title_episode', '') or new_item.title)
                    episodios = True
                    if generictools is not False: generictools = True

                if elem.get('mediatype', ''): new_item.contentType = elem['mediatype']
                elif item.c_type == 'peliculas': new_item.contentType = 'movie'
                new_item = self.define_content_type(new_item, contentType=new_item.contentType)

                new_item.context = ['buscar_trailer']
                if elem.get('context', []): new_item.context.extend(elem['context'])
                new_item.context = filtertools.context(new_item, self.list_language, self.list_quality_movies \
                                                       if new_item.contentType == 'movie' else self.list_quality_tvshow)

                if elem.get('post', None): new_item.post = elem['post']
                if elem.get('headers', None): new_item.headers = elem['headers']
                if elem.get('action', ''): new_item.action = elem['action']
                
                new_item.url = self.do_url_replace(new_item.url, url_replace)

                if postprocess:
                    new_item = postprocess(elem, new_item, item, **AHkwargs)

                if new_item:
                    cnt_title += 1

                    if new_item and not new_item.matches and (new_item.url.startswith('magnet') or new_item.url.endswith('.torrent') \
                                                 or elem.get('matches', [])):
                        new_item.matches = []
                        new_item.matches.append(elem.get('matches', []) or elem.copy())

                    #Ahora se filtra por idioma, si procede, y se pinta lo que vale
                    if filter_languages > 0 and self.list_language:             # Si hay idioma seleccionado, se filtra
                        itemlist = filtertools.get_link(itemlist, new_item, self.list_language)
                    else:
                        itemlist.append(new_item.clone())                       # Si no, se añade a la lista

                    cnt_title = len(itemlist)                                   # Recalculamos los items después del filtrado
                    # Contador de líneas añadidas
                    if cnt_title >= self.cnt_tot and (len(matches) - cnt_match) + cnt_title > self.cnt_tot * cnt_tot_ovf:
                        break
                    
                    #if DEBUG: logger.debug('New_item: %s' % new_item)

            matches = matches[cnt_match:]                                       # Salvamos la entradas no procesadas
            cnt_tot_match += cnt_match                                          # Calcular el num. total de items mostrados

        if DEBUG: logger.debug('curr_page: %s / last_page: %s / cnt_match: %s / cnt_tot: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                % (str(self.curr_page), str(self.last_page), str(cnt_match), str(self.cnt_tot), 
                                   str(page_factor), str(next_page_url), len(matches)))

        if itemlist:
            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico and not self.httptools.TEST_ON_AIR
            if not isinstance(finds_controls.get('tmdb_extended_info', True), bool):
                if episodios: tmdb.set_infoLabels_itemlist(itemlist, modo_grafico, idioma_busqueda=idioma_busqueda)
                tmdb_extended_info = False
            else:
                tmdb_extended_info = not finds_controls.get('tmdb_extended_info', True)     # Info de TMDB extendida para Series y Episodios
            tmdb.set_infoLabels_itemlist(itemlist, modo_grafico, idioma_busqueda=idioma_busqueda, extended_info=tmdb_extended_info)
            
            # Marcamos los items si están filtrados
            itemlist = self.check_filter(item, itemlist, **AHkwargs)

            for new_item in itemlist:
                if new_item.season_search == '*':
                    new_item.season_search = new_item.contentSerieName if new_item.contentType != 'movie' else new_item.contentTitle
                else:
                    new_item.season_search = new_item.season_search.lstrip('*')
                if not isinstance(new_item.infoLabels['year'], int):
                    new_item.infoLabels['year'] = str(new_item.infoLabels['year']).replace('-', '')
                if new_item.broadcast:
                    new_item.contentPlot = '%s\n\n%s' % (new_item.broadcast, new_item.contentPlot)
                    del new_item.broadcast

            if item.extra != 'find_seasons':
                if generictools:
                    # Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
                    from lib.generictools import AH_post_tmdb_listado
                    item, itemlist = AH_post_tmdb_listado(item, itemlist, **AHkwargs)
                if videolab_status:
                    # Llamamos al método para encontrar el estado del vídeo en la videoteca
                    from lib.generictools import AH_find_videolab_status
                    itemlist = AH_find_videolab_status(item, itemlist, **AHkwargs)

        # Si es necesario añadir paginacion
        if ((((self.curr_page <= self.last_page and self.last_page < 999999) \
                                          or (cnt_match > self.cnt_tot and len(matches) > 0  and next_page_url and not self.btdigg)\
                                          or len(matches) > 0) \
                                      and (next_page_url or len(matches) > 0)) or custom_pagination) \
                                      and AHkwargs['function'] != 'find_seasons':

            curr_page_print = int(cnt_tot_match / float(self.cnt_tot))
            if curr_page_print < 1:
                curr_page_print = 1
            if self.last_page and self.last_page not in [9999]:
                if self.last_page > 1:
                    last_page_print = int((self.last_page * page_factor) + 0.999999)
                title = '%s de %s' % (curr_page_print, last_page_print)
            else:
                title = '%s' % curr_page_print
            title = ">> Página siguiente %s" % title
            if item.infoLabels.get('mediatype'): del item.infoLabels['mediatype']

            if finds_controls.get('jump_page') and self.last_page:
                itemlist.append(item.clone(action="get_page_num", to_action="list_all", title="[B]>> Ir a Página...[/B]", unify=False, 
                                           title_lista=title_lista, post=post, matches=matches, 
                                           url=next_page_url, last_page=str(self.last_page), curr_page=str(self.curr_page), 
                                           page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), 
                                           last_page_print=last_page_print, custom_pagination=custom_pagination))

            itemlist.append(item.clone(action="list_all", title=title, unify=False, 
                                       title_lista=title_lista, post=post, matches=matches, 
                                       url=next_page_url, last_page=str(self.last_page), curr_page=str(self.curr_page), 
                                       page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), 
                                       last_page_print=last_page_print))

        return itemlist

    def section(self, item, data= '', action="list_all", matches_post=None, postprocess=None, 
                section_list={}, finds={}, **kwargs):
        logger.info()

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        finds_out = finds.get('categories', {})
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)
        itemlist = list()
        matches = list()
        matches_section = list()
        soup = {}
        if not matches_post and item.matches_post: matches_post = item.matches_post
        if item.contentPlot: del item.infoLabels['plot']

        AHkwargs = {'soup': soup, 'finds': finds, 'kwargs': kwargs, 'function': 'section'}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = matches_post or kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)

        if DEBUG: logger.debug('FINDS_categories: %s; FINDS_controls: %s' % (finds_out, finds_controls))

        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)

        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

        if section_list:
            for genre, url in list(section_list.items()):
                matches.append({'url': url, 'title': genre})
        else:
            kwargs.update({'timeout': timeout, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
            soup = data or self.create_soup(item.url, **kwargs)

            itemlist = self.itemlist + itemlist
            self.itemlist = []

            AHkwargs['soup'] = self.response.soup or self.response.json or self.response.data
            matches_section = self.parse_finds_dict(soup, finds_out) if finds_out \
                              else (self.response.soup or self.response.json or self.response.data)
            if not isinstance(matches_section, (list, _dict)):
                matches_section = []

            if not matches and matches_section and ('profile' in finds_controls or not matches_post):
                for elem in matches_section:
                    elem_json = {}
                    
                    if profile in [DEFAULT]:
                        try:
                            elem_json['url'] = elem.a.get("href", '') if elem.a else elem.get("href", '') or elem.get("value", '')
                            elem_json['title'] = elem.a.get_text(strip=True) if elem.a else elem.get_text(strip=True)
                            
                            # External Labels
                            if finds.get('profile_labels', {}).get('section_url'):
                                url = self.parse_finds_dict(elem, finds['profile_labels']['section_url'])
                                if url: elem_json['url'] = url
                            if finds.get('profile_labels', {}).get('findvideos_title'):
                                title = self.parse_finds_dict(elem, finds['profile_labels']['section_title'])
                                if title: elem_json['title'] = title

                        except Exception:
                            elem_json['url'] = elem.get("href", '')
                            elem_json['title'] = elem.get_text(strip=True)
                            logger.error(traceback.format_exc())
                    
                    matches.append(elem_json.copy())
                AHkwargs['matches'] = matches
            
            if matches_post and matches_section:
                matches = matches_post(item, matches_section, **AHkwargs)

        if not matches:
            logger.error('NO MATCHES: %s' % finds_out)
            logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or section_list)
            return itemlist

        AHkwargs['matches'] = matches
        if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))
        
        # Refrescamos variables posiblemente actualizadas en "matches_post"
        finds = self.finds.copy()
        finds_controls = finds.get('controls', {})
        year = finds_controls.get('year', False)
        reverse = finds_controls.get('reverse', False)
        host_referer = finds_controls.get('host_referer', host) or host_referer
        post = item.post or finds_controls.pop('post', None) or post
        headers = item.headers or finds_controls.get('headers', {}) or headers
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)
        
        for elem in matches:
            if not elem.get('url'): continue
            elem['url'] = self.urljoin(self.host, elem['url'])
            if elem.get('thumbnail', ''): 
                elem['thumbnail'] = elem['thumbnail'] if elem['thumbnail'].startswith('http') \
                                                         else 'https:' + elem['thumbnail'] if elem['thumbnail'].startswith('//') \
                                                         else self.urljoin(self.host, elem['thumbnail'])
                if ('tmdb' in elem['thumbnail'] or 'imdb' in elem['thumbnail']) and '=http' in elem['thumbnail']:
                    elem['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem['thumbnail']), '=(.*?)[&|$]')

            new_item = item.clone(
                                  category=item.channel.capitalize(),
                                  title=elem.get('title', '').title(),
                                  action=action,
                                  url=elem.get('url', ''),
                                  thumbnail=elem.get('thumbnail', item.thumbnail)
                                  )

            if item.extra: new_item.extra = item.extra
            if elem.get('extra', ''): new_item.extra = elem['extra']
            if 'post' in new_item: del new_item.post
            if elem.get('post', None): new_item.post = elem['post']
            if 'headers' in new_item: del new_item.headers
            if elem.get('headers', None): new_item.headers = elem['headers']
            if elem.get('context', []): new_item.context = [elem['context']]
            if elem.get('broadcast', ''): new_item.contentPlot = '%s\n\n%s' % (elem['broadcast'], new_item.contentPlot)
            if elem.get('plot_extend', ''): new_item.plot_extend = elem['plot_extend']
            if 'plot_extend_show' in elem: new_item.plot_extend_show = elem['plot_extend_show']
            if finds_controls.get('mediatype', ''): new_item.contentType = finds_controls['mediatype']
            if finds_controls.get('action', ''): new_item.action = finds_controls['action']
            if elem.get('action', ''): new_item.action = elem['action']
            if year and scrapertools.find_single_match(new_item.title, '\d{4}'):
                new_item.infoLabels = {'year': int(scrapertools.find_single_match(new_item.title, '\d{4}'))}
            
            if elem.get('quality', ''):
                new_item.quality = elem['quality']
                for clean_org, clean_des in finds.get('quality_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.quality, clean_org):
                            new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                            break
                    else:
                        new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
            if str(elem.get('quality', '')).startswith('*'):
                elem['quality'] = new_item.quality
                new_item.quality = self.find_quality(elem, item)

            if elem.get('language', self.language):
                new_item.language = elem.get('language', self.language)
                for clean_org, clean_des in finds.get('language_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.language, clean_org):
                            new_item.language = scrapertools.find_single_match(new_item.language, clean_org).strip()
                            break
                    else:
                        new_item.language = re.sub(clean_org, clean_des, new_item.language).strip()
            if '*' in str(elem.get('language', '')):
                elem['language'] = new_item.language
                new_item.language = self.find_language(elem, item)

            new_item.url = self.do_url_replace(new_item.url, url_replace)

            if postprocess:
                new_item = postprocess(elem, new_item, item, **AHkwargs)

            if new_item: itemlist.append(new_item.clone())

        if reverse:
            return itemlist[::-1]

        return itemlist

    def seasons(self, item, data='', action="episodesxseason", matches_post=None, postprocess=None, 
                seasons_search_post=None, generictools=True, seasons_list={}, finds={}, **kwargs):
        from lib.generictools import AH_post_tmdb_seasons, AH_find_videolab_status
        from core import tmdb

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        finds_out = finds.get('seasons', {})
        finds_season_num = finds.get('season_num', {})
        finds_seasons_search = finds.get('controls', {}).get('seasons_search', False)
        find_seasons_search_num_rgx = finds.get('seasons_search_num_rgx', '')
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)
        itemlist = list()
        matches = list()
        matches_seasons = list()
        soup = {}
        if not matches_post and item.matches_post: matches_post = item.matches_post

        self.btdigg = finds_controls.get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

        AHkwargs = {'url': item.url, 'soup': soup, 'finds': finds, 'kwargs': kwargs, 'function': 'seasons'}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = matches_post or kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)

        logger.info('Serie: %s; Seasons_search: %s' % (item.contentSerieName, finds_seasons_search))

        if DEBUG: logger.debug('FINDS_seasons: %s; FINDS_season_num: %s; FINDS_controls: %s' \
                                % (finds_out, finds_season_num, finds_controls))

        item.title  = item.title.replace('(V)-' , '')
        item.contentTitle  = item.contentTitle.replace('(V)-' , '')
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        url_replace = self.url_replace = self.finds.get('url_replace', [])
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)

        last_season_only = config.get_setting('last_season_only', 'videolibrary', default=False)
        modo_ultima_temp = AHkwargs['modo_ultima_temp'] = last_season_only \
                                                          or config.get_setting('seleccionar_ult_temporadda_activa', item.channel, default=True)
        no_pile_on_seasons = config.get_setting('no_pile_on_seasons', 'videolibrary', default=1)       
        self.season_colapse = config.get_setting('season_colapse', item.channel, default=True if no_pile_on_seasons <= 1 else False)
        if no_pile_on_seasons == 2: self.season_colapse = False
        if item.season_colapse == False: self.season_colapse = item.season_colapse
        AHkwargs['season_colapse'] = self.season_colapse
        filter_languages = config.get_setting('filter_languages', item.channel, default=0)
        modo_grafico = True if (item.library_urls or finds_seasons_search or self.btdigg ) \
                                else config.get_setting('modo_grafico', item.channel, default=True)
        idioma_busqueda = 0
        if not filter_languages: filter_languages = 0

        item.context = []
        item.context = filtertools.context(item, self.list_language, self.list_quality_tvshow)

        item.url = self.do_url_replace(item.url, url_replace)

        if item.library_urls or finds_seasons_search:
            config.set_setting('tmdb_cache_read', False)
            tmdb.set_infoLabels_item(item, modo_grafico, idioma_busqueda=idioma_busqueda)
            config.set_setting('tmdb_cache_read', True)

        if item.matches:
            matches = item.matches[:]
            del item.matches
        else:
            if BTDIGG in item.url:
                AHkwargs['function'] = 'find_seasons'
                AHkwargs['language'] = item.language or self.language
                matches = self.do_seasons_search(item, matches, **AHkwargs)
                AHkwargs['function'] = 'seasons'
                if matches:
                    if not BTDIGG in matches[0]['url']:
                        item.url = matches[0]['url']
                        if 'btdig_in_use' in item: del item.btdig_in_use

            if seasons_list:
                for elem in seasons_list:
                    elem_json = {}

                    elem_json['season'] = int(scrapertools.find_single_match(str(elem.get('season', '1')), '\d+') or '1')
                    elem_json['url'] = self.urljoin(self.host, elem.get('url', item.url))
                    elem_json['post'] = elem.get('post', None)
                    elem_json['headers'] = elem.get('headers', None)
                    if not elem.get('url', ''): continue

                    matches.append(elem_json.copy())

            elif finds_seasons_search and not BTDIGG in item.url:
                AHkwargs['function'] = 'find_seasons'
                AHkwargs['language'] = item.language or self.language
                if not matches: matches = self.do_seasons_search(item, matches, **AHkwargs)
                if matches_post and matches:
                    matches = matches_post(item, matches, **AHkwargs)
                AHkwargs['function'] = 'seasons'

            else:
                if BTDIGG in item.url:
                    soup = {}
                    matches_seasons = matches = []
                else:
                    kwargs.update({'timeout': timeout, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
                    soup = data or self.create_soup(item.url, **kwargs)

                    itemlist = self.itemlist + itemlist
                    self.itemlist = []

                    AHkwargs['soup'] = self.response.soup or self.response.json or self.response.data
                    matches_seasons = self.parse_finds_dict(soup, finds_out) if finds_out \
                                      else (self.response.soup or self.response.json or self.response.data)
                    if not isinstance(matches_seasons, (list, _dict)):
                        matches_seasons = []

                if not matches and matches_seasons and ('profile' in finds_controls or not matches_post):
                    for elem in matches_seasons:
                        elem_json = {}

                        try:
                            if profile in [DEFAULT]:
                                elem_json['season'] = elem_json.get('season', '')

                                if not elem_json.get('season'):
                                    if finds_season_num:
                                        elem_json['season'] = self.parse_finds_dict(elem, finds_season_num)
                                    if find_seasons_search_num_rgx:
                                        elem_json['season'] = scrapertools.find_single_match(elem_json.get('season', '') \
                                                                                             or str(elem), find_seasons_search_num_rgx)
                                    if not elem_json.get('season'):
                                        try:
                                            elem_json['season'] = int(elem.span.get_text(strip=True).lower().replace('temporada', ''))
                                        except Exception:
                                            try:
                                                elem_json['season'] = int(elem["value"])
                                            except Exception:
                                                try:
                                                    find_seasons_search_num_rgx = '(?i)(?:Temp|Season)[^\d]*(\d{1,2})'
                                                    elem_json['season'] = scrapertools.find_single_match(str(elem), find_seasons_search_num_rgx)
                                                except Exception:
                                                    elem_json['season'] = 1

                                if not elem_json['season']:
                                    continue
                                if "todas" in str(elem_json['season']).lower():
                                    continue
                                elif "especiales" in str(elem_json['season']).lower():
                                    elem_json['season'] = "0"

                                if elem_json.get('season'):
                                    try:
                                        elem_json['season'] = int(elem_json['season'])
                                    except Exception:
                                        elem_json['season'] = 1

                                if finds.get('season_url'):
                                    elem_json['url'] = finds['season_url'] if str(finds['season_url']) != self.host else item.url
                                if not elem_json.get('url'): elem_json['url'] = item.url if not "href" in str(elem) \
                                                     else elem.find('a').get("href", '') if (elem.find('a') and "href" in str(elem.find('a'))) \
                                                     else elem.a.get("href", '') if (elem.a and "href" in str(elem.a)) \
                                                     else elem.get("href", '') if "href" in str(elem) else item.url

                                # External Labels
                                if finds.get('profile_labels', {}).get('seasons_url'):
                                    url = self.parse_finds_dict(elem, finds['profile_labels']['seasons_url'])
                                    if url: elem_json['url'] = url
                                if not elem_json['url']: elem_json['url'] = item.url
                                if 'javascript' in elem_json['url']: elem_json['url'] = self.doo_url if post else item.url
                                if elem_json['url'].startswith('#'):
                                    elem_json['url'] = self.urljoin(item.url, elem_json['url'])
                                else:
                                    elem_json['url'] = self.urljoin(self.host, elem_json['url'])

                        except Exception:
                            logger.error(elem)
                            logger.error(traceback.format_exc())

                        matches.append(elem_json.copy())
                        AHkwargs['matches'] = matches

                if matches_post and matches_seasons:
                    matches = matches_post(item, matches_seasons, **AHkwargs)

            if self.btdigg:
                if (len(matches) < 1 and item.infoLabels.get('number_of_seasons', 1) > 1) or (len(matches) >= 1 \
                                     and matches[-1].get('season', 1) < item.infoLabels.get('number_of_seasons', 1)):
                    AHkwargs['btdigg_contentSeason'] = 1
                if 'matches' in AHkwargs: del AHkwargs['matches']
                matches = self.find_btdigg_seasons(item, matches, finds_controls.get('domain_alt', DOMAIN_ALT), **AHkwargs)

            if not matches:
                logger.error('NO MATCHES: %s' % finds_out)
                logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or seasons_list)
                return itemlist

        # Si solo hay una temporada y está configurado así, se listan los episodios directamente
        if len(matches) == 1 and no_pile_on_seasons >= 1: 
            self.season_colapse = False
        
        AHkwargs['matches'] = matches
        if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))

        # Refrescamos variables posiblemente actualizadas en "matches_post"
        finds = self.finds.copy()
        finds_controls = finds.get('controls', {})
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host) or host_referer
        post = item.post or finds_controls.pop('post', None) or post
        headers = item.headers or finds_controls.get('headers', {}) or headers
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
        url_base64 = finds_controls.get('url_base64', True)
        IDIOMAS_TMDB = finds_controls.get('IDIOMAS_TMDB', {}) or self.IDIOMAS_TMDB
        idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', item.channel, default=0)]    # Idioma base para TMDB
        if not idioma_busqueda: idioma_busqueda = 0
        idioma_busqueda_org = idioma_busqueda
        idioma_busqueda_save = ''
        idioma_busqueda_VO = IDIOMAS_TMDB[2]                                    # Idioma para VO: Local,VO
        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

        for elem in matches:
            elem['season'] = int(scrapertools.find_single_match(str(elem.get('season', '1')), '\d+') or '1')
            if item.infoLabels['number_of_seasons'] and elem['season'] > item.infoLabels['number_of_seasons']:
                logger.error('TEMPORADA ERRONEA: WEB: %s; TMDB: %s' % (elem['season'], item.infoLabels['number_of_seasons']))
                continue

            elem['url'] = elem.get('url', item.url)
            if url_base64: elem['url'] = self.convert_url_base64(elem['url'], self.host, item=item)

            if elem.get('thumbnail', ''): 
                elem['thumbnail'] = elem['thumbnail'] if elem['thumbnail'].startswith('http') \
                                                         else 'https:' + elem['thumbnail'] if elem['thumbnail'].startswith('//') \
                                                         else self.urljoin(self.host, elem['thumbnail'])
                if ('tmdb' in elem['thumbnail'] or 'imdb' in elem['thumbnail']) and '=http' in elem['thumbnail']:
                    elem['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem['thumbnail']), '=(.*?)[&|$]')

            new_item = item.clone(action=action,
                                  category=item.channel.capitalize(), 
                                  url=elem['url'], 
                                  url_tvshow = matches[-1]['url'] if finds_seasons_search else item.url, 
                                  contentSeason=elem['season'], 
                                  title=('Temporada %s' % elem['season']) if elem['season'] > 0 else 'Especiales',
                                  contentPlot=elem.get('plot', item.contentPlot), 
                                  thumbnail=elem.get('thumbnail', item.thumbnail), 
                                  contentType='season'
                                 )

            if elem.get('quality', ''):
                new_item.quality = elem['quality']
                for clean_org, clean_des in finds.get('quality_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.quality, clean_org):
                            new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                            break
                    else:
                        new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
            if str(elem.get('quality', '')).startswith('*'):
                elem['quality'] = new_item.quality
                new_item.quality = self.find_quality(elem, item)

            if elem.get('language', self.language):
                new_item.language = elem.get('language', self.language)
                for clean_org, clean_des in finds.get('language_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.language, clean_org):
                            new_item.language = scrapertools.find_single_match(new_item.language, clean_org).strip()
                            break
                    else:
                        new_item.language = re.sub(clean_org, clean_des, new_item.language).strip()
            if '*' in str(elem.get('language', '')):
                elem['language'] = new_item.language
                new_item.language = self.find_language(elem, item)

            if elem.get('extra', ''): new_item.extra = elem['extra']
            if 'post' in new_item: del new_item.post
            if elem.get('post', None): new_item.post = elem['post']
            if 'headers' in new_item: del new_item.headers
            if elem.get('headers', None): new_item.headers = elem['headers']
            if elem.get('context', []): new_item.context.extend(elem['context'])
            if elem.get('broadcast', ''): new_item.broadcast = elem['broadcast']
            if elem.get('info', None): new_item.info = elem['info']
            if elem.get('plot_extend', ''): new_item.infoLabels['plot_extend'] = elem['plot_extend']
            if 'plot_extend_show' in elem: new_item.plot_extend_show = elem['plot_extend_show']
            if finds_controls.get('mediatype', ''): new_item.contentType = finds_controls['mediatype']
            if finds_controls.get('action', ''): new_item.action = finds_controls['action']
            if elem.get('action', ''): new_item.action = elem['action']
            if item.filtertools: new_item.filtertools = item.filtertools

            new_item.url = self.do_url_replace(new_item.url, url_replace)

            if postprocess:
                new_item = postprocess(elem, new_item, item, **AHkwargs)

            if new_item: itemlist.append(new_item.clone())
            #if DEBUG: logger.debug('SEASONS: %s' % new_item)

        for new_item in itemlist:

            if new_item.quality:
                for clean_org, clean_des in finds.get('quality_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.quality, clean_org):
                            new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                            break
                    else:
                        new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
            if str(new_item.quality).startswith('*'):
                new_item.quality = self.find_quality(new_item, item)
            if not new_item.quality and item.quality:
                new_item.quality = item.quality

            if new_item.language:
                for clean_org, clean_des in finds.get('language_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.language, clean_org):
                            new_item.language = scrapertools.find_single_match(new_item.language, clean_org).strip()
                            break
                    else:
                        new_item.language = re.sub(clean_org, clean_des, new_item.language).strip()
            if '*' in str(new_item.language):
                new_item.language = self.find_language(new_item, item)
            if not new_item.language and item.language:
                new_item.language = item.language
            if 'CAST' in str(new_item.language) or 'LAT' in str(new_item.language) or 'DUAL' in str(new_item.language):
                idioma_busqueda_save = idioma_busqueda
            if 'VO' in str(new_item.language) and not idioma_busqueda_save:
                idioma_busqueda = idioma_busqueda_VO

        if itemlist:
            itemlist = sorted(itemlist, key=lambda it: int(it.contentSeason))
            if (item.infoLabels.get('last_season_only', False) and item.add_videolibrary) \
                                or (modo_ultima_temp and item.library_playcounts):
                itemlist = [itemlist[-1]]

            find_add_video_to_videolibrary = finds_controls.get('add_video_to_videolibrary', True)
            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico and not self.httptools.TEST_ON_AIR
            config.set_setting('tmdb_cache_read', False)
            tmdb.set_infoLabels_itemlist(itemlist, modo_grafico, idioma_busqueda=idioma_busqueda)
            config.set_setting('tmdb_cache_read', True)
            
            for new_item in itemlist:
                if new_item.broadcast:
                    new_item.contentPlot = '%s\n\n%s' % (new_item.broadcast, new_item.contentPlot)
                    del new_item.broadcast

            # Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
            if generictools and not (item.add_videolibrary or item.library_playcounts or item.downloadFilename):
                item, itemlist = AH_post_tmdb_seasons(item, itemlist, **AHkwargs)
            
            if find_add_video_to_videolibrary:
                if videolab_status:
                    # Llamamos al método para encontrar el estado del vídeo en la videoteca
                    itemlist = AH_find_videolab_status(item, itemlist, **AHkwargs)
                if self.season_colapse:
                    itemlist = self.add_video_to_videolibrary(item, itemlist)

        if item.add_videolibrary or item.library_playcounts or item.downloadFilename:
            return itemlist
        
        if not self.season_colapse:
            channel = __import__('channels.%s' % item.channel, None, None, ["channels.%s" % item.channel])

            if hasattr(channel, "episodesxseason"):
                templist = itemlist[:]
                itemlist = []
                add_video_to_videolibrary = finds['controls'].get('add_video_to_videolibrary', False)
                finds['controls'].update({'add_video_to_videolibrary': False})
                btdigg = finds['controls'].get('btdigg', False)
                finds['controls'].update({'btdigg': False})

                for x, tempitem in enumerate(templist):
                    if x >= len(templist) - 1:
                        finds['controls'].update({'add_video_to_videolibrary': add_video_to_videolibrary})
                        finds['controls'].update({'btdigg': btdigg})
                    if "actualizar_titulos" in tempitem.action or "_to_library" in tempitem.action: continue
                    try:
                        itemlist.extend(getattr(channel, "episodesxseason")(tempitem, **AHkwargs))
                    except Exception:
                        itemlist.extend(getattr(channel, "episodesxseason")(tempitem))

        return itemlist

    def episodes(self, item, data='', action="findvideos", matches_post=None, postprocess=None, 
                 generictools=False, episodes_list={}, finds={}, **kwargs):
        logger.info('Serie: %s; Season: %s/%s' % (item.contentSerieName, item.contentSeason, item.infoLabels['number_of_seasons']))
        from lib.generictools import AH_post_tmdb_episodios, AH_find_videolab_status
        from core import tmdb

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        finds_out = finds.get('episodes', {})
        finds_episode_num = finds.get('episode_num', [])
        do_episode_clean = finds.get('episode_clean') if finds.get('episode_clean') else [['(?i)\s*\d+x\d+', '']]
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)
        itemlist = list()
        matches = list()
        matches_episodes = list()
        soup = {}
        if not matches_post and item.matches_post: matches_post = item.matches_post

        self.btdigg = finds_controls.get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

        AHkwargs = {'url': item.url, 'soup': soup, 'kwargs': kwargs, 'finds': finds, 'function': 'episodes'}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = matches_post or kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)

        if DEBUG: logger.debug('FINDS_episodes: %s; FINDS_controls: %s' % (finds_out, finds_controls))

        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        url_replace = self.url_replace = self.finds.get('url_replace', [])
        min_temp = finds_controls.get('min_temp', False)
        join_dup_episodes = finds_controls.get('join_dup_episodes', True)

        modo_ultima_temp = AHkwargs['modo_ultima_temp'] = config.get_setting('seleccionar_ult_temporadda_activa', item.channel, default=True)
        self.season_colapse = config.get_setting('season_colapse', item.channel, default=True)
        if item.season_colapse == False: self.season_colapse = item.season_colapse
        filter_languages = config.get_setting('filter_languages', item.channel, default=0)
        modo_grafico = True if self.btdigg else config.get_setting('modo_grafico', item.channel, default=True)
        idioma_busqueda = 0
        if not filter_languages: filter_languages = 0

        item.context = []
        item.context = filtertools.context(item, self.list_language, self.list_quality_tvshow)

        # Vemos la última temporada de TMDB y del .nfo
        if item.ow_force == "1":                                                # Si hay una migración de canal o url, se actualiza todo 
            modo_ultima_temp = False
        max_temp = int(item.infoLabels['number_of_seasons'] or 0)
        max_nfo = 0
        y = []
        if modo_ultima_temp and item.library_playcounts:                        # Averiguar cuantas temporadas hay en Videoteca
            patron = 'season (\d+)'
            matches = re.compile(patron, re.DOTALL).findall(str(item.library_playcounts))
            for x in matches:
                y += [int(x)]
            max_nfo = max(y)
        if max_nfo > 0 and max_nfo != max_temp:
            max_temp = max_nfo
        if max_temp == 0 or max_nfo:
            modo_ultima_temp = min_temp = False

        item.url = self.do_url_replace(item.url, url_replace)

        if episodes_list:
            for elem in episodes_list:
                elem_json = {}

                elem_json['season'] = elem.get('season', item.contentSeason)
                elem_json['episode'] = int(scrapertools.find_single_match(str(elem.get('episode', '1')), '\d+') or '1')
                elem_json['url'] = elem.get('url', '')
                if not elem.get('url', ''): continue
                elem_json['url'] = self.urljoin(self.host, elem['url'])
                elem_json['title'] = elem.get('title', '')
                elem_json['quality'] = elem.get('quality', '')
                elem_json['language'] = elem.get('language', '')
                elem_json['server'] = elem.get('server', '')
                elem_json['size'] = elem.get('size', '')
                elem_json['torrent_info'] = elem.get('torrent_info', '')
                if elem.get('btdig_in_use', False): elem_json['btdig_in_use'] = elem.get('btdig_in_use', False)
                elem_json['password'] = elem.get('password', '')
                elem_json['plot'] = elem.get('plot', '')
                elem_json['post'] = elem.get('post', None)
                elem_json['headers'] = elem.get('headers', None)
                if elem.get('info', None): elem_json['info'] = elem['info']

                matches.append(elem_json.copy())
        else:
            if BTDIGG in item.url:
                soup = {}
                matches_episodes = matches = []
            else:
                kwargs.update({'timeout': timeout, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
                soup = data or self.create_soup(item.url, **kwargs)

                itemlist = self.itemlist + itemlist
                self.itemlist = []

                AHkwargs['soup'] = self.response.soup or self.response.json or self.response.data
                matches_episodes = self.parse_finds_dict(soup, finds_out) if finds_out \
                                   else (self.response.soup or self.response.json or self.response.data)
                if not isinstance(matches_episodes, (list, _dict)):
                    matches_episodes = []

            if matches_post and matches_episodes:
                matches = matches_post(item, matches_episodes, **AHkwargs)

        if self.btdigg:
            if 'matches' in AHkwargs: del AHkwargs['matches']
            matches = self.find_btdigg_episodes(item, matches, finds_controls.get('domain_alt', DOMAIN_ALT), **AHkwargs)

        if not matches:
            logger.error('NO MATCHES: %s' % finds_out)
            logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or episodes_list)
            return itemlist

        # Refrescamos variables posiblemente actualizadas en "matches_post"
        finds = self.finds.copy()
        finds_controls = finds.get('controls', {})
        find_add_video_to_videolibrary = finds_controls.get('add_video_to_videolibrary', True)
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host) or host_referer
        post = item.post or finds_controls.pop('post', None) or post
        headers = item.headers or finds_controls.get('headers', {}) or headers
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
        url_base64 = finds_controls.get('url_base64', True)
        IDIOMAS_TMDB = finds_controls.get('IDIOMAS_TMDB', {}) or self.IDIOMAS_TMDB
        idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', item.channel, default=0)]    # Idioma base para TMDB
        if not idioma_busqueda: idioma_busqueda = 0
        idioma_busqueda_org = idioma_busqueda
        idioma_busqueda_save = ''
        idioma_busqueda_VO = IDIOMAS_TMDB[2]                                    # Idioma para VO: Local,VO
        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

        AHkwargs['matches'] = matches
        if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))
        
        for elem in matches:
            infolabels = item.infoLabels.copy()

            if not elem.get('url', ''): continue
            if url_base64: 
                elem['url'] = self.convert_url_base64(elem['url'], self.host, item=item)
            else:
                elem['url'] = self.urljoin(self.host, elem['url'])
            elem['url'] = self.do_url_replace(elem['url'], url_replace)

            infolabels["season"] = elem.get('season', item.contentSeason)

            infolabels["episode"] = elem.get('episode', 1)
            if isinstance(finds_episode_num, list):
                for episode_num in finds_episode_num:
                    if scrapertools.find_single_match(elem.get('title', ''), episode_num):
                        infolabels["episode"] = int(scrapertools.find_single_match(elem.get('title', ''), episode_num))
                        break
                else:
                    infolabels["episode"] = int(scrapertools.find_single_match(str(elem.get('episode', '1')), '\d+') or '1')

            if isinstance(do_episode_clean, list):
                for clean_org, clean_des in do_episode_clean:
                    if clean_des is None:
                        if scrapertools.find_single_match(elem.get('title', ''), clean_org):
                            elem['title'] = scrapertools.find_single_match(elem['title'], clean_org).strip()
                            break
                    else:
                        elem['title'] = re.sub(clean_org, clean_des, elem.get('title', '')).strip()
            elem['title'] = elem.get('title', '').strip()
            if elem['title'].startswith('al '):
                infolabels['episodio_titulo'] = elem['title']
                elem['title'] = '%sx%s %s %s' % (infolabels["season"], infolabels["episode"], elem['title'], item.contentSerieName)
            else:
                elem['title'] = "%sx%s - %s" % (infolabels["season"], infolabels["episode"], elem['title'] or item.contentSerieName)
            elem['title'] = scrapertools.slugify(elem.get('title', '').strip(), strict=False)
            infolabels = scrapertools.episode_title(elem['title'].capitalize(), infolabels)

            if elem.get('thumbnail', ''): 
                elem['thumbnail'] = elem['thumbnail'] if elem['thumbnail'].startswith('http') \
                                                         else 'https:' + elem['thumbnail'] if elem['thumbnail'].startswith('//') \
                                                         else self.urljoin(self.host, elem['thumbnail'])
                if ('tmdb' in elem['thumbnail'] or 'imdb' in elem['thumbnail']) and '=http' in elem['thumbnail']:
                    elem['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem['thumbnail']), '=(.*?)[&|$]')

            new_item = Item(channel=item.channel,
                            category=item.channel.capitalize(), 
                            url=elem['url'], 
                            url_tvshow = item.url_tvshow, 
                            title=elem['title'],
                            action=action,
                            infoLabels=infolabels,
                            contentType='episode',
                            quality=elem.get('quality', ''),
                            language=elem.get('language', ''),
                            contentPlot=elem.get('plot', item.contentPlot), 
                            thumbnail=elem.get('thumbnail', item.thumbnail), 
                            context=item.context[:] or []
                           )

            if elem.get('extra', ''): new_item.extra = elem['extra']
            if elem.get('btdig_in_use', False): new_item.btdig_in_use = elem['btdig_in_use']
            if elem.get('post', None): new_item.post = elem['post']
            if elem.get('headers', None): new_item.headers = elem['headers']
            if item.video_path: new_item.video_path = item.video_path
            if item.filtertools: new_item.filtertools = item.filtertools
            if elem.get('info', None): new_item.info = elem['info']
            if elem.get('playcount', 0): new_item.infoLabels['playcount'] = elem['playcount']
            if elem.get('broadcast', ''): new_item.broadcast = elem['broadcast']
            if elem.get('plot_extend', ''): new_item.plot_extend = elem['plot_extend']
            if 'plot_extend_show' in elem: new_item.plot_extend_show = elem['plot_extend_show']
            if finds_controls.get('mediatype', ''): new_item.contentType = finds_controls['mediatype']
            if finds_controls.get('action', ''): new_item.action = finds_controls['action']
            if elem.get('action', ''): new_item.action = elem['action']
            
            if new_item.quality:
                for clean_org, clean_des in finds.get('quality_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.quality, clean_org):
                            new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                            break
                    else:
                        new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
            if str(new_item.quality).startswith('*'):
                new_item.quality = self.find_quality(new_item, item)
            if not new_item.quality and item.quality:
                new_item.quality = item.quality
            elem['quality'] = new_item.quality

            if new_item.language:
                for clean_org, clean_des in finds.get('language_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.language, clean_org):
                            new_item.language = scrapertools.find_single_match(new_item.language, clean_org).strip()
                            break
                    else:
                        new_item.language = re.sub(clean_org, clean_des, new_item.language).strip()
            if '*' in str(new_item.language):
                new_item.language = self.find_language(new_item, item)
            if not new_item.language and item.language:
                new_item.language = item.language
            elem['language'] = new_item.language

            if 'CAST' in str(new_item.language) or 'LAT' in str(new_item.language) or 'DUAL' in str(new_item.language):
                idioma_busqueda_save = idioma_busqueda
            if 'VO' in str(new_item.language) and not idioma_busqueda_save:
                idioma_busqueda = idioma_busqueda_VO
            if elem.get('context', []): new_item.context.extend(elem['context'])

            new_item.url = self.do_url_replace(new_item.url, url_replace)

            if postprocess:
                new_item = postprocess(elem, new_item, item, **AHkwargs)

            if new_item and not new_item.matches and (new_item.url.startswith('magnet') or new_item.url.endswith('.torrent') \
                                                 or elem.get('matches', [])):
                if elem.get('url_episode', ''): 
                    new_item.url = elem['url_episode']
                    del elem['url_episode']
                new_item.matches = []
                if elem.get('matches'):
                    new_item.matches = elem['matches'][:]
                else:
                    new_item.matches.append(elem.copy())
            
            if new_item: itemlist.append(new_item.clone())
            #if DEBUG: logger.debug('EPISODES: %s' % new_item)

        if itemlist:
            itemlist_copy = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))
            itemlist = []

            for new_item in itemlist_copy:

                # Comprobamos si hay más de un enlace por episodio, entonces los agrupamos
                if join_dup_episodes:
                    if DEBUG and len(itemlist) > 0: 
                        logger.debug('EPISODE-DUP: SEASON: %s; EPISODE: %s; QUALITY: %s; LANGUAGE: %s; ' \
                                     'SEASON[-1]: %s; EPISODE[-1]: %s; QUALITY[-1]: %s; LANGUAGE[-1]: %s' \
                                     % (new_item.contentSeason, new_item.contentEpisodeNumber, 
                                        new_item.quality, new_item.language, 
                                        itemlist[-1].contentSeason, itemlist[-1].contentEpisodeNumber, 
                                        itemlist[-1].quality, itemlist[-1].language, ))
                    if len(itemlist) > 0 and new_item.contentSeason == itemlist[-1].contentSeason \
                                and new_item.contentEpisodeNumber == itemlist[-1].contentEpisodeNumber \
                                and itemlist[-1].contentEpisodeNumber != 0:     # solo guardamos un episodio ...
                        if itemlist[-1].quality:
                            if new_item.quality not in itemlist[-1].quality:
                                itemlist[-1].quality += ", " + new_item.quality # ... pero acumulamos las calidades
                        else:
                            itemlist[-1].quality = new_item.quality

                        if itemlist[-1].language:
                            for language in new_item.language:
                                if language not in itemlist[-1].language:
                                    itemlist[-1].language += [language]
                        elif new_item.language:
                            itemlist[-1].language = new_item.language
                        if not itemlist[-1].matches and new_item.matches: itemlist[-1].matches = []
                        if new_item.matches: itemlist[-1].matches.extend(new_item.matches)       # Salvado Matches en el episodio anterior
                        continue                                                # ignoramos el episodio duplicado
                
                if modo_ultima_temp and item.library_playcounts:                # Si solo se actualiza la última temporada de Videoteca
                    if min_temp and new_item.contentSeason < max_temp:
                        if DEBUG: logger.debug('%s: &s: %s' % (str(min_temp), new_item.contentSerieName, new_item.title))
                        if 'continue' in str(min_temp): continue                # Ignora episodio
                        if 'break' in str(min_temp): break                      # Sale del bucle
                    if item_local.contentSeason < max_temp:
                        if DEBUG: logger.debug('%s: &s: %s' % (str(min_temp), new_item.contentSerieName, new_item.title))
                        continue                                                # Ignora episodio

                itemlist.append(new_item.clone())

            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico and not self.httptools.TEST_ON_AIR
            tmdb.set_infoLabels_itemlist(itemlist, modo_grafico, idioma_busqueda=idioma_busqueda)

            for new_item in itemlist:
                if new_item.broadcast:
                    new_item.contentPlot = '%s\n\n%s' % (new_item.broadcast, new_item.contentPlot)
                    del new_item.broadcast

            # Requerido para FilterTools
            if item.library_playcounts and config.get_setting('auto_download_new', channel=self.channel):
                itemlist = filtertools.get_links(itemlist, item, self.list_language, self.list_quality_tvshow)
                #if DEBUG: logger.debug('EPISODE-LAST: %s' % itemlist[-1])

            # Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
            if generictools:
                item, itemlist = AH_post_tmdb_episodios(item, itemlist, **AHkwargs)

            if find_add_video_to_videolibrary:
                if videolab_status:
                    # Llamamos al método para encontrar el estado del vídeo en la videoteca
                    itemlist = AH_find_videolab_status(item, itemlist, **AHkwargs)
                itemlist = self.add_video_to_videolibrary(item, itemlist)

        return itemlist

    def get_video_options(self, item, url, data='', langs=[], matches_post=None, postprocess=None, 
                          verify_links=False, generictools=False, findvideos_proc=False, finds={}, **kwargs):
        if item.contentType == 'movie':
            logger.info('Movie: %s' % item.contentTitle)
        else:
            logger.info('Serie: %s; Season: %s: Episode: %s' % (item.contentSerieName, item.contentSeason, item.contentEpisodeNumber))
        if DEBUG: logger.debug('FINDS: %s' % finds)
        from lib.generictools import AH_post_tmdb_findvideos, AH_find_videolab_status
        from core import tmdb
        import xbmc

        self.Window_IsMedia = bool(xbmc.getCondVisibility('Window.IsMedia'))
        if not item.url_tvshow: item.url_tvshow = item.url

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        finds_out = finds.get('findvideos', {})
        finds_out_episodes = finds.get('episodes', {})
        finds_langs = finds.get('langs', {})
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)
        options = list()
        results = list()
        itemlist = []
        itemlist_total = []
        soup = {}
        matches = []
        matches_findvideos = []
        if not matches_post and item.matches_post: matches_post = item.matches_post
        matches_post_episodes = None

        self.btdigg = finds_controls.get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)
        btdig_in_use = False

        AHkwargs = {'url': item.url, 'soup': soup, 'finds': finds, 'kwargs': kwargs, 'function': 'get_video_options', 'videolibrary': False}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = matches_post or kwargs.pop('matches_post_get_video_options', None)

        if DEBUG: logger.debug('FINDS_findvideos: %s; FINDS_langs: %s; FINDS_controls: %s' % (finds_out, finds_langs, finds_controls))

        item.title  = item.title.replace('(V)-' , '')
        item.contentTitle  = item.contentTitle.replace('(V)-' , '')
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)
        self.host_torrent = finds_controls.get('host_torrent', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % self.host
        host_torrent_referer = finds_controls.get('host_torrent_referer', self.host_torrent)
        url_replace = self.url_replace = self.finds.get('url_replace', [])
        manage_torrents = finds_controls.get('manage_torrents', True)

        filter_languages = config.get_setting('filter_languages', item.channel, default=0)
        modo_grafico = True if self.btdigg else config.get_setting('modo_grafico', item.channel, default=True)
        if not filter_languages: filter_languages = 0
        IDIOMAS_TMDB = finds_controls.get('IDIOMAS_TMDB', {}) or self.IDIOMAS_TMDB
        idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', item.channel, default=0)]    # Idioma base para TMDB
        if not idioma_busqueda: idioma_busqueda = 0
        idioma_busqueda_org = idioma_busqueda
        idioma_busqueda_save = ''
        idioma_busqueda_VO = IDIOMAS_TMDB[2]                                    # Idioma para VO: Local,VO

        item.context = filtertools.context(item, self.list_language, self.list_quality_tvshow)
        
        url = self.do_url_replace(url, url_replace)

        tmdb.set_infoLabels_item(item, modo_grafico, idioma_busqueda=idioma_busqueda)

        if not data and item.matches and item.url_tvshow and BTDIGG not in item.url_tvshow \
                                     and (item.channel == 'videolibrary' or item.contentChannel == 'videolibrary' \
                                          or item.from_channel == 'videolibrary'):
            matches_post_episodes = AHkwargs['matches_post_episodes']
            if matches_post_episodes:
                if item.btdig_in_use:
                    del item.btdig_in_use
                if item.url.startswith('magnet') or item.url.endswith('.torrent'):
                    url = item.url = item.url_tvshow
 
        if data or item.url.startswith('magnet') or item.url.endswith('.torrent') \
                or (item.matches and item.channel != 'videolibrary' and item.contentChannel != 'videolibrary' \
                                 and item.from_channel != 'videolibrary') \
                or item.btdig_in_use:
            soup = data
            response = self.response
            response.data = data
            response.soup = soup
        else:
            kwargs.update({'timeout': timeout, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
            soup = self.create_soup(url, **kwargs) if not BTDIGG_URL in url else {}

            itemlist = self.itemlist + itemlist
            self.itemlist = []

            response = self.response
            soup = response.soup or {}
            AHkwargs['soup'] = response.soup or response.json or response.data
            
            if matches_post_episodes:
                matches_episodes = self.parse_finds_dict(soup, finds_out_episodes)
                if matches_episodes:
                    matches_epi = matches_post_episodes(item, matches_episodes, **AHkwargs)
                    for epi in matches_epi:
                        if not epi.get('episode', 0) == item.contentEpisodeNumber: continue
                        matches.append(epi.copy())
                    if matches:
                        item.matches = matches[:]
                    elif isinstance(item.matches[0], _dict):
                        matches = item.matches[:]
        
        langs = langs or self.parse_finds_dict(soup, finds_langs) or self.language
        if not isinstance(langs, list):
            langs = []

        if not item.matches and (item.url.startswith('magnet') or item.url.endswith('.torrent') or not finds_out):
            elem_json = {}

            if item.contentType != 'movie':
                if item.contentSeason: elem_json['season'] = item.contentSeason
                if item.contentEpisodeNumber: elem_json['episode'] = item.contentEpisodeNumber
            elem_json['url'] = item.url
            if not elem_json['url'].startswith('magnet'): elem_json['url'] = self.urljoin(self.host, elem_json['url'])
            elem_json['quality'] = item.quality
            elem_json['language'] = item.language
            elem_json['server'] = 'torrent' if (elem_json['url'].startswith('magnet') \
                                                or elem_json['url'].endswith('.torrent')) else ''
            elem_json['title'] = elem_json['server'] or '%s'
            if item.torrent_info: elem_json['size'] = elem_json['torrent_info'] = item.torrent_info
            if item.btdig_in_use: elem_json['btdig_in_use'] = item.btdig_in_use
            if item.password: elem_json['password'] = item.password
            if item.plot: elem_json['plot'] = item.plot
            if item.post: elem_json['post'] = item.post
            if item.headers: elem_json['headers'] = item.headers

            matches.append(elem_json.copy())
        
        if not item.matches or (item.matches and not matches and (item.channel == 'videolibrary' \
                                                                  or item.contentChannel == 'videolibrary' \
                                                                  or item.from_channel == 'videolibrary')):
            matches_findvideos = self.parse_finds_dict(soup, finds_out) if finds_out \
                                 else (self.response.soup or self.response.json or self.response.data)
            if not isinstance(matches_findvideos, (list, _dict)):
                matches_findvideos = []
            if item.matches and not isinstance(item.matches[0], _dict):
                AHkwargs['matches'] = item.matches
                del item.matches
            if matches_post and matches_findvideos:
                matches, langs = matches_post(item, matches_findvideos, langs, response, **AHkwargs)
            if matches and AHkwargs.get('matches'):
                item.matches = matches[:]
                del AHkwargs['matches']

        if (item.matches or AHkwargs.get('matches')) and not matches:
            matches = AHkwargs.get('matches', []) or item.matches
            if item.matches and not isinstance(item.matches[0], _dict):
                AHkwargs['matches'] = matches[:]
                matches_findvideos = matches[:]
                del item.matches
            if matches_post and matches_findvideos and not isinstance(matches_findvideos[0], _dict):
                # Generar el json desde matches videoteca antiguos
                AHkwargs['videolibrary'] = True
                matches, langs = matches_post(item, matches_findvideos, langs, response, **AHkwargs)
                item.matches = matches[:]
            if AHkwargs.get('matches'): del AHkwargs['matches']

        if self.btdigg:
            if AHkwargs.get('matches'): del AHkwargs['matches']
            matches = self.find_btdigg_findvideos(item, item.matches or matches, finds_controls.get('domain_alt', DOMAIN_ALT), **AHkwargs)
        
        if not matches:
            if item.emergency_urls and not item.videolibray_emergency_urls:     # Hay urls de emergencia?
                item.armagedon = True                                           # Marcamos la situación como catastrófica 
                if len(item.emergency_urls) > 1:
                    matches_findvideos = item.emergency_urls[1]                 # Restauramos matches de vídeos
                else:
                    matches_findvideos = item.emergency_urls[0]                 # Restauramos torrents/magnetes
                if matches_post and matches_findvideos and not isinstance(matches_findvideos[0], _dict):
                    # Generar el json desde matches videoteca antiguos
                    AHkwargs['videolibrary'] = True
                    matches, langs = matches_post(item, matches_findvideos, langs, response, **AHkwargs)
            if not matches:
                if item.videolibray_emergency_urls:                             # Si es llamado desde creación de Videoteca...
                    return item                                                 # Devolvemos el Item de la llamada
                else:
                    return itemlist                                             # Si no hay más datos, algo no funciona, pintamos lo que tenemos

        # Refrescamos variables posiblemente actualizadas en "matches_post"
        finds = self.finds.copy()
        finds_controls = finds.get('controls', {})
        self.host_torrent = finds_controls.get('host_torrent', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % self.host
        host_torrent_referer = finds_controls.get('host_torrent_referer', self.host_torrent)
        post = item.post or finds_controls.pop('post', None) or post
        headers = item.headers or finds_controls.get('headers', {}) or headers
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
        url_base64 = finds_controls.get('url_base64', True)
        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

        AHkwargs['matches'] = matches
        if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))

        # Si es un lookup para cargar las urls de emergencia en la Videoteca...
        if item.videolibray_emergency_urls:
            item.emergency_urls = []                                            # Iniciamos emergency_urls
            item.emergency_urls.append([])                                      # Reservamos el espacio para los .torrents locales
            item.emergency_urls.append([])                                      # Reservada para matches de los vídeos
            item.emergency_urls.append([])                                      # Reservada para urls de los vídeos
            item.emergency_urls.append([])                                      # Reservamos el espacio para los tamaños de los .torrents/magnets

        #Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
        if generictools and not item.videolibray_emergency_urls:
            item, itemlist_total = AH_post_tmdb_findvideos(item, itemlist_total, **AHkwargs)

        for _lang in langs or ['CAST']:
            lang = _lang

            if 'descargar' in lang: continue
            if 'latino' in lang: lang = ['LAT']
            if 'español' in lang: lang += ['CAST']
            if 'subtitulado' in lang: lang += ['VOS']

            for elem in matches:
                if not elem.get('url', ''): continue
                    
                elem['channel'] = item.channel
                if not elem.get('mediatype', '') and finds_controls.get('mediatype', ''): elem['mediatype'] = finds_controls['mediatype']
                if not elem.get('action', '') and finds_controls.get('action', ''): elem['action'] = finds_controls['action']
                elem['action'] = elem.get('action', 'play')
                elem['language'] = lang = elem.get('language', lang)
                elem['quality'] = elem.get('quality', item.quality)

                if elem['url'].startswith('//'):
                    elem['url'] = 'https:%s' % elem['url']
                if url_base64: elem['url'] = self.convert_url_base64(elem['url'], self.host_torrent, referer=host_torrent_referer, item=item)

                if not 'title' in elem:
                    elem['title'] = 'torrent' if elem.get('server', '').lower() == 'torrent' else '%s'

                # Tratamos las particulirades de los .torrents/magnets
                if elem.get('btdig_in_use', False): btdig_in_use = elem['btdig_in_use']
                if elem.get('server', '').lower() == 'torrent' and manage_torrents:
                    elem = self.manage_torrents(item, elem, lang, soup, finds, **kwargs)

                options.append((lang, elem))
        
        # Si es un lookup para cargar las urls de emergencia en la Videoteca...
        if item.videolibray_emergency_urls:
            return item

        results.append([soup, options])

        if not findvideos_proc: return results[0]

        if btdig_in_use and not self.httptools.TEST_ON_AIR:
            itemlist_total.append(Item(channel=item.channel, action="", infoLabels=item.infoLabels, quality='', 
                                       title="[COLOR blue] Enlaces (imprecisos) buscados en %s" % BTDIGG_LABEL))
        for lang, elem in results[0][1]:
            new_item = item.clone()
            
            if verify_links and elem.get('server', '') and elem.get('server', '').lower() != 'torrent':
                if config.get_setting("hidepremium") and not servertools.is_server_enabled(elem['server']):
                    continue
                item_url = elem['url']
                if not isinstance(verify_links, bool): item_url = verify_links(Item(url=item_url, server=elem['server']))[0].url
                elem['alive'] = servertools.check_video_link(item_url, elem['server'])  # Link Activo ?
                if 'NO' in elem['alive']:
                    continue
            
            new_item.channel = elem.get('channel', item.channel)
            new_item.category = new_item.channel.capitalize()
            new_item.action = elem.get('action', 'play')
            new_item.url = elem.get('url', '')
            new_item.server = elem.get('server', '')
            new_item.title = elem.get('title', '%s')
            if elem.get('post', None): new_item.post = elem['post']
            new_item.headers = elem.get('headers', {'Referer': item.url})
            new_item.setMimeType = 'application/vnd.apple.mpegurl'

            if elem.get('quality', ''):
                new_item.quality = elem['quality']
                if 'bluray' in new_item.quality.lower(): new_item.quality = new_item.quality.replace('-', ' ').replace('_', ' ')
                for clean_org, clean_des in finds.get('quality_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.quality, clean_org):
                            new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                            break
                    else:
                        new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
            if str(elem.get('quality', '')).startswith('*'):
                elem['quality'] = new_item.quality
                new_item.quality = self.find_quality(elem, item)

            if elem.get('language', lang):
                new_item.language = elem['language']
                for clean_org, clean_des in finds.get('language_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.language, clean_org):
                            new_item.language = scrapertools.find_single_match(new_item.language, clean_org).strip()
                            break
                    else:
                        new_item.language = re.sub(clean_org, clean_des, new_item.language).strip()
            if '*' in str(elem.get('language', '')):
                elem['language'] = new_item.language
                new_item.language = self.find_language(elem, item)
            if not new_item.language: new_item.language = [lang]

            if elem.get('mediatype', ''): new_item.contentType = elem['mediatype']
            if elem.get('season', ''): new_item.contentSeason = elem['season']
            if elem.get('episode', ''): new_item.contentEpisodeNumber = elem['episode']
            if elem.get('extra', ''): new_item.extra = elem['extra']
            if elem.get('plot', ''): new_item.contentPlot = elem['plot']
            if elem.get('broadcast', ''): new_item.contentPlot = '%s\n\n%s' % (elem['broadcast'], new_item.contentPlot)
            if elem.get('torrent_info', ''): new_item.torrent_info = elem['torrent_info']
            if elem.get('password', ''): new_item.password = elem['password']
            if elem.get('torrents_path', ''): new_item.torrents_path = elem['torrents_path']
            if elem.get('torrent_alt', ''): new_item.torrent_alt = elem['torrent_alt']
            if 'alive' in elem: new_item.alive = elem['alive']
            if 'unify' in elem: new_item.unify = elem['unify']
            if 'folder' in elem: new_item.folder = elem['folder']
            if elem.get('item_org', ''): new_item.item_org = elem['item_org']
            if elem.get('subtitle', ''): new_item.subtitle = elem['subtitle']
            if elem.get('context', []): new_item.context.extend(elem['context'])
            if elem.get('playcount', 0): new_item.infoLabels['playcount'] = elem['playcount']
            if elem.get('plot_extend', ''): new_item.infoLabels['plot_extend'] = elem['plot_extend']
            if 'plot_extend_show' in elem: new_item.plot_extend_show = elem['plot_extend_show']
            new_item.play_type = elem.get('play_type', 'Ver')
            new_item.size = self.convert_size(elem.get('size', 0))

            if new_item.server.lower() not in ['torrent', 'header']:
                new_item.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][%s][/COLOR] '
                new_item.title += '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' \
                                    % (new_item.quality, str(new_item.language), new_item.torrent_info)

            new_item.url = self.do_url_replace(new_item.url, url_replace)

            if postprocess:
                new_item = postprocess(elem, new_item, item, **AHkwargs)

            if new_item: 
                if new_item.server == "Header":
                    new_item.server = ""
                    new_item.infoLabels['playcount'] = 0
                    itemlist_total.append(new_item.clone())
                else:
                    itemlist.append(new_item.clone())

        # Requerido para FilterTools
        if itemlist:
            itemlist = filtertools.get_links(itemlist, item, self.list_language, self.list_quality_movies \
                                             if new_item.contentType == 'movie' else self.list_quality_tvshow)

        if itemlist:
            find_add_video_to_videolibrary = finds_controls.get('add_video_to_videolibrary', True)
            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico
            try:
                itemlist = servertools.get_servers_itemlist(itemlist, lambda it: it.title % it.server.capitalize())
            except Exception:
                pass

            if itemlist and itemlist[0].channel != 'filtertools' and finds_controls.get('sort_findvideos', True):
                try:
                    itemlist = sorted(itemlist, key=lambda it: (1 if it.play_type == 'Ver' else 2, int(-it.size if it.size \
                                                and it.contentType == 'movie' else it.size if it.size else 0), 
                                                it.language[0] if (it.language and isinstance(it.language, list)) else it.language, 
                                                it.server))
                except Exception:
                    size = []
                    for it in itemlist:
                        size += [[it.size, it.title]]
                        if not it.size and 'magnet' in new_item.torrent_info.lower(): it.size = 'Magnet'
                    logger.error('ERROR_SIZE: %s' % size)
                    logger.error(traceback.format_exc())
                for it in itemlist:
                    if not it.size and 'magnet' in new_item.torrent_info.lower(): it.size = 'Magnet'
                if videolab_status:
                    # Llamamos al método para encontrar el estado del vídeo en la videoteca
                    itemlist = AH_find_videolab_status(item, itemlist, **AHkwargs)
                if find_add_video_to_videolibrary:
                    itemlist = self.add_video_to_videolibrary(item, itemlist, contentType=item.contentType)

            itemlist_total.extend(itemlist)

        # Requerido para AutoPlay
        autoplay.start(itemlist, item, user_server_list=[], user_quality_list=self.list_quality_tvshow if item.contentType != 'movie' else [])

        return itemlist_total


class DictionaryAdultChannel(AlfaChannelHelper):

    def list_all(self, item, data='', matches_post=None, postprocess=None, generictools=False, finds={}, **kwargs):
        logger.info()
        from bs4 import Comment
        self.Comment = Comment

        itemlist = list()
        matches = []
        matches_list_all = []
        if not matches_post and item.matches_post: matches_post = item.matches_post

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        if DEBUG: logger.debug('FINDS: %s' % finds)
        finds_out = finds.get('find', {})
        finds_next_page = finds.get('next_page', {})
        finds_next_page_rgx = finds.get('next_page_rgx') if finds.get('next_page_rgx') else [['page\/\d+\/', 'page/%s/']]
        finds_last_page = finds.get('last_page', {})
        finds_year = finds.get('year', {})
        finds_season_episode = finds.get('season_episode', {})
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)
        premium_skip = finds_controls.get('premium_skip', '')

        AHkwargs = {'url': item.url, 'soup': item.matches or {}, 'finds': finds, 'kwargs': kwargs, 'function': 'list_all_A', 
                    'function_alt': kwargs.get('function', '')}
        AHkwargs['matches_post_list_all'] = matches_post or kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)
        matches_post_json_force = kwargs.pop('matches_post_json_force', False)

        # Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
        title_lista = []                                        # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
        if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
            title_lista.extend(item.title_lista)                                # Se usa la lista de páginas anteriores en Item
            del item.title_lista                                                # ... limpiamos

        self.curr_page = 1                                          # Página inicial
        self.last_page = 99999 if (not isinstance(finds_last_page, bool) \
                                   and not finds_controls.get('custom_pagination', False)) \
                                  else 9999 if finds_controls.get('custom_pagination', False) else 0    # Última página inicial
        last_page_print = 1                                                     # Última página inicial, para píe de página
        page_factor = finds_controls.get('page_factor', 1.0 )                   # Factor de conversión de pag. web a pag. Alfa
        self.cnt_tot = finds_controls.get('cnt_tot', 20)                        # Poner el num. máximo de items por página
        cnt_tot_ovf = finds_controls.get('page_factor_overflow', 1.3)           # Overflow al num. máximo de items por página
        cnt_match = 0                                                           # Contador de matches procesadas
        cnt_title = 0                                                           # Contador de líneas insertadas en Itemlist
        cnt_tot_match = 0.0                                                     # Contador TOTAL de líneas procesadas de matches
        custom_pagination =  finds_controls.get('custom_pagination', False)     # Paginación controlada por el usuario
        if 'cnt_tot_match' in item:
            cnt_tot_match = float(item.cnt_tot_match)                           # restauramos el contador TOTAL de líneas procesadas de matches
            del item.cnt_tot_match
        if 'curr_page' in item:
            self.curr_page = int(item.curr_page)                                # Si viene de una pasada anterior, lo usamos
            del item.curr_page                                                  # ... y lo borramos
        if 'last_page' in item:
            self.last_page = int(item.last_page)                                # Si viene de una pasada anterior, lo usamos
            del item.last_page                                                  # ... y lo borramos
        if 'page_factor' in item:
            page_factor = float(item.page_factor)                               # Si viene de una pasada anterior, lo usamos
            del item.page_factor                                                # ... y lo borramos
        if 'last_page_print' in item:
            last_page_print = item.last_page_print                              # Si viene de una pasada anterior, lo usamos
            del item.last_page_print                                            # ... y lo borramos
        if 'unify' in item:
            del item.unify                                                      # ... y lo borramos

        inicio = time.time()                                                    # Controlaremos que el proceso no exceda de un tiempo razonable
        fin = inicio + finds_controls.get('inicio', 5)                          # Después de este tiempo pintamos (segundos)
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)     # Timeout normal
        timeout_search = timeout * 2                                            # Timeout para búsquedas

        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)
        if not item.c_type: item.c_type = 'peliculas'

        self.next_page_url = next_page_url = item.url
        # Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
        while (cnt_title < self.cnt_tot and (self.curr_page <= self.last_page or (self.last_page == 0 and finds_next_page \
                                             and next_page_url and (item.matches or matches))) \
                                        and fin > time.time()) \
                                        or item.matches:
            
            # Descarga la página
            soup = data
            data = ''
            cnt_match = 0                                                       # Contador de líneas procesadas de matches
            if not item.matches and next_page_url:                              # si no viene de una pasada anterior, descargamos
                kwargs.update({'timeout': timeout_search, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
                soup = soup or self.create_soup(next_page_url, **kwargs)

                itemlist = self.itemlist + itemlist
                self.itemlist = []

                if self.url:
                    if DEBUG: logger.debug('self.URL: %s / %s' % (next_page_url, self.url))
                    self.next_page_url = next_page_url = item.url = self.url
                    self.url = ''
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if not scrapertools.find_single_match(item.url, rgx_org): continue
                        item.url = re.sub(rgx_org, rgx_des % str(self.curr_page), item.url.rstrip('/')).replace('//?', '/?')
                if soup:
                    AHkwargs['soup'] = self.response.soup or self.response.json or self.response.data
                    self.curr_page += 1

                    matches_list_all = self.parse_finds_dict(soup, finds_out) if finds_out \
                                       else (self.response.soup or self.response.json or self.response.data)
                    if not isinstance(matches_list_all, (list, _dict)):
                        matches = []

                    if matches_list_all and ('profile' in finds_controls or not matches_post):
                        for elem in matches_list_all:
                            if isinstance(elem, str): continue
                            elem_json = {}
                            #logger.error(elem)
                            
                            try:
                                if profile in [DEFAULT]:
                                    elem_json['url'] = elem.get('href', '') or (elem.a.get('href', '') if elem.a else '')
                                    elem_json['title'] = elem.get('title', '') or (elem.a.get('title', '') if elem.a else '') \
                                                         or (elem.find(class_='title').get_text(strip=True) if elem.find(class_='title') else '') \
                                                         or (elem.img.get('alt', '') if elem.img else '')
                                    elem_json['thumbnail'] = (elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                             or elem.img.get('data-src', '') \
                                                             or elem.img.get('src', '')) if elem.img else ''
                                    elem_json['stime'] = elem.find(class_='duration').get_text(strip=True) if elem.find(class_='duration') else ''
                                    if not elem_json['stime'] and elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                              and 'duration' in text):
                                        elem_json['stime'] = self.do_soup(elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                                          and 'duration' in text)).find(class_='duration').get_text(strip=True)
                                    if not elem_json['stime'] and elem.find(string=re.compile('\d{2}:\d{2}$')):
                                        elem_json['stime'] = elem.find(string=re.compile('(\d{2}:\d{2}$)')).replace("duration: ", "")
                                    if elem.find('span', class_=['hd-thumbnail', 'is-hd']):
                                        elem_json['quality'] = elem.find('span', class_=['hd-thumbnail', 'is-hd']).get_text(strip=True)
                                    elif elem.find(text=lambda text: isinstance(text, self.Comment) and 'hd' in text):
                                        elem_json['quality'] = 'HD'
                                    elem_json['premium'] = elem.find('i', class_='premiumIcon') \
                                                           or elem.find('span', class_='ico-private') or ''
                                    if elem_json['premium'] and not isinstance(elem_json['premium'], str):
                                        try:
                                            premium = elem_json['premium'].get_text(strip=True)
                                            if premium: elem_json['premium'] = premium
                                        except Exception:
                                            pass
                                    if premium_skip and premium_skip in elem_json['premium']:
                                        if DEBUG: logger.debug('PREMIUM-SKIP %s: %s' % (elem_json['premium'], elem_json['title']))
                                        continue
                                    if elem.find('div', class_='videoDetailsBlock') \
                                                             and elem.find('div', class_='videoDetailsBlock').find('span', class_='views'):
                                        elem_json['views'] = elem.find('div', class_='videoDetailsBlock')\
                                                            .find('span', class_='views').get_text('|', strip=True).split('|')[0]
                                    elif elem.find('div', class_='views'):
                                        elem_json['views'] = elem.find('div', class_='views').get_text(strip=True)
                            
                                    # External Labels
                                    if finds.get('profile_labels', {}).get('list_all_url'):
                                        url = self.parse_finds_dict(elem, finds['profile_labels']['list_all_url'])
                                        if url: elem_json['url'] = url
                                    if finds.get('profile_labels', {}).get('list_all_title'):
                                        title = self.parse_finds_dict(elem, finds['profile_labels']['list_all_title'])
                                        if title: elem_json['title'] = title
                                    if finds.get('profile_labels', {}).get('list_all_thumbnail'):
                                        thumbnail = self.parse_finds_dict(elem, finds['profile_labels']['list_all_thumbnail'])
                                        if thumbnail: elem_json['thumbnail'] = thumbnail
                                    if finds.get('profile_labels', {}).get('list_all_stime'):
                                        stime = self.parse_finds_dict(elem, finds['profile_labels']['list_all_stime'])
                                        if stime: elem_json['stime'] = stime
                                    if finds.get('profile_labels', {}).get('list_all_quality'):
                                        quality = self.parse_finds_dict(elem, finds['profile_labels']['list_all_quality'])
                                        if quality: elem_json['quality'] = quality
                                    if finds.get('profile_labels', {}).get('list_all_premium'):
                                        premium = self.parse_finds_dict(elem, finds['profile_labels']['list_all_premium'])
                                        if premium: elem_json['premium'] = premium
                                    if finds.get('profile_labels', {}).get('list_all_views'):
                                        views = self.parse_finds_dict(elem, finds['profile_labels']['list_all_views'])
                                        if views: elem_json['views'] = views

                            except Exception:
                                logger.error(elem)
                                logger.error(traceback.format_exc())
                                continue
                            
                            #if elem_json['premium']: continue
                            if not elem_json['url']: continue

                            matches.append(elem_json.copy())
                        AHkwargs['matches'] = matches

                    if matches_post and matches_list_all:
                        matches = matches_post(item, matches_list_all, **AHkwargs)
                        if custom_pagination:
                            if len(matches) < self.cnt_tot:
                                custom_pagination = False
                                self.last_page = 0
                    
                    if not matches and item.extra != 'continue':
                        logger.error('NO MATCHES: %s' % finds_out)
                        if AHkwargs.get('function_alt', '') != 'find_seasons' and item.c_type not in ['search']:
                            logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or section_list)
                        if self.last_page in [9999]:
                            self.last_page = 0
                        break

            else:
                matches =  AHkwargs['soup'] = item.matches
                if not matches: 
                    custom_pagination = False
                    self.last_page = 0
                    break
                del item.matches
                if matches_post_json_force and matches_post and matches: 
                    matches = matches_post(item, matches, **AHkwargs)
                    if custom_pagination:
                        if len(matches) < self.cnt_tot:
                            custom_pagination = False
                            self.last_page = 0

            AHkwargs['matches'] = matches
            if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))

            # Refrescamos variables posiblemente actualizadas en "matches_post"
            finds = self.finds.copy()
            finds_controls = finds.get('controls', {})
            self.cnt_tot = self.cnt_tot or finds_controls.get('cnt_tot', 20)
            host = finds_controls.get('host', self.host)
            self.doo_url = "%swp-admin/admin-ajax.php" % host
            if AHkwargs.get('url') and AHkwargs['url'] != item.url: self.next_page_url = next_page_url = item.url
            next_page_url = self.next_page_url
            host_referer = finds_controls.get('host_referer', host) or host_referer
            post = item.post or finds_controls.pop('post', None) or post
            headers = item.headers or finds_controls.get('headers', {}) or headers
            url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
            url_base64 = finds_controls.get('url_base64', True)

            # Buscamos la próxima página
            if soup:
                if finds_next_page:
                    next_page_url_save = next_page_url
                    next_page_url = self.parse_finds_dict(soup, finds_next_page, next_page=True, c_type=item.c_type).lstrip('#')
                    if next_page_url_save == next_page_url:
                        next_page_url = ''
                        self.last_page = 0
                    elif next_page_url: 
                        next_page_url = self.urljoin(self.host, next_page_url)
                        self.last_page = 9999 if self.last_page in [0, 9999, 99999] else self.last_page
                    elif not next_page_url: 
                        next_page_url = item.url
                        self.last_page = 0

                elif self.last_page > 0 and not custom_pagination:
                    url_page = item.url
                    url_page_control = 'url'
                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list):
                        if finds_controls['force_find_last_page'][2] == 'post': 
                            url_page = post
                            url_page_control = 'post'
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if scrapertools.find_single_match(url_page, rgx_org): break
                    else:
                        url = item.url.split('?')
                        item.url = url[0].rstrip('/') + finds_next_page_rgx[0][1] % str(self.curr_page)
                        if '?' in item.url and len(url) > 1: url[1] = url[1].replace('?', '&')
                        if len(url) > 1: item.url = '%s?%s' % (item.url, url[1].lstrip('/'))
                    next_page_url = item.url
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if url_page_control == 'url':
                            if not scrapertools.find_single_match(next_page_url, rgx_org): continue
                            next_page_url = re.sub(rgx_org, rgx_des % str(self.curr_page), next_page_url.rstrip('/')).replace('//?', '/?')
                        else:
                            if not scrapertools.find_single_match(post, rgx_org): continue
                            post = re.sub(rgx_org, rgx_des % str(self.curr_page), post.rstrip('/')).replace('//?', '/?')

                self.next_page_url = next_page_url

            if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                    % (str(self.curr_page), str(self.last_page), str(page_factor), str(next_page_url), len(matches)))

            # Buscamos la última página
            if self.last_page == 99999:                                              # Si es el valor inicial, buscamos
                try:
                    self.last_page = int(self.parse_finds_dict(soup, finds_last_page, next_page=True, c_type=item.c_type).lstrip('#'))
                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list) \
                                           and isinstance(finds_controls['force_find_last_page'][0], int) \
                                           and isinstance(finds_controls['force_find_last_page'][1], int):
                        if self.last_page >= finds_controls['force_find_last_page'][0]:
                            url = next_page_url
                            for rgx_org, rgx_des in finds_next_page_rgx:
                                if not scrapertools.find_single_match(url, rgx_org): continue
                                url = re.sub(rgx_org, rgx_des % str(finds_controls['force_find_last_page'][1]), 
                                             url.rstrip('/')).replace('//?', '/?')
                            soup_last_page = self.create_soup(url, hide_infobox=True, **kwargs)
                            self.last_page = int(self.parse_finds_dict(soup_last_page, finds_last_page, next_page=True, 
                                                                  c_type=item.c_type).lstrip('#'))
                    page_factor = float(len(matches)) / float(self.cnt_tot)
                except Exception:
                    self.last_page = 0
                    last_page_print = int((float(len(matches)) / float(self.cnt_tot)) + 0.999999)

                if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                        % (str(self.curr_page), str(self.last_page), str(page_factor), str(next_page_url), len(matches)))

            if item.matches_org is True: item.matches_org = matches[:]
            for elem in matches:
                new_item = Item()
                new_item.infoLabels = item.infoLabels.copy()
                if new_item.infoLabels['plot']: del new_item.infoLabels['plot']
                cnt_match += 1

                new_item.channel = item.channel
                new_item.category = new_item.channel.capitalize()
                new_item.contentType = 'movie'

                new_item.url = elem.get('url', '')
                if not new_item.url: continue
                new_item.url = self.urljoin(self.host, new_item.url)
                
                new_item.title = elem.get('title', '')
                new_item.title = self.unify_custom(new_item.title, item, elem, **AHkwargs)
                for clean_org, clean_des in finds.get('title_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.title, clean_org):
                            new_item.title = scrapertools.find_single_match(new_item.title, clean_org).strip()
                            break
                    else:
                        new_item.title = re.sub(clean_org, clean_des, new_item.title).strip()
                # Slugify, pero más light
                new_item.title = scrapertools.htmlclean(new_item.title).strip()
                new_item.title = new_item.title.replace("á", "a").replace("é", "e").replace("í", "i")\
                                               .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                                               .replace("ï¿½", "ñ").replace("Ã±", "ñ")
                new_item.title = scrapertools.decode_utf8_error(new_item.title).strip()
                if not new_item.title: continue
                new_item.contentTitle = new_item.title

                if elem.get('thumbnail', ''): 
                    elem['thumbnail'] = elem['thumbnail'] if elem['thumbnail'].startswith('http') \
                                                             else 'https:' + elem['thumbnail'] if elem['thumbnail'].startswith('//') \
                                                             else self.urljoin(self.host, elem['thumbnail'])
                    if ('tmdb' in elem['thumbnail'] or 'imdb' in elem['thumbnail']) and '=http' in elem['thumbnail']:
                        elem['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem['thumbnail']), '=(.*?)[&|$]')
                    new_item.thumbnail = elem['thumbnail']

                if elem.get('quality', ''):
                    new_item.quality = elem['quality']
                    for clean_org, clean_des in finds.get('quality_clean', []):
                        if clean_des is None:
                            if scrapertools.find_single_match(new_item.quality, clean_org):
                                new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                                break
                        else:
                            new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
                if str(elem.get('quality', '')).startswith('*'):
                    elem['quality'] = new_item.quality
                    new_item.quality = self.find_quality(elem, item)

                if elem.get('language', self.language):
                    new_item.language = elem.get('language', self.language)
                    for clean_org, clean_des in finds.get('language_clean', []):
                        if clean_des is None:
                            if scrapertools.find_single_match(new_item.language, clean_org):
                                new_item.language = scrapertools.find_single_match(new_item.language, clean_org).strip()
                                break
                        else:
                            new_item.language = re.sub(clean_org, clean_des, new_item.language).strip()
                if '*' in str(elem.get('language', '')):
                    elem['language'] = new_item.language
                    new_item.language = self.find_language(elem, item)

                if elem.get('extra', ''): new_item.extra = elem['extra']
                if elem.get('plot', ''): new_item.contentPlot =  elem['plot']
                if elem.get('broadcast', ''): new_item.contentPlot = '%s\n\n%s' % (elem['broadcast'], new_item.contentPlot)
                if elem.get('info', ''): new_item.info =  elem['info']
                if elem.get('mediatype', ''): new_item.contentType = elem['mediatype']
                if elem.get('post', None): new_item.post = elem['post']
                if elem.get('headers', None): new_item.headers = elem['headers']
                if elem.get('context', []): new_item.context = [elem['context']]
                new_item.action = elem.get('action', self.movie_action)
                if self.TEST_ON_AIR: new_item.action = 'findvideos'
                if finds_controls.get('mediatype', ''): new_item.contentType = finds_controls['mediatype']
                if finds_controls.get('action', ''): new_item.action = finds_controls['action']
                if elem.get('action', ''): new_item.action = elem['action']

                new_item.url = self.do_url_replace(new_item.url, url_replace)

                if postprocess:
                    new_item = postprocess(elem, new_item, item, **AHkwargs)

                if new_item:
                    cnt_title += 1

                    itemlist.append(new_item.clone())

                    cnt_title = len(itemlist)
                    if cnt_title >= self.cnt_tot and (len(matches) - cnt_match) + cnt_title > self.cnt_tot * cnt_tot_ovf:
                        break
                    
                    #if DEBUG: logger.debug('New_item: %s' % new_item)

            matches = matches[cnt_match:]                                       # Salvamos la entradas no procesadas
            cnt_tot_match += cnt_match                                          # Calcular el num. total de items mostrados

        if DEBUG: logger.debug('curr_page: %s / last_page: %s / cnt_match: %s / cnt_tot: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                % (str(self.curr_page), str(self.last_page), str(cnt_match), str(self.cnt_tot), 
                                   str(page_factor), str(next_page_url), len(matches)))

        # Si es necesario añadir paginacion
        if ((((self.curr_page <= self.last_page and self.last_page < 999999) \
                                          or (cnt_match > self.cnt_tot and len(matches) > 0  and next_page_url and not self.btdigg)\
                                          or len(matches) > 0) \
                                      and (next_page_url or len(matches) > 0)) or custom_pagination) \
                                      and AHkwargs['function'] != 'find_seasons':

            self.curr_page_print = int(cnt_tot_match / float(self.cnt_tot))
            if self.curr_page_print < 1:
                self.curr_page_print = 1
            if self.last_page and self.last_page not in [9999]:
                if self.last_page > 1:
                    last_page_print = int((self.last_page * page_factor) + 0.999999)
                title = '%s de %s' % (self.curr_page_print, last_page_print)
            else:
                title = '%s' % self.curr_page_print
            title = ">> Página siguiente %s" % title
            title = self.unify_custom(title, item, {'page': title}, **AHkwargs)
            if item.infoLabels.get('mediatype'): del item.infoLabels['mediatype']

            if finds_controls.get('jump_page') and self.last_page:
                itemlist.append(item.clone(action="get_page_num", to_action="list_all", title="[B]>> Ir a Página...[/B]", unify=False, 
                                           title_lista=title_lista, post=post, matches=matches, 
                                           url=next_page_url, last_page=str(self.last_page), curr_page=str(self.curr_page), 
                                           page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), 
                                           last_page_print=last_page_print))

            itemlist.append(item.clone(action="list_all", title=title, unify=False, 
                                       title_lista=title_lista, post=post, matches=matches, 
                                       url=next_page_url, last_page=str(self.last_page), curr_page=str(self.curr_page), 
                                       page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), 
                                       last_page_print=last_page_print))

        return itemlist

    def section(self, item, data= '', action="list_all", matches_post=None, postprocess=None, 
                section_list={}, finds={}, **kwargs):
        logger.info()
        from bs4 import Comment
        self.Comment = Comment

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        finds_out = finds.get('categories', {})
        finds_next_page = finds.get('next_page', {})
        finds_next_page_rgx = finds.get('next_page_rgx') if finds.get('next_page_rgx') else [['page\/\d+\/', 'page/%s/']]
        finds_last_page = finds.get('last_page', {})
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)
        itemlist = list()
        matches = list()
        matches_section = list()
        soup = {}
        if item.contentPlot: del item.infoLabels['plot']
        if not matches_post and item.matches_post: matches_post = item.matches_post

        AHkwargs = {'url': item.url, 'soup': item.matches or soup, 'finds': finds, 'kwargs': kwargs, 'function': 'section_A'}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = matches_post or kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)
        matches_post_json_force = kwargs.pop('matches_post_json_force', False)

        if DEBUG: logger.debug('FINDS_categories: %s; FINDS_controls: %s' % (finds_out, finds_controls))

        # Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
        title_lista = []                                        # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
        if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
            title_lista.extend(item.title_lista)                                # Se usa la lista de páginas anteriores en Item
            del item.title_lista                                                # ... limpiamos

        self.curr_page = 1                                                           # Página inicial
        self.last_page = 99999 if (not isinstance(finds_last_page, bool) \
                                   and not finds_controls.get('custom_pagination', False)) \
                                  else 9999 if finds_controls.get('custom_pagination', False) else 0    # Última página inicial
        last_page_print = 1                                                     # Última página inicial, para píe de página
        page_factor = finds_controls.get('page_factor', 1.0 )                   # Factor de conversión de pag. web a pag. Alfa
        self.cnt_tot = finds_controls.get('cnt_tot', 20)                        # Poner el num. máximo de items por página
        cnt_tot_ovf = finds_controls.get('page_factor_overflow', 1.3)           # Overflow al num. máximo de items por página
        cnt_match = 0                                                           # Contador de matches procesadas
        cnt_title = 0                                                           # Contador de líneas insertadas en Itemlist
        cnt_tot_match = 0.0                                                     # Contador TOTAL de líneas procesadas de matches
        custom_pagination =  finds_controls.get('custom_pagination', False)     # Paginación controlada por el usuario
        if 'cnt_tot_match' in item:
            cnt_tot_match = float(item.cnt_tot_match)                           # restauramos el contador TOTAL de líneas procesadas de matches
            del item.cnt_tot_match
        if 'curr_page' in item:
            self.curr_page = int(item.curr_page)                                # Si viene de una pasada anterior, lo usamos
            del item.curr_page                                                  # ... y lo borramos
        if 'last_page' in item:
            self.last_page = int(item.last_page)                                # Si viene de una pasada anterior, lo usamos
            del item.last_page                                                  # ... y lo borramos
        if 'page_factor' in item:
            page_factor = float(item.page_factor)                               # Si viene de una pasada anterior, lo usamos
            del item.page_factor                                                # ... y lo borramos
        if 'last_page_print' in item:
            last_page_print = item.last_page_print                              # Si viene de una pasada anterior, lo usamos
            del item.last_page_print                                            # ... y lo borramos
        if 'unify' in item:
            del item.unify                                                      # ... y lo borramos

        inicio = time.time()                                                    # Controlaremos que el proceso no exceda de un tiempo razonable
        fin = inicio + finds_controls.get('inicio', 5)                          # Después de este tiempo pintamos (segundos)
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)     # Timeout normal
        timeout_search = timeout * 2                                            # Timeout para búsquedas

        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)
        reverse = finds_controls.get('reverse', False)

        if section_list:
            for genre, url in list(section_list.items()):
                matches.append({'url': url, 'title': genre})
            item.matches = matches

        self.next_page_url = next_page_url = item.url
        # Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
        while (cnt_title < self.cnt_tot and (self.curr_page <= self.last_page or (self.last_page == 0 and finds_next_page \
                                             and next_page_url and (item.matches or matches))) \
                                        and fin > time.time()) \
                                        or item.matches:

            # Descarga la página
            soup = data
            data = ''
            cnt_match = 0                                                       # Contador de líneas procesadas de matches
            if not item.matches and next_page_url:                              # si no viene de una pasada anterior, descargamos
                kwargs.update({'timeout': timeout, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
                soup = data or self.create_soup(next_page_url, **kwargs)

                itemlist = self.itemlist + itemlist
                self.itemlist = []

                if soup:
                    AHkwargs['soup'] = self.response.soup or self.response.json or self.response.data
                    self.curr_page += 1
                    matches_section = self.parse_finds_dict(soup, finds_out) if finds_out \
                                      else (self.response.soup or self.response.json or self.response.data)
                    if not isinstance(matches_section, (list, _dict)):
                        matches_section = []

            else:
                matches =  AHkwargs['soup'] = item.matches
                if not matches: 
                    custom_pagination = False
                    self.last_page = 0
                    break
                del item.matches
                if matches_post_json_force and matches_post and matches: 
                    matches = matches_post(item, matches, **AHkwargs)
                    if custom_pagination:
                        if len(matches) < self.cnt_tot:
                            custom_pagination = False
                            self.last_page = 0

            if not matches and matches_section and ('profile' in finds_controls or not matches_post):
                for elem in matches_section:
                    if isinstance(elem, str): continue
                    elem_json = {}
                    #logger.error(elem)

                    try:
                        if profile in [DEFAULT]:
                            elem_json['url'] = elem.get("href", '') or elem.a.get("href", '')
                            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                                     or elem.img.get('data-src', '') \
                                                                                                     or elem.img.get('src', '')
                            if elem.find('span', class_=['videoCount', 'videosNumber']):
                                elem_json['cantidad'] = elem.find('span', class_=['videoCount', 'videosNumber']).get_text(strip=True)
                            elif elem.find('div', class_='videos'):
                                elem_json['cantidad'] = elem.find('div', class_='videos').get_text(strip=True)
                            elif elem.find(string=re.compile(r"(?i)videos|movies")):
                                elem_json['cantidad'] = elem.find(string=re.compile(r"(?i)videos|movies"))
                                cantidad = elem_json['cantidad']
                                try:
                                    for x in range(5):
                                        cantidad = elem_json['cantidad']
                                        if scrapertools.find_single_match(str(elem_json['cantidad']), "\d+"):
                                            elem_json['cantidad'] = scrapertools.find_single_match(str(elem_json['cantidad']), "(\d+)")
                                            break
                                        elem_json['cantidad'] = elem_json['cantidad'].parent
                                    else:
                                        elem_json['cantidad'] = ''
                                        logger.error('ERROR en cantidad.parent: %s' % cantidad)
                                except Exception:
                                    elem_json['cantidad'] = ''
                                    logger.error('ERROR en cantidad.parent: %s' % cantidad)
                                    logger.error(elem)
                                    logger.error(traceback.format_exc())
                            if not elem_json.get('cantidad') and elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                             and 'videos' in text):
                                elem_json['cantidad'] = self.do_soup(elem.find(text=lambda text: isinstance(text, self.Comment) \
                                                                     and 'videos' in text)).find(class_='videos').get_text(strip=True)
                            if elem_json.get('cantidad'):
                                elem_json['cantidad'] = scrapertools.find_single_match(elem_json['cantidad'], "(\d+)")
                            if elem.a:
                                elem_json['title'] = elem.a.get('data-mxptext', '') or elem.a.get('title', '') \
                                                                                    or (elem.img.get('alt', '') if elem.img else '') \
                                                                                    or elem.a.get_text(strip=True)
                            else:
                                elem_json['title'] = elem.get('data-mxptext', '') or elem.get('title', '') \
                                                                                  or elem.get('alt', '') \
                                                                                  or elem.get_text(strip=True)
                            
                            # External Labels
                            if finds.get('profile_labels', {}).get('section_url'):
                                url = self.parse_finds_dict(elem, finds['profile_labels']['section_url'])
                                url = elem_json['url'] = url
                            if finds.get('profile_labels', {}).get('section_title'):
                                title = self.parse_finds_dict(elem, finds['profile_labels']['section_title'])
                                if title: elem_json['title'] = title
                            if finds.get('profile_labels', {}).get('section_thumbnail'):
                                thumbnail = self.parse_finds_dict(elem, finds['profile_labels']['section_thumbnail'])
                                if thumbnail: elem_json['thumbnail'] = thumbnail
                            if finds.get('profile_labels', {}).get('section_stime'):
                                stime = self.parse_finds_dict(elem, finds['profile_labels']['section_stime'])
                                elem_json['stime'] = stime
                            if finds.get('profile_labels', {}).get('section_cantidad'):
                                cantidad = self.parse_finds_dict(elem, finds['profile_labels']['section_cantidad'])
                                if not cantidad and elem.find(text=lambda text: isinstance(text, self.Comment) and 'videos' in text):
                                    cantidad = self.do_soup(elem.find(text=lambda text: isinstance(text, self.Comment) and 'videos' in text))
                                    cantidad = self.parse_finds_dict(cantidad, finds['profile_labels']['section_cantidad'])
                                if cantidad: elem_json['cantidad'] = cantidad

                    except Exception:
                        logger.error(elem)
                        logger.error(traceback.format_exc())
                    
                    if not elem_json.get('url', ''): continue

                    matches.append(elem_json.copy())
                AHkwargs['matches'] = matches

            if matches_post and matches_section:
                matches = matches_post(item, matches_section, **AHkwargs)
                if custom_pagination:
                    if len(matches) < self.cnt_tot:
                        custom_pagination = False
                        self.last_page = 0

            if not matches:
                logger.error('NO MATCHES: %s' % finds_out)
                logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or section_list)
                return itemlist

            AHkwargs['matches'] = matches
            if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))

            # Refrescamos variables posiblemente actualizadas en "matches_post"
            finds = self.finds.copy()
            finds_controls = finds.get('controls', {})
            self.cnt_tot = self.cnt_tot or finds_controls.get('cnt_tot', 20)
            reverse = finds_controls.get('reverse', False)
            if AHkwargs.get('url') and AHkwargs['url'] != item.url: self.next_page_url = next_page_url = item.url
            next_page_url = self.next_page_url
            host_referer = finds_controls.get('host_referer', host) or host_referer
            post = item.post or finds_controls.pop('post', None) or post
            headers = item.headers or finds_controls.get('headers', {}) or headers
            url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
            
            # Buscamos la próxima página
            if soup:
                if item.extra.lower() in ['categorías', 'categorias'] and self.cnt_tot != 9999:
                    next_page_url = ''
                elif finds_next_page:
                    next_page_url_save = next_page_url
                    next_page_url = self.parse_finds_dict(soup, finds_next_page, next_page=True, c_type=item.c_type).lstrip('#')
                    if next_page_url_save == next_page_url:
                        next_page_url = ''
                        self.last_page = 0
                    elif next_page_url: 
                        next_page_url = self.urljoin(self.host, next_page_url)
                        self.last_page = 9999 if self.last_page in [0, 9999, 99999] else self.last_page
                    elif not next_page_url: 
                        next_page_url = item.url
                        self.last_page = 0

                elif self.last_page > 0 and not custom_pagination:
                    url_page = item.url
                    url_page_control = 'url'
                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list):
                        if finds_controls['force_find_last_page'][2] == 'post': 
                            url_page = post
                            url_page_control = 'post'
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if scrapertools.find_single_match(url_page, rgx_org): break
                    else:
                        url = item.url.split('?')
                        item.url = url[0].rstrip('/') + finds_next_page_rgx[0][1] % str(self.curr_page)
                        if '?' in item.url and len(url) > 1: url[1] = url[1].replace('?', '&')
                        if len(url) > 1: item.url = '%s?%s' % (item.url, url[1].lstrip('/'))
                    next_page_url = item.url
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if url_page_control == 'url':
                            if not scrapertools.find_single_match(next_page_url, rgx_org): continue
                            next_page_url = re.sub(rgx_org, rgx_des % str(self.curr_page), next_page_url.rstrip('/')).replace('//?', '/?')
                        else:
                            if not scrapertools.find_single_match(post, rgx_org): continue
                            post = re.sub(rgx_org, rgx_des % str(self.curr_page), post.rstrip('/')).replace('//?', '/?')

                if not next_page_url:
                    self.cnt_tot = 9999
                    self.last_page = 0

                self.next_page_url = next_page_url

            if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                    % (str(self.curr_page), str(self.last_page), str(page_factor), str(next_page_url), len(matches)))

            # Buscamos la última página
            if self.last_page == 99999:                                              # Si es el valor inicial, buscamos
                try:
                    self.last_page = int(self.parse_finds_dict(soup, finds_last_page, next_page=True, c_type=item.c_type).lstrip('#'))
                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list) \
                                           and isinstance(finds_controls['force_find_last_page'][0], int) \
                                           and isinstance(finds_controls['force_find_last_page'][1], int):
                        if self.last_page >= finds_controls['force_find_last_page'][0]:
                            url = next_page_url
                            for rgx_org, rgx_des in finds_next_page_rgx:
                                if not scrapertools.find_single_match(url, rgx_org): continue
                                url = re.sub(rgx_org, rgx_des % str(finds_controls['force_find_last_page'][1]), 
                                             url.rstrip('/')).replace('//?', '/?')
                            soup_last_page = self.create_soup(url, hide_infobox=True, **kwargs)
                            self.last_page = int(self.parse_finds_dict(soup_last_page, finds_last_page, next_page=True, 
                                                                  c_type=item.c_type).lstrip('#'))
                    page_factor = float(len(matches)) / float(self.cnt_tot)
                except Exception:
                    self.last_page = 0
                    last_page_print = int((float(len(matches)) / float(self.cnt_tot)) + 0.999999)

                if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                        % (str(self.curr_page), str(self.last_page), str(page_factor), str(next_page_url), len(matches)))
            
            if item.matches_org is True: item.matches_org = matches[:]
            for elem in matches:
                if not elem.get('url'): continue
                cnt_match += 1
                elem['url'] = self.urljoin(self.host, elem['url'])
                if elem.get('thumbnail', ''): 
                    elem['thumbnail'] = elem['thumbnail'] if elem['thumbnail'].startswith('http') \
                                                             else 'https:' + elem['thumbnail'] if elem['thumbnail'].startswith('//') \
                                                             else self.urljoin(self.host, elem['thumbnail'])
                    if ('tmdb' in elem['thumbnail'] or 'imdb' in elem['thumbnail']) and '=http' in elem['thumbnail']:
                        elem['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem['thumbnail']), '=(.*?)[&|$]')

                new_item = item.clone(
                                      category=item.channel.capitalize(),
                                      title=elem.get('title', ''),
                                      action=action,
                                      url=elem.get('url', ''),
                                      thumbnail=elem.get('thumbnail', item.thumbnail)
                                      )

                if item.extra: new_item.extra = item.extra
                if elem.get('extra', ''): new_item.extra = elem['extra']
                if elem.get('plot', ''): new_item.contentPlot =  elem['plot']
                if elem.get('broadcast', ''): new_item.contentPlot = '%s\n\n%s' % (elem['broadcast'], new_item.contentPlot)
                if 'post' in new_item: del new_item.post
                if elem.get('post', None): new_item.post = elem['post']
                if 'headers' in new_item: del new_item.headers
                if elem.get('headers', None): new_item.headers = elem['headers']
                if elem.get('context', []): new_item.context = [elem['context']]
                if finds_controls.get('mediatype', ''): new_item.contentType = finds_controls['mediatype']
                if finds_controls.get('action', ''): new_item.action = finds_controls['action']
                if elem.get('action', ''): new_item.action = elem['action']

                new_item.title = self.unify_custom(new_item.title, item, elem, **AHkwargs)
                for clean_org, clean_des in finds.get('title_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.title, clean_org):
                            new_item.title = scrapertools.find_single_match(new_item.title, clean_org).strip()
                            break
                    else:
                        new_item.title = re.sub(clean_org, clean_des, new_item.title).strip()
                # Slugify, pero más light
                new_item.title = scrapertools.htmlclean(new_item.title).strip()
                new_item.title = new_item.title.replace("á", "a").replace("é", "e").replace("í", "i")\
                                               .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                                               .replace("ï¿½", "ñ").replace("Ã±", "ñ")
                new_item.title = scrapertools.decode_utf8_error(new_item.title).strip()
                if not new_item.title: continue
                
                if elem.get('quality', ''):
                    new_item.quality = elem['quality']
                    for clean_org, clean_des in finds.get('quality_clean', []):
                        if clean_des is None:
                            if scrapertools.find_single_match(new_item.quality, clean_org):
                                new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                                break
                        else:
                            new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
                if str(elem.get('quality', '')).startswith('*'):
                    elem['quality'] = new_item.quality
                    new_item.quality = self.find_quality(elem, item)

                new_item.url = self.do_url_replace(new_item.url, url_replace)

                if postprocess:
                    new_item = postprocess(elem, new_item, item, **AHkwargs)

                if new_item:
                    cnt_title += 1

                    itemlist.append(new_item.clone())

                    cnt_title = len(itemlist)
                    # Contador de líneas añadidas
                    if cnt_title >= self.cnt_tot and (len(matches) - cnt_match) + cnt_title > self.cnt_tot * cnt_tot_ovf:
                        break

                    #if DEBUG: logger.debug('New_item: %s' % new_item)

            matches = matches[cnt_match:]                                       # Salvamos la entradas no procesadas
            cnt_tot_match += cnt_match                                          # Calcular el num. total de items mostrados

        if DEBUG: logger.debug('curr_page: %s / last_page: %s / cnt_match: %s / cnt_tot: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                % (str(self.curr_page), str(self.last_page), str(cnt_match), str(self.cnt_tot), 
                                   str(page_factor), str(next_page_url), len(matches)))

        if item.extra.lower() in ['categorías', 'categorias'] or item.title.lower() in ['categorías', 'categorias']:
            itemlist = sorted(itemlist, key=lambda it: it.title)
        if reverse:
            itemlist = itemlist[::-1]

        # Si es necesario añadir paginacion
        if ((((self.curr_page <= self.last_page and self.last_page < 999999) \
                                          or (cnt_match > self.cnt_tot and len(matches) > 0  and next_page_url and not self.btdigg)\
                                          or len(matches) > 0) \
                                      and (next_page_url or len(matches) > 0)) or custom_pagination) \
                                      and AHkwargs['function'] != 'find_seasons':

            self.curr_page_print = int(cnt_tot_match / float(self.cnt_tot))
            if self.curr_page_print < 1:
                self.curr_page_print = 1
            if self.last_page and self.last_page not in [9999]:
                if self.last_page > 1:
                    last_page_print = int((self.last_page * page_factor) + 0.999999)
                title = '%s de %s' % (self.curr_page_print, last_page_print)
            else:
                title = '%s' % self.curr_page_print
            title = ">> Página siguiente %s" % title
            title = self.unify_custom(title, item, {'page': title}, **AHkwargs)
            if item.infoLabels.get('mediatype'): del item.infoLabels['mediatype']

            if finds_controls.get('jump_page') and self.last_page:
                itemlist.append(item.clone(action="get_page_num", to_action="section", title="[B]>> Ir a Página...[/B]", unify=False, 
                                           title_lista=title_lista, post=post, matches=matches, 
                                           url=next_page_url, last_page=str(self.last_page), curr_page=str(self.curr_page), 
                                           page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), 
                                           last_page_print=last_page_print))

            itemlist.append(item.clone(action="section", title=title, 
                                       title_lista=title_lista, post=post, matches=matches, unify=False, 
                                       url=next_page_url, last_page=str(self.last_page), curr_page=str(self.curr_page), 
                                       page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), 
                                       last_page_print=last_page_print))

        return itemlist

    def get_video_options(self, item, url, data='', langs=[], matches_post=None, postprocess=None, 
                          verify_links=False, generictools=False, findvideos_proc=False, finds={}, **kwargs):
        if item.contentType == 'movie':
            logger.info('Movie: %s' % item.contentTitle)
        else:
            logger.info('Serie: %s; Season: %s: Episode: %s' % (item.contentSerieName, item.contentSeason, item.contentEpisodeNumber))
        if DEBUG: logger.debug('FINDS: %s' % finds)

        import xbmc
        self.Window_IsMedia = bool(xbmc.getCondVisibility('Window.IsMedia'))
        if not item.url_tvshow: item.url_tvshow = item.url

        if not finds: finds = self.finds.copy()
        self.finds = finds.copy()
        finds_out = finds.get('findvideos', {})
        finds_out_episodes = finds.get('episodes', {})
        finds_langs = finds.get('langs', {})
        finds_controls = finds.get('controls', {})
        profile = self.profile = finds_controls.get('profile', self.profile)
        options = list()
        results = list()
        itemlist = []
        itemlist_total = []
        soup = {}
        matches = []
        matches_findvideos = []
        if not matches_post and item.matches_post: matches_post = item.matches_post
        matches_post_episodes = None

        AHkwargs = {'url': item.url, 'soup': soup, 'finds': finds, 'kwargs': kwargs, 'function': 'get_video_options_A', 'videolibrary': False}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_get_video_options'] = matches_post or kwargs.pop('matches_post_get_video_options', None)

        if DEBUG: logger.debug('FINDS_findvideos: %s; FINDS_langs: %s; FINDS_controls: %s' % (finds_out, finds_langs, finds_controls))

        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)
        self.host_torrent = finds_controls.get('host_torrent', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % self.host
        host_torrent_referer = finds_controls.get('host_torrent_referer', self.host_torrent)
        url_replace = self.url_replace = self.finds.get('url_replace', [])
        manage_torrents = finds_controls.get('manage_torrents', True)
        
        url = self.do_url_replace(url, url_replace)
 
        if data or item.url.startswith('magnet') or item.url.endswith('.torrent'):
            soup = data
            response = self.response
            response.data = data
            response.soup = soup
        else:
            kwargs.update({'timeout': timeout, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
            soup = self.create_soup(url, **kwargs)

            itemlist = self.itemlist + itemlist
            self.itemlist = []

            response = self.response
            soup = response.soup or {}
            AHkwargs['soup'] = response.soup or response.json or response.data
        
        langs = langs or self.parse_finds_dict(soup, finds_langs) or self.language
        if not isinstance(langs, list):
            langs = []

        if not item.matches and (item.url.startswith('magnet') or item.url.endswith('.torrent') or not finds_out):
            elem_json = {}

            elem_json['url'] = item.url
            if not elem_json['url'].startswith('magnet'): elem_json['url'] = self.urljoin(self.host, elem_json['url'])
            elem_json['quality'] = item.quality
            elem_json['language'] = item.language
            elem_json['server'] = 'torrent' if (elem_json['url'].startswith('magnet') \
                                                or elem_json['url'].endswith('.torrent')) else ''
            elem_json['title'] = elem_json['server'] or '%s'
            if item.torrent_info: elem_json['size'] = elem_json['torrent_info'] = item.torrent_info
            if item.btdig_in_use: elem_json['btdig_in_use'] = item.btdig_in_use
            if item.password: elem_json['password'] = item.password
            if item.plot: elem_json['plot'] = item.plot
            if item.post: elem_json['post'] = item.post
            if item.headers: elem_json['headers'] = item.headers

            matches.append(elem_json.copy())
        
        if not item.matches and not matches and finds_out:
            matches_findvideos = self.parse_finds_dict(soup, finds_out) if finds_out \
                                 else (self.response.soup or self.response.json or self.response.data)
            if not isinstance(matches_findvideos, (list, _dict)):
                matches_findvideos = []

            if not matches and matches_findvideos and ('profile' in finds_controls or not matches_post):
                for elem in matches_findvideos:
                    if isinstance(elem, str): continue
                    elem_json = {}
                    #logger.error(elem)

                    try:
                        if profile in [DEFAULT]:
                            elem_json['url'] = elem.get("href", '') or (elem.a.get("href", '') if elem.a else '') or elem.get("src", '')
                            elem_json['quality'] = item.quality
                            elem_json['language'] = item.language
                            elem_json['server'] = 'torrent' if (elem_json['url'].startswith('magnet') \
                                                                or elem_json['url'].endswith('.torrent')) else ''
                            elem_json['title'] = elem_json['server'] or '%s'

                            # External Labels
                            if finds.get('profile_labels', {}).get('findvideos_url'):
                                url = self.parse_finds_dict(elem, finds['profile_labels']['findvideos_url'])
                                if url: elem_json['url'] = url
                            if finds.get('profile_labels', {}).get('findvideos_title'):
                                title = self.parse_finds_dict(elem, finds['profile_labels']['findvideos_title'])
                                if title: elem_json['title'] = title
                            if finds.get('profile_labels', {}).get('findvideos_quality'):
                                quality = self.parse_finds_dict(elem, finds['profile_labels']['findvideos_quality'])
                                if quality: elem_json['quality'] = quality
                            if finds.get('profile_labels', {}).get('findvideos_language'):
                                language = self.parse_finds_dict(elem, finds['profile_labels']['findvideos_language'])
                                if language: elem_json['language'] = language
                            if finds.get('profile_labels', {}).get('findvideos_server'):
                                server = self.parse_finds_dict(elem, finds['profile_labels']['findvideos_server'])
                                if server: elem_json['server'] = server
                            
                    except Exception:
                        logger.error(traceback.format_exc())

                    matches.append(elem_json.copy())
                AHkwargs['matches'] = matches

            if matches_post and matches_findvideos:
                matches, langs = matches_post(item, matches_findvideos, langs, response, **AHkwargs)

        # Refrescamos variables posiblemente actualizadas en "matches_post"
        finds = self.finds.copy()
        finds_controls = finds.get('controls', {})
        self.host_torrent = finds_controls.get('host_torrent', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % self.host
        host_torrent_referer = finds_controls.get('host_torrent_referer', self.host_torrent)
        post = item.post or finds_controls.pop('post', None) or post
        headers = item.headers or finds_controls.get('headers', {}) or headers
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
        url_base64 = finds_controls.get('url_base64', True)

        AHkwargs['matches'] = matches
        if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))

        for _lang in langs or ['CAST']:
            lang = _lang

            if 'descargar' in lang: continue
            if 'latino' in lang: lang = ['LAT']
            if 'español' in lang: lang += ['CAST']
            if 'subtitulado' in lang: lang += ['VOS']

            for elem in matches:
                if not elem.get('url', ''): continue
                    
                elem['channel'] = item.channel
                if not elem.get('mediatype', '') and finds_controls.get('mediatype', ''): elem['mediatype'] = finds_controls['mediatype']
                if not elem.get('action', '') and finds_controls.get('action', ''): elem['action'] = finds_controls['action']
                elem['action'] = elem.get('action', 'play')
                elem['language'] = elem.get('language', lang)

                if elem['url'].startswith('//'):
                    elem['url'] = 'https:%s' % elem['url']
                if url_base64: elem['url'] = self.convert_url_base64(elem['url'], self.host_torrent, referer=host_torrent_referer, item=item)

                if not 'title' in elem:
                    elem['title'] = 'torrent' if elem.get('server', '').lower() == 'torrent' else '%s'

                # Tratamos las particulirades de los .torrents/magnets
                if elem.get('btdig_in_use', False): btdig_in_use = elem['btdig_in_use']
                if elem.get('server', '').lower() == 'torrent' and manage_torrents:
                    elem = self.manage_torrents(item, elem, lang, soup, finds, **kwargs)

                options.append((lang, elem))

        results.append([soup, options])

        if not findvideos_proc: return results[0]

        for lang, elem in results[0][1]:
            new_item = item.clone()
            
            if verify_links and elem.get('server', '') and elem.get('server', '').lower() != 'torrent':
                if config.get_setting("hidepremium") and not servertools.is_server_enabled(elem['server']):
                    continue
                item_url = elem['url']
                if not isinstance(verify_links, bool): item_url = verify_links(Item(url=item_url, server=elem['server']))[0].url
                elem['alive'] = servertools.check_video_link(item_url, elem['server'])  # Link Activo ?
                if 'NO' in elem['alive']:
                    continue
            
            new_item.channel = elem.get('channel', item.channel)
            new_item.category = new_item.channel.capitalize()
            new_item.action = elem.get('action', 'play')
            new_item.url = elem.get('url', '')
            new_item.server = elem.get('server', '')
            new_item.title = elem.get('title', '%s')
            if elem.get('post', None): new_item.post = elem['post']
            new_item.headers = elem.get('headers', {'Referer': item.url})
            new_item.setMimeType = 'application/vnd.apple.mpegurl'

            if elem.get('quality', ''):
                new_item.quality = elem['quality']
                for clean_org, clean_des in finds.get('quality_clean', []):
                    if clean_des is None:
                        if scrapertools.find_single_match(new_item.quality, clean_org):
                            new_item.quality = scrapertools.find_single_match(new_item.quality, clean_org).strip()
                            break
                    else:
                        new_item.quality = re.sub(clean_org, clean_des, new_item.quality).strip()
            if str(elem.get('quality', '')).startswith('*'):
                elem['quality'] = new_item.quality
                new_item.quality = self.find_quality(elem, item)

            if elem.get('extra', ''): new_item.extra = elem['extra']
            if elem.get('plot', ''): new_item.contentPlot = elem['plot']
            if elem.get('broadcast', ''): new_item.contentPlot = '%s\n\n%s' % (elem['broadcast'], new_item.contentPlot)
            if elem.get('torrent_info', ''): new_item.torrent_info = elem['torrent_info']
            if elem.get('password', ''): new_item.password = elem['password']
            if elem.get('torrents_path', ''): new_item.torrents_path = elem['torrents_path']
            if elem.get('torrent_alt', ''): new_item.torrent_alt = elem['torrent_alt']
            if elem.get('alive', ''): new_item.alive = elem['alive']
            if elem.get('unify', ''): new_item.unify = elem['unify']
            if elem.get('folder', ''): new_item.folder = elem['folder']
            if elem.get('item_org', ''): new_item.item_org = elem['item_org']
            if elem.get('subtitle', ''): new_item.subtitle = elem['subtitle']
            if elem.get('context', []): new_item.context = [elem['context']]
            new_item.size = self.convert_size(elem.get('size', 0))

            new_item.title = self.unify_custom(new_item.title, item, elem, **AHkwargs)

            new_item.url = self.do_url_replace(new_item.url, url_replace)

            if postprocess:
                new_item = postprocess(elem, new_item, item, **AHkwargs)

            if new_item: itemlist.append(new_item.clone())

        if itemlist:
            try:
                itemlist = servertools.get_servers_itemlist(itemlist, lambda it: it.title % it.server.capitalize())
            except Exception:
                pass
            if itemlist and itemlist[0].channel != 'filtertools':
                try:
                    itemlist = sorted(itemlist, key=lambda it: (int(-it.size if it.size \
                                                and it.contentType == 'movie' else it.size if it.size else 0), 
                                                it.language[0] if (it.language and isinstance(it.language, list)) else '', 
                                                it.server))
                except Exception:
                    size = []
                    for it in itemlist:
                        size += [[it.size, it.title]]
                    logger.error('ERROR_SIZE: %s' % size)
                    logger.error(traceback.format_exc())

            itemlist_total.extend(itemlist)

        # Requerido para AutoPlay
        autoplay.start(itemlist, item)

        return itemlist_total


class DooPlay(AlfaChannelHelper):

    def __init__(self, host, canonical={}, channel='', finds={}, debug=False,
                 list_language=[], list_quality=[], list_quality_tvshow=[], list_quality_movies=[], 
                 list_servers=[], language=[], idiomas={}, url_replace=[], 
                 IDIOMAS_TMDB={0: 'es', 1: 'en', 2: 'es,en'}, forced_proxy_opt=''):
        global DEBUG
        DEBUG = debug
        from core import httptools

        self.host = host
        self.canonical = canonical
        self.channel = channel
        self.finds = finds or {'find': dict([('find', [{'tagOR': ['div'], 'id': ['archive-content']}, 
                                                       {'tag': ['div'], 'class': ['content', 'result-item']}]), 
                                             ('find_all', [{'tag': ['article'], 'class': ['item movies', 'item tvshows']}])]),
                               'categories': dict([('find', [{'tag': ['li'], 'id': ['menu-item-%s']}, 
                                                             {'tag': ['ul'], 'class': ['sub-menu']}]), 
                                                   ('find_all', [{'tag': ['li']}])]), 
                               'search': {'find_all': [{'tag': ['div'], 'class': ['result-item']}]}, 
                               'get_language': {'find_all': [{'tag': ['span'], 'class': ['flag']}]}, 
                               'get_language_rgx': '(?:flags\/|-)(\w+)\.(?:png|jpg|jpeg|webp)', 
                               'get_quality': dict([('find', [{'tag': ['span'], 'class': ['quality']}]), 
                                                    ('get_text', [{'strip': True}])]), 
                               'get_quality_rgx': '', 
                               'next_page': {}, 
                               'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
                               'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}, 
                                                            {'tag': ['span']}]), 
                                                  ('get_text', [{'@TEXT': '(?i)\d+\s*de\s*(\d+)'}])]), 
                               'year': dict([('find', [{'tag': ['div'], 'class': ['metadata', 'meta']}]), 
                                             ('get_text',[{'tag': '|', 'strip': True}] )]), 
                               'season_episode': {'find': [{'tag': ['img'], '@ARG': 'alt', '@TEXT': '(?i)(\d+x\d+)'}]}, 
                               'seasons': dict([('find', [{'tag': ['div'], 'id': ['seasons']}]), 
                                                ('find_all', [{'tag': ['div'], 'class': ['se-q']}])]), 
                               'season_num': {'find': [{'tag': ['span'], 'class': ['se-t'], '@TEXT': '(\d+)'}]}, 
                               'episode_url': '', 
                               'episodes': dict([('find', [{'tag': ['div'], 'id': ['seasons']}]), 
                                                 ('find_all', [{'tag': ['li']}])]), 
                               'episode_num': dict([('find', [{'tag': ['div'], 'class': ['numerando']}]), 
                                                    ('get_text', [{'strip': True}])]), 
                               'episode_clean': [], 
                               'plot': dict([('find', [{'tag': ['div'], 'class': ['texto', 'contenido']}]), 
                                             ('get_text', [{'strip': True}])]), 
                               'findvideos': dict([('find', [{'tagOR': ['div'], 'id': ['playeroptions']}, 
                                                             {'tag': ['ul'], 'class': ['options']}]), 
                                                   ('find_all', [{'tag': 'li'}])]), 
                               'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie', ''],
                                              ['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s+sub|\s+spn|\s+\(+en\s+emisi.n\)+|\s+s2|\s+eng|\s+espa\w+', '']],
                               'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real', ''], 
                                                 ['extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
                               'language_clean': [], 
                               'url_replace': [], 
                               'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 
                                            'add_video_to_videolibrary': True, 'get_lang': False, 
                                            'custom_pagination': False}, 
                               'timeout': 5}

        self.url = self.movie_path = self.tv_path = self.movie_action = self.tv_action = ''
        self.timeout = finds.get('control', {}).get('timeout', 5)
        self.doo_url = "%swp-admin/admin-ajax.php" % self.host
        self.forced_proxy_opt = forced_proxy_opt
        self.list_language = list_language
        self.list_servers = list_servers or LIST_SERVERS
        self.list_quality_movies = list_quality_movies or LIST_QUALITY_MOVIES
        self.list_quality_tvshow = list_quality_tvshow or LIST_QUALITY_TVSHOW
        self.list_quality = list_quality or self.list_quality_movies + self.list_quality_tvshow
        self.language = language
        self.idiomas = idiomas or IDIOMAS
        self.IDIOMAS_TMDB = finds.get('control', {}).get('IDIOMAS_TMDB', {}) or IDIOMAS_TMDB
        self.url_replace = url_replace
        self.Window_IsMedia = True
        self.season_colapse = True
        self.unescape = False
        self.alfa_domain_web_list = {}
        self.headers = {}
        self.unescape = False
        self.response_preferred_proxy_ip = ''
        self.httptools = httptools
        self.response = self.httptools.build_response(HTTPResponse=True)
        self.response_proxy = self.response.proxy__
        self.itemlist = []
        self.profile = 'default'
        self.color_setting = {}
        self.window = window
        self.Comment = None
        self.last_page = 0
        self.curr_page = 0
        self.next_page_url = ''


    def list_all_matches(self, item, matches_int, **AHkwargs):
        logger.info()

        matches = []
        finds = self.finds
        
        if item.json:
            json = jsontools.load(matches_int) if not isinstance(matches_int, _dict) else matches_int
    
            for key, elem in list(json.items()):
                elem_json = {}

                elem_json['url'] = elem.get('url', '')
                elem_json['title'] = elem.get('title', '')
                elem_json['thumbnail'] = elem.get('thumb', '') or elem.get('thumbnail', '') or elem.get('img', '')
                if ('tmdb' in elem_json['thumbnail'] or 'imdb' in elem_json['thumbnail']) and '=http' in elem_json['thumbnail']:
                    elem_json['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem_json['thumbnail']), '=(.*?)[&|$]')
                elem_json['year'] = elem.get('year', '-') or '-'
                if elem.get('info', ''):
                    elem_json['plot'] = elem['info']
                if finds['controls']['get_lang']:
                    elem_json['language'] = '*'
                
                if not elem_json['url']: continue

                matches.append(elem_json.copy())

        else:
            for elem in matches_int:
                elem_json = {}
                if DEBUG: logger.debug('MATCHES_int %s' % (str(elem)))

                if item.c_type == 'episodios':
                    sxe = self.parse_finds_dict(elem, finds.get('season_episode', {}), c_type=item.c_type)
                    elem_json['season'], elem_json['episode'] = sxe.split('x')
                    elem_json['season'] = int(elem_json['season'] or 1)
                    elem_json['episode'] = int(elem_json['episode'] or 1)
                    elem_json['year'] = '-'

                elem_json['url'] = elem.a.get('href', '')
                elem_json['title'] = re.sub('(?i)\(*en emisi.n\)*', '', elem.img.get('alt', '')).strip() if item.c_type != 'episodios' \
                                                             else elem.img.get('alt', '').replace(sxe, '').strip()
                elem_json['quality'] = '*%s' % self.parse_finds_dict(elem, finds.get('get_quality', {}), c_type=item.c_type)
                elem_json['thumbnail'] = elem.img.get('data-src', '') or elem.img.get('src', '')
                if ('tmdb' in elem_json['thumbnail'] or 'imdb' in elem_json['thumbnail']) and '=http' in elem_json['thumbnail']:
                    elem_json['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem_json['thumbnail']), '=(.*?)(?:&|$)')
                if '/http' in elem_json['thumbnail']:
                    elem_json['thumbnail'] = scrapertools.find_single_match(self.do_unquote(elem_json['thumbnail']), '\/(http.*?)(?:&|$)')
                elem_json['year'] = self.parse_finds_dict(elem, finds.get('year', {}), year=True, c_type=item.c_type).split('|')
                elem_json['year'] = elem_json['year'][1] if (len(elem_json['year']) >= 3 and len(elem_json['year'][1]) == 4) \
                                    else elem_json['year'][0] if (len(elem_json['year']) >= 2 and len(elem_json['year'][0]) == 4) \
                                    else elem_json['year'][1] if (len(elem_json['year']) >= 2 and len(elem_json['year'][1]) == 4) \
                                    else elem_json['year'][0] if (len(elem_json['year']) >= 1 and len(elem_json['year'][0]) == 4) \
                                    else '-'
                if self.parse_finds_dict(elem, finds.get('plot', {}), c_type=item.c_type):
                    elem_json['plot'] = self.parse_finds_dict(elem, finds.get('plot', {}), c_type=item.c_type)

                if not elem_json['url']: continue
                    
                if finds['controls']['get_lang']: 
                    self.get_language_and_set_filter(elem, elem_json)

                matches.append(elem_json.copy())

        return matches

    def episodesxseason_matches(self, item, matches_int, **AHkwargs):
        logger.info()

        matches = []
        finds = self.finds
        if DEBUG: logger.debug('MATCHES_int %s' % (str(matches_int)))

        for x, elem in enumerate(matches_int):
            elem_json = {}

            try:
                seasonxepi = self.parse_finds_dict(elem, finds.get('episode_num', {}), c_type='episodios')
                if seasonxepi: season, elem_json["episode"] = seasonxepi.split(" - ")
                season = int(season)
                elem_json["episode"] = int(elem_json["episode"])
            except Exception:
                logger.error('ERROR en seasonxepi: %s' % elem)
                logger.error(traceback.format_exc())
                continue

            if item.contentSeason != season: continue

            elem_json['url'] = elem.a.get("href", '')
            try:
                elem_json['title'] = elem.find("div", class_="episodiotitle").get_text('|', strip=True).split('|')[0]
            except Exception:
                logger.error(traceback.format_exc())

            elem_json['season'] = item.contentSeason
            elem_json['thumbnail'] = elem.img.get('src', '')

            if not elem_json.get('url', ''): 
                continue

            matches.append(elem_json.copy())

        return matches

    def findvideos_matches(self, item, matches_int, langs, response, **AHkwargs):
        logger.info()

        matches = []
        finds = self.finds
        self.doo_url = "%swp-admin/admin-ajax.php" % self.host

        for elem in matches_int:
            elem_json = {}

            post = {"action": "doo_player_ajax",
                    "post": elem.get("data-post", ""),
                    "nume": elem.get("data-nume", ""),
                    "type": elem.get("data-type", "")
                   }

            if DEBUG: logger.debug('MATCHES_int %s; POST: %s' % (str(elem), str(post)))
            soup = self.create_soup(self.doo_url, timeout=self.finds.get('timeout', self.timeout), post=post)
            response = self.response

            if response.json:
                if DEBUG: logger.debug('MATCHES_JSON %s' % (str(response.json)))
                elem_json['url'] = response.json.get("embed_url", "")
                if 'base64,' in elem_json['url']: 
                    #elem_json['url'] = base64.b64decode(scrapertools.find_single_match(elem_json['url'], 'base64,([^"]+)"')).decode('utf-8')
                    continue
                elem_json['quality'] = '*'
                elem_json['title'] = '%s'

                if not elem_json['url'] or "youtube" in elem_json['url'] or "waaw" in elem_json['url'] \
                                        or "jetload" in elem_json['url']:
                    continue

                if finds['controls']['get_lang']: 
                    self.get_language_and_set_filter(elem, elem_json)
                    elem_json['language'] = '*%s' % elem_json['language']
                if not elem_json.get('language', '') and item.language:
                    elem_json['language'] = item.language

                matches.append(elem_json.copy())

        return matches, langs
