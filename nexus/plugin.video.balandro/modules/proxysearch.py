# -*- coding: utf-8 -*-

import os, re, xbmcgui

from platformcode import config, logger, platformtools
from core.item import Item
from core import channeltools, scrapertools, httptools, proxytools, filetools


color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


procesados = 0


config.set_setting('proxysearch_process', '')
config.set_setting('proxysearch_process_proxies', '')


channels_poe = [
        ['gdrive', 'https://drive.google.com/drive/']
        ]


def proxysearch_all(item):
    logger.info()

    your_ip = ''

    try:
       data = httptools.downloadpage('http://httpbin.org/ip').data
       data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
       your_ip = scrapertools.find_single_match(str(data), '.*?"origin".*?"(.*?)"')
    except:
       pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://ipinfo.io/ip').data
        except: pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://www.icanhazip.com/').data
        except: pass

    if not your_ip:
        platformtools.dialog_ok(config.__addon_name, '[COLOR red][B]Parece que NO hay conexión con internet.[/B][/COLOR]', 'Compruebelo realizando cualquier Búsqueda, desde un Navegador Web ')

    proxies_auto = config.get_setting('proxies_auto', default=True)

    proxies_provider = config.get_setting('proxies_provider', default='10')
    if proxies_provider == 10: proxies_todos = True
    else: proxies_todos = False

    if proxies_todos:
        if proxies_auto:
            if item.extra:
               if not platformtools.dialog_yesno(config.__addon_name, '[COLOR plum][B]Este proceso Podría necesitar un considerable espacio de tiempo según su configuración actual de proxies.[/B][/COLOR]', "[COLOR yellow][B]¿ Desea iniciar la búsqueda de proxies para TODOS los canales que los necesiten ?[/B][/COLOR]"):
                   return
            else:
               if not platformtools.dialog_yesno(config.__addon_name, '[COLOR plum][B]Este proceso Requerirá un considerable consumo de tiempo según su configuración actual de proxies.[/B][/COLOR]', "[COLOR yellow][B]¿ Desea iniciar la búsqueda de proxies para TODOS los canales que los necesiten ?[/B][/COLOR]"):
                   return
        else:
           platformtools.dialog_ok(config.__addon_name, '[COLOR red][B]En los Ajustes categoría proxies de la configuración, No tiene el Modo buscar automaticamente.[/B][/COLOR]')
           return


    cfg_excludes = 'proxysearch_excludes'
    channels_excludes = config.get_setting(cfg_excludes, default='')

    channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')
    iniciales_channels_proxies_memorized = channels_proxies_memorized


    proceso_seleccionar = True

    filtros = {'searchable': True}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        if channels_list_status == 1: filtros = {'searchable': True, 'status': 0}
        else: filtros = {'searchable': True, 'status': 1}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
        if config.get_setting('memorize_channels_proxies', default=True):
            if channels_proxies_memorized:
                if not platformtools.dialog_yesno(config.__addon_name, '[COLOR cyan][B]¿ Desea SOLO buscar en los canales con proxies memorizados actualmente ?[/B][/COLOR]', '[COLOR yellow][B]En el caso de NO contestar afirmativamente se Eliminaran los proxies memorizados en la actualidad de estos canales ?[/B][/COLOR]'):
                    config.set_setting('channels_proxies_memorized', '')
                    iniciales_channels_proxies_memorized = ''
                else: proceso_seleccionar = False

        if proceso_seleccionar:
            txt_avis = '¿ Desea Quitar previamente los Proxies memorizados en TODOS los canales que intervienen en las Búsquedas ?'
            if item.extra: txt_avis = '¿ Desea Quitar previamente los Proxies memorizados en los canales que intervienen en las Búsquedas ?'

            if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]' + txt_avis + '[/B][/COLOR]'):
               for ch in ch_list:
                   if not 'proxies' in ch['notes'].lower(): continue

                   if item.extra:
                       if item.extra == 'movies':
                           if not 'movie' in ch['search_types']: continue

                       elif item.extra == 'tvshows':
                             if not 'tvshow' in ch['search_types']: continue

                       elif item.extra == 'mixed':
                             if not 'all' in ch['search_types']: continue

                       elif item.extra == 'documentaries':
                             if not 'documentary' in ch['search_types']: continue

                       elif item.extra == 'torrents':
                             if not 'torrent' in ch['categories']: continue

                       else:
                            if 'movie' in ch['search_types']: pass
                            elif 'tvshow' in ch['search_types']: pass
                            elif 'documentary' in ch['search_types']: pass
                            elif 'torrent' in ch['categories']: pass
                            elif 'all' in ch['search_types']: pass
                            else: continue

                   # por NAME vensiones anteriores a 2.0
                   cfg_proxies_channel = 'channel_' + ch['name'] + '_proxies'

                   if config.get_setting(cfg_proxies_channel, default=''):
                       config.set_setting(cfg_proxies_channel, '')

                       cfg_proxytools_max_channel = 'channel_' + ch['name'] + '_proxytools_max'
                       if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')

                       cfg_proxytools_provider = 'channel_' + ch['name'] + '_proxytools_provider'
                       if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')

                   # por ID
                   cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
                   cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
                   cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

                   if not config.get_setting(cfg_proxies_channel, default=''):
                       if not config.get_setting(cfg_proxytools_max_channel, default=''):
                           if not config.get_setting(cfg_proxytools_provider, default=''): continue

                   if config.get_setting(cfg_proxies_channel, default=''): config.set_setting(cfg_proxies_channel, '')
                   if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')
                   if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')


               proceso_seleccionar = False

               if channels_excludes:
                   config.set_setting(cfg_excludes, '')
                   platformtools.dialog_ok(config.__addon_name, '[B][COLOR %s]Proxies y sus canales excluidos eliminados[/B][/COLOR]' % color_infor)
               else:
                   platformtools.dialog_ok(config.__addon_name, '[B][COLOR %s]Proxies eliminados en los canales que interviene en las Búsquedas[/B][/COLOR]' % color_infor)

               config.set_setting('channels_proxies_memorized', '')
               iniciales_channels_proxies_memorized = ''

    if proceso_seleccionar:
        only_includes = config.get_setting('search_included_all', default='')
        if only_includes:
            if not platformtools.dialog_yesno(config.__addon_name, '[COLOR yellowgreen][B]¿ Quiere mantener los canales que actualmente están SOLO Incluidos en el Buscar ?[/B][/COLOR]'):
                config.set_setting('search_included_all', '')

        if not channels_excludes:
            if not platformtools.dialog_yesno(config.__addon_name, '[COLOR yellow][B]¿ Quiere excluir canales en la Búsqueda Global de Configurar proxies a usar en los canales que los necesiten ?[/B][/COLOR]'):
                proceso_seleccionar = False


    filtros = {'searchable': True}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        if channels_list_status == 1: filtros = {'searchable': True, 'status': 0}
        else: filtros = {'searchable': True, 'status': 1}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if proceso_seleccionar:
       preselect = []
       channels_ids = []
       opciones = []

       i = 0
       for ch in ch_list:
           if not 'proxies' in ch['notes'].lower(): continue

           i =+1

       if i == 0:
           platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales con proxies memorizados[/B][/COLOR]' % color_adver)
           return

       if channels_excludes:
           channels_orden = []

           i = 0
           for ch in ch_list:
               channels_orden.append(ch['id'])
               i += 1

           channels_preselct = str(channels_excludes).replace('[', '').replace(']', ',')

           matches = scrapertools.find_multiple_matches(channels_preselct, "(.*?), '(.*?)',")
           for ch_nro, ch_name in matches:
               if not ch_name in channels_orden[int(ch_nro)]:
                   tex1 = '[COLOR plum]El orden de la lista de los canales ha variado respecto a su lista anterior (Preferidos, Desactivados, Inactivos ó Anulados).[/COLOR]'
                   tex2 = '[COLOR cyan][B]Deberá seleccionar de nuevo los canales a excluir deseados.[/B][/COLOR]'
                   tex3 = '[COLOR red]Porque se eliminan los canales memorizados para excluirlos de [COLOR yellow] Configurar proxies a usar [/COLOR]'
                   platformtools.dialog_ok(config.__addon_name, tex1, tex2, tex3)
                   config.set_setting(cfg_excludes, '')
                   preselect = []
                   break

               ch_nro = ch_nro.strip()
               preselect.append(int(ch_nro))

       i = 0
       for ch in ch_list:
           if not 'proxies' in ch['notes'].lower(): continue

           if not channels_excludes: preselect.append(i)
           channels_ids.append(ch['id'])
           i += 1

       for ch in ch_list:
           if not 'proxies' in ch['notes'].lower(): continue

           cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
           cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
           cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

           if not config.get_setting(cfg_proxies_channel, default=''):
               if not config.get_setting(cfg_proxytools_max_channel, default=''):
                   if not config.get_setting(cfg_proxytools_provider, default=''): continue

           info = ''

           if channels_excludes:
               channels_preselct = str(channels_excludes).replace('[', '').replace(']', ',')
               if ("'" + ch['id'] + "'") in str(channels_preselct): info = info + '[COLOR moccasin][B]EXCLUIDO [/B][/COLOR]'

           if ch['status'] == 1: info = info + '[B][COLOR %s][I] Preferido [/I][/B][/COLOR]' % color_list_prefe
           elif ch['status'] == -1: info = info + '[B][COLOR %s][I] Desactivado [/I][/B][/COLOR]' % color_list_inactive

           if 'dominios' in ch['notes'].lower():
               dominio = config.get_setting('channel_' + ch['id'] + '_dominio', default='')
               if dominio:
                   dominio = dominio.replace('https://', '').replace('/', '')
                   info = info + '[B][COLOR cyan] %s [/B][/COLOR]' % dominio

           if config.get_setting(cfg_proxies_channel, default=''): info = info + '[B][COLOR %s] Proxies [/B][/COLOR]' % color_list_proxies
           elif config.get_setting(cfg_proxytools_provider, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'
           elif config.get_setting(cfg_proxytools_max_channel, default=''): info = info + '[COLOR yellowgreen][B] Sin proxies [/B][/COLOR]'

           tipos = ch['search_types']
           tipos = str(tipos).replace('[', '').replace(']', '').replace("'", '')
           tipos = str(tipos).replace('movie', 'Películas').replace('tvshow', 'Series').replace('documentary', 'Documentales').replace('all,', '')

           if info: info = info + '  '
           info = info + '[COLOR mediumspringgreen][B]' + tipos + '[/B][/COLOR]'

           idiomas = ch['language']
           idiomas = str(idiomas).replace('[', '').replace(']', '').replace("'", '')
           idiomas = str(idiomas).replace('cast', 'Esp').replace('lat', 'Lat').replace('vose', 'Vose')

           if info: info = info + '  '
           info = info + '[COLOR mediumaquamarine]' + idiomas + '[/COLOR]'

           it = xbmcgui.ListItem(ch['name'], info)
           it.setArt({'thumb': ch['thumbnail']})
           opciones.append(it)

       ret = xbmcgui.Dialog().multiselect('Excluir canales en las búsquedas de [COLOR yellow] Proxies [/COLOR]', opciones, preselect=preselect, useDetails=True)

       if ret is None:
           if platformtools.dialog_yesno(config.__addon_name, "[COLOR tan][B]¿ Desea abandonar la búsqueda de proxies para TODOS los canales que los necesiten ?[/B][/COLOR]"):
               return

       seleccionados = channels_excluded_list(ret, channels_ids, channels_excludes)

       if str(seleccionados) == '[]': seleccionados = ''
       config.set_setting(cfg_excludes, str(seleccionados))


    channels_excludes = config.get_setting(cfg_excludes, default='')

    config.set_setting('proxysearch_process_proxies', '[]')


    for ch in ch_list:
        if not 'proxies' in ch['notes'].lower(): continue

        if config.get_setting('mnu_simple', default=False):
            if 'inestable' in ch['clusters']: continue
            elif 'problematic' in ch['clusters']: continue
        else:
            if not config.get_setting('mnu_torrents', default=False) or config.get_setting('search_no_exclusively_torrents', default=False):
                if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue

            if config.get_setting('mnu_problematicos', default=False):
                if 'problematic' in ch['clusters']: continue

            if config.get_setting('search_no_inestables', default=False):
                if 'inestable' in ch['clusters']: continue

        if channels_excludes:
            channels_preselct = str(channels_excludes).replace('[', '').replace(']', ',')
            if ("'" + ch['id'] + "'") in str(channels_preselct):
                platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por excluido[/COLOR][/B]' % color_exec)
                continue

        if item.extra:
            if item.extra == 'movies':
                if not 'movie' in ch['search_types']: continue
            elif item.extra == 'tvshows':
                if not 'tvshow' in ch['search_types']: continue
            elif item.extra == 'mixed':
                if not 'all' in ch['search_types']: continue
            elif item.extra == 'documentaries':
                if not 'documentary' in ch['search_types']: continue
            elif item.extra == 'torrents':
                if not 'torrent' in ch['categories']: continue
            else:
                if 'Puede requerir el uso de proxies' in ch['notes']: pass
                elif not 'all' in ch['search_types']: continue

        config.set_setting('proxysearch_process', True)

        proxysearch_channel(item, ch['id'], ch['name'], iniciales_channels_proxies_memorized)


    # ~ los que No intervienen en el buscar ganeral
    if not config.get_setting('mnu_simple', default=False):
        filtros = {'searchable': False}

        channels_list_status = config.get_setting('channels_list_status', default=0)
        if channels_list_status > 0:
            if channels_list_status == 1: filtros = {'searchable': False, 'status': 0}
            else: filtros = {'searchable': False, 'status': 1}

        ch_list = channeltools.get_channels_list(filtros=filtros)

        if ch_list:
           for ch in ch_list:
               if not 'proxies' in ch['notes'].lower(): continue

               if channels_excludes:
                   channels_preselct = str(channels_excludes).replace('[', '').replace(']', ',')
                   if ("'" + ch['id'] + "'") in str(channels_preselct):
                       platformtools.dialog_notification(ch['name'], '[B][COLOR %s]Ignorado por excluido[/COLOR][/B]' % color_exec)
                       continue

               if item.extra:
                   if item.extra == 'movies':
                       if not 'movie' in ch['search_types']: continue
                   elif item.extra == 'tvshows':
                       if not 'tvshow' in ch['search_types']: continue
                   elif item.extra == 'mixed':
                       if not 'all' in ch['search_types']: continue
                   elif item.extra == 'documentaries':
                       if not 'documentary' in ch['search_types']: continue
                   elif item.extra == 'torrents':
                       if not 'torrent' in ch['categories']: continue
                   else:
                       if 'Puede requerir el uso de proxies' in ch['notes']: pass
                       elif not 'all' in ch['search_types']: continue

               config.set_setting('proxysearch_process', True)

               proxysearch_channel(item, ch['id'], ch['name'], iniciales_channels_proxies_memorized)


    config.set_setting('proxysearch_process', '')
    config.set_setting('proxysearch_process_proxies', '')


    if procesados == 0:
        if iniciales_channels_proxies_memorized:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales a Proceasar según los Memorizados[/B][/COLOR]' % color_adver)
        else:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales a Proceasar según sus Parámetros[/B][/COLOR]' % color_adver)
        return

    if config.get_setting('memorize_channels_proxies', default=True):
       txt = 'Revise los canales Memorizados, porque podría ser que algún canal no los necesite ó viceversa. '
    else:
       txt = 'Revise los canales, porque podría ser que algún canal no los necesite ó viceversa. '
       if not item.extra:
           txt += 'Para ello bastará con entrar al canal y ver si se presentan listas en cualquiera de sus opciones, '
           txt += 'si procede deberá eliminar los proxies memorizados ó configurarlos de nuevo dentro del canal.'

    platformtools.dialog_ok(config.__addon_name, 'Proceso configurar proxies a usar y su memorización Finalizado.', '[COLOR yellow][B]' + txt + '[/COLOR][/B]')


def channels_excluded_list(ret, channels_ids, channels_excludes):
    logger.info()

    channel_sel = []
    seleccionados = []

    if channels_excludes:
        for ch in ret:
            channel_sel.append(ch)
    else:
        nro_sel = 0

        for ch in ret:
            if not ch == nro_sel:
                channel_sel.append(nro_sel)
                nro_sel += 1

                while not (nro_sel == ch):
                    channel_sel.append(nro_sel)
                    nro_sel += 1

            nro_sel += 1

    for ch_sel in channel_sel:
        seleccionados.append(ch_sel)
        i_id = 0

        for channel_id in channels_ids:
            if ch_sel == i_id: seleccionados.append(channel_id)
            i_id += 1

    return seleccionados


def proxysearch_channel(item, channel_id, channel_name, iniciales_channels_proxies_memorized):
    logger.info()

    global procesados


    channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')

    if config.get_setting('memorize_channels_proxies', default=True):
        if channels_proxies_memorized:
            el_memorizado = "'" + channel_id + "'"

            if iniciales_channels_proxies_memorized:
                if not el_memorizado in str(channels_proxies_memorized): return

            cfg_proxies_channel = 'channel_' + channel_id + '_proxies'

            config.set_setting(cfg_proxies_channel, '')

            cfg_proxytools_max_channel = 'channel_' + channel_id + '_proxytools_max'
            cfg_proxytools_provider = 'channel_' + channel_id + '_proxytools_provider'

            if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')
            if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')

    procesados += 1

    only_includes = config.get_setting('search_included_all', default='')
    if only_includes:
        only_channels_includes = str(only_includes).replace('[', '').replace(']', ',')
        if not ("'" + channel_id + "'") in str(only_channels_includes):
            el_canal = ('[B][COLOR %s]Ignorado no está en Incluidos[/B][/COLOR]') % color_infor
            platformtools.dialog_notification(config.__addon_name + ' [COLOR cyan][B]' + channel_name + '[/COLOR][/B]' , el_canal)
            return

    cfg_searchable_channel = 'channel_' + channel_id + '_no_searchable'
    if config.get_setting(cfg_searchable_channel, default=False):
        el_canal = ('[B][COLOR %s]Ignorado por Excluido[/B][/COLOR]') % color_infor
        platformtools.dialog_notification(config.__addon_name + ' [COLOR cyan][B]' + channel_name + '[/COLOR][/B]' , el_canal)
        return

    el_canal = '[B][COLOR %s]' % color_exec
    el_canal += channel_name
    el_canal += '[COLOR %s] procesando ...[/COLOR][/B]' % color_avis
    platformtools.dialog_notification('Buscar proxies', el_canal)

    channel_py = channel_id + '.py'
    filename_py = os.path.join(config.get_runtime_path(), 'channels', channel_py)

    dominio = config.get_setting('dominio', channel_id, default='')

    host = ''

    channel_poe = "'" + channel_id + "'"
    esta_en_poe = False

    if channel_poe in str(channels_poe):
        for x in channels_poe:
            if x[0] == channel_id:
               esta_en_poe = True
               channel_poe = x[0]
               host = x[1]
               break

    if not esta_en_poe:
       if dominio: host = dominio
       else:
           try:
              data = filetools.read(filename_py)
           except:
              el_canal = ('Se ignora este canal en el proceso, no se pudo acceder a su módulo ' + channel_py  + '[B][COLOR %s] en el caso de que requiera proxies, deberá efectuar esta Configuracíon dentro del propio canal.') % color_alert
              platformtools.dialog_ok(config.__addon_name + ' ' + channel_name , el_canal + '[/COLOR][/B]')
              return

           part_py = 'def mainlist'

           if 'CLONES ' in data or 'clones ' in data: part_py = 'clones '
           elif 'CLASS ' in data or 'class ' in data: part_py = 'class '

           elif 'def login' in data: part_py = 'def login'
           elif 'def configurar_proxies' in data: part_py = 'def configurar_proxies'
           elif 'def do_downloadpage' in data: part_py = 'def do_downloadpage'

           bloc = scrapertools.find_single_match(data.lower(), '(.*?)' + part_py)
           if 'ant_hosts' in bloc: bloc = scrapertools.find_single_match(data.lower(), '(.*?)ant_hosts')

           bloc = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', bloc)

           host = scrapertools.find_single_match(str(bloc), ".*?host = '(.*?)'")
           if not host: host = scrapertools.find_single_match(str(bloc), '.*?host = "(.*?)"')

           if not host: host = scrapertools.find_single_match(bloc, '.*?host.*?"(.*?)"')
           if not host: host = scrapertools.find_single_match(bloc, ".*?host.*?'(.*?)'")

    host = host.strip()

    if not host or not '//' in host:
        el_canal = ('Se ignora este canal en el proceso, porque Falta seleccionar que dominio "HOST" se utilizará  [B][COLOR %s]' + channel_name) % color_alert

        platformtools.dialog_ok(config.__addon_name, el_canal + '[/COLOR][/B]')
        return

    cfg_proxies_channel = 'channel_' + channel_id + '_proxies'

    if not config.get_setting(cfg_proxies_channel, default=''):
        response = httptools.downloadpage(host, raise_weberror=False)

        if response.sucess == True:
            if len(response.data) > 999:
                if config.get_setting('memorize_channels_proxies', default=True):
                   el_memorizado = "'" + channel_id + "'"
                   if el_memorizado in str(channels_proxies_memorized):
                       channels_proxies_memorized = str(channels_proxies_memorized).replace(el_memorizado + ',', '').replace(el_memorizado, '').strip()
                       config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

                el_canal = ('[B][COLOR %s]' + channel_name + '[/COLOR][/B]') % color_exec
                el_canal += ('[B][COLOR %s] no los necesita[/COLOR][/B]') % color_infor
                platformtools.dialog_notification(config.__addon_name, el_canal)
                return
    else:
        response = httptools.downloadpage(host, raise_weberror=False)

        if response.sucess == True:
            if len(response.data) > 999:
                if config.get_setting('memorize_channels_proxies', default=True):
                    el_memorizado = "'" + channel_id + "'"
                    if el_memorizado in str(channels_proxies_memorized):
                        channels_proxies_memorized = str(channels_proxies_memorized).replace(el_memorizado + ',', '').replace(el_memorizado, '').strip()
                        config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

                el_canal = ('[B][COLOR %s]Proxies quitados ') % color_alert
                el_canal += ('[COLOR %s]' + channel_name + '[/COLOR][/B]') % color_exec
                platformtools.dialog_notification(config.__addon_name, el_canal)

                config.set_setting(cfg_proxies_channel, '')

                cfg_proxytools_max_channel = 'channel_' + channel_id + '_proxytools_max'
                cfg_proxytools_provider = 'channel_' + channel_id + '_proxytools_provider'

                if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')
                if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')
                return

    if config.get_setting('memorize_channels_proxies', default=True):
        el_memorizado = "'" + channel_id + "'"

        if not channels_proxies_memorized:
            channels_proxies_memorized = el_memorizado
            config.set_setting('channels_proxies_memorized', channels_proxies_memorized)
        else:
           if not el_memorizado in str(channels_proxies_memorized):
               if not channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized  + el_memorizado + ','
               else: channels_proxies_memorized = channels_proxies_memorized + ' ,' + el_memorizado

               config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

        if el_memorizado in str(channels_proxies_memorized):
            return proxytools.configurar_proxies_canal(channel_name, host)

        return

    return proxytools.configurar_proxies_canal(channel_name, host)


def channels_proxysearch_del(item):
    logger.info()

    cfg_excludes = 'proxysearch_excludes'
    canales_excluidos = config.get_setting(cfg_excludes, default='')

    canales_excluidos = scrapertools.find_multiple_matches(str(canales_excluidos), "(.*?), '(.*?)'")

    txt_excluidos = ''

    for orden_nro, id_canal in canales_excluidos:
        if not txt_excluidos: txt_excluidos = id_canal.capitalize()
        else: txt_excluidos += (', ' + id_canal.capitalize())

    if not platformtools.dialog_yesno(config.__addon_name, '[COLOR plum][B]' + str(txt_excluidos) + '[/B][/COLOR]', '[COLOR red][B]¿ Desea anular los canales memorizados para excluirlos de Configurar Proxies a usar ?[/B][/COLOR]'):
        return

    config.set_setting(cfg_excludes, '')

    platformtools.itemlist_refresh()
