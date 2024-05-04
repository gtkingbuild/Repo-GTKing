# -*- coding: utf-8 -*-
# -*- Debrider All-Debrid -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
import time
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

from core import httptools
from core import scrapertools
from platformcode import platformtools
from platformcode import config, logger

api = 'https://api.alldebrid.com/v4/'
agent_id = "AlfaAddon"
ERRORS = {  
        'GENERIC': 'Ha ocurrido un error',
        '404': "Error en la url de la api",
        'AUTH_MISSING_APIKEY': 'La Api-Key no fue enviada',
        'AUTH_BAD_APIKEY': 'Autentificación/Api-Key no válida',
        'AUTH_BLOCKED': 'Api-Key con geobloqueo (Deshabilitelo en su cuenta)\n o ip bloqueada',
        'AUTH_USER_BANNED': 'Esta cuenta ha sido baneada',

        'LINK_IS_MISSING': 'No se ha enviadado ningún link',
        'LINK_HOST_NOT_SUPPORTED': 'Servidor o link no soportados',
        'LINK_DOWN': 'Link caido, no disponible',
        'LINK_PASS_PROTECTED': 'Link con contraseña',
        'LINK_HOST_UNAVAILABLE': 'Servidor en mantenimiento o no disponible',
        'LINK_TOO_MANY_DOWNLOADS': 'Demasiadas descargas simultaneas para este Servidor',
        'LINK_HOST_FULL': 'Nuestros servidores están temporalmente ocupados, intentelo más tarde',
        'LINK_HOST_LIMIT_REACHED': "Ha excedido el limite de descarga para este Servidor",
        'LINK_ERROR': 'No se puede convertir este link',

        'FREE_TRIAL_LIMIT_REACHED': 'Ha superado el limite para cuenta de prueba (7 dias // 25GB descargados\n o Servidor inaccesible para cuentas de prueba)',
        'MUST_BE_PREMIUM': "Debe tener cuenta Premium para procesar este link",

        'PIN_ALREADY_AUTHED': "Ya tiene una Api-Key autentificada",
        'PIN_EXPIRED': "El código introducido expiró",
        'PIN_INVALID': "El código introducido no es válido",

        'NO_SERVER': "Los servidores no tienen permitido usar esta opción. \nVisite https://alldebrid.com/vpn si está usando una VPN."}

def get_video_url(page_url, premium=False, user="", password="", video_password="", retry=True):
    logger.info()
    #page_url = correct_url(page_url)
    api_key = config.get_setting("api_key", server="alldebrid")

    if not api_key:
        if config.is_xbmc():
            api_key = authentication()
            if not api_key:
                return [["All-Debdrid: No se ha podido completar el proceso de autentificación", ""]]
            elif isinstance(api_key, dict):
                error = api_key['error']
                return [['[All-Debrid] %s' % error, ""]]
        else:
            return [["Es necesario activar la cuenta manualmente. Accede al menú de ayuda", ""]]
    
    page_url = urllib.quote(page_url)
    url = "%slink/unlock?agent=%s&apikey=%s&link=%s" % (api, agent_id, api_key, page_url)
    
    dd = httptools.downloadpage(url).json
    dd_data = dd.get('data', '')

    error = dd.get('error', '')
    if error:
        code = error.get('code', '')
        if code == 'AUTH_BAD_APIKEY' and retry:
            config.set_setting("api_key", "", server="alldebrid")
            return get_video_url(page_url, premium=premium, retry=False)
        elif code:
            msg = ERRORS.get(code, code)
            logger.error(dd)
            return [['[All-Debrid] %s' % msg, ""]]




    video_urls = get_links(dd_data)
    
    if video_urls:
        return video_urls
    else:
        server_error = "Alldebrid: Error desconocido en la api"
        return server_error


# def correct_url(url):
#     if "uptostream.com" in url:
#         url = url.replace("uptostream.com/iframe/", "uptobox.com/")
#     return url

def get_links(dd_data):
    logger.info()
    if not dd_data:
        return False
    video_urls = list()

    link = dd_data.get('link', '')
    streams = dd_data.get('streams', '')
    
    if link:
        extension = dd_data['filename'][-4:]
        video_urls.append(['%s [Original][All-Debrid]' % extension, link])
    
    if streams:
        for info in streams:
            quality = str(info.get('quality', ''))
            if quality:
                quality += 'p'
            ext = info.get('ext', '')
            link = info.get('link', '')
            video_urls.append(['%s %s [All-Debrid]' % (extension, quality), link])

    return video_urls

def authentication():
    logger.info()
    api_key = ""
    try:

        #https://docs.alldebrid.com
        url = "%spin/get?agent=%s" % (api, agent_id)
        data = httptools.downloadpage(url, ignore_response_code=True).json
        json_data = data.get('data','')
        if not json_data:
            return False

        pin = json_data["pin"]
        base_url = json_data["base_url"]
        #check = json_data["check"]
        expires = json_data["expires_in"]
        check_url = json_data["check_url"]

        intervalo = 5

        dialog_auth = platformtools.dialog_progress(config.get_localized_string(70414),
                                                    config.get_localized_string(60252) % base_url,
                                                    config.get_localized_string(70413) % pin,
                                                    config.get_localized_string(60254))

        #Cada 5 segundos se intenta comprobar si el usuario ha introducido el código
        #Si el tiempo que impone alldebrid (10 mins) expira se detiene el proceso
        while expires > 0:
            time.sleep(intervalo)
            expires -= intervalo
            try:
                if dialog_auth.iscanceled():
                    return False

                
                data = httptools.downloadpage(check_url, ignore_response_code=True).json
                check_data = data.get('data','')
                
                if not check_data:
                    code = data['error']['code']
                    msg = ERRORS.get(code, code)
                    return {'error': msg}
                
                if check_data["activated"]:
                    api_key = check_data["apikey"]
                    break
            except:
                pass

        try:
            dialog_auth.close()
        except:
            pass

        if expires <= 0:
            error = "Tiempo de espera expirado. Vuelva a intentarlo"
            return {'error': error}

        if api_key:
            config.set_setting("api_key", api_key, server="alldebrid")
            return api_key
        else:
            return False
    except:
        import traceback
        logger.error(traceback.format_exc())
        return False
