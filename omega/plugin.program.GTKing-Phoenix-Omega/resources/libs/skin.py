################################################################################
#      Copyright (C) 2019 drinfernoo                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc

import re
import threading

try:
    import json as simplejson
except ImportError:
    import simplejson

from resources.libs.common.config import CONFIG

DEFAULT_SKINS = ['skin.estuary', 'skin.estouchy']


def _get_old(old_key):
    try:
        old = '"{0}"'.format(old_key)
        xbmc.log('old= ' + str(old), xbmc.LOGINFO)
        query = '{{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{{"setting":{0}}}, "id":1}}'.format(old)
        response = xbmc.executeJSONRPC(query)
        response = simplejson.loads(response)
        xbmc.log('response_old= ' + str(response), xbmc.LOGINFO)
        if 'result' in response:
            if 'value' in response['result']:
                return response['result']['value']
    except:
        pass
        # need to be logging error here
        
    return None
    
    
def _set_new(new_key, value):
    try:
        new = '"{0}"'.format(new_key)
        value = '"{0}"'.format(value)
        query = '{{"jsonrpc":"2.0","method":"Settings.SetSettingValue","params":{{"setting":{0},"value":{1}}}, "id":1}}'.format(new, value)
        response = xbmc.executeJSONRPC(query)
        
    except Exception as e:
        pass
        # need to be logging error here
        
    return None


def _swap_skins(skin):
    _set_new('lookandfeel.skin', skin)
    xbmc.log('skin= ' + str(skin), xbmc.LOGINFO)
    
    return _dialog_watch()


def switch_to_skin(goto, title="Error"):
    from resources.libs.common import logging
    xbmc.log('goto= ' + str(goto), xbmc.LOGINFO)
    result = _swap_skins(goto)
    

    if result:
        logging.log('[COLOR {0}]{1}: Éxito en el cambio de Skin![/COLOR]'.format(CONFIG.COLOR2, title))
    #else:
        #logging.log_notify(CONFIG.ADDONTITLE,'[COLOR {0}]{1}: Skin Swap Failed![/COLOR]'.format(CONFIG.COLOR2, title))
                           
    return result


def skin_to_default(title):
    if _get_old('lookandfeel.skin') not in DEFAULT_SKINS:
        skin = 'skin.estuary'
        return switch_to_skin(skin, title)
    else:
        from resources.libs.common import logging
        logging.log('[COLOR {0}]{1}: Omitir el cambio de Skin [/COLOR]'.format(CONFIG.COLOR2, title))
        return False


def look_and_feel_data(do='save'):
    from resources.libs.common import logging

    scan = ['lookandfeel.skin','lookandfeel.enablerssfeeds', 'lookandfeel.font', 'lookandfeel.rssedit', 'lookandfeel.skincolors',
            'lookandfeel.skintheme', 'lookandfeel.skinzoom', 'lookandfeel.soundskin', 'lookandfeel.startupwindow',
            'lookandfeel.stereostrength']
            
    if do == 'save':
        for item in scan:
            query = '{{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{{"setting":"{0}"}}, "id":1}}'.format(item)
            response = xbmc.executeJSONRPC(query)
            xbmc.log('response= ' + str(response), xbmc.LOGINFO)
            if 'error' not in response:
                match = re.compile('{"value":(.+?)}').findall(str(response))
                xbmc.log('match= ' + str(match), xbmc.LOGINFO)
                CONFIG.set_setting(item.replace('lookandfeel', 'default'), match[0])
                logging.log("%s saved to %s" % (item, match[0]))
    elif do == 'restore':
        for item in scan:
            value = CONFIG.get_setting(item.replace('lookandfeel', 'default'))
            xbmc.log('value= ' + str(value), xbmc.LOGINFO)
            query = '{{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{{"setting":"{0}","value":{1}}}, "id":1}}'.format(item, value)
            response = xbmc.executeJSONRPC(query)
            logging.log("{0} restaurado a {1}".format(item, value))


def swap_us():
    from resources.libs.common import logging

    new = '"addons.unknownsources"'
    query = '{{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{{"setting":{0}}}, "id":1}}'.format(new)
    response = xbmc.executeJSONRPC(query)
    logging.log("Fuentes Desconocidas Obtener Configuración: {0}".format(str(response)))
    if 'false' in response:
        value = 'true'
        threading.Thread(target=_dialog_watch).start()
        xbmc.sleep(200)
        query = '{{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{{"setting":{0},"value":{1}}}, "id":1}}'.format(new, value)
        response = xbmc.executeJSONRPC(query)
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]Fuentes Desconocidas:[/COLOR] [COLOR {1}]Activado[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2))
        logging.log("Unknown Sources Set Settings: {0}".format(str(response)))
    elif 'true' in response:
        value = 'false'
        threading.Thread(target=_dialog_watch).start()
        xbmc.sleep(200)
        query = '{{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{{"setting":{0},"value":{1}}}, "id":1}}'.format(new, value)
        response = xbmc.executeJSONRPC(query)
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]Fuentes Desconocidas:[/COLOR] [COLOR {1}]Desactivado[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2))
        logging.log("Unknown Sources Set Settings: {0}".format(str(response)))


def _dialog_watch():
    x = 0
    while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 100:
        x += 1
        xbmc.sleep(1)

    if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
        xbmc.executebuiltin('SendClick(yesnodialog, 11)')
        return True
    else:
        return False
