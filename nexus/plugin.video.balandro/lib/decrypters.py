# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    PY3 = False

    import urllib
    from urllib import unquote_plus

    import urlparse
else:
    PY3 = True

    import urllib.parse as urlparse
    from urllib.parse import unquote_plus

import re, base64

from core import httptools, scrapertools
from platformcode import logger


patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'
patron_linkser = 'name="linkser"\s*value="([^"]*)"'

key_safe = 'fee631d2cffda38a78b96ee6d2dfb43a'


def decrypt_dcs(code):
    left = ''
    right = ''

    matches = scrapertools.find_single_match(code, "ysmm = '(.*?)';")        

    for c in [matches[i:i+2] for i in range(0, len(matches), 2)]:
        left += c[0]
        right = c[1] + right

    encoded_uri = list(left + right)
    numbers = ((i, n) for i, n in enumerate(encoded_uri) if str.isdigit(n))
    for first, second in zip(numbers, numbers):
        xor = int(first[1]) ^ int(second[1])
        if xor < 10: encoded_uri[first[0]] = str(xor)

    decoded_uri = base64.b64decode("".join(encoded_uri).encode())[16:-16].decode()

    if re.search(r'go\.php\?u\=', decoded_uri): decoded_uri = base64.b64decode(re.sub(r'(.*?)u=', '', decoded_uri)).decode()

    data = unquote_plus(unquote_plus(decoded_uri))

    final_url = scrapertools.find_single_match(data,'\&dest\=(.*?)$')

    return final_url


def decode_adfly(url, unquoted=True):
    logger.info()

    def resolve(code):
        zeros = ''
        ones = ''
        for n,letter in enumerate(code):
            if n % 2 == 0: zeros += code[n]
            else: ones = code[n] + ones

        key = zeros + ones
        key = list(key)
        i = 0

        while i < len(key):
            if key[i].isdigit():
                for j in range(i + 1, len(key)):
                    if key[j].isdigit():
                        u = int(key[i])^int(key[j])
                        if u < 10: key[i] = str(u)
                        i = j                   
                        break
            i +=1

        key = ''.join(key)

        return base64.b64decode(key)[16:-16].decode('utf-8')

    data = httptools.downloadpage(url).data
    ysmm = scrapertools.find_single_match(data, "var ysmm = '([^']+)';")
    if not ysmm: 
        logger.debug('Adfly no detectado en: %s' % url)
        # ~ logger.debug(data)
        return ''

    newurl = resolve(ysmm)
    if unquoted:
        newurl = urllib.unquote(urllib.unquote(newurl))
        if 'dest=' in newurl: newurl = scrapertools.find_single_match(newurl, 'dest=([^&]+)')
        elif 'href=' in newurl: newurl = scrapertools.find_single_match(newurl, 'href=([^&]+)')
        else: logger.debug('Adfly redirección no contemplada: %s => %s' % (url, newurl))

    if not newurl.startswith('http'): return ''

    return newurl


def decode_uiiio(url):
    logger.info()

    data = httptools.downloadpage(url).data

    # ~ Usa recaptcha v2 invisible
    if '/recaptcha/' in data: url = ''

    return url

def decode_srtam(url):
    logger.info()

    data = httptools.downloadpage(url).data

    # ~ Usa recaptcha v2 invisible
    if '/recaptcha/' in data: url = ''

    return url

def decode_streamcrypt(url):
    logger.info()

    n = 0
    while url and 'streamcrypt.net/' in url and n < 5:
        if 'embed.php' in url and not 'p=2' in url: url += '&p=2'
        url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')
        n += 1

    return url


def decode_url_base64(url, host_torrent):
    logger.info()

    host_list = [
        ('adfly.mobi')
        ]

    domain = scrapertools.find_single_match(url, patron_domain)

    url_base64 = url

    url_sufix = ''

    if '&' in url_base64 and not 'magnet:' in url_base64:
        url_base64_list = url_base64.split('&')
        url_base64 = url_base64_list[0]

        for param in url_base64_list[1:]:
            url_sufix += '&%s' % param

    if '=http' in url_base64 and not 'magnet:' in url_base64: url_base64 = scrapertools.find_single_match(url_base64, '=(http.*?$)')

    if len(url_base64) > 1 and not 'magnet:' in url_base64 and not '.torrent' in url_base64:
        patron_php = 'php(?:#|\?\w=)(.*?)(?:\&|$)'

        if not scrapertools.find_single_match(url_base64, patron_php): patron_php = '\?(?:\w+=.*&)?(?:urlb64)?=(.*?)(?:&|$)'

        url_base64 = scrapertools.find_single_match(url_base64, patron_php)

        try:
            for x in range(20):
                url_base64 = base64.b64decode(url_base64).decode('utf-8')

            url_base64 = url
        except:
            if url_base64 and url_base64 != url: url_base64 = url_base64.replace(' ', '%20')

            if not url_base64: url_base64 = url

            if url_base64.startswith('magnet') or url_base64.endswith('.torrent'): return url_base64 + url_sufix

            if domain and domain in str(host_list): url_base64_bis = sorted_urls(url_base64, url_base64, host_torrent)
            else: url_base64_bis = sorted_urls(url, url_base64, host_torrent)

            domain_bis = scrapertools.find_single_match(url_base64_bis, patron_domain)

            if domain_bis: domain = domain_bis

            if url_base64_bis != url_base64: url_base64 = url_base64_bis

            if '//cdn.pizza/' in url_base64:
                if url_base64.startswith('//cdn.pizza/'): url_base64 = 'https:' + url_base64
                return url_base64

    if not domain: domain = 'default'

    if host_torrent and host_torrent not in url_base64 and not url_base64.startswith('magnet') and domain not in str(host_list):
        url_base64 = urlparse.urljoin(host_torrent, url_base64)

        if url_base64 != url or host_torrent not in url_base64:
            host_name = scrapertools.find_single_match(url_base64, patron_host)
            url_base64 = re.sub(host_name, host_torrent, url_base64)

    return url_base64 + url_sufix


def sorted_urls(url, url_base64, host_torrent):
    logger.info()

    from lib.pyberishaes import GibberishAES

    sortened_domains = {
            'acortalink.me': ['linkser=uggcf%3A%2F%2Flrfgbeerag.arg', "TTTOzBmk\s*=\s*'(.*?)'", 14, 8, False],
            'acortaenlace.com': ['linkser=uggcf%3A%2F%2Fzntargcryvf.pbz', "TTTOzBmk\s*=\s*'(.*?)'", 14, 8, False],
            'acorta-enlace.com': ['linkser=ngbzgg.pbz', "TTTOzBmk\s*=\s*'(.*?)'", 14, 8, False],
            'short-link.one': ['linkser=uggcf%3A%2F%2Fpvargbeerag.pb', "TTTOzBmk\s*=\s*'(.*?)'", 14, 8, False],
            'acorta-link.com': ['linkser=uggcf%3A%2F%2Fgbqbgbeeragf.arg', "TTTOzBmk\s*=\s*'(.*?)'", 14, 8, False],
            'acortame-esto.com': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'mediafire.com': [None, '(?i)=\s*"Download file"\s*href="([^"]+)"\s*id\s*=\s*"downloadButton"', 0, 0, False],
            'sub-short.link': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'divxto.site': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'ddtorrent.live': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'short-info.link': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'desbloqueador.site': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'ttlinks.live': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'enlace-directo.com': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'linkup.wf': ['linkser=uggcf%3A%2F%2Flrfgbeerag.arg', "TTTOzBmk\s*=\s*'(.*?)'", 14, 8, False],
            'link-vip.xyz': ['linkser=uggcf%3A%2F%2Flrfgbeerag.arg', "TTTOzBmk\s*=\s*'(.*?)'", 14, 8, False],
            'recorta-enlace.com': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'enlace-rapido.com': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'enlace-protegido.com': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False],
            'super-enlace.com': [None, [64, 123 ,77, 91, 96, 109, 13, 13], 0, 0, False]
            }

    if not url_base64 or url_base64.startswith('magnet') or url_base64.endswith('.torrent'): return url_base64

    domain = scrapertools.find_single_match(url, patron_domain)

    if sortened_domains.get(domain, False) == False or not url_base64 or url_base64.startswith('magnet'): return url_base64

    if ('//' in url_base64  or ':?' in url_base64) and not (url_base64.startswith('magnet') or url_base64.startswith('http')):
        try:
            chers = []

            chars = GibberishAES.s2a(GibberishAES(), url_base64)
            chors = sortened_domains[domain][1]

            for c in chars:
                try:
                    if chors[0] < c < chors[1]:
                        if chors[2] < c < chors[3]: chers.append(c - chors[6])
                        elif c > chors[5]: chers.append(c - chors[6])
                        elif chors[3] <= c <= chors[4]: chers.append(c)
                        else: chers.append(c + chors[7])
                    else:
                        chers.append(c)
                except:
                    chers.append(c)

            url_base64 = "".join([chr(x) for x in chers])
        except:
            import traceback
            logger.error('Error translation: %s' % url_base64)
            logger.error(traceback.format_exc())

        return url_base64

    host_name = scrapertools.find_single_match(url, patron_host)

    if host_name and not host_name.endswith('/'): host_name += '/'

    if url_base64.startswith('http'):
        resp = httptools.downloadpage(url_base64, only_headers=True)
        if resp.sucess: return url_base64

    data_new = httptools.downloadpage(url, headers={'Referer': host_torrent}, raise_weberror=False).data
    data_new = re.sub(r'\n|\r|\t', '', data_new)

    if sortened_domains[domain][1] and scrapertools.find_single_match(data_new, sortened_domains[domain][1]):
        url_base64 = scrapertools.find_single_match(data_new, sortened_domains[domain][1])
        if url_base64.startswith('magnet') or url_base64.startswith('http'): return url_base64

    if scrapertools.find_single_match(data_new, patron_linkser):
        sortened_domains[domain][0] = 'linkser=%s' % unquote_plus(scrapertools.find_single_match(data_new, patron_linkser))

    post = sortened_domains[domain][0]

    headers = {'Referer': url, 'Content-type': 'application/x-www-form-urlencoded'}

    data_new = httptools.downloadpage(host_name, post=post, headers=headers, raise_weberror=False).data
    data_new = re.sub(r'\n|\r|\t', '', data_new)

    key = ''

    if data_new :
        key = scrapertools.find_single_match(data_new, sortened_domains[domain][1])
        if not key or not sortened_domains[domain][1]: key = key_safe

    try:
        url_base64_bis = None

        if not key: key = key_safe

        url_base64_bis = GibberishAES(string=url_base64, pass_=key, Nr=sortened_domains[domain][2], Nk=sortened_domains[domain][3], Decrypt=sortened_domains[domain][4])

        if url_base64_bis.result and (url_base64_bis.result.startswith('magnet') or url_base64_bis.result.startswith('http') or url_base64_bis.result.startswith('//')):
            if url_base64_bis.result.startswith('//'): url_base64 = 'https:' + url_base64_bis.result
            else: url_base64 = url_base64_bis.result
        else:
            if url_base64_bis.result.startswith('//cdn.pizza/'):
                url_base64 = 'https:' + url_base64_bis.result
                return url_base64

            logger.error('Error Result: %s' % url_base64_bis.result)
            return url_base64
    except:
        import traceback
        logger.error('Error Key: %s' % key)
        logger.error(traceback.format_exc())
        return url_base64

    if not (url_base64.startswith('magnet') or url_base64.startswith('http')): key = ''

    if not key: return sorted_urls(url, url_base64, host_torrent)

    return url_base64
