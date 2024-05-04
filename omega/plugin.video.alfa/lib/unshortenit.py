#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

try:
    from urllib.parse import urlsplit, urlparse, parse_qs, urljoin, quote_plus
except:
    from urlparse import urlsplit, urlparse, parse_qs, urljoin
    from urllib import quote_plus

import json
import os
import re
import time
import urllib
import traceback
from base64 import b64decode

from core import httptools, scrapertools
from core.item import Item
from platformcode import config, logger


def find_in_text(regex, text, flags=re.IGNORECASE | re.DOTALL):
    rec = re.compile(regex, flags=flags)
    match = rec.search(text)
    if not match:
        return False
    return match.group(1)


class UnshortenIt(object):
    _adfly_regex = r'adf\.ly|j\.gs|q\.gs|u\.bb|ay\.gy|atominik\.com|tinyium\.com|microify\.com|threadsphere\.bid|clearload\.bid|activetect\.net|swiftviz\.net|briskgram\.net|activetect\.net|baymaleti\.net|thouth\.net|uclaut.net|gloyah.net|xterca.net|larati.net'
    _linkbucks_regex = r'linkbucks\.com|any\.gs|cash4links\.co|cash4files\.co|dyo\.gs|filesonthe\.net|goneviral\.com|megaline\.co|miniurls\.co|qqc\.co|seriousdeals\.net|theseblogs\.com|theseforums\.com|tinylinks\.co|tubeviral\.com|ultrafiles\.net|urlbeat\.net|whackyvidz\.com|yyv\.co'
    _adfocus_regex = r'adfoc\.us'
    _lnxlu_regex = r'lnx\.lu'
    _shst_regex = r'sh\.st|festyy\.com|ceesty\.com'
    _hrefli_regex = r'href\.li'
    _anonymz_regex = r'anonymz\.com'
    _shrink_service_regex = r'shrink-service\.it'
    _rapidcrypt_regex = r'rapidcrypt\.net'
    _cryptmango_regex = r'cryptmango'

    _maxretries = 5

    _this_dir, _this_filename = os.path.split(__file__)
    _timeout = 10

    def unshorten(self, uri, type=None):

        domain = urlsplit(uri).netloc

        if not domain:
            return uri, "No domain found in URI!"

        had_google_outbound, uri = self._clear_google_outbound_proxy(uri)

        if re.search(self._adfly_regex, domain,
                     re.IGNORECASE) or type == 'adfly':
            return self._unshorten_adfly(uri)
        if re.search(self._adfocus_regex, domain,
                     re.IGNORECASE) or type == 'adfocus':
            return self._unshorten_adfocus(uri)
        if re.search(self._linkbucks_regex, domain,
                     re.IGNORECASE) or type == 'linkbucks':
            return self._unshorten_linkbucks(uri)
        if re.search(self._lnxlu_regex, domain,
                     re.IGNORECASE) or type == 'lnxlu':
            return self._unshorten_lnxlu(uri)
        if re.search(self._shrink_service_regex, domain, re.IGNORECASE):
            return self._unshorten_shrink_service(uri)
        if re.search(self._shst_regex, domain, re.IGNORECASE):
            return self._unshorten_shst(uri)
        if re.search(self._hrefli_regex, domain, re.IGNORECASE):
            return self._unshorten_hrefli(uri)
        if re.search(self._anonymz_regex, domain, re.IGNORECASE):
            return self._unshorten_anonymz(uri)
        if re.search(self._rapidcrypt_regex, domain, re.IGNORECASE):
            return self._unshorten_rapidcrypt(uri)
        if re.search(self._cryptmango_regex, uri, re.IGNORECASE):
            return self._unshorten_cryptmango(uri)

        return uri, 0

    def unwrap_30x(self, uri, timeout=10):
        def unwrap_30x(uri, timeout=10):

            domain = urlsplit(uri).netloc
            self._timeout = timeout

            try:
                # headers stop t.co from working so omit headers if this is a t.co link
                if domain == 't.co':
                    r = httptools.downloadpage(uri, timeout=self._timeout)
                    return r.url, r.code
                # p.ost.im uses meta http refresh to redirect.
                if domain == 'p.ost.im':
                    r = httptools.downloadpage(uri, timeout=self._timeout)
                    uri = re.findall(r'.*url\=(.*?)\"\.*', r.data)[0]
                    return uri, r.code

                retries = 0
                while True:
                    r = httptools.downloadpage(
                        uri,
                        timeout=self._timeout,
                        cookies=False,
                        follow_redirects=False)
                    if not r.sucess:
                        return uri, -1

                    if '4snip' not in r.url and 'location' in r.headers and retries < self._maxretries:
                        r = httptools.downloadpage(
                            r.headers['location'],
                            cookies=False,
                            follow_redirects=False)
                        uri = r.url
                        retries += 1
                    else:
                        return r.url, r.code

            except Exception as e:
                return uri, str(e)

        uri, code = unwrap_30x(uri, timeout)

        if 'vcrypt' in uri and 'fastshield' in uri:
            # twince because of cookies
            httptools.downloadpage(
                uri,
                timeout=self._timeout,
                post='go=go')
            r = httptools.downloadpage(
                uri,
                timeout=self._timeout,
                post='go=go')
            return r.url, r.code

        return uri, code

    def _clear_google_outbound_proxy(self, url):
        '''
        So google proxies all their outbound links through a redirect so they can detect outbound links.
        This call strips them out if they are present.

        This is useful for doing things like parsing google search results, or if you're scraping google
        docs, where google inserts hit-counters on all outbound links.
        '''

        # This is kind of hacky, because we need to check both the netloc AND
        # part of the path. We could use urllib.parse.urlsplit, but it's
        # easier and just as effective to use string checks.
        if url.startswith("http://www.google.com/url?") or \
                url.startswith("https://www.google.com/url?"):

            qs = urlparse(url).query
            query = parse_qs(qs)

            if "q" in query:  # Google doc outbound links (maybe blogspot, too)
                return True, query["q"].pop()
            elif "url" in query:  # Outbound links from google searches
                return True, query["url"].pop()
            else:
                raise ValueError(
                    "Google outbound proxy URL without a target url ('%s')?" %
                    url)

        return False, url

    def _unshorten_adfly(self, uri):

        try:
            r = httptools.downloadpage(
                uri, timeout=self._timeout, cookies=False)
            html = r.data
            ysmm = re.findall(r"var ysmm =.*\;?", html)

            if len(ysmm) > 0:
                ysmm = re.sub(r'var ysmm \= \'|\'\;', '', ysmm[0])

                left = ''
                right = ''

                for c in [ysmm[i:i + 2] for i in range(0, len(ysmm), 2)]:
                    left += c[0]
                    right = c[1] + right

                # Additional digit arithmetic
                encoded_uri = list(left + right)
                numbers = ((i, n) for i, n in enumerate(encoded_uri) if str.isdigit(n))
                for first, second in zip(numbers, numbers):
                    xor = int(first[1]) ^ int(second[1])
                    if xor < 10:
                        encoded_uri[first[0]] = str(xor)

                decoded_uri = b64decode("".join(encoded_uri).encode())[16:-16].decode()

                if re.search(r'go\.php\?u\=', decoded_uri):
                    decoded_uri = b64decode(re.sub(r'(.*?)u=', '', decoded_uri)).decode()

                return decoded_uri, r.code
            else:
                return uri, 'No ysmm variable found'

        except Exception as e:
            return uri, str(e)

    def _unshorten_linkbucks(self, uri):
        '''
        (Attempt) to decode linkbucks content. HEAVILY based on the OSS jDownloader codebase.
        This has necessidated a license change.

        '''
        if config.is_xbmc():
            import xbmc

        r = httptools.downloadpage(uri, timeout=self._timeout)

        firstGet = time.time()

        baseloc = r.url

        if "/notfound/" in r.url or \
                "(>Link Not Found<|>The link may have been deleted by the owner|To access the content, you must complete a quick survey\.)" in r.data:
            return uri, 'Error: Link not found or requires a survey!'

        link = None

        content = r.data

        regexes = [
            r"<div id=\"lb_header\">.*?/a>.*?<a.*?href=\"(.*?)\".*?class=\"lb",
            r"AdBriteInit\(\"(.*?)\"\)",
            r"Linkbucks\.TargetUrl = '(.*?)';",
            r"Lbjs\.TargetUrl = '(http://[^<>\"]*?)'",
            r"src=\"http://static\.linkbucks\.com/tmpl/mint/img/lb\.gif\" /></a>.*?<a href=\"(.*?)\"",
            r"id=\"content\" src=\"([^\"]*)",
        ]

        for regex in regexes:
            if self.inValidate(link):
                link = find_in_text(regex, content)

        if self.inValidate(link):
            match = find_in_text(r"noresize=\"[0-9+]\" src=\"(http.*?)\"", content)
            if match:
                link = find_in_text(r"\"frame2\" frameborder.*?src=\"(.*?)\"", content)

        if self.inValidate(link):
            scripts = re.findall("(<script type=\"text/javascript\">[^<]+</script>)", content)
            if not scripts:
                return uri, "No script bodies found?"

            js = False

            for script in scripts:
                # cleanup
                script = re.sub(r"[\r\n\s]+\/\/\s*[^\r\n]+", "", script)
                if re.search(r"\s*var\s*f\s*=\s*window\['init'\s*\+\s*'Lb'\s*\+\s*'js'\s*\+\s*''\];[\r\n\s]+", script):
                    js = script

            if not js:
                return uri, "Could not find correct script?"

            token = find_in_text(r"Token\s*:\s*'([a-f0-9]{40})'", js)
            if not token:
                token = find_in_text(r"\?t=([a-f0-9]{40})", js)

            assert token

            authKeyMatchStr = r"A(?:'\s*\+\s*')?u(?:'\s*\+\s*')?t(?:'\s*\+\s*')?h(?:'\s*\+\s*')?K(?:'\s*\+\s*')?e(?:'\s*\+\s*')?y"
            l1 = find_in_text(r"\s*params\['" + authKeyMatchStr + r"'\]\s*=\s*(\d+?);", js)
            l2 = find_in_text(
                r"\s*params\['" + authKeyMatchStr + r"'\]\s*=\s?params\['" + authKeyMatchStr + r"'\]\s*\+\s*(\d+?);",
                js)

            if any([not l1, not l2, not token]):
                return uri, "Missing required tokens?"

            authkey = int(l1) + int(l2)

            p1_url = urljoin(baseloc, "/director/?t={tok}".format(tok=token))
            r2 = httptools.downloadpage(p1_url, timeout=self._timeout)

            p1_url = urljoin(baseloc, "/scripts/jquery.js?r={tok}&{key}".format(tok=token, key=l1))
            r2 = httptools.downloadpage(p1_url, timeout=self._timeout)

            time_left = 5.033 - (time.time() - firstGet)
            if config.is_xbmc():
                xbmc.sleep(max(time_left, 0) * 1000)
            else:
                time.sleep(5 * 1000)

            p3_url = urljoin(baseloc, "/intermission/loadTargetUrl?t={tok}&aK={key}&a_b=false".format(tok=token,
                                                                                                      key=str(authkey)))
            r3 = httptools.downloadpage(p3_url, timeout=self._timeout)

            resp_json = json.loads(r3.data)
            if "Url" in resp_json:
                return resp_json['Url'], r3.code

        return "Wat", "wat"

    def inValidate(self, s):
        # Original conditional:
        # (s == null || s != null && (s.matches("[\r\n\t ]+") || s.equals("") || s.equalsIgnoreCase("about:blank")))
        if not s:
            return True

        if re.search("[\r\n\t ]+", s) or s.lower() == "about:blank":
            return True
        else:
            return False

    def _unshorten_adfocus(self, uri):
        orig_uri = uri
        try:

            r = httptools.downloadpage(uri, timeout=self._timeout)
            html = r.data

            adlink = re.findall("click_url =.*;", html)

            if len(adlink) > 0:
                uri = re.sub('^click_url = "|"\;$', '', adlink[0])
                if re.search(r'http(s|)\://adfoc\.us/serve/skip/\?id\=', uri):
                    http_header = dict()
                    http_header["Host"] = "adfoc.us"
                    http_header["Referer"] = orig_uri

                    r = httptools.downloadpage(uri, headers=http_header, timeout=self._timeout)

                    uri = r.url
                return uri, r.code
            else:
                return uri, 'No click_url variable found'
        except Exception as e:
            return uri, str(e)

    def _unshorten_lnxlu(self, uri):
        try:
            r = httptools.downloadpage(uri, timeout=self._timeout)
            html = r.data

            code = re.findall('/\?click\=(.*)\."', html)

            if len(code) > 0:
                payload = {'click': code[0]}
                r = httptools.downloadpage(
                    'http://lnx.lu?' + urllib.urlencode(payload),
                    timeout=self._timeout)
                return r.url, r.code
            else:
                return uri, 'No click variable found'
        except Exception as e:
            return uri, str(e)

    def _unshorten_shst(self, uri):
        try:
            r = httptools.downloadpage(uri, timeout=self._timeout)
            html = r.data
            session_id = re.findall(r'sessionId\:(.*?)\"\,', html)
            if len(session_id) > 0:
                session_id = re.sub(r'\s\"', '', session_id[0])

                http_header = dict()
                http_header["Content-Type"] = "application/x-www-form-urlencoded"
                http_header["Host"] = "sh.st"
                http_header["Referer"] = uri
                http_header["Origin"] = "http://sh.st"
                http_header["X-Requested-With"] = "XMLHttpRequest"

                if config.is_xbmc():
                    import xbmc
                    xbmc.sleep(5 * 1000)
                else:
                    time.sleep(5 * 1000)

                payload = {'adSessionId': session_id, 'callback': 'c'}
                r = httptools.downloadpage(
                    'http://sh.st/shortest-url/end-adsession?' +
                    urllib.urlencode(payload),
                    headers=http_header,
                    timeout=self._timeout)
                response = r.data[6:-2].decode('utf-8')

                if r.code == 200:
                    resp_uri = json.loads(response)['destinationUrl']
                    if resp_uri is not None:
                        uri = resp_uri
                    else:
                        return uri, 'Error extracting url'
                else:
                    return uri, 'Error extracting url'

            return uri, r.code

        except Exception as e:
            return uri, str(e)

    def _unshorten_hrefli(self, uri):
        try:
            # Extract url from query
            parsed_uri = urlparse(uri)
            extracted_uri = parsed_uri.query
            if not extracted_uri:
                return uri, 200
            # Get url status code
            r = httptools.downloadpage(
                extracted_uri,
                timeout=self._timeout,
                follow_redirects=False)
            return r.url, r.code
        except Exception as e:
            return uri, str(e)

    def _unshorten_anonymz(self, uri):
        # For the moment they use the same system as hrefli
        return self._unshorten_hrefli(uri)

    def _unshorten_shrink_service(self, uri):
        try:
            r = httptools.downloadpage(uri, timeout=self._timeout, cookies=False)
            html = r.data

            uri = re.findall(r"<input type='hidden' name='\d+' id='\d+' value='([^']+)'>", html)[0]

            from core import scrapertools
            uri = scrapertools.decodeHtmlentities(uri)

            uri = uri.replace("&sol;", "/") \
                .replace("&colon;", ":") \
                .replace("&period;", ".") \
                .replace("&excl;", "!") \
                .replace("&num;", "#") \
                .replace("&quest;", "?") \
                .replace("&lowbar;", "_")

            return uri, r.code

        except Exception as e:
            return uri, str(e)

    def _unshorten_rapidcrypt(self, uri):
        try:
            r = httptools.downloadpage(uri, timeout=self._timeout, cookies=False)
            html = r.data

            if 'embed' in uri:
                uri = re.findall(r'<a class="play-btn" href=([^">]*)>', html)[0]
            else:
                uri = re.findall(r'<a class="push_button blue" href=([^>]+)>', html)[0]

            return uri, r.code

        except Exception as e:
            return uri, 0

    def _unshorten_cryptmango(self, uri):
        try:
            r = httptools.downloadpage(uri, timeout=self._timeout, cookies=False)
            html = r.data

            uri = re.findall(r'<iframe src="([^"]+)"[^>]+>', html)[0]

            return uri, r.code

        except Exception as e:
            return uri, str(e)


def unwrap_30x_only(uri, timeout=10):
    unshortener = UnshortenIt()
    uri, status = unshortener.unwrap_30x(uri, timeout=timeout)
    return uri, status


def unshorten_only(uri, type=None, timeout=10):
    unshortener = UnshortenIt()
    uri, status = unshortener.unshorten(uri, type=type)
    return uri, status


def unshorten(uri, type=None, timeout=10):
    unshortener = UnshortenIt()
    uri, status = unshortener.unwrap_30x(uri, timeout=timeout)
    uri, status = unshortener.unshorten(uri, type=type)
    if status == 200:
        uri, status = unshortener.unwrap_30x(uri, timeout=timeout)
    return uri, status


def sortened_urls(url, url_base64, host, retry=False, referer=None, alfa_s=True, item=Item()):
    
    if not PY3:
        from lib.alfaresolver import unlock_urls
    else:
        from lib.alfaresolver_py3 import unlock_urls

    return unlock_urls(url, url_base64, host, retry=retry, referer=referer, alfa_s=alfa_s, item=item)
