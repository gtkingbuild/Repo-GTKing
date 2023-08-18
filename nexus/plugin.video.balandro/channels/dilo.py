# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, jsontools, servertools


host = 'https://www.dilo.nu/'


h_catalogue = host + 'catalogue'


IDIOMAS = {'la': 'Lat', 'es': 'Esp', 'en_es': 'Vose', 'en': 'VO'}


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_dilo_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar ...[/B]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, follow_redirects=True, only_headers=False, raise_weberror=False):
    headers = {'Referer': host}

    timeout = None
    if host in url:
        if config.get_setting('channel_dilo_proxies', default=''): timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        resp = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror, timeout=timeout)
    else:
        resp = httptools.downloadpage_proxy('dilo', url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror, timeout=timeout)

        if not resp.data:
            if not 'search?s=' in url:
                platformtools.dialog_notification('Dilo', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')
                resp = httptools.downloadpage_proxy('dilo', url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror, timeout=timeout)

    if '<title>You are being redirected...</title>' in resp.data or '<title>Just a moment...</title>' in resp.data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(resp.data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    resp = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror, timeout=timeout)
                else:
                    resp = httptools.downloadpage_proxy('dilo', url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror, timeout=timeout)
        except:
            pass

    if only_headers: return resp.headers

    if '<title>Just a moment...</title>' in resp.data:
        if not 'search?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return resp.data


def acciones(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( channel='submnuctext', action='_test_webs', title='Test Web del canal [COLOR yellow][B] ' + host + '[/B][/COLOR]',
                                from_channel='dilo', folder=False, text_color='chartreuse' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_dilo', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='acciones', title= '[B]Acciones[/B] [COLOR plum](si no hay resultados)[/COLOR]', text_color='goldenrod' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = h_catalogue, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevos episodios', action = 'last_epis', url = host, search_type = 'tvshow', text_color = 'olive' ))

    itemlist.append(item.clone( title = 'Las de la semana', action = 'list_all', url = h_catalogue+'?sort=mosts-week', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Actualizadas', action = 'list_all', url = h_catalogue+'?sort=latest', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = h_catalogue+'?status=0', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Finalizadas', action = 'list_all', url = h_catalogue+'?status=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = h_catalogue + '?genre[]=pelicula', group ='pelis', search_type = 'tvshow', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(h_catalogue)

    patron = '<input type="checkbox" class="[^"]+" id="[^"]+" value="([^"]+)" name="genre\[\]">'
    patron += '\s*<label class="custom-control-label" for="[^"]+">([^<]+)</label>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for valor, titulo in matches:
        if titulo == 'Libros': continue
        elif titulo == 'Pelicula': continue
        elif titulo == 'Audiolibros': continue
        elif titulo == 'Juegos PC': continue
        elif titulo == 'Onlyfans': continue
        elif titulo == 'Software Portable': continue

        itemlist.append(item.clone( title = titulo.strip(), url = h_catalogue + '?genre[]=' + valor, action = 'list_all', text_color = 'hotpink' ))

    if not descartar_xxx:
        if itemlist:
            itemlist.append(item.clone( action = 'list_all', title = 'xxx / adultos', url = host + 'search?s=adultos', text_color = 'hotpink' ))
            itemlist.append(item.clone( action = 'temporadas', title = 'xxx / adultos internacional', url = host + 'internacional-adultos/', text_color = 'hotpink' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1970, -1):
        itemlist.append(item.clone( title = str(x), url = h_catalogue + '?year[]=' + str(x), action = 'list_all', text_color = 'hotpink' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    web_paises = [
       ['AR', 'Argentina'],
       ['AU', 'Australia'],
       ['AT', 'Austria'],
       ['BE', 'B\xc3\xa9lgica'],
       ['BO', 'Bolivia'],
       ['BR', 'Brasil'],
       ['BG', 'Bulgaria'],
       ['CA', 'Canad\xc3\xa1'],
       ['CL', 'Chile'],
       ['CN', 'China'],
       ['CO', 'Colombia'],
       ['CR', 'Costa Rica'],
       ['HR', 'Croacia'],
       ['CU', 'Cuba'],
       ['CZ', 'Rep\xc3\xbablica Checa'],
       ['DK', 'Dinamarca'],
       ['EC', 'Ecuador'],
       ['SV', 'El Salvador'],
       ['FI', 'Finlandia'],
       ['FR', 'Francia'],
       ['DE', 'Alemania'],
       ['GR', 'Grecia'],
       ['GT', 'Guatemala'],
       ['HN', 'Honduras'],
       ['HK', 'Hong Kong'],
       ['HU', 'Hungr\xc3\xada'],
       ['IS', 'Islandia'],
       ['IN', 'India'],
       ['IE', 'Irlanda'],
       ['IL', 'Israel'],
       ['IT', 'Italia'],
       ['JP', 'Jap\xc3\xb3n'],
       ['LT', 'Lituania'],
       ['MY', 'Malasia'],
       ['MX', 'M\xc3\xa9xico'],
       ['NL', 'Pa\xc3\xadses Bajos'],
       ['NZ', 'Nueva Zelanda'],
       ['NO', 'Noruega'],
       ['PA', 'Panam\xc3\xa1'],
       ['PY', 'Paraguay'],
       ['PE', 'Per\xc3\xba'],
       ['PL', 'Polonia'],
       ['PT', 'Portugal'],
       ['PR', 'Puerto Rico'],
       ['RO', 'Rumania'],
       ['RU', 'Rusia'],
       ['RS', 'Serbia'],
       ['SG', 'Singapur'],
       ['ES', 'Espa\xc3\xb1a'],
       ['SE', 'Suecia'],
       ['CH', 'Suiza'],
       ['TH', 'Tailandia'],
       ['TR', 'Turqu\xc3\xada'],
       ['UA', 'Ucrania'],
       ['GB', 'Reino Unido'],
       ['US', 'Estados Unidos'],
       ['UY', 'Uruguay'],
       ['VE', 'Venezuela']
       ]

    for x in sorted(web_paises, key=lambda x: x[1]):
        title = x[1]

        if x[1] == 'B\xc3\xa9lgica': title = 'Bélgica'
        elif x[1] == 'Canad\xc3\xa1': title = 'Canadá'
        elif x[1] == 'Rep\xc3\xbablica Checa': title = 'República Checa'
        elif x[1] == 'Hungr\xc3\xada': title = 'Hungría'
        elif x[1] == 'Jap\xc3\xb3n': title = 'Japón'
        elif x[1] == 'M\xc3\xa9xico': title = 'México'
        elif x[1] == 'Pa\xc3\xadses Bajos': title = 'Países Bajos'
        elif x[1] == 'Panam\xc3\xa1': title = 'Panamá'
        elif x[1] == 'Per\xc3\xba': title = 'Perú'
        elif x[1] == 'Espa\xc3\xb1a': title = 'España'
        elif x[1] == 'Turqu\xc3\xada': title = 'Turquía'

        itemlist.append(item.clone( title = title, url = h_catalogue + '?country[]=' + x[0], action = 'list_all', text_color = 'moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="col-lg-2 col-md-3 col-6 mb-3">\s*<a(.*?)</a>\s*</div>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        title = scrapertools.find_single_match(article, '<div class="text-white[^"]*">([^<]+)</div>').strip()

        if not url or not title: continue

        if descartar_xxx and ('/coleccion-adulto-espanol/' in url or '/internacional-adultos/' in url): continue

        year = scrapertools.find_single_match(article, '<div class="txt-gray-200 txt-size-\d+">(\d+)</div>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        title = title.replace('&amp;', '&')

        SerieName = title

        title_alt = ''
        if item.group == 'pelis': title_alt = title

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentType='tvshow', contentSerieName=SerieName, infoLabels={'year': year}, contentTitleAlt = title_alt))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="page-item"><a href="([^"]+)" aria-label="(?:Netx|Next)"')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url = h_catalogue + next_page, action='list_all',  group = item.group, text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    epis = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if not item.page: item.page = 0

    perpage = 24

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Nuevos episodios<(.*?)>Nuevas series<')

    matches = scrapertools.find_multiple_matches(bloque, '<a class="media"(.*?)</a>')


    # ~ Reducir Matches
    i = 0

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)"')

        if not url: continue

        if descartar_xxx and ('/coleccion-adulto-espanol/' in url or '/internacional-adultos/' in url): continue

        if '/va-' in url: continue
        elif '/cocina-' in url: continue
        elif '/coches-' in url: continue
        elif '/motos-' in url: continue
        elif '/car-' in url: continue
        elif '/ebook-' in url: continue
        elif '/mp3tag-' in url: continue
        elif '/gadget-' in url: continue
        elif '/mastermix-' in url: continue
        elif '/computer-' in url: continue
        elif '/mega-' in url: continue
        elif '/cinemania-' in url: continue
        elif '/diez-' in url: continue
        elif '/lecturas-' in url: continue
        elif '/gran-' in url: continue
        elif '/various-' in url: continue
        elif '/muy-interesante-' in url: continue
        elif '/sport-' in url: continue
        elif '/bad-' in url: continue
        elif '/score-' in url: continue
        elif '/thickncurvy-' in url: continue
        elif '/bra-busters-' in url: continue
        elif '/reposteria-' in url: continue
        elif '/artistas-eternos-' in url: continue
        elif '/secretos-y-sabores-' in url: continue
        elif '/los-grandes-enigmas-del-mundo-' in url: continue
        elif '/mens-health-' in url: continue
        elif '/sucesos-de-la-historia-' in url: continue
        elif '/voluptuous-' in url: continue
        elif '/hustlers-taboo-' in url: continue
        elif '/tortillas-crepes-y-rebozados-' in url: continue
        elif '/mas-vegetales-menos-animales-' in url: continue
        elif '/hustler-usa-' in url: continue
        elif '/penthouse-usa-' in url: continue
        elif '/fhm-south-africa-' in url: continue
        elif '/pan-paso-a-paso-' in url: continue
        elif '/larousse-gastronomique-' in url: continue
        elif '/motociclismo-' in url: continue
        elif '/barely-legal-' in url: continue
        elif '/computadoras-que-aprenden-' in url: continue
        elif '/accion-cine-video-' in url: continue
        elif '/la-mitologia-templaria-' in url: continue
        elif 'rico-rico-y-con-fundamento-' in url: continue
        elif '/cocinar-sin-carbohidratos-' in url: continue
        elif '/chocolate-' in url: continue
        elif '/postres-' in url: continue
        elif '/freidora-de-aire-' in url: continue
        elif '/best-of-club-international-' in url: continue
        elif '/escort-readers-wives-' in url: continue
        elif '/anocero-' in url: continue
        elif '/hoy-me-comere-la-vida-' in url: continue
        elif '/razzle-extreme-' in url: continue
        elif '/naughty-neighbors-' in url: continue
        elif '/hobby-consolas-' in url: continue
        elif '/pizzas-' in url: continue
        elif '/best-of-men-only-' in url: continue
        elif '/mayfair-lingerie-' in url: continue

        elif '-pc-' in url: continue
        elif '-magazine-' in url: continue
        elif '-pack-' in url: continue
        elif '-cocina-' in url: continue
        elif '-recetas-' in url: continue
        elif '-motor-' in url: continue
        elif '-pdf-' in url: continue
        elif '-portable-' in url: continue
        elif '-flac-' in url: continue
        elif '-mp3-' in url: continue
        elif '-remix-' in url: continue
        elif '-dance-' in url: continue
        elif '-hits-' in url: continue
        elif '-photo-' in url: continue
        elif '-volume-' in url: continue
        elif 'audiolibrovoz-' in url: continue
        elif '-fotos-' in url: continue
        elif '-espana-' in url: continue
        elif '-national-geographic-' in url: continue
        elif '-mayfair-' in url: continue

        epis.append(match)

        i +=1


    matches = epis
    num_matches = i

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, ' href="([^"]+)"')

        title = scrapertools.find_single_match(match, ' title="([^"]+)"')
        title = title.replace(' Online sub español', '').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')

        title = title.replace('&amp;', '&')

        name = scrapertools.find_single_match(match, ' style="max-width.*?">(.*?)</div>')

        name = name.replace('&amp;', '&')

        if " - " in name: SerieName = name.split(" - ")[0]
        elif " ( " in name: SerieName = name.split(" ( ")[0]
        elif ": " in name: SerieName = name.split(": ")[0]
        elif " (" in name: SerieName = name.split(" (")[0]
        else: SerieName = name

        temp_epis = scrapertools.find_single_match(match, '</div><div>(.*?)</div>')

        season = scrapertools.find_single_match(temp_epis, '(.*?)x')
        episode = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentSerieName=SerieName,
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)


    # ~ Peliculas
    for new_item in itemlist:
        if new_item.infoLabels['season'] == 1 and new_item.infoLabels['episode'] == 1:
             if not new_item.infoLabels['tmdb_id']:
                 tmdb.set_infoLabels_item(new_item)

                 if not new_item.infoLabels['tmdb_id']:
                     new_item.contentType = 'movie'
                     new_item.contentTitle = new_item.title = new_item.contentSerieName
                     new_item.infoLabels['year'] = '-'

                     new_item.title = new_item.title + '[COLOR deepskyblue] Película[/COLOR]'

                     del new_item.contentSerieName
                     del new_item.contentSeason
                     del new_item.contentEpisodeNumber

                     del new_item.infoLabels['season']
                     del new_item.infoLabels['episode']
                     del new_item.infoLabels['tvshowtitle']

                     tmdb.set_infoLabels_item(new_item)


    if itemlist:
        if num_matches > ((item.page + 1) * perpage):
            itemlist.append(item.clone( title="Siguientes ...", action = "last_epis", page = item.page + 1, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    item_id = scrapertools.find_single_match(data, 'data-json=\'\{"item_id": "([^"]+)')

    post = 'item_id=%s' % item_id

    data = jsontools.load(do_downloadpage(host + 'api/web/seasons.php', post=post))

    # cuantas temporadas
    tot_temp = 0

    for tempo in data:
        tot_temp += 1
        if tot_temp > 1: break

    for tempo in data:
        title = 'Temporada %s' % tempo['number']

        numtempo = tempo['number']

        if tot_temp == 1:
            if not item.group == 'pelis':
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.id = item_id
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, item_id = item_id, contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    if not item.item_id:
        data = do_downloadpage(item.url)
        item.item_id = scrapertools.find_single_match(data, 'data-json=\'\{"item_id": "([^"]+)')

    post = 'item_id=%s&season_number=%s' % (item.item_id, item.contentSeason)

    data = jsontools.load(do_downloadpage(host + 'api/web/episodes.php', post=post))

    title_peli = ''
    if item.group == 'pelis':
        if len(data) == 1: title_peli = item.contentSerieName

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(data)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Dilo', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Dilo', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Dilo', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Dilo', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Dilo', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Dilo', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epi in data[item.page * item.perpage:]:
        titulo = '%sx%s %s' % (epi['season_number'], epi['number'], epi['name'])

        plot = epi['description']

        langs = re.findall('languajes/([^.]+).png', epi['audio'])

        if langs: titulo += ' [COLOR %s]%s[/COLOR]' % (color_lang, ', '.join([IDIOMAS.get(lang, lang) for lang in langs]))

        thumb = '' if 'picture' not in epi or not epi['picture'] else 'https://cdn.dilo.nu/resize/episode/220x125@' + epi['picture']

        if title_peli:
            titulo = title_peli
            thumb = item.thumbnail

        itemlist.append(item.clone( action='findvideos', url= host + epi['permalink'] + '/', title = titulo, plot = plot, thumbnail = thumb,
                                    contentType='episode', contentSeason=epi['season_number'], contentEpisodeNumber=epi['number'] ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(data) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<a href="#" class="[^"]*" data-link="([^"]+)".*?\?domain=([^."]+).*?/languajes/([^.]+).png'

    matches = re.compile(patron, re.DOTALL).findall(data)

    ses = 0

    for url, servidor, lang in matches:
        ses += 1

        if '/download?' in url:
            server = servertools.corregir_servidor(servidor)
            if server not in ['uptobox']: continue
        else:
            server = scrapertools.find_single_match(url, '/servers/([^.]+)')
            server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data, 'iframe class="" src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, 'a href="([^"]+)" target="_blank" class="player"')

    if not url:
        action = scrapertools.find_single_match(data, ' action="([^"]+)')
        token = scrapertools.find_single_match(data, ' name="token" value="([^"]+)')
        if action and token: url = host + action + '?token=' + token

    if host in url:
        url = do_downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')

    if url != '': 
        itemlist.append(item.clone(url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
