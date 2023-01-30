# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    from urllib.parse import unquote
else:
    from urlparse import unquote


import os, xbmc

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, filetools, jsontools

from modules import tester


channels_currents = [
        'animefenix', 'animeflv', 'caricaturashd',
        'cinecalidad', 'cinecalidadla', 'cinecalidadlol',
        'cinetux',
        'cuevana3', 'cuevana3video',
        'divxtotal', 'dontorrents', 'elifilms', 'elitetorrent', 'entrepeliculasyseries',
        'gnula24', 'grantorrent', 'grantorrents',
        'hdfull', 'hdfullse',
        'inkapelis', 'kindor', 'pelis28', 'pelisflix', 'pelishouse', 'pelismaraton',
        'pelispedia', 'pelispediaws',
        'pelisplus', 'pelisplushd', 'pelisplushdlat',
        'playdede',
        'repelis24', 'repelishd',
        'series24', 'seriesanimadas', 'seriesyonkis', 'subtorrents', 'torrentdivx', 'torrentpelis'
        ]

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


def manto_domain_animefenix(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando AnimeFenix[/B][/COLOR]' % color_exec)

    channel_json = 'animefenix.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] AnimeFenix') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_animefenix(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('AnimeFenix')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - AnimeFenix', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_animeflv(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando AnimeFlv[/B][/COLOR]' % color_exec)

    channel_json = 'animeflv.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] AnimeFlv') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_animeflv(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('AnimeFlv')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - AnimeFlv', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_caricaturashd(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CaricaturasHd[/B][/COLOR]' % color_exec)

    channel_json = 'caricaturashd.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] CaricaturasHd') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_caricaturashd(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CaricaturasHd')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CaricaturasHd', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cinecalidad(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineCalidad[/B][/COLOR]' % color_exec)

    channel_json = 'cinecalidad.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] CineCalidad') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_cinecalidad(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CineCalidad')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CineCalidad', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cinecalidadla(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineCalidadLa[/B][/COLOR]' % color_exec)

    channel_json = 'cinecalidadla.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] CineCalidadLa') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_cinecalidadla(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CineCalidadLa')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CineCalidadLa', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cinecalidadlol(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineCalidadLol[/B][/COLOR]' % color_exec)

    channel_json = 'cinecalidadlol.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] CineCalidadLol') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_cinecalidadlol(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CineCalidadLol')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CineCalidadLol', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cinetux(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineTux[/B][/COLOR]' % color_exec)

    channel_json = 'cinetux.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] CineTux') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_cinetux(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CineTux')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CineTux', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cuevana3(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Cuevana3[/B][/COLOR]' % color_exec)

    channel_json = 'cuevana3.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] Cuevana3') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_cuevana3(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Cuevana3')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Cuevana3', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cuevana3video(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Cuevana3Video[/B][/COLOR]' % color_exec)

    channel_json = 'cuevana3video.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] Cuevana3Video') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_cuevana3video(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Cuevana3Video')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Cuevana3Video', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_divxtotal(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando DivxTotal[/B][/COLOR]' % color_exec)

    channel_json = 'divxtotal.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] DivxTotal') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_divxtotal(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('DivxTotal')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - DivxTotal', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def last_domain_dontorrents(item):
    logger.info()

    domain = config.get_setting('dominio', 'dontorrents', default='')

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando dominio[/B][/COLOR]' % color_exec)

    channel_json = 'dontorrents.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] DonTorrents') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    last_domain = ''

    try:
       data = httptools.downloadpage('https://t.me/s/DonTorrent').data

       dominios = scrapertools.find_multiple_matches(data, '>Dominio Oficial.*?<a href="(.*?)"')

       if dominios:
           for dominio in dominios:
               last_domain = dominio
    except:
       pass

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - DonTorrents', '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - DonTorrents', '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://t.me/s/DonTorrent[/B][/COLOR]')
        return


    host_channel = ''
    config.set_setting('user_test_channel', 'host_channel')

    try:
        localize = tester.test_channel('dontorrents')
    except:
        localize = ''

    if config.get_setting('user_test_channel', default=''):
        host_channel = config.get_setting('user_test_channel', default='')
        if not host_channel.startswith('https://'): host_channel = ''
	
        config.set_setting('user_test_channel', '')

        if host_channel:
            if not config.get_setting('dominio', 'dontorrents', default=''):
                if host_channel == item.host_canal:
                    platformtools.dialog_ok(config.__addon_name + ' - DonTorrents', '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                    return

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - DonTorrents', '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Último Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if platformtools.dialog_yesno(config.__addon_name + ' - DonTorrents', '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'dontorrents')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - DonTorrents', '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def manto_domain_dontorrents(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando DonTorrents[/B][/COLOR]' % color_exec)

    channel_json = 'dontorrents.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] DonTorrents') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)
    return


def test_domain_dontorrents(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('DonTorrents')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - DonTorrents', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_elifilms(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EliFilms[/B][/COLOR]' % color_exec)

    channel_json = 'elifilms.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] EliFilms') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_elifilms(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EliFilms')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EliFilms', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_elitetorrent(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EliteTorrent[/B][/COLOR]' % color_exec)

    channel_json = 'elitetorrent.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] EliteTorrent') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_elitetorrent(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EliteTorrent')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EliteTorrent', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_entrepeliculasyseries(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EntrePeliculasySeries[/B][/COLOR]' % color_exec)

    channel_json = 'entrepeliculasyseries.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] EntrePeliculasySeries') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_entrepeliculasyseries(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EntrePeliculasySeries')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EntrePeliculasySeries', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_gnula24(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Gnula24[/B][/COLOR]' % color_exec)

    channel_json = 'gnula24.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] Gnula24') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_gnula24(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Gnula24')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Gnula24', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_grantorrent(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando GranTorrent[/B][/COLOR]' % color_exec)

    channel_json = 'grantorrent.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] GranTorrent') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_grantorrent(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('GranTorrent')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - GranTorrent', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_grantorrents(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando GranTorrents[/B][/COLOR]' % color_exec)

    channel_json = 'grantorrents.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] GranTorrents') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_grantorrents(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('GranTorrents')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - GranTorrents', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def latest_domains_hdfull(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando dominios[/B][/COLOR]' % color_exec)

    channel_json = 'hdfull.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFull') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para conocer el ultimo dominio vigente en actions
    # ~ web  'https://dominioshdfull.com/'

    last_domain = ''

    try:
       host_domain = 'https://dominioshdfull.com/'

       data = httptools.downloadpage(host_domain).data

       latest_domain = scrapertools.find_single_match(data, 'onclick="location.href.*?' + "'(.*?)'")

       if latest_domain:
           latest_domain = latest_domain.replace('login', '')
           if not latest_domain.endswith('/'): latest_domain = latest_domain + '/'
    except:
       latest_domain = ''

    if latest_domain: last_domain = latest_domain

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://twitter.com/hdfulloficial[/B][/COLOR]')
        return

    platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]El último dominio es ', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')


def last_domain_hdfull(item):
    logger.info()

    domain = config.get_setting('dominio', 'hdfull', default='')

    if not domain:
        platformtools.dialog_notification(config.__addon_name + '[COLOR yellow][B] HdFull[/B][/COLOR]', '[B][COLOR %s]Falta Configurar el Dominio a usar ...[/COLOR][/B]' % color_alert)
        return

    platformtools.dialog_notification(config.__addon_name+ ' - HdFull', '[B][COLOR %s]Comprobando dominio[/B][/COLOR]' % color_exec)

    channel_json = 'hdfull.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFull') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    if domain:
        if domain == 'https://new.hdfull.one/':
            platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Dominio especial correcto[/B][/COLOR]' % color_infor)
            return


    # ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ webs  0)-'https://dominioshdfull.com/'  1)-'https://new.hdfull.one/'


    last_domain = ''

    if domain:
        try:
           host_domain = 'https://dominioshdfull.com/'

           data = httptools.downloadpage(host_domain).data

           latest_domain = scrapertools.find_single_match(data, 'onclick="location.href.*?' + "'(.*?)'")

           if latest_domain:
               latest_domain = latest_domain.replace('login', '')
               if not latest_domain.endswith('/'): latest_domain = latest_domain + '/'
        except:
           latest_domain = ''

        if latest_domain:
            if latest_domain == domain: last_domain = latest_domain


    if not last_domain:
        try:
           host_domain = 'https://dominioshdfull.com/'

           data = httptools.downloadpage(host_domain).data

           last_domain = scrapertools.find_single_match(data, 'onclick="location.href.*?' + "'(.*?)'")

           if last_domain:
               last_domain = last_domain.replace('login', '')
               if not last_domain.endswith('/'): last_domain = last_domain + '/'
        except:
           last_domain = ''


    if not last_domain:
        try:
           host_domain = 'https://new.hdfull.one/login'

           if item.desde_el_canal:
               if item.dominios_ret: host_domain = item.dominios_ret + 'login'

           data = httptools.downloadpage(host_domain).data

           last_domain = scrapertools.find_single_match(data, 'location.replace.*?"(.*?)"')
           if not last_domain: last_domain = scrapertools.find_single_match(data, '<link rel="canonical".*?href="(.*?)"')

           if not last_domain:
               if config.get_setting('channel_hdfull_proxies', default=''):
                   data = httptools.downloadpage_proxy('hdfull', host_domain).data
                   last_domain = scrapertools.find_single_match(data, 'location.replace.*?"(.*?)"')
                   if not last_domain: last_domain = scrapertools.find_single_match(data, '<link rel="canonical".*?href="(.*?)"')

           if last_domain:
               last_domain = last_domain.replace('login', '')
               if not last_domain.endswith('/'): last_domain = last_domain + '/'
        except:
           last_domain = ''


    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://twitter.com/hdfulloficial[/B][/COLOR]')
        return


    host_channel = ''
    config.set_setting('user_test_channel', 'host_channel')

    try:
        localize = tester.test_channel('hdfull')
    except:
        localize = ''

    if config.get_setting('user_test_channel', default=''):
        host_channel = config.get_setting('user_test_channel', default='')
        if not host_channel.startswith('https://'): host_channel = ''
	
        config.set_setting('user_test_channel', '')

        if host_channel:
            if host_channel == item.host_canal:
                platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                return

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Último Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if platformtools.dialog_yesno(config.__addon_name + ' - HdFull', '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'hdfull')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def operative_domains_hdfull(item):
    logger.info()

    domains = []

    domain = config.get_setting('dominio', 'hdfull', default='')

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando dominios[/B][/COLOR]' % color_exec)

    channel_json = 'hdfull.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFull') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para comprobar tods los dominios operativos
    # ~ web  0)-'https://dominioshdfull.com/'


    try:
       host_domain = 'https://dominioshdfull.com/'

       data = httptools.downloadpage(host_domain).data

       operative_domains = scrapertools.find_multiple_matches(data, 'onclick="location.href.*?' + "'(.*?)'")

       if not operative_domains:
           operative_domains_unescape = scrapertools.find_multiple_matches(data, "document.write.*?'(.*?)'")

           if operative_domains_unescape:
               operative_domains_unescape = unquote(str(operative_domains_unescape))

               operative_domains = scrapertools.find_multiple_matches(operative_domains_unescape, 'onclick="location.href.*?' + "'(.*?)'")
    except:
       platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Error Acceso Dominios Operativos[/B][/COLOR]' % color_alert)
       return

    i = -1
    preselect = 0

    for operative in operative_domains:
        i += 1

        if not operative.endswith('/'): operative = operative + '/'

        if operative == domain: preselect = i

        domains.append(operative)

    if not domains:
        platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Sin Dominios Operativos[/B][/COLOR]' % color_alert)
        return

    sel_domain = ''

    ret = platformtools.dialog_select('HdFull - Dominios Operativos', domains, preselect = preselect)

    if ret == -1: return False

    sel_domain = domains[ret]

    if domain:
        if domain == 'https://new.hdfull.one/':
            platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Dominio especial correcto[/B][/COLOR]' % color_infor)
            return

    nom_dom = domain
    txt_dom = 'Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if not sel_domain:
        platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Error Comprobación Dominio[/B][/COLOR]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name + ' - HdFull', '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Seleccionado:   [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'hdfull')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def del_datos_hdfull(item):
    logger.info()

    username = config.get_setting('hdfull_username', 'hdfull', default='')
    password = config.get_setting('hdfull_password', 'hdfull', default='')

    if not username or not password:
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma eliminar sus credenciales de HdFull ?[/B][/COLOR]'):
        config.set_setting('channel_hdfull_hdfull_login', False)
        config.set_setting('channel_hdfull_hdfull_password', '')
        config.set_setting('channel_hdfull_hdfull_username', '')


def manto_domain_hdfull(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando HdFull[/B][/COLOR]' % color_exec)

    channel_json = 'hdfull.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFull') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)
    return


def test_domain_hdfull(item):
    logger.info()

    domain = config.get_setting('dominio', 'hdfull', default='')

    if not domain:
        platformtools.dialog_notification(config.__addon_name + '[COLOR yellow][B] HdFull[/B][/COLOR]', '[B][COLOR %s]Falta Configurar el Dominio a usar ...[/COLOR][/B]' % color_alert)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('HdFull')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def last_domain_hdfullse(item):
    logger.info()

    domain = config.get_setting('dominio', 'hdfullse', default='')

    platformtools.dialog_notification(config.__addon_name+ ' - HdFullSe', '[B][COLOR %s]Comprobando dominio[/B][/COLOR]' % color_exec)

    channel_json = 'hdfullse.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFullSe') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ web 0)-'https://hdfull.pm'


    last_domain = ''

    if domain:
        try:
           host_domain = 'https://hdfull.pm'

           data = httptools.downloadpage(host_domain).data

           latest_domain = scrapertools.find_single_match(data, 'onClick="location.href.*?' + "'(.*?)'")

           if '/movies' in latest_domain: latest_domain = latest_domain.replace('/movies', '').strip()

        except:
           latest_domain = ''

        if latest_domain:
            if latest_domain == domain: last_domain = latest_domain


    if not last_domain:
        try:
           host_domain = 'https://hdfull.pm'

           data = httptools.downloadpage(host_domain).data

           latest_domain = scrapertools.find_single_match(data, 'onClick="location.href.*?' + "'(.*?)'")

           if '/movies' in latest_domain: latest_domain = latest_domain.replace('/movies', '').strip()

        except:
           last_domain = ''

        if latest_domain:
            if domain:
                if latest_domain == domain: last_domain = latest_domain
            else: last_domain = latest_domain


    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - HdFullSe', '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://hdfull.pm[/B][/COLOR]')
        return


    host_channel = ''
    config.set_setting('user_test_channel', 'host_channel')

    try:
        localize = tester.test_channel('hdfullse')
    except:
        localize = ''

    if config.get_setting('user_test_channel', default=''):
        host_channel = config.get_setting('user_test_channel', default='')
        if not host_channel.startswith('https://'): host_channel = ''
	
        config.set_setting('user_test_channel', '')

        if host_channel:
            if host_channel == item.host_canal:
                platformtools.dialog_ok(config.__addon_name + ' - HdFullSe', '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                return

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - HdFullSe', '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Último Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if platformtools.dialog_yesno(config.__addon_name + ' - HdFullSe', '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'hdfullse')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - HdFullSe', '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def operative_domains_hdfullse(item):
    logger.info()

    domains = []

    domain = config.get_setting('dominio', 'hdfullse', default='')

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando dominios[/B][/COLOR]' % color_exec)

    channel_json = 'hdfullse.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFullSe') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ web 0)-'https://hdfull.pm'


    try:
       host_domain = 'https://hdfull.pm'

       data = httptools.downloadpage(host_domain).data

       operative_domains = scrapertools.find_multiple_matches(data, 'onClick="location.href.*?' + "'(.*?)'")

    except:
       platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]Error Acceso Dominios Operativos[/B][/COLOR]' % color_alert)
       return

    i = -1
    preselect = 0

    for operative in operative_domains:
        i += 1

        if '/movies' in operative: operative = operative.replace('/movies', '').strip()

        if operative == domain: preselect = i

        domains.append(operative)

    if not domains:
        platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]Sin Dominios Operativos[/B][/COLOR]' % color_alert)
        return

    sel_domain = ''

    ret = platformtools.dialog_select('HdFullSe - Dominios Operativos', domains, preselect = preselect)

    if ret == -1: return False

    sel_domain = domains[ret]

    nom_dom = domain
    txt_dom = 'Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if not sel_domain:
        platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]Error Comprobación Dominio[/B][/COLOR]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name + ' - HdFullSe', '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Seleccionado:   [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'hdfullSe')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - HdFullSe', '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def manto_domain_hdfullse(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando HdFullSe[/B][/COLOR]' % color_exec)

    channel_json = 'hdfullse.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFullSe') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_hdfullse(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('HdFullSe')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_inkapelis(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando InkaPelis[/B][/COLOR]' % color_exec)

    channel_json = 'inkapelis.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] InkaPelis') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_inkapelis(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('InkaPelis')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - InkaPelis', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_kindor(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Kindor[/B][/COLOR]' % color_exec)

    channel_json = 'kindor.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] Kindor') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_kindor(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Kindor')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Kindor', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelis28(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Pelis28[/B][/COLOR]' % color_exec)

    channel_json = 'pelis28.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] Pelis28') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelis28(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Pelis28')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Pelis28', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelisflix(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisFlix[/B][/COLOR]' % color_exec)

    channel_json = 'pelisflix.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisFlix') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelisflix(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisFlix')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisFlix', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelishouse(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisHouse[/B][/COLOR]' % color_exec)

    channel_json = 'pelishouse.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisHouse') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelishouse(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisHouse')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisHouse', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelismaraton(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisMaraton[/B][/COLOR]' % color_exec)

    channel_json = 'pelismaraton.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisMaraton') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelismaraton(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisMaraton')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisMaraton', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelispedia(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPedia[/B][/COLOR]' % color_exec)

    channel_json = 'pelispedia.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisPedia') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelispedia(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPedia')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPedia', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelispediaws(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPediaWs[/B][/COLOR]' % color_exec)

    channel_json = 'pelispediaws.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisPediaWs') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelispediaws(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPediaWs')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPediaWs', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelisplus(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlus[/B][/COLOR]' % color_exec)

    channel_json = 'pelisplus.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisPlus') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelisplus(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPlus')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPlus', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelisplushd(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlusHd[/B][/COLOR]' % color_exec)

    channel_json = 'pelisplushd.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisPlusHd') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelisplushd(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPlusHd')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPlusHd', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelisplushdlat(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlusHdLat[/B][/COLOR]' % color_exec)

    channel_json = 'pelisplushdlat.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PelisPlusHdLat') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_pelisplushdlat(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPlusHdLat')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPlusHdLat', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def del_datos_playdede(item):
    logger.info()

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    if not username or not password:
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma eliminar sus credenciales de PlayDede ?[/B][/COLOR]'):
        config.set_setting('channel_playdede_playdede_login', False)
        config.set_setting('channel_playdede_playdede_password', '')
        config.set_setting('channel_playdede_playdede_username', '')


def manto_domain_playdede(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Playdede[/B][/COLOR]' % color_exec)

    channel_json = 'playdede.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] Playdede') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_playdede(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PlayDede')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PlayDede', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_repelis24(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando RePelis24[/B][/COLOR]' % color_exec)

    channel_json = 'repelis24.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] RePelis24') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_repelis24(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('RePelis24')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - RePelis24', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_repelishd(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando RepPlisHd[/B][/COLOR]' % color_exec)

    channel_json = 'repelishd.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] RePelisHd') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_repelishd(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('RePelisHd')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - RePelisHd', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_series24(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Series24[/B][/COLOR]' % color_exec)

    channel_json = 'series24.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] Series24') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_series24(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Series24')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Series24', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_seriesanimadas(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SeriesAnimadas[/B][/COLOR]' % color_exec)

    channel_json = 'seriesanimadas.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] SeriesAnimadas') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_seriesanimadas(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SeriesAnimadas')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SeriesAnimadas', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_seriesyonkis(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SeriesYonkis[/B][/COLOR]' % color_exec)

    channel_json = 'seriesyonkis.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] SeriesYonkis') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_seriesyonkis(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SeriesYonkis')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SeriesYonkis', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_subtorrents(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SubTorrents[/B][/COLOR]' % color_exec)

    channel_json = 'subtorrents.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] SubTorrents') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_subtorrents(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SubTorrents')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SubTorrents', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_torrentdivx(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando TorrentDivx[/B][/COLOR]' % color_exec)

    channel_json = 'torrentdivx.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] TorrentDivx') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_torrentdivx(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('TorrentDivx')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - TorrentDivx', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_torrentpelis(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando TorrentPelis[/B][/COLOR]' % color_exec)

    channel_json = 'torrentpelis.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] TorrentPelis') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    id = params['id']
    name = params['name']

    manto_domain_common(item, id, name)


def test_domain_torrentpelis(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('TorrentPelis')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - TorrentPelis', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_common(item, id, name):
    logger.info()

    config.set_setting('user_test_channel', '')

    domain = config.get_setting('dominio', id, default='')

    if id in str(channels_currents):
        if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + name + '[/B][/COLOR]', '[COLOR yellowgreen][B]¿ Desea Localizar el Nuevo Dominio Permanente del Canal ?[/B][/COLOR]'):
            if id == 'hdfull':
                last_domain_hdfull(item)
                return

            elif id == 'hdfullse':
                last_domain_hdfullse(item)
                return

            elif id == 'dontorrents':
                last_domain_dontorrents(item)
                return

            config.set_setting('user_test_channel', 'localize')

            try:
                localize = tester.test_channel(id)
            except:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)
                return

            if config.get_setting('user_test_channel', default=''):
                if config.get_setting('user_test_channel') == 'localize':
                    config.set_setting('user_test_channel', '')

                    platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B]' + name + '[/B][/COLOR]', '[B][COLOR %s]El Dominio Actual está Vigente[/B][/COLOR]' % color_infor)
                    return

                else:
                    platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B]' + name + '[/B][/COLOR]', '[B][COLOR %s]Localizado Nuevo Dominio[/B][/COLOR]' % color_avis)

                    domain = config.get_setting('user_test_channel')
                    if domain.startswith('http:'): domain = domain.replace('http:', 'https:')

            else:
                platformtools.dialog_notification(config.__addon_name + ' [COLOR yellow][B]' + name + '[/B][/COLOR]', '[B][COLOR %s]Nuevo Dominio No localizado[/B][/COLOR]' % color_alert)

    if id == 'animefenix':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.animefenix.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeFenix  -->  [COLOR %s]https://??.animefenix.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.animefenix.': return

    elif id == 'animeflv':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://animeflv.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeFlv  -->  [COLOR %s]https://??.animeflv.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://animeflv.': return

    elif id == 'caricaturashd':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CaricaturasHd  -->  [COLOR %s]https://caricaturashd.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cinecalidad':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidad  -->  [COLOR %s]https://??.cinecalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cinecalidadla':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://cinecalidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidadLa  -->  [COLOR %s]https://cinecalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://cinecalidad.': return

    elif id == 'cinecalidadlol':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://cinecalidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidadLol  -->  [COLOR %s]https://cinecalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://cinecalidad.': return

    elif id == 'cinetux':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://cinetux.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineTux  -->  [COLOR %s]https://cinetux..??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://cinetux.': return

    elif id == 'cuevana3':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Cuevana3  -->  [COLOR %s]https://??.cuevana3.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cuevana3video':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Cuevana3Video  -->  [COLOR %s]https://???.cuevana3.??[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'divxtotal':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.divxtotal.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio DivxTotal  -->  [COLOR %s]https://www.divxtotal.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.divxtotal.': return

    elif id == 'dontorrents':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://dontorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio DonTorrents  -->  [COLOR %s]https://dontorrent.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://dontorrent.': return

    elif id == 'elifilms':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://allcalidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EliFilms  -->  [COLOR %s]https://allcalidad..??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://allcalidad.': return

    elif id == 'elitetorrent':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EliteTorrent  -->  [COLOR %s]https://??.elitetorrent.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'entrepeliculasyseries':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://entrepeliculasyseries.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EntrePeliculasySeries  -->  [COLOR %s]https://entrepeliculasyseries.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://entrepeliculasyseries.': return

    elif id == 'gnula24':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Gnula24  -->  [COLOR %s]https://??.gnula24.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'grantorrent':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://grantorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio GranTorrent  -->  [COLOR %s]https://grantorrent.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://grantorrent.': return

    elif id == 'grantorrents':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://grantorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio GranTorrents  -->  [COLOR %s]https://grantorrent.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://grantorrent.': return

    elif id == 'hdfull':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://hdfull.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio HdFull  -->  [COLOR %s]https://hdfull.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://hdfull.': return

    elif id == 'hdfullse':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://hdfull.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio HdFullSe  -->  [COLOR %s]https://hdfull.??[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://hdfull.': return

    elif id == 'inkapelis':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio InkaPelis  -->  [COLOR %s]https://??.inkapelis.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'kindor':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://kindor.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Kindor  -->  [COLOR %s]https://kindor.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://kindor.': return

    elif id == 'pelis28':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelis28.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Pelis28  -->  [COLOR %s]https://pelis28..??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelis28.': return

    elif id == 'pelisflix':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelisflix.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisFlix  -->  [COLOR %s]https://pelisflix.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelisflix.': return

    elif id == 'pelishouse':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisHouse  -->  [COLOR %s]https://??.pelishouse.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelismaraton':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisMaraton  -->  [COLOR %s]https://pelismaraton.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelispedia':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPedia  -->  [COLOR %s]https://pelispedia.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelispediaws':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPediaWs  -->  [COLOR %s]https://??.gnula4.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplus':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlus  -->  [COLOR %s]https://???.pelisplus.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplushd':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHd  -->  [COLOR %s]https://???.pelisplus.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplushdlat':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHdLat  -->  [COLOR %s]https://???.pelisplus.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'playdede':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://playdede.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PlayDede  -->  [COLOR %s]https://playdede.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://playdede.': return

    elif id == 'repelis24':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio RePelis24  -->  [COLOR %s]https://??.repelis24.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'repelishd':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio RePelisHd  -->  [COLOR %s]https://??.repelishd.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'series24':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Series24  -->  [COLOR %s]https://??.series24.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'seriesanimadas':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesAnimadas  -->  [COLOR %s]https://??.animedesho.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'seriesyonkis':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesYonkis  -->  [COLOR %s]https://.seriesyonkis.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'subtorrents':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.subtorrents.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SubTorrents  -->  [COLOR %s]https://www.subtorrents.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.subtorrents.': return

    elif id == 'torrentdivx':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio TorrentDivx  -->  [COLOR %s]https://??.ditorrent.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'torrentpelis':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio TorrentPelis  -->  [COLOR %s]https://??.torrentpelis.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    else:
        return

    config.set_setting('user_test_channel', '')

    if not new_domain:
        if domain:
            if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red][B] Confirma eliminar el dominio Memorizado ?[/B][/COLOR]', '[COLOR cyan][B] ' + domain + ' [/B][/COLOR]'): 
                config.set_setting('dominio', new_domain, id)

                if item.desde_el_canal:
                    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio eliminado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar el Canal e Ingresar de nuevo en él.[/B][/COLOR]')
                else:
                    if not item.from_action == 'mainlist':
                        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')
        return

    if new_domain:
        new_domain = new_domain.lower()

        mistake = False

        if ':' not in new_domain: mistake = True
        elif '//' not in new_domain: mistake = True
        elif '.' not in new_domain: mistake = True

        if mistake:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Dominio incorrecto[/B][/COLOR]' % color_adver)
            return

        if new_domain.startswith('http:'): new_domain = new_domain.replace('http:', 'https:')
        elif new_domain.startswith('//'): new_domain = 'https:' + new_domain

        if not new_domain.startswith('https://'): new_domain = 'https://' + new_domain
        if not new_domain.endswith('/'):
            if not id == 'cuevana3video' and not id == 'hdfullse': new_domain = new_domain + '/'
        else:
           if id == 'cuevana3video' or id == 'hdfullse':
               platformtools.dialog_notification(config.__addon_name + ' - Cuevana3Video', '[B][COLOR %s]Dominio sin / al final[/B][/COLOR]' % color_adver)
               return

        if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR yellow][B] Confirma el dominio informado ?[/B][/COLOR]', '[COLOR cyan][B] ' + new_domain + ' [/B][/COLOR]'): 
            config.set_setting('dominio', new_domain, id)

            if item.desde_el_canal:
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar el Canal e Ingresar de nuevo en él.[/B][/COLOR]')
            else:
                if not item.from_action == 'mainlist':
                    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')

    return

