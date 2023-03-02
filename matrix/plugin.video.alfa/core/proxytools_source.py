# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# proxytools
# ------------------------------------------------------------------------------
"""
Realiza funciones de ocultación de la url de las web de destino listadas, para bordear
 los bloqueos judiciales o de las operadoras.  Se pretende que este proceso sea lo más 
 automático y transparente para los canales en lo posible.

Existen dos tipos de proxies gratuitos:
-	Proxy Web
-	Proxy “directo”.  Dentro de este grupo hay direcciones que soportar CloudFlare.

En el Proxy Web, se llama a una web Proxy donde se le pasa como Post la url de la 
web de destino, así como los parámetros que indican que NO encripte la url o los 
datos, y que sí use cookies.

En los datos de respuesta hay que suprimir de las urls una cabecera y una cola, 
que varían según la web Proxy.  El resultado es una página bastante parecida a 
la que se obtendría sin usar el proxy, aunque en el canal que lo use se debe 
verificar que las expresiones regex funcionan sin problemas.

Se ha creado un Diccionario con las entradas verificadas de Proxy Webs.  En esas 
entradas se encuentran los parámetros necesarios para enviar la url de la web de 
destino, así como para convertir los datos de retorno a algo transparente para el 
canal.  Habrá que ir añadiendo y borrando Webs Proxy según su rendimiento y estabilidad.

El Proxy “directo”, es totalmente transparente para el canal, permitiendo usar 
Post, y en algunos casos llamadas a webs que usan Cloudflare.  El problema que 
tienen estos Proxies es su extremada volatilidad en la disponibilidad y tiempo 
de respuesta.

Se ha confeccionado una lista inicial de Proxies directos y otra de Proxies CloudFlare 
que han sido probados y que suelen funcionar 
con regularidad.  A esta lista inicial se añaden dinámicamente otros de web(s) que 
listan estos proxy gratuitos, con algunos criterios de búsqueda exigentes de 
disponibilidad y tiempo de respuesta.  La búsqueda se limita a 50 direcciones válidas.

Se ha optado por usar por defecto los Proxies “directos”, dejando los Proxy Webs 
como alternativa automática para el caso de indisponibilidad de Proxies “directos”.

Desde cualquier Canal se pueden hacer llamadas a Httptools para que sean filtradas 
por algún tipo de Proxy.  Las llamadas deben incluir los parámetros "proxy=True o 
proxy_web=True" y "forced_proxy=Total|ProxyDirect|ProxyCF|ProxyWeb[:WebName]".  Con la opción 
"Total" asumirá "ProxyDirect" para "proxy=True".  También se puede añadir una dirección
IP estática para usar como proxy ('http[s]': 'xxx.xxx.xxx.xxx'), sola (sin recuperación) 
o en conjunción con las opciones anteriores (con recuperación)

TABLAS:
Como va a ser un módulo de mucho uso, se ha organizado con tablas en memoria en 
vez de en archivos .json, para minimizar el impacto en el rendimiento.  Por otra 
parte, es recomendable que este .py (y por tanto sus tablas) esté “encoded” o mejor 
encriptado para evitar que las acciones y direcciones que aquí se describen sean 
fácilmente neutralizables.

-	channel_bloqued_list = lista de webs bloqueadas a ser tratadas por Proxytools.  
Tiene lista de bloqueos geográfica.
-	operator_bloqued_list = lista de webs/servidores bloqueados por Operadoras en 
países específicos.  Verifica si el usuario tiene esa Operadora en su geografía,
y si es así añade las urls a la lista final de channel_bloqued_list.  Se puede
especificar el nombre o el ASN de la Operadora (sin el prefijo "AS")
-	proxies_list = lista de Proxies “directos” iniciales, verificados tanto para 
http como para https
-   proxies_cloudflare_list = lista de Proxies “directos CloodFlare” iniciales, 
verificados
-	proxy_web_list = lista de Proxy Webs, con sus parámetros de uso
-	proxy_white_list_init = lista de webs bloqueadas donde se dice con qué tipo 
de proxy especifico se quiere tratar.  Si la web bloqueada no está en esta lista, 
se trata con los proxies por defecto.

MÉTODOS:
-	get_proxy_list_monitor: es un SERVICIO que se lanza al inicio de Alfa. Si en 
los settings se ha especificado que el uso de "Acceso Alternativo a la Web" está 
desactivado, se activa el "Modo Demanda" usando las direciones de Proxies por 
defecto.  Si está activo, se asume el "Modo Forzado" y se ejecutará periódicamente 
(cada 12 horas), siempre que no haya reporducciones activas.  Este servicio realiza 
las siguiente funciones:
	o	Identifica el país del usuario y activa/desactiva el proxy en cada web 
    bloquedad según la lista paises bloqueados
	o	Aleatoriza las listas iniciales de direcciones proxy
    o	Si no hay bloqueos en la zona geográfica del usuario, abandona
-   Si estamos en "Modo Forzado", llama al método get_proxy_list_method, que realiza 
estas tareas de inicilaización de tablas:
	o	Carga la lista inicial de Proxies “directos” y los aleatoriza
	o	De la web “HideMy.name” obtiene una lista adicional de Proxies “directos”
	o	Usando la web bloqueada “mejortorrent.com”, se validan los Proxies “directos” 
    hasta que se encuentra uno que responde correctamente.  Este proxy encontrado 
    pasa a ser el usado por defecto durante este periodo
    o	Similar a Proxies “directos”, de la lista inicial se aleatoriza y se verifica 
    uno que funcione
	o	Se valida la lista de Proxy Webs hasta que se encuentra una que responda 
    correctamente.  Esta Proxy Web encontrada pasa a ser la usada por defecto durante 
    este periodo. Es preferible utilizar "hidester.com" por su reputación y porque 
    soporta bien las llamadas con POST desde el canal.  Si no estuviera disponoble, 
    te tomaría otra, pero las llamadas con POST se realizarían por "ProxyDirect"
	o	En la “whitelist” se analiza si hay más de una Proxy alternativo por web 
    bloqueada.  Si es así, se aleatorizan las entradas y se escoge una para este periodo
	o	Los datos de Proxy “directo” activo, lista de Proxies “directos”, nombre 
    de Proxy Web activo,  y Proxy “whitelist” en uso se guardan como parámetros 
    en “settings.xml, encoded Base64”, aunque está preparado para encriptarlo con 
    un nivel de seguridad más alto.
-	randomize_lists: aleatoriza las listas iniciales de direcciones proxy
-	set_proxy_web: prepara los parámetros para llamar a un Proxy Web
-	restore_after_proxy_web: retira los datos del Proxy Web de la respuesta, para 
hacerlo transparente al canal
-	channel_proxy_list: verifica si la web de la url está bloqueada en esa geolocalización
-	get_proxy_addr: pasa los datos del Proxy “directo”, Proxy “CloudFlare” y 
Proxy Web por defecto, modificados con los valores de la “whitelist”, si los hay
-	encrypt_proxy: codifica en Base64 los datos pasados, con potencial para encriptación
-	decrypt_proxy: decodifica desde Base64 los datos pasados
"""

#from builtins import str
from builtins import range
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                                               # Usamos el nativo de PY2 que es más rápido

import base64
import re
import time
import threading
import traceback
import ast
import random
import queue
import json
import os

from platformcode import config, logger
from platformcode.logger import WebErrorException
from core.scrapertools import find_single_match

debugging = False


proxies_list = ['1.180.156.226:65001', '113.160.37.152:53281', '119.28.30.159:60080', 
                '37.29.80.161:8080']

proxies_cloudflare_list = proxies_list

proxy_web_list = {
    'hidester.com': ('https://us.hidester.com/do.php?action=go',
                'https://us.hidester.com', '', '/proxy.php?u=', '&b=2', 
                '&b=\d+|&amp;b=\d+', 'u=%s+&allowCookies=on', '', {}, ''), 
    'hide.me': ('https://nl.hideproxy.me/includes/process.php?action=update',
                'https://nl.hideproxy.me', '', '/go.php?u=', '&b=4', '&b=\d+|&amp;b=\d+', 'u=%s&proxy_formdata_server=nl&allowCookies=1&encodeURL=0', '', {}, ''), 
    'webproxy.to': ('http://webproxy.to/includes/process.php?action=update', 
                'http://webproxy.to', '', '/browse.php?u=', '&b=4', '&b=\d+|&amp;b=\d+', 'u=%s&encodeURL=0&encodePage=0&allowCookies=on&stripJS=0&stripObjects=0', '', {}, ''), 
    'logistef.fr': ('https://proxy.logistef.fr/includes/process.php?action=update', 
                'https://proxy.logistef.fr', '', '/browse.php?u=', '&b=4', '&b=\d+|&amp;b=\d+', 'u=%s&encodeURL=0&encodePage=0&allowCookies=on&stripJS=0&stripObjects=0', '', {}, ''), 
    'itoad.net': ('https://p.itoad.net/includes/process.php?action=update', 
                'https://p.itoad.net', '', '/browse.php?u=', '&b=4', '&b=\d+|&amp;b=\d+', 'u=%s&encodeURL=0&encodePage=0&allowCookies=on&stripJS=0&stripObjects=0', '', {}, ''), 
    'croxyproxy.com': ('%ssuggest/?__cpo=%s', 
                '%s/%s/?__cpo=%s', '', '', '', '', '', 'https://www.croxyproxy.com/requests?fso=', 
                {'Content-type': 'application/x-www-form-urlencoded', 'Referer': 'https://www.croxyproxy.com/servers'}, 
                'url=%s&proxyServerId=%s&demo=0')
                 }
"""
Está filtrando las webs bloqueadas
'yellowproxy.net': ('https://www.yellowproxy.net/includes/process.php?action=update',
                'https://www.yellowproxy.net', '', '/browse.php?u=', '&b=4', '&b=\d+|&f=ajax|&amp;b=\d+|&amp;f=ajax', 'u=%s&allowCookies=on'), 
"""

proxy_web_name_LIST = ['hide.me', 'webproxy.to']                                # Lista de ProxyWebs activos
proxy_web_name_POST = ['hidester.com', 'croxyproxy.com']                        # ProxyWebs que soportan POST
proxy_web_name_JSON = ['croxyproxy.com']                                        # ProxyWebs que soportan JSON
proxy_web_name_JSON_url = ''                                                    # ProxyWeb URL para gestionar JSONs


channel_bloqued_list = {"gnula.nu": "ES", "playview.io": "ES", "dilo.nu": "ES",  
                        "yts.mx": "ES", "cinetux.nu": "ES", 
                        "pelisgratis.nu": "ES", "pelisplushd.net": "ES", 
                        "cliver.to": "ES", 
                        "mejortorrent.one": "ES", "fanpelis.org": "ES", 
                        "pelisplay.co": "ES", "pelisplus.me": "ES",
                        "cuevana3.io": "ES", "api.cuevana3.io": "ES", 
                        "allpeliculas.ac": "ES", "fanpelis.ac": "ES", 
                        "allcalidad.ac": "ES", "entrepeliculasyseries.nu": "ES"
                        }
                
operator_bloqued_list = {"jazztel.ES": ("",), "telefonica.ES": ("", ""), "3352.ES": ("",),
                         "vodafone.ES": ("", ""), "12430.ES": ("",), "6739.ES": ("",), 
                         "orange.ES": ("", ""), "12479.ES": ("",), "12715.ES": ("",)
                         }
"""
https://ipinfo.io/countries/es
operator_bloqued_list = {"jazztel.ES": ("openload.co",), "telefonica.ES": ("openload.co", 
                "powvideo.net", "vidoza.net"), "vodafone.ES": ("openload.co",), 
                "15704.ES": ("seriespapaya.net",), "3352.ES": ("seriespapaya.net",)}    #Códigos ASN en vez de nombre de Operadoras
"""

# Llamadas que descargan en formato .json no están soportadas en ProxyWeb.  Deben incluir el parámetro "forced_proxy_opt='ProxyCF'" en la llamada
proxy_white_list_init = {"gnula.nu": "ProxyWeb:croxyproxy.com", "playview.io": "ProxyWeb", 
                         "yts.mx": "ProxyWeb", "cinetux.nu": "ProxyWeb", "dilo.nu": "ProxyWeb", 
                         "pelisgratis.nu": "ProxyWeb", "pelisplushd.net": "ProxyWeb", 
                         "cliver.to": "ProxyWeb:croxyproxy.com", 
                         "mejortorrent.one": "ProxyWeb", "fanpelis.org": "ProxyWeb",
                         "pelisplay.co": "ProxyWeb", "pelisplus.me": "ProxyWeb", 
                         "cuevana3.io": "ProxyWeb", "api.cuevana3.io": "ProxyWeb", 
                         "allpeliculas.ac": "ProxyWeb", "fanpelis.ac": "ProxyWeb", 
                         "allcalidad.ac": "ProxyWeb", "entrepeliculasyseries.nu": "ProxyWeb"
                         }

no_verify_proxy_list = ["gnula.nu"]

patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?[\w|\-\d]+\.(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+))(?:\/|\?|$)'
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?([\w|\-\d]+\.(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+\.?)?(?:[\w|\-\d]+))(?:\/|\?|$)'


def get_proxy_list(test=False, debugging=debugging, monitor_start=True, silence=False):

    def get_proxy_list_monitor(test, debugging, monitor_start):
        from platformcode import platformtools

        if debugging: logger.info('Entrando en Monitor :' + 
                    str(config.get_setting('alternative_web_access')))
        # Empezamos a preparar el monitor
        if config.get_platform(True)['num_version'] >= 14:          # Si es Kodi, lanzamos el monitor
            import xbmc
            monitor = xbmc.Monitor()
        else:                                                       # Si no, ponemos los valores de inicio...
            get_proxy_list_method(test=test, debugging=debugging)   # Inicializar las tablas de proxies
            return

        while not monitor.abortRequested():                         # Loop infinito hasta cancelar Kodi

            if not platformtools.is_playing():                      # Si no se está reproduciendo nada...
                get_proxy_list_method(test=test, debugging=debugging)   # ... inicializar las tablas de proxies
            
            timer = 3600 * 12                                       # 12 horas de intervalo
            if monitor.waitForAbort(timer):                         # Espera el tiempo programado o hasta que cancele Kodi
                break                                               # Cancelación de Kodi, salimos

    
    from core.httptools import downloadpage
    
    if debugging:
        alfa_s = False                                              # Httptools log verbose
        if silence: alfa_s = True
    else:
        alfa_s = True                                               # Httptools log silent

    try:
        if not config.get_setting('proxy_addr'):                    # Si es la primera vez
            if debugging: logger.error('NO proxy_addr')
            randomize_lists(debugging)                              # se aleatorizan las listas iniciales
    except:
        if debugging: logger.error('NO proxy_addr')
        randomize_lists(debugging)                                  # se aleatorizan las listas iniciales
        
    if os.path.exists(os.path.join(config.get_runtime_path(), 'channels', 'custom.py')):
        proxy_dev = 'dev'                                           # El usuario es un desarrollador
        alfa_s = False
        if silence: alfa_s = True
    else:
        proxy_dev = 'user'                                          # El usuario es un usuario estándar
    config.set_setting('proxy_dev', encrypt_proxy(proxy_dev, debugging))    # se guarda la variable de tipo de usuario
    
    if (proxy_dev == 'dev' or debugging) and not config.get_setting('debug'):
        logger.log_enable(True)

    # Verifica si los bloqueos geográficos aplican a este usuario
    proxy_channel_bloqued = {}
    proxy_geoloc = []
    proxy_geoloc.append(['https://api.ip.sb/geoip', '"country_code"', '"organization"', '"asn"'])
    proxy_geoloc.append(['https://ipinfo.io/json', '"country"', '"org"', '"org"'])
    proxy_geoloc.append(['http://ip-api.com/json/', '"countryCode"', '"as"', '"as"'])
    random.shuffle(proxy_geoloc)
    proxy_geoloc.append(['https://geoip-db.com/json/', '"country_code"', '"NONE"', '"NONE"'])   # No da la operadora
    proxy_geoloc.append(['https://ipapi.co/json', '"country"', '"org"', '"asn"'])               # Requiere CF y da error de CF_2

    try:
        data = ''
        response = {}
        country_cod = ''
        country_code = ''
        operator_cod = ''
        operator_code = ''
        asn_cod = ''
        asn_code = ''
        for web_ip, country_exp, operator_exp, asn in proxy_geoloc:
            response = downloadpage(web_ip, proxy=False, proxy_web=False,
                    alfa_s=alfa_s, timeout=30, ignore_response_code=True, CF_test=False)
            if not response.sucess:
                continue
            
            data = re.sub(r"\n|\r|\t|\s{2,}", "", response.data)
            patron = '%s:\s*"([^"]+)"' % country_exp
            country_cod = find_single_match(data, patron)
            patron = '%s:\s*"([^"]+)"' % operator_exp
            operator_cod = find_single_match(data, patron)
            patron = '%s:\s*"([^"]+)"' % asn
            asn_cod = find_single_match(data, patron)
            if not asn_cod:
                patron = '%s:\s*([^,]+),' % asn
                asn_cod = find_single_match(data, patron)
            if (proxy_dev == 'dev' and not country_cod) or debugging: 
                logger.debug('Country: ' + str(country_cod) + ' / Operator: ' 
                    + str(operator_cod)  + ' / ASN: ' + str(asn_cod)
                    + ' / R.Code: ' + str(response.code) 
                    + ' / Data: ' + str(data) + ' / Patrón: ' + patron
                    + ' / Web_ip: ' + str(web_ip))
            if country_cod:
                country_code = country_cod
                if operator_cod:
                    operator_code = operator_cod
                if asn_cod:
                    asn_code = asn_cod
                if not debugging:
                    break
    except:
        logger.error(traceback.format_exc())
    if not country_code: country_code = 'ES'
    
    if not debugging:
        data = ''

    try:
        config.set_setting('proxy_zip', encrypt_proxy('Country: ' + str(country_code) + 
                        ' / Operator: ' + str(operator_code) + ' / ASN: ' + str(asn_code) +
                        ' / R.Code: ' + str(response.code) + ' / Data: ' + str(data) + 
                        ' / Web_ip: ' + str(web_ip), debugging))    # se guarda el país para debugging
    except:
        try:
            config.set_setting('proxy_zip', encrypt_proxy('Country: ' + str(country_code) + 
                        ' / Operator: ' + str(operator_code) + ' / ASN: ' + str(asn_code) +
                        ' / R.Code: ' + str(response.code) + ' / Data: ' + 'Encode Error' + 
                        ' / Web_ip: ' + str(web_ip), debugging))    # se guarda el país para debugging
        except:
            config.set_setting('proxy_zip', encrypt_proxy('Country: ' + str(country_code) + 
                        ' / Operator: ' + 'Encode Error' + ' / ASN: ' + 'Encode Error' + 
                        ' / R.Code: ' + str(response.code) + ' / Data: ' + 'Encode Error' + 
                        ' / Web_ip: ' + str(web_ip), debugging))    # se guarda el país para debugging
    
    # Se comprueba si geográficamente han algún canal bloqueado que necesite proxy
    
    try:
        proxy_active = False
        for channel, countries in list(channel_bloqued_list.items()):
            if country_code in countries or 'ALL' in countries:
                proxy_channel_bloqued.update({channel: "ON"})           # Canal bloqueado en esa geografía
                proxy_active = True
        
        for operator_cou, channels in list(operator_bloqued_list.items()):
            op_bloqued, countries = operator_cou.split('.')
            if (op_bloqued in operator_code.lower() or op_bloqued in asn_code.lower()) and (country_code in countries or 'ALL' in countries):
                for channel in channels:
                    if channel:
                        proxy_channel_bloqued.update({channel: "ON"})   # url bloqueado en esa operadora
                        proxy_active = True
        
        for white, value in list(proxy_white_list_init.items()):
            if white in str(proxy_channel_bloqued):
                proxy_channel_bloqued.update({white: value})
        
        if proxy_channel_bloqued:                                   # Guardamos la lista de canales bloqueados
            config.set_setting('proxy_channel_bloqued', encrypt_proxy(str(proxy_channel_bloqued), debugging))
        else:
            config.set_setting('proxy_channel_bloqued', encrypt_proxy('{"proxy": "OFF"}', debugging))

        config.set_setting('proxy_active', encrypt_proxy(str(proxy_active), debugging)) # Hay algún canal activo con proxy?
    except:
        logger.error(traceback.format_exc())

    # Si no hay ningún bloqueo, o monitor, nos vamos sin hacer nada más
    if (not proxy_active and not config.get_setting('alternative_web_access')) or not monitor_start:
        randomize_lists(debugging)                                  # se aleatorizan las listas ...
        res = verify_proxy_validity(debugging)                      # Verificamos si alguna web ha dejado de necesitar Proxy
        logger_disp(debugging)                                      # Escribe en el log el estado de las tablas proxy
        return                                                      # y no se inicia el servicio
        
    # Se identifica el método de uso de Proxytools: "en Demanda": no se inicia el Servicio, "Forzado": se inicia
    if not config.get_setting('alternative_web_access'):            # Si se usa Proxytools "en demanda", ...
        randomize_lists(debugging)                                  # se aleatorizan las listas ...
        res = verify_proxy_validity(debugging)                      # Verificamos si alguna web ha dejado de necesitar Proxy
        logger_disp(debugging)                                      # Escribe en el log el estado de las tablas proxy
        return                                                      # y no se inicia el servicio
    
    # Lanzamos en Servicio de búsqueda de PROXIES
    try:
        threading.Thread(target=get_proxy_list_monitor, args=(test, debugging, 
                monitor_start)).start()                             # Creamos un Thread independiente, hasta el fin de Kodi
        time.sleep(5)                                               # Dejamos terminar la primera verificación...
    except:                                                         # Si hay problemas de threading, nos vamos
        logger.error(traceback.format_exc())

    return
    
    
def randomize_lists(debugging=False):
    
    if debugging and not config.get_setting('debug'):
        logger.log_enable(True)
    
    """
    # Borra las claves ofuscadas de Proxytools en cada nueva versión de Alfa, para evitar acumulación de claves zoombies
    try:
        from core import filetools
        if  filetools.exists(filetools.join(config.get_runtime_path(), "custom_code.json")):
            settings_path = filetools.join(config.get_data_path(), "settings.xml")
            settings = filetools.read(settings_path)
            matches = settings.split('\n')
            patron = '<setting\s*id="([^"]+)"(?:\s*default="[^"]*")?>.*?<\/setting>'
            for setting in matches:
                key = find_single_match(setting, patron)
                if len(key) > 400 or key.startswith('proxy_'):
                    settings = settings.replace(setting + '\n', '')

            res = filetools.write(settings_path, settings)
            if not res:
                raise
    except:
        logger.error(traceback.format_exc(1))
    """

    # ProxyDirect
    proxies = proxies_list[:]                                       # Copia la lista inicial
    random.shuffle(proxies)
    config.set_setting('proxy_addr', encrypt_proxy(str(proxies[0]), debugging))
    config.set_setting('proxy_list', encrypt_proxy(str(proxies), debugging))
    
    # ProxyCF
    proxies = proxies_cloudflare_list[:]                            # Copia la lista inicial
    random.shuffle(proxies)
    if not config.get_setting('proxy_CF_addr'):                     # Si ya tiene las credenciales CF, lo mantenemos
        config.set_setting('proxy_CF_addr', encrypt_proxy(str(proxies[0]), debugging))
    config.set_setting('proxy_CF_list', encrypt_proxy(str(proxies), debugging))
    
    # ProxyWeb
    config.set_setting('proxy_web_name', encrypt_proxy(random.choice(proxy_web_name_LIST), debugging))      # Guarda la web inicial
    
    # Verifica la tabla de Whitelist.  Si hay más de una alternativa por entrada, eleatoriza y salva el resultado
    proxy_white_list = proxy_white_list_init.copy()
    proxy_table = []
    
    for label_a, value_a in list(proxy_white_list.items()):
        proxy_t_s = ''
        proxy_t = proxy_white_list[label_a]
        if 'ProxyCF:' in proxy_t:
            proxy_t_s = 'ProxyCF:'
            proxy_t = proxy_t.replace('ProxyCF:', '')
        if 'ProxyWeb:' in proxy_t:
            proxy_t_s = 'ProxyWeb:'
            proxy_t = proxy_t.replace('ProxyWeb:', '')
        proxy_table = proxy_t.split(',')
        if len(proxy_table) > 1:
            random.shuffle(proxy_table)
        if proxy_t_s:
            proxy_table[0] = proxy_t_s + str(proxy_table[0])
        proxy_white_list.update({label_a: proxy_table[0]})
        
    config.set_setting('proxy_white_list', encrypt_proxy(str(proxy_white_list), debugging))
    
    if not config.get_setting('debug'):
        logger.log_enable(False)
    
    return
    

def verify_proxy_validity(debugging=False, alfa_s=True, timeout=15):

    updated = False
    proxy_channel_bloqued_str = decrypt_proxy(config.get_setting('proxy_channel_bloqued', default=''))
    if not proxy_channel_bloqued_str:
        return updated
    
    try:
        proxy_channel_bloqued = dict()
        proxy_channel_bloqued = ast.literal_eval(proxy_channel_bloqued_str)
        proxy_channel_bloqued_upd = proxy_channel_bloqued.copy()

        from core.httptools import downloadpage
        for channel, option in list(proxy_channel_bloqued.items()):
            if option in ['ProxyDirect', 'ProxyCF'] and channel not in str(no_verify_proxy_list):
                for prefix in ['http://', 'https://']:
                    response = downloadpage(prefix+channel, proxy=False, proxy_web=False,
                               alfa_s=alfa_s, timeout=timeout, ignore_response_code=True)
                    if response.sucess and not 'error 404' in response.data.lower():
                        del proxy_channel_bloqued_upd[channel]
                        updated = True
                        break
    
        if updated:
            config.set_setting('proxy_channel_bloqued', encrypt_proxy(str(proxy_channel_bloqued_upd), debugging))
    
    except:
        logger.error(traceback.format_exc())

    return updated


def get_proxy_list_method(test=False, proxy_init='Total', debugging=debugging, 
                            lote_len=4, error_skip=None, url_test=None, exp_test=None, post_test=None):

    if debugging: 
        logger.info('Test: ' + str(test) + ', Proxy_init: ' + str(proxy_init))
    from core.httptools import downloadpage
    
    if debugging:
        alfa_s = False                                              # Httptools log verbose
    else:
        alfa_s = True                                               # Httptools log silent
    try:
        proxy_dev = decrypt_proxy(config.get_setting('proxy_dev'))
    except:
        proxy_dev = 'user'
        config.set_setting('proxy_dev', encrypt_proxy(proxy_dev, debugging))    # se guarda la variable de tipo de usuario
    if proxy_dev == 'dev': alfa_s = False
    proxies_save = []
    proxy_addr = ''
    proxy_list = []
    proxy_list_rep = []
    proxy_list_salen = []
    proxy_CF_addr = ''
    proxy_CF_list = []
    proxy_list_CF_rep = []
    proxy_list_CF_salen = []
    proxy_web_name = ''
    max_valid_proxies = 50
    if proxy_init == 'Total':
        lote_len = int(lote_len * 2)
    else:
        lote_len = int(lote_len / 2)
    
    #country_list = ['SG', 'IN', 'CN']
    country_list = []
    country_list = ['ALL']

    proxy_post_test = post_test
    #proxy_url_test = 'http://www.mejortorrent.com/torrents-de-peliculas.html'
    #proxy_pattern_test = '<a href="((?:[^"]+)?/peli-descargar-torrent[^"]+)">?'
    #proxy_url_test = 'http://seriesdanko.to/'
    #proxy_pattern_test = "<div class='widget HTML' id='HTML3'.+?<div class='widget-content'>(.*?)</div>"
    #proxy_url_test = 'https://www.todo-peliculas.net/torrents'
    proxy_url_test = ''
    proxy_pattern_test = '<div class="blogitem "><a title="([^"]+)"\s+href="([^"]+)">.*?src="([^"]+)" onload'
    if url_test and (proxy_init == 'ProxyDirect' or proxy_init == 'ProxyWeb'):
        if find_single_match(url_test, '(http.?\:\/\/(?:www.)?.*?\.\w+(?:\.\w+)?\/)') != find_single_match(proxy_url_test, '(http.?\:\/\/(?:www.)?.*?\.\w+(?:\.\w+)?\/)'):
            proxy_url_test = url_test
            proxy_pattern_test = ''
            if exp_test:
                proxy_pattern_test = exp_test

    #proxy_CF_url_test = 'http://gnula.nu/peliculas-online/lista-de-peliculas-online-parte-1/'
    #proxy_CF_url_test = 'http://gnula.nu/generos/lista-de-peliculas-del-genero-aventuras/'
    #proxy_CF_pattern_test = '<a class="Ntooltip" href="([^"]+)">([^<]+)<span><br[^<]+'
    #proxy_CF_pattern_test += '<img src="([^"]+)"></span></a>(.*?)<br'
    #proxy_CF_url_test = 'https://animeflv.net/'
    #proxy_CF_pattern_test = ''
    #proxy_CF_url_test = 'https://www2.seriespapaya.nu/'
    #proxy_CF_pattern_test = '<h2>Series Nuevas</h2>'
    proxy_CF_url_test = 'https://pelisplushd.net/pelicula/viuda-negra'
    proxy_CF_pattern_test = "video\[\d+\]\s*=\s*'([^']+)'"
    cf_v2 = False
    CF = False
    if url_test and proxy_init == 'ProxyCF':
        if find_single_match(url_test, '(http.?\:\/\/(?:www.)?.*?\.\w+(?:\.\w+)?\/)') != find_single_match(proxy_CF_url_test, '(http.?\:\/\/(?:www.)?.*?\.\w+(?:\.\w+)?\/)'):
            proxy_CF_url_test = url_test
            proxy_CF_pattern_test = ''
            if exp_test:
                proxy_CF_pattern_test = exp_test

    #Aleatoriza todas las listas
    randomize_lists(debugging)
    
    # Valores iniciales por defecto para ProxyDirect
    proxies = []
    proxies_str = decrypt_proxy(config.get_setting('proxy_list'))
    proxies = ast.literal_eval(proxies_str)
    proxies_init = proxies[:]
    
    #Listas de direcciones proxy: desde Custom.py ejecutar "Reiniciar Servicio Proxy, 
    #Test de Todas las Direcciones".  Salvar a las variables definitivas las direcciones 
    #que han pasado los tests

    #Analiza el resultado de las webs de listas de proxies
    if proxy_dev == 'dev' or debugging: logger.debug('Tabla inicial ProxyDirect: ' + 
                str(proxies))
    if proxy_dev == 'dev' or debugging: logger.debug('Tabla inicial ProxyCF: ' + 
                str(decrypt_proxy(config.get_setting('proxy_CF_list'))))
    
    if proxy_init == 'Total':
        timeout = 15                                                            # si es un reinicio manual de damos más tiempo
    else:
        timeout = 10                                                            # si es una recuperación on-line, ajustamos
    
    if proxy_init == 'Total' or proxy_init == 'ProxyDirect':
        matches = []

        for country in country_list:
            try:
                #Página www.proxy-list.download
                if country == 'ALL':
                    url_list = 'https://www.proxy-list.download/api/v1/get?type=https&anon=elite'
                    #url_list = 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=2000&country=all&ssl=yes&anonymity=elite&simplified=true'  'https://proxysource.org/api/proxies/getWorkingProxies?apiToken=1791413ffa4d436f35175d41c84b9119423&latencyMax=2000&latencyMin=0&outputMode=plaintext&uptimeMax=100&uptimeMin=95'          # https://hidemy.name/es/proxy-checker/        https://proxyscrape.com/online-proxy-checker
                else:
                    url_list = 'https://www.proxy-list.download/api/v1/get?type=https&anon=elite&country=%s' % country
                data = ''
                response = downloadpage(url_list, proxy=False, proxy_web=False, proxy_retries=0, 
                        count_retries_tot=2, timeout=timeout, random_headers=True, ignore_response_code=True)
                if not response.sucess:
                    continue
                
                if response.data:
                    data = re.sub(r'\r|\t|&nbsp;|<br>|\s{2,}', "", response.data)
                    data = "'" + re.sub(r'\n', "', '", data)
                    if data.endswith(", '"):
                        data = data[:-3]
                    if not data.endswith("'"):
                        data += "'"
                    matches = []
                    matches = ast.literal_eval(data)

                    for var_a in matches:
                        proxy_a = var_a
                        if proxy_a and proxy_a not in proxies:
                            proxies.append(proxy_a)
            except:
                logger.error(traceback.format_exc())
            if proxy_dev == 'dev' or debugging: logger.debug('Tabla proxy-list.download ' + 
                        country + ': ' + str(matches))


    #Si test=True analiza el resultado de las webs de listas de proxies y verifica cada uno
    if test:
        data = ''
        """
        #Página HideMy.name
        try:
            data = ''
            data = downloadpage('https://hidemyna.me/en/proxy-list/?country=HKNLSG&maxtime=1000&type=s&anon=4#list', 
                    proxy=True, proxy_web=False, proxy_retries=1, count_retries_tot=2, 
                    timeout=timeout, random_headers=True, forced_proxy='ProxyCF').data
        except:
            logger.error(traceback.format_exc())

        if data:
            data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
            patron = "<td class=tdl>(.*?)<\/td><td>(.*?)<\/td>"
            
            matches = re.compile(patron, re.DOTALL).findall(data)
            
            for var_a, var_c in matches:
                proxy_a = '%s:%s' % (var_a, var_c)
                if proxy_a not in proxies:
                    proxies.append(proxy_a)
            
            if proxy_dev == 'dev' or debugging: 
                logger.debug('Tabla HideMy.name: ' + str(matches))
        """
        
        #Página ProxyDB.  Inactiva por ser muy inestable y por no devolver ningún proxy válido
        """
        try:
            data = ''
            data = downloadpage('http://proxydb.net/?protocol=https&anonlvl=4&min_uptime=95&max_response_time=1&exclude_gateway=1&country=', 
                    proxy=False, proxy_web=False, proxy_retries=0, count_retries_tot=2, 
                    random_headers=True, timeout=timeout).data
        except:
            logger.error(traceback.format_exc())

        if data:
            data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
            patron = "var\w ='([^']+)'.*?var \w{3} =.*?atob\('([^']+)'.*?varpp =\((\d+)"

            matches = re.compile(patron, re.DOTALL).findall(data)

            for var_a, var_b, var_c in matches:
                decoded = ''
                var_a = var_a[::-1]
                var_b = var_b.split('\\x')
                for i in var_b:
                    #decoded += (i.decode('hex'))
                    decoded = codecs.decode(i, "hex")
                    if PY3 and isinstance(decoded, bytes):
                        decoded = decoded.decode("utf8")
                decoded = base64.b64decode(decoded)
                var_c = int(var_c) + 3
                proxy_a = '%s%s:%s' % (var_a, decoded, var_c)
                if proxy_a not in proxies:
                    proxies.append(proxy_a)
                    
            if proxy_dev == 'dev' or debugging: 
                        logger.debug('Tabla ProxyDB: ' + str(matches))
        """

    if proxy_init == 'Total' or proxy_init == 'ProxyDirect' and (proxy_dev == 'dev' or debugging):
        logger.debug('Tabla ANTES del testing: ' + str(proxies))

    #Verificando la validez de los proxies listados.  Si Test=True, verificará todos, 
    #si Test=False (defecto) tomará el primero válido
    if error_skip and error_skip in proxies: proxies.remove(error_skip)
    if (proxy_init == 'Total' or proxy_init == 'ProxyDirect') and proxy_url_test:
        if proxy_dev == 'dev' or debugging:
            logger.debug('INIT ProxyDirect: ' + proxy_init)
        threads_list = []
        proxy_que = queue.Queue()
        full = False

        for proxy_lote in range(0, len(proxies), lote_len):
            if (proxy_addr and not test) or full:
                break

            for proxy_a in proxies[proxy_lote:proxy_lote + lote_len]:
                if proxy_a in proxy_list:
                    continue
                try:
                    config.set_setting('proxy_addr', encrypt_proxy(str(proxy_a), debugging))
                    proxy_thread = threading.Thread(target=test_proxy_addr, 
                            args=(proxy_a, proxy_url_test, proxy_pattern_test, proxy_post_test, 
                            True, False, 'ProxyDirect', 0, 1, timeout, alfa_s, 
                            proxy_que, test, debugging, False, cf_v2))
                    proxy_thread.daemon = True
                    proxy_thread.start()
                    threads_list.append(proxy_thread)
                except:
                    logger.error(traceback.format_exc())
                
            while [thread_x for thread_x in threads_list if thread_x.is_alive()]:
                try:
                    proxy_addr = proxy_que.get(True, 1)
                    proxy_list.append(proxy_addr)
                    config.set_setting('proxy_addr', encrypt_proxy(str(proxy_addr), debugging))
                    if not test:
                        proxy_list = proxies_init
                        break
                    if proxy_addr in proxies_init:
                        proxy_list_rep.append(proxy_addr)
                    if len(proxy_list) >= max_valid_proxies:
                        full = True
                        break
                except queue.Empty:
                    proxy_addr = ''

        if not proxy_addr and len(proxy_list) > 0:
            proxy_addr = proxy_list[-1]
        if not proxy_addr and proxy_init == 'Total':
            proxy_addr = proxies_list[0]
        if test:
            for addr in proxies_init:
                if addr not in proxy_list:
                    proxy_list_salen.append(addr)
            
        config.set_setting('proxy_addr', encrypt_proxy(str(proxy_addr), debugging))
        config.set_setting('proxy_list', encrypt_proxy(str(proxy_list), debugging))
        if proxy_dev == 'dev' or debugging:
            logger.info('ProxyDirect addr: ' + str(proxy_addr))

    # Valores iniciales por defecto para Proxy Cloudflare
    if (proxy_init == 'Total' or proxy_init == 'ProxyCF') and proxy_CF_url_test:
        if proxy_dev == 'dev' or debugging:
            logger.debug('INIT ProxyCF: ' + proxy_init)
        proxies_str = decrypt_proxy(config.get_setting('proxy_CF_list'))
        proxies_cf = ast.literal_eval(proxies_str)
        proxies_init = proxies_cf[:]

        if proxy_init == 'Total' and (proxy_dev == 'dev' or debugging):         #Añadimos también los Proxy Direct
            proxies_cf.extend(proxies)
        elif proxy_init == 'Total':
            proxies_cf.extend(proxy_list)                                       #Sólo los validados previamente
        
        #Verificando la validez de los proxies CF listados.  Si Test=True, 
        #verificará todos, si Test=False (defecto) tomará el primero válido
        threads_list_CF = []
        proxy_que_CF = queue.Queue()
        #lote_len = 2

        for proxy_lote in range(0, len(proxies_cf), lote_len):

            if proxy_CF_addr and not test:
                break

            for proxy_a in proxies_cf[proxy_lote:proxy_lote + lote_len]:
                if proxy_a in proxy_CF_list:
                    continue
                try:
                    config.set_setting('proxy_CF_addr', encrypt_proxy(str(proxy_a), debugging))
                    proxy_thread = threading.Thread(target=test_proxy_addr, 
                            args=(proxy_a, proxy_CF_url_test, proxy_CF_pattern_test, proxy_post_test, 
                            True, False, 'ProxyCF', 0, 1, timeout, alfa_s, proxy_que_CF, 
                            test, debugging, CF, cf_v2))
                    proxy_thread.daemon = True
                    proxy_thread.start()
                    threads_list_CF.append(proxy_thread)
                except:
                    logger.error(traceback.format_exc())
                
            while [thread_x for thread_x in threads_list_CF if thread_x.is_alive()]:
                try:
                    proxy_CF_addr = proxy_que_CF.get(True, 1)
                    proxy_CF_list.append(proxy_CF_addr)
                    config.set_setting('proxy_CF_addr', encrypt_proxy(str(proxy_CF_addr), debugging))
                    if not test:
                        proxy_CF_list = proxies_init
                        break
                    if proxy_CF_addr in proxies_init:
                        proxy_list_CF_rep.append(proxy_CF_addr)
                except queue.Empty:
                    proxy_CF_addr = ''

        if not proxy_CF_addr and len(proxy_CF_list) > 0:
            proxy_CF_addr = proxy_CF_list[-1]
        if not proxy_CF_addr:
            proxy_CF_addr = proxies_cloudflare_list[0]
        if test:
            for addr in proxies_init:
                if addr not in proxy_CF_list:
                    proxy_list_CF_salen.append(addr)
            
        config.set_setting('proxy_CF_addr', encrypt_proxy(str(proxy_CF_addr), debugging))
        config.set_setting('proxy_CF_list', encrypt_proxy(str(proxy_CF_list), debugging))
        if proxy_dev == 'dev' or debugging:
            logger.info('ProxyCF addr: ' + str(proxy_CF_addr))

    # Verificación de los Proxy Webs.  Si Test=True, verificará todos, si Test=False (defecto) tomará el primero válido
    proxy_table = []
    if (proxy_init == 'Total' or proxy_init == 'ProxyWeb') and proxy_url_test:
        if proxy_dev == 'dev' or debugging:
            logger.debug('INIT ProxyWeb: ' + proxy_init)
        
        for label_a, value_a in list(proxy_web_list.items()):
            if error_skip and label_a == error_skip:
                continue
            """
            if label_a not in str(proxy_web_name_POST):
                continue
            """
            proxy_table.append(label_a)
        random.shuffle(proxy_table)
        #proxy_table = sorted(proxy_table)
        
        for label_a in proxy_table:
            proxy_web_name = label_a
            config.set_setting('proxy_web_name', encrypt_proxy(str(proxy_web_name), debugging))
            try:
                data = ''
                response = downloadpage(proxy_url_test, proxy=False, 
                        proxy_web=True, forced_proxy='ProxyWeb', proxy_retries=0, 
                        count_retries_tot=1, timeout=timeout, alfa_s=alfa_s, 
                        ignore_response_code=True)
            except:
                logger.error(traceback.format_exc())
                proxy_web_name = ''
                continue
            if not response.sucess:
                continue

            if response.data:
                data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", response.data)
                if proxy_pattern_test:
                    data_test = find_single_match(data, proxy_pattern_test)
                    if not data_test:
                        if proxy_dev == 'dev' or debugging:
                            logger.error('ProxyWeb error: ' + proxy_web_name + ' / ' 
                                        + proxy_pattern_test + ' / ' + data)
                        proxy_web_name = ''
                        continue
                    else:
                        if not test:
                            break
                else:
                    break
            else:
                proxy_web_name = ''

        if not proxy_web_name and proxy_init == 'Total':
            config.set_setting('proxy_web_name', encrypt_proxy(random.choice(proxy_web_name_LIST), debugging))
        elif not proxy_web_name and proxy_init != 'Total':
            config.set_setting('proxy_web_name', encrypt_proxy('', debugging))

    proxy_vars = logger_disp(debugging, test, proxy_list_rep, proxy_list_CF_rep, 
                             proxy_list_salen, proxy_list_CF_salen)

    return


def test_proxy_addr(proxy_addr, proxy_url_test, proxy_pattern_test, proxy_post_test, proxy, 
                    proxy_web, forced_proxy, proxy_retries, count_retries_tot, 
                    timeout, alfa_s, proxy_que, test, debugging, CF, cf_v2):
    
    #Realizamos el test de cada Proxy IP que nos pasan.
    from core.httptools import downloadpage

    header = find_single_match(proxy_url_test, '(http.*):\/\/')
    if not header: header = 'http'
    proxy_a = {header:proxy_addr}

    try:
        data = ''
        response = downloadpage(proxy_url_test, proxy=proxy, proxy_web=proxy_web, 
                forced_proxy=forced_proxy, proxy_addr_forced=proxy_a, post=proxy_post_test, 
                proxy_retries=proxy_retries, count_retries_tot=count_retries_tot, 
                timeout=timeout, alfa_s=alfa_s, ignore_response_code=True, CF=CF, cf_v2=cf_v2)
        data = response.data
    except:
        logger.error(traceback.format_exc())
        return ''
    if not response.sucess:
        return ''
    
    #Si la Proxy IP es buena se acumula en una Queue que gestiona el llamador
    if data:
        if proxy_pattern_test:                                          #Si hay patron, se analizan los datos
            data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
            data_test = find_single_match(data, proxy_pattern_test)
            if data_test: 
                if isinstance(proxy_que, queue.Queue):                  #Si la cola esta activa...
                    proxy_que.put(proxy_addr)                           #... se acumula la IP
            else:
                proxy_addr = ''
        else:                                                           #Si no hay patrón, se da la IP por buena
            if isinstance(proxy_que, queue.Queue):                      #Si la cola esta activa...
                proxy_que.put(proxy_addr)                               #... se acumula la IP
    else:
        proxy_addr = ''

    return proxy_addr                                       #Se devuelve la IP por si la llamada no viene de un Thread
    
    
def logger_disp(debugging=False, test=False, proxy_list_rep=[], proxy_list_CF_rep=[], 
                proxy_list_salen=[], proxy_list_CF_salen=[]):
    
    try:
        proxy_vars = {}
        
        proxy_dev = decrypt_proxy(config.get_setting('proxy_dev'))
        if (proxy_dev == 'dev' or debugging) and not config.get_setting('debug'):
            logger.log_enable(True)
        
        # Mostramos los resultados solo para desarrolladores en abierto y en base64.b64encode(data.encode('utf-8')) para usuarios
        proxy_vars['proxy__active'] = decrypt_proxy(config.get_setting('proxy_active'))
        proxy_vars['proxy__alter'] = str(config.get_setting('alternative_web_access'))
        proxy_vars['proxy__channel__country'] = str(channel_bloqued_list) + str(operator_bloqued_list)
        proxy_channel_bloqued_str = decrypt_proxy(config.get_setting('proxy_channel_bloqued'))
        proxy_vars['proxy__channel_bloqued'] = ast.literal_eval(proxy_channel_bloqued_str)
        proxy_white_list_str = decrypt_proxy(config.get_setting('proxy_white_list'))
        proxy_vars['proxy__channel_white_list'] = ast.literal_eval(proxy_white_list_str)
        proxy_vars['proxy_cf_addr'] = decrypt_proxy(config.get_setting('proxy_CF_addr'))
        proxy_vars['proxy_cf_list'] = decrypt_proxy(config.get_setting('proxy_CF_list'))
        proxy_vars['proxy_cf_rep'] = proxy_list_CF_rep
        proxy_vars['proxy_cf_salen'] = proxy_list_CF_salen
        proxy_vars['proxy_normal_addr'] = decrypt_proxy(config.get_setting('proxy_addr'))
        proxy_vars['proxy_normal_list'] = decrypt_proxy(config.get_setting('proxy_list'))
        proxy_vars['proxy_normal_rep'] = proxy_list_rep
        proxy_vars['proxy_normal_salen'] = proxy_list_salen
        proxy_vars['proxy_web__addr'] = decrypt_proxy(config.get_setting('proxy_web_name'))
        proxy_vars['proxy_web__list'] = sorted(proxy_web_list.items())
        proxy_vars['proxy_web__post'] = proxy_web_name_POST
        proxy_vars['proxy_zip'] = decrypt_proxy(config.get_setting('proxy_zip'))

        if proxy_dev == 'dev':
            logger.info('Alternative_web_access: ' + str(proxy_vars['proxy__alter']) + 
                    ' / Proxy Activo: ' + str(proxy_vars['proxy__active']) + 
                    ' / PROXY Lists: ProxyDirect: ' + str(proxy_vars['proxy_normal_addr']) + 
                    ' / ProxyDirect Pool: ' + str(proxy_vars['proxy_normal_list']) + ' / ProxyCF: ' + 
                    str(proxy_vars['proxy_cf_addr']) + ' / ProxyCF Pool: ' + 
                    str(proxy_vars['proxy_cf_list']) + ' / ProxyWeb: ' + 
                    str(proxy_vars['proxy_web__addr']) + ' / Proxy Whitelist: ' + 
                    str(proxy_vars['proxy__channel_white_list']) + ' / Bloqued Counties: ' + 
                    str(proxy_vars['proxy__channel__country']) + ' / Bloqued Channels: ' + 
                    str(proxy_vars['proxy__channel_bloqued']) + ' / ' + str(proxy_vars['proxy_zip']))
        else:
            logger.info(str(encrypt_proxy(encrypt_proxy(encrypt_proxy(encrypt_proxy(encrypt_proxy(
                    'Alternative_web_access: ' + 
                    str(proxy_vars['proxy__alter']) + ' / Proxy Activo: ' + 
                    str(proxy_vars['proxy__active']) + ' / PROXY Lists: ProxyDirect: ' + 
                    str(proxy_vars['proxy_normal_addr']) + ' / ProxyDirect Pool: ' + 
                    str(proxy_vars['proxy_normal_list']) + ' / ProxyCF: ' + 
                    str(proxy_vars['proxy_cf_addr']) + ' / ProxyCF Pool: ' + 
                    str(proxy_vars['proxy_cf_list']) + ' / ProxyWeb: ' + 
                    str(proxy_vars['proxy_web__addr']) + ' / Proxy Whitelist: ' + 
                    str(proxy_vars['proxy__channel_white_list']) + ' / Bloqued Counties: ' + 
                    str(proxy_vars['proxy__channel__country']) + ' / Bloqued Channels: ' + 
                    str(proxy_vars['proxy__channel_bloqued']) + ' / ' + str(proxy_vars['proxy_zip']))))))))
            
        if proxy_dev == 'dev' and test:
            logger.info('PROXY Lists REPITEN: ProxyDirect: ' + str(proxy_vars['proxy_normal_rep']) + 
                    ' / PROXY Lists REPITEN: ProxyCF: ' + str(proxy_vars['proxy_cf_rep']))
            logger.info('PROXY Lists SALEN: ProxyDirect: ' + str(proxy_vars['proxy_normal_salen']) + 
                    ' / PROXY Lists SALEN: ProxyCF: ' + str(proxy_vars['proxy_cf_salen']))
        
        if not config.get_setting('debug'):
            logger.log_enable(False)
        
        if proxy_dev != 'dev' and not debugging: proxy_vars = {}
    
    except:
        logger.error(traceback.format_exc())
    
    return proxy_vars
    

def set_proxy_web(url, proxy_data, **opt):
    global proxy_web_name_JSON_url
    
    post = opt.get('post', None)
    forced_proxy_opt = opt.get('forced_proxy_opt', False)
    headers = opt.get('headers', {})
    json_type = True if forced_proxy_opt == 'ProxyJSON' else False
    proxy_web_name = proxy_data.get('web_name', '')
    force_proxy_get = opt.get('force_proxy_get', False)

    proxy_site_url_post = proxy_web_list[proxy_web_name][0]
    proxy_site_url_get = proxy_web_list[proxy_web_name][1] + proxy_web_list[proxy_web_name][3]
    proxy_site_referer = proxy_web_list[proxy_web_name][2]
    if proxy_site_referer:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Referer'] = proxy_site_referer
        headers['X-Requested-With'] = 'XMLHttpRequest'
    proxy_site_header = proxy_web_list[proxy_web_name][3]
    proxy_site_h_tail = proxy_web_list[proxy_web_name][4]
    proxy_site_tail = proxy_web_list[proxy_web_name][5]
    proxy_site_post = proxy_web_list[proxy_web_name][6]
    proxy_site_init = proxy_web_list[proxy_web_name][7]
    proxy_site_init_headers = proxy_web_list[proxy_web_name][8]
    proxy_site_init_post = proxy_web_list[proxy_web_name][9]
    payload = {}

    if debugging:
        logger.info('PROXY POST: ' + proxy_site_url_post + ' / GET: ' + proxy_site_url_get)
    if post and proxy_web_name not in str(proxy_web_name_POST):
        proxy_web_name = random.choice(proxy_web_name_POST)
    if json_type and proxy_web_name not in proxy_web_name_JSON:
        proxy_web_name = random.choice(proxy_web_name_JSON)
        
    if proxy_web_name:
        if json_type or proxy_web_name in proxy_web_name_JSON:
            host = find_single_match(url, patron_host)
            host_quoted = urllib.quote_plus(host)
            if not proxy_web_name_JSON_url:
                from core.httptools import downloadpage
                try:
                    if proxy_web_name in ['croxyproxy.com']:
                        #server_list = [16, 17, 18, 19, 23, 24, 28, 31, 34, 36, 37, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 56]
                        server_list = [23, 24, 28, 31]                          # Con CF=True
                        req = {}
                        code = ''
                        for server_id in random.sample(server_list, len(server_list)):
                            proxy_site_init_post = proxy_web_list[proxy_web_name][9] % (host_quoted, server_id)
                            req = downloadpage(proxy_site_init, post=proxy_site_init_post, 
                                        headers=proxy_site_init_headers, timeout=3, alfa_s=True, ignore_response_code=True, 
                                        proxy=False, proxy_web=False, proxy_retries=0, count_retries_tot=1)
                            code = req.code
                            if code not in [200]: continue
                            break
                    
                        if req and req.headers.get('access-control-allow-origin', ''):
                            proxy_web_name_JSON_url = req.headers['access-control-allow-origin']
                except:
                    logger.error(url + ' / ' + str(post) + ' / ' + str(headers) + ' / ' + proxy_web_name + ' / ' + str(code))
                    return (url, post, headers, '')
                    
            if proxy_web_name_JSON_url:
                separator = '?' if not '?' in url else '&'
                url = url.replace(host, proxy_web_name_JSON_url) + '%s__cpo=%s' % (separator, encrypt_proxy(host))

        else:
            url = urllib.quote_plus(url)
            if post or force_proxy_get:
                url = proxy_site_url_get + url
                tail = proxy_site_h_tail.split('|')
                for tail_item in tail:
                    if '&amp;' in tail_item: continue
                    url += tail_item
            else:
                post = proxy_site_post % url
                post = post.replace('[', '%5B').replace(']', '%5D')
                url = proxy_site_url_post
    
    if debugging:
        logger.debug(url + ' / ' + post + ' / ' + headers + ' / ' + proxy_web_name)
    return (url, post, headers, proxy_web_name)

        
def restore_after_proxy_web(response, proxy_data, url):

    resp = response.copy()
    data = resp['data']
    headers = resp['headers']
    json_data = resp.get('json', {})
    proxy_web_name = proxy_data['web_name']
    proxy_site_header = proxy_web_list[proxy_web_name][3]
    proxy_site_tail = proxy_web_list[proxy_web_name][5]
    
    if 'Hotlinking directly to proxied pages is not permitted.' in data or '<h3>Something is wrong</h3>' in data:
        resp['data'] = 'ERROR'                                                  #Hay que iniciar ProxyWeb
        return resp

    try:
        if headers.get('location', '') and '?__cpo=' in headers['location'] and '#' in headers['location']:
            location_domain, location_url = find_single_match(headers['location'], '(.*?)\?__cpo=(.*?$)')
            host_location = find_single_match(location_domain, patron_host)
            location_url = location_url.split('#')
            if location_domain and location_url:
                host = decrypt_proxy(location_url[0])
                location_domain = location_domain.replace(host_location, host)
                headers['location'] = '%s#%s' % (location_domain, location_url[1])
        elif headers.get('location', ''):
            host = find_single_match(url, patron_host)
            if headers.get('location', '') and '?__cpo=' in headers['location'] and not '#' in headers['location']:
                host = decrypt_proxy(find_single_match(headers['location'], '\?__cpo=(.*?)(?:$|&)'))
            host_location = find_single_match(headers['location'], patron_host)
            if host and host_location:
                headers['location'] = headers['location'].replace(host_location, host)
                headers['location'] = re.sub('(.__cpo=.*?)(?:$|&)', '', headers['location'])
    except:
        logger.error(traceback.format_exc())

    if not json_data and '[{' in data and '}]' in data:                         # Si Requests no convierte el json, lo intentamos...
        json_data = find_single_match(data, '\[\{[^\]]+\}\]')
        try:
            resp['json'] = json.loads(json_data)
        except:
            pass
    
    if not find_single_match(data, '^d\d+:.*?\d+:') and not data.startswith("PK"):     #NO .torrent ni PKZIP
        data = urllib.unquote(data)
        proxy_site_table = proxy_site_header.split('|')
        for proxy_header in proxy_site_table:
            data = data.replace(proxy_header, '')
        proxy_site_table = proxy_site_tail.split('|')
        for proxy_tail in proxy_site_table:
            data = re.sub(proxy_tail, '', data)
        data = data.replace('href="%smagnet:?' % url, 'href="magnet:?')
        data = data.replace("href='%smagnet:?" % url, "href='magnet:?")
        data = data.replace("&amp;f=frame", "")

        # Retiramos los tags "parseURL('https:...')" dejando las urls limpias
        patron = '(parseURL\(([^\)]+)\))'
        if find_single_match(data, patron):
            matches = re.compile(patron, re.DOTALL).findall(data)
            for url_total, url_limpia in matches:
                data = data.replace(url_total, url_limpia)

    domain = find_single_match(url, patron_domain)
    if proxy_data.get('proxy__test', '') == 'retry':
        if resp['code'] == 200:
            add_domain_retried(domain)
        else:
            add_domain_retried(domain, proxy__type='ProxyCF')
        
    resp['data'] = data
    resp['headers'] = headers
    
    return resp


def add_domain_retried(domains, proxy__type='ProxyWeb', delete=False):
    
    if domains:
        if not isinstance(domains, list):
            domains = [domains]
        proxy_channel_bloqued_str = decrypt_proxy(config.get_setting('proxy_channel_bloqued'))
        proxy_channel_bloqued = dict()
        if proxy_channel_bloqued_str:
            proxy_channel_bloqued = ast.literal_eval(proxy_channel_bloqued_str)
        
        for domain in domains:
            if not domain: continue
            if 'forced' in str(delete):
                proxy_channel_bloqued.pop(domain, '')
            elif delete and domain not in proxy_white_list_init:
                proxy_channel_bloqued.pop(domain, '')
            else:
                if proxy__type == 'ProxyWeb':
                    proxy_channel_bloqued[domain] = '%s:%s' % (proxy__type, proxy_web_name_JSON[0] or proxy_web_name_POST[0])
                else:
                    proxy_channel_bloqued[domain] = proxy__type
        config.set_setting('proxy_channel_bloqued', encrypt_proxy(str(proxy_channel_bloqued), debugging))


def channel_proxy_list(url, forced_proxy=None):
    
    proxy_channel_bloqued_str = decrypt_proxy(config.get_setting('proxy_channel_bloqued'))
    proxy_channel_bloqued = dict()
    if proxy_channel_bloqued_str:
        proxy_channel_bloqued = ast.literal_eval(proxy_channel_bloqued_str)
    
    if not url.endswith('/'):
        url += '/'
    if find_single_match(url, patron_domain) in proxy_channel_bloqued:
        if forced_proxy:
            return True
        if 'ON' in proxy_channel_bloqued[find_single_match(url, patron_domain)]:
            if debugging: 
                logger.debug(find_single_match(url, patron_domain))
            return True
    
    return False
    

def get_proxy_addr(url, forced_proxy_m=None, **opt):

    forced_proxy = forced_proxy_m or opt.get('forced_proxy', None)
    post = opt.get('post', None)
    forced_proxy_opt = opt.get('forced_proxy_opt', '')
    proxy_a = ''
    proxy_CF_a = ''
    proxy_white_list_str = ''
    proxy_w = False
    proxy_log = ''
    header = 'http'
    domain = ''
    url_f = url
    
    proxy_a = decrypt_proxy(config.get_setting('proxy_addr'))
    proxy_CF_a = decrypt_proxy(config.get_setting('proxy_CF_addr'))
    #proxy_white_list_str = decrypt_proxy(config.get_setting('proxy_white_list'))
    proxy_white_list_str = decrypt_proxy(config.get_setting('proxy_channel_bloqued'))
    if post and forced_proxy_opt != 'ProxyJSON':
        proxy_web_name = random.choice(proxy_web_name_POST)
    elif forced_proxy_opt == 'ProxyJSON':
        proxy_web_name = random.choice(proxy_web_name_JSON)
    else:
        proxy_web_name = random.choice(proxy_web_name_LIST)
    proxy_dev = decrypt_proxy(config.get_setting('proxy_dev'))
    
    header = str(find_single_match(url_f, '(http.*):\/\/'))
    if not url_f.endswith('/'):
        url_f += '/'
    domain = find_single_match(url_f, patron_domain)
    
    if domain and proxy_white_list_str and not forced_proxy:
        if domain in proxy_white_list_str:
            proxy_w = True
            proxy_white_list = dict()
            proxy_white_list = ast.literal_eval(proxy_white_list_str)
            if 'ProxyWeb' in proxy_white_list.get(domain, ''):
                proxy_a = ''
                proxy_CF_a = ''
                if ':' in proxy_white_list.get(domain, ''):
                    proxy_web_name = proxy_white_list[domain].replace('ProxyWeb:', '')
            elif 'ProxyCF' in proxy_white_list.get(domain, ''):
                proxy_a = ''
                proxy_web_name = ''
                if ':' in proxy_white_list.get(domain, ''):
                    proxy_CF_a = proxy_white_list[domain].replace('ProxyCF:', '')
            else:
                proxy_a = proxy_white_list.get(domain, '')
                proxy_CF_a = ''
                proxy_web_name = ''
    
    if forced_proxy:
        if forced_proxy == 'Total':
            pass
        elif forced_proxy == 'ProxyCF':
            proxy_a = ''
            proxy_web_name = ''
        elif 'ProxyWeb' in forced_proxy:
            proxy_a = ''
            proxy_CF_a = ''
            if ':' in forced_proxy:
                proxy_web_name = forced_proxy.split(':')[1]
        else:
            proxy_CF_a = ''
            proxy_web_name = ''
    elif not proxy_w:
        proxy_CF_a = ''
        proxy_web_name = ''

    if proxy_web_name:
        proxy_log = url
    if proxy_CF_a:
        proxy_log = proxy_CF_a
        proxy_CF_a = {header:str(proxy_CF_a)}
    if proxy_a:
        proxy_log = proxy_a
        proxy_a = {header:str(proxy_a)}
    if not proxy_a and not proxy_CF_a and not proxy_web_name:
        proxy_CF_a = decrypt_proxy(config.get_setting('proxy_CF_addr'))
        proxy_a = ''
        proxy_web_name = ''
        if proxy_CF_a:
            proxy_log = proxy_CF_a
            proxy_CF_a = {header:str(proxy_CF_a)}
        else:
            proxy_CF_a = ''
    if proxy_dev != 'dev':
        proxy_log = ''
    
    if debugging: 
        logger.debug('Proxy: ' + str(proxy_a) + ' / Proxy CF: ' + str(proxy_CF_a) + 
                ' / ProxyWeb: ' + str(proxy_web_name) + ' / ProxyLog: ' + str(proxy_log))
    return (proxy_a, proxy_CF_a, proxy_web_name, proxy_log)

    
def encrypt_proxy(data, debugging=False):
    if debugging: logger.debug('Before: ' + str(data))
        
    if data:
        data = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    
    if debugging: logger.debug('After: ' + str(data))
    return data
    
    
def decrypt_proxy(data, debugging=False):
    if debugging: logger.debug('Before: ' + str(data))
        
    if data:
        data_new = data
        for x in range(4):
            try:
                data_new = base64.b64decode(data_new).decode('utf-8')
                data = data_new
                break
            except:
                data_new = data_new + '='                               # Padding

    if debugging: logger.debug('After: ' + str(data))
    return data
