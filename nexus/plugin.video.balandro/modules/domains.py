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
from core import channeltools, httptools, scrapertools, filetools, jsontools

from modules import tester


channels_currents = [
        'animefenix', 'animeflv', 'animeonline',
        'cinecalidad', 'cinecalidadla', 'cinecalidadlol', 'cinecalidadmx', 'cliversite', 'cuevana3video',
        'divxtotal', 'dontorrents',
        'elifilms', 'elitetorrent', 'ennovelas', 'entrepeliculasyseries', 'estrenosdoramas',
        'gnula24', 'grantorrent', 'grantorrents',
        'hdfull', 'hdfullse', ' henaojara',
        'mejortorrentapp',
        'pelishouse', 'pelismaraton', 'pelispedia', 'pelispediaws', 'pelisplus', 'pelisplushd', 'pelisplushdlat', 'pelisplushdnz', 'pelispluslat', 'playdede', 'poseidonhd2',
        'series24', 'seriesantiguas', 'serieskao', 'seriesyonkis', 'srnovelas', 'subtorrents',
        'torrentpelis'
        ]

dominioshdfull = [
         'https://hdfull.quest/',
         'https://hdfull.today/',
         'https://hdfull.sbs/',
         'https://hdfull.store/',
         'https://hdfull.one/',
         'https://hdfull.org/'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_animefenix(item):
    logger.info()

    datos = channeltools.get_channel_parameters('animefenix')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_animeflv(item):
    logger.info()

    datos = channeltools.get_channel_parameters('animeflv')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('AnimeFlv')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - AnimeFlv', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_animeonline(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando AnimeOnline[/B][/COLOR]' % color_exec)

    channel_json = 'animeonline.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_animeonline(item):
    logger.info()

    datos = channeltools.get_channel_parameters('animeonline')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('AnimeOnline')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - AnimeOnline', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_cinecalidad(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cinecalidad')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_cinecalidadla(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cinecalidadla')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_cinecalidadlol(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cinecalidadlol')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CineCalidadLol')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CineCalidadLol', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cinecalidadmx(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineCalidadMx[/B][/COLOR]' % color_exec)

    channel_json = 'cinecalidadmx.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_cinecalidadmx(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cinecalidadmx')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CineCalidadMx')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CineCalidadMx', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cliversite(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CliverSite[/B][/COLOR]' % color_exec)

    channel_json = 'cliversite.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_cliversite(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cliversite')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('CliverSite')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - CliverSite', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_cuevana3video(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cuevana3video')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_divxtotal(item):
    logger.info()

    datos = channeltools.get_channel_parameters('divxtotal')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
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
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://t.me/s/DonTorrent[/B][/COLOR]')
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
                    if item.host_canal == last_domain:
                        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                        return

    if host_channel:
        if not domain:
            if last_domain in host_channel:
                 platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                 return

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Último Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'dontorrents')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)
    return


def test_domain_dontorrents(item):
    logger.info()

    datos = channeltools.get_channel_parameters('dontorrents')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_elifilms(item):
    logger.info()

    datos = channeltools.get_channel_parameters('elifilms')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_elitetorrent(item):
    logger.info()

    datos = channeltools.get_channel_parameters('elitetorrent')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EliteTorrent')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EliteTorrent', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_ennovelas(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EnNovelas[/B][/COLOR]' % color_exec)

    channel_json = 'ennovelas.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_ennovelas(item):
    logger.info()

    datos = channeltools.get_channel_parameters('ennovelas')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EnNovelas')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EnNovelas', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_entrepeliculasyseries(item):
    logger.info()

    datos = channeltools.get_channel_parameters('entrepeliculasyseries')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EntrePeliculasySeries')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EntrePeliculasySeries', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_estrenosdoramas(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EstrenosDoramas[/B][/COLOR]' % color_exec)

    channel_json = 'estrenosdoramas.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_estrenosdoramas(item):
    logger.info()

    datos = channeltools.get_channel_parameters('estrenosdoramas')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EstrenosDoramas')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EstrenosDoramas', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)



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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_gnula24(item):
    logger.info()

    datos = channeltools.get_channel_parameters('gnula24')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_grantorrent(item):
    logger.info()

    datos = channeltools.get_channel_parameters('grantorrent')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_grantorrents(item):
    logger.info()

    datos = channeltools.get_channel_parameters('grantorrents')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para conocer el ultimo dominio vigente en actions
    # ~ web  'https://dominioshdfull.com/'

    last_domain = ''
    latest_domain = ''

    try:
       host_domain = 'https://dominioshdfull.com/'

       data = httptools.downloadpage(host_domain).data

       latest_domain = scrapertools.find_single_match(data, 'onclick="location.href.*?' + "'(.*?)'")

       if not latest_domain: latest_domain = dominioshdfull[0]

       if latest_domain:
           latest_domain = latest_domain.replace('login', '')
           if not latest_domain.endswith('/'): latest_domain = latest_domain + '/'
    except:
       latest_domain = ''

    if latest_domain: last_domain = latest_domain

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://twitter.com/hdfulloficial[/B][/COLOR]')
        return

    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio es ', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')


def last_domain_hdfull(item):
    logger.info()

    domain = config.get_setting('dominio', 'hdfull', default='')

    if not domain:
        platformtools.dialog_notification(config.__addon_name + '[COLOR yellow][B] HdFull[/B][/COLOR]', '[B][COLOR %s]Falta Configurar el Dominio a usar ...[/COLOR][/B]' % color_alert)
        return

    platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Comprobando dominio[/B][/COLOR]' % color_exec)

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    if domain:
        if domain == 'https://new.hdfull.one/':
            platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Dominio especial correcto[/B][/COLOR]' % color_infor)
            return


    # ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ webs  0)-'https://dominioshdfull.com/'  1)-'https://new.hdfull.one/'


    last_domain = ''
    latest_domain = ''

    if domain:
        try:
           host_domain = 'https://dominioshdfull.com/'

           data = httptools.downloadpage(host_domain).data

           latest_domain = scrapertools.find_single_match(data, 'onclick="location.href.*?' + "'(.*?)'")

           if not latest_domain:
               operative_domains = scrapertools.find_multiple_matches(data, 'onclick="location.href.*?' + "'(.*?)'")

               if not operative_domains:
                   operative_domains_unescape = scrapertools.find_multiple_matches(data, "document.write.*?'(.*?)'")

                   if operative_domains_unescape:
                       operative_domains_unescape = unquote(str(operative_domains_unescape))

                       operative_domains = scrapertools.find_multiple_matches(operative_domains_unescape, 'onclick="location.href.*?' + "'(.*?)'")

                   if operative_domains: latest_domain = operative_domains[0]

           if not latest_domain: latest_domain = dominioshdfull[0]

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

           if not last_domain:
               operative_domains = scrapertools.find_multiple_matches(data, 'onclick="location.href.*?' + "'(.*?)'")

               if not operative_domains:
                   operative_domains_unescape = scrapertools.find_multiple_matches(data, "document.write.*?'(.*?)'")

                   if operative_domains_unescape:
                       operative_domains_unescape = unquote(str(operative_domains_unescape))

                       operative_domains = scrapertools.find_multiple_matches(operative_domains_unescape, 'onclick="location.href.*?' + "'(.*?)'")

                   last_domain = operative_domains[0]

           if not last_domain: last_domain = dominioshdfull[0]

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

           if not last_domain: last_domain = dominioshdfull[0]

           if last_domain:
               last_domain = last_domain.replace('login', '')
               if not last_domain.endswith('/'): last_domain = last_domain + '/'
        except:
           last_domain = ''


    if not last_domain:
        if not domain in str(dominioshdfull):
            platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

            xbmc.sleep(1000)
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://twitter.com/hdfulloficial[/B][/COLOR]')
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
                if item.host_canal == last_domain:
                    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                    return

    if host_channel:
        if not domain:
            if last_domain in host_channel:
                 platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                 return

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Último Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if not last_domain: last_domain = dominioshdfull[0]

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'hdfull')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


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

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
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

       if not operative_domains: operative_domains = dominioshdfull

    except:
       platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Error Acceso Dominios Operativos[/B][/COLOR]' % color_alert)
       return

    i = -1
    preselect = 0

    for operative in operative_domains:
        i += 1

        if not operative.endswith('/'): operative = operative + '/'

        if operative == domain: preselect = i

        domains.append(operative)

    if not domains:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Sin Dominios Operativos[/B][/COLOR]' % color_alert)
        return

    sel_domain = ''

    ret = platformtools.dialog_select('HdFull - Dominios Operativos', domains, preselect = preselect)

    if ret == -1: return False

    sel_domain = domains[ret]

    if domain:
        if domain == 'https://new.hdfull.one/':
            platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Dominio especial correcto[/B][/COLOR]' % color_infor)
            return

    nom_dom = domain
    txt_dom = 'Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if not sel_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Error Comprobación Dominio[/B][/COLOR]' % color_alert)
        return

    if domain == sel_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Dominio correcto[/B][/COLOR]' % color_infor)
        return

    if not last_domain: last_domain = dominioshdfull[0]

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Seleccionado:   [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'hdfull')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def del_datos_hdfull(item):
    logger.info()

    username = config.get_setting('hdfull_username', 'hdfull', default='')
    password = config.get_setting('hdfull_password', 'hdfull', default='')

    if not username:
        if not password:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]HdFull Sin credenciales[/B][/COLOR]' % color_exec)
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)
    return


def test_domain_hdfull(item):
    logger.info()

    datos = channeltools.get_channel_parameters('hdfull')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]Comprobando dominio[/B][/COLOR]' % color_exec)

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

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ web 0)-'https://hdfull.pm'


    last_domain = ''
    latest_domain = ''

    if domain:
        try:
           host_domain = 'https://hdfull.pm'

           if config.get_setting('channel_hdfullse_proxies', default=''): data = httptools.downloadpage_proxy('hdfullse', host_domain).data
           else: data = httptools.downloadpage(host_domain).data

           latest_domain = scrapertools.find_single_match(data, 'onClick="location.href.*?' + "'(.*?)'")

           if '/movies' in latest_domain: latest_domain = latest_domain.replace('/movies', '').strip()

        except:
           latest_domain = ''

        if latest_domain:
            if latest_domain == domain: last_domain = latest_domain


    if not last_domain:
        try:
           host_domain = 'https://hdfull.pm'

           if config.get_setting('channel_hdfullse_proxies', default=''): data = httptools.downloadpage_proxy('hdfullse', host_domain).data
           else: data = httptools.downloadpage(host_domain).data

           latest_domain = scrapertools.find_single_match(data, 'onClick="location.href.*?' + "'(.*?)'")

           if '/movies' in latest_domain: latest_domain = latest_domain.replace('/movies', '').strip()

        except:
           last_domain = ''

        if latest_domain:
            if domain:
                if latest_domain == domain: last_domain = latest_domain
            else: last_domain = latest_domain


    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://hdfull.pm[/B][/COLOR]')
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
            if not config.get_setting('dominio', 'hdfullse', default=''):
                if host_channel == item.host_canal:
                    if item.host_canal == last_domain:
                        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                        return

    if host_channel:
        if not domain:
            if last_domain in host_channel:
                 platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                 return

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Último Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'hdfullse')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


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

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ web 0)-'https://hdfull.pm'


    try:
       host_domain = 'https://hdfull.pm'

       if config.get_setting('channel_hdfullse_proxies', default=''): data = httptools.downloadpage_proxy('hdfullse', host_domain).data
       else: data = httptools.downloadpage(host_domain).data

       if not data:
           xbmc.sleep(1000)
           platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para conocer los dominios operativos vigentes deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://hdfull.pm[/B][/COLOR]')
           return

       operative_domains = scrapertools.find_multiple_matches(data, 'onClick="location.href.*?' + "'(.*?)'")

    except:
       platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Error Acceso Dominios Operativos[/B][/COLOR]' % color_alert)
       return

    i = -1
    preselect = 0

    for operative in operative_domains:
        i += 1

        if '/movies' in operative: operative = operative.replace('/movies', '').strip()

        if operative == domain: preselect = i

        domains.append(operative)

    if not domains:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Sin Dominios Operativos[/B][/COLOR]' % color_alert)
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
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Error Comprobación Dominio[/B][/COLOR]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Seleccionado:   [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'hdfullSe')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_hdfullse(item):
    logger.info()

    datos = channeltools.get_channel_parameters('hdfullse')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('HdFullSe')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_henaojara(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando HenaOjara[/B][/COLOR]' % color_exec)

    channel_json = 'henaojara.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_henaojara(item):
    logger.info()

    datos = channeltools.get_channel_parameters('henaojara')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('HenaOjara')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - HenaOjara', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_mejortorrentapp(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando MejorTorrentApp[/B][/COLOR]' % color_exec)

    channel_json = 'mejortorrentapp.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_mejortorrentapp(item):
    logger.info()

    datos = channeltools.get_channel_parameters('mejortorrentapp')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('MejorTorrentApp')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - MejorTorrentApp', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelishouse(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelishouse')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelismaraton(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelismaraton')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelispedia(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelispedia')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelispediaws(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelispediaws')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelisplus(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelisplus')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelisplushd(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelisplushd')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelisplushdlat(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelisplushdlat')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPlusHdLat')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPlusHdLat', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelisplushdnz(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlusHdNz[/B][/COLOR]' % color_exec)

    channel_json = 'pelisplushdnz.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelisplushdnz(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelisplushdnz')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPlusHdNz')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPlusHdNz', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelispluslat(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlusLat[/B][/COLOR]' % color_exec)

    channel_json = 'pelispluslat.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_pelispluslat(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelispluslat')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPlusLat')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPlusLat', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def del_datos_nextdede(item):
    logger.info()

    email = config.get_setting('nextdede_email', 'nextdede', default='')
    password = config.get_setting('nextdede_password', 'nextdede', default='')
    username = config.get_setting('nextdede_username', 'nextdede', default='')

    if not email:
        if not password:
            if not username:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Nextdede Sin credenciales[/B][/COLOR]' % color_exec)
                return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma eliminar sus credenciales de NextDede ?[/B][/COLOR]'):
        config.set_setting('channel_nextdede_nextdede_login', False)
        config.set_setting('channel_nextdede_nextdede_email', '')
        config.set_setting('channel_nextdede_nextdede_password', '')
        config.set_setting('channel_nextdede_nextdede_username', '')


def test_domain_nextdede(item):
    logger.info()

    datos = channeltools.get_channel_parameters('nextdede')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('NextDede')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - NextDede', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def last_domain_playdede(item):
    logger.info()

    domain = config.get_setting('dominio', 'playdede', default='')

    platformtools.dialog_notification(config.__addon_name + ' - PlayDede', '[B][COLOR %s]Comprobando dominio[/B][/COLOR]' % color_exec)

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

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ webs  0)-'https://dominiosplaydede.com/'

    last_domain = ''
    latest_domain = ''

    try:
        host_domain = 'https://dominiosplaydede.com/'

        data = httptools.downloadpage(host_domain).data

        last_domain = scrapertools.find_single_match(data, '>Dominio actual.*?<a href="(.*?)"')
    except:
        last_domain = ''

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para conocer el último dominio vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://twitter.com/playdedeoficial[/B][/COLOR]')
        return


    host_channel = ''
    config.set_setting('user_test_channel', 'host_channel')

    try:
        localize = tester.test_channel('playdede')
    except:
        localize = ''

    if config.get_setting('user_test_channel', default=''):
        host_channel = config.get_setting('user_test_channel', default='')
        if not host_channel.startswith('https://'): host_channel = ''
	
        config.set_setting('user_test_channel', '')

        if host_channel:
            if not config.get_setting('dominio', 'playdede', default=''):
                if host_channel == item.host_canal:
                    if item.host_canal == last_domain:
                        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                        return

            domain = last_domain

    if last_domain:
        if not last_domain.endswith('/'): last_domain = last_domain + '/'

    if host_channel:
        if last_domain:
            if last_domain in host_channel:
                 platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                 return

    if domain == last_domain:
        if item.host_canal:
            if item.host_canal == last_domain:
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        else:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Último Dominio memorizado incorrecto.'

    if last_domain:
        if item.host_canal:
            if not item.host_canal == last_domain:
                nom_dom = item.host_canal
                txt_dom = 'Dominio/Host del canal incorrecto.'

    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'playdede')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def operative_domains_playdede(item):
    logger.info()

    domain = ''

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando dominios[/B][/COLOR]' % color_exec)

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

    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return


    # ~ web para comprobar tods los dominios operativos
    # ~ web  0)-'https://dominiosplaydede.com/'


    sel_domain = ''

    try:
       host_domain = 'https://dominiosplaydede.com/'

       data = httptools.downloadpage(host_domain).data

       sel_domain = scrapertools.find_single_match(data, '>Dominio actual.*?<a href="(.*?)"')
    except:
       platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Error Acceso Dominios Operativos[/B][/COLOR]' % color_alert)
       return

    host_channel = ''
    config.set_setting('user_test_channel', 'host_channel')

    try:
        localize = tester.test_channel('playdede')
    except:
        localize = ''

    if config.get_setting('user_test_channel', default=''):
        host_channel = config.get_setting('user_test_channel', default='')
        if not host_channel.startswith('https://'): host_channel = ''
	
        config.set_setting('user_test_channel', '')

        if host_channel:
            if not config.get_setting('dominio', 'playdede', default=''):
                if host_channel == item.host_canal:
                    if item.host_canal == sel_domain:
                        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + host_channel + '[/B][/COLOR]')
                        return

            domain = sel_domain

    if not domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Sin Dominios Operativos[/B][/COLOR]' % color_alert)
        return

    if sel_domain:
        if not sel_domain.endswith('/'): sel_domain = sel_domain + '/'

    if host_channel:
        if sel_domain:
            if sel_domain in host_channel:
                 platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + sel_domain + '[/B][/COLOR]')
                 return

    if domain == sel_domain:
        if item.host_canal == sel_domain:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + sel_domain + '[/B][/COLOR]')
            return

    nom_dom = domain
    txt_dom = 'Dominio memorizado incorrecto.'

    if sel_domain:
        if not item.host_canal == sel_domain:
            nom_dom = item.host_canal
            txt_dom = 'Dominio/Host del canal incorrecto.'

    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if domain == sel_domain:
        if item.host_canal == sel_domain:
            platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Dominio correcto[/B][/COLOR]' % color_infor)
            return

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Seleccionado:   [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'playdede')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def del_datos_playdede(item):
    logger.info()

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    if not username:
        if not password:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]PlayDede Sin credenciales[/B][/COLOR]' % color_exec)
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_playdede(item):
    logger.info()

    datos = channeltools.get_channel_parameters('playdede')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PlayDede')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PlayDede', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_poseidonhd2(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PoseidonHd2[/B][/COLOR]' % color_exec)

    channel_json = 'poseidonhd2.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_poseidonhd2(item):
    logger.info()

    datos = channeltools.get_channel_parameters('poseidonhd2')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PoseidonHd2')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PoseidonHd2', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_series24(item):
    logger.info()

    datos = channeltools.get_channel_parameters('series24')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Series24')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Series24', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_seriesantiguas(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SeriesAntiguas[/B][/COLOR]' % color_exec)

    channel_json = 'seriesantiguas.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_seriesantiguas(item):
    logger.info()

    datos = channeltools.get_channel_parameters('seriesantiguas')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SeriesAntiguas')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SeriesAntiguas', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_serieskao(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SeriesKao[/B][/COLOR]' % color_exec)

    channel_json = 'serieskao.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_serieskao(item):
    logger.info()

    datos = channeltools.get_channel_parameters('serieskao')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SeriesKao')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SeriesKao', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_seriesyonkis(item):
    logger.info()

    datos = channeltools.get_channel_parameters('seriesyonkis')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SeriesYonkis')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SeriesYonkis', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_srnovelas(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SrNovelas[/B][/COLOR]' % color_exec)

    channel_json = 'srnovelas.json'
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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_srnovelas(item):
    logger.info()

    datos = channeltools.get_channel_parameters('srnovelas')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('srnovelas')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SrNovelas', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_subtorrents(item):
    logger.info()

    datos = channeltools.get_channel_parameters('subtorrents')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SubTorrents')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SubTorrents', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    id = params['id']
    name = params['name']

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] ' + name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    manto_domain_common(item, id, name)


def test_domain_torrentpelis(item):
    logger.info()

    datos = channeltools.get_channel_parameters('torrentpelis')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('TorrentPelis')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - TorrentPelis', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_common(item, id, name):
    logger.info()

    config.set_setting('user_test_channel', '')

    domain = config.get_setting('dominio', id, default='')

    falso = True

    for channel_current in channels_currents:
        if not id == channel_current: continue

        falso = False
        break

    if falso:
        platformtools.dialog_notification(config.__addon_name + '[B][COLOR yellow] ' + name + '[/COLOR][/B]', '[B][COLOR %s]Comprobación NO permitida[/B][/COLOR]' % color_alert)
        return
    else:
       if platformtools.dialog_yesno(config.__addon_name + ' [COLOR yellow][B]' + name + '[/B][/COLOR]', '[COLOR yellowgreen][B]¿ Desea Localizar el Nuevo Dominio Permanente del Canal ?[/B][/COLOR]'):
           if id == 'dontorrents':
               last_domain_dontorrents(item)
               return

           elif id == 'hdfull':
               last_domain_hdfull(item)
               return

           elif id == 'hdfullse':
               last_domain_hdfullse(item)
               return

           elif id == 'playdede':
               last_domain_playdede(item)
               return

           config.set_setting('user_test_channel', 'localize')

           try:
               localize = tester.test_channel(id)
           except:
               platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)
               return

           if config.get_setting('user_test_channel', default=''):
               if config.get_setting('user_test_channel') == 'localized': config.set_setting('user_test_channel', 'localize')

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

        if not domain: domain = 'https://animefenix.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeFenix  -->  [COLOR %s]https://animefenix.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://animefenix.': return

    elif id == 'animeflv':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://animeflv.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeFlv  -->  [COLOR %s]https://???.animeflv.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://animeflv.': return

    elif id == 'animeonline':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeOnline  -->  [COLOR %s]https://???.animeonline.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cinecalidad':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://cinecalidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidad  -->  [COLOR %s]https://cinecalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://cinecalidad.': return

    elif id == 'cinecalidadla':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://cinecalidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidadLa  -->  [COLOR %s]https://cinecalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://cinecalidad.': return

    elif id == 'cinecalidadlol':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://cinecalidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidadLol  -->  [COLOR %s]https://cinecalidad.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://cinecalidad.': return

    elif id == 'cinecalidadmx':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidadMx  -->  [COLOR %s]https://???.cinecalidad.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cliversite':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CliverSite  -->  [COLOR %s]https://???.cliver..??/[/COLOR]' % color_avis)

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

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio DivxTotal  -->  [COLOR %s]https://www.divxtotal.??/[/COLOR]' % color_avis)

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

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EliFilms  -->  [COLOR %s]https://allcalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://allcalidad.': return

    elif id == 'elitetorrent':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.elitetorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EliteTorrent  -->  [COLOR %s]https://www.elitetorrent.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.elitetorrent.': return

    elif id == 'ennovelas':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EnNovelas  -->  [COLOR %s]https://??.ennovelas.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'entrepeliculasyseries':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://entrepeliculasyseries.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EntrePeliculasySeries  -->  [COLOR %s]https://entrepeliculasyseries.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://entrepeliculasyseries.': return

    elif id == 'estrenosdoramas':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EstrenosDoramas  -->  [COLOR %s]https://???.estrenosdoramas.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'gnula24':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Gnula24  -->  [COLOR %s]https://???.gnula24.???/[/COLOR]' % color_avis)

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

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio GranTorrents  -->  [COLOR %s]https://grantorrent.???/[/COLOR]' % color_avis)

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

    elif id == 'henaojara':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio HenaOjara  -->  [COLOR %s]https://???.henaojara.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'mejortorrentapp':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio MejorTorrentApp  -->  [COLOR %s]https://???.mejortorrent.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelishouse':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisHouse  -->  [COLOR %s]https://???.pelishouse.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelismaraton':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelismaraton.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisMaraton  -->  [COLOR %s]https://pelismaraton.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelismaraton.': return

    elif id == 'pelispedia':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelispedia.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPedia  -->  [COLOR %s]https://pelispedia.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelispedia.': return

    elif id == 'pelispediaws':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.gnula4.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPediaWs  -->  [COLOR %s]https://www.gnula4.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.gnula4.': return

    elif id == 'pelisplus':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelisplus.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlus  -->  [COLOR %s]https://pelisplus.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelisplus.': return

    elif id == 'pelisplushd':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHd  -->  [COLOR %s]https://???.pelisplus.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplushdlat':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHdLat  -->  [COLOR %s]https://???.pelisplus.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplushdnz':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHdNz  -->  [COLOR %s]https://???.pelisplushd.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelispluslat':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusLat  -->  [COLOR %s]https://pelisplus.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'playdede':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://playdede.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PlayDede  -->  [COLOR %s]https://playdede.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://playdede.': return

    elif id == 'poseidonhd2':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PoseidonHd2  -->  [COLOR %s]https://???.poseidonhd2.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'series24':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Series24  -->  [COLOR %s]https://???.series24.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'seriesantiguas':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesAntiguas  -->  [COLOR %s]https://???.seriesantiguas.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'serieskao':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://serieskao.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesKao  -->  [COLOR %s]https://serieskao.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://serieskao.': return

    elif id == 'seriesyonkis':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://seriesyonkis.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesYonkis  -->  [COLOR %s]https://seriesyonkis.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://seriesyonkis.': return

    elif id == 'srnovelas':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SrNovelas  -->  [COLOR %s]https://??????.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'subtorrents':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.subtorrents.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SubTorrents  -->  [COLOR %s]https://www.subtorrents.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.subtorrents.': return

    elif id == 'torrentpelis':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://torrentpelis.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio TorrentPelis  -->  [COLOR %s]https://torrentpelis.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://torrentpelis.': return

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

