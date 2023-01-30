# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# alfa_assistant tools - Requiere al menos Assistant v. 1.0.498 (del 09/10/2020)
# ------------------------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

import base64
import json
import re
import xbmc
import subprocess
import time
import os
import traceback

from core import httptools
from core import filetools
from core import scrapertools
from core import jsontools
from platformcode import logger
from platformcode import config
from platformcode import platformtools


EXTRA_TIMEOUT = 10

PLATFORM = config.get_system_platform()
VERBOSE = config.get_setting('addon_update_message', default=False)

ASSISTANT_APP = 'com.alfa.alfamobileassistant'
ASSISTANT_DESKTOP = 'alfa-desktop-assistant'
ASSISTANT_SERVER = "http://127.0.0.1"
ASSISTANT_SERVER_PORT = 48884
ASSISTANT_SERVER_PORT_PING = 48886
ASSISTANT_MODE = config.get_setting("assistant_mode")

assistant_urls = ['https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/assistant/', \
                  'https://gitlab.com/addon-alfa/alfa-repo/-/raw/master/downloads/assistant/']
assistant_desktop_urls = {
                          'windows': [
                                      'https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/assistant/',
                                      'https://gitlab.com/addon-alfa/alfa-repo/-/raw/master/downloads/assistant/'
                                     ],
                          'linux':   [
                                      'https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/assistant/',
                                      'https://gitlab.com/addon-alfa/alfa-repo/-/raw/master/downloads/assistant/'
                                     ],
                          'osx':     [
                                      'https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/assistant/',
                                      'https://gitlab.com/addon-alfa/alfa-repo/-/raw/master/downloads/assistant/'
                                     ]
                         }
if PLATFORM not in ['android', 'atv2'] and ASSISTANT_MODE == "este":
    if assistant_desktop_urls.get(PLATFORM, []):
        assistant_urls = assistant_desktop_urls[PLATFORM]
    else:
        assistant_urls = []

isAlfaAssistantOpen = False
debugGlobal = False

if ASSISTANT_MODE == "otro":
    if config.get_setting("assistant_custom_address"):
        ASSISTANT_SERVER = "http://%s" % config.get_setting("assistant_custom_address")
URL_CALL = '%s:%s' % (ASSISTANT_SERVER, ASSISTANT_SERVER_PORT)
URL_PING = '%s:%s' % (ASSISTANT_SERVER, ASSISTANT_SERVER_PORT_PING)

JS_CODE_CLICK_ON_VJS_BIG_PLAY_BUTTON = """
((() => { 
    try {
        document.documentElement.getElementsByClassName('vjs-big-play-button')[0].click();
    } catch (e) {
        console.error('##Error getting vjs-big-play-button', e);
    };
}))();
"""

JS_CODE_CLICK_ON_JWPLAYER = """
((() => {
    try {
        document.documentElement.getElementsByClassName('jwplayer')[0].click();
    } catch (e) {
        console.error('##Error getting jwplayer', e);
    };
}))();
"""

## Comunica con el navegador Alfa Assistant ##################################################################################################################################
#
# Recupera el código fuente de los recursos visitados y las URLS
#
def get_source_by_page_finished(url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, 
                                jsDirectCode2NoReturn=None, extraPostDelay=0, userAgent=None, 
                                debug=None, headers=None, malwareWhiteList=None, disableCache = None, 
                                closeAfter = None, getData = None, postData = None, getCookies = None, 
                                update = None, alfa_s=False, version=None, clearWebCache = False, 
                                removeAllCookies = False, hardResetWebView = False, keep_alive = False, 
                                returnWhenCookieNameFound = None, retryIfTimeout = False, mute = True, 
                                urlParamRemoveAllCookies=False, useAdvancedWebView=False):
    return get_generic_call('getSourceByPageFinished', url, timeout, jsCode, jsDirectCodeNoReturn, 
                             jsDirectCode2NoReturn, extraPostDelay, userAgent, debug, headers, 
                             malwareWhiteList, disableCache, closeAfter, getData, postData, getCookies, 
                             update, alfa_s, version, clearWebCache, removeAllCookies, hardResetWebView, 
                             keep_alive, returnWhenCookieNameFound, retryIfTimeout, mute, urlParamRemoveAllCookies, 
                             useAdvancedWebView)
##############################################################################################################################################################################

## Comunica con el navegador Alfa Assistant ##################################################################################################################################
#
# Recupera las URLS de los recursos visitados
#
def get_urls_by_page_finished(url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, 
                              jsDirectCode2NoReturn=None, extraPostDelay=0, userAgent=None, 
                              debug=None, headers=None, malwareWhiteList=None, disableCache = None, 
                              closeAfter = None, getData = None, postData = None, getCookies = None, 
                              update = None, alfa_s=False, version=None, clearWebCache = False, 
                              removeAllCookies = False, hardResetWebView = False, keep_alive = False, 
                              returnWhenCookieNameFound = None, retryIfTimeout = False, mute = True, 
                              urlParamRemoveAllCookies=False, useAdvancedWebView=False):
    return get_generic_call('getUrlsByPageFinished', url, timeout, jsCode, jsDirectCodeNoReturn, 
                             jsDirectCode2NoReturn, extraPostDelay, userAgent, debug, headers, 
                             malwareWhiteList, disableCache, closeAfter, getData, postData, 
                             getCookies, update, alfa_s, version, clearWebCache, removeAllCookies, 
                             hardResetWebView, keep_alive, returnWhenCookieNameFound, retryIfTimeout, 
                             mute, urlParamRemoveAllCookies, useAdvancedWebView)
##############################################################################################################################################################################

## Comunica con el navegador Alfa Assistant ##################################################################################################################################
#
# [Uso de parámetros]
#
# - Dirección Web donde Assistant va a navegar (GET) usando "url". Para usar POST ver "postData". El audio de la Web se silenciará para no molestar al usuario.
#   Ejemplo:
#       url = "https://www.myhost.com"
#
# - Configurar tiempo extra de espera tras la carga de la Web (para permitir que JS realice tareas).
#   Ejemplo (segundos):
#       timeout = 1
#
# - Envío de datos JSON a través de POST usando "postData". Esto se realiza cargando la Web en un iFrame (es útil porque hay Webs que lo requieren).
#   Ejemplo:
#       postData = '{"jsonKey1":"jsonValue1", "jsonKey2":"jsonValue2"}'
#
# - Envío de datos de formulario a través de POST usando "postData". Esto se realiza cargando la Web en un iFrame (es útil porque hay Webs que lo requieren).
#   Ejemplo:
#       postData = 'formKey1=formValue1&formkey2=formValue2'
#
# - Envío de datos de formulario a través de GET usando "getData": mismos ejemplos de uso que "postData". Esto se realiza cargando la Web en un iFrame (es útil porque hay Webs que lo requieren).
#
# - Configurar "UserAgent" para TODA la navegación en Assistant.
#   Ejemplo:
#       userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
#
# - Añadir "headers" a la URL inicial. El User Agent no se debería indicar aquí pues solo valdría para la URL inicial y no el resto (usar mejor parámetro "useAgent").
#   Ejemplo 1:
#       headers = '''[
#       {"name": "referer", "value": "https://www.myWebsite.com/"},
#       {"name": "otherKey", "value": "otherValue"}
#       ]'''
#
#   Ejemplo 2:
#       headers = '''[
#       {"name": "referer", "value": "{0}"},
#       {"name": "otherKey", "value": "{1}"}
#       ]'''
#       print(headers.format("value0", "value1"))
#
# - Ejecución de Javascript (CON retorno opcional) usando "jsCode".
#   Ejemplo:
#       jsCode = """
#           ((() => {
#               try {
#                   document.documentElement.getElementsByClassName('myClass')[0].click();
#                   return 'OK';    //LÍNEA OPCIONAL!!
#               } catch (e) {
#                   console.error('##Error getting jwplayer', e);
#                   return 'KO';    //LÍNEA OPCIONAL!!
#               };
#           }))();
#       """
#
# - Ejecución de Javascript SIN retorno usando "jsDirectCodeNoReturn": mismo uso y ejemplos que jsCode pero sin "return".
#
# - Ejecución de Javascript SIN retorno usando jsDirectCode2NoReturn: mismo uso y ejemplos que jsCode pero sin "return".
#
# - Espera tras ejecución de JS (o sea tras "jsCode", "jsDirectCodeNoReturn" o "jsDirectCode2NoReturn") usando "extraPostDelay".
#   Ejemplo (segundos):
#       extraPostDelay = 1
#
# - Recibir cookies (por defecto False).
#   Ejemplo:
#       getCookies = True
#   Posible respuesta:
#       ...
#       "cookies":
#           {
#               "cookiesList": "cookie1; cookie2=valor2; cookie3="
#               "urls": [
#                   "http://www.myweb1.com",
#                   "http://www.myweb2.com"    
#               ]
#           
#           }
#       ...
#
# - Por defecto y para acelerar las consultas repetitivas, Assistant usa caché de respuestas (con caducidad de 24 horas).
#   Ejemplo de desactivación:
#       disableCache = True
#
# - Cierre automático de Assistant tras su uso (sino queda abierto -aunque no en primer plano sino de fondo-).
#   Ejemplo de cierre tras uso de Assistant:
#       closeAfter = True
#
# - Assistant filtra los recursos que se intentan usar en la navegación a partir de varios repositorios online anti-malware, anti-mining, etc. Se pueden añadir exclusiones a esta lista a través del parámetro "malwareWhiteList" (usando Regex de tipo Java).
#   Ejemplo:
#       malwareWhiteList = '''[
#       ".*google.*com",
#       ".*yahoo.*com",
#       ]'''
#
#
#
# - NUNCA USAR EN PRODUCCIÓN: PARA AYUDAR A LOS DESARROLLADORES se puede mostrar lo que el navegador Assistant está haciendo. Cuidado: ni limpia recursos ni se cierra, además se puede incluso oir el audio de la Web visitada.
#   Ejemplo de activación de depuración:
#       debug = true
#
def get_generic_call(endpoint, url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, 
                     jsDirectCode2NoReturn=None, extraPostDelay=0, userAgent=None, debug=None, 
                     headers=None, malwareWhiteList=None, disableCache = None, closeAfter = None, 
                     getData = None, postData = None, getCookies = None, update = None, alfa_s = False, 
                     version = None, clearWebCache = False, removeAllCookies = False, hardResetWebView = False, 
                     keep_alive = False, returnWhenCookieNameFound = None, retryIfTimeout = False, mute = True, 
                     urlParamRemoveAllCookies = False, useAdvancedWebView = False):
    EXTRA_TIMEOUT_PLUS = 0
    debug = debug or debugGlobal
    if debug: alfa_s = False

    if endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit', 'terminate']:
        res = open_alfa_assistant(closeAfter, alfa_s=alfa_s)
        if not alfa_s: logger.info('##Assistant Endpoint: %s, Status: %s' % (endpoint, str(res)))
        if not res:
            return False
    if url:
        if not alfa_s: logger.info('##Assistant URL: %s' % url)
    else:
        url = 'about:blank'
    if timeout and endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit', 'terminate']:
        if not alfa_s: logger.info('##Assistant delay-after-html-load: %s' % str(int(timeout*1000)))
    elif not timeout:
        timeout = 0
    if endpoint in ['ping', 'getWebViewInfo', 'quit', 'terminate']:
        serverCall = URL_PING
    else:
        serverCall = URL_CALL
    if endpoint == 'getWebViewInfo':
        serverCall = '%s/%s' % (serverCall, 'ping')
    else:
        serverCall = '%s/%s' % (serverCall, endpoint)
    if endpoint == 'update':
        serverCall += '?version=%s' % version
    if endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit', 'terminate']:
        serverCall += '?url=%s&time=%s' % (base64.b64encode(url.encode('utf8')).decode('utf8'), str(int(timeout*1000)))
    
    if jsCode:
        serverCall += '&jsCode=%s' % base64.b64encode(jsCode.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant js-to-run-directly-with-return: %s' % jsCode)
    if jsDirectCodeNoReturn:
        serverCall += '&jsDirectCodeNoReturn=%s' % base64.b64encode(jsDirectCodeNoReturn.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant js-to-run-directly-with-no-return(type I): %s' % jsDirectCodeNoReturn)
    if jsDirectCode2NoReturn:
        serverCall += '&jsDirectCode2NoReturn=%s' % base64.b64encode(jsDirectCode2NoReturn.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant js-to-run-directly-with-no-return(type II): %s' % jsDirectCode2NoReturn)
    if userAgent:
        serverCall += '&userAgent=%s' % base64.b64encode(userAgent.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant user-agent: %s' % userAgent)
    ## Por defecto "debug" es False y debe serlo siempre en Producción
    if debug:
        serverCall += '&debug=%s' % debug
        if not alfa_s: logger.info('##Assistant debug-mode: %s' % str(debug))
    ## Por defecto "getCookies" es False
    if getCookies:
        serverCall += '&getCookies=%s' % getCookies
        if not alfa_s: logger.info('##Assistant get-cookies: %s' % str(getCookies)      )  
    ## Por defecto "cache" es True pero en casos como mixdrop es mejor no usarla
    if disableCache:
        serverCall += '&cache=False'
        if not alfa_s: logger.info('##Assistant disableCache: %s' % str(disableCache))
    if malwareWhiteList:
        serverCall += '&malwareWhiteList=%s' % base64.b64encode(malwareWhiteList.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant malware-white-list: %s' % malwareWhiteList)
    if getData:
        serverCall += '&getData=%s' % base64.b64encode(getData.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant get-data: %s' % getData)
    if postData:
        serverCall += '&postData=%s' % base64.b64encode(postData.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant post-data: %s' % postData)
    if returnWhenCookieNameFound:
        serverCall += '&returnWhenCookieNameFound=%s' % base64.b64encode(returnWhenCookieNameFound.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant returnWhenCookieNameFound: %s' % str(returnWhenCookieNameFound))
    if clearWebCache:
        serverCall += '&clearWebCache=%s' % clearWebCache
        if not alfa_s: logger.info('##Assistant clearWebCache: %s' % str(clearWebCache))
    if headers:
        if isinstance(headers, dict):
            headers_out = []
            for key, value in list(headers.items()):
                headers_out += [{"name": key.lower(), "value": value}]
            headers = str(headers_out).replace("'", '"')
        serverCall += '&headers=%s' % base64.b64encode(headers.encode('utf8')).decode('utf8')
        if not alfa_s: logger.info('##Assistant headers: %s' % headers)

    timeout = int(timeout) + extraPostDelay
    serverCall += '&extraPostDelay=%s' % (extraPostDelay*1000)
    if not alfa_s: logger.info('##Assistant delay-after-js-load: %s' % str(extraPostDelay*1000))
    serverCall += '&removeAllCookies=%s' % removeAllCookies
    if not alfa_s: logger.info('##Assistant removeAllCookies: %s' % str(removeAllCookies))
    serverCall += '&hardResetWebView=%s' % hardResetWebView
    if not alfa_s: logger.info('##Assistant hardResetWebView: %s' % str(hardResetWebView))
    serverCall += '&mute=%s' % mute
    if not alfa_s: logger.info('##Assistant mute: %s' % str(mute))
    serverCall += '&urlParamRemoveAllCookies=%s' % urlParamRemoveAllCookies
    if not alfa_s: logger.info('##Assistant urlParamRemoveAllCookies: %s' % str(urlParamRemoveAllCookies))
    serverCall += '&useAdvancedWebView=%s' % useAdvancedWebView
    if not alfa_s: logger.info('##Assistant useAdvancedWebView: %s' % str(useAdvancedWebView))

    if endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit', 'terminate']:
        EXTRA_TIMEOUT_PLUS = 10 if timeout+EXTRA_TIMEOUT <= 10 else 0
        if not alfa_s: logger.info('##Assistant URL: %s - TIMEOUT: %s' % (serverCall, str(timeout+EXTRA_TIMEOUT)))
    response = httptools.downloadpage(serverCall, timeout=timeout+EXTRA_TIMEOUT+EXTRA_TIMEOUT_PLUS, alfa_s=alfa_s, 
                                      ignore_response_code=True, keep_alive=keep_alive, retry_alt=False, proxy_retries=0)
    if not response.sucess and endpoint in ['ping', 'getWebViewInfo']:
        if not alfa_s: logger.info('##Assistant "%s" FALSE, timeout %s: %s' % (endpoint, timeout+EXTRA_TIMEOUT, serverCall), force=True)
    if not (response.sucess or response.data) and endpoint not in ['ping', 'getWebViewInfo', 'quit', 'terminate']:
        if retryIfTimeout: retryIfTimeout = response
        res = close_alfa_assistant(retryIfTimeout=retryIfTimeout)
        time.sleep(2)
        if not res:
            res = get_generic_call('ping', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
        if res:
            serverCall = serverCall.replace('&cache=True', '&cache=False').replace('&clearWebCache=True', '&clearWebCache=False')
            if not alfa_s: logger.info('##Assistant retrying URL: ' + serverCall)
            response = httptools.downloadpage(serverCall, timeout=timeout+EXTRA_TIMEOUT+EXTRA_TIMEOUT_PLUS, alfa_s=alfa_s, 
                                              ignore_response_code=True, keep_alive=keep_alive, retry_alt=False, proxy_retries=0)
        else:
            platformtools.dialog_notification("ACTIVE Alfa Assistant en ", "%s" % ASSISTANT_SERVER)
    data = response.data
    
    #if closeAfter:
    #    close_alfa_assistant()

    if data:
        if endpoint in ['update']:
            return data
        try:
            data_ret = jsontools.load(data)
            if data_ret.get('assistantVersion', '') and '?' in data_ret['assistantVersion']: 
                data_ret['assistantVersion'] = '0.0.01'
            if data_ret.get('assistantLatestVersion', '') and '?' in data_ret['assistantLatestVersion']: 
                data_ret['assistantLatestVersion'] = '0.0.01'
            if data_ret.get('wvbVersion', '') and '?' in data_ret['wvbVersion']: 
                data_ret['wvbVersion'] = '0.0.0'
            if endpoint in ['ping', 'getWebViewInfo']:
                if endpoint in ['ping']:
                    data_ret = data_ret.get('assistantVersion', '')
                else:
                    if isinstance(isAlfaAssistantOpen, dict) and isAlfaAssistantOpen.get('assistantLatestVersion'):
                        data_ret['assistantLatestVersion'] = isAlfaAssistantOpen['assistantLatestVersion']
                if not alfa_s: logger.info('##Assistant "%s" TRUE, timeout %s: %s' % (endpoint, timeout+EXTRA_TIMEOUT, str(data_ret)))
        except:
            data_ret = data
            logger.error('##Assistant "%s" ERROR, timeout %s: %s' % (endpoint, timeout+EXTRA_TIMEOUT, str(data_ret)))
        return data_ret
    else:
        data = ''
        return data
##############################################################################################################################################################################

#
# Lista el código fuente (decodificado) según filtro regex (parámetro "pattern") entre los datos que devuelve el navegador Alfa Assistant (parámetro "data")
#
def find_htmlsource_by_url_pattern(data, pattern):
    if not data:
        logger.info('##Assistant NOT received data from Alfa Assistant')
    else:
        logger.info('##Assistant Received data from Alfa Assistant')
        if data['htmlSources'] and len(data['htmlSources']) >= 1:
            for attrs in data['htmlSources']:
                if re.search(pattern, attrs['url']):
                    logger.info('##Assistant URL found by find_htmlsource_by_url_pattern: ' + attrs['url'])
                    return {
                        'url': attrs['url'],
                        'source': base64.b64decode(attrs['source']).decode('utf8')
                    }
                else:
                    logger.info('##Assistant The data found in Alfa Assistant has not the right info')
    return

#
# Prepara en una línea los argumentos necesarios para constituir una URL a partir de una lista que proviene de consultar Alfa Assistant
# Ejemplo:
#   from lib import alfa_assistant
#   data_assistant = alfa_assistant.get_urls_by_page_finished(global_url, 1, jsDirectCode2NoReturn=js_code, extraPostDelay=2, userAgent=ua, disableCache=True, closeAfter=True)
#   for visited in data_assistant["urlsVisited"]:
#       url = visited["url"] + alfa_assistant.getInlineRequestedHeaders(visited["requestHeaders"], [])
#
def getInlineRequestedHeaders(requestHeaders, namesExceptionList = None):
    res = ""
    try:
        count = 0
        if requestHeaders:
            for requestHeader in requestHeaders:
                name = requestHeader["name"]
                if not namesExceptionList or name not in namesExceptionList:
                    value = requestHeader["value"]
                    if count == 0:
                        res += "|%s=%s" % (name, value)
                    else:
                        res += "&%s=%s" % (name, value)
                    count += 1

    except:
        logger.error('##Assistant getInlineRequestedHeaders Error')
        logger.error(traceback.format_exc(1))

    return res    #Ejemplo: |param1=value1&param2=value2


##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
## F U N C I O N E S   D E   B A J O   N I V E L #############################################################################################################################
################# NO TOCAR ###################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def open_alfa_assistant(closeAfter=None, getWebViewInfo=False, retry=False, assistantLatestVersion=True, alfa_s=False):
    global isAlfaAssistantOpen
    version = 'alfa-mobile-assistant.version'
    if PLATFORM not in ['android', 'atv2']:
        version = ''
    res = False
    
    if not isAlfaAssistantOpen:
        try:
            if ASSISTANT_MODE == 'este':

                if not is_alfa_installed():
                    logger.error('##Assistant not installed or not available')
                    return False

                logger.info('##Assistant Opening at %s' % ASSISTANT_SERVER, force=True)
                
                ver_upd = get_generic_call('ping', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
                if closeAfter:
                    cmd = 'openAndQuit'
                else:
                    cmd = 'open'
                
                if not ver_upd and (config.get_platform(True)['num_version'] >= 19 or \
                                (config.get_platform(True)['num_version'] < 19 \
                                and not xbmc.Player().isPlaying())):
                    res = execute_in_alfa_assistant_with_cmd(cmd)

                for x in range(14):
                    time.sleep(1)
                    res = get_generic_call('getWebViewInfo', timeout=1-EXTRA_TIMEOUT, alfa_s=True)
                    if res:
                        if isinstance(res, dict):
                            check_webview_version(res.get('wvbVersion', ''))
                            if not getWebViewInfo:
                                res = res.get('assistantVersion', '')
                            isAlfaAssistantOpen = res
                        else:
                            isAlfaAssistantOpen = res
                        logger.info('##Assistant Opened @ %s. getWebViewInfo: %s' % (ASSISTANT_SERVER, res), force=True)
                        break
                else:
                    return False

            else:
                res = get_generic_call('getWebViewInfo', timeout=3-EXTRA_TIMEOUT, alfa_s=True)
                if res:
                    if isinstance(res, dict):
                        check_webview_version(res.get('wvbVersion', ''))
                        if not getWebViewInfo:
                            res = res.get('assistantVersion', '')
                        isAlfaAssistantOpen = res
                    else:
                        isAlfaAssistantOpen = res
                    logger.info('##Assistant Opened @ %s. getWebViewInfo: %s' % (ASSISTANT_SERVER, res), force=True)
                else:
                    if not retry:
                        platformtools.dialog_notification("ACTIVE Alfa Assistant en %s" % ASSISTANT_SERVER, 
                                    "o Instale manualmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]")
                    return False

            if isinstance(res, dict) and getWebViewInfo and assistantLatestVersion and PLATFORM in ['android', 'atv2']:
                for url in assistant_urls:
                    response = httptools.downloadpage(url+version, timeout=2, alfa_s=True, ignore_response_code=True, 
                                                      retry_alt=False, proxy_retries=0)
                    if response.sucess:
                        data = response.data
                        if PY3 and isinstance(data, bytes):
                            data = "".join(chr(x) for x in bytes(data))
                        if '?' in data: data = '0.0.01'
                        res['assistantLatestVersion'] = data
                        isAlfaAssistantOpen = res
                        break
            
            return isAlfaAssistantOpen
        
        except:
            logger.error('##Assistant Error opening it')
            logger.error(traceback.format_exc())
        return res
    
    else:
        if not alfa_s: logger.info('##Assistant Already was Opened @ %s: %s' % (ASSISTANT_SERVER, str(isAlfaAssistantOpen)), force=True)
        return isAlfaAssistantOpen

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def close_alfa_assistant(retryIfTimeout=False):
    global isAlfaAssistantOpen
    isAlfaAssistantOpen = False
    res = False

    if is_alfa_installed():
        logger.info('##Assistant Close at ' + URL_PING, force=True)
        res = get_generic_call('quit', timeout=1-EXTRA_TIMEOUT, alfa_s=True)
        
        if retryIfTimeout:
            try:
                if not isinstance(retryIfTimeout, bool):
                    if not 'ead timed out' in retryIfTimeout.code:
                        retryIfTimeout = False
                if retryIfTimeout:
                    logger.info('##Assistant Reset at ' + URL_PING, force=True)
                    response = httptools.downloadpage(URL_PING+'/terminate', timeout=2, alfa_s=True, ignore_response_code=True, 
                                                      retry_alt=False, proxy_retries=0)
                    if ASSISTANT_MODE != 'este' or config.get_setting('assistant_binary', default='') == 'AstOK':
                        time.sleep(10)
                    time.sleep(5)
                    res = open_alfa_assistant(getWebViewInfo=True, retry=True)
            except:
                logger.error(traceback.format_exc())

    return res    

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def check_webview_version(wvbVersion):
    
    if PLATFORM not in ['android', 'atv2'] and ASSISTANT_MODE == "este":
        return

    if not wvbVersion:
        logger.info('##Assistant wvbVersion NO DETECTADA', force=True)
        return
        
    if 'NEEDED_TO_CHECK_ONLINE_LIST_BASED_ON_ANDROID_VERSION' in wvbVersion:
        logger.info('##Assistant wvbVersion ANTERIOR a Android 5', force=True)
        return

    # Comparar la versión de WebView que tiene el Android donde reside la APP con la versión mínima adecuada
    ver_min = 109
    
    wvbVersion_list = wvbVersion.split('.')
    wvbVersion_msg = config.get_setting('wvbVersion_msg', default=0)
    if isinstance(wvbVersion_msg, bool): 
        wvbVersion_msg = 85
        config.set_setting('wvbVersion_msg', ver_min)
    if len(wvbVersion_list) > 1:
        try:
            wvbVersion_major = int(wvbVersion_list[0])
        except:
            logger.error('##Assistant Error in wvbVersion: %s' % str(wvbVersion))
            return
            
        if wvbVersion_major < ver_min:
            logger.info('##Assistant wvbVersion OBSOLETA: %s' % str(wvbVersion), force=True)
            if wvbVersion_msg < ver_min:
                config.set_setting('wvbVersion_msg', ver_min)
                platformtools.dialog_notification("Alfa Assistant WebView: versión obsoleta", \
                            "%s - Actualice a una versión actual" % str(wvbVersion), time=10000)
    else:
        logger.error('##Assistant wvbVersion INCOMPATIBLE: %s' % str(wvbVersion))
        if wvbVersion_msg < ver_min:
            config.set_setting('wvbVersion_msg', ver_min)
            platformtools.dialog_notification("Alfa Assistant WebView: versión INCOMPATIBLE", \
                        "%s - Actualice a una versión actual" % str(wvbVersion), time=10000)
    
    return
#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def is_alfa_installed(remote='', verbose=VERBOSE):
    version = True
    if not isAlfaAssistantOpen:
        version, app_name = install_alfa_assistant(update=False, remote=remote, verbose=verbose)
    return version

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def update_alfa_assistant(remote='', verbose=VERBOSE):
    #return execute_in_alfa_assistant_with_cmd('update')
    return install_alfa_assistant(update=True, remote=remote, verbose=verbose)

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def check_permissions_alfa_assistant():
    return execute_in_alfa_assistant_with_cmd('checkPermissions')

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def execute_in_alfa_assistant_with_cmd(cmd, dataURI='about:blank', wait=False, debug=debugGlobal):
    global isAlfaAssistantOpen
    if PLATFORM in ['android', 'atv2']:
        try:
            app = ASSISTANT_APP
            intent = ''  # com.alfa.alfamobilehelper.MainActivity'
            dataType = cmd # 'openForDebug'
            cmd = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (app, intent, dataType, dataURI)
            logger.info('##Assistant executing CMD: %s' % cmd)
            xbmc.executebuiltin(cmd, wait)
            return True
        except:
            logger.error(traceback.format_exc(1))
            return False
    
    elif ASSISTANT_MODE == 'este':
        creationflags = 0
        sufix = ''
        arquitecture = 'amd64'
        java_version = 11
        if PLATFORM in ['windows', 'xbox']:
            creationflags = 0x08000000
            sufix = '.exe'
        assistant_path = filetools.join(config.get_data_path(), 'assistant')
        logs_path = filetools.join(assistant_path, 'temp', 'logs', ' ').strip()
        binary_path = ASSISTANT_DESKTOP+'.exe'
        command_path = filetools.join(assistant_path, 'runtime', 'so', PLATFORM, ' ').strip()
        command = {
                   'windows': [
                               '%sstart.cmd' % command_path
                              ], 
                   'windows_debug': ['>', '%sstart.log' % logs_path, '2>', '%serror.log' % logs_path], 
                   'linux':   [
                               '%sstart.cmd' % command_path
                              ], 
                   'linux_debug':   ' > %sstart.log' % logs_path + '2> %serror.log' % logs_path, 
                   'osx':     [
                               '%sstart.cmd' % command_path
                              ], 
                   'osx_debug':     ' > %sstart.log' % logs_path + '2> %serror.log' % logs_path
                  }
        cmdexe = command.get(PLATFORM, [])
        if debug:
            res = True
            if not filetools.exists(logs_path):
                res = filetools.mkdir(logs_path, silent=True)
            if res:
                if PLATFORM in ['windows', 'xbox']: 
                    cmdexe += command.get('%s_debug' % PLATFORM, [])
                else:
                    cmdexe[0] += command.get('%s_debug' % PLATFORM, '')
        
        try:
            p = subprocess.Popen(cmdexe, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                 stdin=subprocess.PIPE, creationflags=creationflags, cwd=assistant_path, shell=True)
            if wait:
                output_cmd, error_cmd = p.communicate()
                if error_cmd: p = False
            logger.info('##Assistant executing CMD: %s, wait=%s' % (cmdexe, wait))
            return p
        except Exception as e:
            if not PY3:
                e = unicode(str(e), "utf8", errors="replace").encode("utf8")
            elif PY3 and isinstance(e, bytes):
                e = e.decode("utf8")
            logger.error('## ERROR Popen CMD: %s, wait=%s - error: %s' % (cmdexe, wait, e))
    
    return False

#
## Android >= 10 ejecuta los binarios en Kodi desde Alfa Assistant, si no, de la forma tradicional ##################################################################################################################################
#
def execute_binary_from_alfa_assistant(function, cmd, wait=False, init=False, retry=False, p=None, **kwargs):
    global isAlfaAssistantOpen
    output_cmd = ''
    error_cmd = ''
    
    """
    Assistant APP acts as a CONSOLE for binaries management in Android 10+ and Kodi 19+
    
    Syntax StartAndroidActivity("USER_APP", "", "function", "cmd|arg| ... |arg|||dict{env} in format |key=value|... "):
          
          - cmd: binary name in format '$PWD/lib'binary_name'.so'
          - 'open':                                                     START the Assitant
          - 'terminate':                                                CLOSES Assistant
          - "OpenBinary", "$PWD/libBINARY.so|-port|61235|-settings|/storage/emulated/.../settings.json|||
                            (kwargs[env]): |key=value|etc=etc":         CALL binary
    
    Syntax Http requests: http://127.0.0.1:48884/command?option=value
          
          - /openBinary?cmd=base64OfFullCommand($PWD/libBINARY.so|-port|61235| 
                            -settings|/storage/emulated/.../settings.json|||
                            (kwargs[env]): |key=value|etc=etc):         CALL binary
                  - returns: {
                              "pid": 999,
                              "output": "Base64encoded",
                              "error": "Base64encoded",
                              "startDate": "Base64encoded(2021-12-13 14:00:12)",
                              "endDate": "Base64encoded([2021-12-13 14:00:12])",    If ended
                              "retCode": "0|1|number|None"                          None if not ended
                              "cmd": "Base64encoded(command *args **kwargs)"        Full command as sent to the app
                              "finalCmd": "Base64encoded($PWD/command *args)"       Actual command executed vy the app
                              
          - /openBinary?cmd=base64OfFullCommand([[ANY Android/Linux command: killall libtorrest.so (kills all Torrest binaries)]])
                  - returns: {As in /openBinary?cmd}
          
          - /getBinaryStatus?pid=999:                                   Request binary STATUS by PID
                  - returns: {As in /openBinary?cmd}
          
          - /killBinary?pid=999:                                        Request KILL binary PID
                  - returns: {As in /openBinary?cmd}

          - /getBinaryList:                                             Return a /getBinaryStatus per binary launched during app session
                  - returns: {As in /openBinary?cmd}
          - terminate:                                                  CLOSES Assistant
    """
        
    if not p:
        logger.info('## Popen CMD: %s, wait=%s' % (cmd, wait), force=True)
        if config.get_setting('assistant_binary'): config.set_setting('assistant_binary', False)
        creationflags = 0
        if PLATFORM in ['windows', 'xbox']: creationflags = 0x08000000
        try:
            p = subprocess.Popen(cmd, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                stdin=subprocess.PIPE, creationflags=creationflags)
            return p
        except Exception as e:
            if not PY3:
                e = unicode(str(e), "utf8", errors="replace").encode("utf8")
            elif PY3 and isinstance(e, bytes):
                e = e.decode("utf8")
            logger.error('## ERROR Popen CMD: %s, wait=%s - error: %s' % (cmd, wait, e))

            if PLATFORM in ['android', 'atv2'] and ('Errno 13' in str(e) or 'Errno 2' in str(e)):
                p = None
            else:
                return p
        
    # The traditional way did not work, so most probably we hit the SDK 29 problem
    # Simulate the response from subprocess.Popen
    if init:
        class ProcInit:
            returncode = 0
        p = ProcInit()
        
        # Check if other add-ons may need the Assistant app
        import xbmcaddon
        app_needed = ''
        for addon_binary in ['torrest', 'quasar']:
            if xbmc.getCondVisibility('System.HasAddon("plugin.video.%s")' % addon_binary):
                try:
                    __settings__ = xbmcaddon.Addon(id="plugin.video.%s" % addon_binary)
                    app_needed += addon_binary.capitalize() + ', '
                except:
                    pass
        if not config.get_setting('assistant_binary'): config.set_setting('assistant_binary', True)

        if filetools.exists(filetools.join(config.get_data_path(), 'alfa-mobile-assistant.version')):
            try:
                version = filetools.read(filetools.join(config.get_data_path(), 'alfa-mobile-assistant.version')).split('.')
                if int(version[0]) > 1 or (int(version[0]) == 1 and int(version[1]) >= 3):
                    if not app_needed:
                        config.set_setting('assistant_binary', 'Ast%s' % version[1])
                    else:
                        config.set_setting('assistant_binary', 'AstOK')
                elif app_needed:
                    config.set_setting('assistant_binary', 'AstNO')
            except:
                pass
        
        if not app_needed:
            return p
        
        if not is_alfa_installed() or config.get_setting("assistant_mode") != 'este':
            if not filetools.exists(filetools.join(config.get_data_path(), 'alfa-mobile-assistant.version')):
                platformtools.dialog_notification("Estos addons necesitan Alfa Assistant: %s " % app_needed.rstrip(', '), 
                                "Instale localmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]", time=10000)
            
            if config.get_setting('assistant_flag_install', default=True):
                time.sleep(10)
                respuesta, app_name = install_alfa_assistant(update='check')
        return p
    
    if not init and not isinstance(p, int) and config.get_setting("assistant_mode") != 'este':
        platformtools.dialog_notification("Este módulo necesita Alfa Assistant: %s" % cmd[0], 
                        "Instale localmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]", time=10000)
        if config.get_setting('assistant_flag_install', default=True):
            time.sleep(10)
            respuesta, app_name = install_alfa_assistant(update='auto')
        if not respuesta or config.get_setting("assistant_mode") != 'este':
            platformtools.dialog_notification("Estos módulo no se van a ejecutar: %s " % cmd[0], 
                        "Instale localmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]", time=10000)
            time.sleep(10)
            p.returncode = 9
        return p

    if (not init and isinstance(p, int)) or (not init and is_alfa_installed() and config.get_setting("assistant_mode") == 'este'):
        try:
            # Lets start the Assistant app
            USER_APP_URL = '%s:%s' % (ASSISTANT_SERVER, '48886')
            USER_APP_URL_ALT = '%s:%s' % (ASSISTANT_SERVER, '48885')
            separator = '|'
            separator_escaped = '\|'
            separator_kwargs = '|||'
            command = []
            status_code = 0
            cmd_app = ''
            
            url = ''
            url_open = '%s/%s%s' % (USER_APP_URL, function, '?cmd=')
            url_killall = url_open + base64.b64encode(str('killall lib%s.so' % cmd[0]).encode('utf8')).decode('utf8')
            cmd_android_close = 'StartAndroidActivity("%s", "", "%s", "%s")' % (ASSISTANT_APP, 'terminate', 'about:blank')
            if isinstance(p, int):
                url_killall = USER_APP_URL + '/killBinary?pid=%s' % p
            else:
                res = open_alfa_assistant()
                time.sleep(3)

            # Build the command & params
            if isinstance(cmd, list):
                command.append(cmd)
                command.append(kwargs)
                # Convert Args to APP format
                cmd_bis = cmd[:]
                cmd_bis[0] = '$PWD/lib%s.so' % filetools.basename(cmd_bis[0])
                for args in cmd_bis:
                    cmd_app += args.replace(separator, separator_escaped) + separator
                cmd_app = cmd_app.rstrip(separator)
                # Convert Kwargs to APP format
                if kwargs.get('env', {}):
                    cmd_app += separator_kwargs
                for key, value in list(kwargs.get('env', {}).items()):
                    if key == 'LD_LIBRARY_PATH':
                        # The app will replace $PWD by the binary/lib path
                        value = '$PWD'
                    if key == 'PATH':
                        # The app will replace $PWD by the binary/lib path
                        value = '$PWD:%s' % value
                    cmd_app += '%s=%s%s' % (key.replace(separator, separator_escaped), \
                                value.replace(separator, separator_escaped), separator)
                cmd_app = cmd_app.rstrip(separator)
                command_base64 = base64.b64encode(cmd_app.encode('utf8')).decode('utf8')
            else:
                command_base64 = cmd
                if p and not isinstance(p, int):
                    cmd = p.args_
                    kwargs = p.kwargs_
                command.append(cmd)
                command.append(kwargs)

            # Launch the Binary
            launch_status = True
            if not wait or isinstance(p, int):
                # We assume that no wait implies only one version of the binary can be active, so cancel all existing Binary sessions
                url = url_killall
                logger.info('## Killing from Assistant App: %s' % url)
                resp = httptools.downloadpage(url, timeout=5, ignore_response_code=True, alfa_s=True, retry_alt=False, proxy_retries=0)
                time.sleep(1)
                if function == 'killBinary':
                    try:
                        status_code = resp.code
                        if status_code != 200:
                            return 999
                        time.sleep(1)
                        url_stat = USER_APP_URL + '/getBinaryStatus?pid=%s&flushAfterRead=true' % p
                        resp = httptools.downloadpage(url_stat, timeout=5, ignore_response_code=True, alfa_s=True, retry_alt=False, proxy_retries=0)
                        status_code = resp.code
                        if status_code != 200:
                            return 999
                        app_response = resp.data
                        if PY3 and isinstance(app_response, bytes):
                            app_response = app_response.decode()
                        app_response = re.sub('\n|\r|\t', '', app_response)
                        app_response = json.loads(app_response)
                        test_json = app_response["pid"]
                        return int(app_response.get('retCode', 9))
                    except:
                        return 999
            
            # Now lets launch the Binary
            logger.info('## Calling binary from Assistant App: %s - Retry = %s' % (cmd, retry), force=True)
            url = url_open + command_base64
            resp = httptools.downloadpage(url, timeout=5, ignore_response_code=True, alfa_s=True, retry_alt=False, proxy_retries=0)
            status_code = resp.code
            if status_code != 200 and not retry:
                logger.error("## Calling %s: Invalid app requests response: %s" % (cmd[0], status_code))
                time.sleep(15)          # let Torrest/Quasar starts first
                isAlfaAssistantOpen = False
                return execute_binary_from_alfa_assistant(function, cmd, wait=wait, init=init, retry=True, **kwargs)
            elif status_code != 200 and retry:
                logger.error("## Calling %s: Invalid app requests response: %s.  Terminating Assistant" % (cmd[0], status_code))
                launch_status = False
                isAlfaAssistantOpen = False
                time.sleep(15)          # let Torrest/Quasar starts first
            try:
                app_response = resp.data
                if launch_status:
                    if PY3 and isinstance(app_response, bytes):
                        app_response = app_response.decode()
                    app_response = re.sub('\n|\r|\t', '', app_response)
                    app_response = json.loads(app_response)
            except:
                status_code = resp.data
                launch_status = False
                logger.error("## Calling %s: Invalid app  response: %s" % (cmd[0], status_code))

            # Simulate the response from subprocess.Popen
            pipeout, pipein = os.pipe()
            class Proc:
                pid = 999999
                stdout = os.fdopen(pipeout, 'rb')
                stdin = os.fdopen(pipein, 'wb')
                stderr = stdout
                returncode = None
                startDate = ''
                endDate = ''
                poll = ''
                terminate = ''
                communicate = ''
                app = ASSISTANT_APP
                url_app = USER_APP_URL
                url_app_alt = USER_APP_URL_ALT
                cmd_app = command_base64
                finalCmd = ''
                args_ = cmd
                kwargs_ = kwargs
                sess = ''
                monitor = xbmc.Monitor()
            
            p = Proc()
            
            def redirect_terminate(p=p, action='killBinary'):
                return binary_stat(p, action)
            def redirect_poll(p=p, action='poll'):
                return binary_stat(p, action)
            def redirect_communicate(p=p, action='communicate'):
                return binary_stat(p, action)
            p.poll = redirect_poll
            p.terminate = redirect_terminate
            p.communicate = redirect_communicate
            
            # If something went wrong on the binary launch, lets return the error so it is recovered from the standard code
            if not launch_status:
                p.returncode = 999
                raise ValueError("No app response:  error code: %s" % status_code)
            
            try:
                p.pid = int(app_response['pid'])
            except:
                raise ValueError("No valid PID returned:  PID code: %s" % resp.content)

            logger.info('## Assistant executing CMD: %s - PID: %s - Wait: %s' % (command[0], p.pid, wait), force=True)
            logger.debug('## Assistant executing CMD **kwargs: %s' % command[1])
        except:
            if function == 'killBinary':
                logger.error('## Assistant ERROR %s in CMD: %s%s - Wait: %s' % (status_code, url_killall, p, wait))
            else:
                logger.error('## Assistant ERROR %s in CMD: %s%s - Wait: %s' % (status_code, url, command, wait))
            logger.error(traceback.format_exc())
    
    return p

def binary_stat(p, action, retry=False, init=False, app_response={}):
    global isAlfaAssistantOpen
    if init: logger.info('## Binary_stat: action: %s; PID: %s; retry: %s; init: %s; app_r: %s' \
                        % (action, p.pid, retry, init, app_response), force=True)
    import traceback
    import base64
    import json
    import time
    import xbmc
    
    try:
        if action in ['poll', 'communicate']:
            url = p.url_app + '/getBinaryStatus?pid=%s&flushAfterRead=true' % str(p.pid)
            url_alt = p.url_app_alt + '/getBinaryStatus?pid=%s&flushAfterRead=true' % str(p.pid)

        if action == 'killBinary':
            url = p.url_app + '/killBinary?pid=%s' % str(p.pid)
            url_alt = p.url_app_alt + '/killBinary?pid=%s' % str(p.pid)

        url_close = p.url_app + '/terminate'
        cmd_android_close = 'StartAndroidActivity("%s", "", "%s", "%s")' % (p.app, 'terminate', 'about:blank')
        cmd_android_permissions = 'StartAndroidActivity("%s", "", "%s", "%s")' % (p.app, 'checkPermissions', 'about:blank')

        finished = False
        retry_req = False
        retry_app = False
        stdout_acum = ''
        stderr_acum = ''
        msg = ''
        while not finished:
            if not isinstance(app_response, dict):
                logger.error("## ERROR in app_response: %s - type: %s" % (str(app_response), str(type(app_response))))
                app_response = {}
            if not app_response:
                resp = httptools.downloadpage(url+str(p.pid), timeout=5, ignore_response_code=True, alfa_s=True, retry_alt=False, proxy_retries=0)
                if resp.code != 200 and not retry_req:
                    if action == 'killBinary' or p.monitor.abortRequested():
                        app_response = {'pid': p.pid, 'retCode': 998}
                    else:
                        logger.error("## Binary_stat: Invalid app requests response for PID: %s: %s - retry: %s" % (p.pid, resp.code, retry_req))
                        retry_req = True
                        url = url_alt
                        msg += str(resp.code)
                        stdout_acum += str(resp.code)
                        isAlfaAssistantOpen = False
                        res = open_alfa_assistant()
                        time.sleep(5)
                        continue
                if resp.code != 200 and retry_req:
                    logger.error("## Binary_stat: Invalid app requests response for PID: %s: %s - retry: %s.  Closing Assistant" % \
                                    (p.pid, resp.code, retry_req))
                    msg += str(resp.code)
                    stdout_acum += str(resp.code)
                    app_response = {'pid': p.pid, 'retCode': 998}
                    isAlfaAssistantOpen = False
                    time.sleep(15)          # let Torrest/Quasar starts first

                if resp.code == 200:
                    try:
                        app_response = resp.data
                        if init: logger.debug(app_response)
                        if PY3 and isinstance(app_response, bytes):
                            app_response = app_response.decode()
                        app_response_save = app_response
                        app_response = re.sub('\n|\r|\t', '', app_response)
                        app_response = json.loads(app_response)
                        test_json = app_response["pid"]
                    except:
                        status_code = resp.data
                        logger.error("## Binary_stat: Invalid app response for PID: %s: %s - retry: %s" % (p.pid, resp.data, retry_app))
                        if retry_app:
                            app_response = {'pid': p.pid}
                            app_response['retCode'] = 999
                            msg += app_response_save
                            stdout_acum += app_response_save
                        else:
                            retry_app = True
                            app_response = {}
                            time.sleep(1)
                            continue
                        
            if app_response.get("pid", 0):
                if app_response.get('output'):
                    stdout_acum += base64.b64decode(app_response['output']).decode('utf-8')
                    msg += base64.b64decode(app_response['output']).decode('utf-8')
                if app_response.get('error'): 
                    stderr_acum += base64.b64decode(app_response['error']).decode('utf-8')
                    msg += base64.b64decode(app_response['error']).decode('utf-8')
                if app_response.get('startDate'): 
                    p.startDate = base64.b64decode(app_response['startDate']).decode('utf-8')
                if app_response.get('endDate'): 
                    p.endDate = base64.b64decode(app_response['endDate']).decode('utf-8')
                if app_response.get('cmd'): 
                    p.cmd_app = base64.b64decode(app_response['cmd']).decode('utf-8')
                if app_response.get('finalCmd'): 
                    p.finalCmd = base64.b64decode(app_response['finalCmd']).decode('utf-8')

                # If still app permissions not allowed, give it a retry
                if 'permission denied' in msg:
                    platformtools.dialog_notification('Accept Assitant permissions', time=15000)
                    time.sleep(5)
                    check_permissions_alfa_assistant()
                    time.sleep(15)
                    isAlfaAssistantOpen = False
                    res = open_alfa_assistant()
                    time.sleep(5)
                
                if msg:
                    try:
                        for line in msg.split('\n'):
                            line += '\n'
                            if PY3 and not isinstance(line, (bytes, bytearray)):
                                line = line.encode('utf-8')
                            p.stdin.write(line)
                            p.stdin.flush()
                    except:
                        pass
            
            p.returncode = None
            if action == 'killBinary' and not app_response.get('retCode', ''):
                app_response['retCode'] = 137
            if app_response.get('retCode', '') or action == 'killBinary' or \
                            (action == 'communicate' and app_response.get('retCode', '') != ''):
                try:
                    p.stdin.flush()
                    p.stdin.close()
                except:
                    pass
                try:
                    p.returncode = int(app_response['retCode'])
                except:
                    p.returncode = app_response['retCode']
                
            if action == 'communicate' and p.returncode is not None:
                logger.info("## Binary_stat: communicate Binary: %s - Returncode: %s" % (p.pid, p.returncode), force=True)
                return stdout_acum, stderr_acum
            
            elif action == 'poll':
                if init and msg:
                    logger.error('## Binary_stat: Binary initial response: %s' % msg)
                    return True
                return p.returncode
            
            elif action == 'killBinary':
                logger.info("## Binary_stat: killBinary Binary: %s - Returncode: %s" % (p.pid, p.returncode), force=True)
                try:
                    if not p.monitor.abortRequested() and p.returncode == 998:
                        time.sleep(15)
                except:
                    logger.error(traceback.format_exc())
                    time.sleep(3)
                return p

            time.sleep(5)
            msg = ''
            app_response = {}

    except:
        logger.info(traceback.format_exc())
    return None


#
## Instala o actualiza la app de Assitant ##################################################################################################################################
#
def install_alfa_assistant(update=False, remote='', verbose=VERBOSE):
    if PLATFORM not in ['android', 'atv2'] and ASSISTANT_MODE == "este":
        return install_alfa_desktop_assistant(update=update, remote=remote, verbose=verbose)
    
    if update:
        logger.info('update=%s' % str(update))
    # Si ya está instalada, devolvemos el control
    app_name = ASSISTANT_APP
    assistant_flag_install = config.get_setting('assistant_flag_install', default=True)
    addonid = 'alfa-mobile-assistant'
    download = addonid + '.apk'
    package = addonid + '.apk'
    version = addonid + '.version'
    forced_menu = False
    respuesta = False
    alfa_s = True
    addons_path = config.get_runtime_path()
    if filetools.exists(filetools.join(addons_path, 'channels', 'custom.py')):
        alfa_s = False

    if not remote:
        ANDROID_STORAGE = os.getenv('ANDROID_STORAGE')
        if not ANDROID_STORAGE: ANDROID_STORAGE = '/storage'
    else:
        # Remote es la url de un servidor FTP o SMB activo que apunta a la ruta "/storage" del dispositivo Android
        ANDROID_STORAGE = remote
        if ANDROID_STORAGE.endswith('/'):
            ANDROID_STORAGE = ANDROID_STORAGE[:-1]
    apk_files = '%s/%s/%s/%s/%s/%s' % (ANDROID_STORAGE, 'emulated', '0', 'Android', 'data', app_name)
    if ASSISTANT_MODE == 'este' and not filetools.exists(filetools.dirname(apk_files)):
        apk_files_alt = scrapertools.find_single_match(os.getenv('HOME'), '(.*?)\/\w*.\w*.\w*\/files')
        logger.info('HOME: ' + apk_files_alt)
        if apk_files_alt and filetools.exists(apk_files_alt):
            apk_files = '%s/%s' % (apk_files_alt, app_name)

    version_path = filetools.join(config.get_data_path(), version)
    version_act = filetools.read(version_path, silent=True)
    if not version_act: version_act = '0.0.0'
    
    # Averiguamos si es instalacción, update, o forzado desde el Menú de Ajustes
    if not update and ASSISTANT_MODE == 'este' and filetools.exists(apk_files):
        return version_act, app_name
    if ASSISTANT_MODE == 'este' and not update:
        check_permissions_alfa_assistant()                                      # activamos la app por si no se ha inicializado
        time.sleep(1)
        if filetools.exists(apk_files):
            return version_act, app_name
        else:
            filetools.remove(version_path, silent=True)
    # Mirarmos si la app está activa y obtenemos el nº de versión
    version_dict = get_generic_call('getWebViewInfo', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
    if isinstance(version_dict, dict):
        version_app = version_dict.get('assistantVersion', '')
        try:
            android_version = int(scrapertools.find_single_match(version_dict.get('userAgent', ''), r"Android\s*(\d+)"))
        except:
            android_version = 8
    else:
        version_app = version_dict
        android_version = 8
    if version_app and not update:
        return version_app, app_name
    
    if version_app:
        app_active = True
    else:
        app_active = False
        if ASSISTANT_MODE == "este":
            execute_in_alfa_assistant_with_cmd('open')                          # activamos la app por si no se ha inicializado
            time.sleep(5)
            version_dict = get_generic_call('getWebViewInfo', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
            if isinstance(version_dict, dict):
                version_app = version_dict.get('assistantVersion', '')
                try:
                    android_version = int(scrapertools.find_single_match(version_dict.get('userAgent', ''), r"Android\s*(\d+)"))
                except:
                    android_version = 8
            else:
                version_app = version_dict
                android_version = 8
    version_actual = filetools.read(version_path, silent=True)
    version_dif = False
    if (not version_actual and version_app) or (version_actual and version_app and version_actual != version_app):
        version_dif = True
        version_actual = version_app
        filetools.write(version_path, version_actual, mode='wb', silent=True)
    elif not version_actual:
        version_actual = '0.0.0'
    elif version_actual and version_app and version_actual == version_app:
        config.set_setting('assistant_flag_install', True)

    if ASSISTANT_MODE != 'este':
        if not version_app:
            if verbose or (update and not isinstance(update, bool)):
                platformtools.dialog_notification("Active Alfa Assistant", 
                            "o Instale manualmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]")
            logger.info("Active Alfa Assistant, o Instale manualmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]", force=True)
            config.set_setting('assistant_flag_install', False)
            return version_app, app_name
        else:
            config.set_setting('assistant_flag_install', True)
            if not update:
                return version_app, app_name
    elif not update and not filetools.exists(apk_files):
        logger.info('NO está instalada. No es Update: %s' % app_name)
        return False, app_name
    elif update and isinstance(update, bool) and not filetools.exists(apk_files):
        logger.info('NO está instalada. No se va a actualizar: %s' % app_name)
        filetools.remove(version_path, silent=True)
        return False, app_name
    elif update and not isinstance(update, bool) and not filetools.exists(apk_files):
        logger.info('NO está instalada. Viene del Menú y se va a instalar: %s' % app_name)
        filetools.remove(version_path, silent=True)
        update = False
        forced_menu = True
    elif not remote and PLATFORM not in ['android', 'atv2']:
        logger.info('El sistema local no es Android: %s' % app_name)
        return False, app_name

    logger.info('assistant_mode=%s, update=%s, forced_menu=%s, assistant_flag_install=%s, version_actual=%s, version_app=%s, android=%s, app_active=%s' \
            % (ASSISTANT_MODE, str(update), str(forced_menu), str(assistant_flag_install), version_actual, \
            version_app, str(android_version), str(app_active)))
    
    # Si no está instalada, o se quiere actualizar, empezamos el proceso
    alfa_assistant_pwd = ''
    apk_updated = filetools.join(addons_path, 'tools')
    apk_path = filetools.join(apk_updated, download)
    apk_apk = filetools.join(apk_updated, package)
    upk_install_path = filetools.join('special://xbmc/', 'files').replace('/cache/apk/assets', '')
    if not remote:
        apk_install = filetools.join(ANDROID_STORAGE, 'emulated', '0', 'Download')
        apk_install_SD = filetools.join(apk_install, package)
    else:
        apk_install = '%s/%s/%s/%s' % (ANDROID_STORAGE, 'emulated', '0', 'Download')
        apk_install_SD = '%s/%s' % (apk_install, package)

    if not update and not remote and not forced_menu:
        # Probamos a iniciar por si se ha instalado manualmente y no se ha iniciado la estrucutra de archivos
        check_permissions_alfa_assistant()
        try:
            command = ['pm', 'list', 'packages']
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            PM_LIST, error_cmd = p.communicate()
            if PY3 and isinstance(PM_LIST, bytes):
                PM_LIST = PM_LIST.decode()
            if app_name in PM_LIST:
                logger.info('Ya instalada. Volvemos: %s' % app_name)
                return version_actual, app_name
        except:
            logger.error(traceback.format_exc(1))
    
    if not update and not forced_menu and not platformtools.dialog_yesno("Instalación Alfa Assistant", \
                    "¿Desea instalar la App [COLOR yellow][B]%s[/B][/COLOR]\n" % app_name +
                    " como ayuda para acceder a ciertos canales y servidores?"):
        config.set_setting('assistant_flag_install', False)
        return respuesta, app_name
    elif update and not isinstance(update, bool) and update != 'check':
        platformtools.dialog_notification("Instalación Alfa Assistant", "Comienza la actualización")
    elif forced_menu:
        platformtools.dialog_notification("Instalación Alfa Assistant", "Comienza la instalación")

    # Comprobamos si el dispositivo está rooteado
    is_rooted = config.is_rooted(silent=True)                                   # ¡OJO! puede pedir permisos root en algunos dispositivos
    if is_rooted == 'rooted' and ASSISTANT_MODE == 'este':                      # El dispositivo esta rooteado?
        update_install = 'py'                                                   # Se actualiza desde esta función
    else:
        update_install = 'app'                                                  # Se actualiza desde la app
    cmd = 'update'                                                              # Comando de la app para auto actualizarse
    dataURI = 'Version:%s'                                                      # Versión a actualizar
    
    # Comprobamos si hay acceso a Github o GitLab
    for assistant_rar in assistant_urls:
        response = httptools.downloadpage(assistant_rar+version, timeout=5, ignore_response_code=True, 
                                          alfa_s=alfa_s, json_to_utf8=False, retry_alt=False, proxy_retries=0)
        if response.sucess:
            break
    
    # Descargamos el archivo de version.  Si hay error avisamos, pero continuamos
    if not response.sucess:
        if update and isinstance(update, bool):
            logger.error("Error en la descarga de control de versión. No se puede actualizar: %s" % str(response.code))
            return respuesta, app_name
        platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la descarga de control de versión. Seguimos")
        logger.error("Error en la descarga de control de versión. Seguimos...: %s" % str(response.code))

    #Si es una actualización programada, comprobamos las versiones de Github y de lo instalado
    if (update and isinstance(update, bool)) or (not isinstance(update, bool) and update == 'check'):
        try:
            newer = False
            installed_version_list = version_actual.split('.')
            web_version_list = response.data.split('.')
            for i, ver in enumerate(web_version_list):
                if int(ver) > int(installed_version_list[i]):
                    newer = True
                    break
                if int(ver) < int(installed_version_list[i]):
                    newer = False
                    break
        except:
            pass

        if not newer:
            if verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Ya está actualizado a version %s" % version_actual)
            logger.info("Alfa Assistant ya actualizado a versión: %s" % version_actual)
            if not app_active and ASSISTANT_MODE == "este":
                execute_in_alfa_assistant_with_cmd('quit')                      # desactivamos la app si no estaba iniciada
            return version_actual, app_name

    # Guardamos archivo de versión
    if remote:
        version_path = '%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s' % (ANDROID_STORAGE, 'emulated', '0', 'Android', 
                        'data', 'org.xbmc.kodi', 'files', '.kodi', 'addons', 'plugin.video.alfa', 
                        'tools', version)
        if not filetools.exists(filetools.dirname(version_path)):
            logger.error("Ruta a carpeta remota de versión no es estándar: %s" % version_path)
            version_path = ''
    version_old = version_actual
    version_actual = response.data
    if version_path:
        res = filetools.write(version_path, response.data, mode='wb', silent=True)
        if not res:
            if not update: platformtools.dialog_notification("Instalación Alfa Assistant", \
                            "Error en la escritura de control de versión. Seguimos...")
            logger.error("Error en la escritura de control de versión. Seguimos...: %s" % assistant_rar)

    # Descargamos y guardamos el .APK
    #assistant_rar = assistant_rar.replace(version, download)                    # Sustituir en la url la versión por el apk
    res = False
    if not update: platformtools.dialog_notification("Instalación Alfa Assistant", "Descargando APK")
    logger.info('Descargando de_ %s' % assistant_rar)
    response = httptools.downloadpage(assistant_rar+download, timeout=10, ignore_response_code=True, 
                                      alfa_s=alfa_s, json_to_utf8=False, retry_alt=False)
    if not response.sucess:
        if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la descarga del .apk")
        response.data = ''
        logger.error("Error en la descarga del .apk: %s" % str(response.code))
    else:
        # Guardamos archivo descargado de APK
        res = filetools.write(apk_path, response.data, mode='wb', silent=True)
        if not res:
            if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la escritura del APK")
            logger.error("Error en la escritura del APK: %s" % apk_path)
        
        else:
            if '.rar' in download:
                # Empezando la extracción del .rar del APK
                try:
                    if PY3 and (not alfa_assistant_pwd or not config.get_setting('assistant_binary')):
                        import rarfile
                    else:
                        import rarfile_py2 as rarfile
                    archive = rarfile.RarFile(apk_path)
                    if alfa_assistant_pwd: archive.setpassword(alfa_assistant_pwd)
                    archive.extractall(apk_updated)
                except:
                    logger.error(traceback.format_exc(1))
            elif '.zip' in download:
                # Empezando la extracción del .rar del APK
                try:
                    import ziptools
                    archive = ziptools.ziptools()
                    #if alfa_assistant_pwd: archive.setpassword(alfa_assistant_pwd)      # No hay password en .zip
                    archive.extract(filetools.basename(apk_updated), filetools.dirname(apk_updated))
                except:
                    xbmc.executebuiltin('Extract("%s","%s")' % (filetools.basename(apk_updated), filetools.dirname(apk_updated)))
                    time.sleep(1)

            # Verificado si está el APK, y si está y es LOCAL lo instalamos
            if ASSISTANT_MODE == "este":
                res = filetools.copy(apk_apk, apk_install_SD, silent=True)
                if not res or not filetools.exists(apk_install_SD):
                    if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error de Extracción o Copia %s" % package)
                    logger.error("Error de Extracción o copia %s" % package)
                
                # Si está rooteado se instala/actualiza directamente
                elif update_install == 'py' and res and filetools.exists(apk_install_SD):

                    # Instalamos: nueva o actualización. 
                    if not update: platformtools.dialog_notification("Instalación Alfa Assistant", "Installando %s" % package)
                    logger.info("Installing %s" % package)
                    
                    # Instalación Remota
                    if remote:
                        filetools.remove(apk_apk, silent=True)
                        platformtools.dialog_notification("Alfa Assistant: Descarga Remota terminada", "Instale manualmente desde: %s" % apk_install_SD)
                        logger.info("Alfa Assistant: Descarga Remota terminada. Instale manualmente desde: %s" % apk_install_SD)
                        return version_actual, app_name

                    # Instalación Local
                    if not filetools.exists(upk_install_path):
                        filetools.mkdir(upk_install_path)
                    upk_install_path = filetools.join(upk_install_path, package)
                    res = filetools.copy(apk_install_SD, upk_install_path, ch_mod='777')    # Copiamos APK a la partición del Sistema, y cambiamos permisos
                    if not res:
                        if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error de Copia %s" % package)
                        logger.error(str(filetools.listdir(apk_install)))
                        logger.error(filetools.file_info(filetools.dirname(upk_install_path)))
                        logger.error(str(filetools.listdir(filetools.dirname(upk_install_path), file_inf=True)))
                    else:

                        # Intenta la instalación vía ROOT y si no funciona como NO ROOT
                        
                        # Marcamos la opción de instalación, -r si es actualización, -g (todos los permisos granted) si es instalación
                        if filetools.exists(apk_files):
                            pm_opt = '-r'
                        else:
                            pm_opt = '-g'
                        
                        # Listamos todas las opciones de comandos, según las variantes de Android
                        command_list = [
                                        ['adb', 'install', '%s' % upk_install_path],
                                        ['su', '-c', 'pm install %s %s' % (pm_opt, upk_install_path)],
                                        ['su', '-c', 'pm', 'install', pm_opt, '%s' % upk_install_path],
                                        ['su', '-0', 'pm install %s %s' % (pm_opt, upk_install_path)],
                                        ['su', '-0', 'pm', 'install', pm_opt, '%s' % upk_install_path]
                                       ]
                        
                        for command in command_list:
                            try:
                                logger.info(command, force=True)
                                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                output_cmd, error_cmd = p.communicate()
                                if PY3 and isinstance(output_cmd, bytes): output_cmd = output_cmd.decode('utf-8')
                                if PY3 and isinstance(error_cmd, bytes): error_cmd = error_cmd.decode('utf-8')
                                if error_cmd:
                                    if error_cmd.startswith('su:'): continue
                                    if update:
                                        ver_upd = get_generic_call('ping', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
                                        if not ver_upd:
                                            execute_in_alfa_assistant_with_cmd('open')  # activamos la app por si no se ha inicializado
                                            time.sleep(5)
                                            ver_upd = get_generic_call('ping', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
                                            execute_in_alfa_assistant_with_cmd('quit')
                                        if ver_upd == version_actual:
                                            logger.debug(str(error_cmd), force=True)
                                            error_cmd = ''
                                    else:
                                        check_permissions_alfa_assistant()
                                        time.sleep(1)
                                        if filetools.exists(apk_files):
                                            logger.debug(str(error_cmd), force=True)
                                            error_cmd = ''
                                    if error_cmd:
                                        logger.error(str(error_cmd))
                                    else:
                                        respuesta = version_actual
                                        break
                                else:
                                    respuesta = version_actual
                                    break
                            except Exception as e:
                                if not PY3:
                                    e = unicode(str(e), "utf8", errors="replace").encode("utf8")
                                logger.error('Command ERROR: %s, %s' % (str(command), str(e)))
                                continue
      
    # Ùltimo resorte: instalación manual desde GitHub o actualización desde la app
    if not respuesta and update and not version_dif:
        
        # Si hay que actualizar se verifica el vehículo de instalación
        logger.info("Instalación Alfa Assistant. Actualización desde la app de %s a %s" % (version_old, version_actual))
        version_mod = version_actual
        if not isinstance(update, bool):
            version_mod = '9.9.999'                                             # Intenta forzar la actualización si viene desde el Menú
        if ASSISTANT_MODE == "este":
            if android_version >= 10:
                app_active = False
                res = open_alfa_assistant(getWebViewInfo=True, assistantLatestVersion=False, retry=True)
                respuesta = execute_in_alfa_assistant_with_cmd(cmd, dataURI=dataURI % version_mod)
            else:
                if not app_active:
                    execute_in_alfa_assistant_with_cmd('openAndQuit')           # activamos la app por si no se ha inicializado
                    time.sleep(5)
                app_active = False
                respuesta = get_generic_call(cmd, version=version_mod, alfa_s=alfa_s)
        else:
            if app_active:
                respuesta = get_generic_call(cmd, version=version_mod, alfa_s=alfa_s)

        if not respuesta and ASSISTANT_MODE != "este":
            if verbose or not isinstance(update, bool):
                platformtools.dialog_notification("Instalación Alfa Assistant", "Intente la actualización manualmente %s" % version_actual)
            logger.info("Instalación Alfa Assistant. Intente la actualización manualmente %s" % version_actual)
            return False, app_name
        elif not respuesta:
            # Update local
            #respuesta = execute_in_alfa_assistant_with_cmd(cmd, dataURI=dataURI % version_mod)
            if not respuesta:
                if verbose or not isinstance(update, bool):
                    platformtools.dialog_notification("Instalación Alfa Assistant", "Actualización en error %s. REINTENTANDO" % version_actual)
                logger.info("Instalación Alfa Assistant. Actualización en error %s. REINTENTANDO" % version_actual)
        else:
            respuesta = version_actual
        
    if not respuesta:
        config.set_setting('assistant_flag_install', False)                     # No vuelve a intentar la instalación
        try:
            #xbmc.executebuiltin('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:%s")' % apk_install_SD)
            
            if ASSISTANT_MODE == "este":
                from lib import generictools
                assistant_rar = assistant_rar.replace('/raw/', '/tree/') + download     # Apuntar a la web de descargas
                browser, res = generictools.call_browser(assistant_rar, lookup=True)
                if browser:
                    filetools.remove(apk_install_SD, silent=True)
                    platformtools.dialog_ok("Alfa Assistant: Instale desde [COLOR yellow]%s[/COLOR]" % browser.capitalize(), 
                                    "O Instale manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_install_SD)
                    logger.info('Browser: %s, Ruta: %s' % (browser.capitalize(), apk_install_SD))
                    time.sleep(5)
                    browser, res = generictools.call_browser(assistant_rar, dataType='application/vnd.android.package-archive')
                    filetools.remove(apk_path, silent=True)
                    filetools.remove(upk_install_path, silent=True)
                else:
                    logger.error('Error de Instalación: NO Browser, Ruta: %s' % apk_install_SD)
                    raise
            else:
                logger.error('Error de Instalación: no se puede instalar en remoto: %s' % ASSISTANT_SERVER)
                raise
        except:
            if ASSISTANT_MODE == "este":
                platformtools.dialog_ok("Alfa Assistant: Error", "Instale manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_install_SD)
                logger.error("Alfa Assistant: Error. Instale manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_install_SD)
                filetools.remove(apk_path, silent=True)
                filetools.remove(upk_install_path, silent=True)
            else:
                platformtools.dialog_ok("Alfa Assistant: Error", "Copie a Android manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_apk)
                logger.error("Alfa Assistant: Error. Copie a Android manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_apk)
            logger.error(traceback.format_exc(1))

    if respuesta:
        if update:
            if verbose or not isinstance(update, bool): platformtools.dialog_notification("Alfa Assistant", \
                                "Actualización con exito: %s" % respuesta)
            logger.info("Actualización terminada con éxito: %s" % respuesta)
        else:
            platformtools.dialog_notification("Alfa Assistant", "Instalación con exito: %s" % respuesta)
            logger.info("Instalación terminada con éxito: %s" % respuesta)
        filetools.remove(apk_path, silent=True)
        filetools.remove(apk_install_SD, silent=True)
        filetools.remove(upk_install_path, silent=True)
        if not update and not forced_menu:
            time.sleep(1)
            check_permissions_alfa_assistant()
            time.sleep(1)
        if app_active and ASSISTANT_MODE == "este":
            execute_in_alfa_assistant_with_cmd('open')                          # re-activamos la app para dejarla como estaba
        
    return respuesta, app_name

#
## Instala o actualiza el DESKTOP de Assitant ##################################################################################################################################
#
def install_alfa_desktop_assistant(update=False, remote='', verbose=VERBOSE):
    
    platform = PLATFORM
    if update:
        logger.info('update=%s' % str(update))

    app_name = ASSISTANT_DESKTOP
    version_name = '%s.version' % (app_name)
    assistant_flag_install = config.get_setting('assistant_flag_install')
    alfa_s = True
    force_install = False                                                       # Instalación bajo demanda ?
    addons_path = config.get_runtime_path()
    if filetools.exists(filetools.join(addons_path, 'channels', 'custom.py')):
        alfa_s = False
    respuesta = False
    assistant_url = ''

    install_path = filetools.join(addons_path, 'lib', 'assistant', platform, version_name)
    version_inst = filetools.read(install_path)
    zip_path = filetools.join(addons_path, 'tools', app_name+'.zip')
    if update and filetools.exists(zip_path): filetools.remove(zip_path, silent=True)
    binary_path = filetools.join(config.get_data_path(), 'assistant')
    binary_exec = filetools.join(binary_path, app_name+'.exe')
    version_actual_path = filetools.join(config.get_data_path(), version_name)
    if filetools.exists(version_actual_path) and not filetools.exists(binary_path):
        version_act = ''
        filetools.remove(version_actual_path, silent=False)
    else:
        version_act = filetools.read(version_actual_path, silent=True)
    if not version_act: version_act = ''
    version_app = version_act

    # Si no se quiere instalar, se borra
    if not assistant_flag_install and str(update) != 'auto':
        if filetools.exists(binary_path):
            res = get_generic_call('quit', timeout=1-EXTRA_TIMEOUT, alfa_s=True)    # desactivamos la app si estaba iniciada
            res = filetools.rmdirtree(binary_path, silent=False)
            if res: filetools.remove(version_actual_path, silent=False)
            logger.info("Alfa Assistant eliminado con éxito, versión: %s" % version_app)
        return respuesta, app_name

    # Si ya está instalada, devolvemos el control
    if not update and version_act and filetools.exists(binary_exec):
        return version_act, app_name
    
    # Si no está instalada y es update normal, devolvemos el control
    if not version_act and str(update) != 'auto' and not force_install:
        logger.info("Alfa Assistant no instalado.  No se actualiza")
        return respuesta, app_name

    # Actualizamos la versión del Assistant
    if version_act == version_inst and update == True and filetools.exists(binary_exec):
        logger.info("Alfa Assistant está actualizado, versión: %s" % version_act)
        return version_act, app_name
        
    # Mirarmos si la app está activa y obtenemos el nº de versión
    if not version_act: version_act = '0.0.01'
    config.set_setting('assistant_flag_install', True)
    if filetools.exists(binary_exec):
        version_dict = get_generic_call('getWebViewInfo', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
        if isinstance(version_dict, dict):
            version_app = version_dict.get('assistantVersion', '')
        else:
            version_app = version_dict
    if not version_app:
        version_app = version_act
    
    # Comprobamos si hay acceso a Github o GitLab o Dropbox
    if not assistant_urls:
        logger.error("Error en la descarga de la VERSIÓN: %s" % str(platform))
        return respuesta, app_name
    for _assistant_url in assistant_urls:
        assistant_url = '%s%s/%s' % (_assistant_url, platform, version_name)
        #assistant_url = _assistant_url
        response = httptools.downloadpage(assistant_url, timeout=5, ignore_response_code=True, 
                                          alfa_s=alfa_s, json_to_utf8=False, retry_alt=False, proxy_retries=0)
        if response.sucess:
            break
    
    # Si hay error terminamos
    if not response.sucess:
        platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la descarga de control de versión")
        logger.error("Error en la descarga de control de versión. No se puede actualizar: %s" % str(response.code))
        return respuesta, app_name
        
    #Si es una actualización programada, comprobamos las versiones de Github y de lo instalado
    data = response.data
    if PY3 and isinstance(data, bytes):
        data = "".join(chr(x) for x in bytes(data))
    if (update and isinstance(update, bool)) or (not isinstance(update, bool) and update == 'check'):
        try:
            newer = False
            installed_version_list = version_app.split('.')
            web_version_list = data.split('.')
            for i, ver in enumerate(web_version_list):
                if int(ver) > int(installed_version_list[i]):
                    newer = True
                    break
                if int(ver) < int(installed_version_list[i]):
                    newer = False
                    break
        except:
            pass

        if not newer:
            if verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Ya está actualizado a version %s" % version_app)
            logger.info("Alfa Assistant ya actualizado a versión: %s" % version_app)
            return version_app, app_name

    # Guardamos el número de versión descargada
    if version_actual_path:
        version_act = version_app = data
        res = filetools.write(version_actual_path, version_act, mode='wb', silent=True)
        if not res:
            if not update: platformtools.dialog_notification("Instalación Alfa Assistant", \
                            "Error en la escritura de control de versión. Seguimos...")
            logger.error("Error en la escritura de control de versión. Seguimos...: %s" % version_actual_path)
        res = filetools.write(install_path, version_act, mode='wb', silent=True)
        if not res:
            logger.error("Error en la escritura de control de versión. Seguimos...: %s" % install_path)

    # Descargamos y guardamos el BINARIO
    if update != True: platformtools.dialog_notification("Instalación Alfa Assistant", "Descargando BINARIO")
    assistant_url = '%s%s/%s-%s.zip' % (_assistant_url, platform, app_name, platform)
    #if assistant_desktop_urls.get(platform, []):
    #    assistant_url = assistant_desktop_urls[platform][1]
    #else:
    #    logger.error("Error en la descarga del BINARIO: %s" % str(platform))
    #    return respuesta, app_name
    logger.info('Descargando de_ %s' % assistant_url)
    response = httptools.downloadpage(assistant_url, timeout=30, ignore_response_code=True, 
                                      alfa_s=alfa_s, json_to_utf8=False, retry_alt=False, proxy_retries=0)
    if not response.sucess:
        if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la descarga del BINARIO")
        logger.error("Error en la descarga del BINARIO: %s" % str(response.code))
        return respuesta, app_name
    else:
        # Guardamos archivo descargado .zip
        res = filetools.write(zip_path, response.data, mode='wb', silent=True)
        if not res:
            if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la escritura del BINARIO")
            logger.error("Error en la escritura del BINARIO: %s" % zip_path)
            return respuesta, app_name
        else:
            global isAlfaAssistantOpen
            isAlfaAssistantOpen = False
            res = get_generic_call('terminate', timeout=1-EXTRA_TIMEOUT, alfa_s=True)   # desactivamos la app si estaba iniciada
            # Empezando la extracción del .zip del DESKTOP
            if filetools.exists(binary_path):
                res = filetools.rmdirtree(binary_path, silent=False)
                time.sleep(2)
            try:
                import ziptools
                archive = ziptools.ziptools()
                archive.extract(zip_path, binary_path)
            except:
                xbmc.executebuiltin('Extract("%s","%s")' % (zip_path, binary_path))
            for x in range(30):
                if filetools.exists(binary_exec): break
                time.sleep(1)
            else:
                filetools.remove(version_actual_path, silent=False)
                logger.error("Error en la instalación del BINARIO: %s" % zip_path)
                if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", 
                                                                            "Error en la instalación del BINARIO, versión: %s" % version_app)
                return respuesta, app_name

    # Procesamos instalaciones adicionales que vengan con el .zip
    for install in sorted(filetools.listdir(binary_path)):
        if not install.startswith('install'): continue
        ins_path = filetools.join(binary_path, install)
        ins_path_cmd = ins_path if ' ' not in ins_path else '"%s"' % ins_path
        ins_path_cmd = '%s %s%s %s' % (ins_path_cmd, _assistant_url, platform, binary_path if ' ' not in binary_path else '"%s"' % binary_path)
        if not filetools.isfile(ins_path): continue
        filetools.chmod(ins_path, '777', silent=True)
        creationflags = 0
        if PLATFORM in ['windows', 'xbox']:
            creationflags = 0x08000000
        try:
            logger.info('Instalando software adicional: %s' % ins_path_cmd)
            p = subprocess.Popen(ins_path_cmd, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                 stdin=subprocess.PIPE, cwd=binary_path, creationflags=creationflags, shell=True)
            output_cmd, error_cmd = p.communicate(timeout=15)
            if not error_cmd:
                filetools.remove(ins_path, silent=True)
            else:
                logger.error('## ERROR Apt_Install CMD: %s, error: %s' % (ins_path, str(error_cmd)))
        except Exception as e:
            if not PY3:
                e = unicode(str(e), "utf8", errors="replace").encode("utf8")
            elif PY3 and isinstance(e, bytes):
                e = e.decode("utf8")
            logger.error('## ERROR Apt_Install CMD: %s, error: %s' % (ins_path, e))
    
    if assistant_flag_install:
        execute_in_alfa_assistant_with_cmd('open')                              # re-activamos la app para dejarla como estaba
        time.sleep(2)
        version_dict = get_generic_call('getWebViewInfo', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
        logger.info('getWebViewInfo: %s' % version_dict)
        if version_dict: 
            isAlfaAssistantOpen = True
            if isinstance(version_dict, dict):
                version_app = version_dict.get('assistantVersion', '')
            else:
                version_app = version_dict
            if not version_app: version_app = '0.0.01'
            if version_app != version_act:
                version_act = version_app
                res = filetools.write(version_actual_path, version_act, mode='wb', silent=True)

    logger.info("Alfa Assistant instalado con éxito, versión: %s" % version_app)
    if not update or verbose:
        platformtools.dialog_notification("Instalación Alfa Assistant", "Instalación terminada con éxito, versión: %s" % version_app)

    return version_act, app_name
