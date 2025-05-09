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


tests_all_webs = []

procesados = 0

config.set_setting('proxysearch_process', '')
config.set_setting('proxysearch_process_proxies', '')


con_incidencias = ''
no_accesibles = ''
con_problemas = ''

try:
    with open(os.path.join(config.get_runtime_path(), 'dominios.txt'), 'r') as f: txt_status=f.read(); f.close()
except:
    try: txt_status = open(os.path.join(config.get_runtime_path(), 'dominios.txt'), encoding="utf8").read()
    except: txt_status = ''

if txt_status:
    # ~ Incidencias
    bloque = scrapertools.find_single_match(txt_status, 'SITUACION CANALES(.*?)CANALES TEMPORALMENTE DES-ACTIVADOS')

    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")

    for match in matches:
        match = match.strip()

        if '[COLOR moccasin]' in match: con_incidencias += '[B' + match + '/I][/B][/COLOR][CR]'

    # ~ No Accesibles
    bloque = scrapertools.find_single_match(txt_status, 'CANALES PROBABLEMENTE NO ACCESIBLES(.*?)ULTIMOS CAMBIOS DE DOMINIOS')

    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")

    for match in matches:
        match = match.strip()

        if '[COLOR moccasin]' in match: no_accesibles += '[B' + match + '/I][/B][/COLOR][CR]'

    # ~ Con Problemas
    bloque = scrapertools.find_single_match(txt_status, 'CANALES CON PROBLEMAS(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, "[B](.*?)[/B]")

    for match in matches:
        match = match.strip()

        if '[COLOR moccasin]' in match: con_problemas += '[B' + match + '/I][/B][/COLOR][CR]'


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

dominiosplaydede = [
         'https://www9.playdede.link/'
         ]

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

    cfg_excludes = 'proxysearch_excludes'
    channels_excludes = config.get_setting(cfg_excludes, default='')

    channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')
    iniciales_channels_proxies_memorized = channels_proxies_memorized

    proxies_auto = config.get_setting('proxies_auto', default=True)

    proxies_provider = config.get_setting('proxies_provider', default='10')
    if proxies_provider == 10: proxies_todos = True
    else: proxies_todos = False

    if proxies_todos:
        text_pro = 'TODOS'
        if config.get_setting('memorize_channels_proxies', default=True):
            if channels_proxies_memorized: text_pro = 'SOLO [COLOR yellowgreen][B](en los que ya Tengan Proxies)[/COLOR] en'

        if proxies_auto:
            if item.extra:
               if not platformtools.dialog_yesno(config.__addon_name, '[COLOR plum][B]Este proceso Podría necesitar un considerable espacio de tiempo según sus Ajustes actuales de proxies.[/B][/COLOR]', "[COLOR yellow][B]¿ Desea iniciar la búsqueda de proxies para [COLOR cyan][B]" + text_pro + "[/B][/COLOR][COLOR yellow][B] los Canales que los Necesiten ?[/B][/COLOR]"):
                   return
            else:
               if not platformtools.dialog_yesno(config.__addon_name, '[COLOR plum][B]Este proceso Requerirá un considerable consumo de tiempo según su Ajustes actuales de proxies.[/B][/COLOR]', "[COLOR yellow][B]¿ Desea iniciar la búsqueda de proxies para [COLOR cyan][B]" + text_pro + "[/B][/COLOR][COLOR yellow][B] los Canales que los Necesiten ?[/B][/COLOR]"):
                   return
        else:
           platformtools.dialog_ok(config.__addon_name, '[COLOR red][B]En sus Ajustes/Preferenncias (categoría proxies), No tiene el Modo buscar automaticamente.[/B][/COLOR]')
           return

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
                if not platformtools.dialog_yesno(config.__addon_name, '[COLOR yellowgreen][B]¿ Desea SOLO buscar en los Canales con proxies Memorizados Actualmente ?[/B][/COLOR]', '[COLOR yellow][B]En el caso de NO contestar afirmativamente se ELIMINARÁN los proxies memorizados en la actualidad de estos canales ?[/B][/COLOR]'):
                    config.set_setting('channels_proxies_memorized', '')
                    iniciales_channels_proxies_memorized = ''
                else:
                    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando Canales Memorizados[/B][/COLOR]' % color_exec)

                    proceso_seleccionar = False

                    added_memorized = False

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

                        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

                        el_memorizado = "'" + ch['id'] + "'"

                        if config.get_setting(cfg_proxies_channel, default=''):
                            if not el_memorizado in str(channels_proxies_memorized):
                                added_memorized = True

                                channels_proxies_memorized = channels_proxies_memorized + ', ' + el_memorizado

                                if "'''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("'''", "'")
                                if "''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("''", "'")

                                if ", ," in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace(", ,", ',')

                        else:
                            if el_memorizado in str(channels_proxies_memorized):
                                added_memorized = True

                                channels_proxies_memorized = channels_proxies_memorized.replace(el_memorizado + ',', '').strip()
                                channels_proxies_memorized = channels_proxies_memorized.replace(', ' + el_memorizado, '').strip()
                                channels_proxies_memorized = channels_proxies_memorized.replace(el_memorizado, '').strip()

                                if "'''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("'''", "'")
                                if "''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("''", "'")

                                if ", ," in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace(", ,", ',')

                                channels_proxies_memorized = channels_proxies_memorized.strip()

                    if added_memorized:
                        config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

                        channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')
                        iniciales_channels_proxies_memorized = channels_proxies_memorized

        if proceso_seleccionar:
            txt_avis = '¿ Desea Quitar previamente los Proxies Memorizados en TODOS los Canales que intervienen en las Búsquedas ?'
            if item.extra: txt_avis = '¿ Desea Quitar previamente los Proxies Memorizados en los Canales que intervienen en las Búsquedas ?'

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
           if platformtools.dialog_yesno(config.__addon_name, "[COLOR cyan][B]¿ Desea abandonar la búsqueda de proxies para los canales que los necesiten ?[/B][/COLOR]"):
               return

       seleccionados = channels_excluded_list(ret, channels_ids, channels_excludes)

       if str(seleccionados) == '[]': seleccionados = ''
       config.set_setting(cfg_excludes, str(seleccionados))


    channels_excludes = config.get_setting(cfg_excludes, default='')

    config.set_setting('proxysearch_process_proxies', '[]')


    for ch in ch_list:
        if not 'proxies' in ch['notes'].lower(): continue

        if config.get_setting('mnu_simple', default=False):
            if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue
            elif 'exclusivamente al dorama' in ch['notes'].lower(): continue
            elif 'exclusivamente al anime' in ch['notes'].lower(): continue
            elif '+18' in ch['notes']: continue

            elif 'inestable' in ch['clusters']: continue
            elif 'problematic' in ch['clusters']: continue
        else:
            if not config.get_setting('mnu_torrents', default=False) or config.get_setting('search_no_exclusively_torrents', default=False):
                if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue

            if not config.get_setting('mnu_doramas', default=True):
                if 'exclusivamente al dorama' in ch['notes'].lower(): continue

            if not config.get_setting('mnu_animes', default=True):
                if 'exclusivamente al anime' in ch['notes'].lower(): continue

            if not config.get_setting('mnu_adultos', default=True):
                if '+18' in ch['notes']: continue

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

    # ~ los que No intervienen en el buscar general
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

               if not config.get_setting('mnu_torrents', default=False) or config.get_setting('search_no_exclusively_torrents', default=False):
                   if 'enlaces torrent exclusivamente' in ch['notes'].lower(): continue

               if not config.get_setting('mnu_doramas', default=True):
                   if 'exclusivamente al dorama' in ch['notes'].lower(): continue

               if not config.get_setting('mnu_animes', default=True):
                   if 'exclusivamente al anime' in ch['notes'].lower(): continue

               if not config.get_setting('mnu_adultos', default=True):
                   if '+18' in ch['notes']: continue

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


               cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

               el_memorizado = "'" + ch['id'] + "'"

               if config.get_setting(cfg_proxies_channel, default=''):
                   if not el_memorizado in str(channels_proxies_memorized):
                       added_memorized = True

                       channels_proxies_memorized = channels_proxies_memorized + ', ' + el_memorizado

                       if "'''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("'''", "'")
                       if "''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("''", "'")

                       if ", ," in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace(", ,", ',')

               else:
                   if el_memorizado in str(channels_proxies_memorized):
                       added_memorized = True

                       channels_proxies_memorized = channels_proxies_memorized.replace(el_memorizado + ',', '').strip()
                       channels_proxies_memorized = channels_proxies_memorized.replace(', ' + el_memorizado, '').strip()
                       channels_proxies_memorized = channels_proxies_memorized.replace(el_memorizado, '').strip()

                       if "'''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("'''", "'")
                       if "''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("''", "'")

                       if ", ," in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace(", ,", ',')

                       channels_proxies_memorized = channels_proxies_memorized.strip()

               if added_memorized:
                   config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

                   channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')
                   iniciales_channels_proxies_memorized = channels_proxies_memorized

    config.set_setting('proxysearch_process', '')
    config.set_setting('proxysearch_process_proxies', '')

    if procesados == 0:
        if iniciales_channels_proxies_memorized:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales a Proceasar según los Memorizados[/B][/COLOR]' % color_adver)
        else:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales a Proceasar según sus Parámetros[/B][/COLOR]' % color_adver)
        return

    if tests_all_webs:
        if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]Canales con Proxies Quitados.[/B][/COLOR]', '[COLOR yellow][B]Desea Verlos ?[/B][/COLOR]'):
            txt_cambiados = ''

            for cambiado in tests_all_webs:
                txt_cambiados += cambiado + '[CR]'

                platformtools.dialog_textviewer('Comprobar Canales con Proxies Quitados', txt_cambiados)

    if config.get_setting('memorize_channels_proxies', default=True):
       txt = 'Revise los canales Memorizados, porque podría ser que algún canal NO los necesite ó viceversa. '
    else:
       txt = 'Revise los canales, porque podría ser que algún canal NO los necesite ó viceversa. '
       if not item.extra:
           txt += 'Para ello bastará con entrar al canal y ver si se presentan listas en cualquiera de sus opciones, '
           txt += 'si procede deberá Eliminar los proxies memorizados ó Configurarlos de Nuevo dentro del canal.'

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

    global tests_all_webs

    global procesados

    if txt_status:
        if con_incidencias:
           if channel_name in str(con_incidencias): return

        if no_accesibles:
           if channel_name in str(no_accesibles): return

        if con_problemas:
           if channel_name in str(con_problemas): return

    channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')

    if config.get_setting('memorize_channels_proxies', default=True):
        if channels_proxies_memorized:
            el_memorizado = "'" + channel_id + "'"

            if iniciales_channels_proxies_memorized:
                if not el_memorizado in str(channels_proxies_memorized): return

            channel_json = channel_id + '.json'
            filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)
            existe = filetools.exists(filename_json)
            if not existe: return

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

          if not host:
              if channel_id == 'hdfull':
                  try:
                     data = httptools.downloadpage('https://dominioshdfull.com/').data

                     bloque = scrapertools.find_single_match(data, 'dominios operativos actualizados(.*?)<script>')

                     operative_domains = scrapertools.find_multiple_matches(bloque, 'href="(.*?)"')

                     if not operative_domains: host = dominioshdfull[0]
                     else:
                        host = operative_domains[0]
                        if not host.endswith('/'): host = host + '/'
                  except:
                     host = dominioshdfull[0]

              elif channel_id == 'playdede':
                  try:
                     data = httptools.downloadpage('https://privacidad.me/@playdede/').data

                     sel_domain = scrapertools.find_single_match(data, '>Dirección actual:(.*?)</a>').strip()

                     if sel_domain:
                         sel_domain = sel_domain.lower()
                         if not 'playdede' in sel_domain: sel_domain = ''

                     if sel_domain:
                         if not 'https' in sel_domain: sel_domain = 'https://' + sel_domain
                         if not sel_domain.endswith('/'): sel_domain = sel_domain + '/'

                         if sel_domain in str(dominiosplaydede):
                             host = sel_domain
                  except:
                     host = dominiosplaydede[0]

          if not host:
              part_py = 'def mainlist'

              if 'ver_stable_chrome' in data: part_py = 'ver_stable_chrome'

              elif 'CLONES =' in data or 'clones =' in data: part_py = 'clones  ='
              elif 'CLASS login_' in data or 'class login_' in data: part_py = 'class login_'

              elif 'def do_make_login_logout' in data: part_py = 'def do_make_login_logout'
              elif 'def login' in data: part_py = 'def login'
              elif 'def logout' in data: part_py = 'def logout'

              elif 'def configurar_proxies' in data: part_py = 'def configurar_proxies'
              elif 'def do_downloadpage' in data: part_py = 'def do_downloadpage'

              bloc = scrapertools.find_single_match(data.lower(), '(.*?)' + part_py)
              bloc = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', bloc)

              host = scrapertools.find_single_match(str(bloc), "host = '(.*?)'")
              if not host: host = scrapertools.find_single_match(str(bloc), 'host = "(.*?)"')

              if not host: host = scrapertools.find_single_match(str(bloc), "dominios =.*?'(.*?)'")
              if not host: host = scrapertools.find_single_match(str(bloc), 'dominios =.*?"(.*?)"')

              if not host: host = scrapertools.find_single_match(str(bloc), "host.*?'(.*?)'")
              if not host: host = scrapertools.find_single_match(str(bloc), 'host.*?"(.*?)"')

              ant_hosts = scrapertools.find_single_match(str(bloc), 'ant_hosts.*?=.*?(.*?)]')
              if not ant_hosts: ant_hosts = scrapertools.find_single_match(str(bloc), "ant_hosts.*?=.*?(.*?)]")

    host = host.strip()

    if not host or not '//' in host:
        el_canal = ('Se ignora este canal en el proceso, porque Falta seleccionar que dominio "HOST" se utilizará  [B][COLOR %s]' + channel_name) % color_alert

        platformtools.dialog_ok(config.__addon_name, el_canal + '[/COLOR][/B]')
        return

    headers = {}

    cfg_proxies_channel = 'channel_' + channel_id + '_proxies'

    if not config.get_setting(cfg_proxies_channel, default=''):
        response = httptools.downloadpage(host, headers=headers, raise_weberror=False)

        if response.sucess == True:
            if len(response.data) >= 1000:
                if config.get_setting('memorize_channels_proxies', default=True):
                   el_memorizado = "'" + channel_id + "'"
                   if el_memorizado in str(channels_proxies_memorized):
                       channels_proxies_memorized = str(channels_proxies_memorized).replace(el_memorizado + ',', '').replace(el_memorizado, '').strip()

                       if "'''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("'''", "'")
                       if "''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("''", "'")

                       if ", ," in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace(", ,", ',')

                       config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

                tests_all_webs.append(channel_name)

                el_canal = ('[B][COLOR %s]' + channel_name + '[/COLOR][/B]') % color_exec
                el_canal += ('[B][COLOR %s] no los necesita[/COLOR][/B]') % color_infor
                platformtools.dialog_notification(config.__addon_name, el_canal)
                return
    else:
        response = httptools.downloadpage(host, headers=headers, raise_weberror=False)

        if response.sucess == True:
            if len(response.data) >= 1000:
                if config.get_setting('memorize_channels_proxies', default=True):
                    el_memorizado = "'" + channel_id + "'"
                    if el_memorizado in str(channels_proxies_memorized):
                        channels_proxies_memorized = str(channels_proxies_memorized).replace(el_memorizado + ',', '').replace(el_memorizado, '').strip()

                        if "'''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("'''", "'")
                        if "''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("''", "'")

                        if ", ," in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace(", ,", ',')

                        config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

                tests_all_webs.append(channel_name)

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
               if not channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized + el_memorizado
               else: channels_proxies_memorized = channels_proxies_memorized + ', ' + el_memorizado

               if "'''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("'''", "'")
               if "''" in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace("''", "'")

               if ", ," in channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized.replace(", ,", ',')

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
