# -*- coding: utf-8 -*-
# -*- Channel PelisVips -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import inspect

from platformcode import logger

players = {'play': 'https://zplayer.live', 
           'stp': 'https://streamtape.com',
           'vipstream': 'https://upstream.to', 
           'stape': 'https://streamtape.com',
           'stream': 'https://streamtape.com',
           'streamtape': 'https://streamtape.com',
           'netu': 'https://waaw.to',
           'netu_pelisvips': 'https://hqq.to',
           'pelisvips': 'https://pelisvips.com',
           'up': 'https://upstream.to', 
           'upstream': 'https://upstream.to', 
           'easy': 'https://easyload.io', 
           'easyload': 'https://easyload.io', 
           'fembed': 'https://www.fembed.com',
           'youtube': '',
           'pelisup': 'https://www.pelisup.com',
           'goo': 'https://gounlimited.to',
           'gounlimited': 'https://gounlimited.to',
           'megavips': 'https://mega.nz',
           'mystream': 'https://embed.mystream.to',
           'bb': 'https://videobb.ru',
           'upload': 'https://uqload.com',
           'uqload': 'https://uqload.com'
           }


def player_parse(url, server, host=''):
    server = server.lower().strip()
    logger.info('url : ' + str(url) + ', server: ' + str(server))
    
    if url.startswith('http'):
        return url
    
    # Obtenemos el nombre del canal
    channel = inspect.getmodule(inspect.currentframe().f_back.f_back)
    if channel == None:
        channel = ""
    else:
        channel = channel.__name__
    
    # Tratamos url de Servidores que vienen sin dominio
    # Buscamos el server en el diccionarios y lo parseamos con la url recibida
    # Si el server no está en el diccionario, usa el host del canal, por si es un directo
    #if server not in str(players):
    if not players.get(server, ''):
        logger.error('Añadir a lista de servers: %s' % server)

        if host:
            url = urlparse.urljoin(host, url)
        return url
    
    if server == 'netu' and '.mp4' in url:
        server = 'stape'

    # Puede haber canales que usen su propia entrada a un server
    if players.get(server+'_'+channel, ''):
        server = server+'_'+channel
    
    url = urlparse.urljoin(players.get(server, ''), url)
    
    return url
