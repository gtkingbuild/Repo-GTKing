# -*- coding: utf-8 -*-
# -*- Alfa Channel Helper -*-
# -*- Herramientas genericas para canales BS -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse
    import urllib.parse as urllib
else:
    import urlparse
    import urllib

import re
import traceback
import time
import base64
import xbmcgui
window = xbmcgui.Window(10000) or None

from core import httptools
from core import scrapertools
from core.scrapertools import episode_title
from core import tmdb
from core import jsontools
from core.item import Item
from platformcode import config
from platformcode import logger
from channels import filtertools

DEBUG = False
BTDIGG = 'btdig'
BTDIGG_URL = config.BTDIGG_URL
BTDIGG_LABEL = config.BTDIGG_LABEL
IDIOMAS = {'mx': 'Latino', 'dk': 'Latino', 'es': 'Castellano', 'en': 'VOSE', 'gb': 'VOSE', 
           'sub': 'VOSE', 'su': 'VOSE', 'eng': 'VOSE', "subtitulado": "VOSE", "usa": "VOSE", 
           'de': 'VOSE', "español": "Castellano", "espana": "Castellano", 'cas': 'Castellano', 
           "mexico": "Latino", "latino": "Latino", 'lat': 'Latino', 'LAT': 'Latino', 'jp': 'VOSE',
           'spain': 'Castellano'}


class AlfaChannelHelper:

    def __init__(self, host, timeout=15, channel='', movie_path="/movies", tv_path="/serie", 
                 movie_action="findvideos", tv_action="seasons", forced_proxy_opt='', 
                 list_language=[], list_quality=[], list_quality_movies=[], list_quality_tvshow=[], 
                 list_servers=[], language=[], idiomas={}, IDIOMAS_TMDB={0: 'es', 1: 'en', 2: 'es,en'}, 
                 actualizar_titulos=True, canonical={}, finds={}, debug=False, url_replace=[]):
        global DEBUG
        DEBUG = debug
        
        self.url = ''
        self.host = host
        self.host_torrent = finds.get('controls', {}).get('host_torrent', self.host)
        self.timeout = timeout
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        self.channel = channel or canonical.get('channel', '')
        self.movie_path = movie_path
        self.tv_path = tv_path
        self.movie_action = movie_action
        self.tv_action = tv_action
        self.forced_proxy_opt = forced_proxy_opt
        self.list_language = list_language
        self.list_quality = self.list_quality_tvshow = list_quality or list_quality_tvshow
        self.list_quality_movies = list_quality_movies
        self.list_servers = list_servers
        self.language = language
        self.idiomas = idiomas or IDIOMAS
        self.IDIOMAS_TMDB = IDIOMAS_TMDB
        self.actualizar_titulos = actualizar_titulos
        self.canonical = canonical
        self.finds = finds
        self.url_replace = url_replace
        self.Window_IsMedia = True
        self.season_colapse = True
        self.unescape = False
        self.btdigg = False
        self.btdigg_search = False
        self.last_page = ''
        self.itemlist = []

        self.response = httptools.build_response(HTTPResponse=True)
        self.response_proxy = self.response.proxy__
        self.response_preferred_proxy_ip = ''
        self.alfa_domain_web_list = jsontools.load(window.getProperty("alfa_domain_web_list")) \
                                                   if window.getProperty("alfa_domain_web_list") else {}
        self.headers = {}
        
        self.SUCCESS_CODES = httptools.SUCCESS_CODES
        self.REDIRECTION_CODES = httptools.REDIRECTION_CODES
        self.PROXY_CODES = httptools.PROXY_CODES
        self.NOT_FOUND_CODES = httptools.NOT_FOUND_CODES
        self.CLOUDFLARE_CODES = httptools.CLOUDFLARE_CODES
        self.OPENSSL_VERSION = httptools.OPENSSL_VERSION
        self.ssl_version = httptools.ssl_version
        self.ssl_context = httptools.ssl_context
        self.patron_local_torrent = '(?i)(?:(?:\\\|\/)[^\[]+\[\w+\](?:\\\|\/)[^\[]+\[\w+\]_\d+\.torrent|magnet\:)'
        try:
            self.ASSISTANT_VERSION = config.get_setting('assistant_version', default='').split('.')
            self.ASSISTANT_VERSION = tuple((int(self.ASSISTANT_VERSION[0]), int(self.ASSISTANT_VERSION[1]), int(self.ASSISTANT_VERSION[2])))
        except:
            self.ASSISTANT_VERSION = tuple()

    def create_soup(self, url, **kwargs):
        """
        :param url: url destino
        :param kwargs: parametros que se usan en donwloadpage
        :return: objeto soup o response sino soup
        """
        from lib.generictools import js2py_conversion, check_blocked_IP

        if "soup" not in kwargs: kwargs["soup"] = True
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
        response = httptools.downloadpage(url, **kwargs)

        if response.code in httptools.SUCCESS_CODES \
                         and ('text/' in response.headers.get('Content-Type', '') \
                         or 'json' in response.headers.get('Content-Type', '') \
                         or 'xml' in response.headers.get('Content-Type', '') \
                         or 'javascript' in response.headers.get('Content-Type', '')):
                response = js2py_conversion(response.data, url, resp=response, size=size_js, **kwargs)
        
        if kwargs.get("soup", True):
            soup = response.soup or {}
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
                        if response.code in httptools.SUCCESS_CODES + httptools.REDIRECTION_CODES else ''
            if 'preferred_proxy_ip' in kwargs:
                kwargs['preferred_proxy_ip'] = self.response_preferred_proxy_ip
            if 'preferred_proxy_ip' in kwargs.get('canonical', {}):
                kwargs['canonical']['preferred_proxy_ip'] = self.canonical['preferred_proxy_ip'] = self.response_preferred_proxy_ip
            if window: window.setProperty("AH_%s_preferred_proxy_ip" % self.channel, str(self.response_preferred_proxy_ip))

        if kwargs.get('check_blocked_IP', False) or kwargs.get('canonical', {}).get('check_blocked_IP', False):
            res, self.itemlist = check_blocked_IP(response.data, self.itemlist or kwargs.get('itemlist', []), 
                                                  url, canonical=self.canonical, verbose=True)

        self.ssl_version = httptools.ssl_version
        self.ssl_context = httptools.ssl_context

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
            new_item.contentSerieName = re.sub('\s*\d+x\d+\s*(?:\s*-\s*)?', '', new_item.title)
            new_item.action = self.movie_action
        elif contentType != 'tvshow' and ((self.movie_path in new_item.url and not self.tv_path in new_item.url) \
                                     or new_item.contentType == 'movie'):
            new_item.action = self.movie_action
            new_item.contentTitle = new_item.title.strip()
            if not new_item.contentType: new_item.contentType = 'movie'
            if not new_item.infoLabels.get("year", ''): new_item.infoLabels["year"] = '-'
        else:
            new_item.action = self.tv_action
            new_item.contentSerieName = new_item.title.strip()
            new_item.contentType = 'tvshow'

        return new_item

    def add_video_to_videolibrary(self, item, itemlist, contentType='tvshow'):

        if item.add_videolibrary or item.library_playcounts or item.downloadFilename:
            return itemlist

        actionType = 'pelicula' if contentType == 'movie' else 'season' if contentType == 'season' else 'serie'
        contentTitle = 'pelicula' if contentType == 'movie' else 'temporada' if contentType == 'season' else 'serie'
        infoLabels = item.infoLabels
        infoLabels['playcount'] = 0

        if self.Window_IsMedia:
            if len(itemlist) > 0:
                if item.action == 'findvideos':
                    itemlist.append(item.clone(channel="trailertools", title="**-[COLOR magenta] Buscar Trailer [/COLOR]-**", 
                                               action="buscartrailer", context="", infoLabels=infoLabels))
            
            if config.get_videolibrary_support() and len(itemlist) > 0 and item.contentChannel != "videolibrary" \
                            and ((item.contentType == 'episode' and item.url_tvshow) or item.action != 'findvideos' \
                            or (item.contentType == 'movie' and item.action == 'findvideos')):
                item.url = self.do_url_replace(item.url)
                
                if self.actualizar_titulos:
                    from lib.generictools import get_color_from_settings
                    itemlist.append(item.clone(title="** [COLOR %s]Actualizar Títulos - vista previa videoteca[/COLOR] **" \
                                                      % get_color_from_settings('library_color', default='yellow'), 
                                               action="actualizar_titulos",
                                               infoLabels = infoLabels, 
                                               tmdb_stat=False, 
                                               from_action=item.action, 
                                               contentType=contentType,
                                               from_title_tmdb=item.title, 
                                               from_update=True, 
                                               thumbnail=item.infoLabels['temporada_poster'] or item.infoLabels['thumbnail']
                                              )
                                   )

                itemlist.append(item.clone(title='[COLOR yellow]Añadir esta %s a la videoteca[/COLOR]' % contentTitle, 
                                           url=item.url_tvshow or item.url,
                                           action="add_%s_to_library" % actionType,
                                           extra="episodios",
                                           infoLabels = infoLabels, 
                                           contentType=contentType, 
                                           contentSerieName=item.contentSerieName
                                          )
                               )
        return itemlist

    def do_url_replace(self, url, url_replace=[]):

        if url and (url_replace or self.url_replace):

            for url_from, url_to in (url_replace or self.url_replace):
                url = re.sub(url_from, url_to, url)

        url = url.replace(' ', '%20')
        return url

    def do_quote(self, url, plus=True):

        if plus:
            return urlparse.quote_plus(url)
        else:
            return urlparse.quote(url)

    def do_unquote(self, url):
        
        return urlparse.unquote(url)

    def do_urlencode(self, post):
        
        return urllib.urlencode(post)

    def urljoin(self, domain, url):
        
        return urlparse.urljoin(domain, url)

    def obtain_domain(self, url, sub=False, point=False, scheme=False):

        return httptools.obtain_domain(url, sub=sub, point=point, scheme=scheme)

    def channel_proxy_list(self, url, forced_proxy=None):

        return httptools.channel_proxy_list(url, forced_proxy=forced_proxy)

    def get_cookie(self, url, name, follow_redirects=False):

        return httptools.get_cookie(url, name, follow_redirects=False)

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
        return AH_find_seasons(item, matches, **AHkwargs)

    def convert_url_base64(self, url, host='', referer=None, rep_blanks=True, force_host=False):

        from lib.generictools import convert_url_base64
        return convert_url_base64(url, host, referer, rep_blanks, force_host)

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
        except:
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

        if isinstance(elem_in, dict):
            elem = elem_in
            c_type = item.c_type or item.contentType
        else:
            elem = {}
            elem['quality'] = elem_in.quality
            elem['title'] = elem_in.title
            elem['url'] = elem_in.url
            elem['language'] = elem_in.language
            c_type = elem_in.contentType

        quality = elem.get('quality', '').replace('*', '').replace('[]', '')

        if c_type in ['series', 'documentales', 'tvshow', 'season', 'episode'] or self.tv_path in elem.get('url', ''):
            if '720p' in elem['title'] or '720p' in elem['url'] or '720p' in elem.get('quality', ''):
                quality = 'HDTV-720p'
            elif '1080p' in elem['title'] or '1080p' in elem['url'] or '1080p' in elem.get('quality', ''):
                quality = 'WEB-DL 1080p'
            elif '4k' in elem['title'].lower() or '4k' in elem['url'] or '4k' in elem.get('quality', '').lower():
                quality = '4KWebRip'
            else:
                quality = 'HDTV'
        else:
            if not quality and ('hd' in item.url.lower() or '4k' in item.url.lower() or '3d' in item.url.lower() \
                        or 'hd' in elem['url'].lower() or '4k' in elem['url'].lower() or '3d' in elem['url'].lower()):
                quality = 'HD'
            elif not quality and ('avi' in elem['title'].lower() or 'avi' in elem['url'].lower() or 'avi' in elem.get('quality', '').lower()):
                quality = 'BlueRayRip'
            if '720' not in quality and ('720' in elem['title'] or '720' in elem['url'] or '720' in elem.get('quality', '')):
                quality += '720p' if not quality else ', 720p'
            if '1080' not in quality and ('1080' in elem['title'] or '1080' in elem['url'] or '1080' in elem.get('quality', '')):
                quality += '1080p' if not quality else ', 1080p'

        if (('4k' in item.url.lower() and not item.url.startswith('magnet')) or ('4k' in elem['url'].lower() \
                                      and not elem['url'].startswith('magnet'))) and not '4k' in quality.lower():
            quality += ', 4K'
        if (('3d' in item.url.lower() and not item.url.startswith('magnet')) or ('3d' in elem['url'].lower() \
                                      and not elem['url'].startswith('magnet'))) and not '3d' in quality.lower():
            quality += ', 3D'

        if 'dual' in quality.lower(): quality = re.sub('(?i)\s*dual', '', quality)
        if 'digg' in elem.get('quality', '').lower(): quality += BTDIGG_LABEL
        if quality == '720': quality = '720p'
        if quality == '1080': quality = '1080p'

        if DEBUG: logger.debug('find_QUALITY: %s' % quality)
        return quality

    def find_language(self, elem_in, item):

        language = []
        
        if isinstance(elem_in, dict):
            elem = elem_in
            c_type = item.c_type or item.contentType
        else:
            elem = {}
            elem['quality'] = elem_in.quality
            elem['title'] = elem_in.title
            elem['url'] = elem_in.url
            elem['language'] = elem_in.language
            c_type = elem_in.contentType
        
        if isinstance(elem.get('language'), str): elem['language'] = [elem['language'].replace('*', '')]
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
                        or 'vos' in elem.get('url', '').lower() or 'vos' in elem.get('title', '').lower() \
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
        
        if isinstance(size, str): size = size.replace('[COLOR magenta][B]RAR-[/B][/COLOR]', '')
        s = 0
        if not size or size == 0 or size == '0':
            return s

        try:
            size_name = {"M·B": 1, "G·B": 1024, "MB": 1, "GB": 1024}
            if ' ' in size:
                size_list = size.split(' ')
                size = float(size_list[0])
                size_factor = size_name.get(size_list[1], 1)
                s = size * size_factor
        except:
            pass

        if DEBUG: logger.debug('SIZE: %s / %s' % (size, s))
        return s

    def manage_torrents(self, item, elem, lang, soup={}, finds={}, **kwargs):

        from lib.generictools import get_torrent_size
        from core import filetools
        if DEBUG: logger.debug('ELEM_IN: %s' % elem)

        finds_controls = finds.get('controls', {})

        self.host_torrent = finds_controls.get('host_torrent', '') or self.host
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
                elem['url'] = self.convert_url_base64(elem['url'], self.host_torrent, referer=host_torrent_referer)
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
                    elem['torrent_alt'] = self.convert_url_base64(elem['torrent_alt'], self.host_torrent, referer=host_torrent_referer)
            except:
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
        if size:
            elem['size'] = size
            size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                       .replace('Mb', 'M·b').replace('.', ',')
            elem['torrent_info'] = '%s, ' % size                                # Agregamos size
        elem['torrent_info'] =  elem.get('torrent_info', '')
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

        matches = matches_init = [] if not year and not next_page else '-' if year else ''
        if not finds or not soup: 
            return matches

        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/

        match = soup
        json = {}
        level_ = ''
        block = ''
        f = ''
        tagOR_save = {}

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
                    argument = ''
                    strip = ''
                    json = {}
                    if isinstance(f, dict):
                        attrs = f.copy()
                        tagOR = match if attrs.get('tagOR', '') else False
                        tag = attrs.pop('tagOR', '') or attrs.pop('tag', '')
                        string = attrs.pop('string', '')
                        regex = attrs.pop('@TEXT', '')
                        regex_sub = attrs.pop('@SUB', '')
                        argument = attrs.pop('@ARG', '')
                        strip = attrs.pop('@STRIP', True)
                        json = attrs.pop('@JSON', {})
                        pos = attrs.pop('@POS', [])
                        if pos: pos = pos[0]
                    else:
                        tag = f
                    if (isinstance(tag, str) and tag == '*') or (isinstance(tag, list) and len(tag) == 1 and tag[0] == '*'): 
                        tag = None

                    if DEBUG: logger.debug('find: %s=%s: %s=%s, %s, %s, %s, %s, [%s]' % (level, [key for key in f if key in ['tagOR', 'tag']], 
                                            tag, attrs, string, regex, argument, str(strip), pos))
                    if '_all' not in level or ('_all' in level and x < len(finds[level])-1) or ('_all' in level and pos):

                        if '_all' in level and pos:
                            match = soup_func_all(tag, attrs=attrs, string=string)[pos]
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
                        elif regex or regex_sub:
                            if pos:
                                if argument:
                                    match = match.get(argument)
                                else:
                                    match = match.text
                            if not pos or not match:
                                if argument:
                                    match = soup_func(tag, attrs=attrs, string=string).get(argument)
                                else:
                                    match = soup_func(tag, attrs=attrs, string=string).text
                            if regex:
                                if not isinstance(regex, list): regex = [regex]
                                for reg in regex:
                                    match = scrapertools.find_single_match(str(match), reg)
                            if regex_sub:
                                for reg_org, reg_des in regex_sub:
                                    match = re.sub(reg_org, reg_des, str(match))
                        elif argument:
                            if pos:
                                match = match.get(argument)
                            else:
                                match = soup_func(tag, attrs=attrs, string=string).get(argument)
                        else:
                            if not pos:
                                match = soup_func(tag, attrs=attrs, string=string)
                    
                    else:
                        match = soup_func_all(tag, attrs=attrs, string=string)
                    if DEBUG and x < len(finds)-1: logger.debug('Matches[500] (%s/%s): %s' % (len(match) if isinstance(match, list) else 1, 
                                                                                              len(str(match)), str(match)[:500]))

                    if not match:
                        if tagOR:
                            match = tagOR
                            continue
                        if tagOR_save:
                            match = tagOR_save
                            tagOR_save = {}
                            break
                        break
                    if match:
                        if tagOR:
                            if y < len(f)-1:
                                tagOR_save = match
                                continue
                            break
                        continue
                if not match: break

            if json:
                try:
                    if DEBUG: logger.debug('Json[500] (%s/%s): %s' % (len(match) if isinstance(match, list) else 1, 
                                                                      len(str(match)), str(match)[:500]))
                    json_all_work = {}
                    json_all = jsontools.load(match)
                    if json_all:
                        match = []
                        if 'DEFAULT' in str(json):
                            json = {}
                            match = json_all
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
                except:
                    match = []
                    logger.error('Json[500] (%s/%s): %s' % (len(json_all_work.keys()), 
                                                            len(str(json_all_work)), str(json_all_work)[:500]))
                    logger.error(traceback.format_exc())
            
            if DEBUG: logger.debug('Matches[500] (%s/%s): %s' % (len(match) if isinstance(match, list) else 1, 
                                                                 len(str(match)), str(match)[:500]))
            
            matches = matches_init if not match else match
        except:
            logger.error('LEVEL: %s, BLOCK; %s, FUNC: %s, MATCHES-TYPE: %s, MATCHES[500]: %s' \
                         % (level, block, f, str(type(match)), str(match)[:500]))
            matches = matches_init
            logger.error(traceback.format_exc())

        return matches


class CustomChannel(AlfaChannelHelper):
    pass


class DictionaryAllChannel(AlfaChannelHelper):

    def list_all(self, item, data='', matches_post=None, postprocess=None, generictools=False, finds={}, **kwargs):
        logger.info()

        itemlist = list()
        matches = []
        matches_post_json_force = kwargs.pop('matches_post_json_force', False)
        if not matches_post and item.matches_post: matches_post = item.matches_post

        if not finds: finds = self.finds
        if DEBUG: logger.debug('FINDS: %s' % finds)
        finds_out = finds.get('find', {})
        finds_next_page = finds.get('next_page', {})
        finds_next_page_rgx = finds.get('next_page_rgx') if finds.get('next_page_rgx') else [['page\/\d+\/', 'page/%s/']]
        finds_last_page = finds.get('last_page', {})
        finds_year = finds.get('year', {})
        finds_season_episode = finds.get('season_episode', {})

        AHkwargs = {'soup': item.matches or {}, 'finds': finds, 'function': 'list_all', 'function_alt': kwargs.get('function', '')}
        AHkwargs['matches_post_list_all'] = matches_post or kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)

        # Sistema de paginado para evitar páginas vacías o semi-vacías en casos de búsquedas con series con muchos episodios
        finds_controls = finds.get('controls', {})

        title_lista = []                                        # Guarda la lista de series que ya están en Itemlist, para no duplicar lineas
        if item.title_lista:                                    # Si viene de una pasada anterior, la lista ya estará guardada
            title_lista.extend(item.title_lista)                                # Se usa la lista de páginas anteriores en Item
            del item.title_lista                                                # ... limpiamos

        curr_page = 1                                                           # Página inicial
        last_page = 99999 if not isinstance(finds_last_page, bool) else 0       # Última página inicial
        last_page_print = 1                                                     # Última página inicial, para píe de página
        page_factor = finds_controls.get('page_factor', 1.0 )                   # Factor de conversión de pag. web a pag. Alfa
        cnt_tot = finds_controls.get('cnt_tot', 20)                             # Poner el num. máximo de items por página
        cnt_tot_ovf = finds_controls.get('page_factor_overflow', 1.3)           # Overflow al num. máximo de items por página
        cnt_match = 0                                                           # Contador de matches procesadas
        cnt_title = 0                                                           # Contador de líneas insertadas en Itemlist
        cnt_tot_match = 0.0                                                     # Contador TOTAL de líneas procesadas de matches
        custom_pagination =  finds_controls.get('custom_pagination', False)     # Paginación controlada por el usuario
        if item.cnt_tot_match:
            cnt_tot_match = float(item.cnt_tot_match)                           # restauramos el contador TOTAL de líneas procesadas de matches
            del item.cnt_tot_match
        if item.curr_page:
            curr_page = int(item.curr_page)                                     # Si viene de una pasada anterior, lo usamos
            del item.curr_page                                                  # ... y lo borramos
        if item.last_page:
            last_page = int(item.last_page)                                     # Si viene de una pasada anterior, lo usamos
            del item.last_page                                                  # ... y lo borramos
        if item.page_factor:
            page_factor = float(item.page_factor)                               # Si viene de una pasada anterior, lo usamos
            del item.page_factor                                                # ... y lo borramos
        if item.last_page_print:
            last_page_print = item.last_page_print                              # Si viene de una pasada anterior, lo usamos
            del item.last_page_print                                            # ... y lo borramos

        inicio = time.time()                                                    # Controlaremos que el proceso no exceda de un tiempo razonable
        fin = inicio + finds_controls.get('inicio', 5)                          # Después de este tiempo pintamos (segundos)
        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)     # Timeout normal
        timeout_search = timeout * 2                                            # Timeout para búsquedas

        if item.extra == 'find_seasons':                                        # Si es un búsqueda de temporadas, se amplían los límites
            cnt_tot = 99
            fin = inicio + 30

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
        if self.btdigg: cnt_tot = finds_controls.get('cnt_tot', 20)

        next_page_url = item.url
        episodios = False
        # Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
        while (cnt_title < cnt_tot and (curr_page <= last_page or (last_page == 0 and finds_next_page and next_page_url)) \
                                   and fin > time.time()) or item.matches:
            
            # Descarga la página
            soup = data
            data = ''
            cnt_match = 0                                                       # Contador de líneas procesadas de matches
            if not item.matches:                                                # si no viene de una pasada anterior, descargamos
                kwargs.update({'timeout': timeout_search, 'post': post, 'headers': headers, 'forced_proxy_opt': forced_proxy_opt})
                soup = soup or self.create_soup(next_page_url, **kwargs)

                itemlist = self.itemlist + itemlist
                self.itemlist = []

                if self.url:
                    if DEBUG: logger.debug('self.URL: %s / %s' % (next_page_url, self.url))
                    next_page_url = item.url = self.url
                    self.url = ''
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        item.url = re.sub(rgx_org, rgx_des % str(curr_page), item.url.rstrip('/')).replace('//?', '/?')
                if soup:
                    AHkwargs['soup'] = self.response.soup or self.response.json or self.response.data
                    curr_page += 1
                    matches = self.parse_finds_dict(soup, finds_out) if finds_out \
                              else self.response.soup or self.response.json or self.response.data
                    if not isinstance(matches, (list, dict)):
                        matches = []
                    if matches_post and matches:
                        matches = matches_post(item, matches, **AHkwargs)
                        if custom_pagination:
                            if len(matches) < cnt_tot:
                                custom_pagination = False

                    if ((self.btdigg and item.extra == 'novedades') or (self.btdigg_search \
                                     and item.c_type == 'search' and item.extra != 'find_seasons')) \
                                     and not item.btdig_in_use:
                        matches = self.find_btdigg_list_all(item, matches, finds_controls.get('channel_alt', ''), **AHkwargs)

                    if not matches and item.extra != 'continue':
                        logger.error('NO MATCHES: %s' % finds_out)
                        if AHkwargs.get('function_alt', '') != 'find_seasons' and item.c_type not in ['search']:
                            logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or section_list)
                        if AHkwargs.get('function_alt', '') == 'find_seasons' or item.c_type in ['search']:
                            last_page = 0
                        break

            else:
                matches =  AHkwargs['soup'] = item.matches
                del item.matches
                if matches_post_json_force and matches_post and matches: 
                    matches = matches_post(item, matches, **AHkwargs)
                    if custom_pagination:
                        if len(matches) < cnt_tot:
                            custom_pagination = False

            AHkwargs['matches'] = matches
            if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))

            # Refrescamos variables posiblemente actualizadas en "matches_post"
            self.finds = finds
            finds_controls = finds.get('controls', {})
            host = finds_controls.get('host', self.host)
            self.doo_url = "%swp-admin/admin-ajax.php" % host
            host_referer = finds_controls.get('host_referer', host)
            url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
            url_base64 = finds_controls.get('url_base64', True)
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
                    next_page_url = self.parse_finds_dict(soup, finds_next_page, next_page=True, c_type=item.c_type).lstrip('#')
                    if next_page_url: next_page_url = self.urljoin(self.host, next_page_url)
                elif last_page > 0:
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
                        item.url = url[0].rstrip('/') + finds_next_page_rgx[0][1] % str(curr_page)
                        if '?' in item.url and len(url) > 1: url[1] = url[1].replace('?', '&')
                        if len(url) > 1: item.url = '%s?%s' % (item.url, url[1].lstrip('/'))
                    next_page_url = item.url
                    for rgx_org, rgx_des in finds_next_page_rgx:
                        if url_page_control == 'url':
                            next_page_url = re.sub(rgx_org, rgx_des % str(curr_page), next_page_url.rstrip('/')).replace('//?', '/?')
                        else:
                            post = re.sub(rgx_org, rgx_des % str(curr_page), post.rstrip('/')).replace('//?', '/?')

            if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                    % (str(curr_page), str(last_page), str(page_factor), str(next_page_url), len(matches)))

            # Buscamos la última página
            if last_page == 99999:                                              # Si es el valor inicial, buscamos
                try:
                    last_page = self.last_page or int(self.parse_finds_dict(soup, finds_last_page, next_page=True, c_type=item.c_type).lstrip('#'))
                    if finds_controls.get('force_find_last_page') and isinstance(finds_controls['force_find_last_page'], list) \
                                           and isinstance(finds_controls['force_find_last_page'][0], int) \
                                           and isinstance(finds_controls['force_find_last_page'][1], int):
                        if last_page >= finds_controls['force_find_last_page'][0]:
                            url = next_page_url
                            for rgx_org, rgx_des in finds_next_page_rgx:
                                url = re.sub(rgx_org, rgx_des % str(finds_controls['force_find_last_page'][1]), 
                                             url.rstrip('/')).replace('//?', '/?')
                            soup_last_page = self.create_soup(url, hide_infobox=True, **kwargs)
                            last_page = int(self.parse_finds_dict(soup_last_page, finds_last_page, next_page=True, 
                                                                  c_type=item.c_type).lstrip('#'))
                    page_factor = float(len(matches)) / float(cnt_tot)
                except:
                    last_page = 0
                    last_page_print = int((float(len(matches)) / float(cnt_tot)) + 0.999999)
                self.last_page = last_page

                if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                        % (str(curr_page), str(last_page), str(page_factor), str(next_page_url), len(matches)))

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
                if isinstance(finds_controls.get('duplicates', False), list) and (self.tv_path in new_item.url \
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

                if elem.get('title_subs', []): new_item.title_subs =  elem['title_subs']

                if elem.get('plot', ''): new_item.contentPlot =  elem['plot']

                if elem.get('info', ''): new_item.info =  elem['info']

                if elem.get('btdig_in_use', ''): new_item.btdig_in_use =  elem['btdig_in_use']
                    
                if elem.get('imdb_id', ''): new_item.infoLabels['imdb_id'] =  elem['imdb_id']
                if elem.get('tmdb_id', ''): new_item.infoLabels['tmdb_id'] =  elem['tmdb_id']
                if elem.get('tvdb_id', ''): new_item.infoLabels['tvdb_id'] =  elem['tvdb_id']
                    
                new_item.season_search = '*%s' % elem.get('season_search', '')

                try:
                    new_item.infoLabels['year'] = int(elem['year'])
                except:
                    new_item.infoLabels['year'] = '-'

                if item.c_type == 'episodios' or elem.get('mediatype', '') == 'episode':
                    new_item.contentType = 'episode'
                    new_item.contentSeason = int(elem.get('season', '1') or '1')
                    new_item.contentEpisodeNumber = int(elem.get('episode', '1') or '1')
                    new_item.title = '%sx%s - %s' % (new_item.contentSeason, new_item.contentEpisodeNumber, new_item.title)
                    episodios = True

                if elem.get('mediatype', ''): new_item.contentType = elem['mediatype']
                elif item.c_type == 'peliculas': new_item.contentType = 'movie'
                new_item = self.define_content_type(new_item, contentType=new_item.contentType)

                new_item.context = "['buscar_trailer']"
                new_item.context = filtertools.context(new_item, self.list_language, self.list_quality_movies \
                                                       if new_item.contentType == 'movie' else self.list_quality_tvshow)

                if elem.get('post', None): new_item.post = elem['post']
                if elem.get('headers', None): new_item.headers = elem['headers']
                
                new_item.url = self.do_url_replace(new_item.url, url_replace)

                if postprocess:
                    new_item = postprocess(elem, new_item, item, **AHkwargs)

                if new_item:
                    cnt_title += 1

                    #Ahora se filtra por idioma, si procede, y se pinta lo que vale
                    if filter_languages > 0 and self.list_language:             # Si hay idioma seleccionado, se filtra
                        itemlist = filtertools.get_link(itemlist, new_item, self.list_language)
                    else:
                        itemlist.append(new_item.clone())                       # Si no, se añade a la lista

                    cnt_title = len(itemlist)                                   # Recalculamos los items después del filtrado
                    if cnt_title >= cnt_tot and (len(matches) - cnt_match) + cnt_title > cnt_tot * cnt_tot_ovf:     # Contador de líneas añadidas
                        break
                    
                    #if DEBUG: logger.debug('New_item: %s' % new_item)

            matches = matches[cnt_match:]                                       # Salvamos la entradas no procesadas
            cnt_tot_match += cnt_match                                          # Calcular el num. total de items mostrados

        if DEBUG: logger.debug('curr_page: %s / last_page: %s / page_factor: %s / next_page_url: %s / matches: %s' \
                                % (str(curr_page), str(last_page), str(page_factor), str(next_page_url), len(matches)))

        if itemlist:
            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico and not httptools.TEST_ON_AIR
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
                    new_item.season_search = new_item.season_search[1:]
                if not isinstance(new_item.infoLabels['year'], int):
                    new_item.infoLabels['year'] = str(new_item.infoLabels['year']).replace('-', '')

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
        if ((((curr_page <= last_page and last_page < 99999) or (last_page == 0 and len(matches) > 0) \
                                    or len(matches) > 0 or (cnt_match >= cnt_tot and next_page_url and not self.btdigg)) \
                                    and next_page_url) or custom_pagination) \
                                    and AHkwargs['function'] != 'find_seasons':

            curr_page_print = int(cnt_tot_match / float(cnt_tot))
            if curr_page_print < 1:
                curr_page_print = 1
            if last_page:
                if last_page > 1:
                    last_page_print = int((last_page * page_factor) + 0.999999)
                title = '%s de %s' % (curr_page_print, last_page_print)
            else:
                title = '%s' % curr_page_print
            title = ">> Página siguiente %s" % title
            if item.infoLabels.get('mediatype'): del item.infoLabels['mediatype']

            itemlist.append(item.clone(action="list_all", title=title, 
                                       title_lista=title_lista, post=post, matches=matches, 
                                       url=next_page_url, last_page=str(last_page), curr_page=str(curr_page), 
                                       page_factor=str(page_factor), cnt_tot_match=str(cnt_tot_match), 
                                       last_page_print=last_page_print))

        return itemlist

    def section(self, item, data= '', action="list_all", matches_post=None, postprocess=None, 
                section_list={}, finds={}, **kwargs):
        logger.info()

        if not finds: finds = self.finds
        finds_out = finds.get('categories', {})
        itemlist = list()
        matches = list()
        soup = {}
        if not matches_post and item.matches_post: matches_post = item.matches_post
        AHkwargs = {'soup': soup, 'finds': finds, 'function': 'section'}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = matches_post or kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)
        
        finds_controls = finds.get('controls', {})
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
                              else self.response.soup or self.response.json or self.response.data
            if not isinstance(matches_section, (list, dict)):
                matches_section = []

            if matches_post and matches_section:
                matches = matches_post(item, matches_section, **AHkwargs)
            else:
                for elem in matches_section:
                    elem_json = {}
                    try:
                        elem_json['url'] = elem.a.get("href", '')
                        elem_json['title'] = elem.a.get_text(strip=True)
                    except:
                        elem_json['url'] = elem.get("href", '')
                        elem_json['title'] = elem.get_text(strip=True)
                    matches.append(elem_json.copy())

        if not matches:
            logger.error('NO MATCHES: %s' % finds_out)
            logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or section_list)
            return itemlist

        AHkwargs['matches'] = matches
        if DEBUG: logger.debug('MATCHES (%s/%s): %s' % (len(matches), len(str(matches)), str(matches)))
        
        # Refrescamos variables posiblemente actualizadas en "matches_post"
        self.finds = finds
        finds_controls = finds.get('controls', {})
        year = finds_controls.get('year', False)
        reverse = finds_controls.get('reverse', False)
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

            if 'post' in new_item: del new_item.post
            if elem.get('post', None): new_item.post = elem['post']
            if 'headers' in new_item: del new_item.headers
            if elem.get('headers', None): new_item.headers = elem['headers']
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

        if not finds: finds = self.finds
        finds_out = finds.get('seasons', {})
        finds_season_num = finds.get('season_num', {})
        finds_seasons_search = finds.get('controls', {}).get('seasons_search', False)
        find_seasons_search_num_rgx = finds.get('seasons_search_num_rgx', '')
        itemlist = list()
        matches = list()
        soup = {}
        if not matches_post and item.matches_post: matches_post = item.matches_post
        AHkwargs = {'soup': soup, 'finds': finds, 'function': 'seasons'}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = matches_post or kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)

        logger.info('Serie: %s; Seasons_search: %s' % (item.contentSerieName, finds_seasons_search))

        finds_controls = finds.get('controls', {})
        if DEBUG: logger.debug('FINDS_seasons: %s; FINDS_season_num: %s; FINDS_season_num: %s' \
                                % (finds_out, finds_season_num, finds_controls))

        item.title  = item.title.replace('(V)-' , '')
        item.contentTitle  = item.contentTitle.replace('(V)-' , '')
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
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
        modo_grafico = config.get_setting('modo_grafico', item.channel, default=True)
        idioma_busqueda = 0
        if not filter_languages: filter_languages = 0

        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

        item.context = filtertools.context(item, self.list_language, self.list_quality_tvshow)

        item.url = self.do_url_replace(item.url, url_replace)

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
                                      else self.response.soup or self.response.json or self.response.data
                    if not isinstance(matches_seasons, (list, dict)):
                        matches_seasons = []

                if matches_post and matches_seasons:
                    matches = matches_post(item, matches_seasons, **AHkwargs)
                else:
                    for elem in matches_seasons:
                        elem_json = {}

                        try:
                            elem_json['season'] = elem_json.get('season', '')

                            if not elem_json.get('season'):
                                if finds_season_num:
                                    elem_json['season'] = self.parse_finds_dict(elem, finds_season_num)
                                if find_seasons_search_num_rgx:
                                    elem_json['season'] = scrapertools.find_single_match(elem_json.get('season', '') \
                                                                                         or str(elem), find_seasons_search_num_rgx)
                                if elem_json.get('season'):
                                    elem_json['season'] = int(elem_json['season'])

                                if not elem_json.get('season'):
                                    try:
                                        elem_json['season'] = int(elem.span.get_text(strip=True).lower().replace('temporada', ''))
                                    except:
                                        try:
                                            elem_json['season'] = int(elem["value"])
                                        except:
                                            try:
                                                elem_json['season'] = int(re.sub('(?i)temp\w*\s*', '', elem.a.get_text(strip=True)))
                                            except:
                                                elem_json['season'] = 1
                            elem_json['url'] = item.url if not "href" in str(elem) \
                                               else elem.find('a').get("href", '') if elem.find('a') and "href" in str(elem.find('a')) \
                                               else elem.a.get("href", '') if elem.a and "href" in str(elem.a) \
                                               else elem.get("href", '') if "href" in str(elem) else item.url
                            if not elem_json['url']: elem_json['url'] = item.url
                            if 'javascript' in elem_json['url']: elem_json['url'] = self.doo_url if post else item.url
                            if elem_json['url'].startswith('#'):
                                elem_json['url'] = self.urljoin(item.url, elem_json['url'])
                            else:
                                elem_json['url'] = self.urljoin(self.host, elem_json['url'])
                        
                            matches.append(elem_json.copy())
                        except:
                            logger.error(elem)
                            logger.error(traceback.format_exc())

            if self.btdigg:
                if (len(matches) < 1 and item.infoLabels.get('number_of_seasons', 1) > 1) or (len(matches) >= 1 and matches[-1].get('season', 1) < item.infoLabels.get('number_of_seasons', 1)):
                    AHkwargs['btdigg_contentSeason'] = 1
                matches = self.find_btdigg_seasons(item, matches, finds_controls.get('domain_alt', ''), **AHkwargs)

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
        self.finds = finds
        finds_controls = finds.get('controls', {})
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
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
                logger.error('TEMPORAD ERRONEA: WEB: %s; TMDB: %s' % (elem['season'], item.infoLabels['number_of_seasons']))
                continue

            elem['url'] = elem.get('url', item.url)
            if url_base64: elem['url'] = self.convert_url_base64(elem['url'], self.host)

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
                                  title='Temporada %s' % elem['season'],
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

            if 'post' in new_item: del new_item.post
            if elem.get('post', None): new_item.post = elem['post']
            if 'headers' in new_item: del new_item.headers
            if elem.get('headers', None): new_item.headers = elem['headers']
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
            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico and not httptools.TEST_ON_AIR
            tmdb.set_infoLabels_itemlist(itemlist, modo_grafico, idioma_busqueda=idioma_busqueda)

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
                    itemlist.extend(getattr(channel, "episodesxseason")(tempitem))

        return itemlist

    def episodes(self, item, data='', action="findvideos", matches_post=None, postprocess=None, 
                 generictools=False, episodes_list={}, finds={}, **kwargs):
        logger.info('Serie: %s; Season: %s' % (item.contentSerieName, item.contentSeason))
        from lib.generictools import AH_post_tmdb_episodios, AH_find_videolab_status
        from channels import filtertools

        if not finds: finds = self.finds
        finds_out = finds.get('episodes', {})
        finds_episode_num = finds.get('episode_num', [])
        do_episode_clean = finds.get('episode_clean') if finds.get('episode_clean') else [['(?i)\s*\d+x\d+', '']]
        itemlist = list()
        matches = list()
        soup = {}
        if not matches_post and item.matches_post: matches_post = item.matches_post
        AHkwargs = {'soup': soup, 'finds': finds, 'function': 'episodes'}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = matches_post or kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = kwargs.pop('matches_post_get_video_options', None)

        finds_controls = finds.get('controls', {})
        if DEBUG: logger.debug('FINDS_episodes: %s; FINDS_controls: %s' % (finds_out, finds_controls))

        timeout = self.timeout = kwargs.pop('timeout', 0) or finds.get('timeout', self.timeout)
        post = item.post or kwargs.pop('post', None) or finds_controls.pop('post', None)
        headers = item.headers or kwargs.pop('headers', None) or finds_controls.get('headers', {})
        forced_proxy_opt = finds_controls.get('forced_proxy_opt', None) or kwargs.pop('forced_proxy_opt', None)
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
        min_temp = finds_controls.get('min_temp', False)
        join_dup_episodes = finds_controls.get('join_dup_episodes', True)

        modo_ultima_temp = AHkwargs['modo_ultima_temp'] = config.get_setting('seleccionar_ult_temporadda_activa', item.channel, default=True)
        self.season_colapse = config.get_setting('season_colapse', item.channel, default=True)
        if item.season_colapse == False: self.season_colapse = item.season_colapse
        filter_languages = config.get_setting('filter_languages', item.channel, default=0)
        modo_grafico = config.get_setting('modo_grafico', item.channel, default=True)
        idioma_busqueda = 0
        if not filter_languages: filter_languages = 0

        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)

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
                                   else self.response.soup or self.response.json or self.response.data
                if not isinstance(matches_episodes, (list, dict)):
                    matches_episodes = []

            if matches_post and matches_episodes:
                matches = matches_post(item, matches_episodes, **AHkwargs)

        if self.btdigg:
            matches = self.find_btdigg_episodes(item, matches, finds_controls.get('domain_alt', ''), **AHkwargs)

        if not matches:
            logger.error('NO MATCHES: %s' % finds_out)
            logger.error('NO MATCHES: %s' % self.response.soup or self.response.json or self.response.data or episodes_list)
            return itemlist

        # Refrescamos variables posiblemente actualizadas en "matches_post"
        self.finds = finds
        finds_controls = finds.get('controls', {})
        find_add_video_to_videolibrary = finds_controls.get('add_video_to_videolibrary', True)
        host = finds_controls.get('host', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        host_referer = finds_controls.get('host_referer', host)
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
                elem['url'] = self.convert_url_base64(elem['url'], self.host)
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
            infolabels = episode_title(elem['title'].capitalize(), infolabels)

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
                            context=item.context
                           )

            if elem.get('btdig_in_use', False): new_item.btdig_in_use = elem['btdig_in_use']
            if elem.get('post', None): new_item.post = elem['post']
            if elem.get('headers', None): new_item.headers = elem['headers']
            if item.video_path: new_item.video_path = item.video_path
            if item.filtertools: new_item.filtertools = item.filtertools
            
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

            new_item.url = self.do_url_replace(new_item.url, url_replace)

            if postprocess:
                new_item = postprocess(elem, new_item, item, **AHkwargs)

            if new_item and not new_item.matches and (new_item.url.startswith('magnet') or new_item.url.endswith('.torrent') \
                                                 or elem.get('matches', [])):
                new_item.matches = []
                new_item.matches.append(elem.get('matches', []).copy() or elem.copy())
            
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
                        if new_item.matches: itemlist[-1].matches.extend(new_item.matches.copy())   # Salvado Matches en el episodio anterior
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

            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico and not httptools.TEST_ON_AIR
            tmdb.set_infoLabels_itemlist(itemlist, modo_grafico, idioma_busqueda=idioma_busqueda)

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
        import xbmc
        self.Window_IsMedia = bool(xbmc.getCondVisibility('Window.IsMedia'))
        if not item.url_tvshow: item.url_tvshow = item.url

        if not finds: finds = self.finds
        finds_out = finds.get('findvideos', {})
        finds_out_episodes = finds.get('episodes', {})
        finds_langs = finds.get('langs', {})
        options = list()
        results = list()
        itemlist = []
        itemlist_total = []
        soup = {}
        matches = []
        if not matches_post and item.matches_post: matches_post = item.matches_post
        matches_post_episodes = None
        AHkwargs = {'soup': soup, 'finds': finds, 'function': 'get_video_options', 'videolibrary': False}
        AHkwargs['matches_post_list_all'] = kwargs.pop('matches_post_list_all', None)
        AHkwargs['matches_post_section'] = kwargs.pop('matches_post_section', None)
        AHkwargs['matches_post_seasons'] = kwargs.pop('matches_post_seasons', None)
        AHkwargs['matches_post_episodes'] = kwargs.pop('matches_post_episodes', None)
        AHkwargs['matches_post_get_video_options'] = matches_post or kwargs.pop('matches_post_get_video_options', None)

        finds_controls = finds.get('controls', {})
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
        url_replace = self.url_replace = self.finds.get('url_replace', []) or self.url_replace
        manage_torrents = finds_controls.get('manage_torrents', True)

        filter_languages = config.get_setting('filter_languages', item.channel, default=0)
        modo_grafico = config.get_setting('modo_grafico', item.channel, default=True)
        if not filter_languages: filter_languages = 0
        IDIOMAS_TMDB = finds_controls.get('IDIOMAS_TMDB', {}) or self.IDIOMAS_TMDB
        idioma_busqueda = IDIOMAS_TMDB[config.get_setting('modo_grafico_lang', item.channel, default=0)]    # Idioma base para TMDB
        if not idioma_busqueda: idioma_busqueda = 0
        idioma_busqueda_org = idioma_busqueda
        idioma_busqueda_save = ''
        idioma_busqueda_VO = IDIOMAS_TMDB[2]                                    # Idioma para VO: Local,VO

        self.btdigg = finds.get('controls', {}).get('btdigg', False) and config.get_setting('find_alt_link_option', item.channel, default=False)
        self.btdigg_search = self.btdigg and config.get_setting('find_alt_search', item.channel, default=False)
        btdig_in_use = False
        
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
            soup = self.create_soup(url, **kwargs)

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
                    elif isinstance(item.matches[0], dict):
                        matches = item.matches[:]
        
        langs = langs or self.parse_finds_dict(soup, finds_langs) or self.language
        if not isinstance(langs, list):
            langs = []

        if not item.matches and (item.url.startswith('magnet') or item.url.endswith('.torrent')):
            elem_json = {}

            if elem.get('season'): elem_json['season'] = elem.get('season', item.contentSeason)
            if elem.get('episode'): elem_json['episode'] = elem.get('episode', item.contentEpisodeNumber)
            elem_json['url'] = elem.get('url', '')
            if not elem.get('url', ''):
                return itemlist
            if not elem_json['url'].startswith('magnet'): elem_json['url'] = self.urljoin(self.host, elem['url'])
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
            matches.append(elem_json.copy())
        
        if not item.matches or (item.matches and not matches and (item.channel == 'videolibrary' \
                                                                  or item.contentChannel == 'videolibrary' \
                                                                  or item.from_channel == 'videolibrary')):
            matches = self.parse_finds_dict(soup, finds_out) if finds_out \
                      else self.response.soup or self.response.json or self.response.data
            if not isinstance(matches, (list, dict)):
                matches = []
            if item.matches and not isinstance(item.matches[0], dict):
                AHkwargs['matches'] = item.matches
                del item.matches
            if matches_post and matches:
                matches, langs = matches_post(item, matches, langs, response, **AHkwargs)
            if matches and AHkwargs.get('matches'):
                item.matches = matches[:]
                del AHkwargs['matches']

        if (item.matches or AHkwargs.get('matches')) and not matches:
            matches = AHkwargs.get('matches', []) or item.matches
            if item.matches and not isinstance(item.matches[0], dict):
                AHkwargs['matches'] = matches
                del item.matches
            if matches_post and matches and not isinstance(matches[0], dict):
                # Generar el json desde matches videoteca antiguos
                AHkwargs['videolibrary'] = True
                matches, langs = matches_post(item, matches, langs, response, **AHkwargs)
                item.matches = matches[:]
            if AHkwargs.get('matches'): del AHkwargs['matches']

        if self.btdigg:
            matches = self.find_btdigg_findvideos(item, item.matches or matches, finds_controls.get('domain_alt', ''), **AHkwargs)
        
        if not matches:
            if item.emergency_urls and not item.videolibray_emergency_urls:     # Hay urls de emergencia?
                item.armagedon = True                                           # Marcamos la situación como catastrófica 
                if len(item.emergency_urls) > 1:
                    matches = item.emergency_urls[1]                            # Restauramos matches de vídeos
                else:
                    matches = item.emergency_urls[0]                            # Restauramos torrents/magnetes
                if matches_post and matches and not isinstance(matches[0], dict):
                    # Generar el json desde matches videoteca antiguos
                    AHkwargs['videolibrary'] = True
                    matches, langs = matches_post(item, matches, langs, response, **AHkwargs)
            if not matches:
                if item.videolibray_emergency_urls:                             # Si es llamado desde creación de Videoteca...
                    return item                                                 # Devolvemos el Item de la llamada
                else:
                    return itemlist                                     #si no hay más datos, algo no funciona, pintamos lo que tenemos

        # Refrescamos variables posiblemente actualizadas en "matches_post"
        self.finds = finds
        finds_controls = finds.get('controls', {})
        self.host_torrent = finds_controls.get('host_torrent', self.host)
        self.doo_url = "%swp-admin/admin-ajax.php" % self.host
        host_torrent_referer = finds_controls.get('host_torrent_referer', self.host_torrent)
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
                elem['action'] = 'play'
                elem['language'] = elem.get('language', lang)

                if elem['url'].startswith('//'):
                    elem['url'] = 'https:%s' % elem['url']
                if url_base64: elem['url'] = self.convert_url_base64(elem['url'], self.host_torrent, referer=host_torrent_referer)

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

        from channels import autoplay
        from channels import filtertools
        from core import servertools

        if btdig_in_use:
            itemlist.append(item.clone(action="", size=999999 if item.contentType == 'movie' else 0, language=[''], 
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

            if elem.get('plot', ''): new_item.contentPlot = elem['plot']
            if elem.get('torrent_info', ''): new_item.torrent_info = elem['torrent_info']
            if elem.get('password', ''): new_item.password = elem['password']
            if elem.get('torrents_path', ''): new_item.torrents_path = elem['torrents_path']
            if elem.get('torrent_alt', ''): new_item.torrent_alt = elem['torrent_alt']
            if elem.get('alive', ''): new_item.alive = elem['alive']
            if elem.get('unify', ''): new_item.unify = elem['unify']
            if elem.get('folder', ''): new_item.folder = elem['folder']
            if elem.get('item_org', ''): new_item.item_org = elem['item_org']
            if elem.get('subtitle', ''): new_item.subtitle = elem['subtitle']
            new_item.size = self.convert_size(elem.get('size', 0))

            if new_item.server.lower() != 'torrent':
                new_item.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][%s][/COLOR] '
                new_item.title += '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' \
                                    % (new_item.quality, str(new_item.language), new_item.torrent_info)

            new_item.url = self.do_url_replace(new_item.url, url_replace)

            if postprocess:
                new_item = postprocess(elem, new_item, item, **AHkwargs)

            if new_item: itemlist.append(new_item.clone())

        # Requerido para FilterTools
        if itemlist:
            itemlist = filtertools.get_links(itemlist, item, self.list_language, self.list_quality_movies \
                                             if new_item.contentType == 'movie' else self.list_quality_tvshow)

        if itemlist:
            find_add_video_to_videolibrary = finds_controls.get('add_video_to_videolibrary', True)
            videolab_status = finds_controls.get('videolab_status', True) and modo_grafico
            try:
                itemlist = servertools.get_servers_itemlist(itemlist, lambda it: it.title % it.server.capitalize())
            except:
                pass
            if itemlist and itemlist[0].channel != 'filtertools':
                try:
                    itemlist = sorted(itemlist, key=lambda it: (int(-it.size if it.size \
                                                and it.contentType == 'movie' else it.size if it.size else 0), 
                                                it.language[0] if it.language and isinstance(it.language, list) else '', 
                                                it.server))
                except:
                    size = []
                    for it in itemlist:
                        size += [[it.size, it.title]]
                    logger.error('ERROR_SIZE: %s' % size)
                    logger.error(traceback.format_exc())
                if videolab_status:
                    # Llamamos al método para encontrar el estado del vídeo en la videoteca
                    itemlist = AH_find_videolab_status(item, itemlist, **AHkwargs)
                if find_add_video_to_videolibrary:
                    itemlist = self.add_video_to_videolibrary(item, itemlist, contentType=item.contentType)

            itemlist_total.extend(itemlist)

        # Requerido para AutoPlay
        autoplay.start(itemlist_total, item)

        return itemlist_total


class DooPlay(AlfaChannelHelper):

    def __init__(self, host, canonical={}, channel='', finds={}, debug=False,
                 list_language=[], list_quality=[], list_quality_tvshow=[], list_quality_movies=[], 
                 list_servers=[], language=[], idiomas={}, url_replace=[], 
                 IDIOMAS_TMDB={0: 'es', 1: 'en', 2: 'es,en'}, forced_proxy_opt=''):
        global DEBUG
        DEBUG = debug

        self.host = host
        self.canonical = canonical
        self.channel = channel
        self.finds = finds or {'find': {'find': [{'tagOR': ['div'], 'id': ['archive-content']}, 
                                                 {'tag': ['div'], 'class': ['content', 'result-item']}], 
                                        'find_all': [{'tag': ['article'], 'class': ['item movies', 'item tvshows']}]},
                               'categories': {'find': [{'tag': ['li'], 'id': ['menu-item-%s']}, {'tag': ['ul'], 'class': ['sub-menu']}], 
                                              'find_all': [{'tag': ['li']}]}, 
                               'search': {'find_all': [{'tag': ['div'], 'class': ['result-item']}]}, 
                               'get_language': {'find_all': [{'tag': ['span'], 'class': ['flag']}]}, 
                               'get_language_rgx': '(?:flags\/|-)(\w+)\.(?:png|jpg|jpeg|webp)', 
                               'get_quality': {'find': [{'tag': ['span'], 'class': ['quality']}], 'get_text': [{'strip': True}]}, 
                               'get_quality_rgx': '', 
                               'next_page': {}, 
                               'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
                               'last_page': {'find': [{'tag': ['div'], 'class': ['pagination']}, {'tag': ['span']}], 
                                             'get_text': [{'@TEXT': '(?i)\d+\s*de\s*(\d+)'}]}, 
                               'year': {'find': [{'tag': ['div'], 'class': ['metadata', 'meta']}], 'get_text': [{'tag': '|', 'strip': True}]}, 
                               'season_episode': {'find': [{'tag': ['img'], '@ARG': 'alt', '@TEXT': '(?i)(\d+x\d+)'}]}, 
                               'seasons': {'find': [{'tag': ['div'], 'id': ['seasons']}], 
                                           'find_all': [{'tag': ['div'], 'class': ['se-q']}]}, 
                               'season_num': {'find': [{'tag': ['span'], 'class': ['se-t'], '@TEXT': '(\d+)'}]}, 
                               'episode_url': '', 
                               'episodes': {'find': [{'tag': ['div'], 'id': ['seasons']}], 
                                            'find_all': [{'tag': ['li']}]}, 
                               'episode_num': {'find': [{'tag': ['div'], 'class': ['numerando']}], 'get_text': [{'strip': True}]}, 
                               'episode_clean': [], 
                               'plot': {'find': [{'tag': ['div'], 'class': ['texto', 'contenido']}], 'get_text': [{'strip': True}]}, 
                               'findvideos': {'find': [{'tagOR': ['div'], 'id': ['playeroptions']}, 
                                                       {'tag': ['ul'], 'class': ['options']}], 
                                              'find_all': [{'tag': 'li'}]}, 
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
        self.list_quality = self.list_quality_tvshow = list_quality or list_quality_tvshow
        self.list_quality_movies = list_quality_movies
        self.list_servers = list_servers
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
        self.response = httptools.build_response(HTTPResponse=True)
        self.response_proxy = self.response.proxy__
        self.itemlist = []


    def list_all_matches(self, item, matches_int, **AHkwargs):
        logger.info()

        matches = []
        finds = self.finds
        
        if item.json:
            json = jsontools.load(matches_int) if not isinstance(matches_int, dict) else matches_int
    
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
                elem_json['year'] = elem_json['year'][1] if len(elem_json['year']) >= 3 and len(elem_json['year'][1]) == 4 \
                                    else elem_json['year'][0] if len(elem_json['year']) >= 2 and len(elem_json['year'][0]) == 4 \
                                    else elem_json['year'][1] if len(elem_json['year']) >= 2 and len(elem_json['year'][1]) == 4 \
                                    else elem_json['year'][0] if len(elem_json['year']) >= 1 and len(elem_json['year'][0]) == 4 \
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
            except:
                logger.error('ERROR en seasonxepi: %s' % elem)
                logger.error(traceback.format_exc())
                continue

            if item.contentSeason != season: continue

            elem_json['url'] = elem.a.get("href", '')
            try:
                elem_json['title'] = elem.find("div", class_="episodiotitle").get_text('|', strip=True).split('|')[0]
            except:
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
