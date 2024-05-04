# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import traceback

from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger, platformtools

context = [{"title": config.get_localized_string(70221),
            "action": "delete_file",
            "channel": "url"}]
btdigg_magnet = '&amp;tr=udp://tracker.openbittorrent.com:80'


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(module=item.module, action="search", title=config.get_localized_string(60089), list_type='server'))
    itemlist.append(Item(module=item.module, action="search", title=config.get_localized_string(60090), list_type='direct'))
    itemlist.append(Item(module=item.module, action="search", title=config.get_localized_string(60091), list_type='findvideos'))
    itemlist.append(Item(module=item.module, action="menu_storage", title="Descargar desde Torrents almacenados", list_type='videolibrary'))

    return itemlist


# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item, texto):
    logger.info("texto=" + texto)

    if not texto.startswith("http"):
        texto = "http://" + texto

    itemlist = []

    if "server" in item.list_type:
        itemlist = servertools.find_video_items(data=texto)
        for item in itemlist:
            item.channel = "url"
            item.action = "play"
    elif "direct" in item.list_type:
        itemlist.append(Item(channel=item.channel, action="play", url=texto, server="directo", title=config.get_localized_string(60092)))
    else:
        data = httptools.downloadpage(texto).data
        itemlist = servertools.find_video_items(data=data)
        for item in itemlist:
            item.channel = "url"
            item.action = "play"

    if len(itemlist) == 0:
        itemlist.append(Item(channel=item.channel, action="search", title=config.get_localized_string(60093)))

    return itemlist


def findvideos(item):
    logger.info()
    from core import filetools
    from lib import generictools

    itemlist = []
    size = ''
    torrent_params = {
                      'url': item.url,
                      'torrents_path': None, 
                      'local_torr': item.torrents_path, 
                      'lookup': False, 
                      'force': True, 
                      'data_torrent': True, 
                      'subtitles': True, 
                      'file_list': True
                      }
    
    #logger.debug(item)
    
    FOLDER_MOVIES = config.get_setting("folder_movies")
    FOLDER_TVSHOWS = config.get_setting("folder_tvshows")
    FOLDER = FOLDER_TVSHOWS if item.infoLabels['mediatype'] == 'episode' else FOLDER_MOVIES
    VIDEOLIBRARY_PATH = config.get_videolibrary_path()
    MOVIES_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_MOVIES)
    TVSHOWS_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_TVSHOWS)
    VIDEO_FOLDER = filetools.join(VIDEOLIBRARY_PATH, FOLDER)

    # Viene desde Kodi/Videoteca de una canal desactivado
    if not item.list_type:
        if item.emergency_urls:
            # Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
            item.infoLabels['playcount'] = 0
            if item.contentChannel == 'videolibrary':
                item.armagedon = True                                           # Lo marcammos como URLs de Emergencia
            item.channel_recovery = 'url'
            item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)
            
            for x, link in enumerate(item.emergency_urls[0]):
                quality = item.quality
                if link.startswith('magnet'):
                    link_path = link
                    item.torrents_path = ''
                else:
                    link_path = filetools.join(VIDEO_FOLDER, link)
                
                if link_path.startswith('magnet') or filetools.isfile(link_path):
                    if btdigg_magnet in link_path and len(item.emergency_urls) > 3 and len(item.emergency_urls[3]) >= x+1:
                        try:
                            z, quality, size = item.emergency_urls[3][x].split('#')
                        except:
                            pass
                    else:
                        torrent_params['url'] = link_path
                        torrent_params['torrents_path'] = link_path
                        torrent_params['local_torr'] = link_path
                        torrent_params = generictools.get_torrent_size(link_path, torrent_params=torrent_params, item=item) # Tamaño en el .torrent
                        size = torrent_params['size']
                        item.torrents_path = torrent_params['torrents_path']
                    if size:
                        # Generamos una copia de Item para trabajar sobre ella
                        item_local = item.clone()
                        
                        item_local.module = 'url'
                        item_local.url = link_path
                        if btdigg_magnet in item_local.url: item_local.btdigg = True
                        item_local.torrent_info = size
                        
                        item_local.quality = quality
                        # Si viene de la Videoteca de Kodi, mostramos que son URLs de Emergencia
                        if item_local.contentChannel == 'videolibrary':
                            item_local.quality = '[COLOR hotpink][E][/COLOR] [COLOR limegreen]%s[/COLOR]' % item_local.quality
                        
                        #Ahora pintamos el link del Torrent
                        item_local.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][Torrent][/COLOR] ' \
                                        + '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' % \
                                        (item_local.quality, str(item_local.language), \
                                        item_local.torrent_info)
                        
                        # Preparamos título y calidad, quitando etiquetas vacías
                        item_local.title = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.title)    
                        item_local.title = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.title)
                        item_local.title = item_local.title.replace("--", "").replace("[]", "")\
                                        .replace("()", "").replace("(/)", "").replace("[/]", "")\
                                        .replace("|", "").strip()
                        
                        item_local.quality = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.quality)
                        item_local.quality = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.quality)
                        item_local.quality = item_local.quality.replace("--", "").replace("[]", "")\
                                        .replace("()", "").replace("(/)", "").replace("[/]", "")\
                                        .replace("|", "").strip()
                        
                        if not size or 'Magnet' in size:
                            item_local.alive = "??"                             #Calidad del link sin verificar
                        elif 'ERROR' in size and 'Pincha' in size:
                            item_local.alive = "ok"                             #link en error, CF challenge, Chrome disponible
                        elif 'ERROR' in size and 'Introduce' in size:
                            item_local.alive = "??"                             #link en error, CF challenge, ruta de descarga no disponible
                            item_local.module = 'setting'
                            item_local.action = 'setting_torrent'
                            item_local.unify = False
                            item_local.folder = False
                            item_local.item_org = item.tourl()
                        elif 'ERROR' in size:
                            item_local.alive = "no"                             #Calidad del link en error, CF challenge?
                        else:
                            item_local.alive = "ok"                             #Calidad del link verificada
                        
                        item_local.action = "play"                              #Visualizar vídeo
                        item_local.server = "torrent"                           #Seridor Torrent
                        
                        itemlist.append(item_local)                             #Pintar pantalla
                        #logger.debug(item_local)

        return itemlist


def menu_storage(item):
    logger.info()
    from core import filetools
    from servers.torrent import torrent_dirs
    
    FOLDER_MOVIES = config.get_setting("folder_movies")
    FOLDER_TVSHOWS = config.get_setting("folder_tvshows")
    FOLDER = FOLDER_TVSHOWS if item.infoLabels['mediatype'] else FOLDER_MOVIES
    VIDEOLIBRARY_PATH = config.get_videolibrary_path()
    MOVIES_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_MOVIES)
    TVSHOWS_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_TVSHOWS)
    VIDEO_FOLDER = filetools.join(VIDEOLIBRARY_PATH, FOLDER)
    TORRENT_PATHS = torrent_dirs()
    MIS_TORRENT_FOLDER = filetools.join(config.get_setting('downloadpath', default=''), 'Mis_Torrents')

    itemlist = []
    
    if 'videolibrary' in item.list_type:
        itemlist.append(Item(module=item.module, action="", title="Videoteca Alfa"))
        itemlist.append(Item(module=item.module, action="list_storage", url=MOVIES_PATH, title="  - " + FOLDER_MOVIES))
        itemlist.append(Item(module=item.module, action="list_storage", url=TVSHOWS_PATH, title="  - " + FOLDER_TVSHOWS))
        
        itemlist.append(Item(module=item.module, action="", title="Almacenamiento general"))
        itemlist.append(Item(module=item.module, action="list_storage", url=MIS_TORRENT_FOLDER, title="  - Mis Torrents"))
        itemlist.append(Item(module=item.module, action="btdigg", url="", 
                        title="  - Buscar Mis Torrents en [B][COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR][/B]"))
        itemlist.append(Item(module=item.module, action="list_storage", url='', title="  - Almacenamiento"))
        
        if TORRENT_PATHS['TORREST_torrents'] or TORRENT_PATHS['QUASAR_torrents'] \
                          or TORRENT_PATHS['ELEMENTUM_torrents'] or TORRENT_PATHS['TORRENTER_torrents']:
            itemlist.append(Item(module=item.module, action="", title="Gestores Torrent"))
            
            if TORRENT_PATHS['TORREST_torrents']:
                itemlist.append(Item(module=item.module, action="list_storage", url=TORRENT_PATHS['TORREST_torrents'], title="  - Torrest"))
            if TORRENT_PATHS['QUASAR_torrents']:
                itemlist.append(Item(module=item.module, action="list_storage", url=TORRENT_PATHS['QUASAR_torrents'], title="  - Quasar"))
            if TORRENT_PATHS['ELEMENTUM_torrents']:
                itemlist.append(Item(module=item.module, action="list_storage", url=TORRENT_PATHS['ELEMENTUM_torrents'], title="  - Elementum"))
            if TORRENT_PATHS['TORRENTER_torrents']:
                itemlist.append(Item(module=item.module, action="list_storage", url=TORRENT_PATHS['TORRENTER_torrents'], title="  - Torrenter"))

            return itemlist


def list_storage(item):
    logger.info()
    from core import filetools
    from lib import generictools
    
    itemlist = []
    
    torrent_params = {
                      'url': item.url,
                      'torrents_path': '', 
                      'local_torr': item.torrents_path, 
                      'lookup': False, 
                      'force': True, 
                      'data_torrent': True, 
                      'subtitles': True, 
                      'file_list': True
                      }
    
    #logger.debug(item)
    
    browse_type = 0
    path_out = item.url
    if not filetools.exists(path_out):
        path_out = ''
    
    if not path_out:
        msg = 'Seleccione carpeta de destino:'
        path_out = platformtools.dialog_browse(browse_type, msg, shares='')
        
    path_list = filetools.listdir(path_out)
    VIDEOLIBRARY_PATH = config.get_videolibrary_path()
    FOLDER_MOVIES = config.get_setting("folder_movies")
    FOLDER_TVSHOWS = config.get_setting("folder_tvshows")
    FOLDER = ''
    if VIDEOLIBRARY_PATH in path_out:
        if FOLDER_MOVIES in path_out:
            FOLDER = FOLDER_MOVIES
        elif FOLDER_TVSHOWS in path_out:
            FOLDER = FOLDER_TVSHOWS
    MOVIES_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_MOVIES)
    TVSHOWS_PATH = filetools.join(VIDEOLIBRARY_PATH, FOLDER_TVSHOWS)
    VIDEO_FOLDER = filetools.join(VIDEOLIBRARY_PATH, FOLDER)
    TEMP_TORRENT_FOLDER = filetools.join(config.get_setting('downloadpath', default=''), 'cached_torrents_Alfa')
    MIS_TORRENT_FOLDER = filetools.join(config.get_setting('downloadpath', default=''), 'Mis_Torrents')
    
    for file in path_list:
        if FOLDER and file.endswith('.json') and file.split('.')[0]+'_01.torrent' in str(path_list):
            json_video = Item().fromjson(filetools.read(filetools.join(path_out, file)))
            json_video.module = 'url'
            json_video.action = 'findvideos'
            json_video.torrents_path = json_video.url
            itemlist.append(json_video)
        
        elif FOLDER and filetools.isdir(filetools.join(path_out, file)):
            if '.torrent' in str(filetools.listdir(filetools.join(path_out, file))) \
                                 or '.magnet' in str(filetools.listdir(filetools.join(path_out, file))):
                itemlist.append(Item(module=item.module, action="list_storage", url=filetools.join(path_out, file), 
                                title=file.title(), contentTitle=file.title(), contentType="list", unify=False, context=context))
                if len(itemlist) > 1:
                    itemlist = sorted(itemlist, key=lambda it: it.title)        #clasificamos
        
        elif not FOLDER and filetools.isdir(filetools.join(path_out, file)):
            if MIS_TORRENT_FOLDER in path_out:
                title = file.title()
                if 'BTDigg' in file:
                    title = title.replace('Btdigg', '[B][COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR][/B]')
                itemlist.append(Item(module=item.module, action="list_storage", url=filetools.join(path_out, file), 
                                title=title, contentTitle=title, contentType="list", unify=False, 
                                btdigg=True if 'BTDigg' in file else False, 
                                url_org=filetools.join(path_out, file), context=context))
                if len(itemlist) > 1:
                    itemlist = sorted(itemlist, key=lambda it: it.title)        #clasificamos
        
        elif not FOLDER and ('.torrent' in file or '.magnet' in file):
            btdigg = False
            if '.torrent' in file:
                url = filetools.join(TEMP_TORRENT_FOLDER, file)
                filetools.copy(filetools.join(path_out, file), url, silent=True)
                if not filetools.exists(url): continue
            else:
                url = filetools.read(filetools.join(path_out, file), silent=True)
                if btdigg_magnet in url: btdigg = True
                size = 'MAGNET'
                if not url: continue
            
            torrent_params['url'] = url
            torrent_params['torrents_path'] = ''
            torrent_params['local_torr'] = filetools.join(TEMP_TORRENT_FOLDER, file)
            torrent_params = generictools.get_torrent_size(url, torrent_params=torrent_params)
            if '.magnet' in file and 'ERROR' in torrent_params['size']: torrent_params['size'] = 'MAGNET'
            size = torrent_params['size']

            itemlist.append(Item(module=item.module, action="play", url=url, url_org=filetools.join(path_out, file), server='torrent', 
                            title=filetools.join(filetools.basename(path_out.rstrip('/').rstrip('\\')), file).title()+" [%s]" % size, 
                            contentTitle=filetools.join(filetools.basename(path_out.rstrip('/').rstrip('\\')), file).title(), 
                            contentType="movie", unify=False, torrents_path=torrent_params['torrents_path'],
                            infoLabels={"tmdb_id": "111"}, context=context, btdigg=btdigg))
            if len(itemlist) > 1:
                    itemlist = sorted(itemlist, key=lambda it: it.title)        #clasificamos

    return itemlist


def btdigg(item):
    if not PY3: from lib.alfaresolver import find_alternative_link
    else: from lib.alfaresolver_py3 import find_alternative_link
    
    context = [{"title": "Copiar a Mis Torrents",
                "action": "copy_file",
                "module": "url"}]
    itemlist = []
    matches = []

    if item.torrent_params:
        torrent_params = item.torrent_params
        del item.torrent_params
    else:
        item.btdigg = url = platformtools.dialog_input(heading='Introduce criterios de búsqueda: título calidad [filtro A Filtro B ...]\r\n' + 
                                                               'ej: silo HDTV [Cap.] ó silo 1080p Cap.110 [Cap.] ó volpina bluray [Esp]')
        url = [item.btdigg]
        contentTitle = []
        if not item.btdigg: return itemlist

        if '[' in item.btdigg:
            contentTitle = scrapertools.find_single_match(item.btdigg, '\s*\[(.*?)[\]|$]').split(' ')
            url = [scrapertools.find_single_match(item.btdigg, '(.*?)\s*\[')]

        torrent_params = {
                          'title_prefix': [{'urls': url, 'checks': contentTitle}], 
                          'quality_alt': [], 
                          'language_alt': [], 
                          'domain_alt': None,
                          'find_alt_link_next': 0
                          }

    if item.matches: 
        matches = item.matches
        del item.matches

    if item.btdigg:
        torrent_params = find_alternative_link(item, torrent_params=torrent_params, cache=True)

    for elem in torrent_params['find_alt_link_result']:
        item_local = item.clone()
        #logger.error(elem)
        
        try:
            scrapedtitle = config.decode_var(elem.get('title', ''))
            
            item_local.url = elem.get('url', '')
            if item_local.url in str(matches): continue
            item_local.server = 'torrent'
            item_local.contentType = 'movie'
            item_local.action = 'play'
            item_local.quality = elem.get('quality', '')
            item_local.language = elem.get('language', [])
            item_local.torrent_info = '%s [MAGNET]: %s' % (elem.get('size', ''), 
                                       scrapedtitle.replace('[B][COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR][/B] ', ''))
            item_local.title = scrapedtitle.replace('[B][COLOR limegreen]BT[/COLOR][COLOR red]Digg[/COLOR][/B] ', '')
            item_local.copytitle = item_local.title
            item_local.contentTitle = '%s / %s' % (item.btdigg, item_local.title)
            item_local.torrents_path = ''
            item_local.infoLabels["tmdb_id"] = "111"
            item_local.context=context
            item_local.btdigg = True
        
        except:
            logger.error(traceback.format_exc())
            continue
            
        itemlist.append(item_local)
        matches.append(elem)

    torrent_params['find_alt_link_result_total'] = []
    if torrent_params['find_alt_link_next'] > 0 and itemlist:
        itemlist.append(item.clone(action='btdigg', title=">> Página siguiente " 
                        + str(torrent_params['find_alt_link_next']+1) + ' de ' + str(int(torrent_params['find_alt_link_found']/10)+1), 
                        torrent_params=torrent_params, matches=matches)) 
    return itemlist


def delete_file(item):
    logger.info()
    from core import filetools
    
    msg = config.get_localized_string(60044) % item.url_org or item.url
    if platformtools.dialog_yesno(config.get_localized_string(70221), msg):

        for file in [item.url, item.url_org]:
            if filetools.isdir(file):
                filetools.rmdirtree(file, silent=True)
                logger.info('Deleting folder: %s' % file)
            elif filetools.isfile(file):
                filetools.remove(file, silent=True)
                logger.info('Deleting file: %s' % file)
            
        platformtools.itemlist_refresh()


def copy_file(item):
    logger.info()
    from core import filetools
    
    MIS_TORRENT_FOLDER = filetools.join(config.get_setting('downloadpath', default=''), 'Mis_Torrents')
    MIS_TORRENT_BTDIGG_FOLDER = filetools.join(MIS_TORRENT_FOLDER, 'BTDigg - resultados')

    if not filetools.exists(MIS_TORRENT_BTDIGG_FOLDER):
        filetools.mkdir(MIS_TORRENT_BTDIGG_FOLDER)
        
    path = filetools.join(MIS_TORRENT_BTDIGG_FOLDER, filetools.validate_path(item.copytitle)+'.magnet')
    filetools.write(path, item.url, silent=True)
    
    platformtools.dialog_notification('Copiando MAGNET', filetools.validate_path(item.copytitle)+'.magnet')
