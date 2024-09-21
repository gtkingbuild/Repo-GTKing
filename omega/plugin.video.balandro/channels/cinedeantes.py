# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cinedeantes2.weebly.com'


perpage = 20
perpeli = 10


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Búsquedas:', action = '', folder=False, text_color='plum' ))
    itemlist.append(item.clone ( title = ' - Buscar película ...', action = 'search', grupo = 'alfab', search_type = 'movie', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = ' - Buscar en Seleccion cine ...', action = 'search', grupo = 'sel', search_type = 'movie', text_color='moccasin' ))
    itemlist.append(item.clone ( title = ' - Buscar por agrupación ...', action = 'search', grupo = 'agrupa', search_type = 'all', text_color='salmon' ))

    itemlist.append(item.clone ( title = 'Novedades', action = 'news' ))

    itemlist.append(item.clone ( title = 'Joyas del cine', action = 'list_all', url = host + '/joyas-del-cine.html', text_color = 'cyan' ))

    itemlist.append(item.clone ( title = 'Selección cine', action = 'list_sel', url = 'https://pastebin.com/raw/QW0A0mzx', text_color = 'moccasin' ))

    itemlist.append(item.clone ( title = 'Por agrupación (A - Z)', action = 'agrupa' , text_color='salmon'))

    itemlist.append(item.clone ( title = 'Por saga', action = 'pelis', grupo = 'sagas' ))
    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por categoría', action = 'pelis', grupo = 'temas' ))
    itemlist.append(item.clone ( title = 'Por interés', action = 'pelis',  grupo = 'desta' ))

    itemlist.append(item.clone ( title = 'Por actor', action = 'pelis', grupo = 'actor' ))
    itemlist.append(item.clone ( title = 'Por actriz', action = 'pelis', grupo = 'actri' ))
    itemlist.append(item.clone ( title = 'Por dirección', action = 'pelis', grupo = 'direc' ))

    itemlist.append(item.clone ( title = 'Por letra (A - Z)', action = 'alfab' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Artes marciales', action = 'list_all', url = host + '/artes-marciales.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Aventuras', action = 'pelis', filtro_search = 'AVENTURAS', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Bélicas (primera guerra)', action = 'list_all', url = host + '/primera-guerra.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Bélicas (guerra de corea)', action = 'list_all', url = host + '/guerra-corea.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Bélicas (guerra de vietnam)', action = 'list_all', url = host + '/vietnam.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Bélicas (acciones bélicas)', action = 'list_all', url = host + '/acciones-beacutelicas.html', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Cine alemán', action = 'list_all', url = host + '/cine-alemaacuten.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine argentino', action = 'list_all', url = host + '/cine-argentino.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine asiático', action = 'list_all', url = host + '/cine-asiaacutetico.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine británico', action = 'pelis', filtro_search = 'CINE BRIT&Aacute;NICO', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine clásico', action = 'pelis', filtro_search = 'CL&Aacute;SICO', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine de acción', action = 'pelis', filtro_search = 'CINE DE ACCI&Oacute;N', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine de romanos', action = 'list_all', url = host + '/cine-romanos.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine de terror', action = 'pelis', filtro_search = 'CINE DE TERROR', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine español', action = 'pelis', filtro_search = 'CINE ESPA&Ntilde;OL', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine europeo oriental', action = 'list_all', url = host + '/cine-europa-oriental.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine francés', action = 'pelis', filtro_search = 'CINE FRANC&Eacute;S', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine infantil', action = 'pelis', filtro_search = 'CINE INFANTIL', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine italiano', action = 'pelis', filtro_search = 'CINE ITALIANO', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine latino', action = 'list_all', url = host + '/cine-latino.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine mexicano', action = 'list_all', url = host + '/cine-mejicano.html', text_color = 'deepskyblue'))
    itemlist.append(item.clone ( title = 'Cine mudo', action = 'pelis', filtro_search = 'CINE MUDO', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine musical', action = 'pelis', filtro_search = 'MUSICAL', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine negro', action = 'pelis', filtro_search = 'CINE NEGRO', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cine religioso', action = 'list_all', url = host + '/cine-religioso.html', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Cien ruso', action = 'list_all', url = host + '/cine-ruso.html', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Comedias', action = 'pelis', filtro_search = 'COMEDIAS', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Ciencia ficción', action = 'pelis', filtro_search = 'CIENCIA-FICCI&Oacute;N', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Espionaje', action = 'pelis', filtro_search = 'ESPIONAJE', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Intriga', action = 'pelis', filtro_search = 'INTRIGA', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Peliculas Vose', action = 'pelis', filtro_search = 'PEL&Iacute;CULAS V.O.S.E.', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Peplum', action = 'pelis', filtro_search = 'PEPLUM', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Westerns', action = 'pelis', filtro_search = 'WESTERN', text_color = 'deepskyblue' ))

    return itemlist


def alfab(item):
    logger.info()
    itemlist = []

    for letra in '#abcdefghijklmnopqrstuvwxyz':
        if letra in '#abcdefghijk': url = host + '/iacutendice-de-peliacuteculas-a---k.html'
        else: url = host + '/iacutendice-de-peliacuteculas-l---z.html'

        itemlist.append(item.clone ( title = letra.upper(), url = url, action = 'list_letra', filtro_search = letra, text_color = 'deepskyblue' ))

    return itemlist


def agrupa(item):
    logger.info()
    itemlist = []

    for letra in '#abcdefghijklmnopqrstuvwxyz':
        itemlist.append(item.clone ( title = letra.upper(), action = 'pelis', filtro_search = letra, text_color='salmon' ))

    return itemlist


def news(item):
    logger.info()
    itemlist = []

    sort_news = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(host).data

    block_esp = scrapertools.find_single_match(data, '<h2 class="wsite-content-title"><font color=".*?especial(.*?)>NOVEDADES')
    block_nov = scrapertools.find_single_match(data, '>NOVEDADES(.*?)>ENLACE AL GRUPO LA TAQUILLA EN FACEBOOK')

    bloque = block_esp + block_nov

    slides = scrapertools.find_multiple_matches(bloque, '<div><div style="height:20px;overflow:hidden"></div>(.*?)<div style="height:20px;overflow:hidden"></div>')

    i = 0

    for slide in slides:
        matches = scrapertools.find_multiple_matches(str(slide), '{"url":(.*?)},')

        for match in matches:
            title = scrapertools.find_single_match(match, '"caption":"(.*?)"').strip()

            if not title: continue

            if 'novedades' in title.lower(): continue
            elif 'cuarentena' in title.lower(): continue

            if 'º' in title:
               if 'comedia ' in title.lower(): title =  title.replace('COMEDIA ', 'COMEDIAS ').replace('Comedia ', 'Comedias ')
            elif 'saga ' in title.lower():
              if 'AÑOS' in title: pass
              title =  title.replace('Saga ', '').replace('SAGA ', '')

            name = title

            title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ')
            title = title.lower()
            title = title.capitalize()

            thumb = scrapertools.find_single_match(match, '"(.*?)"')
            thumb = host + '/uploads/' + thumb

            i +=1

            sort_news.append([thumb, title, name])

    if not i == 0:
       num_matches = i -1
       desde = item.page * perpage
       hasta = desde + perpage

       sort_news = sorted(sort_news, key=lambda x: x[1])

       for thumb, title, name in sort_news[desde:hasta]:
           if name == 'SAGA': continue
           elif name == 'S A G A  AÑOS 80-90': continue
           elif 'V.O.S.E.' in name: continue
           elif '/VOSE' in name: continue
           elif 'CINE ASIÁTICO' in name: continue
           elif 'CIENCIA-FUCCIÓN' in name: continue
           elif 'CINE MUDO' in name: continue

           accion = 'pelis'
           url = host

           title = title.replace('º', 'ª').replace(' - ', ' ').replace(' -', ' ')

           if ' -' in name:
               if not name.endswith('º'): name = name + 'º'

               name = name.replace(' - ', ' ').replace(' -', ' ')

           if 'º' in name:
              grupo = 'temas'

              name = name.split('º')[0]

              if 'ACCIÓN' in name: name = name.replace('ACCIÓN', 'ACCI&Oacute;N')
              elif '-FICCIÓN' in name: name = name.replace('-FICCIÓN', '-FICCI&Oacute;N')
              elif 'BRITÁNICO' in name: name = name.replace('BRITÁNICO', 'BRIT&Aacute;NICO')
              elif 'ESPAÑOL' in name: name = name.replace('ESPAÑOL', 'ESPA&Ntilde;OL')
              elif 'FRANCÉS' in name: name = name.replace('FRANCÉS', 'FRANC&Eacute;S')
              elif 'CLÁSICO' in name: name = name.replace('CLÁSICO', 'CL&Aacute;SICO')
              elif 'BÉLICAS' in name: name = name.replace('BÉLICAS', 'B&Eacute;LICAS')
              elif 'AÑOS' in name: name = name.replace('AÑOS', 'A&Ntilde;OS')
              elif 'WESTERN SPAGHETTI 1' in name: name = name.replace('WESTERN SPAGHETTI 1', 'SPAGHETTI WESTERN 1')
              elif 'WESTERN SPAGHETTI 2' in name: name = name.replace('WESTERN SPAGHETTI 2', 'SPAGHETTI WESTERN 2')

           else:
              grupo = ''

              if name == 'AÑOS 80-90': name = name.replace('AÑOS 80-90', 'SAGAS A&Ntilde;OS 80 Y 90')
              elif name == 'años 80-90': name = name.replace('años 80-90', 'SAGAS A&Ntilde;OS 80 Y 90')

              elif name == 'Paco Martínez Soria': name = name.replace('Paco Martínez Soria', 'PACO MART&Iacute;NEZ SORIA')
              elif name == 'Sissi': name = name.replace('Sissi', 'SISSI')
              elif name == 'JOAN CROWFORD': name = name.replace('JOAN CROWFORD', 'JOAN CRAWFORD')
              elif name == 'HUMOR BOB HOPE (Camino a la utopía)': name = name.replace('HUMOR BOB HOPE (Camino a la utopía)', 'BOB HOPE (1903-2003)')
              elif name == 'HUMOR, BUSTER KEATON, CORTOS DEL AÑO 21': name = name.replace('HUMOR, BUSTER KEATON, CORTOS DEL AÑO 21', 'BUSTER KEATON')
              elif name == 'HUMOR CANTINFLAS': name = name.replace('HUMOR CANTINFLAS', 'CANTINFLAS')
              elif name == 'HUMOR LOUIS DE FUNES': name = name.replace('HUMOR LOUIS DE FUNES', 'LOUIS DE FUNES')
              elif name == 'LUÍS BUÑUEL': name = name.replace('LUÍS BUÑUEL', 'LU&Iacute;S BU&Ntilde;UEL (1900-1983)')

              elif name == 'CINE ALEMÁN':
                    accion = 'list_all'
                    url = host + '/cine-alemaacuten.html'
              elif name == 'CINE EUROPA ORIENTAL':
                    accion = 'list_all'
                    url = host + '/cine-europa-oriental.html'

           itemlist.append(item.clone( action = accion, title = title, url = url, thumbnail = thumb, grupo = grupo, filtro_search = name, page = 0, text_color='orchid' ))

       if itemlist:
           if i > perpage:
               if num_matches > hasta:
                  next_page = item.page + 1
                  itemlist.append(item.clone( title = 'Siguientes ...', page = next_page, action = 'news', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div id=".*?class="wcustomhtml".*?src="(.*?)"')

    cover = scrapertools.find_single_match(data, '<div><div class="wsite-image wsite-image-border-none ".*?<img src="([^"]+)"')
    if cover.startswith("/") == True: cover = host + cover

    num_matches = len(matches)
    desde = item.page * perpeli
    hasta = desde + perpeli

    order = 0

    for match in matches[desde:hasta]:
        if match.startswith('//') == True: url = 'https:' + match
        else: url = match

        data_thumb = httptools.downloadpage(url).data

        thumb = scrapertools.find_single_match(data_thumb, '<img src="([^"]+)"')
        thumb = thumb.replace('&amp;', '&')

        if not thumb: thumb = cover

        title = scrapertools.find_single_match(data_thumb, 'class="vid-card_n">(.*?)</span>')
        title = title.replace('(EEEE) p30', '').replace('(EEE) p20', '').replace('(EE)', '').replace('(C)', '').replace('(c)', '').strip()

        year = '-'

        try:
           name = title.split(" (")[0]
           year = title.split(" (")[1]

           if ')' in year: year = year.split(")")[0]
           elif '-' in year: year = year.split("-")[0]

           if year: title = name
        except:
            name = title

        if not title:
           order += 1
           title = '¿ Pelicula  ' + str(order) + ' ?'
        else:
           if title.endswith(") 0") == True: title = title.replace(' 0', '')
           elif title.endswith(") 1") == True: title = title.replace(' 1', '')
           elif title.endswith(") 2") == True: title = title.replace(' 2', '')
           elif title.endswith(") 3") == True: title = title.replace(' 3', '')
           elif title.endswith(") 4") == True: title = title.replace(' 4', '')
           elif title.endswith(") 5") == True: title = title.replace(' 5', '')
           elif title.endswith(") 6") == True: title = title.replace(' 6', '')
           elif title.endswith(") 7") == True: title = title.replace(' 7', '')
           elif title.endswith(") 8") == True: title = title.replace(' 8', '')
           elif title.endswith(") 9") == True: title = title.replace(' 9', '')

        lang = 'Esp'
        if ' vose' in title.lower() or ' v.o.s.e.' in title.lower(): lang = 'Vose'

        itemlist.append(item.clone( action='findvideos', url = url, title = title, language = lang, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = name, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if matches:
            if num_matches > hasta:
                next_page = item.page + 1

                itemlist.append(item.clone( title = 'Siguientes ...', page = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def list_letra(item):
    logger.info()
    itemlist = []

    if not item.desde: item.desde = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<div style="display:block;font-size(.*?)<div id="main-wrap">')

    matches = scrapertools.find_multiple_matches(bloque, '<h2 class="wsite-content-title"(.*?)</h2>')

    num_matches = len(matches)

    if not item.desde :
        for match in matches:
            item.desde = item.desde + 1

            match = match.replace('<font size="4"><em><u>', '').replace('</u></em></font>', '').replace('L<u style=""><em style="">', 'L')
            match = match.replace('<font size="3">', '').replace('<font size="4">', '').replace('</font>', '')
            match = match.replace('title=""><u><em>', '>').replace('</em></u>', '').strip()

            title = scrapertools.find_single_match(match, '.*?<a href=.*?>(.*?)<')

            if '<em style="">' in title: title = scrapertools.find_single_match(title, '<em style="">(.*?)<')
            elif '<em>' in title: title = scrapertools.find_single_match(title, '<em>(.*?)<')

            title = title.replace('&Aacute;', 'A').replace('&Eacute;', 'E').replace('&Iacute;', 'I').replace('&Oacute;', 'O').replace('&Uacute;', 'U')
            title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&iacute;', 'i').replace('&oacute;', 'o').replace('&uacute;', 'u').replace('&ntilde;', 'ñ')

            title = title.replace('&iquest;', '').replace('&iexcl;', '').replace('&#8203;', '').replace('&nbsp;', '').strip()

            letra = item.filtro_search.lower().strip()
            titulo = title.lower().strip()

            if item.title_search:
               if not item.title_search == title: continue

            try:
                letra_titulo = titulo[0]
                if not letra_titulo == letra:
                    if letra == '#':
                        if not letra_titulo in '0123456789': continue
                    else: continue
            except:
                continue

            item.desde = item.desde - 1
            break

    desde = item.desde
    hasta = desde + perpage

    for match in matches[desde:hasta]:
        match = match.replace('<font size="4"><em><u>', '').replace('</u></em></font>', '').replace('L<u style=""><em style="">', 'L')
        match = match.replace('<font size="3">', '').replace('<font size="4">', '').replace('</font>', '')
        match = match.replace('title=""><u><em>', '>').replace('</em></u>', '').strip()

        title = scrapertools.find_single_match(match, '.*?<a href=.*?>(.*?)<')

        if '<em style="">' in title: title = scrapertools.find_single_match(title, '<em style="">(.*?)<')
        elif '<em>' in title: title = scrapertools.find_single_match(title, '<em>(.*?)<')
        elif '<font size="4">' in title: title = scrapertools.find_single_match(title, '<font size="4">(.*?)<')

        title = title.replace('&Aacute;', 'A').replace('&Eacute;', 'E').replace('&Iacute;', 'I').replace('&Oacute;', 'O').replace('&Uacute;', 'U')
        title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&iacute;', 'i').replace('&oacute;', 'o').replace('&uacute;', 'u').replace('&ntilde;', 'ñ')

        title = title.replace('&iquest;', '').replace('&iexcl;', '').replace('&#8203;', '').replace('&nbsp;', '').strip()

        letra = item.filtro_search.lower().strip()
        titulo = title.lower().strip()

        try:
            letra_titulo = titulo[0]
            if not letra_titulo == letra:
                if letra == '#':
                    if not letra_titulo in '0123456789': continue
                else: continue
        except:
            continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        url = host + url

        lang = 'Esp'

        itemlist.append(item.clone( action='list_all', url = url, title = title, language = lang, filtro_search = '',
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if len(itemlist) == 20: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) == 20:
            itemlist.append(item.clone( title = 'Siguientes ...', desde = hasta, action = 'list_letra',
                                        filtro_search = item.filtro_search, text_color = 'coral' ))

        elif item.filtro_search.upper() == 'L':
            if title == 'Madame Curie':
                itemlist.append(item.clone( title = 'Siguientes ...', desde = 0,
                                            title_search = 'Los diablos de la guerra', action = 'list_letra',
                                            filtro_search = item.filtro_search, text_color = 'coral' ))

    return itemlist


def pelis(item):
    logger.info()
    itemlist = []

    sort_pelis = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<li id="active" class="wsite-menu-item-wrap">(.*?)</div><!-- end header-wrap -->')

    if item.grupo:
       if item.grupo == 'sagas': bloque = scrapertools.find_single_match(data, '/s-a-g-a-s.html(.*?)/c-i-c-l-o-s.html')
       elif item.grupo == 'actor': bloque = scrapertools.find_single_match(data, '/actores.html(.*?)/actrices.html')
       elif item.grupo == 'actri': bloque = scrapertools.find_single_match(data, '/actrices.html(.*?)/humor.html')
       elif item.grupo == 'direc': bloque = scrapertools.find_single_match(data, '/directores.html(.*?)/actores.html')
       elif item.grupo == 'desta': bloque = scrapertools.find_single_match(data, '/humor.html(.*?)</div><!-- end header-wrap -->')

    if item.filtro_search: matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</a>')
    else:
       if not item.grupo == 'temas': matches = scrapertools.find_multiple_matches(bloque, '<li id=(.*?)</li>')
       else: matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</a>')

    i = 0

    for match in matches:
        if '<span class="wsite-menu-arrow">' in match:
           if not 'SAGAS A&Ntilde;OS 80 Y 90' in match: continue

        if '<li id="wsite-nav-' in match:
           match = match + '</li>'
           match = scrapertools.find_single_match(match, '<li id="wsite-nav-(.*?)</li>')

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not url: continue

        title = scrapertools.find_single_match(match, 'class="wsite-menu-title">(.*?)</span>').strip()
        if not title: title = scrapertools.find_single_match(match, 'class="wsite-menu-item".*?>(.*?)</a>').strip()

        if item.filtro_search:
           if not title:
              if 'class="wsite-menu-item"' in match:
                 match_mod = match 
                 if not '</a>' in match_mod: match_mod = match_mod + '</a>'
                 title = scrapertools.find_single_match(match_mod, 'class="wsite-menu-item".*?>(.*?)</a>').strip()
                 if not title: title = scrapertools.find_single_match(match_mod, 'class="wsite-menu-item".*?>(.*?)</span>').strip()

        if not title: continue

        if title == 'Blog': continue
        elif title == 'C I C L O S': continue
        elif title == 'S A G A S': continue
        elif title == 'AVENTURAS': continue
        elif title == 'BÉLICAS': continue
        elif title == 'CIENCIA-FICCIÓN': continue
        elif title == 'CINE ALEMÁN': continue
        elif title == 'CINE BRITÁNICO': continue
        elif title == 'CINE DE ACCIÓN': continue
        elif title == 'CINE DE TERROR': continue
        elif title == 'CINE ESPAÑOL': continue
        elif title == 'CINE EUROPA ORIENTAL': continue
        elif title == 'CINE INFANTIL': continue
        elif title == 'CINE ITALIANO': continue
        elif title == 'CINE MUSICAL': continue
        elif title == 'CINE MUDO': continue
        elif title == 'CINE NEGRO': continue
        elif title == 'COMEDIAS': continue
        elif title == 'ESPIONAJE': continue
        elif title == 'HUMOR': continue
        elif title == 'INTRIGA': continue
        elif title == 'PELÍCULAS V.O.S.E.': continue
        elif title == 'PEPLUM': continue
        elif title == 'SEGUNDA GUERRA': continue
        elif title == 'SPAGHETTI WESTERN': continue
        elif title == 'WESTERNS': continue

        if not item.filtro_search:
            if title == 'ACCIONES B&Eacute;LICAS': continue

        url = host + url

        if 'WESTERN 6 ' in title: title = title.replace('WESTERN 6 ', 'WESTERN 6&ordm; ')
        elif title == 'A L I E N': title = title.replace('A L I E N', 'ALIEN')
        elif title == 'A S T E R I X': title = title.replace('A S T E R I X', 'ASTERIX')
        elif title == 'D R &Aacute; C U L A': title = title.replace('D R &Aacute; C U L A', 'DRACULA')
        elif title == 'P A S O L I N I': title = title.replace('P A S O L I N I', 'PASOLINI')
        elif title == 'R A M B O': title = title.replace('R A M B O', 'RAMBO')
        elif title == 'S A N D O K A N': title = title.replace('S A N D O K A N', 'SANDOKAN')
        elif title == 'S I M B A D': title = title.replace('S I M B A D', 'SIMBAD')
        elif title == 'S I S S I': title = title.replace('S I S S I', 'SISSI')
        elif title == 'T A R Z &Aacute; N': title = title.replace('T A R Z &Aacute; N', 'TARZAN')

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
           if not item.grupo == 'temas':
              if '&ordm;' in title: continue
           else:
              if not '&ordm;' in title: continue

        title = title.replace('&ordm;', 'ª').replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú')

        title = title.lower()
        title = title.capitalize()

        if 'Cine  de' in title: title = title.replace('Cine  de', 'Cine de')
        elif 'Pel&iacute;culas  v' in title: title = title.replace('Pel&iacute;culas  v', 'Pel&iacute;culas v')

        if item.grupo == 'desta':
           if title == '007 - james bond': continue
           elif title == 'Artes marciales': continue
           elif title == 'Aventuras': continue
           elif title == 'Primera guerra': continue
           elif title == 'Guerra corea': continue
           elif title == 'Vietnam': continue
           elif title == 'Acciones b&eacute;licas': continue
           elif title == 'Cine argentino': continue
           elif title == 'Cine asiático': continue
           elif title == 'Cine británico': continue
           elif title == 'Cine clásico': continue
           elif title == 'Cine de acción': continue
           elif title == 'Cine romanos': continue
           elif title == 'Cine de terror': continue
           elif title == 'Cine español': continue
           elif title == 'Cine francÉs': continue
           elif title == 'Cine infantil': continue
           elif title == 'Cine italiano': continue
           elif title == 'Cine latino': continue
           elif title == 'Cine mejicano': continue
           elif title == 'Cine mudo': continue
           elif title == 'Cine musical': continue
           elif title == 'Cine negro': continue
           elif title == 'Cine religioso': continue
           elif title == 'Cine ruso': continue
           elif title == 'Comedias': continue
           elif title == 'Ciencia ficción': continue
           elif title == 'Espionaje': continue
           elif title == 'Intriga': continue
           elif title == 'Joyas del cine': continue
           elif title == 'Peliculas v.o.s.e.': continue
           elif title == 'Peplum': continue
           elif title == 'Westerns': continue

        if item.filtro_search:
           if title == 'Artes marciales': continue
           elif title == 'Cine argentino': continue
           elif title == 'Cine asiático': continue
           elif title == 'Cine francÉs': continue
           elif title == 'Cine mejicano': continue
           elif title == 'Clásico': continue

        if 'ª' in title: title = title.replace('ª', 'ª - L')

        title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&iacute;', 'i').replace('&oacute;', 'o').replace('&uacute;', 'u').replace('&ntilde;', 'ñ')

        i +=1

        sort_pelis.append([url, title])

    if not i == 0:
       num_matches = i -1
       desde = item.page * perpage
       hasta = desde + perpage

       sort_pelis = sorted(sort_pelis, key = lambda x: x[1])

       for url, title in sort_pelis[desde:hasta]:
           if item.grupo == 'temas': text_color = 'deepskyblue'
           else: text_color = 'moccasin'

           itemlist.append(item.clone( action = 'list_all', title = title, url = url, page = 0, text_color = text_color ))

       if itemlist:
           if i > perpage:
               if num_matches > hasta:
                   next_page = item.page + 1
                   itemlist.append(item.clone( title = 'Siguientes ...', page = next_page, filtro_search = item.filtro_search, action = 'pelis',
                                               grupo = item.grupo, text_color='coral' ))

    return itemlist


#  viene del menu de Grupos
def categorias(item):
    logger.info()

    item.grupo = 'temas'
    return pelis(item)


def findvideos(item):
    logger.info()
    itemlist = []

    servidor = servertools.get_server_from_url(item.url)

    if servidor and servidor != 'directo':
       url = servertools.normalize_url(servidor, item.url)

       itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = item.language ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    url1 = host + '/iacutendice-de-peliacuteculas-a---k.html'
    data1 = httptools.downloadpage(url1).data
    bloque1 = scrapertools.find_single_match(data1, '<div style="display:block;font-size(.*?)<div id="main-wrap">')

    url2 = host + '/iacutendice-de-peliacuteculas-l---z.html'
    data2 = httptools.downloadpage(url2).data
    bloque2 = scrapertools.find_single_match(data2, '<div style="display:block;font-size(.*?)<div id="main-wrap">')

    bloques = bloque1 + bloque2

    matches = scrapertools.find_multiple_matches(bloques, '<h2 class="wsite-content-title"(.*?)</h2>')

    if matches:
        if config.get_setting('channels_charges_movies', default=True):
            platformtools.dialog_notification('CineDeAntes', '[COLOR blue]Cargando películas[/COLOR]')

    for match in matches:
        match = match.replace('<font size="4"><em><u>', '').replace('</u></em></font>', '').replace('L<u style=""><em style="">', 'L')
        match = match.replace('<font size="3">', '').replace('<font size="4">', '').replace('</font>', '')
        match = match.replace('title=""><u><em>', '>').replace('</em></u>', '').strip()

        title = scrapertools.find_single_match(match, '.*?<a href=.*?>(.*?)<')

        if '<em style="">' in title: title = scrapertools.find_single_match(title, '<em style="">(.*?)<')
        elif '<em>' in title: title = scrapertools.find_single_match(title, '<em>(.*?)<')
        elif '<font size="4">' in title: title = scrapertools.find_single_match(title, '<font size="4">(.*?)<')

        title = title.replace('&Aacute;', 'A').replace('&Eacute;', 'E').replace('&Iacute;', 'I').replace('&Oacute;', 'O').replace('&Uacute;', 'U')
        title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&iacute;', 'i').replace('&oacute;', 'o').replace('&uacute;', 'u').replace('&ntilde;', 'ñ')

        title = title.replace('&iquest;', '').replace('&iexcl;', '').replace('&#8203;', '').replace('&nbsp;', '').strip()

        title = title.replace('Á', 'A').replace('É', 'E').replace('Í', 'i').replace('Ó', 'o').replace('Ú', 'u').replace('Ñ', 'ñ')
        title = title.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

        titulo = title.lower().strip()

        if not item.title_search.lower() in titulo: continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        url = host + url

        lang = 'Esp'

        itemlist.append(item.clone( action='list_all', url = url, title = title, language = lang, filtro_search = '',
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if len(itemlist) > 100: break

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_sel(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = data.replace('"imageScale": "fitCenter"', '"url": ""').replace('"isHost" : "true"', '').replace('true', '"url": ""')

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(str(data), '"Cine Español 1980-1999"(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '"name": "(.*?)".*?"image": "(.*?)".*?"url": "(.*?)"')

    num_matches = len(matches)

    for title, thumb, url in matches[item.page * perpage:]:
        if not url or not title: continue

        if '.rtve.' in url: continue
        elif '.zerocdn.' in url: continue
        elif 'streamcloud.' in url: continue
        elif '.akamaized.' in url: continue
        elif 'pelis123.' in url: continue
        elif '/rtve' in url: continue
        elif '/openload' in url: continue

        if '|' in title: title = title.split("|")[0]

        PeliName = title

        if '(C)' in PeliName: PeliName = PeliName.split("(C)")[0]

        if 'Acción' in PeliName: PeliName = PeliName.split("Acción")[0]
        if 'Aventuras' in PeliName: PeliName = PeliName.split("Aventuras")[0]
        if 'Bigrafía' in PeliName: PeliName = PeliName.split("Bigrafía")[0]
        if 'Biopic' in PeliName: PeliName = PeliName.split("Biopic")[0]
        if 'Comedia' in PeliName: PeliName = PeliName.split("Comedia")[0]
        if 'Crimen' in PeliName: PeliName = PeliName.split("Crimen")[0]
        if 'Destape' in PeliName: PeliName = PeliName.split("Destape")[0]
        if 'Documental' in PeliName: PeliName = PeliName.split("Documental")[0]
        if 'Drama' in PeliName: PeliName = PeliName.split("Drama")[0]
        if 'Fantástico' in PeliName: PeliName = PeliName.split("Fantástico")[0]
        if 'Flameco' in PeliName: PeliName = PeliName.split("Flamenco")[0]
        if 'Intriga' in PeliName: PeliName = PeliName.split("Intriga")[0]
        if 'Misterio' in PeliName: PeliName = PeliName.split("Misterio")[0]
        if 'Musical' in PeliName: PeliName = PeliName.split("Musical")[0]
        if 'Política' in PeliName: PeliName = PeliName.split("Política")[0]
        if 'Romance' in PeliName: PeliName = PeliName.split("Romance")[0]
        if 'Terror' in PeliName: PeliName = PeliName.split("Terror")[0]
        if 'Thriller' in PeliName: PeliName = PeliName.split("Thriller")[0]
        if 'Sci-fi' in PeliName: PeliName = PeliName.split("Sci-fi")[0]
        if 'Suspense' in PeliName: PeliName = PeliName.split("Suspense")[0]
        if 'Suspenso' in PeliName: PeliName = PeliName.split("Suspenso")[0]
        if 'Vejez' in PeliName: PeliName = PeliName.split("Vejez")[0]

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year: year = scrapertools.find_single_match(title, ' \d{4} ')

        if year:
            title = title.replace('(' + year + ')', '').replace(year, '').strip()
            PeliName = PeliName.replace('(' + year + ')', '').replace(year, '').strip()
        else: year = '-'

        PeliName = PeliName.strip()

        thumb = thumb.replace('-mmed', '-large') + '|User-Agent=Mozilla/5.0'

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, language= 'Esp',
                                    contentType = 'movie', contentTitle = PeliName, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_sel', text_color='coral' ))

    return itemlist


def search_list_sel(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = data.replace('"imageScale": "fitCenter"', '"url": ""').replace('"isHost" : "true"', '').replace('true', '"url": ""')

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(str(data), '"Cine Español 1980-1999"(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '"name": "(.*?)".*?"image": "(.*?)".*?"url": "(.*?)"')

    for title, thumb, url in matches:
        if not url or not title: continue

        if '.rtve.' in url: continue
        elif '.zerocdn.' in url: continue
        elif 'streamcloud.' in url: continue
        elif '.akamaized.' in url: continue
        elif 'pelis123.' in url: continue
        elif '/rtve' in url: continue
        elif '/openload' in url: continue

        if not item.filtro_search_sel.lower() in title.lower(): continue

        if '|' in title: title = title.split("|")[0]

        PeliName = title

        if '(C)' in PeliName: PeliName = PeliName.split("(C)")[0]

        if 'Acción' in PeliName: PeliName = PeliName.split("Acción")[0]
        if 'Aventuras' in PeliName: PeliName = PeliName.split("Aventuras")[0]
        if 'Bigrafía' in PeliName: PeliName = PeliName.split("Bigrafía")[0]
        if 'Biopic' in PeliName: PeliName = PeliName.split("Biopic")[0]
        if 'Comedia' in PeliName: PeliName = PeliName.split("Comedia")[0]
        if 'Crimen' in PeliName: PeliName = PeliName.split("Crimen")[0]
        if 'Destape' in PeliName: PeliName = PeliName.split("Destape")[0]
        if 'Documental' in PeliName: PeliName = PeliName.split("Documental")[0]
        if 'Drama' in PeliName: PeliName = PeliName.split("Drama")[0]
        if 'Fantástico' in PeliName: PeliName = PeliName.split("Fantástico")[0]
        if 'Flameco' in PeliName: PeliName = PeliName.split("Flamenco")[0]
        if 'Intriga' in PeliName: PeliName = PeliName.split("Intriga")[0]
        if 'Misterio' in PeliName: PeliName = PeliName.split("Misterio")[0]
        if 'Musical' in PeliName: PeliName = PeliName.split("Musical")[0]
        if 'Política' in PeliName: PeliName = PeliName.split("Política")[0]
        if 'Romance' in PeliName: PeliName = PeliName.split("Romance")[0]
        if 'Terror' in PeliName: PeliName = PeliName.split("Terror")[0]
        if 'Thriller' in PeliName: PeliName = PeliName.split("Thriller")[0]
        if 'Sci-fi' in PeliName: PeliName = PeliName.split("Sci-fi")[0]
        if 'Suspense' in PeliName: PeliName = PeliName.split("Suspense")[0]
        if 'Suspenso' in PeliName: PeliName = PeliName.split("Suspenso")[0]
        if 'Vejez' in PeliName: PeliName = PeliName.split("Vejez")[0]

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year: year = scrapertools.find_single_match(title, ' \d{4} ')

        if year:
            title = title.replace('(' + year + ')', '').replace(year, '').strip()
            PeliName = PeliName.replace('(' + year + ')', '').replace(year, '').strip()
        else: year = '-'

        PeliName = PeliName.strip()

        thumb = thumb.replace('-mmed', '-large') + '|User-Agent=Mozilla/5.0'

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, language= 'Esp',
                                    contentType = 'movie', contentTitle = PeliName, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host

       if item.grupo == 'alfab':
            item.title_search = texto
            return list_search(item)

       elif item.grupo == 'sel':
            item.url = 'https://pastebin.com/raw/QW0A0mzx'

            item.filtro_search_sel = texto
            return search_list_sel(item)

       else:
            item.filtro_search = texto
            return pelis(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
