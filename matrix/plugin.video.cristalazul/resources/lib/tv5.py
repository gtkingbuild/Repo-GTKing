
import base64
import re
import zlib

from six.moves import urllib_parse
from six.moves import urllib_request


key = base64.b64decode(b'ZXQgb3VhaSBtZWMh')


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


def decode_base64_and_inflate(b64string):
    decoded_data = base64.b64decode(b64string)
#    print ord(decoded_data[0])
    return zlib.decompress(decoded_data , 15)


def deflate_and_base64_encode(string_val):
    zlibbed_str = zlib.compress(string_val)
    compressed_string = zlibbed_str  # # zlibbed_str[2:-4]
    return base64.b64encode(compressed_string)

    
def decode(param1, param2):
    param1dec = decode_base64_and_inflate(param1)
    _loc3_ = bytearray()
    _loc3_.extend(param1dec)
    _loc4_ = 0;
    _loc5_ = len(param1dec);
    _loc6_ = 0;
    while _loc6_ < _loc5_:
        _loc3_[_loc6_] = _loc3_[_loc6_] ^ ord(param2[_loc4_]);
        _loc4_ += 1;
        if(_loc4_ >= len(param2)):
            _loc4_ = 0;
        _loc6_ += 1;
    return _loc3_


def encode(param1, param2):
    param1dec = param1
    _loc3_ = bytearray()
    _loc3_.extend(param1dec)
    _loc4_ = 0;
    _loc5_ = len(param1dec);
    _loc6_ = 0;
    while _loc6_ < _loc5_:
        _loc3_[_loc6_] = _loc3_[_loc6_] ^ ord(param2[_loc4_]);
        _loc4_ += 1;
        if(_loc4_ >= len(param2)):
            _loc4_ = 0;
        _loc6_ += 1;
    return  deflate_and_base64_encode(_loc3_.decode("utf-8"))
    return _loc3_  


def extractUrl(uid): 
    str = "operation=getPlaylist&uid=%s" % urllib_parse.quote_plus(uid)
    str = encode(str, key)
    s = getUrl("http://www.tv5mondeplusafrique.com/html/servicesV2/getPlaylist.xml?BulkLoaderNoCache=2_2&", post=str)
    s = decode(s, key)
    print ("returned", repr(s.decode("unicode-escape")))
    from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
    xmlobj = BeautifulSOAP(s.decode("unicode-escape"), convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    
    vurl = xmlobj("video")[0];
    su = vurl("secureurl")[0].string
    su = re.sub('[\[CDATA\]]', '', su)
    if 'manifest.f4m?' in su:
        su = 'plugin://plugin.video.f4mTester/?url=' + urllib_parse.quote_plus(su)
    return su
