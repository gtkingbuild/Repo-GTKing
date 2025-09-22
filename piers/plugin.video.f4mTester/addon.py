# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
from urllib.parse import urlparse, parse_qs, parse_qsl, quote, unquote, quote_plus, unquote_plus, urlencode #python 3
from app import PORT

URL_HLSRETRY = f"http://127.0.0.1:{PORT}/hlsretry?url="
URL_TS_DOWNLOADER = f"http://127.0.0.1:{PORT}/tsdownloader?url="

addon = xbmcaddon.Addon()
addonName = addon.getAddonInfo('name')
dialog_ = xbmcgui.Dialog()
translate = xbmcvfs.translatePath
homeDir = addon.getAddonInfo('path')
addonIcon = translate(os.path.join(homeDir, 'icon.png'))

kversion = int(xbmc.getInfoLabel('System.BuildVersion').split(".")[0])

def m3u8_to_ts(url):
    if '.m3u8' in url and '/live/' in url and int(url.count("/")) > 5:
        url = url.replace('/live', '').replace('.m3u8', '')
    return url

def dialog(msg):
    dialog = xbmcgui.Dialog()
    dialog.ok(addonName, msg)

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

def select(name,items):
    op = dialog_.select(name, items)
    return op     


def basename(p):
    """Returns the final component of a pathname"""
    i = p.rfind('/') + 1
    return p[i:]
    
def convert_to_m3u8(url):
    if '|' in url:
        url = url.split('|')[0]
    elif '%7C' in url:
        url = url.split('%7C')[0]
    if not '.m3u8' in url and not '/hl' in url and int(url.count("/")) > 4 and not '.mp4' in url and not '.avi' in url:
        parsed_url = urlparse(url)
        try:
            host_part1 = '%s://%s'%(parsed_url.scheme,parsed_url.netloc)
            host_part2 = url.split(host_part1)[1]
            url = host_part1 + '/live' + host_part2
            file = basename(url)
            if '.ts' in file:
                file_new = file.replace('.ts', '.m3u8')
                url = url.replace(file, file_new)
            else:
                url = url + '.m3u8'
                # file_new = file + '.m3u8'
                # new_url = url.replace(file, file_new)
        except:
            pass
    return url 

def player_hlsretry(name,url,iconimage,description):
    if name:
        name = 'F4MTESTER - HLSRETRY - ' + name
    else:
        name = 'F4MTESTER - HLSRETRY'
    url = unquote_plus(url)
    url = url.split('%7C')[0] if '%7C' in url else url
    url = url.split('|')[0] if '|' in url else url    
    url = convert_to_m3u8(url)
    url = URL_HLSRETRY + quote(url)
    li=xbmcgui.ListItem(name)
    iconimage = iconimage if iconimage else ''
    li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
    if kversion > 19:
        info = li.getVideoInfoTag()
        info.setTitle(name)
        info.setPlot(description)
    else:
        li.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    xbmc.Player().play(item=url, listitem=li)

def player_tsdownloader(name,url,iconimage,description):
    if name:
        name = 'F4MTESTER - TSDOWNLOADER - ' + name
    else:
        name = 'F4MTESTER - TSDOWNLOADER'
    url = unquote_plus(url)
    url = url.split('%7C')[0] if '%7C' in url else url
    url = url.split('|')[0] if '|' in url else url
    url = url.replace('live/', '').replace('.m3u8', '')
    url = URL_TS_DOWNLOADER + quote(url)
    li=xbmcgui.ListItem(name)
    iconimage = iconimage if iconimage else ''
    li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
    if kversion > 19:
        info = li.getVideoInfoTag()
        info.setTitle(name)
        info.setPlot(description)
    else:
        li.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    xbmc.Player().play(item=url, listitem=li)           


   


#### run addon ####
def run(params):
    stream_type = params.get('streamtype', None)
    iconimage = params.get('iconImage', params.get('thumbnailImage', addonIcon))
    name = params.get('name', 'F4mTester')
    url = params.get('url', '')
    description = params.get('description', '')
    if not stream_type:
        dialog('F4MTESTER PLAYER')
    elif stream_type !=None:
        if url:
            op = select('SELECT PLAYER', ['PROXY - HLSRETRY', 'PROXY - TSDOWNLOADER'])
            if op == 0:
                player_hlsretry(name,url,iconimage,description)
            elif op == 1:
                player_tsdownloader(name,url,iconimage,description)
                

