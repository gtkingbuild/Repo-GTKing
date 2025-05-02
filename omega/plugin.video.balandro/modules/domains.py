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
        'animeflv', 'animeid', 'animeonline',
        'cinecalidad', 'cinecalidadla', 'cinecalidadlol', 'cliversite', 'cuevana2', 'cuevana2esp', 'cuevana3pro', 'cuevana3video',
        'divxtotal', 'dontorrents', 'dontorrentsin',
        'elifilms', 'elitetorrent', 'elitetorrentnz', 'ennovelastv', 'entrepeliculasyseries',
        'gnula', 'gnula24', 'gnula24h', 'grantorrent',
        'hdfull', 'hdfullse', 'henaojara', 'homecine',
        'mejortorrentapp', 'mejortorrentnz', 'mitorrent',
        'novelastop',
        'peliculaspro', 
        'pelisforte', 'pelismart', 'pelispanda', 'pelispediaws', 'pelisplus', 'pelisplushd', 'pelisplushdlat', 'pelisplushdnz',
        'playdede',
        'poseidonhd2',
        'series24', 'serieskao', 'seriespapayato', 'seriesplus', 'srnovelas', 'subtorrents',
        'todotorrents',
        'veronline'
        ]

dominioshdfull = [
         'https://hdfull.blog/',
         'https://hdfull.today/',
         'https://hd-full.biz/',
         'https://hdfull.sbs/',

         'https://hdfull.cv/',
         'https://hdfull.monster/',
         'https://hdfull.cfd/',
         'https://hdfull.tel/',
         'https://hdfull.buzz/',
         'https://hdfull.one/',
         'https://hdfull.org/',

         'https://new.hdfull.one/'
         ]

domains_cloudflare_hdfull = [
         'https://hdfull.cv/',
         'https://hdfull.monster/',
         'https://hdfull.cfd/',
         'https://hdfull.tel/',
         'https://hdfull.buzz/',
         'https://hdfull.one/',
         'https://hdfull.org/',
         'https://new.hdfull.one/'
         ]

ant_hosts_hdfull = [
         'https://hdfull.sh/', 'https://hdfull.im/', 'https://hdfull.in/',
         'https://hdfull.pro/', 'https://hdfull.la/', 'https://hdfull.tv/',
         'https://hd-full.cc/', 'https://hdfull.me/', 'https://hdfull.io/',
         'https://hdfull.lv/', 'https://hdfullcdn.cc/', 'https://hdfull.stream/',
         'https://hdfull.click/', 'https://hdfull.lol/', 'https://hdfull.fun/',
         'https://hdfull.top/', 'https://hdfull.vip/', 'https://hdfull.wtf/',
         'https://hdfull.gdn/', 'https://hdfull.cloud/', 'https://hdfull.video/',
         'https://hdfull.work/', 'https://hdfull.life/', 'https://hdfull.digital/',
         'https://hdfull.store/', 'https://hd-full.in/', 'https://hdfull.icu/',
         'https://hd-full.im/', 'https://hd-full.one/', 'https://hdfull.link/',
         'https://hd-full.co/', 'https://hd-full.lol/', 'https://hdfull.quest/',
         'https://hd-full.info/', 'https://hd-full.sbs/', 'https://hd-full.life/',
         'https://hd-full.fit/', 'https://hd-full.me/', 'https://hd-full.vip/'
         ]


dominiosplaydede = [
         'https://www9.playdede.link/'
         ]

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


def manto_domain_animeflv(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando AnimeFlv[/B][/COLOR]' % color_exec)

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


def manto_domain_animeid(item):
    logger.info()

    channel_json = 'animeid.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando AnimeId[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_animeid(item):
    logger.info()

    datos = channeltools.get_channel_parameters('animeid')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('AnimeId')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - AnimeId', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_animeonline(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando AnimeOnline[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineCalidad[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineCalidadLa[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CineCalidadLol[/B][/COLOR]' % color_exec)

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


def manto_domain_cliversite(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando CliverSite[/B][/COLOR]' % color_exec)

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


def manto_domain_cuevana2(item):
    logger.info()

    channel_json = 'cuevana2.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Cuevana2[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_cuevana2(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cuevana2')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Cuevana2')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Cuevana2', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cuevana2esp(item):
    logger.info()

    channel_json = 'cuevana2esp.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Cuevana2Esp[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_cuevana2esp(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cuevana2esp')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Cuevana2Esp')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Cuevana2Esp', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cuevana3pro(item):
    logger.info()

    channel_json = 'cuevana3pro.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Cuevana3Pro[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_cuevana3pro(item):
    logger.info()

    datos = channeltools.get_channel_parameters('cuevana3pro')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Cuevana3Pro')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Cuevana3Pro', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_cuevana3video(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Cuevana3Video[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando DivxTotal[/B][/COLOR]' % color_exec)

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


def operative_domains_dontorrents(item):
    logger.info()

    domain = config.get_setting('dominio', 'dontorrents', default='')

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Dominio[/B][/COLOR]' % color_exec)

    # ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ web 0)-'https://t.me/s/DonTorrent'

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
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para saber el Último Dominio Vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://t.me/s/DonTorrent[/B][/COLOR]')
        return

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    nom_dom = domain
    txt_dom = 'Dominio memorizado incorrecto.'
    if not domain:
        nom_dom = 'Sin información'
        txt_dom = 'Aún No hay ningún Dominio memorizado.'

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Error Comprobación Dominio[/B][/COLOR]' % color_alert)
        return

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Encontrado:     [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'Dontorrents')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def last_domain_dontorrents(item):
    logger.info()

    domain = config.get_setting('dominio', 'dontorrents', default='')

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Dominio[/B][/COLOR]' % color_exec)

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
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para saber el Último Dominio Vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]https://t.me/s/DonTorrent[/B][/COLOR]')
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

    if localize:
        if localize == domain:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El dominio vigente es correcto.', '[COLOR cyan][B]' + localize + '[/B][/COLOR]')
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
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def manto_domain_dontorrents(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando DonTorrents[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


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


def manto_domain_dontorrentsin(item):
    logger.info()

    channel_json = 'dontorrentsin.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando DonTorrentsIn[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_dontorrentsin(item):
    logger.info()

    datos = channeltools.get_channel_parameters('dontorrentsin')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('DonTorrentsIn')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - DonTorrentsIn', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_elifilms(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EliFilms[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EliteTorrent[/B][/COLOR]' % color_exec)

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


def manto_domain_elitetorrentnz(item):
    logger.info()

    channel_json = 'elitetorrentnz.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EliteTorrentNz[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_elitetorrentnz(item):
    logger.info()

    datos = channeltools.get_channel_parameters('elitetorrentnz')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EliteTorrentNz')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EliteTorrentNz', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_ennovelastv(item):
    logger.info()

    channel_json = 'ennovelastv.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EnNovelasTv[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_ennovelastv(item):
    logger.info()

    datos = channeltools.get_channel_parameters('ennovelastv')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('EnNovelasTv')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - EnNovelasTv', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_entrepeliculasyseries(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando EntrePeliculasySeries[/B][/COLOR]' % color_exec)

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


def manto_domain_gnula(item):
    logger.info()

    channel_json = 'gnula.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Gnula[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_gnula(item):
    logger.info()

    datos = channeltools.get_channel_parameters('gnula')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Gnula')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Gnula', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_gnula24(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Gnula24[/B][/COLOR]' % color_exec)

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


def manto_domain_gnula24h(item):
    logger.info()

    channel_json = 'gnula24h.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Gnula24H[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_gnula24h(item):
    logger.info()

    datos = channeltools.get_channel_parameters('gnula24h')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('Gnula24H')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - Gnula24H', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_grantorrent(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando GranTorrent[/B][/COLOR]' % color_exec)

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


def latest_domains_hdfull(item):
    logger.info()

    domain = config.get_setting('dominio', 'hdfull', default='')

    if not domain:
        platformtools.dialog_notification(config.__addon_name + '[COLOR yellow][B] HdFull[/B][/COLOR]', '[B][COLOR %s]Falta Configurar el Dominio a usar ...[/COLOR][/B]' % color_alert)
        return

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando dominios[/B][/COLOR]' % color_exec)

    # ~ web para saber el ultimo dominio vigente
    # ~ web 0)-https://dominioshdfull.com/

    last_domain = ''
    latest_domain = ''

    try:
       data = httptools.downloadpage('https://dominioshdfull.com/').data

       bloque = scrapertools.find_single_match(data, 'dominios operativos actualizados(.*?)<script>')

       latest_domain = scrapertools.find_single_match(bloque, 'href="(.*?)"')

       if not latest_domain: latest_domain = dominioshdfull[0]
       else:
           if not latest_domain.endswith('/'): latest_domain = latest_domain + '/'
    except:
       latest_domain = ''

    if latest_domain: last_domain = latest_domain

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para saber el Último Dominio Vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]dominioshdfull.com//B][/COLOR]')
        return

    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio es ', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')


def last_domain_hdfull(item):
    logger.info()

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

    domain = config.get_setting('dominio', 'hdfull', default='')

    if not domain:
        platformtools.dialog_notification(config.__addon_name + '[COLOR yellow][B] HdFull[/B][/COLOR]', '[B][COLOR %s]Falta Configurar el Dominio a usar ...[/COLOR][/B]' % color_alert)
        return

    platformtools.dialog_notification(config.__addon_name + ' - HdFull', '[B][COLOR %s]Comprobando Dominios[/B][/COLOR]' % color_exec)

    # ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ webs  0)-https://dominioshdfull.com/  1)-https://new.hdfull.one/

    last_domain = ''
    latest_domain = ''

    try:
       data = httptools.downloadpage('https://dominioshdfull.com/').data

       bloque = scrapertools.find_single_match(data, 'dominios operativos actualizados(.*?)<script>')

       latest_domain = scrapertools.find_single_match(bloque, 'href="(.*?)"')

       if not latest_domain: latest_domain = dominioshdfull[0]
       else:
           if not latest_domain.endswith('/'): latest_domain = latest_domain + '/'
    except:
       latest_domain = ''

    if latest_domain:
        if latest_domain == domain: last_domain = latest_domain

    if not last_domain:
        try:
           data = httptools.downloadpage('https://dominioshdfull.com/').data

           bloque = scrapertools.find_single_match(data, 'dominios operativos actualizados(.*?)<script>')

           last_domain = scrapertools.find_single_match(bloque, 'href="(.*?)"')

           if not last_domain: last_domain = dominioshdfull[0]

           if last_domain:
               if not last_domain.endswith('/'): last_domain = last_domain + '/'
        except:
           last_domain = ''

    if not last_domain:
        if not domain in str(dominioshdfull):
            platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

            xbmc.sleep(1000)
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para saber el Último Dominio Vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]dominioshdfull.com[/B][/COLOR]')
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

    if localize:
        if last_domain:
            if last_domain == domain:
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                return

        elif localize == domain:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El dominio vigente es correcto.', '[COLOR cyan][B]' + localize + '[/B][/COLOR]')
            return
    else:
        if last_domain == domain:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
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
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def operative_domains_hdfull(item):
    logger.info()

    domains = []

    domain = config.get_setting('dominio', 'hdfull', default='')

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Dominios[/B][/COLOR]' % color_exec)

    # ~ web para comprobar todos los dominios operativos
    # ~ web  0)-https://dominioshdfull.com/

    last_domain = ''

    try:
       data = httptools.downloadpage('https://dominioshdfull.com/').data

       bloque = scrapertools.find_single_match(data, 'dominios operativos actualizados(.*?)<script>')

       operative_domains = scrapertools.find_multiple_matches(bloque, 'href="(.*?)"')

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

    if domains[ret] in str(ant_hosts_hdfull):
        platformtools.dialog_ok(config.__addon_name + ' HdFull - Dominios Operativos', '[COLOR red][B]Dominio Obsoleto.[/B][/COLOR]', '[COLOR cyan][B]' + domains[ret] + ' [/B][/COLOR]')
        return False

    elif domains[ret] in str(domains_cloudflare_hdfull):
        if not platformtools.dialog_yesno(config.__addon_name + ' HdFull - Dominios Operativos', '[COLOR yellow][B]Este Dominio, probablemente Necesitará[/COLOR] [COLOR red] Proxies[/B][/COLOR]', '[COLOR cyan][B]' + domains[ret] + '[/B][/COLOR][CR][COLOR yellowgreen][B]¿ Confirma el Dominio seleccionado ?[/B][/COLOR]'):
            return False

    sel_domain = domains[ret]

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

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Encontrado:     [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'hdfull')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def del_datos_hdfull(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando HdFull[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


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

    platformtools.dialog_notification(config.__addon_name + ' - HdFullSe', '[B][COLOR %s]Comprobando Dominio[/B][/COLOR]' % color_exec)

    # ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ web 0)-https://hdfull.pm/  1)-'https://www.hdfull.it'

    last_domain = ''
    latest_domain = ''

    if domain:
        try:
           host_domain = 'https://hdfull.pm/'

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
           host_domain = 'https://hdfull.pm/'

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
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para saber el Último Dominio Vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]hdfull.pm/  ó  www.hdfull.it[/B][/COLOR]')
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

    if localize:
        if localize == domain:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El dominio vigente es correcto.', '[COLOR cyan][B]' + localize + '[/B][/COLOR]')
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
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def operative_domains_hdfullse(item):
    logger.info()

    domains = []

    domain = config.get_setting('dominio', 'hdfullse', default='')

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Dominio[/B][/COLOR]' % color_exec)

    # ~ web para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ web 0)-https://hdfull.pm/ 1)-'https://www.hdfull.it'

    try:
       host_domain = 'https://hdfull.pm/'

       if config.get_setting('channel_hdfullse_proxies', default=''): data = httptools.downloadpage_proxy('hdfullse', host_domain).data
       else: data = httptools.downloadpage(host_domain).data

       if not data:
           xbmc.sleep(1000)
           platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para saber el Último Dominio Vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]hdfull.pm/  ó  www.hdfull.it/[/B][/COLOR]')
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

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Encontrado:     [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'hdfullse')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def manto_domain_hdfullse(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando HdFullSe[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando HenaOjara[/B][/COLOR]' % color_exec)

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


def manto_domain_homecine(item):
    logger.info()

    channel_json = 'homecine.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando HomeCine[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_homecine(item):
    logger.info()

    datos = channeltools.get_channel_parameters('homecine')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('HomeCine')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - HomeCine', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_mejortorrentapp(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando MejorTorrentApp[/B][/COLOR]' % color_exec)

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


def manto_domain_mejortorrentnz(item):
    logger.info()

    channel_json = 'mejortorrentnz.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando MejorTorrentNz[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_mejortorrentnz(item):
    logger.info()

    datos = channeltools.get_channel_parameters('mejortorrentnz')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('MejorTorrentNz')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - MejorTorrentNz', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_mitorrent(item):
    logger.info()

    channel_json = 'mitorrent.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando MiTorrent[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_mitorrent(item):
    logger.info()

    datos = channeltools.get_channel_parameters('mitorrent')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('MiTorrent')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - MiTorrent', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_novelastop(item):
    logger.info()

    channel_json = 'novelastop.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando NovelasTop[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_novelastop(item):
    logger.info()

    datos = channeltools.get_channel_parameters('novelastop')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('NovelasTop')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - NovelasTop', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_peliculaspro(item):
    logger.info()

    channel_json = 'peliculaspro.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PeliculasPro[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_peliculaspro(item):
    logger.info()

    datos = channeltools.get_channel_parameters('peliculaspro')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PeliculasPro')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PeliculasPro', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelisforte(item):
    logger.info()

    channel_json = 'pelisforte.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisForte[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_pelisforte(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelisforte')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisForte')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisForte', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelismart(item):
    logger.info()

    channel_json = 'pelismart.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisMart[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_pelismart(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelismart')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisMart')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisMart', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelispanda(item):
    logger.info()

    channel_json = 'pelispanda.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPanda[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_pelispanda(item):
    logger.info()

    datos = channeltools.get_channel_parameters('pelispanda')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('PelisPanda')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - PelisPanda', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_pelispediaws(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPediaWs[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlus[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlusHd[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlusHdLat[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PelisPlusHdNz[/B][/COLOR]' % color_exec)

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


def last_domain_playdede(item):
    logger.info()

    domain = config.get_setting('dominio', 'playdede', default='')

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

    platformtools.dialog_notification(config.__addon_name + ' - PlayDede', '[B][COLOR %s]Comprobando Dominio[/B][/COLOR]' % color_exec)

    # ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
    # ~ webs  0)-https://privacidad.me/@playdede  1)-https://entrarplaydede.com  2)-X https://x.com/playdedesocial

    last_domain = ''
    latest_domain = ''

    try:
        data = httptools.downloadpage('https://privacidad.me/@playdede/').data

        last_domain = scrapertools.find_single_match(data, '>Dirección actual:(.*?)</a>').strip()

        if last_domain:
            last_domain = last_domain.lower()

            if not 'playdede' in last_domain: last_domain = ''

        if last_domain:
            if not 'https' in last_domain: last_domain  = 'https://' + last_domain
            if not last_domain.endswith('/'): last_domain = last_domain + '/'
    except:
        pass

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)

        xbmc.sleep(1000)
        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Para conocer el Último Dominio Vigente deberá acceder a través de un navegador web a:', '[COLOR cyan][B]privacidad.me/@playdede[/B][/COLOR] ó [B][COLOR greenyellow]entrarplaydede.com[/COLOR][/B] ó [B][COLOR greenyellow]x.com/playdedesocial[/COLOR][/B]')
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
                 if last_domain in str(dominiosplaydede):
                     platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                     return

    if domain == last_domain:
        if last_domain in str(dominiosplaydede):
            if item.host_canal:
                if item.host_canal == last_domain:
                    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                else:
                    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
                return

    if localize:
        if localize == domain:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El dominio vigente es correcto.', '[COLOR cyan][B]' + localize + '[/B][/COLOR]')
            return
    else:
        if last_domain == domain:
            platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]El dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
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
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def operative_domains_playdede(item):
    logger.info()

    domain = ''

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Dominio[/B][/COLOR]' % color_exec)

    # ~ web para comprobar todos los dominios operativos
    # ~ webs  0)-https://privacidad.me/@playdede  1)-https://entrarplaydede.com  2)-X https://x.com/playdedesocial

    sel_domain = ''

    try:
       data = httptools.downloadpage('https://privacidad.me/@playdede/').data

       sel_domain = scrapertools.find_single_match(data, '>Dirección actual:(.*?)</a>').strip()

       if sel_domain:
           sel_domain = sel_domain.lower()
           if not 'playdede' in sel_domain: sel_domain = ''

       if sel_domain:
           if not 'https' in sel_domain: sel_domain = 'https://' + sel_domain
           if not sel_domain.endswith('/'): sel_domain = sel_domain + '/'
    except:
       pass

    if not sel_domain:
        platformtools.dialog_notification(config.__addon_name + ' - ' + name, '[B][COLOR %s]Error Acceso Dominio Operativo[/B][/COLOR]' % color_alert)
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

    if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red] ' + txt_dom + ' [/COLOR] Desea cambiarlo  ?', 'Memorizado:  [COLOR yellow][B]' + nom_dom + '[/B][/COLOR]', 'Encontrado:     [COLOR cyan][B]' + sel_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', sel_domain, 'playdede')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Último dominio vigente memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')


def del_datos_playdede(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Playdede[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando PoseidonHd2[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Series24[/B][/COLOR]' % color_exec)

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


def manto_domain_serieskao(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SeriesKao[/B][/COLOR]' % color_exec)

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


def manto_domain_seriespapayato(item):
    logger.info()

    channel_json = 'seriespapayato.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SeriesPapayaTo[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_seriespapayato(item):
    logger.info()

    datos = channeltools.get_channel_parameters('seriespapayato')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SeriesPapayaTo')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SeriesPapayaTo', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_seriesplus(item):
    logger.info()

    channel_json = 'seriesplus.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SeriesPlus[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_seriesplus(item):
    logger.info()

    datos = channeltools.get_channel_parameters('seriespapayato')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('SeriesPlus')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - SeriesPlus', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_srnovelas(item):
    logger.info()

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SrNovelas[/B][/COLOR]' % color_exec)

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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando SubTorrents[/B][/COLOR]' % color_exec)

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


def manto_domain_todotorrents(item):
    logger.info()

    channel_json = 'todotorrents.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando TodoTorrents[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_todotorrents(item):
    logger.info()

    datos = channeltools.get_channel_parameters('todotorrents')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('TodoTorrents')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - TodoTorrents', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


def manto_domain_veronline(item):
    logger.info()

    channel_json = 'veronline.json'
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

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando VerOnline[/B][/COLOR]' % color_exec)

    manto_domain_common(item, id, name)


def test_domain_veronline(item):
    logger.info()

    datos = channeltools.get_channel_parameters('veronline')
    if not datos['active']:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]El canal está Inactivo[/B][/COLOR]' % color_avis)
        return

    config.set_setting('developer_test_channels', '')

    try:
        tester.test_channel('VerOnline')
    except:
        platformtools.dialog_notification(config.__addon_name + ' - VerOnline', '[B][COLOR %s]Error comprobación, Reintentelo de Nuevo[/B][/COLOR]' % color_alert)


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

    if id == 'animeflv':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeFlv  -->  [COLOR %s]https://????.animeflv.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'animeid':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://animeid.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeId  -->  [COLOR %s]https://animeid.????/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://animeid.': return

    elif id == 'animeonline':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio AnimeOnline  -->  [COLOR %s]https://???.animeonline.?????/[/COLOR]' % color_avis)

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

        if not domain: domain = 'https://cine-calidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidadLa  -->  [COLOR %s]https://cine-calidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://cine-calidad.': return

    elif id == 'cinecalidadlol':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CineCalidadLol  -->  [COLOR %s]https://???.cinecalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cliversite':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio CliverSite  -->  [COLOR %s]https://????.cliver.??[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cuevana2':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Cuevana2  -->  [COLOR %s]https://???.cuevana2.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cuevana2esp':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Cuevana2Esp  -->  [COLOR %s]https://???.cuevana2espanol.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'cuevana3pro':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Cuevana3Pro  -->  [COLOR %s]https://??.cuevana3.vip[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return


    elif id == 'cuevana3video':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Cuevana3Video  -->  [COLOR %s]https://cuevana3.??[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'divxtotal':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://divxtotal.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio DivxTotal  -->  [COLOR %s]https://divxtotal.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://divxtotal.': return

    elif id == 'dontorrents':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://dontorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio DonTorrents  -->  [COLOR %s]https://dontorrent.????/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://dontorrent.': return

    elif id == 'dontorrentsin':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio DonTorrentsIn  -->  [COLOR %s]https://?????.dontorrent.link/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'elifilms':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://allcalidad.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EliFilms  -->  [COLOR %s]https://allcalidad.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://allcalidad.': return

    elif id == 'elitetorrent':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.elitetorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EliteTorrent  -->  [COLOR %s]https://www.elitetorrent.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.elitetorrent.': return

    elif id == 'elitetorrentnz':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.elitetorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EliteTorrentNz  -->  [COLOR %s]https://www.elitetorrent.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.elitetorrent.': return

    elif id == 'ennovelastv':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EnNovelasTv  -->  [COLOR %s]https://?.ennovelas-tv.com/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'entrepeliculasyseries':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://entrepeliculasyseries.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio EntrePeliculasySeries  -->  [COLOR %s]https://entrepeliculasyseries.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://entrepeliculasyseries.': return

    elif id == 'gnula':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://gnulahd.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Gnula  -->  [COLOR %s]https://gnulahd.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://gnulahd.': return

    elif id == 'gnula24':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Gnula24  -->  [COLOR %s]https://????.seriesgod.cc/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'gnula24h':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Gnula24H  -->  [COLOR %s]https://????.gnula.cc/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'grantorrent':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://grantorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio GranTorrent  -->  [COLOR %s]https://grantorrent.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://grantorrent.': return

    elif id == 'hdfull':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://hdfull'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio HdFull  -->  [COLOR %s]https://hdfull???.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://hdfull': return

    elif id == 'hdfullse':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.hdfull.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio HdFullSe  -->  [COLOR %s]https://www.hdfull.??[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.hdfull.': return

    elif id == 'henaojara':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio HenaOjara  -->  [COLOR %s]https://???.henaojara.com/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'homecine':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://homecine.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio HomeCine  -->  [COLOR %s]https://homecine.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://homecine.': return

    elif id == 'mejortorrentapp':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio MejorTorrentApp  -->  [COLOR %s]https://?????.mejortorrent.??[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'mejortorrentnz':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://mejortorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio MejorTorrentNz  -->  [COLOR %s]https://mejortorrent.???[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://mejortorrent.': return

    elif id == 'mitorrent':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://mitorrent.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio MiTorrent  -->  [COLOR %s]https://mitorrent.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://mitorrent.': return

    elif id == 'novelastop':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio NovelasTop  -->  [COLOR %s]https://???.srnovelashd.??[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'peliculaspro':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://peliculaspro.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PeliculasPro  -->  [COLOR %s]https://peliculaspro.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://peliculaspro.': return

    elif id == 'pelisforte':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisForte  -->  [COLOR %s]https://????.pelisforte.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelismart':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://smartpelis.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisMart  -->  [COLOR %s]https://smatpelis.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://smartpelis.': return

    elif id == 'pelispanda':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelispanda.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPanda  -->  [COLOR %s]https://pelispanda.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelispanda.': return

    elif id == 'pelispediaws':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPediaWs  -->  [COLOR %s]https://????.pelistv.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplus':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelisplusgo.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlus  -->  [COLOR %s]https://pelisplusgo.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelisplusgo.': return

    elif id == 'pelisplushd':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHd  -->  [COLOR %s]https://???.pelisplushd.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplushdlat':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHdLat  -->  [COLOR %s]https://?????.pelisplushd.to/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'pelisplushdnz':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://pelisplushd.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PelisPlusHdNz  -->  [COLOR %s]https://pelisplushd.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://pelisplushd.': return

    elif id == 'playdede':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PlayDede  -->  [COLOR %s]https://www?.playdede.link/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www': return

    elif id == 'poseidonhd2':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio PoseidonHd2  -->  [COLOR %s]https://???.poseidonhd2.??/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'series24':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio Series24  -->  [COLOR %s]https://????.series24.cc/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'serieskao':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://serieskao.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesKao  -->  [COLOR %s]https://serieskao.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://serieskao.': return

    elif id == 'seriespapayato':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesPapayaTo  -->  [COLOR %s]https://????.papayaseries.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'seriesplus':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SeriesPlus  -->  [COLOR %s]https://????.gnula2h.cc/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'srnovelas':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://srnovelas.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SrNovelas  -->  [COLOR %s]https://srnovelas.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://srnovelas.': return

    elif id == 'subtorrents':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio SubTorrents  -->  [COLOR %s]https://????.subtorrents.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://': return

    elif id == 'todotorrents':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://todotorrents.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio TodoTorrents  -->  [COLOR %s]https://todotorrents.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://todotorrents.': return

    elif id == 'veronline':
        config.set_setting('user_test_channel', '')

        if not domain: domain = 'https://www.veronline.'

        new_domain = platformtools.dialog_input(default=domain, heading='Indicar dominio VerOnline  -->  [COLOR %s]https://www.veronline.???/[/COLOR]' % color_avis)

        if new_domain is None: return
        elif new_domain == 'https://www.veronline.': return

    else:
        return

    config.set_setting('user_test_channel', '')

    if not new_domain:
        if domain:
            if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR red][B] Confirma eliminar el Dominio Memorizado ?[/B][/COLOR]', '[COLOR cyan][B] ' + domain + ' [/B][/COLOR]'): 
                config.set_setting('dominio', new_domain, id)

                if item.desde_el_canal:
                    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio eliminado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar el Canal e Ingresar de nuevo en él.[/B][/COLOR]')
                else:
                    if not item.from_action == 'mainlist':
                        platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')
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
            if id == 'cliversite': pass
            elif id == 'cuevana3pro': pass
            elif id == 'cuevana3video': pass
            elif id == 'hdfullse': pass
            elif id == 'mejortorrentapp': pass
            elif id == 'mejortorrentnz': pass
            else: new_domain = new_domain + '/'
        else:
            avisar = False
            if id == 'cliversite': avisar = True
            elif id == 'cuevana3pro': avisar = True
            elif id == 'cuevana3video': avisar = True
            elif id == 'hdfullse': avisar = True
            elif id == 'mejortorrentapp': avisar = True
            elif id == 'mejortorrentnz': avisar = True

            if avisar:
                platformtools.dialog_notification(config.__addon_name + ' - ' + id.capitalize(), '[B][COLOR %s]Dominio sin / al final[/B][/COLOR]' % color_adver)
                return

        if platformtools.dialog_yesno(config.__addon_name + ' - ' + name, '¿ [COLOR yellow][B] Confirma el Dominio informado ?[/B][/COLOR]', '[COLOR cyan][B] ' + new_domain + ' [/B][/COLOR]'): 
            config.set_setting('dominio', new_domain, id)

            if item.desde_el_canal:
                platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar el Canal e Ingresar de nuevo en él.[/B][/COLOR]')
            else:
                if not item.from_action == 'mainlist':
                    platformtools.dialog_ok(config.__addon_name + ' - ' + name, '[COLOR yellow]Dominio memorizado, pero aún NO guardado.[/COLOR]', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar los Ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')

    return

