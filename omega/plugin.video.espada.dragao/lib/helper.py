# -*- coding: utf-8 -*-
try:
    from kodi_six import xbmc as xbmc_, xbmcgui as xbmcgui_, xbmcplugin as xbmcplugin_, xbmcaddon as xbmcaddon_, xbmcvfs as xbmcvfs_
except:
    pass
import six as six_
if six_.PY3:
    from urllib.parse import urlparse as urlparse_, parse_qs as parse_qs_, parse_qsl as parse_qsl_, quote as quote_, unquote as unquote_, quote_plus as quote_plus_, unquote_plus as unquote_plus_, urlencode as urlencode_ #python 3
else:
    from urlparse import urlparse as urlparse_, parse_qs as parse_qs_, parse_qsl as parse_qsl_ #python 2
    from urllib import quote as quote_, unquote as unquote_, quote_plus as quote_plus_, unquote_plus as unquote_plus_, urlencode as urlencode_
import sys
import os as os_
import requests as rq
try:
    import json as json_
except ImportError:
    import simplejson as json_
from bs4 import BeautifulSoup as bfs
import base64

six = six_
requests = rq
json = json_
BeautifulSoup = bfs
try:
    xbmc = xbmc_
    xbmcgui = xbmcgui_
    xbmcplugin = xbmcplugin_
    xbmcaddon = xbmcaddon_
    xbmcvfs = xbmcvfs_
except:
    pass
urlparse = urlparse_
parse_qs = parse_qs_
parse_qsl = parse_qsl_
quote = quote_
unquote = unquote_
quote_plus = quote_plus_
unquote_plus = unquote_plus_
urlencode = urlencode_
os = os_

if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf-8')




try:
    class Progress_six:
        dp = xbmcgui.DialogProgress()
        @classmethod
        def create(cls,heading,msg):
            if six.PY3:
                cls.dp.create(str(heading),str(msg))
            else:
                cls.dp.create(str(heading),str(msg), '','')
        @classmethod
        def update(cls,update,heading):
            if six.PY3:
                cls.dp.update(int(update), str(heading))
            else:
                cls.dp.update(int(update), str(heading),'', '')

    class ProgressBG_six:
        dp = xbmcgui.DialogProgressBG()
        @classmethod
        def create(cls,heading,msg):
            if six.PY3:
                cls.dp.create(str(heading),str(msg))
            else:
                cls.dp.create(str(heading),str(msg), '','')
        @classmethod
        def update(cls,update,heading):
            if six.PY3:
                cls.dp.update(int(update), str(heading))
            else:
                cls.dp.update(int(update), str(heading),'', '')
except:
    pass

try:
    addon = xbmcaddon.Addon()
    addonName = addon.getAddonInfo('name')
    addonVersion = addon.getAddonInfo('version')
    localLang = addon.getLocalizedString
    homeDir = addon.getAddonInfo('path')
    translate = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath
    addonIcon = translate(os.path.join(homeDir, 'icon.png'))
    addonFanart = translate(os.path.join(homeDir, 'fanart.jpg'))
    profile = translate(addon.getAddonInfo('profile'))
    kversion = int(xbmc.getInfoLabel('System.BuildVersion').split(".")[0])
    plugin = sys.argv[0]
    base = plugin
    handle = int(sys.argv[1])
    dialog_ = xbmcgui.Dialog()
    executebuiltin = xbmc.executebuiltin
except:
    pass

def yesno(heading="",message="",nolabel="Nao",yeslabel="Sim"):
    if not heading:
        heading = addonName
    if six.PY2:
        q = dialog_.yesno(heading=heading, line1=message, nolabel=nolabel, yeslabel=yeslabel)
    else:
        q = dialog_.yesno(heading=heading, message=message, nolabel=nolabel, yeslabel=yeslabel)
    return q        


def route(r):
    try:
        route_decorator = r.split('/')[1] # function name from route
        plugin_route = base.split('/')[3:] # command from sys
        route_sys = plugin_route[0] # function name from sys
        def decorator(f):
            params = {}
            try:
                param_root = plugin_route[1] # params from sys
                param_root = unquote_plus(param_root).split('&')
                for command in param_root:
                    if '=' in command:
                        split_command = command.split('=')
                        key = unquote_plus(split_command[0])
                        value = unquote_plus(split_command[1])
                        params[key] = value
                    else:
                        params[command] = ''
            except:
                pass
            if not route_decorator and not route_sys:
                try:
                    f(params)
                except:
                    f()
            elif route_decorator == route_sys:
                try:
                    f(params)
                except:
                    f()
        return decorator
    except:
        def decorator(f):
            return f
        return decorator

def opensettings():
    addon.openSettings()

def getsetting(text):
    return addon.getSetting(text)

def setsetting(key,value):
    return addon.setSetting(key, value)

def exists(path):
    return xbmcvfs.exists(path)

def mkdir(path):
    try:
        xbmcvfs.mkdir(path)
    except:
        pass

def dialog(msg):
    dialog = xbmcgui.Dialog()
    dialog.ok(addonName, msg)

def progress_six():
    dp = Progress_six()
    return dp 

def progressBG_six():
    pDialog = ProgressBG_six()
    return pDialog

def select(name,items):
    op = dialog_.select(name, items)
    return op 

def log(txt):
    try:
        message = ''.join([addonName, ' : ', txt])
        xbmc.log(msg=message, level=xbmc.LOGDEBUG)
    except:
        pass

def string_utf8(string):
    if isinstance(string, bytes):
        return string

    return string.encode("utf-8", errors="ignore")

def to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)
    return text

def get_search_string(heading='', message=''):
    """Ask the user for a search string"""
    search_string = None
    keyboard = xbmc.Keyboard(message, heading)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_string = to_unicode(keyboard.getText())
    return search_string 

def input_text(heading='Put text'):
    vq = get_search_string(heading=heading, message="")        
    if ( not vq ): return False
    return vq

def infoDialog(message, iconimage='', time=3000, sound=False):
    heading = addonName
    if iconimage == '':
        iconimage = addonIcon
    elif iconimage == 'INFO':
        iconimage = xbmcgui.NOTIFICATION_INFO
    elif iconimage == 'WARNING':
        iconimage = xbmcgui.NOTIFICATION_WARNING
    elif iconimage == 'ERROR':
        iconimage = xbmcgui.NOTIFICATION_ERROR
    dialog_.notification(heading, message, iconimage, time, sound=sound)

def notify(msg):
    try:
        infoDialog(msg,iconimage='INFO') 
    except:
        pass

def addMenuItem(params={}, destiny='', folder=True):
    try:
        destiny = destiny.split('/')[1]
    except:
        pass
    name = params.get('name', '')
    description = params.get("description", "")
    originaltitle = params.get("originaltitle", "")        
    try:
        params.update({'name': string_utf8(name)})
    except:
        pass
    try:
        params.update({'description': string_utf8(description)})
    except:
        pass
    try:
        params.update({'originaltitle': string_utf8(originaltitle)})
    except:
        pass               
    u = 'plugin://%s/%s/%s'%(base.split("/")[2],destiny,quote_plus(urlencode(params)))
    iconimage = params.get("iconimage", "")
    fanart = params.get("fanart", "")
    codec = params.get("codec", "")
    playable = params.get("playable", "")
    duration = params.get("duration", "")
    imdbnumber = params.get("imdbnumber", "")
    if not imdbnumber:
        imdbnumber = params.get("imdb", "")
    aired = params.get("aired", "")
    genre = params.get("genre", "")
    season = params.get("season", "")
    episode = params.get("episode", "")
    year = params.get("year", "")
    mediatype = params.get("mediatype", "video")
    li=xbmcgui.ListItem(name)
    iconimage = iconimage if iconimage else addonIcon
    li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
    if kversion > 19:
        info = li.getVideoInfoTag()
        info.setTitle(name)
        info.setPlot(description)
        infotag = True
    else:
        li.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
        infotag = False
    if year:
        if infotag:
            info.setYear(int(year))
        else:
            li.setInfo('video', {'year': int(year)})
    if codec:
        if infotag:
            info.addVideoStream(xbmc.VideoStreamDetail(codec='h264'))
        else:
            li.addStreamInfo('video', {'codec': codec})
    if duration:
        if infotag:
            info.setDuration(int(duration))
        else:
            li.setInfo('video', {'duration': int(duration)})
    if originaltitle:
        if infotag:
            info.setOriginalTitle(str(originaltitle))
        else:
            li.setInfo('video', {'originaltitle': str(originaltitle) })
    if imdbnumber:
        if infotag:
            info.setIMDBNumber(str(imdbnumber))
        else:
            li.setInfo('video', {'imdbnumber': str(imdbnumber)})
    if aired:
        if infotag:
            info.setFirstAired(str(aired))
        else:
            li.setInfo('video', {'aired': str(aired)})
    if genre:
        if infotag:
            info.setGenres([str(genre)])
        else:
            li.setInfo('video', {'genre': str(genre)})
    if season:
        if infotag:
            info.setSeason(int(season))
        else:
            li.setInfo('video', {'season': int(season)})
    if episode:
        if infotag:
            info.setEpisode(int(episode))
        else:
            li.setInfo('video', {'episode': int(episode)})
    if mediatype:
        if infotag:
            info.setMediaType(str(mediatype))
        else:
            li.setInfo('video', {'mediatype': str(mediatype)})       
    if playable and folder == False and not playable == 'false':
        li.setProperty('IsPlayable', 'true')        
    if fanart:
        li.setProperty('fanart_image', fanart)
    else:
        li.setProperty('fanart_image', addonFanart)
    xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=li, isFolder=folder)

def play_video(params):
    name = params.get('name', '')
    url = params.get('url', '')
    sub = params.get('sub', '')
    description = params.get("description", "")
    originaltitle = params.get("originaltitle", "") 
    iconimage = params.get("iconimage", "")
    fanart = params.get("fanart", "")
    codec = params.get("codec", "")
    playable = params.get("playable", "")
    duration = params.get("duration", "")
    imdbnumber = params.get("imdbnumber", "")
    if not imdbnumber:
        imdbnumber = params.get("imdb", "")
    aired = params.get("aired", "")
    genre = params.get("genre", "")
    season = params.get("season", "")
    episode = params.get("episode", "")
    year = params.get("year", "")
    mediatype = params.get("mediatype", "video")
    li=xbmcgui.ListItem(name)
    iconimage = iconimage if iconimage else ''
    li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
    if kversion > 19:
        info = li.getVideoInfoTag()
        info.setTitle(name)
        info.setPlot(description)
        infotag = True
    else:
        li.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
        infotag = False
    if year:
        if infotag:
            info.setYear(int(year))
        else:
            li.setInfo('video', {'year': int(year)})
    if codec:
        if infotag:
            info.addVideoStream(xbmc.VideoStreamDetail(codec='h264'))
        else:
            li.addStreamInfo('video', {'codec': codec})
    if duration:
        if infotag:
            info.setDuration(int(duration))
        else:
            li.setInfo('video', {'duration': int(duration)})
    if originaltitle:
        if infotag:
            info.setOriginalTitle(str(originaltitle))
        else:
            li.setInfo('video', {'originaltitle': str(originaltitle) })
    if imdbnumber:
        if infotag:
            info.setIMDBNumber(str(imdbnumber))
        else:
            li.setInfo('video', {'imdbnumber': str(imdbnumber)})
    if aired:
        if infotag:
            info.setFirstAired(str(aired))
        else:
            li.setInfo('video', {'aired': str(aired)})
    if genre:
        if infotag:
            info.setGenres([str(genre)])
        else:
            li.setInfo('video', {'genre': str(genre)})
    if season:
        if infotag:
            info.setSeason(int(season))
        else:
            li.setInfo('video', {'season': int(season)})
    if episode:
        if infotag:
            info.setEpisode(int(episode))
        else:
            li.setInfo('video', {'episode': int(episode)})
    if mediatype:
        if infotag:
            info.setMediaType(str(mediatype))
        else:
            li.setInfo('video', {'mediatype': str(mediatype)})
    if fanart:
        li.setProperty('fanart_image', fanart)
    else:
        li.setProperty('fanart_image', addonFanart)                
    li.setPath(url)
    if sub:
        li.setSubtitles([sub])               
    if playable and not playable == 'false':
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
    else:
        xbmc.Player().play(item=url, listitem=li)

def setcontent(name):
    xbmcplugin.setContent(handle, name)  

def end():
    xbmcplugin.endOfDirectory(handle)

def setview(name):
    mode = {'Wall': '500',
            'List': '50',
            'Poster': '51',
            'Shift': '53',
            'InfoWall': '54',
            'WideList': '55',
            'Fanart': '502'
            }.get(name, '50')
    view = 'Container.SetViewMode(%s)'%mode
    xbmc.executebuiltin(view)   