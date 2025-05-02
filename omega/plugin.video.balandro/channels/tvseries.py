# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


# ~ links_genres_series host = 'https://cinedeantes2.weebly.com'

host = 'https://seriestvdeantes'


perpage = 25


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    # ~ itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Series de [COLOR hotpink]Ciencia Ficción[/COLOR]', action = 'menu_series', url = host + '-02.weebly.com' ))

    itemlist.append(item.clone( title = 'Series de [COLOR hotpink]Comedias[/COLOR]', action = 'menu_series', url = host + '-05.weebly.com' ))

    itemlist.append(item.clone( title = 'Series de [COLOR hotpink]Dibujos Animados[/COLOR]', action = 'menu_series', url = host + '-06.weebly.com' ))

    itemlist.append(item.clone( title = 'Series de [COLOR hotpink]Detectives-Espionaje[/COLOR]', action = 'menu_series', url = host + '-04.weebly.com' ))

    itemlist.append(item.clone( title = 'Series [COLOR hotpink]Policiacas[/COLOR]', action = 'menu_series', url = host + '-03.weebly.com' ))

    itemlist.append(item.clone( title = 'Series de [COLOR hotpink]TVE, Mini Series y en Vose[/COLOR]', action = 'menu_series', url = host + '-07.weebly.com' ))

    itemlist.append(item.clone( title = 'Series [COLOR hotpink]Variadas[/COLOR]', action = 'menu_series', url = host + '-08.weebly.com' ))

    itemlist.append(item.clone( title = 'Series de [COLOR hotpink]Westerns[/COLOR]', action = 'menu_series', url = host + '-01.weebly.com' ))

    itemlist.append(item.clone( title = 'YouTube [COLOR hotpink]Animación[/COLOR] ', action = 'youtubes', thumbnail=config.get_thumb('youtube'), text_color = 'moccasin' ))

    itemlist.append(item.clone( title = 'YouTube [COLOR hotpink]Humor[/COLOR] ', action = 'youtubes2', thumbnail=config.get_thumb('youtube'), text_color = 'moccasin' ))

    return itemlist


def menu_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', url = item.url, search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'series', url = item.url, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Catálogo series con temporadas', action = 'series', url = item.url, grupo = 'seasons', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', url = item.url, search_type = 'tvshow' ))

    return itemlist


def youtubes(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    title = 'Alvin y las ardillas'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=5Vjg3ANC4DU&list=PLOsRHhzd4sScQJEGfperCQ1SrllmM0QoV', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Campeones oliver y benji'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=MhMxi5ShEks&list=PLtdTPPagpK29qTvIM49_ZvRIifiHpHf4q', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = "D'artacán y los tres mosqueperros"
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=k9YIjOL-KZU&list=PLpSWLIHTG6idwDXwIm-7eaCpauPBw0vGf', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Daniel el travieso'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=uL_E5wum6hI&list=PLrzXhAF3O2FOaRwEQblgHh0zyMZ6EcNPZ', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'David el gnomo'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=2dCUmOQfQ4E&list=PL6jgvKHZMaUX_JfZPZ_GCsHx1aSNmnIjo', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Dragones y mazmorras'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=VuaYo4KVRhY&list=PLsHZRFRhMph1o1qcw0MO71pPtnJrupuvy', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'El gato isidoro'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=2xUmmgPyrbg&list=PLyq8RHRc3jNjinn6pHFmIY6C3aRNunCOw', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'El libro de la selva'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=y1ynWnB9JpI&list=PLHfWUw8p_628MqyXvX4C9-QqviKJGOmS_', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Érase una vez el cuerpo humano'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=CtCQI8gP1HM&list=PL3trIOgZnbH1Xk_qpl2srL5wYlgd8Bu9f', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Fraguel rock'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=9mQ_Im0MBlg&list=PL7KciiA9T9EYwWlZbAxn5GksT2pn7wAYy', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'He-Man y los masters del universo'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=Stwkaqqtous&list=PLHVth4IGGf8uJ8WoenAucdukgFmzgWvmv', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Heidi'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=n5qQMnje_kU&list=PLUuRJYptYFXBmaLE1oNJYPxyl-3mSLKL3', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Inspector gadget'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=gTjd0VbDqNQ&list=PLQrG71R4T-nJ3aeMzWhP0U0Luy3USWdXN', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'La abeja maya'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=E-pKGTkcUkQ&list=PLYpTR-80tSP2dA3FsuEklQm_u4mtLoQdA', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'La vuelta al mundo en 80 días de willy fog'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=GJUnJcKjeyA&list=PL82F9AECFA0523F53', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Las aventuras de teddy ruxpin'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=fZPv0cdLSd0&list=PLvVLlsVj1Vgj1tBps9gIoDoT81RPVQU5A', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Las aventuras de tom sawyer'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=4VCilhIiQFM&list=PLYsIs7mU2MjMA_4OU7RZ0ulWFcrd2E5et', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Las tortugas ninjas'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=FPfaWD01ux0&list=PL5RvWvJcaVMyXET6HLQTPLHslCJofLrVR', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los cazafantasmas'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=bRDJRNXsThM&list=PLhcFeyCsqAAXXK2XS03ZnNZyE2YET8yl-', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los diminutos'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=lPHVQGZX54w&list=PLx5yOvA8qMRWVlvCjkWrJkAuzb9J-OVts', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los fruitis'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=7yoSgrvOf5o&list=PLdwgTWQaV-mj75-Xr3YuOM71ULjtubjRz', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los pequeños picapiedra'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=3xvmV327wNE&list=PLLhOnau-tupRZXJFjWGL-3ozRzp_Ax4-d', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los pitufos'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=PNKQQ_N6L8g&list=PLynb7MteT3bv-JXyQJFD0dgMX1p-kbTyw', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los osos amorosos'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=vE7gDUUmGG0&list=PLyq8RHRc3jNh2wu2N4eVT5z1RyRWrEkdn', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los teleñecos'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=LUjRXvicq4s&list=PLsNgeP_gZnvnNtuJzsP_eguYiBg1YWRJG', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Los trotamusicos'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=CLvxg1YH3zg&list=PLjGG4eB-AY7lLRIEZTftqW63JTe6jCg1W', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Lucky luke'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=oJk3rxJ3l10&list=PLpSWLIHTG6idKFhxc3tP14r04ZMNyrl47', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Marco'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=hBZyqA8pjXQ&list=PLutxf9xWvQKa0-ZMI5fyFSeABblPOF3Kk', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Mofli el último koala'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=4R-iGriuhLA&list=PLpSWLIHTG6idAf7gkOl7N92WnKu3iZqnt', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Popeye'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=DgQCJ8HPJCA&list=PLV0ww1Vq7oOxQs1VyZqMOzQuaclGbLRmD', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Rui el pequeño cid'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=4KY-WmxftUM&list=PL1812714DE488ECFC', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Sherlock holmes'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=2HDDvei0RSA&list=PL04gTKRCAl-Pc6AEz99h-lhC49Q6O2Pas', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Ulises 31'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url = 'https://www.youtube.com/watch?v=fns5R61QhhI&list=PL99kuo33pyKXVljP_1-9eSUrES6915Uk9', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def youtubes2(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    title = 'Benny Hill'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url =
    'https://www.youtube.com/watch?v=izKn-txodjA&list=PLVEyZctUi_RvVybY548yOPUZYc5NnEUIm', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'El Club de la Comedia'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url =
    'https://www.youtube.com/watch?v=apbUKEW1pbg&list=PL0451CE1EE0C1E5F4', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    title = 'Mr. Bean'
    itemlist.append(item.clone ( title = title, action = 'list_tubes', url =
    'https://www.youtube.com/watch?v=MxPvcpUI1cg&list=PLC1EDzqtkrh9Vqv7dOHN30tuIw2gyRWFf', contentSerieName = title, contentExtra='3', infoLabels = {'year': '-'}, text_color=text_color ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_tubes(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(str(data), '"playlist":.*?"playlist":.*?"title":(.*?)$')

    matches = scrapertools.find_multiple_matches(str(bloque), 'playlistPanelVideoRenderer":.*?simpleText":"(.*?)".*?"videoId":"(.*?)".*?"playlistId"')

    for title, _id in matches:
        if not _id or not title: continue

        thumb = 'https://i.ytimg.com/vi/' + _id + '/hqdefault.jpg'

        url = 'https://www.youtube.com/watch?v=' + _id

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb, contentExtra='tvseries', language = 'Esp' ))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    sort_series = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<li id="active" class="wsite-menu-item-wrap">(.*?)<a class="hamburger"')

    if not bloque: bloque = scrapertools.find_single_match(data, '<div class="dummy-nav">(.*?)<div class="hamburger')
    if not bloque: bloque = scrapertools.find_single_match(data, '<li id="active" class="wsite-menu-item-wrap">(.*?)<li id="active" class="wsite-menu-item-wrap">')

    if not item.grupo == 'seasons': matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</li>')
    else: matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</a>')

    i = 0

    for match in matches:
        if '<span class="wsite-menu-arrow">' in match: continue

        if '<li id="wsite-nav-' in match:
            match = match + '</li>'
            match = scrapertools.find_single_match(match, '<li id="wsite-nav-(.*?)</li>')

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not url: continue

        title = scrapertools.find_single_match(match, 'class="wsite-menu-title">(.*?)</span>').strip()
        if not title: title = scrapertools.find_single_match(match, 'class="wsite-menu-item".*?>(.*?)</a>').strip()

        if not title: continue

        url = item.url + url

        if item.filtro_search:
            buscado = item.filtro_search.lower().strip()
            titulo = title.lower().strip()

            if len(buscado) == 1:
                letra_titulo = titulo[0]
                if not letra_titulo == buscado:
                    if not buscado == '#': continue
                    if letra_titulo in '0123456789': pass
                    else: continue
            elif not buscado in titulo: continue
        else:
            if item.grupo == 'seasons':
                if not '&ordm;' in title: continue

        title = title.replace('&Aacute;', 'A').replace('&Eacute;', 'E').replace('&Iacute;', 'I').replace('&Oacute;', 'O').replace('&Uacute;', 'U').replace('&Ntilde;', 'Ñ')
        title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&Iicute;', 'i').replace('&oacute;', 'o').replace('&uacute;', 'u').replace('&ntilde;', 'ñ')
        title = title.replace('&acute;', "'")
		 
        title = title.replace('&iquest;', '').replace('&iexcl;', '').replace('&#8203;', '').replace('&nbsp;', '').strip()

        title = title.replace('&ordm;', 'ª').replace('))', ')').replace('Ó', 'ó').replace('Á', 'á').replace('Í', 'í').replace('Ñ', 'ñ')

        if title.startswith("á") == True: title = title.replace('á', 'a')

        title = title.lower()
        title = title.capitalize()

        if 'ª' in title: title = title.replace('ª', 'ª - T')

        year = ''

        try:
            name = title.split("(")[0]
            name = name.strip()

            if not item.grupo == 'seasons': year = title.split(" (")[1]

            year = year.replace(')', '')
            if '-' in year: year = year.split("-")[0]
        except:
            name = title

        if 'ª' in year: year = '-'
        elif not year == '-':
            if ('(' + year +')') in title:
                title = title.replace('(' + year + ')', '').strip()

        i +=1

        sort_series.append([url, title, name, year])

    if not i == 0:
        num_matches = i -1
        desde = item.page * perpage
        hasta = desde + perpage

        if num_matches < desde:
            hasta = desde
            desde = 0

        sort_series = sorted(sort_series, key=lambda x: x[1])

        for url, title, name, year in sort_series[desde:hasta]:
            itemlist.append(item.clone( action = 'list_all', title = title, url = url, contentType = 'tvshow', contentSerieName = name, infoLabels = {'year': year} ))

        tmdb.set_infoLabels(itemlist)

        if itemlist:
            if not item.filtro_search:
                if i > perpage:
                    if num_matches > hasta:
                        next_page = item.page + 1
                        itemlist.append(item.clone( title = 'Siguientes ...', page = next_page, action = 'series', text_color='coral' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div id=".*?class="wcustomhtml".*?src="(.*?)"')

    cover = scrapertools.find_single_match(data, '<div><div class="wsite-image wsite-image-border-none ".*?<img src="([^"]+)"')
    if cover.startswith("/") == True: cover = item.url + cover

    order = 0

    if matches:
        if config.get_setting('channels_charges', default=True):
            platformtools.dialog_notification('TvSeries', '[COLOR blue]Cargando episodios[/COLOR]')

    for match in matches:
        if match.startswith('//') == True: url = 'https:' + match
        else: url = match

        data_thumb = httptools.downloadpage(url).data

        thumb = scrapertools.find_single_match(data_thumb, '</div><img src="([^"]+)"')
        thumb = thumb.replace('&amp;', '&')

        if not thumb: thumb = cover

        title = scrapertools.find_single_match(data_thumb, 'class="vid-card_n">(.*?)</span>')
        title = title.replace('(EEEE) p30', '').replace('(EEE) p20', '').replace('(EE)', '').replace('(C)', '').replace('(c)', '').strip()

        invertir_temp_epis = True

        if not title:
            order += 1
            title = '¿ Episodio  ' + str(order) + ' ?'
        else:
            if title.endswith(") 0") == True:
                invertir_temp_epis = False
                title = title.replace(' 0', '')
            elif title.endswith(") 1") == True:
                invertir_temp_epis = False
                title = title.replace(' 1', '')
            elif title.endswith(") 2") == True:
                invertir_temp_epis = False
                title = title.replace(' 2', '')
            elif title.endswith(") 3") == True:
                invertir_temp_epis = False
                title = title.replace(' 3', '')
            elif title.endswith(") 4") == True:
                invertir_temp_epis = False
                title = title.replace(' 4', '')
            elif title.endswith(") 5") == True:
                invertir_temp_epis = False
                title = title.replace(' 5', '')
            elif title.endswith(") 6") == True:
                invertir_temp_epis = False
                title = title.replace(' 6', '')
            elif title.endswith(") 7") == True:
                invertir_temp_epis = False
                title = title.replace(' 7', '')
            elif title.endswith(") 8") == True:
                invertir_temp_epis = False
                title = title.replace(' 8', '')
            elif title.endswith(") 9") == True:
                invertir_temp_epis = False
                title = title.replace(' 9', '')

        lang = 'Esp'
        if ' Vose' in title or ' VOSE' in title or ' vose' in title or ' V.o.s.e.' in title or ' V.O.S.E.' in title or ' v.o.s.e.' in title: lang = 'Vose'

        temporada = 0
        capitulo = 0

        if not '"' in title:
            titulo = title.lower()
            titulo = titulo.replace('(', '"').replace(')', '"')

            if not invertir_temp_epis:
                temporada = scrapertools.find_single_match(titulo, '.*?"(.*?)x')
                capitulo = scrapertools.find_single_match(titulo, '.*?".*?x(.*?)"')
            else:
                temporada = scrapertools.find_single_match(titulo, '.*?".*?x(.*?)"')
                capitulo = scrapertools.find_single_match(titulo, '.*?"(.*?)x')

        if 'x' in temporada: temporada = temporada.replace('x', '').strip()
        if 'x' in capitulo: capitulo = capitulo.replace('x', '').strip()

        if not temporada: temporada = 0
        if not capitulo: capitulo = 0

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, language = lang, thumbnail = thumb,
                                    contentType='episode', contentSeason = temporada, contentEpisodeNumber = capitulo ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#abcdefghijklmnopqrstuvwxyz':
        itemlist.append(item.clone ( title = letra.upper(), url = item.url, action = 'series', filtro_search = letra, text_color = 'hotpink' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    servidor = servertools.get_server_from_url(item.url)
    servidor = servertools.corregir_servidor(servidor)

    if servidor:
        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = item.language, url = item.url ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.filtro_search = texto
        return series(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
