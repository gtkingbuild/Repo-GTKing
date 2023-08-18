# -*- coding: utf-8 -*-
import sys, xbmc, os, json, requests, urllib3, xbmcplugin, vavoosigner, resolveurl, base64
from resources.lib import utils
from xbmcgui import ListItem, Dialog
urllib3.disable_warnings()
session = requests.session()
BASEURL = "https://www2.vavoo.to/ccapi/"
try:from concurrent.futures import ThreadPoolExecutor, as_completed
except:pass
try: lines = json.loads(utils.addon.getSetting("favs"))
except: lines=[]

def _index(params):
	utils.set_content("files")
	if len(lines)>0: addDir2("TV Favoriten (Live)", "DefaultAddonPVRClient", "favchannels")
	addDir2("Live", "DefaultAddonPVRClient", "channels")
	addDir2("Filme", "DefaultMovies", "indexMovie")
	addDir2("Serien", "DefaultTVShows", "indexSerie")
	utils.end()

def _indexMovie(params):
	utils.set_content("movies")
	addDir2("Beliebte Filme", "DefaultMovies", "list", id="movie.popular")
	addDir2("Angesagte Filme", "DefaultMovies", "list", id="movie.trending")
	addDir2("Genres", "DefaultGenre", "genres", id="movie.popular")
	addDir2("Suche", "DefaultAddonsSearch", "search", id="movie.popular")
	utils.end()

def _indexSerie(params):
	utils.set_content("tvshows")
	addDir2("Beliebte Serien", "DefaultTVShows", "list", id="series.popular")
	addDir2("Angesagte Serien", "DefaultTVShows", "list", id="series.trending")
	addDir2("Genres", "DefaultGenre", "genres", id="series.popular")
	addDir2("Suche", "DefaultAddonsSearch", "search", id="series.popular")
	utils.end()

def createListItem(params):
	data = utils.get_meta(params)
	if not data: return
	infos = data["infos"]
	if params.get("e"):o = ListItem("S%sxE%s %s" %(params["s"], params["e"], infos["title"]) , infos["title"])
	else:o = ListItem(infos["title"])
	o.setInfo("Video", infos)
	o.setProperties(data["properties"])
	art = data["art"]
	if art.get("poster"): art["icon"] = art["poster"]
	if art.get("thumb"): art["poster"] = art["thumb"]
	o.setArt(art)
	o.setCast(data["cast"])
	o.setUniqueIDs(data["ids"], "tmdb")
	return o

def _list(params):
	data = cachedcall("list", params)
	next=data["next"]
	data = [i for i in data["data"] if i.get("description")]
	content, isFolder, action = "tvshows", True, "seasons"
	cat = "Beliebte Serien" if "popular" in params["id"] else "Angesagte Serien"
	if params["id"].startswith("movie"):
		cat = cat.replace("Serien", "Filme")
		content, isFolder, action = "movies", False, "get"
	utils.set_content(content)
	utils.set_category(cat)
	paramslist = [{"action": action,"id":e["id"]} for e in data]
	with ThreadPoolExecutor(len(paramslist)) as executor:
		future_to_url = {executor.submit(createListItem, urlparams):urlparams for urlparams in paramslist}
		for future in as_completed(future_to_url):
			urlparams = future_to_url[future]
			o = future.result()
			if o:
				if not isFolder: o.addContextMenuItems([("Manuelle Stream Auswahl", "RunPlugin(%s&manual=true)" % utils.url_for(urlparams))])
				utils.add(urlparams, o, isFolder)
	if next: addDir(">>> Weiter", {"action": "list", "id": next})
	utils.end()

def _search(params):
	query = params.get("query")
	if not query:
		heading="VAVOO.TO - SERIEN SUCHE" if params["id"].startswith("serie") else "VAVOO.TO - FILM SUCHE"
		kb = xbmc.Keyboard("", heading, False)
		kb.doModal()
		if (kb.isConfirmed()): query = kb.getText()
	if query:
		params["id"] = "%s.search=%s" % (params["id"], query.replace(".", "%2E"))
		_list(params)
	return

def _genres(params):
	serie_genrelist = [
		{"genre": "Action & Adventure", "icon":"Adventure"}, {"genre": "Animation", "icon":"Animation"}, {"genre": "Komödie", "icon":"Comedy"}, {"genre": "Krimi", "icon":"Crime"}, {"genre": "Dokumentarfilm", "icon":"Documentary"}, {"genre": "Drama", "icon":"Drama"},
		{"genre": "Familie", "icon":"Family"}, {"genre": "Kids", "icon":"Children"}, {"genre": "Mystery", "icon":"Mystery"}, {"genre": "News", "icon":"News"}, {"genre": "Reality", "icon":"Reality"}, {"genre": "Sci-Fi & Fantasy", "icon":"Sci-Fi"},
		{"genre": "Soap", "icon":"Soap"}, {"genre": "Talk", "icon":"Biography"}, {"genre": "War & Politics", "icon":"War"}, {"genre": "Western", "icon":"Western"}]
	movie_genrelist = [
		{"genre": "Action", "icon":"Action"}, {"genre": "Abenteuer", "icon":"Adventure"}, {"genre": "Animation", "icon":"Animation"}, {"genre": "Komödie", "icon":"Comedy"}, {"genre": "Krimi", "icon":"Crime"}, {"genre": "Dokumentarfilm", "icon":"Documentary"},
		{"genre": "Drama", "icon":"Drama"}, {"genre": "Familie", "icon":"Family"}, {"genre": "Fantasy", "icon":"Fantasy"}, {"genre": "Historie", "icon":"History"}, {"genre": "Horror", "icon":"Horror"}, {"genre": "Musik", "icon":"Music"},
		{"genre": "Mystery", "icon":"Mystery"}, {"genre": "Liebesfilm", "icon":"Romance"}, {"genre": "Science Fiction", "icon":"Sci-Fi"}, {"genre": "TV-Film", "icon":"Mini-Series"},
		{"genre": "Thriller", "icon":"Thriller"}, {"genre": "Kriegsfilm", "icon":"War"}, {"genre": "Western", "icon":"Western"}]
	genrelist= serie_genrelist if params["id"].startswith("serie") else movie_genrelist
	for genre in genrelist: addDir2(genre["genre"], genre["icon"], "list", id="%s.genre=%s" % (params["id"], genre["genre"]))
	utils.end()

def _seasons(params):
	utils.set_content("seasons")
	utils.set_category("Staffeln")
	seasons = utils.get_meta(params)["seasons"]
	if len(seasons) == 1:
		params["s"] = "1"
		_episodes(params)
	params["action"] = "episodes"
	for season in seasons:
		params["s"] = str(season["season_number"])
		o = createListItem(params)
		utils.add(params, o, True)
	utils.end()
	
def _episodes(params):
	utils.set_content("episodes")
	utils.set_category("Staffel %s/Episoden" %params["s"])
	episodes = utils.get_meta(params)["infos"]["sortepisode"]
	params["action"], i = "get", 1
	while i <= episodes:
		params["e"] = str(i)
		o = createListItem(params)
		o.addContextMenuItems([("Manuelle Stream Auswahl", "RunPlugin(%s&manual=true)" % utils.url_for(params))])
		utils.add(params, o)
		i+=1
	utils.end()

def showFailedNotification(msg="Keine Streams gefunden"):
	xbmc.executebuiltin("Notification(VAVOO.TO,%s,5000,%s)" % (msg,utils.addonInfo("icon")))
	sys.exit()

def resolve(mirror):
	if "hd-stream" in mirror["url"]:
		try:
			posturl = "https://hd-stream.to/api/source/%s" % mirror["url"].split("/")[-1]
			data = {"r": "https://kinoger.to/", "d": "hd-stream.to"}
			response = session.post(posturl, data)
			response.raise_for_status()
			return sorted(response.json()["data"], key=lambda x: int(x["label"].replace("p", "")), reverse=True)[0]["file"]
		except Exception as e: utils.log(e)
	elif resolveurl.relevant_resolvers(utils.urlparse(mirror["url"]).hostname):
		try: return resolveurl.resolve(mirror["url"])
		except Exception as e: utils.log(e)
	try: return callApi2("open", {"link": mirror["url"]})[-1]["url"]
	except Exception as e: utils.log(e)

def checkstream(url):
	try:
		if not url: raise Exception("Keine Url")
		newurl, headers, params = url, {}, {}
		if "|" in newurl:
			newurl, headers = newurl.split("|")
			headers = dict(utils.parse_qsl(headers))
		if "?" in newurl:
			newurl, params = newurl.split("?")
			params = dict(utils.parse_qsl(params))
		res = session.get(newurl, headers=headers, params=params, stream=True)
		res.raise_for_status()
		if "text" in res.headers.get("Content-Type","text"): raise Exception("Keine Videodatei")
	except Exception as e: print(e)
	else: return url

def _get(params):
	manual = True if params.get("manual") == "true" else False
	if params.get("e"): params["id"] = "%s.%s.%s" % (params["id"], params["s"], params["e"])
	mirrors = callApi2("links", {"id": params["id"], "language": "de"})
	if not mirrors: return showFailedNotification()
	newurllist, url =[], None
	for i ,a in enumerate(mirrors, 1):
		a["hoster"] = utils.urlparse(a["url"]).netloc
		if "streamz" in a["hoster"]: continue # den hoster kann man vergessen
		if "language" in a:
			if "de" in a["language"] :
				if "1080p" in a["name"]:
					if int(utils.addon.getSetting("stream_quali")) > 0: continue
					a["name"], a["weight"] = "%s %s" %(a["hoster"], "1080p"), 1080+i
				elif "720p" in a["name"]:
					if int(utils.addon.getSetting("stream_quali")) > 1: continue
					a["name"], a["weight"] = "%s %s" %(a["hoster"], "720p"), 720+i
				elif "480p" in a["name"]: a["name"], a["weight"] = "%s %s" %(a["hoster"], "480p"), 480+i
				elif "360p" in a["name"]: a["name"], a["weight"] = "%s %s" %(a["hoster"], "360p"), 360+i
				else: a["name"], a["weight"] = a["hoster"], i
				newurllist.append(a)
		else:
			a["name"], a["weight"] = a["hoster"], i
			newurllist.append(a)
	mirrors = list(sorted(newurllist, key=lambda x: x["weight"], reverse=True))
	for i, a in enumerate(mirrors, 1): a["name"] = "%s. %s" % (i, a["name"])
	if utils.addon.getSetting("stream_select") == "0" or manual:
		index = Dialog().select("VAVOO", [ mirror["name"] for mirror in mirrors ])
		if index == -1: return
		if utils.addon.getSetting("auto_try_next_stream") !="true": mirrors = [mirrors[index]]
		else: mirrors = mirrors[index:]
	for mirror in mirrors:
		url = checkstream(resolve(mirror))
		if url: break
	if not url: return showFailedNotification()
	utils.log("Spiele :%s" % url)
	o = ListItem(xbmc.getInfoLabel("ListItem.Title"))
	o.setPath(url)
	o.setProperty("IsPlayable", "true")
	if ".m3u8" in url:
		o.setMimeType("application/vnd.apple.mpegurl")
		if utils.PY2: o.setProperty("inputstreamaddon", "inputstream.adaptive")
		else: o.setProperty("inputstream", "inputstream.adaptive")
		o.setProperty("inputstream.adaptive.manifest_type", "hls")
	if int(sys.argv[1]) > 0: utils.set_resolved(o)
	else: 
		from resources.lib.player import cPlayer
		xbmc.Player().play(url, o)
		return cPlayer().startPlayer()

def addDir(name, params, iconimage="DefaultFolder.png", isFolder=True):
	liz = ListItem(name)
	liz.setArt({"icon":iconimage, "thumb":iconimage})
	plot , cm = " ", [("Einstellungen", "RunPlugin(%s?action=settings)" % sys.argv[0])]
	if name == "TV Favoriten (Live)":
		plot = "[COLOR gold]Liste der eigenen Live Favoriten[/COLOR]"
		cm.append(("Alle Favoriten entfernen", "RunPlugin(%s?action=delallTvFavorit)" % sys.argv[0]))
	liz.addContextMenuItems(cm)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
	utils.add(params, liz, isFolder)

def addDir2(name_, icon_, action, isFolder=True, **params):
	params["action"] = action
	iconimage = utils.getIcon(icon_) if utils.getIcon(icon_) else icon_
	addDir(name_, params, iconimage, isFolder)

def cachedcall(action, params):
	content = utils.get_cache(params)
	if content: return content
	else:
		content = callApi2(action, params)
		utils.set_cache(params, content, timeout=75600)
		return content

def callApi(action, params, method="GET", headers=None, **kwargs):
	utils.log("Action:%s params: %s" % (action,json.dumps(params)))
	if not headers: headers = dict()
	headers["auth-token"] = vavoosigner.getAuthSignature()
	resp = session.request(method, (BASEURL + action), params=params, headers=headers, **kwargs)
	resp.raise_for_status()
	data = resp.json()
	utils.log("callApi res: %s" % json.dumps(data))
	return data

def callApi2(action, params):
	res = callApi(action, params, verify=False)
	while True:
		if type(res) is not dict or "id" not in res or "data" not in res:
			return res
		data = res["data"]
		if type(data) is dict and data.get("type") == "fetch":
			params = data["params"]
			body = params.get("body")
			headers = params.get("headers")
			try: resp = session.request(params.get("method", "GET").upper(), data["url"], headers={k:v[0] if type(v) in (list, tuple) else v for k, v in headers.items()} if headers else None, data=body.decode("base64") if body else None, allow_redirects=params.get("redirect", "follow") == "follow")
			except: return
			headers = dict(resp.headers)
			resData = {"status": resp.status_code, "url": resp.url, "headers": headers, "data": base64.b64encode(resp.content).decode("utf-8").replace("\n", "") if data["body"] else None}
			utils.log(json.dumps(resData))
			utils.log(resp.text)
			res = callApi("res", {"id": res["id"]}, method="POST", json=resData, verify=False)
		elif type(data) is dict and data.get("error"):
			utils.log(data.get("error"))
			return
		else: return data