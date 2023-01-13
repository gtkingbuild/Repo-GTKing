# -*- coding: utf-8 -*-
import sys, re, requests, time, os, xbmcplugin, xbmcgui, xbmc, json, utils
groupfile = os.path.join(utils.addonpath,"groups")
favoritenfile = os.path.join(utils.addonpath,"tvfavoriten")
url="https://www2.vavoo.to/live2/index"
home = xbmcgui.Window(10000)

def getchannels():
    try:
        with open(groupfile, "r") as k:
            group = json.load(k)
    except:
        group = choose()
    chanfile = home.getProperty('chanfile')
    if chanfile:
        r = json.loads(chanfile)
        if r.get('ValidUntil', 0) > int(time.time()):
            return r.get('channels')
    channels={}
    for c in requests.get(url, params={'output': 'json'}).json():
        if "DE :" in c["name"] or c["group"] in group:
            name = re.sub('( (SD|HD|FHD|UHD|H265))?( \\(BACKUP\\))? \\(\\d+\\)$', '', c['name'])
            name = re.sub("\(.*\)", "", name)
            name = name.replace('EINS', '1').replace('ZWEI', '2').replace('DREI', '3').replace('SIEBEN', '7').replace('DE : ', '').replace(' |C', '').replace(' |E', '').replace(' FHD', '').replace(' HD', '').replace(' 1080', '').replace(' AUSTRIA', '').replace(' GERMANY', '').replace(' DEUTSCHLAND', '').replace(' |D', '').replace('HEVC', '').replace('RAW', '').replace('  ', ' ').replace("TNT", "WARNER").replace(' SD', '').replace('  YOU', '').replace('.', '').replace('III', '3').replace('II', '2').strip()
            if "1-2-3" in name: name = "1-2-3 TV"
            name = "EURONEWS" if "EURONEWS" in name else name
            name = "NICKELODEON" if "NICKEL" in name else name
            if "ORF" in name:
                name = "ORF SPORT" if "SPORT" in name else name
                if "3" in name: name = "ORF 3"
                if "2" in name: name = "ORF 2"
                if "1" in name: name = "ORF 1"
                if "I" in name: name = "ORF 1"
            if "AXN" in name: name = "AXN"
            if "SONY" in name: name = "SONY CHANNEL"
            if "HEIMA" in name: name = "HEIMATKANAL"
            if "SIXX" in name: name = "SIXX"
            if "REPLAY" in name or "FOX" in name: name = "SKY REPLAY"
            if "SWR" in name: name = "SWR"
            if "CENTRAL" in name or "VIVA" in name: name = "VIVA"
            if "BR" in name and "FERNSEHEN" in name: name = "BR"
            if "DMAX" in name: name = "DMAX"
            if "DISNEY" in name: name = "DISNEY CHANNEL"
            if "KINOWELT" in name: name = "KINOWELT"
            if "MDR" in name: name = "MDR"
            if "RBB" in name: name = "RBB"
            if "SERVUS" in name: name = "SERVUS TV"
            if "NITRO" in name: name = "RTL NITRO"
            if "RTL" in name:
                if "CRIME" in name: name = "RTL CRIME"
                elif "2" in name: name = "RTL 2"
                elif "UP" in name: name = "RTL UP"
                elif "+" in name: name = "RTL UP"
                elif "PLUS" in name: name = "RTL UP"
                elif "PASSION" in name: name = "RTL PASSION"
                elif "NITRO" in name: name = "RTL NITRO"
                elif "LIVING" in name: name = "RTL LIVING"
                else: name = "RTL"
            if "UNIVERSAL" in name: name = "UNIVERSAL TV"
            if "WDR" in name: name = "WDR"
            if "PLANET" in name: name = "PLANET"
            if "SYFY" in name: name = "SYFY"
            if "E!" in name: name = "E! ENTERTAINMENT"
            if "ENTERTAINMENT" in name: name = "E! ENTERTAINMENT"
            if "STREET" in name: name = "13TH STREET"
            if "WUNDER" in name: name = "WELT DER WUNDER"
            if "KAB" in name:
                if "CLA" in name: name = "KABEL 1 CLASSICS"
                elif "DOKU" in name: name = "KABEL 1 DOKU"
                else: name = "KABEL 1"
            elif "PRO" in name:
                if "FUN" in name: name = "PRO 7 FUN"
                elif "MAXX" in name: name = "PRO 7 MAXX"
                else: name = "PRO 7"
            if "SKY" in name:
                if "PREMIERE" in name:
                    if "24" in name: name = "SKY CINEMA PREMIEREN +24"
                    else: name = "SKY CINEMA PREMIEREN"
                if "ATLANTIC" in name: name = "SKY ATLANTIC"
                if "ACTION" in name: name = "SKY CINEMA ACTION"
                if "BEST" in name or "HITS" in name: name = "SKY CINEMA BEST OF"
                if "CINEMA" in name and "COMEDY" in name: name = "SKY CINEMA FUN"
                if "COMEDY" in name: name = "SKY COMEDY"
                if "FAMI" in name: name = "SKY CINEMA FAMILY"
                if "SHOW" in name: name = "SKY SERIEN & SHOWS"
                if "SPECI" in name: name = "SKY CINEMA SPECIAL"
                if "THRILLER" in name: name = "SKY CINEMA THRILLER"
                if "FUN" in name: name = "SKY CINEMA FUN"
                if "CLASSIC" in name: name = "SKY CINEMA CLASSICS"
                if "NOSTALGIE" in name: name = "SKY CINEMA CLASSICS"
                if "KRIM" in name: name = "SKY KRIMI"
            if "NATURE" in name: name = "SKY NATURE"
            if "ZEE" in name: name = "ZEE ONE"
            if "DELUX" in name: name = "DELUXE MUSIC"
            if "DISCO" in name: name = "DISCOVERY"
            if "TLC" in name: name = "TLC"
            if "HISTORY" in name: name = "HISTORY"
            if "VISION" in name: name = "MOTORVISION"
            if "INVESTIGATION" in name or "A&E" in name: name = "A&E"
            if "AUTO" in name: name = "AUTO MOTOR SPORT"
            if "FOX" in name:
                if "FIX" in name: name = "FIX & FOXI"
                else: name = "SKY REPLAY"
            if "WELT" in name:
                if "WUNDER" in name: name = "WELT DER Wunder"
                else: name = "WELT"
            if "NAT" in name and "GEO" in name:
                if "WILD" in name: name = "NAT GEO WILD"
                else: name = "NATIONAL GEOGRAPHIC"
            if "3" in name and "SAT" in name: name = "3 SAT"
            if "WARNER" in name:
                if "SERIE" in name: name = "WARNER TV SERIE"
                if "FILM" in name: name = "WARNER TV FILM"
                if "COMEDY" in name: name = "WARNER TV COMEDY"
            if "VOX" in name:
                if "+" in name: name = "VOX UP"
                elif "UP" in name: name = "VOX UP"
                else:
                    name = "VOX"
            if "SAT" in name and "1" in name:
                if "GOLD" in name:
                    name = "SAT 1 GOLD"
                elif "EMOT" in name:
                    name = "SAT 1 EMOTIONS"
                else:
                    name = "SAT 1"
            if name not in channels:
                channels[name] = []
            channels[name].append(c['url'])
    data={"ValidUntil": int(time.time()) + 300, "channels": channels}
    home.setProperty('chanfile', json.dumps(data))
    return channels
    
def choose():
    groups=[]
    for c in requests.get(url, params={'output': 'json'}).json():
        if c["group"] not in groups:
            groups.append(c["group"])
    new_groups = sorted(groups)
    indicies = utils.selectDialog(new_groups, "Choose Groups", True)
    group = []
    if indicies:
        for i in indicies:
            group.append(new_groups[i])
    if len(group) > 0:
        with open(groupfile, "w") as write_file:
            #json.dump(group, write_file, indent=4, sort_keys=True)
            json.dump(group, write_file)
        return group

def handle_wait(time_to_wait, kanal, heading="Abbrechen zur manuellen Auswahl", text1="Starte Stream in  : ", text2="STARTE  : "):
    progress = xbmcgui.DialogProgress()
    create = progress.create(heading, text2+kanal)
    secs=0
    percent=0
    increment = int(100 / time_to_wait)
    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment*secs
        secs_left = str((time_to_wait - secs))
        if utils.PY2:progress.update(percent,text2+kanal,text1+str(secs_left))
        else:progress.update(percent,text2+kanal+"\n"+text1+str(secs_left))
        xbmc.sleep(1000)
        if (progress.iscanceled()):
            cancelled = True
            break
    if cancelled == True:
        progress.close()
        return False
    else:
        progress.close()
        return True

def livePlay(name):
    m = getchannels()[name]
    if len(m) > 1:
        if int(utils.addon.getSetting('auto')) == 0 or int(utils.addon.getSetting('auto'))== 1 and handle_wait(int(utils.addon.getSetting('count')), name):
            n = m[0]
        else:
            cap=[]
            i = 0
            while i < len(m):
                i+=1
                cap.append('STREAM'+' '+str(i))
            index = utils.selectDialog(cap,'',False)
            if index < 0:
                return
            n = m[index]
    else:
        n = m[0]
    o = xbmcgui.ListItem(name)
    o.setPath(n + '?n=1&b=5&vavoo_auth=' + utils.getAuthSignature() + '|User-Agent=VAVOO/2.6')
    if xbmc.getCondVisibility('System.HasAddon("inputstream.ffmpegdirect")'):
        o.setMimeType("video/mp2t")
        o.setProperty("inputstream", "inputstream.ffmpegdirect")
        o.setProperty("inputstream.ffmpegdirect.is_realtime_stream", "true")
        o.setProperty("inputstream.ffmpegdirect.stream_mode", "timeshift")
    o.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(utils.handle(), True, o)
    xbmcplugin.endOfDirectory(utils.handle(), succeeded=True, cacheToDisc=False)
            
def channels():
    try:
        with open(favoritenfile, "r") as f:
        	lines= json.load(f)
    except:
        lines=[]
    results = getchannels()
    for name in results:
        name = name.strip()
        url = utils.getPluginUrl({'name': name})
        o = xbmcgui.ListItem(name)
        cm = []
        if not name in lines:
            cm.append(('zu TV Favoriten hinzufügen', 'RunPlugin(%s?action=addTvFavorit&channel=%s)' % (sys.argv[0], name.replace('&', '%26').replace('+', '%2b'))))
            plot = ''
        else:
            plot = '[COLOR gold]TV Favorit[/COLOR]' #% name
            cm.append(('von TV Favoriten entfernen', 'RunPlugin(%s?action=delTvFavorit&channel=%s)' % (sys.argv[0], name.replace('&', '%26').replace('+', '%2b'))))
        o.addContextMenuItems(cm)
        #o.setInfo(type='Video', infoLabels={'Title': name, 'Label': lable})
        o.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
        o.setProperty('IsPlayable', 'true')
        o.setProperty('selectaction', 'play')
        xbmcplugin.addDirectoryItem(utils.handle(), url, o, isFolder=False)
    xbmcplugin.addSortMethod(utils.handle(), xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.endOfDirectory(utils.handle(), succeeded=True, cacheToDisc=False)

def favchannels():
    try:
        with open(favoritenfile, "r") as f:
        	lines= json.load(f)
    except:
        return
    for name in getchannels():
        if not name in lines: continue
        url = utils.getPluginUrl({'name': name})
        o = xbmcgui.ListItem(name)
        cm = []
        cm.append(('von TV Favoriten entfernen', 'RunPlugin(%s?action=delTvFavorit&channel=%s)' % (sys.argv[0], name.replace('&', '%26').replace('+', '%2b'))))
        o.addContextMenuItems(cm)
        o.setInfo(type='Video', infoLabels={'Title': name, 'Plot': '[COLOR gold]Liste der eigene Live Favoriten[/COLOR]'})
        o.setProperty('IsPlayable', 'true')
        o.setProperty('selectaction', 'play')
        xbmcplugin.addDirectoryItem(utils.handle(), url, o, isFolder=False)
    xbmcplugin.addSortMethod(utils.handle(), xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.endOfDirectory(utils.handle(), succeeded=True, cacheToDisc=False)

def addtvfavorit(name):
	try:
		with open(favoritenfile, "r") as k:
			lines = json.load(k)
	except:
		lines= []
	finally:
		lines.append(name)
		with open(favoritenfile, "w") as k:
			json.dump(lines, k)
		xbmc.executebuiltin('Container.Refresh')

def deltvfavorit(name):
	try:
		with open(favoritenfile, "r") as k:
			lines = json.load(k)
	except:
		lines=[]
	finally:
		if name in lines:
			lines.remove(name)
		with open(favoritenfile, "w") as k:
			json.dump(lines, k)
		xbmc.executebuiltin('Container.Refresh')