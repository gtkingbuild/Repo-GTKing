# -*- coding: utf-8 -*-
try:
    from lib.ClientScraper import cfscraper
except ImportError:
    from ClientScraper import cfscraper
import xml.dom.minidom
import base64
try:
    from lib.helper import *
except:
    from helper import *
import re

def getSoup(url):
    try:
        url = cfscraper.get(url).json()['url']
    except:
        pass
    xml_ = ''    
    try:
        xml_ = cfscraper.get(url).text
    except:
        pass
    if xml_:
        if not '<?xml' in xml_:
            xml_ = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml_
        if not '&amp;' in xml_:
            xml_ = xml_.replace('&', '&#38;')
        try:
            return xml.dom.minidom.parseString(xml_)
        except Exception as e:
            print(e)
    return ''


def get_value(key,xml):
    try:
        return xml.getElementsByTagName(key)[0].firstChild.nodeValue
    except:
        return ''

def getData(url):
    xml_ = getSoup(url)
    if xml_:
        try:
            channel = xml_.getElementsByTagName('channel')
        except:
            channel = []
        try:
            items = xml_.getElementsByTagName('item')
        except:
            items = []            
        
        if channel:
            for chan in channel:
                name = get_value('name',chan)
                thumbnail = get_value('thumbnail',chan)
                fanart = get_value('fanart',chan)
                info = get_value('info',chan)
                externallink = get_value('externallink',chan)
                if name:
                    if not externallink:
                        try:
                            addMenuItem({'name': name, 'description': info, 'iconimage': thumbnail, 'fanart': fanart}, destiny='')
                        except:
                            pass
                    else:
                        try:
                            addMenuItem({'name': name, 'description': info, 'iconimage': thumbnail, 'fanart': fanart, 'url': externallink}, destiny='/get_data')
                        except:
                            pass
        elif items and not channel:
            for item in items:
                name = get_value('title',item)
                link = get_value('link',item)
                thumbnail = get_value('thumbnail',item)
                fanart = get_value('fanart',item)
                info = get_value('info',item)
                if name:
                    if not link:
                        try:
                            addMenuItem({'name': name, 'description': info, 'iconimage': thumbnail, 'fanart': fanart, 'playable': 'true'}, destiny='', folder=False)
                        except:
                            pass
                    else:                          
                        try:
                            addMenuItem({'name': name, 'url': link, 'description': info, 'iconimage': thumbnail, 'fanart': fanart, 'playable': 'true'}, destiny='/resolve_play', folder=False)
                        except:
                            pass                    



