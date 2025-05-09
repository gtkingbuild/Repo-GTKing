import sys
import six
import os
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
from urllib.parse import urlparse, quote, unquote, quote_plus, unquote_plus, urlencode #python 3
from urllib.request import Request, urlopen, URLError  # Python 3
import re
import time
import server
import threading
import requests
import json

plugin = sys.argv[0]
handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonid = addon.getAddonInfo('id')
icon = addon.getAddonInfo('icon')
translate = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath
profile = translate(addon.getAddonInfo('profile')) if six.PY3 else translate(addon.getAddonInfo('profile')).decode('utf-8')
home = translate(addon.getAddonInfo('path')) if six.PY3 else translate(addon.getAddonInfo('path')).decode('utf-8')
fanart_default = os.path.join(home, 'fanart.png')
dialog = xbmcgui.Dialog()



def route(f):
    action_f = f.__name__
    params_dict = {}
    param_string = sys.argv[2]
    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
        for command in split_commands:
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = split_command[1]
                    try:
                        key = unquote_plus(key)
                    except:
                        pass
                    try:
                        value = unquote_plus(value)
                    except:
                        pass
                    params_dict[key] = value
                else:
                    params_dict[command] = ""
    action = params_dict.get('action')
    url = params_dict.get('url')
    if action is None and action_f == 'main':
        f()
    elif url and action is None and action_f == 'playitem':
        f(params_dict)
    elif action == action_f:
        f(params_dict)

def infoDialog(message, heading=addonname, iconimage='', time=3000, sound=False):
    if iconimage == '':
        iconimage = icon
    elif iconimage == 'INFO':
        iconimage = xbmcgui.NOTIFICATION_INFO
    elif iconimage == 'WARNING':
        iconimage = xbmcgui.NOTIFICATION_WARNING
    elif iconimage == 'ERROR':
        iconimage = xbmcgui.NOTIFICATION_ERROR
    dialog.notification(heading, message, iconimage, time, sound=sound)



def SetView(name):
    if name == 'Wall':
        try:
            xbmc.executebuiltin('Container.SetViewMode(500)')
        except:
            pass
    if name == 'List':
        try:
            xbmc.executebuiltin('Container.SetViewMode(50)')
        except:
            pass
    if name == 'Poster':
        try:
            xbmc.executebuiltin('Container.SetViewMode(51)')
        except:
            pass
    if name == 'Shift':
        try:
            xbmc.executebuiltin('Container.SetViewMode(53)')
        except:
            pass
    if name == 'InfoWall':
        try:
            xbmc.executebuiltin('Container.SetViewMode(54)')
        except:
            pass
    if name == 'WideList':
        try:
            xbmc.executebuiltin('Container.SetViewMode(55)')
        except:
            pass
    if name == 'Fanart':
        try:
            xbmc.executebuiltin('Container.SetViewMode(502)')
        except:
            pass

def get_kversion():
	full_version_info = xbmc.getInfoLabel('System.BuildVersion')
	baseversion = full_version_info.split(".")
	intbase = int(baseversion[0])
	# if intbase > 16.5:
	# 	log('HIGHER THAN 16.5')
	# if intbase < 16.5:
	# 	log('LOWER THAN 16.5')
	return intbase

def get_url(params):
    if params:
        url = '%s?%s'%(plugin, urlencode(params))
    else:
        url = ''
    return url


def item(params,folder=True):
    u = get_url(params)
    if not u:
        u = ''
    name = params.get("name")
    if name:
        name = name
    else:
        name = 'Unknow'
    iconimage = params.get("iconimage")
    if not iconimage:
        iconimage = params.get("iconImage", icon)
    fanart = params.get("fanart")
    if not fanart:
        fanart = fanart_default
    description = params.get("description")
    if not description:
        description = ''           
    playable = params.get("playable")
    liz = xbmcgui.ListItem(name)
    liz.setArt({'fanart': fanart, 'thumb': iconimage, 'icon': "DefaultFolder.png"})
    # if params.get("media"):
    if get_kversion() > 19:
        info = liz.getVideoInfoTag()
        info.setTitle(name)
        info.setMediaType('video')
        info.setPlot(description)
    else:    
        liz.setInfo(type="Video", infoLabels={"Title": name, 'mediatype': 'video', "Plot": description})
    # else:
    #     liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})                                                  
    if playable:
        if playable == 'true':
            liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=handle, url=u, listitem=liz, isFolder=folder)
    return ok


class MyPlayer(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)
    def play(self, url, listitem):
        #print 'Now im playing... %s' % url
        xbmc.Player().play(url, listitem)        
    def onPlayBackEnded(self):
        #Will be called when xbmc stops playing a file
        server.thread_stop()
    def onPlayBackStopped(self):
        # Will be called when user stops xbmc playing a file
        server.thread_stop()

class MyPlayer2(xbmc.Player):

    def __init__ (self):
        xbmc.Player.__init__(self)

    def play(self, url, li):
        #print 'Now im playing... %s' % url
        # self.stopPlaying.clear()
        # runningthread=thread.start_new_thread(xbmc.Player().play(item=url, listitem=li),(parar,))
        progress = xbmcgui.DialogProgress()
        # import checkbad
        # checkbad.do_block_check(False)

        #progress.create('Conectando...')
        progress.create('Estabilizador','Conectando...')
        # stream_delay = 1
        #progress.update( 20, "", 'Aguarde...', "" )
        # xbmc.sleep(stream_delay*100)
        #progress.update( 100, "", 'Carregando transmissão...', "" )
        prog=0
        xbmc.sleep(2000)


        
        xbmc.Player().play(item=url, listitem=li)
        count = 0
        while not xbmc.Player().isPlaying() and not xbmc.Monitor().abortRequested():
            xbmc.sleep(200)
            progress.update(prog+10,'Carregando transmissão...')
            prog=prog+10
            count +=10
            if count == 50 and xbmc.Player().isPlaying():
                break


        progress.close()


    def onPlayBackEnded( self ):
        # Will be called when xbmc stops playing a file
        print("seting event in onPlayBackEnded " )
        threading.Event()

        # self.stopPlaying.set()
        # thread.exit()
        # iniciavideo().stop()

        #print "stop Event is SET" 
    def onPlayBackStopped( self ):
        # Will be called when user stops xbmc playing a file
        print("seting event in onPlayBackStopped ") 
        threading.Event()
        # self.stopPlaying.set()
        # thread.exit()
        # iniciavideo().stop()

        #print "stop Event is SET"
        # 
class iniciavideo():
    
    def tocar(url, li):

        
        # parar=threading.Event()
        # parar.clear()   
        mplayer = MyPlayer2()    
        # iniciavideo().stop()
        # mplayer.stopPlaying = parar

        mplayer.play(url,li)


        # thread.start_new_thread(mplayer.play,(url,li))
        
        # mplayer.play(url,listitem)

        firstTime=True
        played=False

        
        while True:
            # if parar.isSet():            
                # break
            if xbmc.Player().isPlaying():
                played=True
            xbmc.log('Sleeping...')
            xbmc.sleep(1000)
            if firstTime:
                xbmc.executebuiltin('Dialog.Close(all,True)')
                firstTime=False
                # parar.isSet()
                # thread.exit()
                # iniciavideo().stop()


                    #print 'Job done'
        # return played
    
    def stop(self):
        threading.Event()

        

def monitor():
    while True:
        #if not xbmc.Player().isPlaying():
        #if xbmc.getCondVisibility("Player.HasMedia") == False:
            #server.mediaserver().stop()
        if not xbmc.Player().isPlaying():
            server.thread_stop()
            break

def req(url):
    try:
        r = requests.get(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'},timeout=20)
        return r.text
    except:
        src = ''
        return src
    
def re_me(data, re_patten):
    match = ''
    m = re.search(re_patten, data)
    if m != None:
        match = m.group(1)
    else:
        match = ''
    return match    

@route
def playlist(param):
    url = param.get('url', '')
    infoDialog('CARREGANDO AGUARDE...', iconimage='INFO')
    data = req(url)
    if re.search("#EXTM3U",data) or re.search("#EXTINF",data):
        xbmcplugin.setContent(handle, 'videos')
        content = data.rstrip()
        match1 = re.compile(r'#EXTINF:.+?tvg-logo="(.*?)".+?group-title="(.*?)",(.*?)[\n\r]+([^\r\n]+)').findall(content)
        if match1:
            group_list = []
            for thumbnail,cat,channel_name,stream_url in match1:
                if not '.mp4' in stream_url and not '.mkv' in stream_url and not '.avi' in stream_url and not '.wmv' in stream_url and not '.mp3' in stream_url:
                    if not cat in group_list:
                        group_list.append(cat)
                        try:
                            cat = cat.encode('utf-8', 'ignore')
                        except:
                            pass
                        item({'name': cat, 'action': 'playlist2', 'url': url, 'iconimage': ''})
        elif not match1:
            match2 = re.compile(r'#EXTINF:(.+?),(.*?)[\n\r]+([^\r\n]+)').findall(content)
            group_list = []
            if match2:
                for other,channel_name,stream_url in match2:
                    if not '.mp4' in stream_url and not '.mkv' in stream_url and not '.avi' in stream_url and not '.wmv' in stream_url and not '.mp3' in stream_url:
                        if 'tvg-logo' in other:
                            thumbnail = re_me(other,'tvg-logo=[\'"](.*?)[\'"]')
                            if thumbnail:
                                if not thumbnail.startswith('http'):
                                    thumbnail = ''
                            else:
                                thumbnail = ''
                        else:
                            thumbnail = ''
                        if 'group-title' in other:
                            cat = re_me(other,'group-title=[\'"](.*?)[\'"]')
                        else:
                            cat = ''
                        if cat:
                            if not cat in group_list:
                                group_list.append(cat)
                                try:
                                    cat = cat.encode('utf-8', 'ignore')
                                except:
                                    pass
                                item({'name': cat, 'action': 'playlist2', 'url': url, 'iconimage': ''})
                        else:
                            stream_url = stream_url.replace(' ', '').replace('\r', '').replace('\n', '')
                            item({'name': channel_name, 'action': 'playitem', 'url': stream_url, 'iconimage': thumbnail},folder=False)
            else:
                infoDialog('Playlist indisponivel', iconimage='INFO')
        xbmcplugin.endOfDirectory(handle)
                                      
@route
def playlist2(param):
    name = param.get('name', '')
    url = param.get('url', '')
    try:
        name = name.decode('utf-8')
    except:
        pass
    infoDialog('CARREGANDO AGUARDE...', iconimage='INFO')    
    data = req(url)
    if re.search("#EXTM3U",data) or re.search("#EXTINF",data):
        xbmcplugin.setContent(handle, 'videos')
        content = data.rstrip()
        match1 = re.compile(r'#EXTINF:.+?tvg-logo="(.*?)".+?group-title="(.*?)",(.*?)[\n\r]+([^\r\n]+)').findall(content)
        if match1:
            group_list = []
            for thumbnail,cat,channel_name,stream_url in match1:
                if not '.mp4' in stream_url and not '.mkv' in stream_url and not '.avi' in stream_url and not '.wmv' in stream_url and not '.mp3' in stream_url: 
                    if cat == name:
                        stream_url = stream_url.replace(' ', '').replace('\r', '').replace('\n', '')
                        item({'name': channel_name, 'action': 'playitem', 'url': stream_url, 'iconImage': thumbnail},folder=False)
        elif not match1:
            match2 = re.compile(r'#EXTINF:(.+?),(.*?)[\n\r]+([^\r\n]+)').findall(content)
            group_list = []
            if match2:
                for other,channel_name,stream_url in match2:
                    if not '.mp4' in stream_url and not '.mkv' in stream_url and not '.avi' in stream_url and not '.wmv' in stream_url and not '.mp3' in stream_url:
                        if 'tvg-logo' in other:
                            thumbnail = re_me(other,'tvg-logo=[\'"](.*?)[\'"]')
                            if thumbnail:
                                if not thumbnail.startswith('http'):
                                    thumbnail = ''
                            else:
                                thumbnail = ''
                        else:
                            thumbnail = ''
                        if 'group-title' in other:
                            cat = re_me(other,'group-title=[\'"](.*?)[\'"]')
                        else:
                            cat = ''
                        if cat:
                            if cat == name:
                                stream_url = stream_url.replace(' ', '').replace('\r', '').replace('\n', '')
                                item({'name':channel_name,'mode': 'playitem', 'url': stream_url, 'iconImage': thumbnail},folder=False)                          
            else:
                infoDialog('Playlist indisponivel', iconimage='INFO')
        xbmcplugin.endOfDirectory(handle)

def is_xtream_codes(url):
    try:
        if int(url.count(":")) == 2:
            return True
    except:
        pass
    return False

def m3u8_to_ts(url):
    if '.m3u8' in url and '/live/' in url and int(url.count("/")) > 5:
        url = url.replace('/live', '').replace('.m3u8', '')
    return url

def ffmpeg_direct(url,name,iconImage):
    try:
        url = unquote_plus(url)
    except:
        pass
    try:
        url = unquote(url)
    except:
        pass
    referer = False
    if not '|' in url:
        headers = '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36&Connection=keep-alive'
    else:
        try:
            url_split = url.split('|')
            url = url_split[0]
            #headers = '|' + url_split[1]
            try:
                headers = unquote_plus(url_split[1])
            except:
                pass
            try:
                headers = unquote(url_split[1])
            except:
                pass 
            headers = '|' + headers
            if not '&Connection' in headers:
                headers = headers + '&Connection=keep-alive'
        except:
            headers = False 
            
    plugin = xbmcvfs.translatePath('special://home/addons/inputstream.ffmpegdirect')
    if os.path.exists(plugin)==False:
        try:
            xbmc.executebuiltin('InstallAddon(inputstream.ffmpegdirect)', wait=True)
        except:
            pass
    if not name:
        name = "F4mTester"
    name = name + ' - inputstream'
    li=xbmcgui.ListItem(name)
    if iconImage:
        li.setArt({"icon": "DefaultVideo.png", "thumb": iconImage})
    if not '.mp4' in url and not '.mp3' in url and not '.mkv' in url and not '.avi' in url and not '.rmvb' in url:
        if os.path.exists(plugin)==True:
            # if headers:
            #     url = m3u8_to_ts(url) + headers
            # else:
            #     url = m3u8_to_ts(url)
            # url,stream = ts_to_m3u8(url)
            # #url = url + headers
            #url = m3u8_to_ts(url)
            urlbase,stream = ts_to_m3u8(url)
            url = urlbase + headers
            li.setProperty('inputstream', 'inputstream.ffmpegdirect')
            li.setProperty('IsPlayable', 'true')
            if '.m3u8' in url:
                li.setContentLookup(False)
                li.setMimeType('application/vnd.apple.mpegurl')
                li.setProperty('inputstream.ffmpegdirect.mime_type', 'application/vnd.apple.mpegurl')
                li.setProperty('ForceResolvePlugin','false')
                # li.setProperty('inputstream', 'inputstream.adaptive')
                # li.setProperty('inputstream.ffmpegdirect.manifest_type','hls')
            else:
                # li.setContentLookup(True)
                li.setMimeType('video/mp2t')
                li.setProperty('inputstream.ffmpegdirect.mime_type', 'video/mp2t')
                # li.setProperty('ForceResolvePlugin','true')
            # li.setProperty('http-reconnect', 'true')
            # li.setProperty('TotalTime', '3600')
            li.setProperty('inputstream.ffmpegdirect.stream_mode', 'catchup')
            # li.setProperty('inputstream.ffmpegdirect.timezone_shift', '20')
            li.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'true')
            li.setProperty('inputstream.ffmpegdirect.is_catchup_stream', 'catchup')
            li.setProperty('inputstream.ffmpegdirect.catchup_granularity', '60')
            li.setProperty('inputstream.ffmpegdirect.catchup_terminates', 'true')
            if is_xtream_codes(urlbase):            
                li.setProperty('inputstream.ffmpegdirect.open_mode', 'curl')
            # li.setProperty('inputstream.ffmpegdirect.playback_as_live', 'true')
            # if '.m3u8' in url:             
                # li.setProperty('inputstream.ffmpegdirect.manifest_type','hls') 
            #li.setProperty('inputstream.ffmpegdirect.manifest_type','ism')
            #print('aqui', url)                
            li.setProperty('inputstream.ffmpegdirect.default_url',url)
            li.setProperty('inputstream.ffmpegdirect.catchup_url_format_string',url)
            li.setProperty('inputstream.ffmpegdirect.programme_start_time','1')
            li.setProperty('inputstream.ffmpegdirect.programme_end_time','19')
            li.setProperty('inputstream.ffmpegdirect.catchup_buffer_start_time','1')
            li.setProperty('inputstream.ffmpegdirect.catchup_buffer_offset','1') 
            li.setProperty('inputstream.ffmpegdirect.default_programme_duration','19')
            li.setPath(url)
        else:
            url = url + headers
            li.setPath(url)
    # xbmc.Player().play(item=url, listitem=li)
    if get_kversion() > 19:
        info = li.getVideoInfoTag()
        info.setTitle(name)
    else:
        li.setInfo(type="Video", infoLabels={"Title": name, "Plot": ""})
    t1 = threading.Thread(target=iniciavideo.tocar,args=(url,li))
    t1.start()
    # t1.join()

def basename(p):
    """Returns the final component of a pathname"""
    i = p.rfind('/') + 1
    return p[i:]

def ts_to_m3u8(url):
    stream = False
    # xbmc.sleep(500)

    if not '.m3u8' in url and int(url.count(":")) == 2 and int(url.count("/")) > 4:
        url_parsed = urlparse(url)
        try:
            host_part1 = '%s://%s'%(url_parsed.scheme,url_parsed.netloc)
            host_part2 = url.split(host_part1)[1]
            url = host_part1 + '/live' + host_part2
            url_no_param = url
            try:
                url_no_param = host_part2.split('&')[0]
            except:
                pass
            try:
                url_no_param = host_part2.split('|')[0]
            except:
                pass         
                
            file = basename(url_no_param)
            try:
                file = file.split('&')[0]
            except:
                pass
            try:
                file = file.split('|')[0]
            except:
                pass
            if '.ts' in file:
                file_new = file.replace('.ts', '.m3u8')
                url = url.replace(file, file_new)
            else:
                file_new = file + '.m3u8'
                url = url.replace(file, file_new)
            stream = 'HLSRETRY'
        except:
            pass
    return url,stream

def playF4mLink(url,name,proxy=None,use_proxy_for_chunks=False,auth_string=None,streamtype='HDS',setResolved=False,swf="", callbackpath="", callbackparam="",referer="", origin="", cookie="", iconImage="",maxbitrate=0, simpleDownloader=False):
    from F4mProxy import f4mProxyHelper
    player=f4mProxyHelper()
    if not name:
        name = "F4mTester"
    name = name + ' - F4mProxy'
    #progress = xbmcgui.DialogProgress()
    #progress.create('Starting local proxy')
    try:
        url = unquote_plus(url)
    except:
        pass
    try:
        url = unquote(url)
    except:
        pass    
    if not '|' in url:
        headers = '|User-Agent='+quote('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')+'&Connection='+quote('keep-alive')
    else:
        try:
            url_split = url.split('|')
            url = url_split[0]
            headers = '|' + url_split[1]
            # try:
            #     headers = unquote_plus(url_split[1])
            # except:
            #     pass
            # try:
            #     headers = unquote(url_split[1])
            # except:
            #     pass 
            #headers = '|' + headers
            if not '&Connection' in headers:
                headers = headers + '&Connection='+quote('keep-alive')
        except:
            headers = False    
    url,stream = ts_to_m3u8(url)
    url = url + headers   
    if stream:
        streamtype = stream        

    if setResolved:
        urltoplay,item=player.playF4mLink(url, name, proxy, use_proxy_for_chunks,maxbitrate,simpleDownloader,auth_string,streamtype,setResolved,swf,callbackpath, callbackparam,referer,origin,cookie,iconImage)
        item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

    else:
        xbmcplugin.endOfDirectory(handle, cacheToDisc=False)        
        player.playF4mLink(url, name, proxy, use_proxy_for_chunks,maxbitrate,simpleDownloader,auth_string,streamtype,setResolved,swf,callbackpath, callbackparam,referer,origin,cookie,iconImage)


def proxy2_thread(name,iconImage,url_to_play):
    if not name:
        name = 'F4mTester'
    name = name + ' - Proxy 2'
    try:
        liz = xbmcgui.ListItem(name)
        liz.setPath(url_to_play)
        if iconImage:
            liz.setArt({"icon": iconImage, "thumb": iconImage})
        else:
            liz.setArt({"icon": icon, "thumb": icon})
        if get_kversion() > 19:
            info = liz.getVideoInfoTag()
            info.setTitle(name)
        else:                  
            liz.setInfo(type='video', infoLabels={'Title': name})
            liz.setMimeType("application/vnd.apple.mpegurl")
        liz.setContentLookup(False) 
        mplayer = MyPlayer()
        mplayer.play(url_to_play,liz)
    except:
        pass

def proxy2_player(url,name,iconImage):
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
    url_to_play = server.prepare_url(url)
    infoDialog('ABRINDO PROXY...',iconimage='INFO', time=6000)
    server.mediaserver().start()
    t1 = threading.Thread(target=proxy2_thread, args=(name,iconImage,url_to_play))
    t1.start()
    count = 0
    while not xbmc.Player().isPlaying():
        count += 1
        time.sleep(1)
        if count == 12:
            break
    t2 = threading.Thread(target=monitor)
    t2.start()                          

                            
@route
def main():    
    xbmcplugin.setContent(handle, 'movies')
    item({'name': 'MINHAS PLAYLISTS', 'action': 'myplaylists'})
    item({'name': 'AJUSTES', 'action': 'settings'})
    xbmcplugin.endOfDirectory(handle)
    SetView('WideList') 

@route
def myplaylists(param):
    listas_disponiveis = []
    for i in range(10):
        i = i + 1
        tag = 'lista' + str(i)
        if 'http' in addon.getSetting(tag):
            listas_disponiveis.append(addon.getSetting(tag))
    if listas_disponiveis:
        for n, i in enumerate(listas_disponiveis):
            n = n + 1
            name = 'LISTA ' + str(n)
            item({'name': name, 'action': 'playlist', 'url': i})
        xbmcplugin.endOfDirectory(handle)
        SetView('WideList')
    else:
        infoDialog('SEM PLAYLIST ADICIONADA', iconimage='INFO')  

@route
def settings(param):
    addon.openSettings()


@route
def playitem(param):
    name = param.get('name', '')
    url = param.get('url','')
    iconImage = param.get('iconImage', '')
    proxy_string = param.get('proxy', None)
    auth_string = param.get('auth', '')
    streamtype = param.get('streamtype', 'HDS')
    swf = param.get('swf', None)
    callbackpath = param.get('callbackpath', '')
    callbackparam = param.get('callbackparam', '')
    referer = param.get('referer', '')
    origin = param.get('origin', '')
    cookie = param.get('cookie', '')
    try:
        proxy_use_chunks_temp = param.get('proxy_for_chunks')
        proxy_use_chunks=json.loads(proxy_use_chunks_temp)
    except:
        proxy_use_chunks=True
    try:
        simpleDownloader_temp = param.get("simpledownloader")
        simpleDownloader=json.loads(simpleDownloader_temp)
    except:
        simpleDownloader=False
    try:
        maxbitrate = param.get("maxbitrate")
        maxbitrate = int(maxbitrate)
    except:
        maxbitrate = 0
    try:
        setResolved = param.get("setresolved")
        setResolved=json.loads(setResolved)
    except:
        setResolved=False
    player_type = int(addon.getSetting("player_type"))
    ask = addon.getSetting("ask")
    if url:
        if 'plugin://' in url:
            xbmc.executebuiltin('RunPlugin(%s)'%url)
        else:
            confirmation = True
            if ask == 'true':
                index = dialog.select('Selecione um player', ['inputstream.ffmpegdirect', 'F4mProxy', 'Proxy 2'])
                if index >= 0:
                    player_type = index
                else:
                    confirmation = False
            if player_type == 0 and confirmation == True:
                ffmpeg_direct(url,name,iconImage)
            elif player_type == 1 and confirmation == True:
                playF4mLink(url,name,proxy_string,proxy_use_chunks,auth_string,streamtype,setResolved,swf,callbackpath,callbackparam,referer,origin,cookie,iconImage,maxbitrate,simpleDownloader)
            elif player_type == 2 and confirmation == True:
                proxy2_player(url,name,iconImage)