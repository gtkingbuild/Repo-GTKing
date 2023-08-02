# -*- coding: utf-8 -*-
import sys, xbmc, os, json, requests, urllib3, utils
from xbmcplugin import setResolvedUrl, endOfDirectory, setContent, addDirectoryItem as add
from xbmcgui import ListItem, DialogProgressBG, Dialog
#from concurrent.futures import ThreadPoolExecutor, as_completed 
urllib3.disable_warnings()
session = requests.session()
from base64 import b64encode, b64decode 
BASEURL = 'https://www2.vavoo.to/ccapi/'

favoritenfile = os.path.join(utils.addonpath,"tvfavoriten")

try:
	with open(favoritenfile, "r") as k:
		lines = json.load(k)
except:
	lines=[]

def end(succeeded=True, cacheToDisc=True):
	return endOfDirectory(utils.handle(), succeeded=succeeded, cacheToDisc=cacheToDisc)

def _index(params):
	setContent(utils.handle(), 'files')
	if len(lines)>0: addDir2("TV Favoriten (Live)", "pvr", "favchannels")
	addDir2("Live", "pvr", "channels")
	addDir2('Filme', 'movies', 'indexMovie')
	addDir2('Serien', 'series', 'indexSerie')
	addDir2('Suche', 'search', 'search', id='all.popular')
	addDir2('Einstellungen', 'settings', 'settings')
	end()

def _indexMovie(params):
	setContent(utils.handle(), 'movies')
	addDir2('Beliebte Filme', 'movies', 'list', id='movie.popular')
	addDir2('Angesagte Filme', 'movies', 'list', id='movie.trending')
	addDir2('Genres', 'genres', 'genres', id='movie.popular')
	addDir2('Suche', 'search', 'search', id='movie.popular')
	addDir2('Einstellungen', 'settings', 'settings')
	end()

def _indexSerie(params):
	setContent(utils.handle(), 'tvshows')
	addDir2('Beliebte Serien', 'series', 'list', id='series.popular')
	addDir2('Angesagte Serien', 'series', 'list', id='series.trending')
	addDir2('Genres', 'genres', 'genres', id='series.popular')
	addDir2('Suche', 'search', 'search', id='series.popular')
	addDir2('Einstellungen', 'settings', 'settings')
	end()

def prepareListItem(params, e):
	infos = {}
	
	def setInfo(key, value):
		if value:
			if type(value) is list:
				infos[key] = (', ').join(value)
			else:
				infos[key] = value

	setInfo('tvshowtitle', e.get('name'))
	setInfo('title', e.get('name'))
	setInfo('originaltitle', e.get('originalName'))
	setInfo('year', e.get('year'))
	art = {'icon': e.get('poster', 'DefaultVideo.png'), 'thumb': e.get('poster', 'DefaultVideo.png'), 'poster': e.get('poster', 'DefaultVideo.png'), 'banner': e.get('backdrop', 'DefaultVideo.png')}
	setInfo('plot', e.get('description'))
	setInfo('code', e.get('id'))
	setInfo('premiered', e.get('releaseDate'))
	season=params.get('season')
	if season:
		setInfo('season', int(season))
		setInfo('sorttitle', 'Staffel %s' % (season))
	ep = e.get('current_episode')
	if ep:
		episode = ep['episode']
		setInfo('sorttitle', 'Staffel %s Episode %s' % (season, episode))
		setInfo('episode', int(episode))
		episode_title = ep.get('name')
		if episode_title and not episode_title.startswith('Episode '):
			setInfo('sorttitle', 'S%sE%s  %s' % (season, episode, episode_title))
	setInfo('genre', e.get('genres'))
	setInfo('country', e.get('country'))
	setInfo('cast', e.get('cast'))
	setInfo('director', e.get('director'))
	setInfo('writer', e.get('writer'))
	return (infos, art)

def createListItem(params, e, isPlayable=False):
	infos, art = prepareListItem(params, e)
	o = ListItem(infos['title'])
	o.setInfo('Video', infos)
	sorttitle =  infos.get('sorttitle')
	if sorttitle:
		o.setLabel(sorttitle)
	o.setProperty('selectaction', 'info')
	if isPlayable:
		o.setProperty('IsPlayable', "true")
	o.setArt(art)
	return o

def _list(params):
	data = cachedcall('list', {'id': params['id']})
	isPlayable = False
	isFolder = True
	action = 'seasons'
	content = 'tvshows'
	if params['id'].startswith('movie'):
		isPlayable = True
		isFolder = False
		action = 'get'
		content = 'movies'
	setContent(utils.handle(), content)
	for e in data['data']:
		urlParams = {'action': action, 'id': e['id']}
		o = createListItem(urlParams, e, isPlayable)
		add(utils.handle(), utils.getPluginUrl(urlParams), o, isFolder)
	if data['next']:
		addDir('>>> Weiter', utils.getPluginUrl({'action': 'list', 'id': data['next']}))
	end()
	
def _search(params):
	query = None
	if params.get('query'):
		query = params.get('query')
	else:
		heading='VAVOO.TO - SUCHE'
		if 'movie' in params['id']:
			heading='VAVOO.TO - FILM SUCHE'
		if 'serie' in params['id']:
			heading='VAVOO.TO - SERIEN SUCHE'
		kb = xbmc.Keyboard('', heading, False)
		kb.doModal()
		if (kb.isConfirmed()):
			query = kb.getText()
	if query:
		params['id'] = '%s.search=%s' % (params['id'], query.replace('.', '%2E'))
		_list(params)
	return

def _genres(params):
	genrelist=['Action', 'Abenteuer', 'Animation', 'Komödie', 'Krimi', 'Dokumentarfilm', 'Drama', 'Familie', 'Fantasy', 'Historie', 'Horror', 'Musik', 'Mystery', 'Liebesfilm', 'Science Fiction', 'TV-Film', 'Thriller', 'Kriegsfilm', 'Western']
	if 'serie' in params['id']:
		genrelist= ['Action & Adventure', 'Animation', 'Komödie', 'Krimi', 'Dokumentarfilm', 'Drama', 'Familie', 'Kids', 'Mystery', 'News', 'Reality', 'Sci-Fi & Fantasy', 'Soap', 'Talk', 'War & Politics', 'Western']
	for genre in genrelist:
		addDir2(genre, genre, 'list', id='%s.genre=%s' % (params['id'], genre))
	end()

def _seasons(params):
	data = cachedcall('info', {'id': params['id'], "language": "de"})
	data['seasons'].pop('0', None)
	seasons = list(data['seasons'].keys())
	if len(seasons) == 1:
		params['season'] = "1"
		_episodes(params)
	setContent(utils.handle(), 'seasons')
	params['action'] = 'episodes'
	for season in seasons:
		params['season'] = season
		o = createListItem(params, data)
		add(handle=utils.handle(), url=utils.getPluginUrl(params), listitem=o, isFolder=True)
	end()

def _episodes(params):
	setContent(utils.handle(), 'episodes')
	idid = params['id']
	data = cachedcall('info', {'id': idid, "language": "de"})
	season = str(params['season'])
	params = {'action': 'get', 'id': idid, 'season':season}
	for i in data['seasons'][season]:
		data['current_episode'] = i
		params['episode'] = str(i["episode"])
		o = createListItem(params, data, isPlayable=True)
		add(handle=utils.handle(), url=utils.getPluginUrl(params), listitem=o, isFolder=False)
	end()

class _get(object):
	def __init__(self, params):
		if params.get('episode'):
			self.params = {'id': '%s.%s.%s' % (params['id'], params['season'], params.get('episode')), "language": "de"}
		else:
			self.params = {'id': params['id'], "language": "de"}
		utils.log(json.dumps(self.params))
		self.data = cachedcall('info', {'id': params['id'], "language": "de"})
		self.run()

	def showFailedNotification(self):
		xbmc.executebuiltin('Notification(%s,%s,%s,%s)' % ('VAVOO.TO','Keine Streams gefunden',5000,utils.addonInfo('icon')))

	def run(self):
		mirrors = cachedcall('links', {'id': self.params['id'], "language": "de"})
		if not mirrors:
			self.showFailedNotification()
			return
		newurllist = []
		for i ,a in enumerate(mirrors):
			i+=1
			if 'de' in a['language'] :
				a['hoster'] = utils.urlparse(a['url']).netloc
				if "1080p" in a['name']:
					a['name'] = "%s. %s %s" %(i , a['hoster'], '1080p')
					a['weight'] = 1080+i
				elif "720p" in a['name']:
					a['name'] = "%s. %s %s" %(i , a['hoster'], '720p')
					a['weight'] = 720+i
				elif "480p" in a['name']:
					a['name'] = "%s. %s %s" %(i , a['hoster'], '480p')
					a['weight'] = 480+i
				elif "360p" in a['name']:
					a['name'] = "%s. %s %s" %(i , a['hoster'], '360p')
					a['weight'] = 360+i
				else:
					a['name'] = "%s. %s %s" %(i , a['hoster'], 'SD')
					a['weight'] = i
				newurllist.append(a)
		newmirrors = list(sorted(newurllist, key=lambda x: x['weight'], reverse=True))
		if utils.addon.getSetting('stream_select') == '0':
			captions = [ mirror['name'] for mirror in newmirrors ]
			index = Dialog().select("VAVOO", captions)
			if utils.addon.getSetting('auto_try_next_stream') !="true":
				self.mirrors = [newmirrors[index]]
			else:
				self.mirrors = newmirrors[index:]
		else:
			self.mirrors = newmirrors
		self.resolvedUrl = None
		for mirror in self.mirrors:
			res = callApi2('open', {'link': mirror['url']})
			if res:
				a = session.get(res[-1].get('url'), stream=True, verify=False)
				utils.log(repr(a.headers))
				utils.log(repr(a.url))
				if "text" not in a.headers.get('Content-Type',"text"):
					self.resolvedUrl = a.url
					if self.resolvedUrl:
						break
			continue
			
		if not self.resolvedUrl:
			return
		o = createListItem(self.params, self.data, isPlayable=True)
		o.setProperty("IsPlayable", "true")
		o.setPath(self.resolvedUrl)
		if ".m3u8" in self.resolvedUrl:
			o.setMimeType("application/vnd.apple.mpegurl")
			if utils.PY2:
				o.setProperty("inputstreamaddon", "inputstream.adaptive")
			else:
				o.setProperty("inputstream", "inputstream.adaptive")
			o.setProperty("inputstream.adaptive.manifest_type", "hls")
		setResolvedUrl(utils.handle(), True, o)


def addDir(name, url, iconimage="DefaultFolder.png", isFolder=True, isPlayable=False):
    if name == 'TV Favoriten (Live)':
        plot = '[COLOR gold]Liste der eigene Live Favoriten[/COLOR]'
    else:
        plot = ' ' # Alt255
    liz = ListItem(name)
    liz.setArt({"icon":iconimage, "thumb":iconimage})
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
    if isPlayable:
        liz.setProperty("IsPlayable", "true")
    add(utils.handle(), url, liz, isFolder)

def addDir2(name_, icon_, action, **params):
	params['action'] = action
	addDir(name_, utils.getPluginUrl(params), utils.getIcon(icon_))

def cachedcall(action, params):
	cacheKey = action + '?' + ('&').join([ str(key) + '=' + str(value) for key, value in sorted(list(params.items())) ])
	content = utils.get_cache(cacheKey)
	if content:
		utils.log("from cache")
		return content
	else:
		content = callApi2(action, params)
		utils.set_cache(cacheKey, content, timeout=1800)
		return content

def callApi(action, params, method='GET', headers=None, **kwargs):
    utils.log('Action:%s params: %s' % (action,json.dumps(params)))
    if not headers:
        headers = dict()
    headers['auth-token'] = utils.getAuthSignature()
    resp = session.request(method, (BASEURL + action), params=params, headers=headers, **kwargs)
    resp.raise_for_status()
    data = resp.json()
    utils.log('callApi res: %s' % json.dumps(data))
    return data

def callApi2(action, params):
	res = callApi(action, params, verify=False)
	while True:
		if type(res) is not dict or 'id' not in res or 'data' not in res:
			return res
		data = res['data']
		if type(data) is dict and data.get('type') == 'fetch':
			params = data['params']
			body = params.get('body')
			headers = params.get('headers')
			try:
				resp = session.request(params.get('method', 'GET').upper(), data['url'], headers={k:v[0] if type(v) in (list, tuple) else v for k, v in headers.items()} if headers else None, data=body.decode('base64') if body else None, allow_redirects=params.get('redirect', 'follow') == 'follow')
			except:
				return
			headers = dict(resp.headers)
			resData = {'status': resp.status_code, 'url': resp.url, 'headers': headers, 'data': b64encode(resp.content).decode("utf-8").replace('\n', '') if data['body'] else None}
			utils.log(json.dumps(resData))
			utils.log(resp.text)
			res = callApi('res', {'id': res['id']}, method='POST', json=resData, verify=False)
		elif type(data) is dict and data.get('error'):
			utils.log(data.get('error'))
			return
		else:
			return data
	return

def main():
	params = dict(utils.parse_qsl(sys.argv[2][1:]))
	if params:
		tv = params.get('name')
		action = params.pop('action', False)
		if action:
			if action == 'choose':
				import vjlive
				vjlive.choose()
			elif action == 'channels':
				import vjlive
				vjlive.channels()
			elif action == 'settings':
				utils.addon.openSettings(sys.argv[1])
			elif action == 'favchannels':
				import vjlive
				vjlive.favchannels()
			elif action == 'addTvFavorit':
				import vjlive
				vjlive.addtvfavorit(params['channel'])
			elif action == 'delTvFavorit':
				import vjlive
				vjlive.deltvfavorit(params['channel'])
			else:
				globals()["_"+action](params)
		elif tv:
			import vjlive
			vjlive.livePlay(params['name'])
		else:
			cancel = params.get('cancel', '').lower()
			if cancel == 'home':
				xbmc.executebuiltin('ActivateWindow(Home)')
	else:
		_index(params)