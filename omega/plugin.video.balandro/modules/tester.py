# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3: PY3 = True
else: PY3 = False


import os, re, time, xbmc, xbmcaddon

from platformcode import config, logger, platformtools, updater
from core import httptools, scrapertools, filetools, jsontools


LINUX = False
BR = False
BR2 = False

if PY3:
    try:
       import xbmc
       if xbmc.getCondVisibility("system.platform.Linux.RaspberryPi") or xbmc.getCondVisibility("System.Platform.Linux"): LINUX = True
    except: pass

try:
   if LINUX:
       try:
          from lib import balandroresolver2 as balandroresolver
          BR2 = True
       except: pass
   else:
       if PY3:
           from lib import balandroresolver
           BR = true
       else:
          try:
             from lib import balandroresolver2 as balandroresolver
             BR2 = True
          except: pass
except:
   try:
      from lib import balandroresolver2 as balandroresolver
      BR2 = True
   except: pass


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')

channels_unsatisfactory = config.get_setting('developer_test_channels', default='')
servers_unsatisfactory = config.get_setting('developer_test_servers', default='')


txt_provs = '[COLOR plum][B]Obtenga Nuevos Proxies desde[/B][/COLOR] [COLOR yellow][B]All-providers[/B][/COLOR], [COLOR yellow][B]Proxyscrape.com[/B][/COLOR], [COLOR yellow][B]Us-proxy.com[/B][/COLOR] ó los [COLOR magenta][B]Recomendados[/B][/COLOR][CR]'
txt_proxs = '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
txt_pnews = '[COLOR red][B]Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
txt_routs = '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'
txt_blocs = '[COLOR darkorange][B]Parece estar Bloqueado por su Operadora de Internet[/B][/COLOR][CR]'
txt_checs = '[COLOR tomato][B]Compruebe su Internet y/ó el Canal, a través de un Navegador Web[/B][/COLOR][CR]'
txt_coffs = '[COLOR gold][B]Puede Marcar el canal como Desactivado[/B][/COLOR][CR]'

txt_erase = '[COLOR orangered][B]Podrían Eliminarse los Proxies del Canal, pueden No necesitarse, salvo bloqueo en Play.[/B][/COLOR]'
txt_quita = '[COLOR orange][B]Se pueden Eliminar los Proxies del Canal, al parecer No se necesitan, excepto bloqueo[/COLOR] [COLOR fuchsia][B]Play[/B][/COLOR]'
txt_suspe = '[CR]account: [COLOR goldenrod][B]Suspendida[/B][/COLOR][CR]'
txt_sorry = '[CR]sorry: [COLOR springgreen][B]Contact your hosting Provider[/B][/COLOR]'
txt_false = '[COLOR springgreen][B]Falso Positivo.[/B][/COLOR][COLOR goldenrod][B] Parece que está redireccionando a otra Web.[/B][/COLOR]'
txt_verif = '[COLOR limegreen][B]Podría estar Correcto (verificar la Web vía internet)[/B][/COLOR]'

timeout = config.get_setting('httptools_timeout', default=15)

espera = config.get_setting('servers_waiting', default=6)


channels_poe = [
        ['gdrive', 'https://drive.google.com/drive/']
        ]

channels_despised = ['beeg', 'cuevana3in', 'hdfullse', 'pelispluscc', 'pelisplushdlat', 'playdo']

servers_poe = [ 'directo', 'm3u8hls', 'torrent' ]


def test_channel(channel_name):
    logger.info()

    channel_id = channel_name.lower()

    channel_json = channel_id + '.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       if not channel_name == 'test_providers':
           el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
           platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
           return

    if channel_name == 'test_providers':
       params = {'id': 'test_providers', 'name': 'TestProviders', 'thumbnail': '', 'active': True, 'searchable': False, 'search_types': ['all'], 'categories': ['all'], 'language': ['all'], 'clusters': ['inestable'], 'notes': 'Pruebas Puede requerir el uso de proxies en función del país/operadora desde el que se accede.'}

    if params['active'] == False:
        el_canal = ('[B][COLOR %s]' + channel_name) % color_avis
        if not 'temporary' in str(params['clusters']):
            platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
            return

    if channel_id == 'hdfull' or channel_id == 'nextdede' or channel_id == 'playdede':
        el_canal = ('[COLOR olivedrab][B]Cargando Info [/B][/COLOR][B][COLOR %s]' + channel_name) % color_infor
        platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    if config.get_setting('developer_mode', default=False): txt = '[COLOR moccasin][B]Internet:[/COLOR]  [COLOR yellow]Status Developer Mode[/B][/COLOR][CR][CR]'
    else: txt = test_internet()

    try: last_ver = updater.check_addon_version()
    except: last_ver = None

    if last_ver is None: last_ver = '[B][I][COLOR %s](sin acceso)[/COLOR][/I][/B]' % color_alert
    elif not last_ver: last_ver = '[B][I][COLOR %s](desfasada)[/COLOR][/I][/B]' % color_adver
    else: last_ver = ''

    last_fix = config.get_addon_version()

    txt += '[COLOR moccasin][B]Balandro:[/B][/COLOR] ' + config.get_addon_version().replace('.fix', '-Fix') + ' ' + last_ver + '[CR][CR]'

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'

    txt += 'id: ' + str(params['id']) + '[CR]'
    txt += 'channel: ' + str(params['name']) + '[CR]'
    txt += 'active: ' + str(params['active']) + '[CR]'

    search_types = str(params['search_types'])
    search_types = search_types.replace('[', '').replace(']', '').replace("'", '').strip()
    txt += 'search_types: ' + str(search_types) + '[CR]'

    categories = str(params['categories'])
    categories = categories.replace('[', '').replace(']', '').replace("'", '').strip()
    txt += 'categories: ' + str(categories) + '[CR]'

    if config.get_setting('developer_mode', default=False):
        txt += '[CR][COLOR moccasin][B]Desarrollo:[/B][/COLOR]'

        sets_clusters = str(params['clusters'])
        sets_clusters = sets_clusters.replace('[', '').replace(']', '').replace("'", '').strip()
        txt += '[CR]clusters: ' + sets_clusters

        sets_notes = str(params['notes'])
        txt += '[CR]notes: ' + sets_notes

        txt += '[CR]'

    txt += '[CR][COLOR moccasin][B]Contenidos:[/B][/COLOR][CR]'

    notes = str(params['notes'])

    if '+18' in notes: notes = notes.replace(' +18', '').strip()

    if 'Canal con enlaces Torrent exclusivamente.' in notes: notes = notes.replace('Canal con enlaces Torrent exclusivamente.', '').strip()

    if 'Canal con enlaces Streaming y Torrent.' in notes: notes = notes.replace('Canal con enlaces Streaming y Torrent.', '').strip()

    if 'Dispone de varios posibles dominios.' in notes: notes = notes.replace('Dispone de varios posibles dominios.', '').strip()

    if 'Puede requerir el uso de proxies' in notes: notes = scrapertools.find_single_match(str(notes), '(.*?)Puede requerir el uso de proxies').strip()

    txt += 'info: [COLOR yellow][B]' + str(notes) + '[/B][/COLOR][CR]'

    if 'temporary' in str(params['clusters']): txt += 'búsquedas: [COLOR red][B]False[/B][/COLOR][CR]'
    else: txt += 'búsquedas: [COLOR chartreuse][B]' + str(params['searchable']) + '[/B][/COLOR][CR]'

    language = str(params['language'])
    language = language.replace('[', '').replace(']', '').replace("'", '').strip()
    language = language.replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose').replace('vo', 'Vo')
    txt += 'idiomas: ' + str(language) + '[CR]'

    clusters = str(params['clusters'])
    clusters = clusters.replace('[', '').replace(']', '').replace("'", '').strip()

    if 'onlyone' in clusters: clusters = clusters.replace('onlyone,', '').strip()
    if 'suggested' in clusters: clusters = clusters.replace('suggested,', '').strip()
    if 'inestable' in clusters: clusters = clusters.replace('inestable,', '').strip()
    if 'problematic' in clusters: clusters = clusters.replace('problematic,', '').strip()
    if 'temporary' in clusters: clusters = clusters.replace('temporary,', '').strip()
    if 'mismatched' in clusters: clusters = clusters.replace('mismatched,', '').strip()
    if 'clons' in clusters: clusters = clusters.replace('clons,', '').strip()
    if 'register' in clusters: clusters = clusters.replace('register,', '').strip()
    if 'current' in clusters: clusters = clusters.replace('current,', '').strip()
    if 'torrents' in clusters: clusters = clusters.replace('torrents,', '').strip()
    if 'notice' in clusters: clusters = clusters.replace('notice,', '').strip()
    if 'languages' in clusters: clusters = clusters.replace('languages,', '').strip()

    if 'news' in clusters: clusters = clusters.replace('news,', '').strip()
    if 'news' in clusters: clusters = clusters.replace('news', '').strip()

    if 'lasts' in clusters: clusters = clusters.replace('lasts,', '').strip()
    if 'lasts' in clusters: clusters = clusters.replace('lasts', '').strip()

    if 'classic' in clusters: clusters = clusters.replace('classic,', '').strip()
    if 'classic' in clusters: clusters = clusters.replace('classic', '').strip()

    if 'rankings' in clusters: clusters = clusters.replace('rankings,', '').strip()
    if 'rankings' in clusters: clusters = clusters.replace('rankings', '').strip()

    if 'countries' in clusters: clusters = clusters.replace('countries,', '').strip()
    if 'countries' in clusters: clusters = clusters.replace('countries', '').strip()

    if 'qualityes' in clusters: clusters = clusters.replace('qualityes,', '').strip()
    if 'qualityes' in clusters: clusters = clusters.replace('qualityes', '').strip()

    if 'producers' in clusters: clusters = clusters.replace('producers,', '').strip()
    if 'producers' in clusters: clusters = clusters.replace('producers', '').strip()

    if 'years' in clusters: clusters = clusters.replace('years,', '').strip()
    if 'years' in clusters: clusters = clusters.replace('years', '').strip()

    if 'stars' in clusters: clusters = clusters.replace('stars,', '').strip()
    if 'stars' in clusters: clusters = clusters.replace('stars', '').strip()

    if 'directors' in clusters: clusters = clusters.replace('directors,', '').strip()
    if 'directors' in clusters: clusters = clusters.replace('directors', '').strip()

    if 'lists' in clusters: clusters = clusters.replace('lists,', '').strip()
    if 'lists' in clusters: clusters = clusters.replace('lists', '').strip()

    if 'categories' in clusters: clusters = clusters.replace('categories,', '').strip()
    if 'categories' in clusters: clusters = clusters.replace('categories', '').strip()

    if 'dorama' in clusters:
        if 'Web dedicada exclusivamente al dorama' in str(params['notes']):
           if 'dorama' in clusters: clusters = clusters.replace('dorama,', '').strip()
           if 'dorama' in clusters: clusters = clusters.replace('dorama', '').strip()

    if 'anime' in clusters:
        if not 'Web dedicada exclusivamente al anime' in str(params['notes']):
           if 'anime' in clusters: clusters = clusters.replace('anime,', '').strip()
           if 'anime' in clusters: clusters = clusters.replace('anime', '').strip()

    if 'adults' in clusters:
        if '+18' in str(params['notes']):
            if 'adults' in clusters: clusters = clusters.replace('adults,', '').strip()
            if 'adults' in clusters: clusters = clusters.replace('adults', '').strip()

    if 'tales' in clusters: clusters = clusters.replace('tales,', '').strip()
    if 'tales' in clusters: clusters = clusters.replace('tales', '').strip()

    if 'docs' in clusters: clusters = clusters.replace('docs,', '').strip()
    if 'docs' in clusters: clusters = clusters.replace('docs', '').strip()

    if 'kids' in clusters: clusters = clusters.replace('kids,', '').strip()
    if 'kids' in clusters: clusters = clusters.replace('kids', '').strip()

    if 'infantil' in clusters: clusters = clusters.replace('infantil,', '').strip()
    if 'infantil' in clusters: clusters = clusters.replace('infantil', '').strip()

    if 'vos' in clusters: clusters = clusters.replace('vos,', '').strip()
    if 'vos' in clusters: clusters = clusters.replace('vos', '').strip()

    if '4k' in clusters: clusters = clusters.replace('4k,', '').strip()
    if '4k' in clusters: clusters = clusters.replace('4k', '').strip()

    if '3d' in clusters: clusters = clusters.replace('3d,', '').strip()
    if '3d' in clusters: clusters = clusters.replace('3d', '').strip()

    if clusters: txt += 'grupos: ' + str(clusters) + '[CR]'

    txt_temas = ''

    if 'géneros' in str(params['notes']) or 'Géneros' in str(params['notes']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR thistle][B]Géneros[/B][/COLOR]'

    if 'languages' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR yellowgreen][B]Idiomas[/B][/COLOR]'

    if 'news' in str(params['clusters']) or 'lasts' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR darksalmon][B]Novedades[/B][/COLOR]'

    if 'classic' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR turquoise][B]Clásicos[/B][/COLOR]'

    if 'rankings' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR powderblue][B]Rankings[/B][/COLOR]'

    if 'countries' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR dodgerblue][B]Paises[/B][/COLOR]'

    if 'qualityes' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR moccasin][B]Calidades[/B][/COLOR]'

    if 'producers' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR teal][B]Productoras[/B][/COLOR]'

    if 'years'  in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR sienna][B]Años[/B][/COLOR]'

    if 'stars' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR magenta][B]Intérpretes[/B][/COLOR]'

    if 'directors' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR slateblue][B]Dirección[/B][/COLOR]'

    if 'lists' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR steelblue][B]Listas[/B][/COLOR]'

    if 'categories' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR violet][B]Categorías[/B][/COLOR]'

    if 'docs' in str(params['clusters']):
        if not str(params['categories']) == "['documentary']":
            if txt_temas: txt_temas += ', '
            txt_temas += '[COLOR cyan][B]Documentales[/B][/COLOR]'

    if 'kids' in str(params['clusters']) or 'infantil' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR lightyellow][B]Infantil[/B][/COLOR]'

    if 'tales' in str(params['clusters']):
        if not 'Web dedicada exclusivamente en Novelas' in str(params['notes']):
            if txt_temas: txt_temas += ', '
            txt_temas += '[COLOR limegreen][B]Novelas[/B][/COLOR]'

    if 'dorama' in str(params['clusters']):
        if not 'Web dedicada exclusivamente al dorama' in str(params['notes']):
            if txt_temas: txt_temas += ', '
            txt_temas += '[COLOR firebrick][B]Doramas[/B][/COLOR]'

    if 'anime' in str(params['clusters']):
        if not 'Web dedicada exclusivamente al anime' in str(params['notes']):
            if txt_temas: txt_temas += ', '
            txt_temas += '[COLOR springgreen][B]Animes[/B][/COLOR]'

    if 'vos' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR yellowgreen][B]VOS[/B][/COLOR]'

    if '4k' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR lightblue][B]4K[/B][/COLOR]'

    if '3d' in str(params['clusters']):
        if txt_temas: txt_temas += ', '
        txt_temas += '[COLOR powderblue][B]3D[/B][/COLOR]'

    if txt_temas: txt += 'temas: ' + txt_temas

    txt_diag = ''

    sets_categories = str(params['categories'])

    if sets_categories == "['movie']":
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'incluye: ' + '[COLOR deepskyblue][B]solo Películas[/B][/COLOR]'

    elif sets_categories == "['movie', 'torrent']":
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'incluye: ' + '[COLOR deepskyblue][B]solo Películas[/B][/COLOR]'

    elif sets_categories == "['tvshow']":
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'incluye: ' + '[COLOR hotpink][B]solo Series[/B][/COLOR]'

    elif sets_categories == "['documentary']":
        if not 'Películas' in str(params['notes']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'incluye: ' + '[COLOR cyan][B]solo Documentales[/B][/COLOR]'

    elif sets_categories == "['movie', 'adults']":
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'incluye: ' + '[COLOR orange][B]solo Vídeos[/B][/COLOR]'

    if 'Web dedicada exclusivamente al anime' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR springgreen][B]solo Animes[/B][/COLOR]'

    elif 'Web dedicada exclusivamente al dorama' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR firebrick][B]solo Doramas[/B][/COLOR]'

    elif 'Web dedicada exclusivamente en Novelas' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR limegreen][B]solo Novelas[/B][/COLOR]'

    elif 'Web dedicada exclusivamente a los tráilers' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR darkgoldenrod][B]solo Tráilers[/B][/COLOR]'

    if 'temporary' in str(params['clusters']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'estado: ' + '[COLOR plum][B]Temporalmente Inactivo[/B][/COLOR]'

    if not 'Temporalmente Inactivo' in txt_diag:
        if 'inestable' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'estado: ' + '[COLOR plum][B]Inestable[/B][/COLOR]'

        if 'problematic' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'servidores: ' + '[COLOR darkgoldenrod][B]Problemáticos[/B][/COLOR]'

        if 'mismatched' in str(params['clusters']):
            if not PY3:
                if txt_diag: txt_diag += '[CR]'
                txt_diag  += 'result: ' + '[COLOR violet][B]Posible MediaCenter Incompatibile (Sin Resultados) si versión anterior a 19.x[/B][/COLOR]'

        if 'clons' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'clones: ' + '[COLOR lightyellow][B]Varios Clones[/B][/COLOR]'

        if 'onlyone' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'play: ' + '[COLOR chocolate][B]un Único servidor[/B][/COLOR]'

            if not '+18' in str(params['notes']):
                if 'torrents' in str(params['clusters']):
                    cliente_torrent = config.get_setting('cliente_torrent', default='Seleccionar')

                    if cliente_torrent == 'Seleccionar' or cliente_torrent == 'Ninguno': tex_tor = cliente_torrent
                    else:
                       tex_tor = cliente_torrent
                       cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
                       if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent):
                          cod_version = xbmcaddon.Addon(cliente_torrent).getAddonInfo("version").strip()
                          tex_tor += '  [COLOR fuchsia]' + cod_version + '[/COLOR]'

                          if txt_diag: txt_diag += '[CR]'
                          txt_diag  += 'motor: ' + '[COLOR gold][B]' + tex_tor + '[/B][/COLOR]'
                else:
                    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'):
                        cod_version = xbmcaddon.Addon("plugin.video.youtube").getAddonInfo("version").strip()
                        tex_yt = '  [COLOR goldenrod]' + cod_version + '[/COLOR]'
                    else: tex_yt = '  [COLOR red]No instalado[/COLOR]'

                    if txt_diag: txt_diag += '[CR]'
                    txt_diag  += 'youtube: ' + '[COLOR gold][B]' + tex_yt + '[/B][/COLOR]'

        if 'suggested' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'canal: ' + '[COLOR aquamarine][B]Sugerido[/B][/COLOR]'

        cfg_status_channel = 'channel_' + channel_id + '_status'

        if str(config.get_setting(cfg_status_channel)) == '1':
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'marcado: ' + '[COLOR gold][B]Preferido[/B][/COLOR]'

        elif str(config.get_setting(cfg_status_channel)) == '-1':
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'marcado: ' + '[COLOR gray][B]Desactivado[/B][/COLOR]'

        if not params['searchable']:
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'buscar: ' + '[COLOR chartreuse][B]No Interviene[/B][/COLOR]'
        else:
            if str(params['search_types']) == "['documentary']":
                if txt_diag: txt_diag += '[CR]'
                txt_diag  += 'buscar: ' + '[COLOR yellow][B]solo Documental[/B][/COLOR]'

        if '+18' in str(params['notes']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'adultos: ' + '[COLOR orange][B]+18[/B][/COLOR]'

        if 'adults' in str(params['clusters']):
            if not '+18' in str(params['notes']):
                if txt_diag: txt_diag += '[CR]'
                txt_diag  += '+18: ' + '[COLOR orange][B]Puede tener enlaces para Adultos[/B][/COLOR]'

        if str(params['search_types']) == "['documentary']":
            if not 'Películas' in str(params['notes']):
                if not 'docs' in str(params['clusters']):
                    if txt_diag: txt_diag += '[CR]'
                    txt_diag  += 'contenido: ' + '[COLOR cyan][B]solo Documentales[/B][/COLOR]'

        if 'Canal con enlaces Torrent exclusivamente' in str(params['notes']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'enlaces: ' + '[COLOR blue][B]solo Torrents[/B][/COLOR]'

        if 'Canal con enlaces Streaming y Torrent' in str(params['notes']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'enlaces: ' + '[COLOR thistle][B]Streaming y Torrent[/B][/COLOR]'

        if 'register' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'

            username = config.get_setting(channel_id + '_username', channel_id, default='')
            if not username: txt_diag += 'cuenta: ' + '[COLOR green][B]Requiere registrarse[/B][/COLOR]'
            else: txt_diag += 'cuenta: ' + '[COLOR green][B]Credenciales informadas[/B][/COLOR]'

        if 'dominios' in str(params['notes']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'dominios: ' + '[COLOR lightyellow][B]Varios disponibles[/B][/COLOR]'

        if 'current' in str(params['clusters']):
            cfg_dominio_channel = 'channel_' + channel_id + '_dominio'
            if config.get_setting(cfg_dominio_channel, default=''):
                if txt_diag: txt_diag += '[CR]'
                txt_diag  += 'memorizado: ' + '[COLOR pink][B]' + config.get_setting(cfg_dominio_channel) + '[/B][/COLOR]'

            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'vigente: ' + '[COLOR darkorange][B]Puede comprobarse el Último Dominio[/B][/COLOR]'

        if 'Puede requerir el uso de proxies' in params['notes']:
            if txt_diag: txt_diag += '[CR]'
            txt_diag += 'bloqueo: ' + '[COLOR red][B]Puede requerir el uso de proxies en función del país/operadora desde el que se accede[/B][/COLOR]'

        if 'notice' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'aviso: ' + '[COLOR indianred][B] CloudFlare [/COLOR][COLOR orangered] Protection[/B][/COLOR]'

        if config.get_setting('search_included_all', default=''):
            if "'" + channel_id + "'" in str(config.get_setting('search_included_all')):
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'incluido: [COLOR yellow][B]Está asignado en búsquedas[/B][/COLOR]'

        if config.get_setting('search_excludes_movies', default=''):
            if "'" + channel_id + "'" in str(config.get_setting('search_excludes_movies')):
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'excluido: [COLOR deepskyblue][B]Búsquedas en Películas[/B][/COLOR]'

        if config.get_setting('search_excludes_tvshows', default=''):
            if "'" + channel_id + "'" in str(config.get_setting('search_excludes_tvshows')):
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'excluido: [COLOR hotpink][B]Búsquedas en Series[/B][/COLOR]'

        if config.get_setting('search_excludes_documentaries', default=''):
            if "'" + channel_id + "'" in str(config.get_setting('search_excludes_documentaries')):
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'excluido: [COLOR cyan][B]Búsquedas en Documentales[/B][/COLOR]'

        if config.get_setting('search_excludes_torrents', default=''):
            if "'" + channel_id + "'" in str(config.get_setting('search_excludes_torrents')):
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'excluido: [COLOR blue][B]Búsquedas en Torrents[/B][/COLOR]'

        if config.get_setting('search_excludes_mixed', default=''):
            if "'" + channel_id + "'" in str(config.get_setting('search_excludes_mixed')):
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'excluido: [COLOR yellow][B]Búsquedas en Películas y/ó Series[/B][/COLOR]'

        if config.get_setting('search_excludes_all', default=''):
            if "'" + channel_id + "'" in str(config.get_setting('search_excludes_all')):
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'excluido: [COLOR green][B]Búsquedas en Todos[/B][/COLOR]'

        if params['searchable']:
            cfg_searchable_channel = 'channel_' + channel_id + '_no_searchable'

            if config.get_setting(cfg_searchable_channel, default=False): txt_diag += '[CR]buscar: [COLOR violet][B]Excluido en Búsquedas[/B][/COLOR]'

    if config.get_setting('autoplay_channels_discarded', default=''):
        sin_autoplay = config.get_setting('autoplay_channels_discarded').split(',')

        for no_autoplay in sin_autoplay:
            no_autoplay = no_autoplay.lower().strip()

            if no_autoplay == channel_id:
                if txt_diag: txt_diag += '[CR]'
                txt_diag += 'Auto Play: [COLOR fuchsia][B]Excluido[/B][/COLOR]'
                break

    if txt_diag:
        if txt_temas: txt += '[CR]'

        txt += '[CR][COLOR moccasin][B]Diagnosis:[/B][/COLOR][CR]'
        txt += txt_diag

    if 'mismatched' in str(params['clusters']):
        from modules import helper

        txt_plat =  helper.get_plataforma('')

        if '(17.' in txt_plat or '(18.' in txt_plat:
            txt_plat = txt_plat.replace('[CR][CR]', '[CR]')
            txt += '[CR][CR]' + txt_plat

    channel_py = channel_id + '.py'
    filename_py = os.path.join(config.get_runtime_path(), 'channels', channel_py)

    dominio = config.get_setting('dominio', channel_id, default='')

    host = ''

    ant_hosts = ''

    channel_poe = "'" + channel_id + "'"
    esta_en_poe = False

    if channel_poe in str(channels_poe):
        for x in channels_poe:
            if x[0] == channel_id:
               esta_en_poe = True
               channel_poe = x[0]
               host = x[1]
               break

    if not esta_en_poe:
       channel_poe = ''

       if dominio: host = dominio
       else:
          if channel_id == 'playdede':
              el_canal = ('[COLOR cyan][B]Cargando espere ... [/B][/COLOR][B][COLOR %s]' + channel_name) % color_avis
              platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]', time=3000)

          try:
             data = filetools.read(filename_py)
          except:
             if not channel_name == 'test_providers':
                 el_canal = ('Falta [B][COLOR %s]' + channel_py) % color_alert
                 platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
                 return

          if channel_name == 'test_providers': data = ''

          if data == False:
             el_canal = ('Falta [B][COLOR %s]' + channel_py) % color_alert
             platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
             return

          part_py = 'def mainlist'

          if 'ver_stable_chrome' in data: part_py = 'ver_stable_chrome'

          elif 'CLONES =' in data or 'clones =' in data: part_py = 'clones  ='
          elif 'CLASS login_' in data or 'class login_' in data: part_py = 'class login_'

          elif 'def do_make_login_logout' in data: part_py = 'def do_make_login_logout'
          elif 'def login' in data: part_py = 'def login'
          elif 'def logout' in data: part_py = 'def logout'

          elif 'def configurar_proxies' in data: part_py = 'def configurar_proxies'
          elif 'def do_downloadpage' in data: part_py = 'def do_downloadpage'

          bloc = scrapertools.find_single_match(data.lower(), '(.*?)' + part_py)
          bloc = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', bloc)

          host = scrapertools.find_single_match(str(bloc), "host = '(.*?)'")
          if not host: host = scrapertools.find_single_match(str(bloc), 'host = "(.*?)"')

          if not host: host = scrapertools.find_single_match(str(bloc), "host.*?'(.*?)'")
          if not host: host = scrapertools.find_single_match(str(bloc), 'host.*?"(.*?)"')

          ant_hosts = scrapertools.find_single_match(str(bloc), 'ant_hosts.*?=.*?(.*?)]')
          if not ant_hosts: ant_hosts = scrapertools.find_single_match(str(bloc), "ant_hosts.*?=.*?(.*?)]")

    host = host.strip()

    if not host:
        if channel_name == 'test_providers': host = 'https://www.youtube.com/'

        if dominio: host = dominio

    if not host or not '//' in host:
        el_canal = ('Falta Dominio/Host/Clon/Metodo en [B][COLOR %s]' + channel_py) % color_alert
        platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
        return

    txt = info_channel(channel_name, channel_poe, host, dominio, txt, ant_hosts)

    if not 'code: [COLOR springgreen][B]200' in str(txt):
        if ant_hosts:
            tab_hosts = scrapertools.find_multiple_matches(ant_hosts, "'(.*?)'")
            if not tab_hosts: tab_hosts = scrapertools.find_multiple_matches(ant_hosts, '"(.*?)"')

            if tab_hosts:
                sort_hosts = []

                i = 0

                for ant_host in tab_hosts:
                    i +=1
                    sort_hosts.append((i, ant_host))

                tab_hosts = sorted(sort_hosts, key=lambda i: i[0], reverse=True)

                ant_hosts = tab_hosts

                txt += '[CR][CR][COLOR moccasin][B]Dominios Anteriores:[/B][/COLOR][CR]'

                for ant_host in ant_hosts:
                    txt += '[COLOR mediumaquamarine][B]' + ant_host[1] + '[/B][/COLOR][CR]'

    if config.get_setting('user_test_channel', default=''):
        if config.get_setting('user_test_channel') == 'host_channel': config.set_setting('user_test_channel', host)
        elif config.get_setting('user_test_channel') == 'localize': config.set_setting('user_test_channel', 'localized')
        return ''

    avis_causas = ''

    avisado = False

    if channel_id in str(channels_poe): pass

    elif channel_id in str(channels_despised):
        invalid = True

        for channel_depised in channels_despised:
            if not channel_id == channel_depised: continue

            invalid = False
            break

        if invalid:
            if '<p>Por causas ajenas a' in txt or '>Por causas ajenas a' in txt: avis_causas = txt_blocs.replace('[CR]', '')

            if not 'code: [COLOR springgreen][B]200' in txt:
                if not channels_unsatisfactory == 'unsatisfactory':
                    platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                    avisado = True

                else:
                    if 'Podría estar Correcto' in txt: pass
                    else:
                        platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')

                    avisado = True
            else:
                if not channels_unsatisfactory == 'unsatisfactory':
                    if 'invalid:' in txt:
                        platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                        avisado = True

                    elif 'Se pueden Eliminar los Proxies' in txt:
                        avis_causas = txt_erase
                        platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                        avisado = True

    else:
       if '<p>Por causas ajenas a' in txt or '>Por causas ajenas a' in txt: avis_causas = txt_blocs.replace('[CR]', '')

       if not 'code: [COLOR springgreen][B]200' in txt:
           if not channels_unsatisfactory == 'unsatisfactory':
               if '[COLOR limegreen][B]Podría estar Correcto (verificar la Web vía internet)[/B][/COLOR]' in txt:
                   avis_causas = txt_verif
                   platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                   avisado = True
               else:
                   if txt_sorry in txt or txt_suspe in txt: avis_causas = '[COLOR goldenrod][B]La Cuenta está Suspendida.[/B][/COLOR]'

                   platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                   avisado = True

           else:
               if 'Podría estar Correcto' in txt: pass
               else:
                   platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')

               avisado = True
       else:
           if not channels_unsatisfactory == 'unsatisfactory':
               if 'invalid:' in txt:
                   platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                   avisado = True

               elif 'Se pueden Eliminar los Proxies' in txt:
                   avis_causas = txt_erase
                   platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                   avisado = True

               elif 'Falso Positivo.' in txt:
                   avis_causas = txt_false
                   if txt_sorry in txt or txt_suspe in txt: avis_causas = '[COLOR goldenrod][B]La Cuenta está Suspendida.[/B][/COLOR]'

                   platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', avis_causas, '[COLOR cyan][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
                   avisado = True

    txt = txt.replace('[CR][CR][CR]', '[CR][CR]')

    if channels_unsatisfactory == 'unsatisfactory':
        if not avisado:
            if 'Se pueden Eliminar los Proxies' in txt: return txt
            elif 'Falso Positivo.' in txt: return txt
            elif 'invalid:' in txt: return txt
            return ''
        else:
            if 'Se pueden Eliminar los Proxies' in txt: return txt
            elif 'invalid:' in txt: return txt
            elif 'Podría estar Correcto' in txt: return ''
            else:
                platformtools.dialog_textviewer(channel_name.upper(), txt)
                return txt

    platformtools.dialog_textviewer(channel_name.upper(), txt)


def info_channel(channel_name, channel_poe, host, dominio, txt, ant_hosts):
    el_canal = ('Accediendo [B][COLOR %s]' + channel_name) % color_avis
    platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    channel_id = channel_name.lower()

    if dominio: txt_dominio = 'dominio'
    else: txt_dominio = ''

    response, txt = acces_channel(channel_name, host, txt_dominio, dominio, txt, ant_hosts, follow_redirects=False)

    if channel_id == channel_poe: return txt

    if response.sucess == False:
        if not '<urlopen error timed out>' in txt:
            if not 'Host error' in txt:
                if not 'Cloudflare' in txt:
                   if not 'Invisible Captcha' in txt:
                       if not 'Parece estar Bloqueado' in txt:
                           if not '<urlopen error' in txt:
                               if not 'timed out' in txt:
                                   if not 'getaddrinfo failed' in txt:
                                       if not 'Denegado' in txt:
                                           platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B][COLOR cyan] Redirect[/COLOR]')
                                           response, txt = acces_channel(channel_name, host, '', dominio, txt, ant_hosts, follow_redirects=True)

    if not dominio:
        dominio = config.get_setting('dominio', channel_id, default='')
        if dominio: response, txt = acces_channel(channel_name, host, txt_dominio, dominio, txt, ant_hosts, follow_redirects=False)

    return txt


def acces_channel(channel_name, host, txt_dominio, dominio, txt, ant_hosts, follow_redirects=None):
    el_canal = ('[COLOR mediumaquamarine]Testeando [B][COLOR %s]' + channel_name) % color_infor
    platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    channel_id = channel_name.lower()

    proxies = ''
    text_with_proxies = ''
    quitar_proxies = False

    cfg_proxies_channel = 'channel_' + channel_id + '_proxies'

    host_acces = host

    if channel_name.lower() == 'hdfull': host_acces = host_acces + 'login'

    # ~ 20/11/2023
    headers = {}

    if channel_id == 'playdo':
        host_acces = host_acces + 'api/search'
        useragent = httptools.get_user_agent()
        headers = {"User-Agent": useragent + " pddkit/2023"}

    if not config.get_setting(cfg_proxies_channel, default=''):
        response = httptools.downloadpage(host_acces, headers=headers, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)

        if 'Checking if the site connection is secure' in response.data:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR cyan][B]Requiere esperar %s segundos[/B][/COLOR]' % espera)
            time.sleep(int(espera))

            response = httptools.downloadpage(host_acces, headers=headers, follow_redirects=follow_redirects, timeout=timeout, raise_weberror=False, bypass_cloudflare=False)

        if '<title>You are being redirected...</title>' in response.data or '<title>Just a moment...</title>' in response.data:
            if BR or BR2:
                try:
                    ck_name, ck_value = balandroresolver.get_sucuri_cookie(response.data)
                    if ck_name and ck_value:
                        httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                        response = httptools.downloadpage(host_acces, headers=headers, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)
                except:
                    pass

        if not response.data:
            if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification(channel_name.capitalize(), '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

            timeout = config.get_setting('channels_repeat', default=30)

            response = httptools.downloadpage(host_acces, headers=headers, follow_redirects=follow_redirects, raise_weberror=False, timeout=timeout, bypass_cloudflare=False)

    else:
        response = httptools.downloadpage(host_acces, headers=headers, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)
        if response.sucess == True: quitar_proxies = True

        if 'Checking if the site connection is secure' in response.data:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR cyan][B]Requiere esperar %s segundos[/B][/COLOR]' % espera)
            time.sleep(int(espera))

            response = httptools.downloadpage(host_acces, headers=headers, follow_redirects=follow_redirects, timeout=timeout, raise_weberror=False, bypass_cloudflare=False)

        proxies = config.get_setting(cfg_proxies_channel, default='')

        if proxies:
            proxies = proxies.replace(' ', '')

            if ';' in proxies: proxies = proxies.replace(',', ';').split(';')
            else: proxies = proxies.split(',')

            platformtools.dialog_notification(config.__addon_name + '[COLOR red][B] con proxies[/B][/COLOR]', el_canal + '[/COLOR][/B]')

            if len(proxies) > 1:
                platformtools.dialog_notification(el_canal + '[/COLOR][/B]', '[COLOR orangered]Test con [B]' + str(len(proxies)) + '[/B] proxies ...[/COLOR]')
                time.sleep(1)

        response = httptools.downloadpage_proxy(channel_id, host_acces, headers=headers, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)

        if 'Checking if the site connection is secure' in response.data:
            platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR cyan][B]Requiere esperar %s segundos[/B][/COLOR]' % espera)
            time.sleep(int(espera))

            response = httptools.downloadpage_proxy(channel_id, host_acces, headers=headers, follow_redirects=follow_redirects, timeout=timeout, raise_weberror=False, bypass_cloudflare=False)

        if '<title>You are being redirected...</title>' in response.data or '<title>Just a moment...</title>' in response.data:
            if BR or BR2:
                try:
                    ck_name, ck_value = balandroresolver.get_sucuri_cookie(response.data)
                    if ck_name and ck_value:
                        httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                        response = httptools.downloadpage_proxy(channel_id, host_acces, headers=headers, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)
                except:
                    pass

        if not response.data:
            if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification(channel_name.capitalize(), '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

            timeout = config.get_setting('channels_repeat', default=30)

            response = httptools.downloadpage_proxy(channel_id, host_acces, headers=headers, follow_redirects=follow_redirects, raise_weberror=False, timeout=timeout, bypass_cloudflare=False)

        text_with_proxies = '[COLOR red] con proxies [/COLOR]'

    if proxies:
        if follow_redirects == False:
            txt += '[CR][CR][COLOR moccasin][B]Proxies: [/B][/COLOR][CR]'

            proxies = str(proxies)
            proxies = proxies.replace('[', '').replace(']', '').replace("'", '').strip()
            txt += 'actuales: ' + str(proxies)

            cfg_provider_channel = 'channel_' + channel_id + '_proxytools_provider'

            if config.get_setting(cfg_provider_channel): txt += '[CR]provider: [COLOR yellowgreen][B]' + config.get_setting(cfg_provider_channel) + '[/B][/COLOR]'
    else:
        if 'requerir el uso de proxies' in txt:
            txt += '[CR][CR][COLOR moccasin][B]Proxies: [/B][/COLOR][CR]'
            txt += 'actuales: [COLOR cyan][B]Sin proxies[/B][/COLOR]'
	
    if dominio: dominio = '[COLOR coral]' + dominio + '[/COLOR]'

    if follow_redirects == False: txt += '[CR][CR][COLOR moccasin][B]Acceso: ' + txt_dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'
    else: txt += '[CR][CR][COLOR moccasin][B]Redirect: ' + txt_dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'

    txt += 'host: [COLOR pink][B]' + host + '[/B][/COLOR][CR]'

    if headers: txt += 'Headers: [COLOR yellowgreen][B][CR]' + str(headers) + '[/B][/COLOR][CR]'

    if response.sucess == True: color_sucess = '[COLOR yellow][B]'
    else: color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    if str(response.code) == '200': color_code = '[COLOR springgreen][B]'
    else: color_code = '[COLOR orangered][B]'

    txt += 'code: ' + color_code + str(response.code) + '[/B][/COLOR][CR]'

    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'length: ' + str(len(response.data))

    if quitar_proxies: txt += '[CR]quitar: ' + txt_quita

    new_web = scrapertools.find_single_match(str(response.headers), "'location':.*?'(.*?)'")

    points = host.count('.')

    if points == 1: host_no_points = host.replace('https://', '').replace('http://', '').replace('/', '')
    else:
        tmp_host = host.split('.')[0]
        tmp_host = tmp_host + '.'
        host_no_points = host.replace(tmp_host, '').replace('/', '')
        host_no_points = host_no_points.replace('.', '')

    if response.sucess == False:
        if 'getaddrinfo failed' in str(response.code): txt += '[CR]domain: [COLOR darkgoldenrod][B]No se puede acceder a este sitio web.[/B][/COLOR][CR]'
        elif 'No address associated with hostname' in str(response.code): txt += '[CR]domain: [COLOR darkgoldenrod][B]Inaccesible no se puede acceder a este sitio.[/B][/COLOR][CR]'
        elif '| 502: Bad gateway</title>' in str(response.data): txt += '[CR][COLOR darkgoldenrod][B]Host error Bad Gateway[/B][/COLOR][CR]'

        elif '<urlopen error timed out>' in str(response.code) or '<urlopen error' in str(response.code):
             if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR]'

             if 'No se puede establecer una conexión' in str(response.code): txt += '[CR][COLOR darkgoldenrod][B]Host error NO responde[/B][/COLOR][CR]'
             else: txt += '[CR][COLOR darkgoldenrod][B]Tiempo máximo de acceso agotado.[/B][/COLOR][CR]'

             if 'actuales:' in txt:
                 if 'Sin proxies' in txt: txt += txt_proxs
                 else:
                    if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                    txt += txt_provs
             else:
                if config.get_setting(cfg_proxies_channel, default=''): txt += '[COLOR red][B]Obtenga nuevos proxies[/B][/COLOR][CR]'
                else: txt += '[COLOR orangered][B]Tiempo máximo de espera excedido.[/B][/COLOR][CR]'

                txt += txt_coffs
                txt += txt_checs
                txt += txt_routs

        else:
            if '| 502: Bad gateway</title>' in response.data or '| 522: Connection timed out</title>' in response.data: txt += '[CR]gate: [COLOR orangered][B]Host error[/B][/COLOR]'
            elif '<title>Attention Required! | Cloudflare</title>' in response.data: txt += '[CR]blocked: [COLOR orangered][B]Cloudflare[/B][/COLOR]'
            elif '<title>Just a moment...</title>' in response.data: txt += '[CR]blocked: [COLOR orangered][B]Cloudflare[/B][/COLOR][COLOR red][B] Protection[/B][/COLOR]'
            elif '/images/trace/captcha/nojs/h/transparent.' in response.data: txt += '[CR]captcha: [COLOR orangered][B]Invisible Captcha[/B][/COLOR]'
            elif '<title>Access Denied</title>' in response.data: txt += '[CR]acces: [COLOR orangered][B]Denegado[/B][/COLOR]'
            else:
               if len(response.data) > 0:
                   txt += '[CR]resp: [COLOR orangered][B]Unknow[/B][/COLOR][CR]'

                   if response.headers:
                       txt += '[CR][COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                       txt += str(response.headers) + '[CR]'

                   if len(response.data) < 1000:
                       response.data = str(response.data).strip()
                       if len(response.data) > 0:
                           txt += '[CR][COLOR moccasin][B]Datos:[/B][/COLOR][CR]'
                           txt += str(response.data).strip() + '[CR]'
    else:
        if  '<span class="error-description">Access denied</span>' in response.data: txt += '[CR]acces: [COLOR orangered][B]Denegado[/B][/COLOR]'
        elif ">The page you’re looking for could have been deleted or never have existed" in response.data: txt += '[CR]acces: [COLOR orangered][B]Web Sin Información [COLOR red]Borrada ó Inexistente[/B][/COLOR]'

        if len(response.data) >= 1000:
            if 'Estamos en mantenimiento, por favor inténtelo más tarde' in response.data: txt += '[CR]obras: [COLOR springgreen][B]Está en mantenimiento[/B][/COLOR]'
            elif '<h1>Index of /</h1>' in response.data: txt += '[CR]obras: [COLOR springgreen][B]Puede estar en mantenimiento[/B][/COLOR]'

            if new_web:
                if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                    if str(response.code) == '301' or str(response.code) == '308': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente[/B][/COLOR]"
                    elif str(response.code) == '302' or str(response.code) == '307': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal[/B][/COLOR]"
                    else: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio[/B][/COLOR]"

                txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                if new_web == host + 'inicio/' or new_web == host + 'principal/' or new_web == host + 'principal-b/' or new_web == host + 'nino' or new_web == host + '/es/' or new_web == host + '/login' or new_web == host + 'home/' or new_web == '/home' or new_web == host + 'novelas02' or new_web == host + 'zerotwo' or new_web == host + 'inicio' or new_web == host + 'hdpa' or new_web == host + 'novelaturca/' or (host + 'tv') in new_web or (host + 'hg') in new_web or (host + 'novelas') in new_web or (host + 'ennovelas') in new_web or '.ennovelas.' in new_web:
                    if 'Diagnosis:' in txt:
                        if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR]'

                    txt += '[CR]inicial: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'
                    new_web = ''

                    if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                        txt += "[CR]comprobar: [COLOR limegreen][B]Podría estar Correcto (verificar la Web vía internet)[/B][/COLOR]"

                if response.headers:
                    txt += '[CR][CR][COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                    txt += str(response.headers) + '[CR]'

            else:
                if not host in str(response.data):
                    no_http_host = host.replace('https://', '').replace('http://', '').strip()

                    if not no_http_host in str(response.data).lower():
                        if '<title>Bot Verification</title>' in response.data: txt += "[CR]robot: [COLOR indianred][B]CloudFlare[/B][/COLOR] [COLOR orangered][B]reCAPTCHA[/B][/COLOR]"
                        elif '<title>One moment, please...</title>' in response.data: txt += "[CR]robot: [COLOR indianred][B]CloudFlare[/B][/COLOR] [COLOR orangered][B]Protection[/B][/COLOR] [COLOR plum][B]Level 2[/B][/COLOR]"

                        invalid = True

                        tab_hosts = scrapertools.find_multiple_matches(ant_hosts, "'(.*?)'")
                        if not tab_hosts: tab_hosts = scrapertools.find_multiple_matches(ant_hosts, '"(.*?)"')

                        if tab_hosts:
                            ant_hosts = tab_hosts

                            for ant_host in ant_hosts:
                                if str(ant_host) in str(response.data).lower():
                                    invalid = False
                                    break

                                no_http_host = ant_host.replace('https://', '').replace('http://', '').strip()

                                if str(no_http_host) in str(response.data).lower():
                                    invalid = False
                                    break

                        if invalid:
                            if host.endswith('/'): no_http_host = host[:-1]
                            else: no_http_host = host

                            no_http_host = no_http_host.replace('https://', '').replace('http://', '').strip()
                            no_http_host = no_http_host.replace('www.', '').replace('www1.', '').strip()
                            no_http_host = no_http_host.replace('.mobi', '').strip()

                            if no_http_host in str(response.data).lower(): invalid = False

                        if invalid:
                            if channel_id in str(response.data).lower(): invalid = False

                        if invalid:
                            if channel_id in str(channels_despised):
                               for channel_depised in channels_despised:
                                   if not channel_id == channel_depised: continue

                                   invalid = False
                                   break

                        if invalid:
                            txt = txt.replace('[CR]quitar: ' + txt_quita, '[CR]quitar: [COLOR orangered][B]NO se pueden Eliminar los Proxies del Canal[/COLOR]')
                            txt += "[CR]invalid: [COLOR goldenrod][B]Acceso sin Host Válido en los datos.[/B][/COLOR]"

                elif channel_id in str(channels_despised):
                    if not 'Sugerencias:' in txt:
                        falso = False

                        for channel_depised in channels_despised:
                            if not channel_id == channel_depised: continue

                            falso = True
                            break

                        if falso:
                            if new_web:
                                txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR]'
                                txt += "[CR]comprobar: [COLOR yellow][B]Podría estar Correcto [/B][/COLOR][COLOR pink][B]el host:[/B][/COLOR] ó [COLOR limegreen][B]quizás ser un Nuevo Dominio (verificar la Web vía internet)[/B][/COLOR]"

        else:
            if len(response.data) < 1000:
                if not 'Diagnosis:' in txt: txt += '[CR][CR][COLOR moccasin][B]Diagnosis:[/B][/COLOR]'

                if '<title>Account Suspended</title>' in response.data: txt += '[CR]status: [COLOR goldenrod][B]Suspendida[/B][/COLOR]'
                elif 'The website is under maintenance' in response.data: txt += '[CR]obras: [COLOR springgreen][B]Está en mantenimiento[/B][/COLOR]'
                elif 'The server is temporarily busy' in response.data: txt += '[CR]obras: [COLOR springgreen][B]Está en mantenimiento[/B][/COLOR]'
                elif '/cgi-sys/defaultwebpage.cgi' in response.data: txt += txt_sorry
                elif '/www.alliance4creativity.com/' in new_web: txt += '[CR]legal: [COLOR springgreen][B]Copyright infringement[/B][/COLOR]'

                if new_web == '/login':
                    if 'Diagnosis:' in txt:
                        if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR]'

                    txt += '[CR]login: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'
                    new_web = ''

                    if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                        if 'dominios:' in txt: txt += "[CR]obtener: [COLOR yellow][B]Puede Obtener Otro Dominio desde Configurar Dominio a usar ...[/B][/COLOR]"

                        txt += "[CR]comprobar: [COLOR limegreen][B]Podría estar Correcto ó quizás ser un Nuevo Dominio (verificar la Web vía internet)[/B][/COLOR]"

                elif new_web == host + 'inicio/' or new_web == host + 'principal/' or new_web == host + 'principal-b/' or new_web == host + 'nino' or new_web == host + '/es/' or new_web == host + '/login' or new_web == host + 'home/' or new_web == host + 'home' or new_web == '/home' or new_web == host + 'novelas02' or new_web == host + 'zerotwo' or new_web == host + 'inicio' or new_web == host + 'hdpa' or new_web == host + 'novelaturca/' or (host + 'tv') in new_web or (host + 'hg') in new_web or (host + 'novelas') in new_web or (host + 'ennovelas') in new_web or '.ennovelas.' in new_web:
                    if 'Diagnosis:' in txt:
                        if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR]'

                    txt += '[CR]inicial: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'
                    new_web = ''

                    if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                        txt += "[CR]comprobar: [COLOR limegreen][B]Podría estar Correcto (verificar la Web vía internet)[/B][/COLOR]"

                if new_web:
                    if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'

                    else:
                       falso = False

                       if channel_id in str(channels_despised):
                           for channel_depised in channels_despised:
                               if not channel_id == channel_depised: continue

                               falso = True
                               break

                           if falso:
                               if not 'nuevo:' in txt: txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR][COLOR pink][B] (Falso)[/B][/COLOR]'
                               txt += "[CR]comprobar: [COLOR yellow][B]Podría estar Correcto [/B][/COLOR][COLOR pink][B]el host:[/B][/COLOR] ó [COLOR limegreen][B]quizás ser un Nuevo Dominio (verificar la Web vía internet)[/B][/COLOR]"
                       else:
                           if not 'nuevo:' in txt: txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                       if not falso:
                           if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                               if str(response.code) == '301' or str(response.code) == '308': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente[/B][/COLOR]"
                               elif str(response.code) == '302' or str(response.code) == '307': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal[/B][/COLOR]"
                               else: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio[/B][/COLOR]"

                               txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                               falso = False

                               if channel_id in str(channels_despised):
                                   for channel_depised in channels_despised:
                                       if not channel_id == channel_depised: continue

                                       falso = True
                                       break

                                   if falso:
                                       if not 'nuevo:' in txt: txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR][COLOR pink][B] (Falso)[/B][/COLOR]'
                                       txt += "[CR]comprobar: [COLOR yellow][B]Podría estar Correcto [/B][/COLOR][COLOR pink][B]el host:[/B][/COLOR] ó [COLOR limegreen][B]quizás ser un Nuevo Dominio (verificar la Web vía internet)[/B][/COLOR]"
                               else:
                                  if not 'nuevo:' in txt: txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                           else: txt += "[CR][CR][COLOR orangered][B]Comprobar Dominio[/B][/COLOR]"

                else:
                    if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'

            if 'status:' in txt:
                if '/cgi-sys/suspendedpage.cgi' in new_web: txt += txt_suspe
                else:
                   if not '<title>Account Suspended</title>' in response.data:
                       if not '>Hello world!<' in response.data: txt += '[CR]account: [COLOR goldenrod][B]Podría estar en Mantenimiento[/B][/COLOR]'

            if 'sorry:' in txt:
                if not 'account:' in txt:
                    if '/cgi-sys/defaultwebpage.cgi' in response.data: txt += txt_suspe
                    else:
                       if not '<title>Account Suspended</title>' in response.data:
                           if not '>Hello world!<' in response.data: txt += '[CR]account: [COLOR goldenrod][B]Podría estar en Mantenimiento[/B][/COLOR]'

            if not "'location': '/login'" in str(response.headers):
                if not 'status:'in txt:
                    txt += '[CR][CR][COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                    txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                if len(response.data) < 1000:
                    if not 'Sugerencias:' in txt:
                        if '<title>Account Suspended</title>' in response.data or '>Hello world!<' in response.data: txt += '[CR]'

                        txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                        if 'actuales:' in txt:
                            if 'Sin proxies' in txt: txt += txt_proxs
                            else:
                               if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                               txt += txt_provs

                        txt += txt_routs

                    txt += '[COLOR springgreen][B]Falso Positivo.[/B][/COLOR][COLOR goldenrod][B] Parece que está redireccionando a otra Web.[/B][/COLOR][CR]'

                if not '/cgi-sys/suspendedpage.cgi' or not '/wp-admin/install.php' in new_web:
                    txt += '[CR][CR][COLOR moccasin][B]Datos:[/B][/COLOR][CR]'
                    txt += str(response.data).strip() + '[CR]'


    if 'active: True' in txt:
        if 'Invisible Captcha' in txt or 'Obtenga nuevos proxies' in txt or 'Host error' in txt or 'No se puede establecer una' in txt or 'Cloudflare' in txt or 'Protection' in txt or 'Unknow' in txt or 'invalid:' in txt:
            if not 'Sugerencias:' in txt:
                if len(response.data) == 0: txt += '[CR]'
                elif len(response.data) > 1000: txt += '[CR]'

                elif 'code: [COLOR orangered][B]4' in txt: txt += '[CR]'
                elif 'invalid:' in txt: txt += '[CR]'

                if 'Invisible Captcha' in txt:
                    if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += txt_proxs
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                           txt += txt_provs

                    txt += txt_routs
 
                elif 'Obtenga nuevos proxies' in txt:
                    if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += txt_proxs
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                           txt += txt_provs

                    txt += txt_routs

                elif 'Host error' in txt:
                    if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                    txt += txt_coffs

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += txt_proxs
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                           txt += txt_provs

                    txt += txt_routs

                elif 'No se puede establecer una' in txt:
                    if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                    txt += 'conexión:[COLOR yellow][B]No se pudo establecer la conectividad[/B][/COLOR][CR]'

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += txt_proxs
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                           txt += txt_provs
                    else: txt += txt_checs

                    txt += txt_routs

                elif 'Cloudflare' in txt or 'Protection' in txt:
                    if not 'code: [COLOR springgreen][B]200' in str(txt):
                        if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                        if 'actuales:' in txt:
                            if 'Sin proxies' in txt: txt += txt_proxs
                            else:
                               if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                               txt += txt_provs

                        else: txt += txt_coffs

                        txt += txt_routs

                elif 'Unknow' in txt:
                    if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                    if '<p>Por causas ajenas a' in txt or '>Por causas ajenas a' in txt: txt += txt_blocs
                    else: txt += '[COLOR goldenrod][B]Puede estar en Mantenimiento[/B][/COLOR][CR]'

                    txt += txt_coffs

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += txt_proxs
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                           txt += txt_provs

                    txt += txt_routs

                elif '<p>Por causas ajenas a' in txt or '>Por causas ajenas a' in txt:
                    if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                    txt += txt_blocs

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += txt_proxs
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                           txt += txt_provs

                    txt += txt_routs

                else:
                    if not 'Sugerencias:' in txt: txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                    txt += txt_coffs
                    txt += txt_checs
                    txt += txt_routs

    if not 'Sugerencias:' in txt:
        if 'Suspendida' in txt:
            txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += '[COLOR goldenrod][B]Puede estar Renovando el Dominio o quizás estar en Mantenimiento[/B][/COLOR]'

        elif not host in response.data:
            host_in_data = host.replace('http://', '').replace('https://', '').replace('www.', '').replace('www1.', '')
            if host_in_data.endswith("/"): host_in_data = host_in_data[:-1]

            falso = True

            if channel_id in str(channels_despised):
                for channel_depised in channels_despised:
                    if not channel_id == channel_depised: continue

                    falso = False
                    break

            if falso:
                try: data_lower = str(response.data.lower())
                except: data_lower = str(response.data)

                if host_in_data in data_lower: falso = False
                elif channel_id in data_lower: falso = False

            if not falso:
                if 'window.location="' in response.data: falso = True

            if falso:
                if str(len(response.data)) == '0':
                    if new_web:
                        if host_no_points in new_web:
                            if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'
                            txt += '[COLOR springgreen][B]Nuevo Dominio[/B][/COLOR][CR]'

                    if not 'nuevo:' in txt:
                        if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                        if 'No se puede acceder a este sitio web' in txt or 'Inaccesible no se puede acceder a este sitio web' in txt: txt += '[COLOR olive][B]Inaccesible[/B][/COLOR][CR]'

                        txt += '[COLOR springgreen][B]Sin Información de Datos.[/B][/COLOR][CR]'
                else:
                    if '<p>Por causas ajenas a' in response.data or '>Por causas ajenas a' in response.data:
                       if not txt_blocs in txt:
                           if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'
                           txt += txt_blocs
                    else:
                       if new_web:
                           if not 'nuevo:' in txt:
                               if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                               if host_no_points in new_web: txt += '[COLOR springgreen][B]Nuevo Dominio[/B][/COLOR][CR]'
                               else: txt += '[COLOR springgreen][B]Falso Positivo.[/B][/COLOR][COLOR goldenrod][B] Parece que está redireccionando a otra Web.[/B][/COLOR][CR]'

                       elif 'window.location="' in response.data:
                          if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                          txt += '[COLOR springgreen][B]Falso Positivo.[/B][/COLOR][COLOR goldenrod][B] Parece que está redireccionando a otra Web.[/B][/COLOR][CR]'

                       if 'This site is being used for fraudulent purposes' in response.data:
                           if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'
                           txt += '[COLOR red][B]Atención [/COLOR][COLOR fuchsia]sitio Web con propósitos Fraudulentos.[/B][/COLOR][CR]'

                if 'Proxies:' in txt:
                    if 'actuales:' in txt:
                        if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                        if 'Sin proxies' in txt: txt += txt_proxs
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += txt_pnews
                           txt += txt_provs

                if not 'Headers:' in txt:
                    if response.sucess == False:
                       if response.headers:
                           txt += '[CR][CR][COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                           txt += str(response.headers) + '[CR]'

        elif response.sucess == False:
            if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += txt_coffs
            txt += txt_checs
            txt += txt_routs

    if config.get_setting('user_test_channel', default=''):
        if config.get_setting('user_test_channel') == 'localized': config.set_setting('user_test_channel', '')

        if 'Nuevo Dominio Permanente' in str(txt) or 'Nuevo Dominio Temporal' in str(txt):
            if new_web: config.set_setting('user_test_channel', new_web)

    return response, txt


def test_server(server_name):
    logger.info()

    server_id = server_name.lower()

    server_json = server_id + '.json'
    filename_json = os.path.join(config.get_runtime_path(), 'servers', server_json)

    try:
       data = filetools.read(filename_json)
       dict_server = jsontools.load(data)
    except:
       el_server = ('Falta [B][COLOR %s]' + server_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')
       return

    if dict_server['active'] == False:
        el_server = ('[B][COLOR %s]' + server_name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_server + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    if 'find_videos' in dict_server: dict_server['find_videos']['patterns'] = dict_server['find_videos'].get('patterns', list())
    else:
        el_server = ('[B][COLOR %s]' + server_name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_server + 'Falta [COLOR %s] find_videos [/COLOR][/B]' % color_alert)
        return

    if config.get_setting('developer_mode', default=False):
        txt = '[COLOR moccasin][B]Internet:[/COLOR]  [COLOR yellow]Status Developer Mode[/B][/COLOR][CR][CR]'
    else:
        txt = test_internet()

    try: last_ver = updater.check_addon_version()
    except: last_ver = None

    if last_ver is None: last_ver = '[B][I][COLOR %s](sin acceso)[/COLOR][/I][/B]' % color_alert
    elif not last_ver: last_ver = '[B][I][COLOR %s](desfasada)[/COLOR][/I][/B]' % color_adver
    else: last_ver = ''

    last_fix = config.get_addon_version()

    txt += '[COLOR moccasin][B]Balandro:[/B][/COLOR] ' + config.get_addon_version().replace('.fix', '-Fix') + ' ' + last_ver + '[CR][CR]'

    bloc = dict_server['find_videos']['patterns']

    servers = scrapertools.find_multiple_matches(str(bloc), '.*?"url".*?"(.*?)"')
    if not servers: servers = scrapertools.find_multiple_matches(str(bloc), ".*?'url'.*?'(.*?)'")

    if not servers:
        el_server = ('Falta url [B][COLOR %s]' + server_name) % color_alert
        platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')
        return

    url_servidor = ''

    server_poe = "'" + server_id + "'"
    esta_en_poe = False

    for url in servers:
        if server_poe in str(servers_poe):
           for x in servers_poe:
               if x == server_id:
                  esta_en_poe = True
                  server_poe = x
                  url_servidor = server_id
                  break

        if not esta_en_poe:
           server_poe = ''

           try:
              type = url.split('/')[0].strip()
              servidor = url.split('/')[2].strip()

              if type:
                  if servidor: url_servidor = type + '//' + servidor + '/'
           except:
              url_servidor = url

        continue

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'

    txt += 'server: ' + server_name + '[CR][CR]'

    try:
       patterns = dict_server['find_videos']['patterns']

       for pattern in patterns:
           tab_pat = scrapertools.find_single_match(str(pattern), "'pattern': '(.*?)'").strip()
           url_pat = scrapertools.find_single_match(str(pattern), "'url': '(.*?)'").strip()

           if not tab_pat or not url_pat: continue

           txt += 'patron: ' + str(tab_pat) + '[CR]'
           txt += 'urlpat: ' + str(url_pat) + '[CR][CR]'
    except:
       txt += 'patrones: ' + str(bloc) + '[CR][CR]'

    txt_diag = ''

    try:
       notes = dict_server['notes']
    except: 
       notes = ''

    if 'Alternative' in notes:
        notes = notes.replace('Alternative vía:', '').strip()
        txt_diag  += 'alternativas: ' + '[COLOR plum][B]' + str(notes) + '[/B][/COLOR][CR]'
    else:
        if notes: txt_diag  += 'notes: ' + '[COLOR plum][B]' + str(notes) + '[/B][/COLOR][CR]'

    try:
       more_ids = dict_server['more_ids']
    except: 
       more_ids = ''

    if more_ids: txt_diag  += 'more ids: ' + '[COLOR gold][B]' + str(more_ids) + '[/B][/COLOR][CR]'

    try:
       ignore_urls = dict_server['ignore_urls']
    except: 
       ignore_urls = ''

    if ignore_urls: txt_diag  += 'more ids: ' + '[COLOR coral][B]' + str(ignore_urls) + '[/B][/COLOR][CR]'

    if txt_diag:
        txt += '[COLOR moccasin][B]Diagnosis:[/B][/COLOR][CR]'
        txt += txt_diag
    else:
        txt += '[CR][COLOR moccasin][B]Diagnosis:[/B][/COLOR][CR]'

    if url_servidor == '': url_servidor = 'Indefinido'
    elif '\\' in url_servidor: url_servidor = 'Variable'

    if not url_servidor: txt += 'url: [COLOR red][B] Falta [/B][/COLOR][CR]'
    else:
       txt += 'url: ' + url_servidor
       txt = info_server(server_name, server_poe, url_servidor, txt)

    avisado = False

    if 'Variable' in txt or 'Indefinido' in txt: pass
    elif server_id in str(servers_poe): pass
    else:
       if not 'code: [COLOR springgreen][B]200' in txt:
           platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + server_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Servidor NO ha resultado Satisfactorio.[/I][/B][/COLOR]', '[COLOR cyan][B]Por favor, compruebe la información del Test del Servidor.[/B][/COLOR]')
           avisado = True

    txt = txt.replace('[CR][CR][CR]', '[CR][CR]')

    if servers_unsatisfactory == 'unsatisfactory':
        if not avisado: return ''
        else:
           platformtools.dialog_textviewer(server_name.upper(), txt)
           return txt

    platformtools.dialog_textviewer(server_name.upper(), txt)


def info_server(server_name, server_poe, url, txt):
    el_server = ('Accediendo [B][COLOR %s]' + server_name) % color_infor
    platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')

    server_id = server_name.lower()

    if server_id == server_poe: return txt
    elif url == 'Indefinido': return txt
    elif url == 'Variable': return txt

    response, txt = acces_server(server_name, url, txt, follow_redirects=False)

    if response.sucess == False:
        if not '<urlopen error timed out>' in txt:
            if not 'Host error' in txt:
                if not 'Cloudflare' in txt:
                   if not 'Invisible Captcha' in txt:
                       if not '<urlopen error' in txt:
                           if not 'timed out' in txt:
                               if not 'getaddrinfo failed' in txt:
                                   if not 'Denegado' in txt:
                                       platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B][COLOR cyan] Redirect[/COLOR]')
                                       response, txt = acces_server(server_name, url, txt, follow_redirects=True)

    return txt


def acces_server(server_name, url, txt, follow_redirects=None):
    el_server = ('[COLOR mediumaquamarine]Testeando [B][COLOR %s]' + server_name) % color_avis
    platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')

    server_id = server_name.lower()

    if '\\1/\\2' in url: url = url.replace('\\1/\\2', '')
    elif '\\1.\\2' in url: url = url.replace('\\1.\\2', '')
    elif '/embed-\\1.html' in url: url = url.replace('/embed-\\1.html', '/')
    elif '/player.php?id=\\1' in url: url = url.replace('/player.php?id=\\1', '/')
    elif '/embed/\\1' in url: url = url.replace('/embed/\\1', '/')
    elif '/vidembed-\\1' in url: url = url.replace('/vidembed-\\1', '/')
    elif '/play/\\1' in url: url = url.replace('/play/\\1', '/')
    elif '/public/dist/asteroid.html?id=\\1' in url: url = url.replace('/public/dist/asteroid.html?id=\\1', '/')
    elif '\\1' in url: url = url.replace('\\1', '')

    if '/s/' in url: url = url.replace('/s/', '/')
    elif '/e/' in url: url = url.replace('/e/', '/')
    elif '/v/' in url: url = url.replace('/v/', '/')
    elif '/api/source/\\1' in url: url = url.replace('/api/source/\\1', '/')
    elif '/embed/' in url: url = url.replace('/embed/', '/')

    response = httptools.downloadpage(url, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)

    if follow_redirects == False: txt += '[CR][CR][COLOR moccasin][B]Acceso: [/B][/COLOR][CR]'
    else: txt += '[CR][CR][COLOR moccasin][B]Redirect: [/B][/COLOR][CR]'

    txt += 'host: [COLOR pink][B]' + url + '[/B][/COLOR][CR]'

    if response.sucess == True: color_sucess = '[COLOR yellow][B]'
    else: color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    if str(response.code) == '200': color_code = '[COLOR springgreen][B]'
    else: color_code = '[COLOR orangered][B]'

    txt += 'code: ' + color_code  + str(response.code) + '[/B][/COLOR][CR]'

    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'length: ' + str(len(response.data))

    new_web = scrapertools.find_single_match(str(response.headers), "'location':.*?'(.*?)'")

    if response.sucess == False:
        if 'getaddrinfo failed' in str(response.code): txt += '[CR]domain: [COLOR darkgoldenrod][B]No se puede acceder a este sitio web.[/B][/COLOR][CR]'
        elif 'No address associated with hostname' in str(response.code): txt += '[CR]domain: [COLOR darkgoldenrod][B]Inaccesible no se puede acceder a este sitio.[/B][/COLOR][CR]'
        elif '| 502: Bad gateway</title>' in str(response.data): txt += '[COLOR darkgoldenrod][B]Host error Bad Gateway[/B][/COLOR][CR]'

        elif '<urlopen error timed out>' in str(response.code) or '<urlopen error' in str(response.code):
             if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

             if 'No se puede establecer una conexión' in str(response.code): txt += '[COLOR darkgoldenrod][B]Host error NO responde[/B][/COLOR][CR]'
             else: txt += '[COLOR darkgoldenrod][B]Tiempo máximo de acceso agotado.[/B][/COLOR][CR]'

             txt += txt_coffs
             txt += txt_checs
             txt += txt_routs

        else:
            if '| 502: Bad gateway</title>' in response.data or '| 522: Connection timed out</title>' in response.data: txt += '[CR]gate: [COLOR orangered][B]Host error[/B][/COLOR]'
            elif '<title>Attention Required! | Cloudflare</title>' in response.data: txt += '[CR]blocked: [COLOR orangered][B]Cloudflare[/B][/COLOR]'
            elif '<title>Just a moment...</title>' in response.data: txt += '[CR]blocked: [COLOR orangered][B]Cloudflare[/B][/COLOR][COLOR red][B] Protection[/B][/COLOR]'
            elif '/images/trace/captcha/nojs/h/transparent.' in response.data: txt += '[CR]captcha: [COLOR orangered][B]Invisible Captcha[/B][/COLOR]'
            elif '<title>Access Denied</title>' in response.data: txt += '[CR]acces: [COLOR orangered][B]Denegado[/B][/COLOR]'
            else:
               if len(response.data) > 0:
                   txt += '[CR]resp: [COLOR orangered][B]Unknow[/B][/COLOR][CR]'

                   if response.headers:
                       txt += '[CR][COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                       txt += str(response.headers) + '[CR]'

                   if len(response.data) < 1000:
                       response.data = str(response.data).strip()
                       if len(response.data) > 0:
                           txt += '[CR][COLOR moccasin][B]Datos:[/B][/COLOR][CR]'
                           txt += str(response.data).strip() + '[CR]'
    else:
        if  '<span class="error-description">Access denied</span>' in response.data: txt += '[CR]acces: [COLOR orangered][B]Denegado[/B][/COLOR]'
        elif ">The page you’re looking for could have been deleted or never have existed" in response.data: txt += '[CR]acces: [COLOR orangered][B]Web Sin Información [COLOR red]Borrada ó Inexistente[/B][/COLOR]'

        if len(response.data) >= 1000:
            if new_web == '?op=login':
                if 'Diagnosis:' in txt:
                    if not 'Sugerencias:' in txt: txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR]'

                txt += '[CR]login: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'
                new_web = ''

                if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                    txt += "[CR]comprobar: [COLOR limegreen][B]Podría estar Correcto (verificar la Web vía internet)[/B][/COLOR]"

            elif new_web:
                if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                    if str(response.code) == '301' or str(response.code) == '308': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente[/B][/COLOR]"
                    elif str(response.code) == '302' or str(response.code) == '307': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal[/B][/COLOR]"
                    else: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal[/B][/COLOR]"

                txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                if response.headers:
                    txt += '[CR][CR][COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                    txt += str(response.headers) + '[CR]'

        else:
            if len(response.data) < 1000:
                if not 'Diagnosis:' in txt: txt += '[CR][CR][COLOR moccasin][B]Diagnosis:[/B][/COLOR]'

                if 'The website is under maintenance' in response.data: txt += '[CR]obras: [COLOR springgreen][B]Está en mantenimiento[/B][/COLOR]'
                elif 'The server is temporarily busy' in response.data: txt += '[CR]obras: [COLOR springgreen][B]Está en mantenimiento[/B][/COLOR]'
                elif '/cgi-sys/defaultwebpage.cgi' in response.data: txt += txt_sorry
                elif '/www.alliance4creativity.com/' in new_web: txt += '[CR]legal: [COLOR springgreen][B]Copyright infringement[/B][/COLOR]'

                if new_web:
                    if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'

                    else:
                       if str(response.code) == '300' or str(response.code) == '301' or str(response.code) == '302' or str(response.code) == '303' or str(response.code) == '304' or str(response.code) == '307' or str(response.code) == '308':
                           if str(response.code) == '301' or str(response.code) == '308': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente[/B][/COLOR]"
                           elif str(response.code) == '302' or str(response.code) == '307': txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal[/B][/COLOR]"
                           else: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio[/B][/COLOR]"

                           txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                       else: txt += "[CR][CR][COLOR orangered][B]Comprobar Dominio[/B][/COLOR]"

                else:
                    if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'

            if 'status:'in txt:
                if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]account: [COLOR goldenrod][B]Suspendida[/B][/COLOR]'
                else: txt += '[CR]account: [COLOR goldenrod][B]Podría estar en Mantenimiento[/B][/COLOR]'

            else:
               if response.headers:
                   txt += '[CR][CR][COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                   txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                if not '/cgi-sys/suspendedpage.cgi' in new_web or not '/wp-admin/install.php' in new_web:
                    txt += '[CR][CR][COLOR moccasin][B]Datos:[/B][/COLOR][CR]'
                    txt += str(response.data).strip() + '[CR]'

    if not 'Sugerencias:' in txt:
        if len(response.data) == 0: txt += '[CR]'

        if 'Invisible Captcha' in txt:
            txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'
            txt += txt_routs

        elif 'Suspendida' in txt:
            txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += '[COLOR goldenrod][B]Puede estar Renovando el Dominio o quizás estar en Mantenimiento[/B][/COLOR]'

        elif response.sucess == False:
            txt += '[CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += '[COLOR gold][B]Puede Descartar el Servidor en los Ajustes preferencias [/COLOR](categoría [COLOR fuchsia]Play[/COLOR])[/B][CR]'
            txt += '[COLOR tomato][B]Compruebe su Internet y/ó el Servidor, a través de un Navegador Web[/B][/COLOR][CR]'
            txt += txt_routs

    return response, txt


def test_internet():
    platformtools.dialog_notification(config.__addon_name, 'Comprobando [B][COLOR %s]Internet[/COLOR][/B]' % color_avis)

    your_ip = ''

    try:
       data = httptools.downloadpage('http://httpbin.org/ip').data
       data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
       your_ip = scrapertools.find_single_match(str(data), '.*?"origin".*?"(.*?)"')
    except:
       pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://ipinfo.io/ip').data
        except: pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://www.icanhazip.com/').data
        except: pass

    if not your_ip: your_ip = '[COLOR red] Sin Conexión [/COLOR]'

    txt = '[COLOR moccasin][B]Internet:[/B][/COLOR]  %s [CR][CR]' % your_ip

    return txt
