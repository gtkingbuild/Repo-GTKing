# -*- coding: utf-8 -*-
import xbmcgui, xbmcaddon, sys, xbmc, os, time, json, xbmcplugin, requests
PY2 = sys.version_info[0] == 2
if PY2:
	from urlparse import urlparse, parse_qsl
	from urllib import urlencode, quote_plus
else:
	from urllib.parse import urlencode, urlparse, parse_qsl, quote_plus
	import xbmcvfs

def translatePath(*args):
	if PY2: return xbmc.translatePath(*args).decode("utf-8")
	else: return xbmcvfs.translatePath(*args)

def exists(*args):
	return os.path.exists(translatePath(*args))

addon = xbmcaddon.Addon()
addonInfo = addon.getAddonInfo
addonID = addonInfo('id')
addonprofile = translatePath(addonInfo('profile'))
addonpath = translatePath(addonInfo('path'))
cachepath = os.path.join(addonprofile, "cache")
if not exists(cachepath): os.makedirs(cachepath)
		
def clear(auto=False):
	for a in os.listdir(cachepath):
		file = os.path.join(cachepath, a)
		if os.path.isfile(file):
			if auto:
				with open(file) as k: r = json.load(k)
				sigValidUntil = r.get('sigValidUntil', 0)
				if sigValidUntil != False and sigValidUntil < int(time.time()): os.remove(file)
			else: os.remove(file)
		
clear(auto=True)

def append_headers(headers):
	return '|%s' % '&'.join(['%s=%s' % (key, quote_plus(headers[key])) for key in headers])
    
def delete_search(params):
	if params["id"] == "all":
		set_cache("seriesearch", {}, False)
		set_cache("moviesearch", {}, False)
		xbmc.executebuiltin("Container.Refresh")
	else:
		type = "SERIEN" if params["id"].startswith("serie") else "FILM"
		history = get_cache("seriesearch" if type == "SERIEN" else "moviesearch") or {}
		if params.get("single"):
			history.pop(params.get("single"))
			set_cache("seriesearch" if type == "SERIEN" else "moviesearch", history, False)
			if not history: xbmc.executebuiltin("Action(ParentDir)")
			else: xbmc.executebuiltin("Container.Refresh")
		else:
			set_cache("seriesearch" if type == "SERIEN" else "moviesearch", {}, False)
			xbmc.executebuiltin("Action(ParentDir)")

def selectDialog(list, heading=None, multiselect = False):
	if heading == 'default' or heading is None: heading = addonInfo('name')
	if multiselect: return xbmcgui.Dialog().multiselect(str(heading), list)
	return xbmcgui.Dialog().select(str(heading), list)

home = xbmcgui.Window(10000)

def set_cache(key, value, timeout=604800):
	path = convertPluginParams(key)
	data={"sigValidUntil": False if timeout == False else int(time.time()) +timeout,"value": value}
	home.setProperty(path, json.dumps(data))
	file = os.path.join(cachepath, path)
	k = open(file+".json", "w") if PY2 else xbmcvfs.File(file+".json", "w")
	json.dump(data, k, indent=4)
	k.close()
	
def get_cache(key):
	path = convertPluginParams(key)
	keyfile = home.getProperty(path)
	if keyfile:
		r = json.loads(keyfile)
		sigValidUntil = r.get('sigValidUntil', 0)
		if sigValidUntil == False or sigValidUntil > int(time.time()):
			log("from cache")
			return r.get('value')
		home.clearProperty(path)
	try:
		file = os.path.join(cachepath, path)
		with open(file+".json") as k: r = json.load(k)
		sigValidUntil = r.get('sigValidUntil', 0) 
		if sigValidUntil == False or sigValidUntil > int(time.time()):
			value = r.get('value')
			data={"sigValidUntil": sigValidUntil,"value": value}
			home.setProperty(path, json.dumps(data))
			log("from cache")
			return value
		os.remove(file)
	except: return

def getGenresFromIDs(genresID):
	tmdb_genres = {12: "Abenteuer", 14: "Fantasy", 16: "Animation", 18: "Drama", 27: "Horror", 28: "Action", 35: "Komödie", 36: "Historie", 37: "Western", 53: "Thriller", 80: "Krimi", 99: "Dokumentarfilm", 878: "Science Fiction", 9648: "Mystery", 10402: "Musik", 10749: "Liebesfilm", 10751: "Familie", 10752: "Kriegsfilm", 10759: "Action & Adventure", 10762: "Kids", 10763: "News", 10764: "Reality", 10765: "Sci-Fi & Fantasy", 10766: "Soap", 10767: "Talk", 10768: "War & Politics", 10770: "TV-Film"}
	sGenres = []
	for gid in genresID:
		genre = tmdb_genres.get(gid)
		if genre: sGenres.append(genre)
	return sGenres

def get_meta(param):
	media_type, tmdb_id = param["id"].replace("series", "tv").split(".")
	_meta, _art, _property, _cast, _episodes= {}, {}, {}, [], []
	_meta["writer"],_meta["director"] = [],[]
	trailer_url = "plugin://plugin.video.youtube/play/?video_id=%s"
	lang = "de" #Addon().getSetting("tmdb_lang")
	api_key = "86dd18b04874d9c94afadde7993d94e3"
	append_to_response = "credits,videos,external_ids,content_ratings,keywords"
	if media_type == "movie": append_to_response = append_to_response.replace("content_ratings", "release_dates")
	poster = "https://image.tmdb.org/t/p/%s" % "w342" #Addon().getSetting("poster_tmdb")
	fanart = "https://image.tmdb.org/t/p/%s" % "w1280" #Addon().getSetting("backdrop_tmdb")
	tmdb_url = "https://api.themoviedb.org/3/%s/%s" % (media_type, tmdb_id)
	url_params = {"language":lang, "api_key":api_key, "append_to_response":append_to_response}
	_meta["mediatype"] = media_type.replace("tv", "tvshow")
	
	def setInfo(key, value):
		if value: _meta[key] = value

	def setproperties(key, value):
		if value: _property[key] = value

	meta = get_cache({"id": param["id"]})
	if not meta:
		meta = requests.get(tmdb_url, params=url_params).json()
		if "success" in meta and meta["success"] == False: return
		set_cache({"id": param["id"]}, meta)
	_seasons = [i for i in meta["seasons"] if i["season_number"] != 0] if meta.get("seasons") else []
	_ids = {"tmdb": tmdb_id}
	external_ids = meta.get("external_ids")
	if external_ids and  external_ids.get("imdb_id"):
		_ids["imdb"] = external_ids["imdb_id"]
		setInfo("imdbnumber", external_ids["imdb_id"])
	if external_ids and  external_ids.get("tvdb_id"): _ids["tvdb"] = external_ids["tvdb_id"]
	setproperties("homepage", meta.get("homepage"))
	setInfo("title", meta.get("title", meta.get("name")))
	setInfo("tvshowtitle", meta.get("name"))
	setInfo("rating", meta.get("vote_average"))
	setInfo("votes", meta.get("vote_count"))
	belongs_to_collection = meta.get("belongs_to_collection")
	if belongs_to_collection:
		setInfo("setid", belongs_to_collection.get("id"))
		setInfo("set", belongs_to_collection.get("name"))
	setInfo("duration", meta.get("runtime", 0)*60)
	setInfo("originaltitle", meta.get("originalName", meta.get("original_title", meta.get("original_name"))))
	if meta.get("genres"): setInfo("genre", [i["name"] for i in meta["genres"]])
	elif meta.get("genre_ids"): setInfo("genre", getGenresFromIDs(meta["genre_ids"]))
	setInfo("plot", meta.get("overview", meta.get("description")))
	setInfo("premiered", meta.get("release_date", meta.get("first_air_date", meta.get("releaseDate"))))
	if len(_meta.get("premiered", "0")) == 10: _meta["year"] = int(_meta["premiered"][:4])
	setInfo("status", meta.get("status"))
	setInfo("tagline", meta.get("tagline"))
	keywords = meta.get("keywords", {})
	tags = keywords.get("results", keywords.get("keywords",{}))
	if tags: setInfo("tag", [i["name"] for i in tags])
	results = meta.get("release_dates", meta.get("content_ratings", {})).get("results")
	results = [i for i in results if i["iso_3166_1"] == "DE"] if results else []
	if results:
		for release in results:
			if release["iso_3166_1"] == "DE":
				if release.get("rating"): setInfo("mpaa", release.get("rating"))
				else:
					for release_date in release["release_dates"]:
						if release_date["type"] == 3: setInfo("mpaa", release_date.get("certification"))
	if meta.get("backdrop_path"): _art["banner"] = fanart + meta["backdrop_path"]
	if meta.get("poster_path"): _art["poster"] = poster + meta["poster_path"]
	if meta.get('budget') and meta['budget'] !=0: setproperties("Budget", '${:,}'.format(meta['budget']))
	if meta.get('revenue') and meta['revenue'] !=0: setproperties("Revenue", '${:,}'.format(meta['revenue']))
	setproperties("TotalSeasons", meta.get("number_of_seasons"))
	setproperties("TotalEpisodes", meta.get("number_of_episodes"))
	if meta.get("production_countries"): _meta["country"] = [i["name"] for i in meta["production_countries"]]
	if meta.get("production_companies"): _meta["studio"] = [i["name"] for i in meta["production_companies"]]
	if meta.get("trailers") and "youtube" in meta["trailers"]:
		for t in meta["trailers"]["youtube"]:
			if t["type"] == "Trailer": setInfo("trailer", trailer_url % t["source"])
	elif meta.get("videos",{}).get("results"):
		for t in meta["videos"]["results"]:
			if t["type"] == "Trailer" and t["site"] == "YouTube": setInfo("trailer", trailer_url % t["key"])
	if param.get("s"):
		_meta["mediatype"] = "season"
		_meta["season"] = param["s"]
		season = [i for i in _seasons if i["season_number"] == int(param["s"])][0]
		_meta["title"] = season["name"]
		setInfo("plot", season.get("overview"))
		_meta["sortepisode"] = season["episode_count"]
		setproperties("TotalEpisodes", season["episode_count"])
		setInfo("aired", season.get("air_date"))
		if _meta.get("aired")  and len(_meta["aired"]) == 10: _meta["year"] = int(_meta["aired"][:4])
		if season.get("poster_path"): _art["poster"] = poster + season["poster_path"]
	if param.get("s") and param.get("e"):
		_meta["mediatype"] = "episode"
		_meta["episode"] = int(param.get("e"))
		meta = get_cache({"id": param["id"], "s":param["s"]})
		if not meta:
			tmdb_url+="/season/%s" % param["s"]
			meta = requests.get(tmdb_url, params=url_params).json()
			set_cache({"id": param["id"], "s":param["s"]}, meta)
		_episodes = meta["episodes"]
		episode = [i for i in _episodes if i["episode_number"] == int(param["e"])][0]
		_meta["title"] = episode["name"] if episode.get("name") else "Staffel:%s Episode:%s" % (param["s"], param["e"])
		_meta["plot"] = episode.get("overview", "")
		_meta["aired"] = episode.get("air_date")
		setInfo("rating", episode.get("vote_average"))
		setInfo("votes", episode.get("vote_count"))
		if _meta.get("aired")  and len(_meta["aired"]) == 10: _meta["year"] = int(_meta["aired"][:4])
		setInfo("code", episode.get("production_code"))
		if episode.get("runtime"): _meta["duration"] = episode["runtime"]*60
		if episode.get("still_path"): _art["thumb"] = poster + episode["still_path"]
		if episode.get("crew"):
			for crew in episode["crew"]:
				if crew["department"] == "Directing": _meta["director"].append(crew["name"])
				elif crew["department"] == "Writing": _meta["writer"].append(crew["name"])
		if episode.get("guest_stars"):
			for i in episode["guest_stars"]:
				if i.get("profile_path"): _cast.append({"name":i["name"], "role":i["character"], "thumbnail": poster + i["profile_path"], "order": i["order"]})
				else: _cast.append({"name":i["name"], "role":i["character"], "order": i["order"]})
	if _meta["mediatype"] in ["movie", "episode"]: _property["IsPlayable"] = "true"
	casts = meta.get("credits",{}).get("cast")
	crews = meta.get("credits",{}).get("crew")
	if crews:
		for crew in crews:
			if crew["job"] == "Director": _meta["director"].append(crew["name"])
			if crew["department"] == "Writing": _meta["writer"].append(crew["name"])
	created_by =  meta.get("created_by")
	if created_by:
		for i in created_by:
			_meta["director"].append(i["name"])
	if casts:
		for a in casts:
			cast = {"name":a["name"], "role":a["character"], "order": a["order"]}
			if a.get("profile_path"): cast["thumbnail"] = poster + a["profile_path"]
			_cast.append(cast)
	return {"infos":_meta, "art":_art, "properties":_property, "cast":_cast, "ids":_ids, "seasons":_seasons, "episodes":_episodes}

def log(msg, header=""):
	try: msg = json.dumps(msg, indent=4)
	except: pass
	#msg += " ".join(repr(args))
	if header: header+="\n"
	out = "\n####VAVOOTO####\n%s%s\n########" % (header, msg)
	mode = xbmc.LOGDEBUG
	if addon.getSetting("debug") == "true":
		mode = xbmc.LOGNOTICE if PY2 else xbmc.LOGINFO
	xbmc.log(out, mode)

def yesno(heading, line1, line2='', line3='', nolabel='', yeslabel=''):
	if PY2: return xbmcgui.Dialog().yesno(heading, line1,line2,line3, nolabel, yeslabel)
	else: return xbmcgui.Dialog().yesno(heading, line1+"\n"+line2+"\n"+line3, nolabel, yeslabel)
	
def ok(heading, line1, line2='', line3=''):
	if PY2: return xbmcgui.Dialog().ok(heading, line1,line2,line3)
	else: return xbmcgui.Dialog().ok(heading, line1+"\n"+line2+"\n"+line3)

def getIcon(name):
	if exists("%s/resources/art/%s.png" % (addonpath ,name)):return "%s/resources/art/%s.png" % (addonpath ,name)
	elif exists("special://skin/extras/videogenre/%s.png" % name): return translatePath("special://skin/extras/videogenre/%s.png" % name)
	else: return  "%s.png" % name

def end(succeeded=True, cacheToDisc=True):
	return xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=succeeded, cacheToDisc=cacheToDisc)
	
def add(params, o, isFolder=False):
	return xbmcplugin.addDirectoryItem(int(sys.argv[1]), url_for(params), o, isFolder)

def set_category(cat):
	xbmcplugin.setPluginCategory(int(sys.argv[1]), cat)

def set_content(cont):
	xbmcplugin.setContent(int(sys.argv[1]), cont)
	
def set_resolved(item):
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def sort_method():
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_TITLE)

def convertPluginParams(params):
	if isinstance(params, dict):
		p = []
		for key, value in list(params.items()):
			if isinstance(value, int):
				value = str(value)
			if PY2 and isinstance(value, unicode):
				value = value.encode("utf-8")
			p.append(urlencode({key: value}))
		params = '&'.join(p)
	return params

def url_for(params):
	return "%s?%s" % (sys.argv[0], convertPluginParams(params))