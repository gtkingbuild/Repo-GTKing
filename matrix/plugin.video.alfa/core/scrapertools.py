# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Scraper tools for reading and processing web elements
# --------------------------------------------------------------------------------

#from future import standard_library
#standard_library.install_aliases()
#from builtins import str
#from builtins import chr
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido
    import urlparse

import re
import time

PATTERN_EPISODE_TITLE = '(?i)(\d+x\d+\s*(?:-\s*)?)?(?:episod(?:e|io)|cap.tulo)\s*\d*\s*(?:\[\d{4}\]\s*)?(?:\[\d{1,2}.\d{1,2}\]\s*)?'


def get_header_from_response(url, header_to_get="", post=None, headers=None):
    from core import httptools
    header_to_get = header_to_get.lower()
    response = httptools.downloadpage(url, post=post, headers=headers, only_headers=True)
    return response.headers.get(header_to_get)


def read_body_and_headers(url, post=None, headers=None, follow_redirects=False, timeout=None):
    from core import httptools
    response = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects,
                                      timeout=timeout)
    return response.data, response.headers


def printMatches(matches):
    from platformcode import logger
    i = 0
    for match in matches:
        logger.info("%d %s" % (i, match))
        i = i + 1


def find_single_match(data, pattern, index=0):
    try:
        matches = re.findall(pattern, data, flags=re.DOTALL)
        return matches[index]
    except Exception:
        return ""


# Parse string and extracts multiple matches using regular expressions
def find_multiple_matches(text, pattern):
    return re.findall(pattern, text, re.DOTALL)


def replace(pattern, replacement, data):
    try:
        return re.sub(pattern, replacement, data, flags=re.DOTALL)
    except Exception:
        return ""


def entityunescape(cadena):
    return unescape(cadena)


def unescape(text):
    """Removes HTML or XML character references
       and entities from a text string.
       keep &amp;, &gt;, &lt; in the source code.
    from Fredrik Lundh
    http://effbot.org/zone/re-sub.htm#unescape-html
    """

    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    text = unichr(int(text[3:-1], 16)).encode("utf-8")
                else:
                    text = unichr(int(text[2:-1])).encode("utf-8")
                if PY3 and isinstance(text, bytes):
                    text = text.decode("utf-8")
                return text

            except ValueError:
                from platformcode import logger
                logger.error("error de valor")
                pass
        else:
            # named entity
            try:
                if PY3:
                    import html.entities as htmlentitydefs
                else:
                    import htmlentitydefs
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]]).encode("utf-8")
                if PY3 and isinstance(text, bytes):
                    text = text.decode("utf-8")
            except KeyError:
                from platformcode import logger
                logger.error("keyerror: %s" % str(text))
                pass
            except Exception:
                pass
        return text  # leave as is

    if PY3:
        text = text.replace(u'\xa0', ' ').replace('\xa0', ' ')
    else:
        text = text.replace(u'\xa0', ' ')
    return re.sub("&#?\w+;", fixup, str(text))

    # Convierte los codigos html "&ntilde;" y lo reemplaza por "ñ" caracter unicode utf-8


def decodeHtmlentities(string):
    string = entitiesfix(string)
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")

    def substitute_entity(match):
        if PY3:
            from html.entities import name2codepoint as n2cp
        else:
            from htmlentitydefs import name2codepoint as n2cp
        ent = match.group(2)
        if match.group(1) == "#":
            ent = unichr(int(ent)).encode('utf-8')
            if PY3 and isinstance(ent, bytes):
                ent = ent.decode("utf-8")
            return ent
        else:
            cp = n2cp.get(ent)

            if cp:
                cp = unichr(cp).encode('utf-8')
                if PY3 and isinstance(cp, bytes):
                    cp = cp.decode("utf-8")
                return cp
            else:
                return match.group()

    return entity_re.subn(substitute_entity, string)[0]


def entitiesfix(string):
    # Las entidades comienzan siempre con el símbolo & , y terminan con un punto y coma ( ; ).
    string = string.replace("&aacute", "&aacute;")
    string = string.replace("&eacute", "&eacute;")
    string = string.replace("&iacute", "&iacute;")
    string = string.replace("&oacute", "&oacute;")
    string = string.replace("&uacute", "&uacute;")
    string = string.replace("&Aacute", "&Aacute;")
    string = string.replace("&Eacute", "&Eacute;")
    string = string.replace("&Iacute", "&Iacute;")
    string = string.replace("&Oacute", "&Oacute;")
    string = string.replace("&Uacute", "&Uacute;")
    string = string.replace("&uuml", "&uuml;")
    string = string.replace("&Uuml", "&Uuml;")
    string = string.replace("&ntilde", "&ntilde;")
    string = string.replace("&#191", "&#191;")
    string = string.replace("&#161", "&#161;")
    string = string.replace(";;", ";")
    return string


def htmlclean(cadena):
    cadena = re.compile("<!--.*?-->", re.DOTALL).sub("", cadena)

    cadena = cadena.replace("<center>", "")
    cadena = cadena.replace("</center>", "")
    cadena = cadena.replace("<cite>", "")
    cadena = cadena.replace("</cite>", "")
    cadena = cadena.replace("<em>", "")
    cadena = cadena.replace("</em>", "")
    cadena = cadena.replace("<u>", "")
    cadena = cadena.replace("</u>", "")
    cadena = cadena.replace("<li>", "")
    cadena = cadena.replace("</li>", "")
    cadena = cadena.replace("<turl>", "")
    cadena = cadena.replace("</tbody>", "")
    cadena = cadena.replace("<tr>", "")
    cadena = cadena.replace("</tr>", "")
    cadena = cadena.replace("<![CDATA[", "")
    cadena = cadena.replace("<wbr>", "")
    cadena = cadena.replace("<Br />", " ")
    cadena = cadena.replace("<BR />", " ")
    cadena = cadena.replace("<Br>", " ")
    cadena = re.compile("<br[^>]*>", re.DOTALL).sub(" ", cadena)

    cadena = re.compile("<script.*?</script>", re.DOTALL).sub("", cadena)

    cadena = re.compile("<option[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</option>", "")

    cadena = re.compile("<button[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</button>", "")

    cadena = re.compile("<i[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</iframe>", "")
    cadena = cadena.replace("</i>", "")

    cadena = re.compile("<table[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</table>", "")

    cadena = re.compile("<td[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</td>", "")

    cadena = re.compile("<div[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</div>", "")

    cadena = re.compile("<dd[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</dd>", "")

    cadena = re.compile("<b[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</b>", "")

    cadena = re.compile("<font[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</font>", "")

    cadena = re.compile("<strong[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</strong>", "")

    cadena = re.compile("<small[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</small>", "")

    cadena = re.compile("<span[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</span>", "")

    cadena = re.compile("<a[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</a>", "")

    cadena = re.compile("<p[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</p>", "")

    cadena = re.compile("<ul[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</ul>", "")

    cadena = re.compile("<h1[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</h1>", "")

    cadena = re.compile("<h2[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</h2>", "")

    cadena = re.compile("<h3[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</h3>", "")

    cadena = re.compile("<h4[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</h4>", "")

    cadena = re.compile("<!--[^-]+-->", re.DOTALL).sub("", cadena)

    cadena = re.compile("<img[^>]*>", re.DOTALL).sub("", cadena)

    cadena = re.compile("<object[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</object>", "")
    cadena = re.compile("<param[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</param>", "")
    cadena = re.compile("<embed[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</embed>", "")

    cadena = re.compile("<title[^>]*>", re.DOTALL).sub("", cadena)
    cadena = cadena.replace("</title>", "")

    cadena = re.compile("<link[^>]*>", re.DOTALL).sub("", cadena)

    cadena = cadena.replace("\t", "")
    cadena = entityunescape(cadena)
    return cadena


def slugify(title, strict=True, convert=[]):
    # print title

    # Sustituye acentos y eñes
    title = title.replace("Á", "a")
    title = title.replace("É", "e")
    title = title.replace("Í", "i")
    title = title.replace("Ó", "o")
    title = title.replace("Ú", "u")
    title = title.replace("á", "a")
    title = title.replace("é", "e")
    title = title.replace("í", "i")
    title = title.replace("ó", "o")
    title = title.replace("ú", "u")
    title = title.replace("À", "a")
    title = title.replace("È", "e")
    title = title.replace("Ì", "i")
    title = title.replace("Ò", "o")
    title = title.replace("Ù", "u")
    title = title.replace("à", "a")
    title = title.replace("è", "e")
    title = title.replace("ì", "i")
    title = title.replace("ò", "o")
    title = title.replace("ù", "u")
    title = title.replace("ç", "c")
    title = title.replace("Ç", "C")
    title = title.replace("Ñ", "ñ")
    title = title.replace("ñ", "n")
    title = title.replace("/", "-")
    title = title.replace("&amp;", "&")
    title = title.replace("&#038;", "&")

    # Pasa a minúsculas
    title = title.lower().strip()
    
    # Covierte los caracteres sumisnistrados por el usuario y los añade a la lista de conversión
    validchars = "abcdefghijklmnopqrstuvwxyz1234567890- "
    if not strict: validchars += "()[]."
    try:
        for change in convert:
            change_from = change.split('=')[0]
            change_to = change.split('=')[1]
            title = title.replace(change_from, change_to)
            if change_to and change_to not in validchars: validchars += change_to
    except:
        pass

    # Elimina caracteres no válidos
    title = ''.join(c for c in title if c in validchars)

    if strict:
        # Sustituye espacios en blanco duplicados y saltos de línea
        title = re.compile("\s+", re.DOTALL).sub(" ", title)

        # Sustituye espacios en blanco por guiones
        title = re.compile("\s", re.DOTALL).sub("-", title.strip())

        # Sustituye espacios en blanco duplicados y saltos de línea
        title = re.compile("\-+", re.DOTALL).sub("-", title)

    # Arregla casos especiales
    if title.startswith("-"):
        title = title[1:]

    if title == "":
        title = "-" + str(time.time())

    return title


def remove_htmltags(string):
    return re.sub('<[^<]+?>', '', string)


def get_filename_from_url(url):

    parsed_url = urlparse.urlparse(url)
    try:
        filename = parsed_url[2]
    except Exception:
        filename = ""

    if "/" in filename:
        filename = filename.split("/")[-1]

    return filename


def get_domain_from_url(url):
    parsed_url = urlparse.urlparse(url)
    try:
        domain = parsed_url[1]
    except Exception:
        domain = ""

    return domain


def unquote(url, plus=False):
    if plus:
        url = urllib.unquote_plus(url)
    else:
        url = urllib.unquote(url)
    
    return url

def quote(url, plus=False):
    if plus:
        url = urllib.quote_plus(url)
    else:
        url = urllib.quote(url)
    return url


def normalize(string):
    import unicodedata
    if not PY3 and isinstance(string, str):
        string = string.decode('utf-8')
    normal = ''.join((c for c in unicodedata.normalize('NFD', unicode(string)) if unicodedata.category(c) != 'Mn'))
    return normal

def remove_format(string):
    #from platformcode import logger
    #logger.info()
    string = string.rstrip()
    string = re.sub(r'(\[|\[\/)(?:color|COLOR|b|B|i|I).*?\]', '', string)
    string = re.sub(r'\:|\.|\-|\_|\,|\¿|\?|\¡|\!|\"|\'|\&', ' ', string)
    string = re.sub(r'\(.*?\).*|\[.*?\].*', ' ', string)
    string = re.sub(r'\s+', ' ', string).strip()
    #logger.debug('sale de remove: %s' % string)
    return string

def simplify(title, year):
    #from platformcode import logger
    
    if not year or year == '-':
        year = find_single_match(title, r"^.+?\s*(?:(\(\d{4}\)$|\[\d{4}\]))")
        if year:
            title = title.replace(year, "").strip()
            year = year[1:-1]
        else:
            year = '-'
    
    title = remove_format(title)
    #title = normalize(title)

    #logger.error(title.lower())
    return title.lower(), year


def get_season_and_episode(title):
    """
    Retorna el numero de temporada y de episodio en formato "1x01" obtenido del titulo de un episodio
    Ejemplos de diferentes valores para title y su valor devuelto:
        "serie 101x1.strm", "s101e1.avi", "t101e1.avi"  -> '101x01'
        "Name TvShow 1x6.avi" -> '1x06'
        "Temp 3 episodio 2.avi" -> '3x02'
        "Alcantara season 13 episodie 12.avi" -> '13x12'
        "Temp1 capitulo 14" -> '1x14'
        "Temporada 1: El origen Episodio 9" -> '' (entre el numero de temporada y los episodios no puede haber otro texto)
        "Episodio 25: titulo episodio" -> '' (no existe el numero de temporada)
        "Serie X Temporada 1" -> '' (no existe el numero del episodio)
    @type title: str
    @param title: titulo del episodio de una serie
    @rtype: str
    @return: Numero de temporada y episodio en formato "1x01" o cadena vacia si no se han encontrado
    """
    #from platformcode import logger
    filename = ""

    patrons = ["(\d+)\s*[x-]\s*(\d+)", "(\d+)\s*×\s*(\d+)", "(?:s|t)(\d+) ?e(\d+)",
               "(?:season|temp\w*)\s*(\d+)\s*(?:capitulo|epi|episode\w*)\s*(\d+)"]

    for patron in patrons:
        try:
            matches = re.compile(patron, re.I).search(title)
            if matches:
                if len(matches.group(1)) == 1:
                    filename = matches.group(1) + "x" + matches.group(2).zfill(2)
                else:
                    filename = matches.group(1).lstrip('0') + "x" + matches.group(2).zfill(2)
                break
        except Exception:
            pass

    # logger.info("'" + title + "' -> '" + filename + "'")

    return filename


def decode_utf8_error(path):
    """
    Convierte una cadena de texto en utf8 que tiene errores de conversión
    reemplazando los caracteres que no estén permitidos en utf-8 por los reales
    @type: str
    @param path: ruta
    @rtype: str
    @return: ruta codificado en UTF-8
    """
    
    utf8_error_table = [
                        ('€', '\xE2\x82\xAC'), 
                        ('‚', '\xE2\x80\x9A'), 
                        ('ƒ', '\xC6\x92'), 
                        ('„', '\xE2\x80\x9E'), 
                        ('…', '\xE2\x80\xA6'), 
                        ('†', '\xE2\x80\xA0'), 
                        ('‡', '\xE2\x80\xA1'), 
                        ('ˆ', '\xCB\x86'), 
                        ('‰', '\xE2\x80\xB0'), 
                        ('Š', '\xC5\xA0'), 
                        ('‹', '\xE2\x80\xB9'), 
                        ('Œ', '\xC5\x92'), 
                        ('Ž', '\xC5\xBD'), 
                        ('‘', '\xE2\x80\x98'), 
                        ('’', '\xE2\x80\x99'), 
                        ('“', '\xE2\x80\x9C'), 
                        ('”', '\xE2\x80\x9D'), 
                        ('•', '\xE2\x80\xA2'), 
                        ('–', '\xE2\x80\x93'), 
                        ('—', '\xE2\x80\x94'), 
                        ('˜', '\xCB\x9C'), 
                        ('™', '\xE2\x84\xA2'), 
                        ('š', '\xC5\xA1'), 
                        ('›', '\xE2\x80\xBA'), 
                        ('œ', '\xC5\x93'), 
                        ('ž', '\xC5\xBE'), 
                        ('Ÿ', '\xC5\xB8'), 
                        ('¡', '\xC2\xA1'), 
                        ('¢', '\xC2\xA2'), 
                        ('£', '\xC2\xA3'), 
                        ('¤', '\xC2\xA4'), 
                        ('¥', '\xC2\xA5'), 
                        ('¦', '\xC2\xA6'), 
                        ('§', '\xC2\xA7'), 
                        ('¨', '\xC2\xA8'), 
                        ('©', '\xC2\xA9'), 
                        ('ª', '\xC2\xAA'), 
                        ('«', '\xC2\xAB'), 
                        ('¬', '\xC2\xAC'), 
                        ('­', '\xC2\xAD'), 
                        ('®', '\xC2\xAE'), 
                        ('¯', '\xC2\xAF'), 
                        ('°', '\xC2\xB0'), 
                        ('±', '\xC2\xB1'), 
                        ('²', '\xC2\xB2'), 
                        ('³', '\xC2\xB3'), 
                        ('´', '\xC2\xB4'), 
                        ('µ', '\xC2\xB5'), 
                        ('¶', '\xC2\xB6'), 
                        ('·', '\xC2\xB7'), 
                        ('¸', '\xC2\xB8'), 
                        ('¹', '\xC2\xB9'), 
                        ('º', '\xC2\xBA'), 
                        ('»', '\xC2\xBB'), 
                        ('¼', '\xC2\xBC'), 
                        ('½', '\xC2\xBD'), 
                        ('¾', '\xC2\xBE'), 
                        ('¿', '\xC2\xBF'), 
                        ('À', '\xC3\x80'), 
                        ('Á', '\xC3\x81'), 
                        ('Â', '\xC3\x82'), 
                        ('Ã', '\xC3\x83'), 
                        ('Ä', '\xC3\x84'), 
                        ('Å', '\xC3\x85'), 
                        ('Æ', '\xC3\x86'), 
                        ('Ç', '\xC3\x87'), 
                        ('È', '\xC3\x88'), 
                        ('É', '\xC3\x89'), 
                        ('Ê', '\xC3\x8A'), 
                        ('Ë', '\xC3\x8B'), 
                        ('Ì', '\xC3\x8C'), 
                        ('Í', '\xC3\x8D'), 
                        ('Î', '\xC3\x8E'), 
                        ('Ï', '\xC3\x8F'), 
                        ('Ð', '\xC3\x90'), 
                        ('Ñ', '\xC3\x91'), 
                        ('Ò', '\xC3\x92'), 
                        ('Ó', '\xC3\x93'), 
                        ('Ô', '\xC3\x94'), 
                        ('Õ', '\xC3\x95'), 
                        ('Ö', '\xC3\x96'), 
                        ('×', '\xC3\x97'), 
                        ('Ø', '\xC3\x98'), 
                        ('Ù', '\xC3\x99'), 
                        ('Ú', '\xC3\x9A'), 
                        ('Û', '\xC3\x9B'), 
                        ('Ü', '\xC3\x9C'), 
                        ('Ý', '\xC3\x9D'), 
                        ('Þ', '\xC3\x9E'), 
                        ('ß', '\xC3\x9F'), 
                        ('à', '\xC3\xA0'), 
                        ('á', '\xC3\xA1'), 
                        ('â', '\xC3\xA2'), 
                        ('ã', '\xC3\xA3'), 
                        ('ä', '\xC3\xA4'), 
                        ('å', '\xC3\xA5'), 
                        ('æ', '\xC3\xA6'), 
                        ('ç', '\xC3\xA7'), 
                        ('è', '\xC3\xA8'), 
                        ('é', '\xC3\xA9'), 
                        ('ê', '\xC3\xAA'), 
                        ('ë', '\xC3\xAB'), 
                        ('ì', '\xC3\xAC'), 
                        ('í', '\xC3\xAD'), 
                        ('î', '\xC3\xAE'), 
                        ('ï', '\xC3\xAF'), 
                        ('ð', '\xC3\xB0'), 
                        ('ñ', '\xC3\xB1'), 
                        ('ò', '\xC3\xB2'), 
                        ('ó', '\xC3\xB3'), 
                        ('ô', '\xC3\xB4'), 
                        ('õ', '\xC3\xB5'), 
                        ('ö', '\xC3\xB6'), 
                        ('÷', '\xC3\xB7'), 
                        ('ø', '\xC3\xB8'), 
                        ('ù', '\xC3\xB9'), 
                        ('ú', '\xC3\xBA'), 
                        ('û', '\xC3\xBB'), 
                        ('ü', '\xC3\xBC'), 
                        ('ý', '\xC3\xBD'), 
                        ('þ', '\xC3\xBE'), 
                        ('ÿ', '\xC3\xBF')
                        ]

    if path:
        try:
            for char_right, chars_wrong in utf8_error_table:
                path = path.replace(chars_wrong, char_right)
        except Exception:
            pass
        
        path = htmlparser(path)
        
    return path


def htmlparser(data):
    """
    Convierte los carateres HTML (&#038;, ...) a su equivalente utf-8
    """

    if PY3:
        from html.parser import unescape as unescape_parse
    else:
        from HTMLParser import HTMLParser
        unescape_parse = HTMLParser().unescape
        
    data = unescape_parse(data)
    
    return data


def episode_title(title, infoLabels):

    if title and infoLabels:
        title = re.sub(PATTERN_EPISODE_TITLE, '', title)
        title = re.sub('\[COLOR\s*\w+\][^\[]+\[\/COLOR\].?\s*', '', title)
        title = re.sub(infoLabels.get('tvshowtitle', ''), '', title)
        title = re.sub('%sx0*%s(?:\s*-*\s*)?' % (infoLabels['season'], infoLabels['episode']), '', title)
        title = title.strip()
    
        if title:
            infoLabels = infoLabels.copy()
            infoLabels['title_from_channel'] = title
    
    return infoLabels