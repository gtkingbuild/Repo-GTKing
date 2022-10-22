# -*- coding: utf-8 -*-
import xbmcgui, xbmcaddon, sys, xbmc, os, time, json
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
	from urllib import urlencode, unquote_plus
	from urlparse import parse_qs, parse_qsl, urlparse
	translatePath = xbmc.translatePath
else:
	from urllib.parse import urlencode, unquote_plus, parse_qs, parse_qsl, urlparse
	import xbmcvfs
	translatePath = xbmcvfs.translatePath
	unicode = str

def py2dec(msg):
	if PY2:
		return msg.decode("utf-8")
	return msg

def py3dec(msg):
	if PY3:
		return msg.decode("utf-8")
	return msg
		
def py2enc(msg):
	if PY2:
		return msg.encode("utf-8")
	return msg

addon = xbmcaddon.Addon()
addonInfo = addon.getAddonInfo
addonID = addonInfo('id')
addonpath = py2dec(translatePath(addonInfo('profile')))
if not os.path.exists(addonpath):
	os.makedirs(addonpath)

def handle():
	return int(sys.argv[1])

def selectDialog(list, heading=None, multiselect = False):
	if heading == 'default' or heading is None:
		heading = xbmcaddon.Addon().getAddonInfo('name')
	if multiselect:
		return xbmcgui.Dialog().multiselect(str(heading), list)
	return xbmcgui.Dialog().select(str(heading), list)

home = xbmcgui.Window(10000)

def set_cache(key, value, timeout=300):
	data={"sigValidUntil": int(time.time()) +timeout,"value": value}
	home.setProperty(key, json.dumps(data))
	
def get_cache(key):
	keyfile = home.getProperty(key)
	if keyfile:
		r = json.loads(keyfile)
		if r.get('sigValidUntil', 0) > int(time.time()):
			return r.get('value')
		home.clearProperty(key)
	return

def getAuthSignature():
	signfile = get_cache('signfile')
	if signfile:
		return signfile
	vec = {"vec": "9frjpxPjxSNilxJPCJ0XGYs6scej3dW/h/VWlnKUiLSG8IP7mfyDU7NirOlld+VtCKGj03XjetfliDMhIev7wcARo+YTU8KPFuVQP9E2DVXzY2BFo1NhE6qEmPfNDnm74eyl/7iFJ0EETm6XbYyz8IKBkAqPN/Spp3PZ2ulKg3QBSDxcVN4R5zRn7OsgLJ2CNTuWkd/h451lDCp+TtTuvnAEhcQckdsydFhTZCK5IiWrrTIC/d4qDXEd+GtOP4hPdoIuCaNzYfX3lLCwFENC6RZoTBYLrcKVVgbqyQZ7DnLqfLqvf3z0FVUWx9H21liGFpByzdnoxyFkue3NzrFtkRL37xkx9ITucepSYKzUVEfyBh+/3mtzKY26VIRkJFkpf8KVcCRNrTRQn47Wuq4gC7sSwT7eHCAydKSACcUMMdpPSvbvfOmIqeBNA83osX8FPFYUMZsjvYNEE3arbFiGsQlggBKgg1V3oN+5ni3Vjc5InHg/xv476LHDFnNdAJx448ph3DoAiJjr2g4ZTNynfSxdzA68qSuJY8UjyzgDjG0RIMv2h7DlQNjkAXv4k1BrPpfOiOqH67yIarNmkPIwrIV+W9TTV/yRyE1LEgOr4DK8uW2AUtHOPA2gn6P5sgFyi68w55MZBPepddfYTQ+E1N6R/hWnMYPt/i0xSUeMPekX47iucfpFBEv9Uh9zdGiEB+0P3LVMP+q+pbBU4o1NkKyY1V8wH1Wilr0a+q87kEnQ1LWYMMBhaP9yFseGSbYwdeLsX9uR1uPaN+u4woO2g8sw9Y5ze5XMgOVpFCZaut02I5k0U4WPyN5adQjG8sAzxsI3KsV04DEVymj224iqg2Lzz53Xz9yEy+7/85ILQpJ6llCyqpHLFyHq/kJxYPhDUF755WaHJEaFRPxUqbparNX+mCE9Xzy7Q/KTgAPiRS41FHXXv+7XSPp4cy9jli0BVnYf13Xsp28OGs/D8Nl3NgEn3/eUcMN80JRdsOrV62fnBVMBNf36+LbISdvsFAFr0xyuPGmlIETcFyxJkrGZnhHAxwzsvZ+Uwf8lffBfZFPRrNv+tgeeLpatVcHLHZGeTgWWml6tIHwWUqv2TVJeMkAEL5PPS4Gtbscau5HM+FEjtGS+KClfX1CNKvgYJl7mLDEf5ZYQv5kHaoQ6RcPaR6vUNn02zpq5/X3EPIgUKF0r/0ctmoT84B2J1BKfCbctdFY9br7JSJ6DvUxyde68jB+Il6qNcQwTFj4cNErk4x719Y42NoAnnQYC2/qfL/gAhJl8TKMvBt3Bno+va8ve8E0z8yEuMLUqe8OXLce6nCa+L5LYK1aBdb60BYbMeWk1qmG6Nk9OnYLhzDyrd9iHDd7X95OM6X5wiMVZRn5ebw4askTTc50xmrg4eic2U1w1JpSEjdH/u/hXrWKSMWAxaj34uQnMuWxPZEXoVxzGyuUbroXRfkhzpqmqqqOcypjsWPdq5BOUGL/Riwjm6yMI0x9kbO8+VoQ6RYfjAbxNriZ1cQ+AW1fqEgnRWXmjt4Z1M0ygUBi8w71bDML1YG6UHeC2cJ2CCCxSrfycKQhpSdI1QIuwd2eyIpd4LgwrMiY3xNWreAF+qobNxvE7ypKTISNrz0iYIhU0aKNlcGwYd0FXIRfKVBzSBe4MRK2pGLDNO6ytoHxvJweZ8h1XG8RWc4aB5gTnB7Tjiqym4b64lRdj1DPHJnzD4aqRixpXhzYzWVDN2kONCR5i2quYbnVFN4sSfLiKeOwKX4JdmzpYixNZXjLkG14seS6KR0Wl8Itp5IMIWFpnNokjRH76RYRZAcx0jP0V5/GfNNTi5QsEU98en0SiXHQGXnROiHpRUDXTl8FmJORjwXc0AjrEMuQ2FDJDmAIlKUSLhjbIiKw3iaqp5TVyXuz0ZMYBhnqhcwqULqtFSuIKpaW8FgF8QJfP2frADf4kKZG1bQ99MrRrb2A="}
	url = 'https://www.vavoo.tv/api/box/ping2'
	import requests
	req = requests.post(url, data=vec).json()
	signed = req['response'].get('signed')
	set_cache('signfile', signed)
	return signed

def log(*args):
	msg=""
	for arg in args:
		msg += repr(arg)
	xbmc.log(msg, xbmc.LOGINFO)

def yesno(heading, line1, line2='', line3='', nolabel='', yeslabel=''):
	if PY3:return xbmcgui.Dialog().yesno(heading, line1+"\n"+line2+"\n"+line3, nolabel, yeslabel)
	else:return xbmcgui.Dialog().yesno(heading, line1,line2,line3, nolabel, yeslabel)
	
def ok(heading, line1, line2='', line3=''):
	if PY3:return xbmcgui.Dialog().ok(heading, line1+"\n"+line2+"\n"+line3)
	else:return xbmcgui.Dialog().ok(heading, line1,line2,line3)

def getIcon(name):
	return py2dec(translatePath('special://home/addons/' + addonID + '/resources/' + name + '.png'))

def convertUrlParameter(param):
	param = param.split('?', 1)[1]
	params = parse_qs(param)
	params = {key:value[0] if len(value) == 1 else value for key, value in list(params.items())}
	return params

def convertPluginParams(params):
	p = []
	for key, value in list(params.items()):
		if isinstance(value, unicode):
			value = py2enc(value)
		p.append(urlencode({key: value}))
	return ('&').join(sorted(p))

def getPluginUrl(params):
	return 'plugin://' + addonID + '/?' + convertPluginParams(params)