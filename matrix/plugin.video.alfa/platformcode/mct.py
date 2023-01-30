# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# MCT - Mini Cliente Torrent
# ------------------------------------------------------------

from __future__ import division
from builtins import hex
#from builtins import str
from builtins import range
from past.utils import old_div

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.request as urllib2                                # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
else:
    import urllib2                                                  # Usamos el nativo de PY2 que es más rápido
    import urllib

import os
import re
import tempfile
import platform
import traceback
import time

try:
    import xbmc
    import xbmcgui
except:
    pass

from platformcode import config
LIBTORRENT_PATH = config.get_setting("libtorrent_path", server="torrent", default='')

from servers import torrent as torr
lt, e, e1, e2 = torr.import_libtorrent(LIBTORRENT_PATH)

from core import scrapertools
from core import filetools
from core import httptools

try:
    BUFFER = int(config.get_setting("mct_buffer", server="torrent", default="50"))
except:
    BUFFER = 50
    config.set_setting("mct_buffer", "50", server="torrent")

try:
    DOWNLOAD_PATH = ''
    DOWNLOAD_PATH = config.get_setting("mct_download_path", \
                server="torrent", default=config.get_setting("downloadpath"))
except:
    DOWNLOAD_PATH = config.get_setting("mct_download_path", server="torrent", default=config.get_setting("downloadpath"))
if not config.get_setting("mct_download_path", server="torrent") and DOWNLOAD_PATH:
    config.set_setting("mct_download_path", DOWNLOAD_PATH, server="torrent")
if not DOWNLOAD_PATH:
    try:
        DOWNLOAD_PATH = str(os.path.join(config.get_data_path(), 'downloads'))
        config.set_setting("mct_download_path", os.path.join(config.get_data_path(), 'downloads'), server="torrent")
    except:
        DOWNLOAD_PATH = os.path.join(config.get_data_path(), 'downloads')
        config.set_setting("mct_download_path", DOWNLOAD_PATH, server="torrent")

BACKGROUND = config.get_setting("mct_background_download", server="torrent", default=True)
RAR = config.get_setting("mct_rar_unpack", server="torrent", default=True)
DOWNLOAD_LIMIT = config.get_setting("mct_download_limit", server="torrent", default="")
if DOWNLOAD_LIMIT:
    try:
        DOWNLOAD_LIMIT = int(DOWNLOAD_LIMIT) * 1024
    except:
        DOWNLOAD_LIMIT = 0
else:
    DOWNLOAD_LIMIT = 0
UPLOAD_LIMIT = 0
if DOWNLOAD_LIMIT > 0:
    UPLOAD_LIMIT = DOWNLOAD_LIMIT / 35
msg_header = 'Alfa MCT Cliente Torrent: %s' % config.get_setting("libtorrent_version", server="torrent", default="")


def play(url, xlistitem={}, is_view=None, subtitle="", password="", item=None):
    allocate = True
    
    try:
        log("XXX KODI XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        log("OS platform: %s %s" % (platform.system(),platform.release()))
        log("xbmc/kodi version: %s" % xbmc.getInfoLabel( "System.BuildVersion" ))
        xbmc_version = int(xbmc.getInfoLabel( "System.BuildVersion" )[:2])
        log("Architecture: %s %s" % (str(platform.machine()), \
                        str(sys.maxsize > 2 ** 32 and "64-bit" or "32-bit")))
        log("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX KODI & platform XXXX")
    except:
        log(traceback.format_exc())

    # -- adfly: ------------------------------------
    if url.startswith("http://adf.ly/"):
        try:
            data = httptools.downloadpage(url).data
            url = decode_adfly(data)
        except:
            ddd = xbmcgui.Dialog()
            ddd.ok( msg_header + ": Sin soporte adf.ly", "El script no tiene soporte para el acortador de urls adf.ly." + '\n' + " " + '\n' + "url: " + url )
            return

    """
    # -- Necesario para algunas webs ----------------------------
    if not url.endswith(".torrent") and not url.startswith("magnet"):
        #t_file = httptools.downloadpage(url, follow_redirects=False).headers["location"]
        t_file = scrapertools.get_header_from_response(url, header_to_get="location")
        if t_file:
            if len(t_file) > 0:
                url = t_file
                t_file = httptools.downloadpage(url, follow_redirects=False).headers["location"]
            if len(t_file) > 0:
                url = t_file
    """

    # -- Crear dos carpetas en descargas para los archivos ------
    save_path_videos = os.path.join( DOWNLOAD_PATH , "MCT-torrent-videos" )
    save_path_torrents = os.path.join( DOWNLOAD_PATH , "MCT-torrents" )
    if not os.path.exists( save_path_torrents ): os.mkdir(save_path_torrents)
    video_path = ''
    global bkg_user
    bkg_user = False
    dp_BG = False
    DOWNGROUND = False
    torrent_stop = False
    BACKGROUND = config.get_setting("mct_background_download", server="torrent", default=True)
    if item.downloadFilename and item.downloadStatus in [2, 4]:                 # Descargas AUTO
        BACKGROUND = True
        DOWNGROUND = True
        bkg_user = True
    global ses_lt
    ses_lt = False
    if item:
        if item.contentType == 'movie':
            video_path = '%s-%s' % (item.contentTitle, item.infoLabels['tmdb_id'])
        else:
            video_path = '%s-%sx%s-%s' % (item.contentSerieName, item.contentSeason, \
                            item.contentEpisodeNumber, item.infoLabels['tmdb_id'])
        item.rar_path = video_path

    # -- Usar - archivo torrent desde web, magnet o HD ---------
    if not os.path.isfile(url) and not url.startswith("magnet"):
        # -- http - crear archivo torrent -----------------------
        data = url_get(url)

        # -- El nombre del torrent será el que contiene en los --
        # -- datos.                                             -
        re_name = urllib.unquote( scrapertools.find_single_match(data,':name\d+:(.*?)\d+:') )
        
        import bencode, hashlib
        decodedDict = bencode.bdecode(data)
        if not PY3:
            re_name = hashlib.sha1(bencode.bencode(decodedDict[b"info"])).hexdigest()
        else:
            re_name = hashlib.sha1(bencode.bencode(decodedDict["info"])).hexdigest()
        
        torrent_file = os.path.join(save_path_torrents, encode(re_name.upper() + '.torrent'))

        f = open(torrent_file,'wb')
        f.write(data)
        f.close()
    elif os.path.isfile(url):
        # -- file - para usar torrens desde el HD ---------------
        torrent_file = filetools.join(save_path_torrents, filetools.basename(url).upper()).replace('.TORRENT', '.torrent')
        filetools.copy(url, torrent_file, silent=True)
    else:
        # -- magnet ---------------------------------------------
        torrent_file = url
    torrent_file = torrent_file.replace('.TORRENT', '.torrent')
    # -----------------------------------------------------------

    # -- MCT - MiniClienteTorrent -------------------------------
    try:
        log("XXX libtorrent pathname: %s" % str(LIBTORRENT_PATH))
        ses = lt.session()
    except Exception as e:
        do = xbmcgui.Dialog()
        e = e1 or e2
        do.ok('ERROR en el cliente MCT Libtorrent', 'Módulo no encontrado o imcompatible con el dispositivo.' + '\n' + 
                    'Reporte el fallo adjuntando un "log".' + '\n' + str(e))
        return
        
    log("XXX libtorrent version: %s" % lt.version)
    log("##### Torrent file: %s ##" % torrent_file)

    ses.add_dht_router("router.bittorrent.com",6881)
    ses.add_dht_router("router.utorrent.com",6881)
    ses.add_dht_router("dht.transmissionbt.com",6881)

    trackers = [
        "udp://tracker.openbittorrent.com:80/announce",
        "http://tracker.torrentbay.to:6969/announce",
        "http://tracker.pow7.com/announce",
        "udp://tracker.ccc.de:80/announce",
        "udp://open.demonii.com:1337",

        "http://9.rarbg.com:2710/announce",
        "http://bt.careland.com.cn:6969/announce",
        "http://explodie.org:6969/announce",
        "http://mgtracker.org:2710/announce",
        "http://tracker.best-torrents.net:6969/announce",
        "http://tracker.tfile.me/announce",
        "http://tracker1.wasabii.com.tw:6969/announce",
        "udp://9.rarbg.com:2710/announce",
        "udp://9.rarbg.me:2710/announce",
        "udp://coppersurfer.tk:6969/announce",

        "http://www.spanishtracker.com:2710/announce",
        "http://www.todotorrents.com:2710/announce",
    ]

    video_file = ""
    # -- magnet2torrent -----------------------------------------
    if torrent_file.startswith("magnet"):
        try:
            import zlib
            btih = hex(zlib.crc32(scrapertools.find_single_match(torrent_file, 'magnet:\?xt=urn:(?:[A-z0-9:]+|)([A-z0-9]{32})')) & 0xffffffff)
            t_hash = scrapertools.find_single_match(torrent_file, 'xt=urn:btih:([^\&]+)\&')
            files = [f for f in os.listdir(save_path_torrents) if os.path.isfile(os.path.join(save_path_torrents, f))]
            for file in files:
                if btih in os.path.basename(file):
                    torrent_file = os.path.join(save_path_torrents, file)
        except:
            pass

    if torrent_file.startswith("magnet"):
        try:
            tempdir = tempfile.mkdtemp(dir=config.get_temp_file('tempfile_mkdtemp/'))
        except IOError:
            tempdir = os.path.join(save_path_torrents , "temp")
            if not os.path.exists(tempdir):
                os.mkdir(tempdir)
        params = {
            'save_path': tempdir,
            'trackers': trackers,
            'storage_mode': lt.storage_mode_t.storage_mode_allocate
        }
        """
        ,
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        """
        h = lt.add_magnet_uri(ses, torrent_file, params)
        dp = xbmcgui.DialogProgress()
        dp.create(msg_header)
        while not h.has_metadata():
            message, porcent, msg_file, s, download = getProgress(h, "Creando torrent desde magnet")
            dp.update(porcent, message + '\n' + msg_file + '\n' + ' ')
            if s.state == 1: download = 1
            if dp.iscanceled():
                dp.close()
                remove_files( download, torrent_file, video_file, ses, h, '', item )
                return
            h.force_dht_announce()
            xbmc.sleep(1000)

        dp.close()
        info = h.get_torrent_info()
        data = lt.bencode( lt.create_torrent(info).generate() )

        #torrent_file = os.path.join(save_path_torrents, unicode(info.name()+"-"+btih, "'utf-8'", errors="replace") + ".torrent")
        torrent_file = os.path.join(save_path_torrents, t_hash.upper()+".torrent")
        f = open(torrent_file,'wb')
        f.write(data)
        f.close()
        ses.remove_torrent(h)
        filetools.rmdirtree(tempdir)
    # -----------------------------------------------------------

    # -- Archivos torrent ---------------------------------------
    e = lt.bdecode(open(torrent_file, 'rb').read())
    info = lt.torrent_info(e)

    # -- El más gordo o uno de los más gordo se entiende que es -
    # -- el vídeo o es el vídeo que se usará como referencia    -
    # -- para el tipo de archivo                                -
    log("##### Archivos ## %s ##" % len(info.files()))
    _index_file, _video_file, _size_file = get_video_file(info)

    # -- Prioritarizar/Seleccionar archivo-----------------------
    _index, video_file, video_size, len_files = get_video_files_sizes( info )
    if len_files == 0:
        dp = xbmcgui.Dialog().ok("No se puede reproducir", "El torrent no contiene ningún archivo de vídeo")

    if _index < 0:
        log("##### parts = %s #########" % str(video_file))
        log("##### video_size = %s #########" % str(video_size))
        log("##### _index = %s #########" % str(_index))
        #if _index == -1:
        #    _index = _index_file
        #    video_size = _size_file
        video_file = _video_file
    else:
        log("##### video_size = %s #########" % str(video_size))
        log("##### _index = %s #########" % str(_index))
    _video_file_ext = os.path.splitext( _video_file )[1]
    log("##### _video_file ## %s ##" % str(_video_file))
    log("##### _video_file_ext ## %s ##" % _video_file_ext)

    if url.startswith('magnet:') or _index > 0:
        item.downloadFilename = ':%s: %s' % ('MCT', video_file)
        if item.torr_folder: item.torr_folder = filetools.dirname(video_path)
    item.downloadQueued = 0
    time.sleep(1)
    torr.update_control(item, function='mct_start')

    dp_cerrado = True
    rar = False
    global extracted_rar
    extracted_rar = False
    global erase_file_path
    erase_file_path = ''
    
    if _video_file_ext == ".rar":
        rar = True
        filename = video_file
        if "/" in filename:
            filename = filename.split("/")[1]
        if (RAR and BACKGROUND):
            xbmcgui.Dialog().notification("Encontrado archivo .RAR de %.2f MB" % (video_size / 1048576.0),
                                        "Puedes realizar otras tareas en Kodi mientrastanto. " + \
                                        "Te informaremos...", time=10000)
            dialog = True
        else:
            dialog = xbmcgui.Dialog().yesno("Encontrado archivo .RAR...", "Nombre: %s" % filename + '\n' + 
                                        "Tamaño: %.2f MB" % (video_size / 1048576.0) + '\n' + 
                                        "¿Descargar en segundo plano? Cancelar en menú Descargas")
        if dialog:
            dp_cerrado = False
            dp = xbmcgui.DialogProgressBG()
            dp.create(msg_header)
            dp_BG = True

    if (_video_file_ext == ".avi" or _video_file_ext == ".mp4" or _video_file_ext == ".mkv") and allocate and int(lt.version.split('.')[0]) < 2:
        log("##### storage_mode_t.storage_mode_allocate ("+_video_file_ext+") #####")
        h = ses.add_torrent( { 'ti':info, 'save_path': save_path_videos, 'trackers':trackers, 'storage_mode':lt.storage_mode_t.storage_mode_allocate } )
    else:
        log("##### storage_mode_t.storage_mode_sparse ("+_video_file_ext+") #####")
        h = ses.add_torrent( { 'ti':info, 'save_path': save_path_videos, 'trackers':trackers, 'storage_mode':lt.storage_mode_t.storage_mode_sparse } )
        allocate = True

    ses_lt = True
    # -----------------------------------------------------------

    # -- Descarga secuencial - trozo 1, trozo 2, ... ------------
    h.set_sequential_download(True)

    h.force_reannounce()
    h.force_dht_announce()

    # -- Inicio de variables para 'pause' automático cuando el  -
    # -- el vídeo se acerca a una pieza sin completar           -
    is_greater_num_pieces = False
    is_greater_num_pieces_plus = False
    is_greater_num_pieces_pause = False

    porcent4first_pieces = int( video_size * 0.000000005 )
    porcent4first_pieces = BUFFER
    if porcent4first_pieces < BUFFER: porcent4first_pieces = BUFFER
    if porcent4first_pieces > 100: porcent4first_pieces = 100
    porcent4last_pieces = int(old_div(porcent4first_pieces,2))

    num_pieces_to_resume = int( video_size * 0.0000000025 )
    if num_pieces_to_resume < 10: num_pieces_to_resume = 10
    if num_pieces_to_resume > 25: num_pieces_to_resume = 25

    log("##### porcent4first_pieces ## %s ##" % porcent4first_pieces)
    log("##### porcent4last_pieces ## %s ##" % porcent4last_pieces)
    log("##### num_pieces_to_resume ## %s ##" % num_pieces_to_resume)

    # -- Prioritarizar o seleccionar las piezas del archivo que -
    # -- se desea reproducir con 'file_priorities'              -
    piece_set = set_priority_pieces(h, _index, video_file, video_size,
                                    porcent4first_pieces, porcent4last_pieces, allocate)
    global tot_piece_set
    tot_piece_set = len(piece_set)
    log("##### total piece_set ## %s ##" % len(piece_set))

    if dp_cerrado:
        if bkg_user:
            dp = xbmcgui.DialogProgressBG()
            dp.create(msg_header)
            dp_BG = True
        else:
            # -- Crear diálogo de progreso para el primer bucle ---------
            dp = xbmcgui.DialogProgress()
            dp.create(msg_header)

    _pieces_info = {}

    ren_video_file = os.path.join( save_path_videos, video_file )
    # -- Doble bucle anidado ------------------------------------
    # -- Descarga - Primer bucle
    x = 1
    while not h.is_seed():
        x += 1
        s = h.status()

        xbmc.sleep(1000)
        if not dp_cerrado and not BACKGROUND:
            dp.close()
            dp_cerrado = True
            dp = xbmcgui.DialogProgress()
            dp.create(msg_header)

        # -- Recuperar los datos del progreso -------------------
        message, porcent, msg_file, s, download = getProgress(h, video_file, _pf=_pieces_info)
        
        # Si se ha borrado el .torrent es porque se quiere cancelar la sesión
        #log("##### x: %s" % str(x))
        #log("##### exists: %s" % str(filetools.exists(torrent_file)))
        if ((download > 1 and (str(x).endswith('0') or str(x).endswith('5'))) \
                        or (download == 0 and x > 30)) and not filetools.exists(torrent_file):
            
            log('LISTADO de .torrent %s' % (filetools.listdir(filetools.dirname(torrent_file))))
            if filetools.exists(torrent_file.replace('.torrent', '.pause')) or filetools.exists(torrent_file.replace('.TORRENT', '.pause')):
                torrent_paused = True
                torrent_stop = True
                action = 'pause'
                item.downloadProgress = -1
                res = filetools.remove(torrent_file.replace('.torrent', '.pause').replace('.TORRENT', '.pause'), silent=True)
                #res = filetools.rename(torrent_file.replace('.torrent', '.pause').replace('.TORRENT', '.pause'), \
                #                        filetools.basename(torrent_file), strict=True, silent=True)
                log("##### Progreso: %s, .torrent pausado: %s" % (str(porcent), video_file))
            elif filetools.exists(torrent_file.replace('.torrent', '.reset')) or filetools.exists(torrent_file.replace('.TORRENT', '.reset')):
                torrent_reseted = True
                torrent_stop = True
                action = 'reset'
                item.downloadProgress = 0
                res = filetools.remove(torrent_file.replace('.torrent', '.reset').replace('.TORRENT', '.reset'), silent=True)
                #res = filetools.rename(torrent_file.replace('.torrent', '.reset').replace('.TORRENT', '.reset'), \
                #                        filetools.basename(torrent_file), strict=True, silent=True)
                log("##### Progreso: %s, .torrent reseteado: %s" % (str(porcent), video_file))
            else:
                torrent_deleted = True
                torrent_stop = True
                action = 'delete'
                item.downloadProgress = 0
                res = True
                log("##### Progreso: %s, .torrent borrado: %s" % (str(porcent), video_file))

            if not res:
                log('ERROR borrando por -%s- el .torrent %s' % (action, filetools.listdir(filetools.dirname(torrent_file))))
            
            if item.downloadProgress == 0 or torrent_stop:
                remove_files( 1, torrent_file, video_file, ses, h, ren_video_file, item )
                bkg_user = False
            dp.close()
            return

        # -- Si hace 'checking' existe descarga -----------------
        # -- 'download' Se usará para saber si hay datos        -
        # -- descargados para el diálogo de 'remove_files'      -
        if s.state == 1: download = 1

        if (s.state == 5 or s.state == 4) and rar:
            # -- Borrar sesión para que libere los archivos y se pueda renombrar la carpeta -------
            ses.pause()
            #video_file, rar, play_file = extract_files(video_file, save_path_videos, password, dp, item=item)
            video_file, rar, play_file, erase_path = torr.extract_files(video_file, \
                            save_path_videos, password, dp, item=item, torr_client='MCT')   # ... extraemos el vídeo del RAR
                            
            item.downloadFilename = play_file.replace(save_path_videos, '')
            item.downloadFilename = filetools.join(item.downloadFilename, video_file)
            item.downloadFilename = ':%s: %s' % ('MCT', item.downloadFilename)
            
            dp.close()
            
            erase_file_path = erase_path
            ren_video_file = erase_file_path
            extracted_rar = rar
            if not play_file:
                remove_files( download, torrent_file, erase_file_path, ses, h, ren_video_file, item )
                return
            is_view = "Ok"
            save_path_videos = play_file
            xbmc.sleep(3000)

        # -- Player - play --------------------------------------
        # -- Comprobar si se han completado las piezas para el  -
        # -- inicio del vídeo                                   -
        first_pieces = True
        #if not extracted_rar:
        _c = 0
        for i in range( piece_set[0], piece_set[porcent4first_pieces] ):
            first_pieces &= h.have_piece(i)
            if h.have_piece(i): _c+= 1
        _pieces_info = {'current': 0, 'continuous': "%s/%s" % (_c, porcent4first_pieces), \
                        'continuous2': "", 'have': h.status().num_pieces, 'len': len(piece_set)}

        last_pieces = True
        if not allocate:
            _c = len(piece_set)-1; _cc = 0
            for i in range(len(piece_set)-porcent4last_pieces, len(piece_set)):
                last_pieces &= h.have_piece(i)
                if h.have_piece(i): _c-= 1; _cc+=1
            _pieces_info['continuous2'] = "[%s/%s] " % (_cc, porcent4last_pieces)

        if is_view != "Ok" and h.status().num_pieces >= BUFFER and not rar and not bkg_user \
                            or ((s.state == 5 or s.state == 4) and bkg_user):
            _pieces_info['continuous2'] = ""
            log("##### porcent [%.2f%%]" % (s.progress * 100))
            dp.close()
            dp_cerrado = True
            if not bkg_user:
                is_view = "Ok"
            else:
                remove_files( download, torrent_file, video_file, ses, h, ren_video_file, item )
                return

        if is_view == "Ok":
            # -- Esperando a que termine otra reproducción --------------------------
            while xbmc.Player().isPlaying():
                xbmc.sleep(3000)
                
            # -- Player - Ver el vídeo --------------------------
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            playlist.clear()

            ren_video_file = os.path.join( save_path_videos, video_file )
            try:
                playlist.add( ren_video_file, xlistitem )
            except:
                playlist.add( ren_video_file )

            if xbmc_version < 17:
                player = play_video( xbmc.PLAYER_CORE_AUTO )
            else:
                player = play_video()
            
            if subtitle:
                time.sleep(0.5)
                player.setSubtitles(item.subtitle)                              # Activamos los subtítulos
            
            player.play(playlist)

            # -- Contador de cancelaciones para la ventana de   -
            # -- 'pause' automático                             -
            is_greater_num_pieces_canceled = 0
            continuous_pieces = 0
            porcent_time = 0.00
            current_piece = 0
            set_next_continuous_pieces = porcent4first_pieces

            # -- Impedir que kodi haga 'resume' a un archivo ----
            # -- que se reprodujo con anterioridad y que se     -
            # -- eliminó para impedir que intente la reprucción -
            # -- en una pieza que aún no se ha completado y se  -
            # -- active 'pause' automático                      -
            not_resume = True

            # -- Bandera subTítulos
            _sub = False

            # -- Segundo bucle - Player - Control de eventos ----
            bkg_auto = True
            log("##### PLAY %s" % (h.status().num_pieces))
            if item: torr.mark_auto_as_watched(item)
            if ses_lt:
                h.set_download_limit(DOWNLOAD_LIMIT)
                h.set_upload_limit(UPLOAD_LIMIT)
            while player.isPlaying():

                # -- Impedir que kodi haga 'resume' al inicio ---
                # -- de la descarga de un archivo conocido      -
                if not_resume:
                    player.seekTime(0)
                    not_resume = False

                # -- Control 'pause' automático                 -
                continuous_pieces = count_completed_continuous_pieces(h, piece_set)

                if xbmc.Player().isPlaying() and not rar:

                    # -- Porcentage del progreso del vídeo ------
                    # -- En kodi 18.x se debe controlar         -
                    # -- ZeroDivisionError: float division by   -
                    # -- zero                                   -
                    player_getTime = player.getTime()
                    player_getTotalTime = player.getTotalTime()
                    try: porcent_time = old_div(player_getTime, player_getTotalTime) * 100
                    except: porcent_time = 0

                    # -- Pieza que se está reproduciendo --------
                    # -- En kodi 18.x se debe controlar         -
                    # -- ZeroDivisionError: float division by   -
                    # -- zero                                   -
                    try: current_piece = int( old_div(porcent_time, 100) * len(piece_set) )
                    except:  current_piece = 0

                    # -- Banderas de control --------------------
                    is_greater_num_pieces = (current_piece > continuous_pieces - num_pieces_to_resume)
                    #is_greater_num_pieces_plus = (current_piece + porcent4first_pieces > continuous_pieces)
                    is_greater_num_pieces_plus = (current_piece + BUFFER > continuous_pieces)
                    #is_greater_num_pieces_finished = (current_piece + porcent4first_pieces >= len(piece_set))
                    is_greater_num_pieces_finished = (current_piece + BUFFER >= len(piece_set))

                    # -- Activa 'pause' automático --------------
                    if is_greater_num_pieces and not player.paused and not is_greater_num_pieces_finished:
                        is_greater_num_pieces_pause = True
                        player.pause()

                    if continuous_pieces >= set_next_continuous_pieces:
                        set_next_continuous_pieces = continuous_pieces + num_pieces_to_resume
                    next_continuous_pieces = str(continuous_pieces - current_piece) + "/" + str(set_next_continuous_pieces - current_piece)
                    _pieces_info = {'current': current_piece, 'continuous': next_continuous_pieces , 'continuous2': _pieces_info['continuous2'], 'have': h.status().num_pieces, 'len': len(piece_set)}

                # -- Cerrar el diálogo de progreso --------------
                if player.resumed:
                    dp.close()

                # -- Mostrar el diálogo de progreso -------------
                if player.paused and dp_cerrado and not rar:
                    # -- Crear diálogo si no existe -------------
                    log("##### PAUSED %s" % (h.status().num_pieces))
                    if not player.statusDialogoProgress:
                        dp = xbmcgui.DialogProgressBG()
                        dp.create(msg_header)
                        dp_BG = True
                        player.setDialogoProgress()

                    # -- Diálogos de estado en el visionado -----
                    if not h.is_seed():
                        # -- Recuperar los datos del progreso ---
                        message, porcent, msg_file, s, download = getProgress(h, video_file, _pf=_pieces_info)
                        if dp_BG:
                            dp.update(porcent, message, msg_file)
                        else:
                            dp.update(porcent, message + '\n' + msg_file + '\n' + ' ')
                    else:
                        if dp_BG:
                            dp.update(100, "Descarga completa: ", video_file)
                        else:
                            dp.update(100, "Descarga completa: " + '\n' + video_file + '\n' + ' ')

                    # -- Se canceló el progreso en el visionado -
                    # -- Continuar                              -
                    if not bkg_auto and dp.iscanceled():
                        dp.close()
                        player.pause()

                    # -- Se canceló el progreso en el visionado -
                    # -- en la ventana de 'pause' automático.   -
                    # -- Parar si el contador llega a 3         -
                    if not bkg_auto and dp.iscanceled() and is_greater_num_pieces_pause:
                        is_greater_num_pieces_canceled+= 1
                        if is_greater_num_pieces_canceled == 3:
                            player.stop()

                    # -- Desactiva 'pause' automático y ---------
                    # -- reinicia el contador de cancelaciones  -
                    if not is_greater_num_pieces_plus and is_greater_num_pieces_pause:
                        dp.close()
                        player.pause()
                        is_greater_num_pieces_pause = False
                        is_greater_num_pieces_canceled = 0
                    
                    # -- El usuario cancelo el visionado --------
                    # -- Terminar                               -
                    if player.ended:
                        # -- Diálogo eliminar archivos ----------
                        remove_files( download, torrent_file, video_file, ses, h, ren_video_file, item )
                        return
                
                xbmc.sleep(1000)
                
        # -- Kodi - Se cerró el visionado -----------------------
        # -- Continuar | Terminar                               -
        if is_view == "Ok" and not xbmc.Player().isPlaying():
            dp.close()
            
            if h.status().num_pieces < tot_piece_set:
                # -- Diálogo continuar o terminar ---------------
                # Preguntamos si el usuario quiere pasar a backgroung
                ok = xbmcgui.Dialog().yesno(msg_header, "¿Borramos los archivo descargados? (incompletos)" + '\n' + 
                                    "Selecciona NO para seguir descargando en segundo plano")
            else: ok = True
            # -- NO ---------------------------------------------
            if not ok:
                is_view=None
                bkg_user = True
                dp_cerrado = False
                dp = xbmcgui.DialogProgressBG()
                dp.create(msg_header)
                dp_BG = True
            
            else:
                # -- Terminar: ----------------------------------
                # -- Comprobar si el vídeo pertenece a una ------
                # -- lista de archivos                          -
                remove_files( download, torrent_file, video_file, ses, h, ren_video_file, item )
                if item.path.endswith('.json'):
                    log("##### BORRANDO Archivo de CONTROL %s" % item.path)
                    filetools.remove(filetools.join(config.get_setting("downloadlistpath"), item.path))
                dp.close()
                return
                """
                #_index, video_file, video_size, len_files = get_video_files_sizes( info )
                if _index < 0 or len_files == 1:
                    # -- Diálogo eliminar archivos --------------
                    #video_file = _video_file
                    remove_files( download, torrent_file, video_file, ses, h, ren_video_file )
                    dp.close()
                    return
                else:
                    # -- Lista de archivos. Diálogo de opciones -
                    piece_set = set_priority_pieces(h, _index, video_file, video_size,
                                                    porcent4first_pieces, porcent4last_pieces, allocate)
                    is_view=None
                    dp = xbmcgui.DialogProgress()
                    dp.create(msg_header)
                """

        # -- Mostar progeso antes del visionado -----------------
        if is_view != "Ok" :
            if dp_BG:
                dp.update(porcent, message, msg_file)
            else:
                dp.update(porcent, message + '\n' + msg_file + '\n' + ' ')

        # -- Se canceló el progreso antes del visionado ---------
        # -- Dar otra oportunidad en background o Terminar                                           -
        if not bkg_user and dp_cerrado and dp.iscanceled():
            dp.close()
            # Preguntamos si el usuario quiere pasar a backgroung
            dialog = xbmcgui.Dialog().yesno(msg_header, "¿Borramos los archivo descargados? (incompletos)", 
                                        "Seleccione NO para seguir descargando en segundo plano")
            if not dialog:
                bkg_user = True
                dp_cerrado = False
                dp = xbmcgui.DialogProgressBG()
                dp.create(msg_header)
                dp_BG = True
                if ses_lt: h.set_download_limit(DOWNLOAD_LIMIT)
                
            else:
                remove_files( download, torrent_file, video_file, ses, h, ren_video_file, item )
                if item.path.endswith('.json'):
                    log("##### BORRANDO Archivo de CONTROL %s" % item.path)
                    filetools.remove(filetools.join(config.get_setting("downloadlistpath"), item.path))
                return
                # -- Comprobar si el vídeo pertenece a una lista de -
                # -- archivos                                       -
                #_index, video_file, video_size, len_files = get_video_files_sizes( info )
                if _index < 0 or len_files == 1:
                    # -- Diálogo eliminar archivos ------------------
                    #video_file = _video_file
                    remove_files( download, torrent_file, video_file, ses, h, ren_video_file, item )
                    return
                else:
                    # -- Lista de archivos. Diálogo de opciones -----
                    piece_set = set_priority_pieces(h, _index, video_file, video_size,
                                                    porcent4first_pieces, porcent4last_pieces, allocate)
                    is_view=None
                    dp = xbmcgui.DialogProgress()
                    dp.create(msg_header)

    # -- Kodi - Error? - No debería llegar aquí -----------------
    if is_view == "Ok" and not xbmc.Player().isPlaying():
        dp.close()
        # -- Diálogo eliminar archivos --------------------------
        remove_files( download, torrent_file, video_file, ses, h, ren_video_file, item )

    return


# -- Progreso de la descarga ------------------------------------
def getProgress(h, video_file, _pf={}):

    if len(_pf) > 0:
        _pf_msg = "[%s] [%s] %s[%s] [%s]" % (_pf['current'], _pf['continuous'], _pf['continuous2'], _pf['have'], _pf['len'])
    else: _pf_msg = ""

    s = h.status()

    state_str = ['queued', 'checking', 'downloading metadata', \
        'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']

    message = '%.2f%% d:%.1f kb/s u:%.1f kb/s p:%d s:%d %s' % \
        (s.progress * 100, old_div(s.download_rate, 1000), old_div(s.upload_rate, 1000), \
        s.num_peers, s.num_seeds, state_str[s.state])
    porcent = int( s.progress * 100 )

    download = ( s.progress * 100 )

    if "/" in video_file: video_file = video_file.split("/")[1]
    msg_file = video_file

    if len(msg_file) > 50:
        msg_file = msg_file.replace( video_file, os.path.splitext(video_file)[0][:50] + "... " + os.path.splitext(video_file)[1] )
    msg_file = msg_file + "[CR]" + "%.2f MB" % (s.total_wanted/1048576.0) + " - " + _pf_msg

    return (message, porcent, msg_file, s, download)


# -- Clase play_video - Controlar eventos -----------------------
class play_video(xbmc.Player):

    def __init__( self, *args, **kwargs ):
        self.paused = False
        self.resumed = True
        self.statusDialogoProgress = False
        self.ended = False

    def onPlayBackPaused(self):
        self.paused = True
        self.resumed = False

    def onPlayBackResumed(self):
        self.paused = False
        self.resumed = True
        self.statusDialogoProgress = False

    def is_paused(self):
        return self.paused

    def setDialogoProgress(self):
        self.statusDialogoProgress = True

    def is_started(self):
        self.ended = False

    def is_ended(self):
        self.ended = True


# -- Conseguir el nombre un alchivo de vídeo del metadata -------
# -- El más gordo o uno de los más gordo se entiende que es el  -
# -- vídeo o es vídeo que se usará como referencia para el tipo -
# -- de archivo                                                 -
def get_video_file( info ):
    extensions_list = ['.aaf', '.3gp', '.asf', '.avi', '.flv', '.mpeg',
                       '.m1v', '.m2v', '.m4v', '.mkv', '.mov', '.mpg',
                       '.mpe', '.mp4', '.ogg', '.rar', '.wmv', '.zip']
    size_file = 0
    for i, f in enumerate(info.files()):
        if f.size > size_file:
            video_file = f.path.replace("\\","/")
            size_file = f.size
            index_file = i
            if os.path.splitext( video_file )[1] in extensions_list:
                break
    return index_file, video_file, size_file


# -- Listado de selección del vídeo a prioritarizar -------------
def get_video_files_sizes( info ):

    opciones = {}
    vfile_name = {}
    vfile_size = {}
    rar_parts = 0
    rar_size = 0
    vid_parts = 0
    vid_size = 0

    # -- Eliminar errores con tíldes -----------------------------
    for i, f in enumerate( info.files() ):
        if not PY3:
            _title = unicode(f.path, "iso-8859-1", errors="replace")
            _title = unicode(f.path, "'utf-8'", errors="replace")
        elif PY3 and isinstance(f.path, bytes):
            _title = f.path.decode('utf-8')

    extensions_list = ['.aaf', '.3gp', '.asf', '.avi', '.flv', '.mpeg',
                       '.m1v', '.m2v', '.m4v', '.mkv', '.mov', '.mpg',
                       '.mpe', '.mp4', '.ogg', '.rar', '.wmv', '.zip']

    for i, f in enumerate( info.files() ):
        _index = int(i)
        _title = f.path.replace("\\","/")
        _size = f.size

        _file_name = os.path.splitext( _title )[0]
        if "/" in _file_name: _file_name = _file_name.split('/')[1]

        _file_ext = os.path.splitext( _title )[1]
        
        if '.rar' in _file_ext or '.zip' in _file_ext or bkg_user:
            rar_parts += 1
            rar_size += _size
        else:
            vid_parts += 1
            vid_size += _size

        if _file_ext in extensions_list:
            index = len(opciones)
            _caption = str(index) + \
                " - " + \
                _file_name + _file_ext + \
                " - %.2f MB" % (_size / 1048576.0)

            vfile_name[index] = _title
            vfile_size[index] = _size

            opciones[i] = _caption

    if len(opciones) > 1:
        if rar_parts > 1:
            seleccion = -1
            index = -9
            return index, rar_parts, rar_size, len(opciones)
        else:
            d = xbmcgui.Dialog()
            seleccion = d.select(msg_header + ": Selecciona el vídeo, o 'Cancelar' para todos", list(opciones.values()))
    else: seleccion = 0

    index = list(opciones.keys())[seleccion]
    if seleccion == -1:
        vfile_name[seleccion] = vid_parts
        vfile_size[seleccion] = vid_size
        index = seleccion

    return index, vfile_name[seleccion], vfile_size[seleccion], len(opciones)

# -- Preguntar si se desea borrar lo descargado -----------------
def remove_files( download, torrent_file, video_file, ses, h, ren_video_file="", item={} ):
    dialog_view = False
    torrent = False

    if os.path.isfile( torrent_file ):
        dialog_view = True
        torrent = True

    if download > 0:
        dialog_view = True
    if bkg_user and not extracted_rar:
        dialog_view = False
    
    if erase_file_path and erase_file_path != \
                            os.path.join( DOWNLOAD_PATH , "MCT-torrent-videos" ):
        ren_video_file = erase_file_path
    if filetools.isfile(ren_video_file) and filetools.split(ren_video_file)[0] != \
                            os.path.join( DOWNLOAD_PATH , "MCT-torrent-videos" ):
        ren_video_file = filetools.split(ren_video_file)[0]
    elif filetools.isdir(ren_video_file) and ren_video_file == \
                            os.path.join( DOWNLOAD_PATH , "MCT-torrent-videos" ):
        ren_video_file = ''

    # Actualizado .json de control de descargas
    if not torrent_file or item.downloadProgress == 0:
        item.downloadProgress = 0
        #log("##### .torrent borrado: %s" % erase_file_path)
    else:
        item.downloadProgress = 100
    torr.update_control(item, function='mct_remove_files')
    if item.downloadStatus in [2, 4] and item.downloadProgress in [100]:
        dialog_view = False
    
    if dialog_view and ren_video_file:
        if h.status().num_pieces >= tot_piece_set:
            d = xbmcgui.Dialog()
            ok = d.yesno(msg_header, '¿Borrarmos los archivos descargados? (completos)' + '\n' +  video_file)
        else:
            ok = True

        # -- SI -------------------------------------------------
        if ok:
            # -- Borrar archivo - torrent -----------------------
            if torrent:
                try:
                    os.remove( torrent_file )
                except:
                    pass
            # -- Borrar carpeta/archivos y sesión - vídeo -------
            try:
                ses.remove_torrent( h, 1 )
                ses_lt = False
            except:
                ses_lt = False
            try:
                if os.path.isdir(ren_video_file):
                    filetools.rmdirtree(ren_video_file, silent=True)
                elif os.path.exists(ren_video_file) and os.path.isfile(ren_video_file): 
                    os.remove(ren_video_file)
                log("##### erase_file_path: %s" % ren_video_file)
            except:
                log("##### erase_file_path: %s" % ren_video_file)

            log("### End session #########")
        else:
            # -- Borrar sesión ----------------------------------
            try:
                ses.remove_torrent( h )
                ses_lt = False
            except:
                ses_lt = False
            log("### End session #########")
    else:
        # -- Borrar sesión --------------------------------------
        try:
            ses.remove_torrent( h )
            ses_lt = False
        except:
            ses_lt = False
        # -- Borrar archivo - torrent -----------------------
        if torrent:
            try:
                os.remove( torrent_file )
            except:
                pass
        log("### End session #########")
        
    filetools.remove(filetools.join( DOWNLOAD_PATH , "MCT-torrent-videos",  '.' + \
                os.path.splitext(filetools.basename(torrent_file))[0].lower() + '.parts'), silent=True)

    return                        


# -- Descargar de la web los datos para crear el torrent --------
# -- Si queremos aligerar el script mct.py se puede importar la -
# -- función del conentor torrent.py                            -
def url_get(url, params={}, headers={}):
    from contextlib import closing

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"

    if params:
        url = "%s?%s" % (url, urllib.urlencode(params))

    req = urllib2.Request(url)
    req.add_header("User-Agent", USER_AGENT)

    for k, v in list(headers.items()):
        req.add_header(k, v)

    try:
        with closing(urllib2.urlopen(req)) as response:
            data = response.read()
            if response.headers.get("Content-Encoding", "") == "gzip":
                import zlib
                return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
            return data
    except:
        return None


# -- Contar las piezas contiguas completas del vídeo ------------
def count_completed_continuous_pieces(h, piece_set):
    not_zero = 0
    for i, _set in enumerate(piece_set):
        if not h.have_piece(_set): break
        else: not_zero = 1
    return i + not_zero


# -- Prioritarizar o seleccionar las piezas del archivo que se  -
# -- desea reproducir con 'file_priorities' estableciendo a 1   -
# -- el archivo deseado y a 0 el resto de archivos almacenando  -
# -- en una lista los índices de de las piezas del archivo      -
def set_priority_pieces(h, _index, video_file, video_size,
                        porcent4first_pieces, porcent4last_pieces, allocate):

    for i, _set in enumerate(h.file_priorities()):
        if i != _index and _index >= 0:
            #h.file_priority(i,0)
            xbmc.sleep(1000)
            h.file_priority(i,0)
        else:
            #h.file_priority(i,0)
            xbmc.sleep(1000)
            h.file_priority(i,1)

    piece_set = []
    x = 0
    for i, _set in enumerate(h.piece_priorities()):
        #log("***** Nº Pieza: %s: %s" % (i, str(_set)))
        if _set > 0:
            piece_set.append(i)
            x += 1
    log("***** Piezas %s : Activas: %s" % (str(i+1), str(x)))

    if not allocate:
        for i in range(0, porcent4first_pieces):
            h.set_piece_deadline(piece_set[i], 10000)

        for i in range(len(piece_set)-porcent4last_pieces, len(piece_set)):
            h.set_piece_deadline(piece_set[i], 10000)

    return piece_set


def decode_adfly(data):
    import base64
    ysmm = scrapertools.find_single_match(data, "var ysmm = '([^']+)'")
    left = ''
    right = ''
    for c in [ysmm[i:i+2] for i in range(0, len(ysmm), 2)]:
        left += c[0]
        right = c[1] + right

    decoded_url = base64.b64decode(left.encode() + right.encode())[2:].decode()
    return decoded_url


def encode(s):
    import unicodedata
    #log("### log ######")
    #for c in s:
    #    log("%s : %s" % (c, str(unicodedata.category(c))))
    #log("##############")
    #return s
    return str(''.join((c for c in unicodedata.normalize('NFD', unicode(s, 'utf-8')) if unicodedata.category(c) != 'Mn')))


def log(texto):
    if PY3:
        xbmc.log(texto, xbmc.LOGINFO)
    else:
        xbmc.log(texto, xbmc.LOGNOTICE)
