# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Horus by Caperucitaferoz based on previous work by:
# - Enen92 (https://github.com/enen92)
# - Joian (https://github.com/jonian)
#
# Thanks to those who have collaborated in any way, especially to:
# - @Canna_76
# - @AceStreamMOD (https://t.me/AceStreamMOD)
# - @luisma66 (tester raspberry)
#
# This file is part of Horus for Kodi
#
# Horus for Kodi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

from lib.utils import *

from acestream.engine import Engine
from acestream.stream import Stream

error_flag = False

class OSD(object):
    def __init__(self, stats):
        self.showing = False
        self.window = xbmcgui.Window(12901)
        self.stats = stats

        viewport_w, viewport_h = self._get_skin_resolution() #(1280, 720)
        posX = viewport_w - 305
        posY = 75

        window_w = 300
        window_h = 250
        font_max = 'font13'
        font_min = 'font10'

        # Background
        self.horus_background = xbmcgui.ControlImage(x=posX, y=posY, width=window_w, height=window_h,
                                                     filename=os.path.join(runtime_path, 'resources', 'media' , 'background.png'))
        # icono
        self.horus_icon = xbmcgui.ControlImage(x=posX + 25, y=posY + 15, width=38, height=28,
                                               filename=os.path.join(runtime_path, 'resources', 'media' , 'acestreamlogo.png'))
        # title
        self.horus_title = xbmcgui.ControlLabel(x=posX + 78, y=posY + 13, width=window_w - 10, height=30,
                                                label="Horus", font=font_max, textColor='0xFFEB9E17')
        # sep
        self.horus_sep1 = xbmcgui.ControlImage(x=posX + 5, y=posY + 55, width=window_w - 10, height=1,
                                               filename=os.path.join(runtime_path, 'resources', 'media', 'separator.png'))
        # Stats
        self.horus_status = xbmcgui.ControlLabel(x=posX + 25, y=posY + 80, width=window_w - 10, height=30, font=font_min, label=translate(30009) % '')
        self.horus_speed_down = xbmcgui.ControlLabel(x=posX + 25, y=posY + 100, width=window_w - 10, height=30, font=font_min, label=translate(30009) % 0)
        self.horus_speed_up = xbmcgui.ControlLabel(x=posX + 25, y=posY + 120, width=window_w - 10, height=30, font=font_min, label=translate(30011) % 0)
        self.horus_peers = xbmcgui.ControlLabel(x=posX + 25, y=posY + 140, width=window_w - 10, height=30, font=font_min, label=translate(30012) % 0)
        self.horus_downloaded = xbmcgui.ControlLabel(x=posX + 25, y=posY + 170, width=window_w - 10, height=30, font=font_min, label=translate(30013) % 0)
        self.horus_uploaded = xbmcgui.ControlLabel(x=posX + 25, y=posY + 190, width=window_w - 10, height=30, font=font_min, label=translate(30014) % 0)

        # sep
        self.horus_sep2 = xbmcgui.ControlImage(x=posX + 5, y=posY + window_h - 30, width=window_w - 10, height=1,
                                               filename=os.path.join(runtime_path, 'resources', 'media', 'separator.png'))

    def update(self,**kwargs):
        if self.showing:
            status = {'dl':translate(30007), 'prebuf': translate(30008) %(self.stats.progress) + '%'}
            self.horus_status.setLabel(translate(30009) % status.get(self.stats.status, self.stats.status))
            self.horus_speed_down.setLabel(translate(30010) % self.stats.speed_down)
            self.horus_speed_up.setLabel(translate(30011) % self.stats.speed_up)
            self.horus_peers.setLabel(translate(30012) % self.stats.peers)
            self.horus_downloaded.setLabel(translate(30013) % (self.stats.downloaded // 1048576))
            self.horus_uploaded.setLabel(translate(30014) % (self.stats.uploaded // 1048576))

    def show(self):
        self.window.addControl(self.horus_background)
        self.window.addControl(self.horus_icon)
        self.window.addControl(self.horus_title)
        self.window.addControl(self.horus_sep1)
        self.window.addControl(self.horus_status)
        self.window.addControl(self.horus_speed_down)
        self.window.addControl(self.horus_speed_up)
        self.window.addControl(self.horus_peers)
        self.window.addControl(self.horus_downloaded)
        self.window.addControl(self.horus_uploaded)
        self.window.addControl(self.horus_sep2)
        self.showing = True

    def hide(self):
        self.showing = False
        self.window.removeControl(self.horus_background)
        self.window.removeControl(self.horus_icon)
        self.window.removeControl(self.horus_title)
        self.window.removeControl(self.horus_sep1)
        self.window.removeControl(self.horus_status)
        self.window.removeControl(self.horus_speed_down)
        self.window.removeControl(self.horus_speed_up)
        self.window.removeControl(self.horus_peers)
        self.window.removeControl(self.horus_downloaded)
        self.window.removeControl(self.horus_uploaded)
        self.window.removeControl(self.horus_sep2)

    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET
        skin_path = translatePath("special://skin/")
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        try: res = tree.findall("./res")[0]
        except: res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])

    def close(self):
        try:
            self.hide()
        except:
            pass


class MyPlayer(xbmc.Player):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MyPlayer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        logger("MyPlayer init")
        self.total_Time = 0
        self.monitor = xbmc.Monitor()
        xbmc.Player().stop()
        while xbmc.Player().isPlaying() and not self.monitor.abortRequested():
            self.monitor.waitForAbort(1)


    def playStream(self, stream, title='', iconimage='', plot='', init_time=0.0):
        self.AVStarted = False
        self.is_active = True
        self.init_time = float(init_time)
        self.osd = OSD(stream.stats)

        status = 'failed'

        listitem = xbmcgui.ListItem()
        title = title or stream.filename or stream.id
        info = {'title': title}
        if plot:
            info['plot'] = plot
        listitem.setInfo('video', info )
        art = {'icon': iconimage if iconimage else os.path.join(runtime_path, 'resources', 'media', 'icono_aces_horus.png')}
        listitem.setArt(art)

        self.play(stream.playback_url, listitem)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False, updateListing = True, cacheToDisc = False)
        xbmc.executebuiltin('Dialog.Close(all,true)')

        show_stat = False
        while self.is_active and not self.monitor.abortRequested():
            try:
                self.current_time = self.getTime()
            except:
                pass
            if get_setting("show_osd"):
                """if show_stat:
                    # update stat
                    self.osd.update()"""

                if not show_stat and xbmc.getCondVisibility('Window.IsActive(videoosd)'):
                    #show windows OSD
                    self.osd.show()
                    stream.connect('stats::updated', self.osd.update)
                    show_stat = True

                elif not xbmc.getCondVisibility('Window.IsActive(videoosd)'):
                    # hide windows OSD
                    if self.osd.showing:
                        self.osd.hide()
                        stream.disconnect('stats::updated')
                    show_stat = False

            self.monitor.waitForAbort(1)

        if self.AVStarted:
            if self.current_time > 180:
                add_historial({'infohash': stream.infohash,
                                'title': title,
                                'icon': iconimage if iconimage else '',
                                'plot': plot})
                if stream.id:
                    set_setting("last_id", stream.id)

            if self.current_time >= 0.9 * self.total_Time:
                status = 'finished'
            else:
                status = 'stopped'

            self.osd.close()
            clear_cache()

        return status

    def onAVStarted(self):
        logger("PLAYBACK AVSTARTED")
        self.AVStarted = True
        self.total_Time = self.getTotalTime()
        if self.init_time:
            self.seekTime(self.init_time)

    def onPlayBackEnded(self):
        logger("PLAYBACK ENDED") # Corte de red o fin del video
        self.is_active = False

    def onPlayBackStopped(self):
        logger("PLAYBACK STOPPED") # Parado por el usuario o no iniciado por http 429
        self.is_active = False

    def onPlayBackError(self):
        logger("PLAYBACK ERROR")
        self.is_active = False

    def onPlayBackStarted(self):
        logger("PLAYBACK STARTED")

    def kill(self):
        logger("Play Kill")
        self.is_active = False


def get_historial():
    historial = list()
    settings_path= os.path.join(data_path, "historial.json")
    if os.path.isfile(settings_path):
        try:
            historial = load_json_file(settings_path)
        except Exception:
            logger("Error load_file", "error")

    return historial


def add_historial(contenido):
    historial = get_historial()
    settings_path = os.path.join(data_path, "historial.json")

    trobat = False
    for i in historial:
        if i['infohash'] == contenido['infohash']:
            trobat = True
            break

    if not trobat:
        historial.insert(0, contenido)
        dump_json_file(historial[:10], settings_path)


def clear_cache():
    aux = False
    home = '.'
    try:
        acestream_cachefolder = get_setting("acestream_cachefolder", None)
        if not acestream_cachefolder:
            if system_platform == "windows":
                home = os.getenv("SystemDrive") + r'\\'
                acestream_cachefolder = os.path.join(os.getenv("SystemDrive"), '\_acestream_cache_')
            elif system_platform == "linux":
                home = os.getenv("HOME")
                acestream_cachefolder = os.path.join(os.getenv("HOME"), '.ACEStream', 'cache', '.acestream_cache')
            else:
                home = "/storage/emulated/0/"
                acestream_cachefolder = '/storage/emulated/0/org.acestream.engine/.ACEStream/.acestream_cache'

        acestream_cachefolder = acestream_cachefolder if os.path.isdir(acestream_cachefolder) else None

        if not acestream_cachefolder:
            for root, dirnames, filenames in os.walk(home):
                if root.endswith(os.path.join('.ACEStream','cache')):
                    aux = root
                if re.search(r'.acestream_cache.?', root):
                    acestream_cachefolder = root
                    break

        if not acestream_cachefolder and aux:
            acestream_cachefolder = aux

        if acestream_cachefolder:
            set_setting("acestream_cachefolder", acestream_cachefolder)
            dirnames, filenames = xbmcvfs.listdir(acestream_cachefolder)
            for f in filenames:
                xbmcvfs.delete(os.path.join(acestream_cachefolder, f))
            logger("clear_cache")
        else:
            logger("clear_cache: cache not found", "error")

    except:
        logger("error clear_cache", "error")


def read_torrent(torrent,headers=None):
    import bencodepy
    import hashlib

    infohash = None

    try:
        if torrent.lower().startswith('http'):
            from six.moves import urllib_request

            if not headers:
                headers = dict()
            elif not isinstance(headers,dict):
                headers = eval(headers)

            if not 'User-Agent' in headers:
                headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'

            req = urllib_request.Request(torrent, headers=headers)
            torrent_file = urllib_request.urlopen(req).read()

        elif os.path.isfile(torrent):
            torrent_file = open(torrent, "rb").read()

        metainfo = bencodepy.decode(torrent_file)

        if not six.PY3:
            infohash = hashlib.sha1(bencodepy.encode(metainfo['info'])).hexdigest()
        else:
            infohash = hashlib.sha1(bencodepy.encode(metainfo[b'info'])).hexdigest()
        logger(infohash)

    except Exception as e:
        logger(e, 'error')

    return infohash


def acestreams(id=None, url=None, infohash=None, title="", iconimage="", plot=""):
    #logger(id)
    global error_flag
    player = None
    stream = None
    engine = None
    cmd_stop_acestream = None
    acestream_executable = None

    #url = 'http://dl.acestream.org/sintel/sintel.torrent'
    #url = 'https://files.grantorrent.nl/torrents/peliculas/Otra-vuelta-de-tuerca-(The-Turning)-(2020).avi53.torrent'
    #infohash = 'eebd63aa0a5edc49b253fc5741e49e32961d0f4f'


    # verificar argumentos
    if infohash:
        url = id = None
    elif url:
        infohash = id = None
    else:
        regex = re.compile(r'[0-9a-f]{40}\Z',re.I)
        if not regex.match(id):
            xbmcgui.Dialog().ok(HEADING, translate(30015))
            return


    if id and system_platform == 'android' and get_setting("reproductor_externo"):
        AndroidActivity = 'StartAndroidActivity("","org.acestream.action.start_content","","acestream:?content_id=%s")' % id
        logger("Abriendo " + AndroidActivity)
        xbmc.executebuiltin(AndroidActivity)
        return

    if not server.available:
        # Create an engine instance
        if system_platform == "windows":
            acestream_executable = os.path.join(get_setting("install_acestream"), 'ace_engine.exe')

        elif system_platform == "linux":
            if arquitectura == 'x86':
                if root:
                    # LibreElec x86
                    acestream_executable = os.path.join(get_setting("install_acestream"), 'acestream_chroot.start')
                    cmd_stop_acestream = ["pkill", "acestream"]
                else:
                    # Ubuntu, arch Linux, fedora, mint etc
                    if os.path.exists('/snap/acestreamplayer'):
                        acestream_executable = 'snap run acestreamplayer.engine'
                        cmd_stop_acestream = ["pkill", "acestream"]
                    else:
                        xbmcgui.Dialog().ok(HEADING,translate(30027))
                        return

            elif arquitectura == 'arm' and not root:
                try:
                    data = ''
                    with open("/etc/os-release") as f:
                        data = six.ensure_str(f.read())
                    if re.search('osmc|openelec|raspios|raspbian', data, re.I):
                        # osmc, openelec, raspios y raspbian
                        acestream_executable = 'sudo ' + os.path.join(get_setting("install_acestream"), 'acestream.start')
                        cmd_stop_acestream = ['sudo', os.path.join(get_setting("install_acestream"), 'acestream.stop')]
                except: pass

            else:
                # LibreELEC, coreElec , alexelec, etc...
                acestream_executable = os.path.join(get_setting("install_acestream"), 'acestream.start')
                cmd_stop_acestream = [os.path.join(get_setting("install_acestream"), 'acestream.stop')]

        elif system_platform == 'android':
            AndroidActivity = None
            if id:
                # Reproducir ID
                AndroidActivity = 'StartAndroidActivity("","org.acestream.action.start_content","","acestream:?content_id=%s")' % id
                logger("Abriendo " + AndroidActivity)
                xbmc.executebuiltin(AndroidActivity)
                return
            else:
                import glob
                for patron in ["/storage/emulated/0/Android/data/org.acestream.*", "/data/user/0/org.acestream.*"]:
                    org_acestream = glob.glob(patron)
                    if org_acestream:
                        AndroidActivity = 'StartAndroidActivity("%s")' % org_acestream[0].split('/')[-1]
                        break

            if AndroidActivity:
                if xbmcgui.Dialog().yesno(HEADING, translate(30041)):
                    logger("Abriendo " + AndroidActivity)
                    xbmc.executebuiltin(AndroidActivity)
                else:
                    return
            else:
                xbmcgui.Dialog().ok(HEADING, translate(30016))
                return

        logger("acestream_executable= %s" % acestream_executable)

        if cmd_stop_acestream:
            set_setting("cmd_stop_acestream", cmd_stop_acestream)

        if acestream_executable and not server.available:
            engine = Engine(acestream_executable)

        elif not acestream_executable and system_platform != 'android':
            logger("plataforma desconocida: %s" % system_platform)
            if not xbmcgui.Dialog().yesno(HEADING, translate(30016), nolabel=translate(30017), yeslabel=translate(30018)):
                return

    try:
        d = xbmcgui.DialogProgress()
        d.create(HEADING, translate(30033))
        timedown = time.time() + get_setting("time_limit")

        if not acestream_executable or system_platform == 'android':
            while not d.iscanceled() and not server.available and time.time() < timedown and error_flag == False:
                seg = int(timedown - time.time())
                progreso = int((seg * 100) / get_setting("time_limit"))
                line1 = translate(30033)
                line2 = translate(30006) % seg
                try:
                    d.update(progreso, line1, line2)
                except:
                    d.update(progreso, '\n'.join([line1, line2]))
                time.sleep(1)

            if not server.available:
                d.close()
                notification_error(translate(30019))
                raise Exception("accion cancelada o timeout")

        elif engine and not server.available:
            # Start engine if the local server is not available
            engine.connect(['error','error::subprocess'], notification_error)
            #engine.connect(['started', 'terminated'], notification_info)
            engine.start()

            # Wait for engine to start
            while not d.iscanceled() and (not engine.running or not server.available) and time.time() < timedown and error_flag == False:
                seg = int(timedown - time.time())
                progreso = int((seg * 100) / get_setting("time_limit"))
                line1 = translate(30033)
                line2 = translate(30006) % seg
                try:
                    d.update(progreso, line1, line2)
                except:
                    d.update(progreso, '\n'.join([line1, line2]))

                time.sleep(1)

            if d.iscanceled() or time.time() >= timedown or error_flag == True: # Tiempo finalizado o cancelado
                if engine.running:
                    engine.stop()
                d.close()
                if time.time() >= timedown:
                    notification_error(translate(30019))
                raise Exception("accion cancelada o timeout")

        hls = False
        if id:
            # Start a stream using an acestream channel ID
            stream = Stream(server, id=id)
        elif url:
            # Start a stream using an url
            hls = True
            stream = Stream(server, url=url)
        else:
            # Start a stream using an acestream infohash
            hls = True
            stream = Stream(server, infohash=infohash)

        stream.connect('error', notification_error)
        stream.connect(['started','stopped'], notification_info)
        stream.start(hls=hls)


        # Wait for stream to start
        timedown = time.time() + get_setting("time_limit")
        while not d.iscanceled() and time.time() < timedown and (not stream.status or stream.status != 'dl') and error_flag == False:
            if stream.status != 'prebuf':
                seg = int(timedown - time.time())
                progreso = int((seg * 100) / get_setting("time_limit"))
            else:
                progreso = stream.stats.progress
                timedown = time.time() + 100

            if not stream.status:
                line1 = translate(30034)
            elif stream.status == 'prebuf':
                line1 = translate(30008) %(progreso) + '%'
            elif stream.status == 'dl':
                line1 = translate(30007)
            else:
                line1 = stream.status

            line2 = translate(30010) % stream.stats.speed_down
            line3 = translate(30012) % stream.stats.peers
            try:
                d.update(progreso, line1, line2, line3)
            except:
                d.update(progreso, '\n'.join([line1, line2, line3]))

            time.sleep(0.25)

        d.close()
        if d.iscanceled() or time.time() >= timedown or error_flag == True:  # Tiempo finalizado o cancelado
            if error_flag:
                raise Exception("error flag")
            else:
                raise Exception("accion cancelada o timeout")

        # Open a media player to play the stream
        player = MyPlayer()
        player.playStream(stream, title, iconimage, plot)

    except Exception as e:
        logger(e, 'error')

    try:
        if player:
            player.kill()
    except: pass

    if stream:
        stream.stop()

    # stop Engine
    if get_setting("stop_acestream", False) or get_setting("linux_id") == 'ubuntu':
        kill_process()


def notification_info(*args,**kwargs):
    transmitter = kwargs['class_name']
    msg = kwargs['event_name']

    logger("%s: %s" %(transmitter, msg))
    #xbmcgui.Dialog().notification('Acestream %s' % transmitter, msg, os.path.join(runtime_path, 'resources', 'media', 'icono_aces_horus.png'))


def notification_error(*args,**kwargs):
    global error_flag
    transmitter = kwargs.get('class_name', ADDON_NAME)
    event = kwargs.get('event_name','')
    msg = args[0]
    error_flag = True

    logger("Error in %s: %s" % (transmitter, msg))

    if event != 'error::subprocess':
        xbmcgui.Dialog().notification('Error Acestream %s' % transmitter, msg,
                                      os.path.join(runtime_path, 'resources', 'media', 'error.png'))


def mainmenu():
    itemlist = list()

    itemlist.append(Item(
        label= translate(30020),
        action='play'
    ))

    itemlist.append(Item(
        label=translate(30038),
        action='search'
    ))

    if get_historial():
        itemlist.append(Item(
            label = translate(30037),
            action = 'historial'
        ))

    if server.available and system_platform != 'android':
        itemlist.append(Item(
            label= translate(30036),
            action='kill'
        ))

    itemlist.append(Item(
        label= translate(30021),
        action='open_settings'
    ))

    return itemlist


def search(url):
    from six.moves import urllib_request

    itemlist = list()
    ids = list()

    # Ejemplos de urls validas:
    #   https://fastestvpn.com/blog/acestream-channels/
    #   http://acetv.org/js/data.json
    #   https://raw.githubusercontent.com/digitaimadness/digitaimadness.github.io/59c454b198f65c6e17ae106f1312b8e0be204211/alpaca.tv/ace.world.m3u

    try:
        data = six.ensure_str(urllib_request.urlopen(url).read())
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        if data:
            if url.startswith('https://ipfs.io/'):
                patron = '<a href="(/ipfs/[^"]+acelive)">(\d*)'
                for ace,n in re.findall(patron, data, re.I):
                    itemlist.append(Item(label="Arenavisión Canal " + n,
                                         action='play',
                                         url="https://ipfs.io" + ace))
            else:
                try:
                    for n, it in enumerate(eval(re.findall('(\[.*?])', data)[0])):
                        label = it.get("name", it.get("title", it.get("label")))
                        id = it.get("id", it.get("url"))
                        id = re.findall('([0-9a-f]{40})', id, re.I)[0]
                        icon = it.get("icon", it.get("image", it.get("thumb")))

                        new_item = Item(label= label if label else translate(30030) % (n,id), action='play', id=id)

                        if icon:
                            new_item.icon = icon

                        itemlist.append(new_item)
                except:
                    for patron in [r'#EXTINF:-1.*?id="([^"]+)".*?([0-9a-f]{40})', '#EXTINF:-1,(.*?)http.*?([0-9a-f]{40})']:
                        for label, id in re.findall(patron, data):
                            itemlist.append(Item(label=label, action='play', id=id))
                        if itemlist: break

                    if not itemlist:
                        itemlist = []
                        for patron in [r"acestream://([0-9a-f]{40})", r'(?:"|>)([0-9a-f]{40})(?:"|<)']:
                            n = 1
                            for id in re.findall(patron, data, re.I):
                                if id not in ids:
                                    ids.append(id)
                                    itemlist.append(Item(label= translate(30030) % (n,id),
                                                         action='play',
                                                         id= id))
                                    n += 1
                            if itemlist: break
    except: pass

    if itemlist:
        return itemlist
    else:
        xbmcgui.Dialog().ok(HEADING,  translate(30031) % url)


def kill_process():
    cmd_stop_acestream = get_setting("cmd_stop_acestream")

    if system_platform == 'windows':
        os.system('taskkill /f /im ace_engine.exe')

    elif cmd_stop_acestream:
        logger("cmd_stop_acestream= %s" % cmd_stop_acestream)
        subprocess.call(cmd_stop_acestream)


    time.sleep(0.75)

    if not server.available:
        logger("Motor Acestream cerrado")
        xbmcgui.Dialog().notification(HEADING, translate(30035),
                                      os.path.join(runtime_path, 'resources', 'media', 'icono_aces_horus.png'))
        return True
    else:
        logger("Motor Acestream NO cerrado")
        xbmcgui.Dialog().notification(HEADING, translate(30040),
                                      os.path.join(runtime_path, 'resources', 'media', 'error.png'))
        return False


def run(item):
    itemlist = list()

    if not item.action:
        logger("Item sin acción")
        return

    if item.action == "mainmenu":
        itemlist = mainmenu()

    elif item.action == "kill":
        if kill_process():
            xbmc.executebuiltin('Container.Refresh')

    elif item.action == "historial":
        for it in get_historial():
            itemlist.append(Item(label= it.get('title'),
                                 action='play',
                                 infohash=it.get('infohash'),
                                 icon=it.get('icon'),
                                 plot=it.get('plot')))

    elif item.action == "search":
        url = xbmcgui.Dialog().input(translate(30032),
                get_setting("last_search", "http://acetv.org/js/data.json"))

        if url:
            itemlist = search(url)
            if itemlist:
                set_setting("last_search", url)
        else:
            return

    elif item.action == 'open_settings':
            xbmcaddon.Addon().openSettings()

    elif item.action == 'play':
        id = url = infohash = None

        if item.id:
            id =item.id
        elif item.url:
            url=item.url
        elif item.infohash:
            infohash=item.infohash
        else:
            last_id = get_setting("last_id", "a0270364634d9c49279ba61ae3d8467809fb7095")
            input = xbmcgui.Dialog().input(translate(30022), last_id if get_setting("remerber_last_id") else "")
            if re.findall('^(http|magnet)', input, re.I):
                url = input
            else:
                id = input

        if id:
            acestreams(id=id)
        elif url and url.lower().endswith('.torrent'):
            infohash = read_torrent(url)
            if infohash:
                acestreams(infohash=infohash)
        elif url and url.lower().startswith('magnet:'):
            infohash = re.findall('xt=urn:btih:([a-f0-9]+)', url, re.I)
            if infohash:
                acestreams(infohash=infohash[0])
        elif url:
            acestreams(url=url)
        elif infohash:
            acestreams(infohash=infohash)

        xbmc.executebuiltin('Container.Refresh')


    if itemlist:
        for item in itemlist:
            listitem = xbmcgui.ListItem(item.label or item.title)
            listitem.setInfo('video', {'title': item.label or item.title, 'mediatype': 'video'})
            listitem.setArt(item.getart())
            if item.plot:
                listitem.setInfo('video', {'plot': item.plot})

            if item.isPlayable:
                listitem.setProperty('IsPlayable', 'true')
                isFolder = False

            elif isinstance(item.isFolder, bool):
                isFolder = item.isFolder

            elif not item.action:
                isFolder = False

            else:
                isFolder = True

            xbmcplugin.addDirectoryItem(
                handle=int(sys.argv[1]),
                url='%s?%s' % (sys.argv[0], item.tourl()),
                listitem=listitem,
                isFolder= isFolder,
                totalItems=len(itemlist)
            )
        
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)


if __name__ == '__main__':
    if system_platform in ['linux', 'windows'] and not get_setting("install_acestream"):
        install_acestream()

    if sys.argv[2]:
        try:
            item = Item().fromurl(sys.argv[2])
        except:
            argumentos = dict()
            for c in sys.argv[2][1:].split('&'):
                k, v = c.split('=')
                argumentos[k] = urllib_parse.unquote_plus(six.ensure_str(v))

            logger("Llamada externa: %s" %argumentos)
            action = argumentos.get('action', '').lower()

            if action == 'play' and (argumentos.get('id') or argumentos.get('url') or argumentos.get('infohash')):
                if argumentos.get('url') and argumentos.get('url').lower().endswith('.torrent'):
                    infohash = read_torrent(argumentos.get('url'), argumentos.get('headers'))
                    if infohash:
                        argumentos['infohash'] = infohash
                        argumentos['url'] = None
                    else:
                        exit(0)
                elif argumentos.get('url') and argumentos.get('url').lower().startswith('magnet:'):
                    infohash = re.findall('xt=urn:btih:([a-f0-9]+)', argumentos.get('url'), re.I)
                    if infohash:
                        argumentos['infohash'] = infohash[0]
                        argumentos['url'] = None
                    else:
                        exit(0)

                acestreams(id=argumentos.get('id'),
                           url=argumentos.get('url'),
                           infohash=argumentos.get('infohash'),
                           title=argumentos.get('title'),
                           iconimage=argumentos.get('iconimage'),
                           plot=argumentos.get('plot'))

            elif action == 'install_acestream':
                if system_platform in ['linux', 'windows']:
                    install_acestream()
            exit (0)

    else:
        item = Item(action='mainmenu')

    run(item)




