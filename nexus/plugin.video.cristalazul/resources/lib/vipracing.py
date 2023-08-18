import math
import re

from six.moves import urllib_parse
from six.moves import urllib_request


def vip_unlockmeta(meta):
	d = ''
	for i in range(0, len(meta)):
		if (i % 3 == 0):
			d += "%";
		else:
			d += meta[i];
	return urllib_parse.unquote(d);


def get_html(meta, data):
	meta_un = vip_unlockmeta(meta)
	oo = ''
	x = data
	l = len(x)
	b = 1024.0
	i, j, r, p = 0, 0, 0, 0
	s = 0
	w = 0
	str_pattern = 'Array\((.*?)\)'
	array_val = re.compile(str_pattern).findall(meta_un)[0] 
	t_string = 't=[' + array_val + ']'
	exec(t_string)
	for j in range(int(math.ceil(l / b)), 0, -1):
		r = '';

		for i in range(int(min(l, b)), 0, -1):
			w |= (t[ ord(x[p]) - 48]) << s;
			p += 1;
			if (s):
				r += chr(165 ^ w & 255);
				w >>= 8;
				s -= 2
			else:
				s = 6
			l -= 1
		oo += r
	return oo


def getUrl(url, cookieJar=None, post=None, timeout=20, headers=None):
	cookie_handler = urllib_request.HTTPCookieProcessor(cookieJar)
	opener = urllib_request.build_opener(cookie_handler, urllib_request.HTTPBasicAuthHandler(), urllib_request.HTTPHandler())
	req = urllib_request.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	if headers:
		for h, hv in headers:
			req.add_header(h, hv)

	response = opener.open(req, post, timeout=timeout)
	link = response.read()
	response.close()
	return link;


def decrypt_vipracing(page_url, justHtml=False, doDecrypt=True, ref=None, swftoken=None):
	if ref:
		headers = [('Referer', ref)]
		page_data = getUrl(page_url, headers=headers)
	else:
		page_data = getUrl(page_url)
	url = page_url
	if doDecrypt:
		str_pattern = 'src="(.*?(\/embed).*?)"'
		url = re.compile(str_pattern).findall(page_data)[0][0]
		meta, data = '', ''
		headers = [('Referer', page_url)]
		html = getUrl(url, headers=headers)
		
		str_pattern = '\'(http.*?)\''
		url = re.compile(str_pattern).findall(html)[0]
		html = getUrl(url, headers=headers)
		
		str_pattern = 'c=\"(.*?)\"'
		meta = re.compile(str_pattern).findall(html)
		if len(meta) > 0 and len(meta[0]) > 0 and 'streamer' not in html:
			meta = meta[0]
			str_pattern = 'x\(\"(.*?)\"\)'
			data = re.compile(str_pattern).findall(html)[0] 
			un_chtml = get_html(meta, data);
			str_pattern = 'streamer.*[\'"](.*?)[\'"]'
		elif 'streamer\'' in html:
			un_chtml = html
			str_pattern = 'streamer\': \'(.*?)\''
		else:
			un_chtml = html
			str_pattern = 'streamer.*[\'"](.*?)[\'"]'
	else:
			un_chtml = page_data
			str_pattern = 'streamer.*[\'"](.*?)[\'"]'

	if justHtml:
		return un_chtml + 'ThisPage[' + url + ']'
	print (str_pattern, un_chtml)
	streamer = re.compile(str_pattern).findall(un_chtml)[0] 
	streamer = streamer.replace('\\/', '/')
	if '//#:' in streamer:
		streamer = streamer.replace('//#:', '//watch10.streamlive.to:')
	str_pattern = 'file[\'"]?: [\'"](.*?)[\'"]'
	file = re.compile(str_pattern).findall(un_chtml)[0].replace('.flv', '')
	if  file == "":
		return ""
	str_pattern = 'getJSON\(\"(.*?)\"'
	token_url = re.compile(str_pattern).findall(un_chtml)[0] 
	if token_url.startswith('//'): token_url = 'http:' + token_url

	headers = [('Referer', url)]
	if not swftoken:
		token_html = getUrl(token_url, headers=headers)
		str_pattern = 'token":"(.*)"'
		token = re.compile(str_pattern).findall(token_html)[0] 
	else:
		token = swftoken
	str_pattern = '\'flash\', src: \'(.*?)\''
	swf = re.compile(str_pattern).findall(un_chtml)
	if not swf or len(swf) == 0:
		str_pattern = 'flashplayer: [\'"](.*?)[\'"]'
		swf = re.compile(str_pattern).findall(un_chtml)
	swf = swf[0]
	if swf.startswith('//'): swf = 'http:' + swf
	app = ''
	if '1935/' in streamer:
		app = streamer.split('1935/')[1]
		app += ' app=' + app
		streamer = streamer.split('1935/')[0] + '1935/'
	final_rtmp = '%s%s playpath=%s swfUrl=%s live=1 token=%s timeout=10 pageUrl=%s flashVer=WIN\\2023,0,0,162' % (streamer, app, file, swf, token, url)
	return final_rtmp
	
