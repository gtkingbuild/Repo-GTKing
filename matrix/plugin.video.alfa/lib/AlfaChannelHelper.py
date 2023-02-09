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
else:
    import urlparse

import re
import traceback

from core import httptools
from core import scrapertools
from core.scrapertools import episode_title
from core import tmdb
from core import jsontools
from core.item import Item
from platformcode import config
from platformcode import logger

forced_proxy_def = 'ProxyCF'
DEBUG = False


class AlfaChannelHelper:

    def __init__(self, host, movie_path="/movies", tv_path="/serie", movie_action="findvideos", 
                 tv_action="seasons", canonical={}, url_replace=[], finds={}, debug=False):
        global DEBUG
        DEBUG = debug
        
        self.host = host
        self.movie_path = movie_path
        self.tv_path = tv_path
        self.movie_action = movie_action
        self.tv_action = tv_action
        self.doo_url = "%swp-admin/admin-ajax.php" % host
        self.canonical = canonical
        self.url_replace = url_replace
        self.finds = finds

    def create_soup(self, url, **kwargs):
        """
        :param url: url destino
        :param kwargs: parametros que se usan en donwloadpage
        :return: objeto soup o response sino soup
        """

        if "soup" not in kwargs: kwargs["soup"] = True
        if "add_referer" not in kwargs: kwargs["add_referer"] = True
        if "ignore_response_code" not in kwargs: kwargs["ignore_response_code"] = True
        if "canonical" not in kwargs: kwargs["canonical"] = self.canonical
        
        if DEBUG: logger.debug('Kwargs: %s' % kwargs)
        response = httptools.downloadpage(url, **kwargs)
        
        if kwargs.get("soup", {}):
            soup = response.soup or {}
        else:
            soup = response
        if response.host:
            self.doo_url = self.doo_url.replace(self.host, response.host)
            self.host = response.host

        return soup

    def list_all(self, item, postprocess=None):
        pass

    def limit_results(self, item, matches, lim_max=20):

        next_page = None
        next_limit = None

        if len(matches) > lim_max and not item.next_limit:
            limit = int(len(matches) / 2)
            next_limit = limit
            next_page = item.url
            matches = matches[:limit]
        elif item.next_limit:
            matches = matches[item.next_limit:]

        return matches, next_limit, next_page

    def section(self, item, menu_id=None, section=None, postprocess=None):
        pass

    def seasons(self, item, action="episodesxseason", postprocess=None):
        pass

    def episodes(self, item, action="findvideos", postprocess=None):
        pass

    def get_video_options(self, url, forced_proxy_opt=forced_proxy_def):
        pass

    def define_content_type(self, new_item, is_tvshow=False):

        if new_item.infoLabels.get("year", '') and str(new_item.infoLabels["year"]) in new_item.title and len(new_item.title) > 4:
            new_item.title = re.sub("\(|\)|%s" % str(new_item.infoLabels["year"]), "", new_item.title)

        if new_item.contentType == 'episode': 
            new_item.contentSerieName = re.sub('\s*\d+x\d+\s*', '', new_item.title)
            new_item.action = self.movie_action
        elif not is_tvshow and (self.movie_path in new_item.url or not self.tv_path in new_item.url):
            new_item.action = self.movie_action
            new_item.contentTitle = new_item.title
            if not new_item.contentType: new_item.contentType = 'movie'
            if not new_item.infoLabels.get("year", ''):
                new_item.infoLabels["year"] = '-'
        else:
            new_item.action = self.tv_action
            new_item.contentSerieName = new_item.title
            new_item.contentType = 'tvshow'

        return new_item

    def add_serie_to_videolibrary(self, item, itemlist):

        if item.add_videolibrary or item.library_playcounts:
            return itemlist
        if not (item.add_videolibrary and item.library_playcounts) and config.get_videolibrary_support() and len(itemlist) > 0:
            item.url = self.do_url_replace(item.url)
            
            itemlist.append(Item(channel=item.channel,
                                 title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                                 url=item.url,
                                 action="add_serie_to_library",
                                 extra="episodios",
                                 contentType='tvshow', 
                                 contentSerieName=item.contentSerieName
                                 )
                            )
        return itemlist

    def do_url_replace(self, url):
        
        if self.url_replace:

            for url_from, url_to in self.url_replace:
                url = re.sub(url_from, url_to, url)

        return url
        
    def do_quote(self, url):
        
        return urlparse.quote_plus(url)
        
    def do_unquote(self, url):
        
        return urlparse.unquote(url)
    
    def list_all_json(self, item, postprocess=None, lim_max=20, is_tvshow=False):
        logger.info()

        itemlist = list()

        json = self.create_soup(item.url, soup=False).json
        
        for key, elem in list(json.items()):

            new_item = Item(channel=item.channel,
                            url=elem.get('url', ''),
                            title=elem.get('title', ''),
                            thumbnail=elem.get('thumb', '') or elem.get('img', ''),
                            infoLabels={"year": elem.get('year', '-')}
                            )
            if postprocess:
                new_item = postprocess(json, elem, new_item, item)

            new_item = self.define_content_type(new_item, is_tvshow=is_tvshow)
            
            new_item.url = self.do_url_replace(new_item.url)

            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)
    
        return itemlist

    def parse_finds_dict(self, soup, finds, year=False, next_page=False, c_type=''):

        matches = matches_init = [] if not year and not next_page else '-' if year else ''
        if not finds: 
            return matches
        
        match = soup
        json = {}

        try:
            for x, (level_, block) in enumerate(finds.items()):
                level = re.sub('\d+', '', level_)
                for f in block:
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
                    attrs = {}
                    string = ''
                    regex = ''
                    argument = ''
                    strip = ''
                    json = {}
                    if isinstance(f, dict):
                        attrs = f.copy()
                        tag = attrs.pop('tag', '')
                        string = attrs.pop('string', '')
                        regex = attrs.pop('@TEXT', '')
                        argument = attrs.pop('@ARG', '')
                        strip = attrs.pop('@STRIP', True)
                        json = attrs.pop('@JSON', {})
                    else:
                        tag = f
                    if (isinstance(tag, str) and tag == '*') or (isinstance(tag, list) and len(tag) == 1 and tag[0] == '*'): 
                        tag = None

                    if DEBUG: logger.debug('find: %s=%s, %s, %s, %s, %s, %s' % (level, tag, attrs, string, regex, argument, str(strip)))
                    if '_all' not in level or ('_all' in level and x < len(finds[level])-1):

                        if level == 'get_text':
                            match = soup_func(tag or '', strip=strip)
                            if regex:
                                match = scrapertools.find_single_match(match, regex)
                        elif regex:
                            match = scrapertools.find_single_match(soup_func(tag, attrs=attrs, string=string).text, regex)
                        elif argument:
                            match = soup_func(tag, attrs=attrs, string=string).get(argument)
                        else:
                            match = soup_func(tag, attrs=attrs, string=string)
                    
                    else:
                        match = soup_func_all(tag, attrs=attrs, string=string)

                    if not match: break
                if not match: break

            if json:
                try:
                    if DEBUG: logger.debug('Json[500]: %s' % str(match)[:500])
                    json_all_work = {}
                    json_all = jsontools.load(match)
                    if json_all:
                        match = []
                        json_match = {}
                        for json_field in json:
                            json_all_work = json_all.copy()
                            key_org, key_des = json_field.split('|')
                            key_org = key_org.split(',')
                            for key_org_item in key_org:
                                json_match[key_des] = json_all_work.get(key_org_item, '')
                                json_all_work = json_all_work.get(key_org_item, {})
                        match.append(json_match)
                except:
                    match = []
                    logger.error('Json[500]: %s' % str(json_all_work)[:500])
                    logger.error(traceback.format_exc())
            
            if DEBUG: logger.debug('Matches[500]: %s' % str(match)[:500])
            
            matches = matches_init if not match else match
        except:
            matches = matches_init
            logger.error(traceback.format_exc())

        return matches


class CustomChannel(AlfaChannelHelper):
    pass


class DictionaryChannel(AlfaChannelHelper):

    def list_all(self, item, data='', postprocess=None, lim_max=30, finds={}):
        logger.info()

        if not finds: finds = self.finds
        finds_out = finds.get('find', {})
        finds_next_page = finds.get('next_page', {})
        finds_year = finds.get('year', {})
        finds_season_episode = finds.get('season_episode', {})
        itemlist = list()
        
        soup = data or self.create_soup(item.url)
        
        matches = self.parse_finds_dict(soup, finds_out)
        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches, lim_max=lim_max)

        next_page = self.parse_finds_dict(soup, finds_next_page, next_page=True, c_type=item.c_type)
        if next_page: next_page = urlparse.urljoin(self.host, next_page)

        for elem in matches:
            try:
                url = urlparse.urljoin(self.host, elem.a["href"])
                title = elem.find("img")["alt"]
                if not title:
                    title = elem.h2.text
            except:
                logger.error(elem)
                continue
            if finds.get('title_clean'):
                cleaner = finds['title_clean']
                if isinstance(finds['title_clean'], str):
                    cleaner = [finds['title_clean']]
                for clean in cleaner:
                    title = re.sub(clean, '', title).strip()
            try:
                thumb = elem.find("img")["data-src"]
            except:
                thumb = elem.find("img")["src"]
            thumb = urlparse.urljoin(self.host, thumb)

            year = self.parse_finds_dict(elem, finds_year, year=True, c_type=item.c_type)

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            infoLabels={"year": year, 'thumbnail': thumb},
                            thumbnail=thumb
                            )

            if item.c_type == 'episodios':
                new_item.contentType = 'episode'
                try:
                    sxe = self.parse_finds_dict(elem, finds_season_episode, c_type=item.c_type)
                    new_item.contentSeason, new_item.contentEpisodeNumber = sxe.text.split('x')
                    new_item.contentSeason = int(new_item.contentSeason)
                    new_item.contentEpisodeNumber = int(new_item.contentEpisodeNumber)
                except:
                    new_item.contentSeason = 1
                    new_item.contentEpisodeNumber = 1
                    logger.error(traceback.format_exc())

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            if item.c_type == 'peliculas': new_item.contentType = 'movie'
            new_item = self.define_content_type(new_item)

            new_item.url = self.do_url_replace(new_item.url)

            itemlist.append(new_item)
            #if DEBUG: logger.debug('New_item: %s' % new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)
        for new_item in itemlist:
            if not isinstance(new_item.infoLabels['year'], int):
                new_item.infoLabels['year'] = str(new_item.infoLabels['year']).replace('-', '')

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_all',
                                 c_type=item.c_type, 
                                 next_limit=next_limit
                                 )
                               )
        return itemlist

    def section(self, item, data= '',  menu_id=None, section=None, action="list_all", postprocess=None, section_list={}, finds={}):
        logger.info()

        if not finds: finds = self.finds
        finds_out = finds.get('find', {})
        itemlist = list()
        matches = list()
        soup = {}

        reverse = True if section == "year" else False

        if section_list:
            for genre, url in list(section_list.items()):
                title = genre.capitalize()
                matches.append([title, url])

        elif finds_out:
            soup = data or self.create_soup(item.url)

            matches = self.parse_finds_dict(soup, finds_out)
            for elem in matches:
                title = elem.a.text
                url = elem.a["href"]
                matches.append([title, url])

        if not matches:
            logger.error(finds_out)
            logger.error(soup or section_list)
            return itemlist

        for title, _url in matches:
            url = urlparse.urljoin(self.host, _url)

            new_item = Item(channel=item.channel,
                            title=title.capitalize(),
                            action=action,
                            url=url,
                            c_type=item.c_type
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)

            itemlist.append(new_item)

        if reverse:
            return itemlist[::-1]

        return itemlist

    def seasons(self, item, data='', action="episodesxseason", postprocess=None, finds={}):
        logger.info()

        if not finds: finds = self.finds
        finds_out = finds.get('season', {})
        itemlist = list()
        item.url = self.do_url_replace(item.url)
        
        soup = data or self.create_soup(item.url)
        
        matches = self.parse_finds_dict(soup, finds_out)

        if not matches:
            logger.error(finds_out)
            logger.error(soup)
            return itemlist

        infolabels = item.infoLabels

        for elem in matches:
            url = item.url
            try:
                if elem.a["href"].startswith('#'):
                    url = urlparse.urljoin(item.url, elem.a["href"])
                else:
                    url = urlparse.urljoin(self.host, elem.a["href"])
            except:
                pass
            try:
                infolabels["season"] = int(elem["value"])
            except:
                try:
                    infolabels["season"] = int(re.sub('(?i)temp\w*\s*', '', elem.a.text))
                except:
                    infolabels["season"] = 1
            title = "Temporada %s" % infolabels["season"]
            infolabels["mediatype"] = 'season'

            new_item = Item(channel=item.channel,
                            url=url, 
                            title=title,
                            action='episodesxseason',
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        itemlist = self.add_serie_to_videolibrary(item, itemlist)

        return itemlist

    def episodes(self, item, data= '', action="findvideos", postprocess=None, json=True, finds={}):
        logger.info()
        
        if not finds: finds = self.finds
        finds_out = finds.get('episodes', {})
        itemlist = list()
        item.url = self.do_url_replace(item.url)

        infolabels = item.infoLabels
        season = infolabels["season"]

        if json:
            soup = data or self.create_soup(item.url)
            soup = jsontools.load(self.parse_finds_dict(soup, finds_out))
            
            for i in range(int(infolabels.get('season', 1))-1, -1, -1):
                try:
                    matches = soup.get('props', {}).get('pageProps', {}).get('post', {})\
                                  .get('seasons', {})[i].get('episodes', {})
                    break
                except:
                    logger.error('Estructura de Temporadas incorrecta. No existe %s' % infolabels['season'])
                    matches = []
                    continue

            if not matches:
                logger.error(finds_out)
                logger.error(soup)
                return itemlist

            for elem in matches:
                try:
                    url = finds.get('episode_url', '') % (self.host, elem.get('slug', {}).get('name', ''), 
                                                          infolabels['season'], elem.get('slug', {}).get('episode', ''))
                    title = elem['title']
                except:
                    continue
                try:
                    infolabels["episode"] = int(elem['number'])
                except:
                    infolabels["episode"] = 1
                infolabels["mediatype"] = 'episode'
                infolabels = episode_title(title, infolabels)
                title = "%sx%s - %s" % (season, infolabels["episode"], title)

                new_item = Item(channel=item.channel,
                                title=title,
                                url=url,
                                action=action,
                                infoLabels=infolabels
                                )

                if postprocess:
                    new_item = postprocess(soup, elem, new_item, item)

                new_item.url = self.do_url_replace(new_item.url)
                
                itemlist.append(new_item)
        else:
            soup = data or self.create_soup(item.url)
        
            matches = self.parse_finds_dict(soup, finds_out)
            
            if not matches:
                logger.error(finds_out)
                logger.error(soup)
                return itemlist

            for elem in matches:
                try:
                    url = elem.a["href"]
                    title = scrapertools.slugify(elem.h2.text.strip(), strict=False)
                except:
                    continue

                for episode_num in finds.get('episode_num', []):
                    if scrapertools.find_single_match(title, episode_num):
                        infolabels["episode"] = int(scrapertools.find_single_match(title, episode_num))
                        break
                else:
                    infolabels["episode"] = int(scrapertools.find_single_match(title, '\d{2}') or 1)

                for episode_clean in finds.get('episode_clean', []):
                    if scrapertools.find_single_match(title, episode_clean):
                        title = scrapertools.find_single_match(title, episode_clean).strip()
                        break

                infolabels["mediatype"] = 'episode'
                infolabels = episode_title(title.capitalize(), infolabels)
                title = "%sx%s - %s" % (season, infolabels["episode"], title)

                new_item = Item(channel=item.channel,
                                title=title,
                                url=url,
                                action=action,
                                infoLabels=infolabels
                                )

                if postprocess:
                    new_item = postprocess(soup, elem, new_item, item)

                new_item.url = self.do_url_replace(new_item.url)
                
                itemlist.append(new_item)

        if itemlist:
            itemlist = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))
            tmdb.set_infoLabels_itemlist(itemlist, True)

        return itemlist

    def get_video_options(self, url, data='', langs=[], forced_proxy_opt=forced_proxy_def, referer=None, findvideos=False, json=False, finds={}):

        if not finds: finds = self.finds
        finds_out = finds.get('findvideos', {})
        finds_langs = finds.get('langs', {})
        options = list()
        results = list()
        url = self.do_url_replace(url)
        if findvideos: 
            item_local = findvideos.clone()
        else:
            item_local = findvideos

        soup = data or self.create_soup(url, forced_proxy_opt=forced_proxy_opt, referer=referer)
        
        langs = langs or self.parse_finds_dict(soup, finds_langs)
        matches = self.parse_finds_dict(soup, finds_out)
        
        if not matches or not langs:
            logger.error(finds_out)
            logger.error(soup)
            if findvideos: return [Item()]
            return [[soup, []]]

        for x, _lang in enumerate(langs):
            try:
                lang = _lang.find("span").text.lower()
            except:
                lang = _lang
            if 'descargar' in lang: continue
            if 'latino' in lang:
                lang = 'latino'
            elif 'español' in lang:
                lang = 'castellano'
            elif 'subtitulado' in lang:
                lang = 'subtitulado'
            
            if json:
                for json_fields in matches:
                    opt = [json_fields.get('server', ''), json_fields.get('url', ''), json_fields.get('quality', '')]
                    options.append((lang, opt))
                    if item_local:
                        if not item_local.plot and json_fields.get('plot', ''): item_local.plot = json_fields['plot']
                        if not item_local.thumbnail and json_fields.get('thumbnail', ''): item_local.plot = json_fields['thumbnail']
                        if not item_local.fanart and json_fields.get('fanart', ''): item_local.plot = json_fields['fanart']
            else:
                try:
                    for opt in matches[x]:
                        if not opt.strip().strip('\n'): continue
                        options.append((lang, opt))
                except:
                    try:
                        for opt in matches[x].find_all("li"):
                            if not opt.strip().strip('\n'): continue
                            options.append((lang, opt))
                    except:
                        pass
        
        if not options:
            for opt in matches:
                options.append((langs[0], opt))

        results.append([soup, options])

        if not findvideos: return results[0]

        itemlist = []
        for lang, url in results[0][1]:
            
            if isinstance(url, list) and len(url) >= 3:
                item_local.server = url[0]
                item_local.url = url[1]
                item_local.quality = url[2]
            else:
                item_local.server = ''
                try:
                    item_local.url = url.iframe.get("src", '') or url.iframe.get("href", '')
                except:
                    try:
                        item_local.url = url.a.get("src", '') or url.a.get("href", '')
                    except:
                        item_local.url = url
            
            item_local.title = '%s'
            item_local.language = lang
            item_local.action = 'play'
            item_local.headers = {'Referer': findvideos.url}
            item_local.setMimeType = 'application/vnd.apple.mpegurl'
            
            itemlist.append(item_local)

        from core import servertools
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

        return itemlist


class DooPlay(AlfaChannelHelper):

    def list_all(self, item, postprocess=None, lim_max=20):
        logger.info()

        itemlist = list()
        block = list()

        try:
            soup = self.create_soup(item.url)

            if soup.find("div", id="archive-content"):
                block = soup.find("div", id="archive-content")
            elif soup.find("div", class_="content"):
                block = soup.find("div", class_="content")
            matches = block.find_all("article", class_="item")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches, lim_max=lim_max)

        try:
            if not next_page:
                next_page = soup.find("div", class_="pagination").find("span", class_="current").next_sibling["href"]
                next_page = urlparse.urljoin(self.host, next_page)
        except:
            pass

        for elem in matches:
            try:
                poster = elem.find("div", class_="poster")
                metadata = elem.find("div", class_="metadata")
                data = elem.find("div", class_="data")
                thumb = poster.img["src"]
                title = poster.img["alt"]
                url = poster.find_all("a")[-1]["href"]
                url = urlparse.urljoin(self.host, url)
            except:
                logger.error(elem)
                continue
            try:
                year = int(metadata.find("span", text=re.compile(r"\d{4}")).text.strip())
            except:
                try:
                    year = int(data.find("span", text=re.compile(r"\d{4}")).text.strip())
                except:
                    year = "-"
            if len(str(year)) > 4:
                if scrapertools.find_single_match(str(year), r"(\d{4})"):
                    year = int(scrapertools.find_single_match(str(year), r"(\d{4})"))
                else:
                    year = "-"

            is_tvshow = True if "tvshows" in elem["class"] else False

            new_item = Item(channel=item.channel,
                            url=url,
                            title=title,
                            thumbnail=thumb,
                            infoLabels={"year": year}
                            )
            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item = self.define_content_type(new_item, is_tvshow=is_tvshow)
            
            new_item.url = self.do_url_replace(new_item.url)

            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action="list_all",
                                 next_limit=next_limit
                                 )
                            )

        return itemlist

    def section(self, item, menu_id=None, section=None, action="list_all", postprocess=None):
        logger.info()

        itemlist = list()
        matches = list()

        try:
            soup = self.create_soup(item.url)

            if menu_id:
                matches = soup.find("li", id="menu-item-%s" % menu_id).find("ul", class_="sub-menu")
            elif section.lower() == "genres":
                matches = soup.find("ul", class_="genres")
            elif section.lower() == "year":
                matches = soup.find("ul", class_="releases")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text
            if section == "genre":
                title = re.sub(r"\d+(?!\w)|\.", "", elem.a.text)

            url = urlparse.urljoin(self.host, url)

            new_item = Item(channel=item.channel,
                            title=title.capitalize(),
                            action=action,
                            url=url,
                            c_type=item.c_type
                            )
            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        return itemlist

    def seasons(self, item, action="episodesxseason", post=None, postprocess=None):
        
        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            if post:
                soup = self.create_soup(self.doo_url, post=post)
            else:
                soup = self.create_soup(item.url)

            matches = soup.find("div", id="seasons").find_all("div", class_="se-c")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels

        for elem in matches:
            try:
                infolabels["season"] = int(elem.find("span", class_="se-t").text)
            except:
                infolabels["season"] = 1
            title = "Temporada %s" % infolabels["season"]
            infolabels["mediatype"] = 'season'

            new_item = Item(channel=item.channel,
                            title=title,
                            url=item.url,
                            action=action,
                            infoLabels=infolabels
                            )
            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        itemlist = self.add_serie_to_videolibrary(item, itemlist)

        return itemlist

    def episodes(self, item, action="findvideos", post=None, postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            if post:
                soup = self.create_soup(self.doo_url, post=post)
            else:
                soup = self.create_soup(item.url)

            matches = soup.find("div", id="seasons").find_all("div", class_="se-c")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels

        season = infolabels["season"]

        for elem in matches:
            if elem.find("span", class_="se-t").text != str(season):
                continue

            epi_list = elem.find("ul", class_="episodios").find_all("li", class_=True)
            if not epi_list:
                epi_list = elem.find("ul", class_="episodios").find_all("li")

            for epi in epi_list:
                try:
                    info = epi.find("div", class_="episodiotitle")
                    url = info.a["href"]
                    epi_name = info.a.text
                except:
                    continue
                try:
                    infolabels["episode"] = int(epi.find("div", class_="numerando").text.split(" - ")[1])
                except:
                    infolabels["episode"] = 1
                infolabels["mediatype"] = 'episode'
                infolabels = episode_title(epi_name, infolabels)
                title = "%sx%s - %s" % (season, infolabels["episode"], epi_name)

                new_item = Item(channel=item.channel,
                                title=title,
                                url=url,
                                action=action,
                                infoLabels=infolabels
                                )
                if postprocess:
                    new_item = postprocess(soup, elem, new_item, item)

                new_item.url = self.do_url_replace(new_item.url)
                
                itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        return itemlist

    def search_results(self, item, action="findvideos", postprocess=None, next_pag=False):
        logger.info()

        itemlist = list()

        try:
            soup = self.create_soup(item.url)
            matches = soup.find_all("div", class_="result-item")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist
        
        try:
            next_page = soup.find("div", class_="pagination").find("span", class_="current").next_sibling["href"]
            next_page = urlparse.urljoin(self.host, next_page)
        except:
            next_page = ''

        for elem in matches:
            url = elem.a.get("href", '')
            if not url: continue
            thumb = elem.img["src"]
            title = elem.img["alt"]
            try:
                year = int(elem.find("span", class_="year").text)
            except:
                year = "-"

            new_item = Item(channel=item.channel,
                            title=title,
                            contentTitle=title,
                            url=url,
                            thumbnail=thumb,
                            action=action,
                            infoLabels={"year": year})

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item = self.define_content_type(new_item)
            
            new_item.url = self.do_url_replace(new_item.url)

            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

        if next_page and next_pag:
            itemlist.append(item.clone(title="Siguiente >>",
                                         url=next_page,
                                         action="search_more"
                                         )
                            )

        return itemlist

    def get_video_options(self, url, forced_proxy_opt=forced_proxy_def, referer=None):

        results = list()
        url = self.do_url_replace(url)

        try:
            soup = self.create_soup(url, forced_proxy_opt=forced_proxy_opt, referer=referer)
            
            if soup.find("nav", class_="player"):
                options = soup.find("ul", class_="options")
            else:
                options = soup.find(id=re.compile("playeroptions"))

            matches = options.find_all("li")
        except:
            matches = []
            logger.error(traceback.format_exc())

        results.append([soup, matches])

        return results[0]

    def get_data_by_post(self, elem=None, post=None, custom_url=""):
        
        if not post:
            post = {"action": "doo_player_ajax",
                    "post": elem["data-post"],
                    "nume": elem["data-nume"],
                    "type": elem["data-type"]
                    }

        if custom_url:
            self.doo_url = self.do_url_replace(custom_url)

        data = httptools.downloadpage(self.doo_url, post=post, add_referer=True, soup=True, ignore_response_code=True)

        return data


class ToroFilm(AlfaChannelHelper):

    def list_all(self, item, postprocess=None, lim_max=20):
        logger.info()

        itemlist = list()
        
        try:
            soup = self.create_soup(item.url)
            matches = soup.find("ul", class_="post-lst").find_all("article", class_="post")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches, lim_max=lim_max)

        if not next_page:
            try:
                next_page = soup.find("div", class_="nav-links").find_all("a")[-1]["href"]
                next_page = urlparse.urljoin(self.host, next_page)
            except:
                pass

        for elem in matches:
            try:
                url = urlparse.urljoin(self.host, elem.a["href"])
                title = elem.h2.text
            except:
                logger.error(elem)
                continue
            try:
                thumb = elem.find("img")["data-src"]
            except:
                thumb = elem.find("img")["src"]

            try:
                year = int(elem.find("span", class_="year").text)
            except:
                year = '-'

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            thumbnail=thumb,
                            infoLabels={"year": year}
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item = self.define_content_type(new_item)
            
            new_item.url = self.do_url_replace(new_item.url)

            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_all',
                                 next_limit=next_limit
                                 )
                               )
        return itemlist

    def section(self, item, menu_id=None, section=None, action="list_all", postprocess=None):
        logger.info()

        itemlist = list()
        matches = list()

        reverse = True if section == "year" else False
        
        try:
            soup = self.create_soup(item.url)

            if menu_id:
                matches = soup.find("li", id="menu-item-%s" % menu_id).find("ul", class_="sub-menu")
            elif section:
                if section == "alpha":
                    matches = soup.find("ul", class_="az-lst")
                elif section == "year":
                    matches = soup.find("section", id=re.compile(r"torofilm_movies_annee-\d+"))
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text

            url = urlparse.urljoin(self.host, url)

            new_item = Item(channel=item.channel,
                            title=title.capitalize(),
                            action=action,
                            url=url,
                            c_type=item.c_type
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)
        
        if reverse:
            return itemlist[::-1]
        return itemlist

    def seasons(self, item, action="episodesxseason", postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)
            matches = soup.find_all("li", class_="sel-temp")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels

        for elem in matches:
            try:
                infolabels["season"] = int(elem.a["data-season"])
            except:
                infolabels["season"] = 1
            title = "Temporada %s" % infolabels["season"]
            infolabels["mediatype"] = 'season'
            post_id = elem.a["data-post"]

            new_item = Item(channel=item.channel,
                            title=title,
                            action='episodesxseason',
                            post_id=post_id,
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        itemlist = self.add_serie_to_videolibrary(item, itemlist)

        return itemlist

    def episodes(self, item, action="findvideos", postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        infolabels = item.infoLabels
        season = infolabels["season"]

        post = {"action": "action_select_season",
                "season": season,
                "post": item.post_id
                }
        
        try:
            soup = self.create_soup(self.doo_url, post=post)

            matches = soup.find_all("li")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches:
            try:
                url = elem.a["href"]
                title = elem.find("span", class_="num-epi").text
            except:
                continue
            try:
                infolabels["episode"] = int(title.split("x")[1])
            except:
                infolabels["episode"] = 1
            infolabels["mediatype"] = 'episode'
            infolabels = episode_title(title, infolabels)
            title = "%sx%s - %s" % (season, infolabels["episode"], title)

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            action=action,
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        return itemlist

    def get_video_options(self, url, forced_proxy_opt=forced_proxy_def, referer=None):

        options = list()
        results = list()
        url = self.do_url_replace(url)

        try:
            soup = self.create_soup(url, forced_proxy_opt=forced_proxy_opt, referer=referer)

            matches = soup.find_all("ul", class_="aa-tbs aa-tbs-video")
        except:
            matches = []
            logger.error(traceback.format_exc())

        for opt in matches:
            options.extend(opt.find_all("li"))

        results.append([soup, options])

        return results[0]


class ToroPdon(AlfaChannelHelper):

    def list_all(self, item, postprocess=None, lim_max=24):
        logger.info()

        itemlist = list()
        
        try:
            soup = self.create_soup(item.url)
            if item.c_type == 'episodios':
                matches = soup.find("ul", class_="MovieList Rows episodes").find_all("li", class_="TPostMv")
            else:
                matches = soup.find("ul", class_="MovieList Rows").find_all("div", class_="TPost C hentry")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches, lim_max=lim_max)

        if not next_page:
            try:
                #next_page = soup.find("div", class_="nav-links").find_all("a")[-1]["href"]
                next_page = soup.find("div", class_="nav-links").find("a", class_="next page-numbers")["href"]
                next_page = urlparse.urljoin(self.host, next_page)
            except:
                pass

        for elem in matches:
            try:
                url = urlparse.urljoin(self.host, elem.a["href"])
                title = elem.find("img")["alt"]
            except:
                logger.error(elem)
                continue
            try:
                thumb = elem.find("img")["data-src"]
            except:
                thumb = elem.find("img")["src"]
            thumb = urlparse.urljoin(self.host, thumb)

            try:
                if item.c_type == 'episodios':
                    year = '-'
                else:
                    year = int(elem.find("span", class_="Year").text)
            except:
                year = '-'

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            thumbnail=thumb,
                            infoLabels={"year": year}
                            )

            if item.c_type == 'episodios':
                new_item.contentSeason, new_item.contentEpisodeNumber = elem.find("span", class_="Year").text.split('x')
                new_item.contentType = 'episode'
            
            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item = self.define_content_type(new_item)

            new_item.url = self.do_url_replace(new_item.url)

            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_all',
                                 c_type=item.c_type, 
                                 next_limit=next_limit
                                 )
                               )
        return itemlist

    def section(self, item, menu_id=None, section=None, action="list_all", postprocess=None):
        logger.info()

        itemlist = list()
        matches = list()

        reverse = True if section == "year" else False
        
        try:
            soup = self.create_soup(item.url)

            if menu_id:
                matches = soup.find("li", id="menu-item-%s" % menu_id).find("ul", class_="sub-menu")
            elif section:
                if section == "alpha":
                    matches = soup.find("ul", class_="az-lst")
                elif section == "year":
                    matches = soup.find("section", id=re.compile(r"torofilm_movies_annee-\d+"))
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text

            url = urlparse.urljoin(self.host, url)

            new_item = Item(channel=item.channel,
                            title=title.capitalize(),
                            action=action,
                            url=url,
                            c_type=item.c_type
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)
        
        if reverse:
            return itemlist[::-1]
        return itemlist

    def seasons(self, item, action="episodesxseason", postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)
            matches = soup.find("select", id="select-season").find_all('option')
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels

        for elem in matches:
            try:
                infolabels["season"] = int(elem["value"])
            except:
                infolabels["season"] = 1
            title = "Temporada %s" % infolabels["season"]
            infolabels["mediatype"] = 'season'

            new_item = Item(channel=item.channel,
                            url=item.url, 
                            title=title,
                            action='episodesxseason',
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        itemlist = self.add_serie_to_videolibrary(item, itemlist)

        return itemlist

    def episodes(self, item, action="findvideos", postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        infolabels = item.infoLabels
        season = infolabels["season"]

        try:
            soup = jsontools.load(self.create_soup(item.url).find("script", id="__NEXT_DATA__").text)
            matches = soup['props']['pageProps']['thisSerie']['seasons'][int(infolabels['season'])-1]['episodes']
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches:
            try:
                url = '%sepisodio/%s-temporada-%s-episodio-%s' % (self.host, elem['slug']['name'], infolabels['season'], elem['slug']['episode'])
                title = elem['title']
            except:
                continue
            try:
                infolabels["episode"] = int(elem['number'])
            except:
                infolabels["episode"] = 1
            infolabels["mediatype"] = 'episode'
            infolabels = episode_title(title, infolabels)
            title = "%sx%s - %s" % (season, infolabels["episode"], title)

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            action=action,
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        return itemlist

    def get_video_options(self, url, forced_proxy_opt=forced_proxy_def, referer=None):

        options = list()
        results = list()
        url = self.do_url_replace(url)

        try:
            soup = self.create_soup(url, forced_proxy_opt=forced_proxy_opt, referer=referer)
            langs = soup.find_all("div", class_="_1R6bW_0")
            matches = soup.find_all("ul", class_="sub-tab-lang _3eEG3_0 optm3 hide")
        except:
            matches = []
            logger.error(traceback.format_exc())
        
        for x, _lang in enumerate(langs):
            lang = _lang.find("span").text.lower()
            if 'descargar' in lang: continue
            if 'latino' in lang:
                lang = 'latino'
            elif 'español' in lang:
                lang = 'castellano'
            elif 'subtitulado' in lang:
                lang = 'subtitulado'
            
            for opt in matches[x].find_all("li"):
                options.append((lang, opt))

        results.append([soup, options])

        return results[0]


class ToroPlay(AlfaChannelHelper):

    def list_all(self, item, postprocess=None, lim_max=20):
        logger.info()

        itemlist = list()
        
        try:
            soup = self.create_soup(item.url)
            matches = soup.find("ul", class_="MovieList").find_all("article", class_=re.compile("TPost C"))
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches, lim_max=lim_max)

        if not next_page:
            try:
                next_page = soup.find(class_="wp-pagenavi").find(class_="current").find_next_sibling()["href"]
                next_page = urlparse.urljoin(self.host, next_page)
            except:
                pass

        for elem in matches:
            try:
                url = urlparse.urljoin(self.host, elem.a["href"])
                title = elem.a.h3.text
                thumb = elem.find("img")
                thumb = thumb["data-src"] if thumb.has_attr("data-src") else thumb["src"]
            except:
                logger.error(elem)
                continue
            try:
                year = scrapertools.find_single_match(title, r'\((\d{4})\)')
                if not year:
                    year = elem.find("span", class_="Year").text
                year = int(year)
            except:
                year = "-"

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            thumbnail=thumb,
                            infoLabels={"year": year}
                            )

            new_item = self.define_content_type(new_item)

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_all',
                                 next_limit=next_limit
                                 )
                            )

        return itemlist

    def section(self, item, menu_id=None, section=None, action="list_all", postprocess=None):
        logger.info()

        itemlist = list()
        matches = list()
        reverse = True if section == "year" else False

        try:
            soup = self.create_soup(item.url)

            if menu_id:
                matches = soup.find("li", id="menu-item-%s" % menu_id).find("ul", class_="sub-menu")
            elif section:
                if section == "genres":
                    matches = soup.find(id=re.compile(r"categories-\d+"))
                elif section == "alpha":
                    matches = soup.find("ul", class_="AZList")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text

            url = urlparse.urljoin(self.host, url)

            new_item = Item(channel=item.channel,
                            title=title.capitalize(),
                            action=action,
                            url=url,
                            c_type=item.c_type
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        if reverse:
            return itemlist[::-1]

        return itemlist

    def list_alpha(self, item, action="season", postprocess=None):

        itemlist = list()

        try:
            soup = self.create_soup(item.url)
            matches = soup.find("tbody").find_all("tr")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist
        
        matches, next_limit, next_page = self.limit_results(item, matches)

        if not next_page:
            try:
                next_page = soup.find(class_="wp-pagenavi").find(class_="current").find_next_sibling()["href"]
                next_page = urlparse.urljoin(self.host, next_page)
            except:
                pass

        for elem in matches:
            info = elem.find("td", class_="MvTbTtl")
            thumb = elem.find("td", class_="MvTbImg").a.img["src"]
            url = info.a["href"]
            title = info.a.text.strip()
            try:
                year = int(elem.find("td", text=re.compile(r"\d{4}")).string)
            except:
                year = "-"

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            action=action,
                            thumbnail=thumb,
                            infoLabels={"year": year}
                            )

            new_item = self.define_content_type(new_item)

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_alpha',
                                 next_limit=next_limit
                                 )
                            )

        return itemlist

    def seasons(self, item, action="episodesxseason", postprocess=None):
        
        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)
            matches = soup.find_all("div", class_="Wdgt AABox")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels
        for elem in matches:
            try:
                infolabels["season"] = int(elem.find("div", class_="AA-Season")["data-tab"])
            except:
                infolabels["season"] = 1
            title = "Temporada %s" % infolabels["season"]
            infolabels["mediatype"] = 'season'

            new_item = Item(channel=item.channel,
                            title=title,
                            url=item.url,
                            action=action,
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        itemlist = self.add_serie_to_videolibrary(item, itemlist)

        return itemlist

    def episodes(self, item, action="findvideos", postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)
            matches = soup.find_all("div", class_="Wdgt AABox")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels
        season = infolabels["season"]

        for elem in matches:
            if elem.find("div", class_="AA-Season")["data-tab"] == str(season):
                epi_list = elem.find_all("tr")
                for epi in epi_list:
                    try:
                        url = epi.a["href"]
                        epi_name = epi.find("td", class_="MvTbTtl").a.text
                    except:
                        continue
                    try:
                        infolabels["episode"] = int(epi.find("span", class_="Num").text)
                    except:
                        infolabels["episode"] = 1
                    infolabels["mediatype"] = 'episode'
                    infolabels = episode_title(epi_name, infolabels)
                    title = "%sx%s - %s" % (season, infolabels["episode"], epi_name)

                    new_item = Item(channel=item.channel,
                                    title=title,
                                    url=url,
                                    action=action,
                                    infoLabels=infolabels
                                    )

                    if postprocess:
                        new_item = postprocess(soup, elem, new_item, item)

                    new_item.url = self.do_url_replace(new_item.url)
                    
                    itemlist.append(new_item)
                break

        tmdb.set_infoLabels_itemlist(itemlist, True)

        return itemlist

    def get_video_options(self, url, forced_proxy_opt=forced_proxy_def, referer=None):
        
        results = list()
        url = self.do_url_replace(url)

        try:
            soup = self.create_soup(url, forced_proxy_opt=forced_proxy_opt, referer=referer)

            matches = soup.find("ul", class_="TPlayerNv").find_all("li")
        except:
            matches = []
            logger.error(traceback.format_exc())

        results.append([soup, matches])

        return results[0]


class ToroFlix(AlfaChannelHelper):

    def list_all(self, item, postprocess=None, lim_max=20):
        logger.info()

        itemlist = list()
        
        try:
            soup = self.create_soup(item.url)
            matches = soup.find("ul", class_="MovieList").find_all("article", class_=re.compile("TPost B"))
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches, lim_max=lim_max)

        if not next_page:
            try:
                next_page = soup.find(class_="wp-pagenavi").find(class_="current").find_next_sibling()["href"]
                next_page = urlparse.urljoin(self.host, next_page)
            except:
                pass

        for elem in matches:
            try:
                url = urlparse.urljoin(self.host, elem.a["href"])
                title = elem.find(class_="Title").text
                thumb = elem.find("img")
                thumb = thumb["data-src"] if thumb.has_attr("data-src") else thumb["src"]
            except:
                logger.error(elem)
                continue
            try:
                year = int(elem.find("span", class_="Date").text)
            except:
                year = "-"

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            thumbnail=thumb,
                            infoLabels={"year": year}
                            )

            new_item = self.define_content_type(new_item)

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_all'
                                 )
                            )

        return itemlist

    def section(self, item, menu_id=None, section=None, action="list_all", postprocess=None):
        logger.info()

        itemlist = list()
        matches = list()
        reverse = True if section == "year" else False

        try:
            soup = self.create_soup(item.url)

            if menu_id:
                matches = soup.find("li", id="menu-item-%s" % menu_id).find("ul", class_="sub-menu")
            elif section:
                if section == "genres":
                    matches = soup.find(id=(r"toroflix_genres_widget-2"))
                elif section == "alpha":
                    matches = soup.find("ul", class_="AZList")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text

            url = urlparse.urljoin(self.host, url)

            new_item = Item(channel=item.channel,
                            title=title.capitalize(),
                            action=action,
                            url=url,
                            c_type=item.c_type
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        if reverse:
            return itemlist[::-1]

        return itemlist

    def list_alpha(self, item, action="season", postprocess=None):

        itemlist = list()

        try:
            soup = self.create_soup(item.url)
            matches = soup.find("tbody").find_all("tr")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches)

        if not next_page:
            try:
                next_page = soup.find(class_="wp-pagenavi").find(class_="current").find_next_sibling()["href"]
                next_page = urlparse.urljoin(self.host, next_page)
            except:
                pass

        for elem in matches:
            info = elem.find("td", class_="MvTbTtl")
            thumb = elem.find("td", class_="MvTbImg").a.img["src"]
            url = info.a["href"]
            title = info.a.text.strip()
            try:
                year = int(elem.find("td", text=re.compile(r"\d{4}")).string)
            except:
                year = "-"
            
            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            action=action,
                            thumbnail=thumb,
                            infoLabels={"year": year}
                            )

            new_item = self.define_content_type(new_item)

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_alpha',
                                 next_limit=next_limit
                                 )
                            )

        return itemlist

    def seasons(self, item, action="episodesxseason", postprocess=None):
        
        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)
            matches = soup.find_all("section", class_="SeasonBx AACrdn")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels

        for elem in matches:
            try:
                infolabels["season"] = int(elem.a.span.text)
            except:
                infolabels["season"] = 1
            title = "Temporada %s" % infolabels["season"]
            infolabels["mediatype"] = 'season'
            url = elem.a["href"]

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            action=action,
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        itemlist = self.add_serie_to_videolibrary(item, itemlist)

        return itemlist

    def episodes(self, item, action="findvideos", postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)
            matches = soup.find_all("tr", class_="Viewed")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels
        season = infolabels["season"]

        for elem in matches:
            try:
                url = elem.find("td", class_="MvTbTtl").a["href"]
                epi_name = elem.find("td", class_="MvTbTtl").a.text
            except:
                continue
            try:
                infolabels["episode"] = int(elem.find("span", class_="Num").text)
            except:
                infolabels["episode"] = 1
            infolabels["mediatype"] = 'episode'
            infolabels = episode_title(epi_name, infolabels)
            title = "%sx%s - %s" % (season, infolabels["episode"], epi_name)

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            action=action,
                            infoLabels=infolabels
                           )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        return itemlist

    def get_video_options(self, url, forced_proxy_opt=forced_proxy_def, referer=None):
        
        results = list()
        url = self.do_url_replace(url)

        try:
            soup = self.create_soup(url, forced_proxy_opt=forced_proxy_opt, referer=referer)
            
            if soup.find("div", class_="optns-bx"):
                matches = soup.find_all("button")
            else:
                matches = soup.find("ul", class_="ListOptions").find_all("li")
        except:
            matches = []
            logger.error(traceback.format_exc())

        results.append([soup, matches])

        return results[0]


class PsyPlay(AlfaChannelHelper):

    def list_all(self, item, postprocess=None, lim_max=20):
        logger.info()

        itemlist = list()

        try:
            soup = self.create_soup(item.url)
            matches = soup.find("div", class_="movies-list").find_all("div", class_="ml-item")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        matches, next_limit, next_page = self.limit_results(item, matches, lim_max=lim_max)
        if not next_page:
            try:
                item.url = re.sub(r"page/\d+/", "", item.url)
                next_page = soup.find("ul", class_="pagination").find("li", class_="active").next_sibling.a.text
                next_page = urlparse.urljoin(self.host, "page/%s/" % next_page)
                next_page = urlparse.urljoin(self.host, next_page)
            except:
                pass

        for elem in matches:
            try:
                thumb = urlparse.urljoin(self.host, elem.a.img.get("src", '') or elem.a.img.get("data-original", ''))
                title = elem.a.find("span", class_="mli-info").h2.text
                url = urlparse.urljoin(self.host, elem.a["href"])
            except:
                logger.error(elem)
                continue

            try:
                year = int(elem.find("div", class_="jt-info", text=re.compile("\d{4}")).text)
            except:
                year = "-"

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            thumbnail=thumb,
                            infoLabels={"year": year})

            new_item = self.define_content_type(new_item)

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

        if next_page:
            itemlist.append(Item(channel=item.channel,
                                 title="Siguiente >>",
                                 url=next_page,
                                 action='list_all'
                                 )
                            )

        return itemlist

    def section(self, item, menu_id=None, section=None, action="list_all", postprocess=None):
        logger.info()

        itemlist = list()
        matches = list()
        reverse = True if section == "year" else False

        try:
            soup = self.create_soup(item.url)

            if menu_id:
                matches = soup.find("li", id="menu-item-%s" % menu_id).find("ul", class_="sub-menu")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches.find_all("li"):
            url = elem.a["href"]
            title = elem.a.text

            url = urlparse.urljoin(self.host, url)

            new_item = Item(channel=item.channel,
                            title=title.capitalize(),
                            action=action,
                            url=url,
                            c_type=item.c_type
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        if reverse:
            return itemlist[::-1]

        return itemlist

    def seasons(self, item, action="episodesxseason", postprocess=None):
        
        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)
            matches = soup.find("div", id="seasons").find_all("div", recursive=False)
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        infolabels = item.infoLabels

        for elem in matches:
            try:
                infolabels["season"] = int(scrapertools.find_single_match(elem.text, r"(\d+)"))
            except:
                infolabels["season"] = 1
            title = "Temporada %s" % infolabels["season"]
            infolabels["mediatype"] = 'season'

            new_item = Item(channel=item.channel,
                            title=title,
                            url=item.url,
                            action=action,
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        itemlist = self.add_serie_to_videolibrary(item, itemlist)

        return itemlist

    def episodes(self, item, action="findvideos", postprocess=None):
        logger.info()

        itemlist = list()
        item.url = self.do_url_replace(item.url)

        try:
            soup = self.create_soup(item.url)

            infolabels = item.infoLabels
            season = infolabels["season"]

            matches = soup.find("div", id="seasons").find_all("div", recursive=False)[int(season) - 1].find_all("a")
        except:
            matches = []
            logger.error(traceback.format_exc())

        if not matches:
            return itemlist

        for elem in matches:
            try:
                url = elem["href"]
            except:
                continue
            try:
                infolabels["episode"] = int(scrapertools.find_single_match(elem.text, r"(\d+)"))
            except:
                infolabels["episode"] = 1
            infolabels["mediatype"] = 'episode'
            title = "%sx%s - " % (season, infolabels["episode"])

            new_item = Item(channel=item.channel,
                            title=title,
                            url=url,
                            action=action,
                            infoLabels=infolabels
                            )

            if postprocess:
                new_item = postprocess(soup, elem, new_item, item)

            new_item.url = self.do_url_replace(new_item.url)
            
            itemlist.append(new_item)

        tmdb.set_infoLabels_itemlist(itemlist, True)

        return itemlist

    def get_video_options(self, url, forced_proxy_opt=forced_proxy_def, referer=None):
        
        results = list()
        url = self.do_url_replace(url)

        try:
            soup = self.create_soup(url, forced_proxy_opt=forced_proxy_opt, referer=referer)
        
            matches = soup.find("ul", class_="idTabs").find_all("li")
        except:
            matches = []
            logger.error(traceback.format_exc())

        results.append([soup, matches])

        return results[0]
