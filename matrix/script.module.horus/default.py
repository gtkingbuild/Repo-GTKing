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

from lib.acestream.engine import Engine
from lib.acestream.stream import Stream

error_flag = False

class OSD(object):
    def __init__(self):
        self.showing = False
        self.window = xbmcgui.Window(12901)

        viewport_w, viewport_h = self._get_skin_resolution() #(1280, 720)
        posX = viewport_w - 305
        posY = 75

        window_w = 300
        window_h = 250
        font_max = 'font13'
        font_min = 'font10'

        # Background
        self._background = xbmcgui.ControlImage(x=posX, y=posY, width=window_w, height=window_h,
                                filename=os.path.join(runtime_path, 'resources', 'media' , 'background.png'))
        # icono
        self._icon = xbmcgui.ControlImage(x=posX + 25, y=posY + 15, width=38, height=28,
                                filename=os.path.join(runtime_path, 'resources', 'media' , 'acestreamlogo.png'))
        # title
        self._title = xbmcgui.ControlLabel(x=posX + 78, y=posY + 13, width=window_w - 10, height=30,
                                             label="Horus", font=font_max, textColor='0xFFEB9E17')
        # sep
        self._sep1 = xbmcgui.ControlImage(x=posX + 5, y=posY + 55, width=window_w - 10, height=1,
                                filename=os.path.join(runtime_path, 'resources', 'media', 'separator.png'))
        # Stats
        self._status = xbmcgui.ControlLabel(x=posX + 25, y=posY + 80, width=window_w - 10, height=30, font=font_min, label=translate(30009) % '')
        self._speed_down = xbmcgui.ControlLabel(x=posX + 25, y=posY + 100, width=window_w - 10, height=30, font=font_min, label=translate(30009) % 0)
        self._speed_up = xbmcgui.ControlLabel(x=posX + 25, y=posY + 120, width=window_w - 10, height=30, font=font_min, label=translate(30011) % 0)
        self._peers = xbmcgui.ControlLabel(x=posX + 25, y=posY + 140, width=window_w - 10, height=30, font=font_min, label=translate(30012) % 0)
        self._downloaded = xbmcgui.ControlLabel(x=posX + 25, y=posY + 170, width=window_w - 10, height=30, font=font_min, label=translate(30013) % 0)
        self._uploaded = xbmcgui.ControlLabel(x=posX + 25, y=posY + 190, width=window_w - 10, height=30, font=font_min, label=translate(30014) % 0)

        # sep
        self._sep2 = xbmcgui.ControlImage(x=posX + 5, y=posY + window_h - 30, width=window_w - 10, height=1,
                                filename=os.path.join(runtime_path, 'resources', 'media', 'separator.png'))

    def update(self, stats):
        if self.showing:
            status = {'dl':translate(30007), 'prebuf': translate(30008) %(stats.progress) + '%'}
            self._status.setLabel(translate(30009) % status.get(stats.status, stats.status))
            self._speed_down.setLabel(translate(30010) % stats.speed_down)
            self._speed_up.setLabel(translate(30011) % stats.speed_up)
            self._peers.setLabel(translate(30012) % stats.peers)
            self._downloaded.setLabel(translate(30013) % (stats.downloaded // 1048576))
            self._uploaded.setLabel(translate(30014) % (stats.uploaded // 1048576))


    def show(self):
        self.showing = True
        self.window.addControl(self._background)
        self.window.addControl(self._icon)
        self.window.addControl(self._title)
        self.window.addControl(self._sep1)
        self.window.addControl(self._status)
        self.window.addControl(self._speed_down)
        self.window.addControl(self._speed_up)
        self.window.addControl(self._peers)
        self.window.addControl(self._downloaded)
        self.window.addControl(self._uploaded)
        self.window.addControl(self._sep2)

    def hide(self):
        self.window.removeControl(self._background)
        self.window.removeControl(self._icon)
        self.window.removeControl(self._title)
        self.window.removeControl(self._sep1)
        self.window.removeControl(self._status)
        self.window.removeControl(self._speed_down)
        self.window.removeControl(self._speed_up)
        self.window.removeControl(self._peers)
        self.window.removeControl(self._downloaded)
        self.window.removeControl(self._uploaded)
        self.window.removeControl(self._sep2)
        self.showing = False


    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET
        skin_path = translatePath("special://skin/")
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        try: res = tree.findall("./res")[0]
        except: res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])


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
        self.osd = OSD()

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
                if show_stat:
                    # update stat
                    self.osd.update(stream.stats)

                if not show_stat and xbmc.getCondVisibility('Window.IsActive(videoosd)'):
                    #show windows OSD
                    self.osd.update(stream.stats)
                    self.osd.show()
                    show_stat = True

                elif not xbmc.getCondVisibility('Window.IsActive(videoosd)'):
                    # hide windows OSD
                    if self.osd.showing:
                        self.osd.hide()
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


def acestreams(id=None, url=None, infohash=None, title="", iconimage="", plot=""):
    #logger(id)
    global error_flag
    player = None
    stream = None
    engine = None
    cmd_stop_acestream = None
    acestream_executable = None

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

    try:
        data = six.ensure_str(urllib_request.urlopen(url).read())
        data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

        if data:
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
                itemlist = []
                for patron in [r"acestream://([0-9a-f]{40})", '(?:"|>)([0-9a-f]{40})(?:"|<)']:
                    n = 1
                    logger(re.findall(patron, data, re.I))
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
            last_id = get_setting("last_id", "fa93b7f9320c7958a5f64513d450cbff688fa886")
            input = xbmcgui.Dialog().input(translate(30022), last_id)
            if input.startswith('http'):
                url = input
            else:
                id = input

        if id:
            acestreams(id=id)
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
                acestreams(id=argumentos.get('id'),
                           url=argumentos.get('url'),
                           infohash=argumentos.get('infohash'),
                           title=argumentos.get('title'),
                           iconimage=argumentos.get('iconimage'),
                           plot=argumentos.get('plot'))

            elif action == 'install_acestream':
                if system_platform in ['linux', 'windows']:
                    set_setting("install_acestream", '')
                    install_acestream()
            exit (0)

    else:
        item = Item(action='mainmenu')

    run(item)

