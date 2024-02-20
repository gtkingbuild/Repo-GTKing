# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3: PY3 = False
else: PY3 = True

import os, time, re

import xbmcgui

from threading import Thread

from core import httptools, proxytoolsz, scrapertools
from platformcode import config, logger, platformtools


item = []


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis  = config.get_setting('notification_avis_color', default='yellow')
color_exec  = config.get_setting('notification_exec_color', default='cyan')


HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = config.get_setting('httptools_timeout', default=15)
if HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT == 0: HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = None


default_provider = 'proxyscrape.com'
all_providers = 'All-providers'
private_list = 'Lista-proxies.txt'

proxies_totales = config.get_setting('proxies_totales', default=False)
proxies_totales_limit = config.get_setting('proxies_totales_limit', default=500)

proxies_extended = config.get_setting('proxies_extended', default=False)
proxies_search_extended = config.get_setting('proxies_search_extended', default=False)

proxies_recommended = config.get_setting('proxies_recommended', default=False)


tot_all_providers = 27

opciones_provider = [
        'spys.one',
        'hidemy.name',
        'httptunnel.ge',
        'proxynova.com',
        'free-proxy-list',
        'spys.me',
        default_provider,
        'proxyservers.pro',
        'us-proxy.org',
        'proxy-list.download',
        all_providers,
        'proxysource.org',
        'silverproxy.xyz',
        'dailyproxylists.com',
        'sslproxies.org',
        'clarketm',
        'google-proxy.net',
        'ip-adress.com',
        'proxydb.net',
        'hidester.com',
        'geonode.com',
        'mmpx12',
        'roosterkid',
        'almroot',
        'shiftytr',
        'mertguvencli',
        private_list
        ]

if proxies_extended:
    opciones_provider.append('z-coderduck')
    opciones_provider.append('z-echolink')
    opciones_provider.append('z-free-proxy-list.anon')
    opciones_provider.append('z-free-proxy-list.com')
    opciones_provider.append('z-free-proxy-list.uk')
    opciones_provider.append('z-github')
    opciones_provider.append('z-opsxcq')
    opciones_provider.append('z-proxy-daily')
    opciones_provider.append('z-proxy-list.org')
    opciones_provider.append('z-proxyhub')
    opciones_provider.append('z-proxyranker')
    opciones_provider.append('z-xroxy')
    opciones_provider.append('z-socks')
    opciones_provider.append('z-squidproxyserver')


opciones_recommended = [
        'almroot',
        'mmpx12',
        default_provider,
        'us-proxy.org',
        'z-free-proxy-list.anon'
        ]


opciones_tipo = ['Cualquier tipo', 'Elite', 'Anonymous', 'Transparent']
opciones_pais = ['Cualquier país', 'ES', 'US', 'FR', 'DE', 'CZ', 'IT', 'CH', 'NL', 'MX', 'RU', 'HK', 'SG']

proxies_auto = config.get_setting('proxies_auto', default=True)
proxies_limit = config.get_setting('proxies_limit', default=True)

proxies_provider = config.get_setting('proxies_provider', default='10')
if proxies_provider == 10: proxies_todos = True
else: proxies_todos = False

proxies_proces = config.get_setting('proxies_proces', default=True)
proxies_tipos = config.get_setting('proxies_tipos', default=False)
proxies_paises = config.get_setting('proxies_paises', default=False)
proxies_maximo = config.get_setting('proxies_maximo', default=True)

proxies_list = config.get_setting('proxies_list', default=False)
proxies_help = config.get_setting('proxies_help', default=True)

if not proxies_list: opciones_provider.remove(private_list)


providers_preferred = config.get_setting('providers_preferred', default='')

if providers_preferred:
    providers_preferred = str(providers_preferred).lower()

    if not providers_preferred.endswith == ',': providers_preferred = providers_preferred + ','

    providers_preferred = providers_preferred.replace(',,', '',)

    provs_preferred = scrapertools.find_multiple_matches(providers_preferred, '(.*?),')

    provs_ok = True

    for prov_preferred in provs_preferred:
        prov_preferred = prov_preferred.strip()

        if not prov_preferred: continue

        if not prov_preferred in str(list(opciones_provider)):
            provs_ok = False
            break

    if not provs_ok:
        platformtools.dialog_ok(config.__addon_name, 'Tiene informados en ajustes [COLOR wheat][B]Proveedores Preferidos[/B][/COLOR] de proxies [COLOR coral][B]Desconocidos[/B][/COLOR].', 'No se tendrán en cuenta [COLOR yellow][B]Ninguno de ellos y se anulan[/B][/COLOR].', '[COLOR red]Preferidos: [COLOR violet][B]' + str(providers_preferred + '[/B][/COLOR]'))
        providers_preferred = ''


# ~ Parámetros proxytools_ específicos del canal
def get_settings_proxytools(canal):
    logger.info()

    provider = config.get_setting('proxytools_provider', canal, default=default_provider)

    tipo_proxy = config.get_setting('proxytools_tipo', canal, default='')
    pais_proxy = config.get_setting('proxytools_pais', canal, default='')

    if provider == all_providers:
        if proxies_maximo: valor = 50
        else: valor = 20
    else:
        valor = proxies_totales_limit
        config.set_setting('proxytools_max', valor, canal)
        time.sleep(0.5)

    max_proxies = config.get_setting('proxytools_max', canal, default=valor)

    return provider, tipo_proxy, pais_proxy, max_proxies


# ~ Diálogo principal para configurar los proxies de un canal concreto
def configurar_proxies_canal(canal, url):
    logger.info()

    procesar = False

    proxies_iniciales = config.get_setting('proxies', canal, default='').strip()

    if proxies_auto:
        proxies_actuales = config.get_setting('proxies', canal, default='').strip()

        procesar = True

        if proxies_todos:
            proxysearch_process = config.get_setting('proxysearch_process')

            if proxysearch_process == True: pass
            else:
               if proxies_actuales:
                   if proxies_proces:
                       if not platformtools.dialog_yesno(config.__addon_name, 'Existen proxies memorizados en el canal [COLOR yellow][B]' + canal.capitalize() + '[/B][/COLOR]', '[COLOR cyan][B]¿ Desea iniciar una nueva búsqueda de proxies en todos los proveedores ?[/B][/COLOR]'):
                           procesar = False

            if procesar:
                provider_auto = all_providers
                proxies_nuevos = ''

                _buscar_proxies(canal, url, provider_auto, procesar)
                config.set_setting('proxytools_provider', provider_auto, canal)

                proxies_encontrados = config.get_setting('proxies', canal, default='').strip()

                if proxies_nuevos: proxies_nuevos = proxies_nuevos + ', '
                proxies_nuevos = proxies_nuevos + proxies_encontrados

                if proxies_nuevos: cuantos_proxies(canal, provider_auto, proxies_nuevos, procesar)
                else: sin_news_proxies(provider_auto, proxies_actuales, procesar)

        else:
            provider_fijo = opciones_provider[proxies_provider]

            if not PY3:
                if not proxies_list:
                    if provider_fijo >= 0 and provider_fijo <= tot_all_providers: provider_fijo = opciones_provider[proxies_provider - 1]
	
            proxysearch_process = config.get_setting('proxysearch_process')

            if proxysearch_process == True: pass
            else:
               if proxies_actuales:
                   if proxies_proces:
                       if not platformtools.dialog_yesno(config.__addon_name, 'Existen proxies memorizados en el canal [COLOR yellow][B]' + canal.capitalize() + '[/B][/COLOR]', '[COLOR cyan][B]¿ Desea iniciar una nueva búsqueda de proxies con el proveedor configurado en los Ajustes categoria proxies ?[/B][/COLOR] ' + '[COLOR red][B] ' + provider_fijo.capitalize() + '[/COLOR][/B]' ):
                           procesar = False

            if procesar:
                 if _buscar_proxies(canal, url, provider_fijo, procesar):
                     config.set_setting('proxytools_provider', provider_fijo, canal)

                     proxies_nuevos = config.get_setting('proxies', canal, default='').strip()

                     if proxies_nuevos: cuantos_proxies(canal, provider_fijo, proxies_nuevos, procesar)
                     else: sin_news_proxies(provider_fijo, proxies_actuales, procesar)

    # ~ Aunque venga por automático y haya localizado nuevos proxies, hay que entrar por si se modifican o se quitan,
    #   o pq no van bien, excepto que inicialmente el canal no tuviera proxies memorizados, o se encontraron nuevos

    if not proxies_iniciales:
        proxies = config.get_setting('proxies', canal, default='').strip()

        if proxies:
            if config.get_setting('memorize_channels_proxies', default=True):
                channels_proxies_memorized = config.get_setting('channels_proxies_memorized', default='')

                el_memorizado = "'" + canal.lower() + "'"

                if not el_memorizado in str(channels_proxies_memorized):
                    if not channels_proxies_memorized: channels_proxies_memorized = channels_proxies_memorized + el_memorizado
                    else: channels_proxies_memorized = channels_proxies_memorized + ', ' + el_memorizado

                    config.set_setting('channels_proxies_memorized', channels_proxies_memorized)

            return True

    proxies_finales = config.get_setting('proxies', canal, default='').strip()

    if proxies_finales:
        if not proxies_finales == proxies_iniciales:
            el_canal = '[B][COLOR %s]' % color_exec
            el_canal += canal.capitalize()
            el_canal += '[COLOR %s] Actualizados[/COLOR][/B]' % color_avis
            platformtools.dialog_notification('Buscar proxies', el_canal)

            return True

    while True:
        proxies = config.get_setting('proxies', canal, default='').strip()

        provider, tipo_proxy, pais_proxy, max_proxies = get_settings_proxytools(canal)

        if provider == private_list:
            tipo_proxy = '-'
            pais_proxy = '-'
        else:
            tipo_proxy = opciones_tipo[0] if tipo_proxy == '' else tipo_proxy.capitalize()
            pais_proxy = opciones_pais[0] if pais_proxy == '' else pais_proxy

        acciones = []

        lbl = proxies if proxies else '(sin proxies)'
        if lbl == '(sin proxies)': texto = '[COLOR plum]Informar proxies manualmente[/COLOR]'
        else: texto = '[COLOR plum]Modificar proxies manualmente[/COLOR]'

        acciones.append(platformtools.listitem_to_select(texto, lbl, ''))
        acciones.append(platformtools.listitem_to_select('[COLOR yellow]Buscar nuevos proxies[/COLOR]', 'Buscar con parámetros actuales (Guardará los mejores)'))
        acciones.append(platformtools.listitem_to_select('[COLOR cyan]Parámetros búsquedas[/COLOR] proveedor, tipo, país, ...', '[COLOR goldenrod][B]%s[/B][/COLOR], [COLOR darkorange]%s[/COLOR], [COLOR chocolate]%s[/COLOR], [COLOR darkgoldenrod]%d[/COLOR]' % (provider, tipo_proxy, pais_proxy, max_proxies), ''))

        if proxies: acciones.append(platformtools.listitem_to_select('[COLOR red]Quitar proxies[/COLOR]', 'Suprimir proxies actuales para probar el canal sin ellos'))

        hay_private = False
        if provider == private_list:
            hay_private = exist_yourlist()
            if hay_private:
                acciones.append(platformtools.listitem_to_select('[COLOR red]Eliminar lista actual [COLOR cyan] ' + private_list + '[/COLOR]', '[COLOR goldenrod][B]Solo si obtuvo una Nueva Lista[/B][/COLOR]'))

        acciones.append(platformtools.listitem_to_select('[COLOR yellowgreen]Ajustes categoría proxies[/COLOR]', '[COLOR mediumaquamarine]Si la modifica debe abandonar por cancelar[/COLOR]'))

        if proxies_help: acciones.append(platformtools.listitem_to_select('[COLOR green]Ayuda[/COLOR]', 'Informacion sobre la gestión de proxies'))

        ret = platformtools.dialog_select('Configuración proxies para [COLOR darkorange][B]%s[/B][/COLOR]' % canal.capitalize(), acciones, useDetails=True)

        if ret == -1: break

        elif ret == 0:
            new_proxies = platformtools.dialog_input(default=proxies, heading='Indicar el proxy a utilizar ó varios separados por comas')
            if new_proxies:
                if '.' in new_proxies and ':' in new_proxies: pass
                else:
                    platformtools.dialog_notification(canal, 'Formato proxy incorrecto')
                    new_proxies = ''

            if new_proxies and new_proxies != proxies:
                config.set_setting('proxies', new_proxies, canal)
                break

        elif ret == 1:
            search_provider = True
            if proxies_auto:
                if proxies_todos: search_provider = False
            elif provider == all_providers: search_provider = False

            if not search_provider:
                if not procesar:
                    provider, tipo_proxy, pais_proxy, max_proxies = get_settings_proxytools(canal)

                    if not provider == all_providers: search_provider = True

            if not search_provider:
                if provider == all_providers: search_provider = True
                else:
                    if not proxies:
                       search_provider = False
                       if _buscar_proxies(canal, url, provider, False): break
                    else:
                       if platformtools.dialog_yesno(config.__addon_name, '[COLOR cyan][B]¿ Desea iniciar la búsqueda de proxies en todos los proveedores ?[/B][/COLOR]', 'en el Canal [COLOR yellow][B]' + canal.capitalize() + '[/B][/COLOR]'):
                           search_provider = True

            if search_provider:
                if _buscar_proxies(canal, url, provider, procesar): break

        elif ret == 2:
            _settings_proxies_canal(canal, sorted(opciones_provider, key=lambda x: x[0]))

        else:
            if not hay_private:
                if ret == 3:
                    if proxies: config.set_setting('proxies', '', canal)
                    else: configuracion_general()

                elif ret == 4:
                     if proxies: configuracion_general()
                     else: show_help_proxies()

                elif ret == 5: show_help_proxies()
            else:
                if ret == 3:
                    if proxies: config.set_setting('proxies', '', canal)
                    else: configuracion_general()

                elif ret == 4:
                    if proxies: manto_yourlist()
                    else: show_help_proxies()

                elif ret == 5:
                     if proxies: configuracion_general()
                     else: show_help_proxies()

                elif ret == 6: show_help_proxies()

    return True


def _settings_proxies_canal(canal, opciones_provider):
    logger.info()

    provider, tipo_proxy, pais_proxy, max_proxies = get_settings_proxytools(canal)

    if proxies_auto:
        if not proxies_todos:
            provider_fijo = opciones_provider[proxies_provider]

            if not provider == provider_fijo:
                if platformtools.dialog_yesno(config.__addon_name, 'Tiene seleccionado un proveedor que no es el asignado en su configuración de proxies [COLOR cyan]' + provider.capitalize() + '[/COLOR]', '¿ Desea asignar este proveedor para este canal [COLOR yellow][B]' + canal.capitalize() + '[/B][/COLOR] ?'):
                    provider = provider_fijo
                    config.set_setting('proxytools_provider', provider, canal)

    preselect = 0 if provider not in opciones_provider else opciones_provider.index(provider)
    ret = platformtools.dialog_select('Proveedores de proxies', opciones_provider, preselect=preselect)
    if ret == -1: return False

    provider = opciones_provider[ret]
    config.set_setting('proxytools_provider', provider, canal)

    if provider == private_list:
        config.set_setting('proxytools_max', 50, canal)
        return True

    if not proxies_tipos: ret = 0
    else:
        preselect = 0 if tipo_proxy.capitalize() not in opciones_tipo else opciones_tipo.index(tipo_proxy.capitalize())
        ret = platformtools.dialog_select('Tipo de anonimidad de los proxies', opciones_tipo, preselect=preselect)
        if ret == -1: return False

    tipo_proxy = '' if ret == 0 else opciones_tipo[ret].lower()

    config.set_setting('proxytools_tipo', tipo_proxy, canal)

    if not proxies_paises: ret = 0
    else:
        preselect = 0 if pais_proxy not in opciones_pais else opciones_pais.index(pais_proxy)
        ret = platformtools.dialog_select('País de los proxies', opciones_pais, preselect=preselect)
        if ret == -1: return False

    pais_proxy = '' if ret == 0 else opciones_pais[ret]

    config.set_setting('proxytools_pais', pais_proxy, canal)

    if proxies_maximo:
        config.set_setting('proxytools_max', 50, canal)
        return True

    try:
        max_proxies = int(platformtools.dialog_numeric(0, 'Valor máximo de proxies a analizar (tope 50)', '20'))
        if ret == -1: return False

        if max_proxies < 3 or max_proxies > 50:
            platformtools.dialog_notification(canal, 'Valor incorrecto, mínimo 3, máximo 50')
            max_proxies = 20
            if proxies_maximo: max_proxies = 50
    except:
        max_proxies = 20
        if proxies_maximo: max_proxies = 50

    config.set_setting('proxytools_max', max_proxies, canal)

    return True


def _buscar_proxies(canal, url, provider, procesar):
    logger.info()

    proxies = ''

    proxies_actuales = config.get_setting('proxies', canal, default='').strip()

    if url == '': url = 'https://www.youtube.com/'

    provider_canal, tipo_proxy, pais_proxy, max_proxies = get_settings_proxytools(canal)

    all_providers_proxies = []

    search_provider = False
    if proxies_auto:
        if proxies_todos: search_provider = True
    elif provider == all_providers: search_provider = True

    if not procesar:
        if not provider == all_providers: search_provider = False

    msg_txt = '[B][COLOR %s]Obteniendo proxies ...[/COLOR][/B]'

    # ~ Providers que nunca intervienen en All-Providers salvo extended
    extended = False
    if not search_provider: extended = True

    if not extended:
       if proxies_extended:
           if proxies_search_extended: extended = True


    # ~ si venimos de proxysearch
    proxysearch = False

    proxysearch_process = config.get_setting('proxysearch_process')

    if proxysearch_process == True:
       proxysearch_process_proxies = config.get_setting('proxysearch_process_proxies')

       if not str(proxysearch_process_proxies) == '[]':
           proxysearch = True

           memo_search_provider = search_provider
           memo_extended = extended
           memo_provider = provider

           search_provider = False
           extended = False
           provider = ''


    if extended:
        if search_provider or provider == 'z-echolink':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'echolink' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Echolink', msg_txt % color_infor)

                    proxies = proxytoolsz.z_echolink(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-free-proxy-list.uk':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not '.uk' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Free-proxy-list-uk', msg_txt % color_infor)

                    proxies = proxytoolsz.z_free_proxy_list_uk(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-free-proxy-list.anon':
            searching = True

            if proxies_recommended:
               if not 'z-free-proxy-list.anon' in opciones_recommended: searching = False

            elif providers_preferred:
                if not '.anon' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Free-proxy-list-anon', msg_txt % color_infor)

                    proxies = proxytoolsz.z_free_proxy_list_anon(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-github':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'github' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Github', msg_txt % color_infor)

                    proxies = proxytoolsz.z_github(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-opsxcq':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'opsxcq' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Opsxcq', msg_txt % color_infor)

                    proxies = proxytoolsz.z_opsxcq(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-proxy-daily':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'proxy-daily' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Proxy-daily', msg_txt % color_infor)

                    proxies = proxytoolsz.z_proxy_daily(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-proxy-list.org':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'proxy-list.org' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Proxy-list.org', msg_txt % color_infor)

                    proxies = proxytoolsz.z_proxy_list_org(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-proxyhub':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'proxyhub' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Proxhub', msg_txt % color_infor)

                    proxies = proxytoolsz.z_proxyhub(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-proxyranker':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'proxyranker' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Proxyranker', msg_txt % color_infor)

                    proxies = proxytoolsz.z_proxyranker(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-squidproxyserver':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'squidproxyserver' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Squidproxyserver', msg_txt % color_infor)

                    proxies = proxytoolsz.z_squidproxyserver(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-socks':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'socks' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Socks', msg_txt % color_infor)

                    proxies = proxytoolsz.z_socks(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-free-proxy-list.com':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not '.com' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Free-proxy-list-com', msg_txt % color_infor)

                    proxies = proxytoolsz.z_free_proxy_list_com(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-xroxy':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'xroxy' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Xroxy', msg_txt % color_infor)

                    proxies = proxytoolsz.z_xroxy(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

        if search_provider or provider == 'z-coderduck':
            searching = True

            if proxies_recommended: searching = False
            elif providers_preferred:
                if not 'coderduck' in providers_preferred: searching = False

            if searching:
                if len(all_providers_proxies) < proxies_totales_limit:
                    if search_provider: platformtools.dialog_notification('Buscar en Coderduck', msg_txt % color_infor)

                    proxies = proxytoolsz.z_coderduck(url, tipo_proxy, pais_proxy, max_proxies)
                    if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)


    # ~ Providers segun settings
    if search_provider or provider == 'mmpx12':
        searching = True

        if proxies_recommended:
           if not 'mmpx12' in opciones_recommended: searching = False
        elif providers_preferred:
            if not 'mmpx12' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Mmpx12', msg_txt % color_infor)

                proxies = _mmpx12(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'almroot':
        searching = True

        if proxies_recommended:
           if not 'almroot' in opciones_recommended: searching = False
        elif providers_preferred:
            if not 'almroot' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Almroot', msg_txt % color_infor)

                proxies = _almroot(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == default_provider:
        searching = True

        if proxies_recommended:
           if not default_provider in opciones_recommended: searching = False
        elif providers_preferred:
            if not 'proxyscrape' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Proxyscrape', msg_txt % color_infor)

                proxies = _proxyscrape_com(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'us-proxy.org':
        searching = True

        if proxies_recommended:
           if not 'us-proxy' in opciones_recommended: searching = False
        elif providers_preferred:
            if not 'us-proxy' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Us-proxy', msg_txt % color_infor)

                proxies = _us_proxy_org(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'free-proxy-list':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'free-proxy-list' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Free-proxy-list', msg_txt % color_infor)

                proxies = _free_proxy_list(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'google-proxy.net':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'google' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Google-proxy', msg_txt % color_infor)

                proxies = _google_proxy_net(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'hidemy.name':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'hidemy' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Hidemy-name', msg_txt % color_infor)

                proxies = _hidemy_name(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'ip-adress.com':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'ip' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Ip-adress', msg_txt % color_infor)

                proxies = _ip_adress_com(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'dailyproxylists.com':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'dailyproxylists' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Dailyproxylists', msg_txt % color_infor)

                proxies = _dailyproxylists_com(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxysource.org':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'proxysource' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Proxysource', msg_txt % color_infor)

                proxies = _proxysource_org(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'spys.one':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'spys.one' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Spys-one', msg_txt % color_infor)

                proxies = _spys_one(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'mertguvencli':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'mertguvencli' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Mertguvencli', msg_txt % color_infor)

                proxies = _mertguvencli(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'shiftytr':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'shiftytr' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Shiftytr', msg_txt % color_infor)

                proxies = _shiftytr(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'roosterkid':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'roosterkid' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Roosterkid', msg_txt % color_infor)

                proxies = _roosterkid(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'clarketm':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'clarketm' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Clarketm', msg_txt % color_infor)

                proxies = _clarketm(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)


    # ~ Providers secundarios
    if search_provider or provider == 'sslproxies.org':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'sslproxies' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Sslproxies', msg_txt % color_infor)

                proxies = _sslproxies_org(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'httptunnel.ge':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'httptunnel' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Httptunnel', msg_txt % color_infor)

                proxies = _httptunnel_ge(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)


    # ~ Providers resto
    if search_provider or provider == 'geonode.com':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'geonode.com' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Geonode', msg_txt % color_infor)

                proxies = _geonode(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxy-list.download':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'proxy-list' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Proxy-list', msg_txt % color_infor)

                proxies = _proxy_list_download(url, tipo_proxy, pais_proxy, max_proxies)

                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'spys.me':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'spys.me' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Spys-me', msg_txt % color_infor)

                proxies = _spys_me(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxynova.com':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'proxynova' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Proxynova', msg_txt % color_infor)

                proxies = _proxynova_com(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxyservers.pro':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'proxyservers' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Proxyservers', msg_txt % color_infor)

                proxies = _proxyservers_pro(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'silverproxy.xyz':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'silverproxy' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Silverproxy', msg_txt % color_infor)

                proxies = _silverproxy_xyz(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxydb.net':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'proxydb' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Proxydb', msg_txt % color_infor)

                proxies = _proxydb_net(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'hidester.com':
        searching = True

        if proxies_recommended: searching = False
        elif providers_preferred:
            if not 'hidester.com' in providers_preferred: searching = False

        if searching:
            if len(all_providers_proxies) < proxies_totales_limit:
                if search_provider: platformtools.dialog_notification('Buscar en Hidester', msg_txt % color_infor)

                proxies = _hidester(url, tipo_proxy, pais_proxy, max_proxies)
                if proxies: all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)


    # ~ si venimos de proxysearch
    if proxysearch:
        search_provider = memo_search_provider
        extended = memo_extended
        provider = memo_provider

        proxysearch_process_proxies = config.get_setting('proxysearch_process_proxies')

        if not str(proxysearch_process_proxies) == '[]':
            proxies = scrapertools.find_multiple_matches(str(proxysearch_process_proxies), "'(.*?)'")
            all_providers_proxies = proxies


    # ~ fichero personal de proxies en userdata (separados por comas o saltos de línea)
    if provider == private_list: proxies = obtener_private_list()
    else:
        if not provider:
            if not search_provider:
                platformtools.dialog_notification('Buscar proxies', '[B][COLOR %s]Parámetros desconocidos[/COLOR][/B]' % color_alert)
                return False


    if not all_providers_proxies:
        if not proxies:
            if providers_preferred:
                platformtools.dialog_ok('Buscar proxies ' + provider.capitalize(), 'Tiene informados en ajustes [COLOR wheat][B]Proveedores Preferidos[/B][/COLOR] de proxies.', '[COLOR yellow][B]Sin proxies según sus parámetros actuales.[/B][/COLOR]', '[COLOR red]Preferidos: [COLOR violet][B]' + str(providers_preferred + '[/B][/COLOR]'))
            else:
               platformtools.dialog_notification('Buscar proxies ' + provider.capitalize(), '[B][COLOR %s]Sin proxies según parámetros[/COLOR][/B]' % color_adver)
            return False


    # ~ Limitar proxies y validar formato
    proxies = list(filter(lambda x: re.match('\d+\.\d+\.\d+\.\d+\:\d+', x), proxies))

    if proxies_totales:
       if len(proxies) > proxies_totales_limit: proxies = proxies[:proxies_totales_limit]
    else:
       if max_proxies: proxies = proxies[:max_proxies]

    # ~ Testear proxies
    if search_provider:
        proxies = all_providers_proxies

        if len(proxies) >= 50: platformtools.dialog_notification('Buscar proxies', '[B][COLOR %s]Cargando proxies ...[/COLOR][/B]' % color_adver)

        tot_proxies = len(proxies)
        if tot_proxies >= proxies_totales_limit: tot_proxies = proxies_totales_limit
        if max_proxies: proxies = proxies[:tot_proxies]


    nom_provider = provider
    if search_provider: nom_provider = all_providers

    proxies_info = testear_lista_proxies(canal, nom_provider, url, proxies)


    # ~ Guardar mejores proxies en la configuración del canal
    selected = []

    for proxy, info in proxies_info:
        if not info['ok']: break
        selected.append(proxy)

        proxies_validos = config.get_setting('proxies_validos', default=True)
        if proxies_validos:
           if not search_provider:
              if len(selected) >= 3: break # ~ los 3 más rápidos
           else:
              if proxies_limit:
                 if len(selected) >= 10: break # ~ si todos los 10 más rápidos
              else:
                 if len(selected) >= 3: break # ~ los 3 más rápidos
        else:
           if proxies_limit:
               if len(selected) >= 10: break # ~ si todos los 10 más rápidos
           else:
               if len(selected) >= 3: break # ~ los 3 más rápidos

    if len(selected) > 0:
        config.set_setting('proxies', ', '.join(selected), canal)
        logger.info('Actualizados %s : %s' % (canal, ', '.join(selected)))
        el_canal = '[B][COLOR %s]' % color_exec
        el_canal += canal.capitalize()
        el_canal += '[COLOR %s] Actualizados[/COLOR][/B]' % color_avis
        platformtools.dialog_notification('Buscar proxies', el_canal)
    else:
        if not proxies_actuales:
            avisar = True
            if proxies_auto:
                if proxies_todos: avisar = False
            elif provider == all_providers: avisar = False

            if avisar: platformtools.dialog_notification('Buscar proxies', '[B][COLOR %s]Sin proxies válidos[/COLOR][/B]' % color_alert)
        else:
            if provider == private_list: platformtools.dialog_notification('Buscar proxies', 'Sin proxies válidos [B][COLOR %s]en su lista[/COLOR][/B]' % color_alert)


    if config.get_setting('developer_mode', default=False):
        loglevel = config.get_setting('debug', 0) # ~ 0 (error), 1 (error+info), 2 (error+info+debug)

        if loglevel == 2:
            proxies_log = os.path.join(config.get_data_path(), 'proxies.log')

            txt_log = os.linesep + '%s Buscar proxies en %s para %s' % (time.strftime("%Y-%m-%d %H:%M"), nom_provider, url) + os.linesep
            if provider != '': txt_log += provider + os.linesep

            num_ok = 0
            for proxy, info in proxies_info:
                txt_log += '%s ~ %s ~ %.2f segundos ~ %s ~ %d bytes' % (proxy, info['ok'], info['time'], info['code'], info['len']) + os.linesep
                if info['ok']: num_ok += 1

            txt_log += 'Búsqueda finalizada. Posibles Proxies válidos: %d' % (num_ok) + os.linesep

            with open(proxies_log, 'wb') as f: f.write(txt_log if not PY3 else txt_log.encode('utf-8')); f.close()

    if not provider == private_list:
        if len(selected) == 0: sin_news_proxies(nom_provider, proxies_actuales, procesar)
        elif len(selected) >= 10:
            valor = len(selected)
            top_news_proxies(nom_provider, proxies_actuales, valor, procesar)

    return True if len(selected) > 0 else False


def cuantos_proxies(canal, provider, proxies_actuales, procesar):
    logger.info()

    cuantos = config.get_setting('proxies', canal, default='').strip()
    cuantos = cuantos.split(',')

    if cuantos:
        valor = len(cuantos)
        top_news_proxies(provider, proxies_actuales, valor, procesar)


def sin_news_proxies(provider, proxies_actuales, procesar):
    logger.info()

    avisar = True

    if proxies_auto:
        if proxies_todos: avisar = False
    else:
        if provider == all_providers: avisar = True

    if not procesar:
        if not provider == all_providers: search_provider = False

    if avisar:
        texto_mensaje = ''
        if proxies_actuales: texto_mensaje = '[COLOR yellow][B]Se conservan los proxies almacenados.[/B][/COLOR]'
        platformtools.dialog_ok('Búsqueda proxies en [COLOR red][B]' + provider.capitalize() + '[/B][/COLOR]', '[COLOR yellow][B]No se ha obtenido ningún proxy válido con este proveedor.[/B][/COLOR]', texto_mensaje, '[COLOR coral][B]Puede intentar obtener nuevos proxies, cambiando de proveedor, en los parámetros para buscar proxies.[/B][/COLOR]')


def top_news_proxies(provider, proxies_actuales, valor, procesar):
    logger.info()

    if not valor: return
    else:
       if valor < 10: return

    avisar = True
    if proxies_auto:
        if proxies_todos: avisar = False
    else:
        if provider == all_providers: avisar = True

    if not procesar:
        if not provider == all_providers: search_provider = False

    if avisar:
        texto_mensaje = ''
        if proxies_actuales: texto_mensaje = '[COLOR yellow][B]El tiempo de espera acceso al canal podría ser muy elevado.[/B][/COLOR]'
        platformtools.dialog_ok('Búsqueda proxies en [COLOR red][B]' + provider.capitalize() + '[/B][/COLOR]', '[COLOR yellow][B]Se han obtenido ' + str(valor) + ' proxies válidos con este proveedor.[/B][/COLOR]', texto_mensaje, '[COLOR coral][B]Puede intentar obtener menos proxies, cambiando de proveedor, en los parámetros para buscar proxies.[/B][/COLOR]')


def _dailyproxylists_com(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.dailyproxylists.com/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td class="cell-.*?>(.*?)</td>.*?class=.*?>(.*?)</td>')

    if enlaces:
        for prox, port in enlaces:
            if not prox or not port: continue

            proxies.append(prox + ':' + port)
    else:
        el_provider = '[B][COLOR %s] Proxypremium[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Dailyproxylists.com', 'Vía' + el_provider)

        url_provider = 'https://proxypremium.top/full-proxy-list'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr class=pp1x onmouseover=.*?<font class=".*?">(.*?)<font.*?</font>(.*?)</font>')

        for prox, port in enlaces:
            if not prox or not port: continue

            prox = prox.replace('/n', '').strip()

            if prox: proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _sslproxies_org(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.sslproxies.org/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Updated at(.*?)</div>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox:
            if '-' in prox: continue
            elif not ':' in prox: continue

            proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _mmpx12(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _mertguvencli(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txtt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _shiftytr(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _almroot(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/almroot/proxylist/master/list.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _roosterkid(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _clarketm(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _google_proxy_net(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.google-proxy.net/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue

        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _ip_adress_com(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.ipaddress.com/proxy-list/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td><a href="https://www.ipaddress.com/.*?">(.*?)</a>(.*?)</td>')

    for prox, port in enlaces:
        if not prox or not port: continue

        proxies.append(prox + port)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _spys_one(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://spys.one/en/free-proxy-list/'

    url_post = 'xpp=0'
    if tipo_proxy == 'anonymous': url_post += 'xf1=3'
    elif tipo_proxy == 'transparent': url_post += 'xf1=2'
    elif tipo_proxy == 'elite': url_post += 'xf1=4'
    else: url_post += '&xf1=0'

    url_post += '&xf2=0&xf4=0&xf5=0'

    resp = httptools.downloadpage(url_provider, post=url_post, raise_weberror=False, follow_redirects=False)

    if '<title>Just a moment...</title>' in resp.data:
        el_provider = '[B][COLOR %s] Freeproxy[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Spys.one', 'Vía' + el_provider)

        url_provider = 'https://freeproxy.world/'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<td class="show-ip-div">(.*?)</td>.*?<a href=.*?">(.*?)</a>')

        for prox, port in enlaces:
            if not prox or not port: continue

            prox = prox.replace('/n', '').strip()

            if prox: proxies.append(prox + ':' + port)

    else:

        valores = {}
        numeros = scrapertools.find_multiple_matches(resp.data, '([a-z0-9]{6})=(\d{1})\^')

        if numeros:
            for a, b in numeros:
                valores[a] = b

            enlaces = scrapertools.find_multiple_matches(str(resp.data), '<font class=spy14>(\d+\.\d+\.\d+\.\d+).*?font>"(.*?)</script>')

            for prox, resto in enlaces:
                puerto = ''
                numeros = scrapertools.find_multiple_matches(resto, '\+\(([a-z0-9]{6})\^')

                for a in numeros:
                    puerto += str(valores[a])

                proxies.append(prox + ':' + puerto)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _hidemy_name(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://hidemy.name/es/proxy-list/?'
    url_provider += 'type=' + ('s' if url.startswith('https') else 'h')

    if pais_proxy != '': url_provider += '&country=' + pais_proxy

    if tipo_proxy == 'anonymous': url_provider += '&anon=3'
    elif tipo_proxy == 'transparent': url_provider += '&anon=2'
    elif tipo_proxy == 'elite': url_provider += '&anon=4'
    else: url_provider += '&anon=1'

    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>')

    if not enlaces:
        url_provider = 'https://hidemyna.me/es/proxy-list/?type=s&anon=1'

        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>')

    if enlaces:
        for prox, puerto in enlaces:
            proxies.append(prox + ':' + puerto)
    else:
        el_provider = '[B][COLOR %s] TheSpeedX-s5[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Hidemy.name', 'Vía' + el_provider)

        url_provider = 'https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        block = scrapertools.find_single_match(str(resp.data), '"rawLines":(.*?)"stylingDirectives"')

        enlaces = scrapertools.find_multiple_matches(block, '"(.*?)"')

        for prox in enlaces:
            proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _httptunnel_ge(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.httptunnel.ge/ProxyListForFree.aspx'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), ' target="_new">(\d+\.\d+\.\d+\.\d+)\:(\d+)</a>.*?<td align="center"[^>]*>(T|A|E|U)</td>.*? src="images/flags/([^.]+)\.gif"')

    if enlaces:
        for prox, puerto, tipo, pais in enlaces:
            if tipo_proxy != '': 
                if tipo == 'T' and tipo_proxy != 'transparent': continue
                elif tipo == 'A' and tipo_proxy != 'anonymous': continue
                elif tipo == 'E' and tipo_proxy != 'elite': continue

            if pais_proxy != '': 
                if pais != pais_proxy: continue

            proxies.append(prox + ':' + puerto)
    else:
        el_provider = '[B][COLOR %s] Proxyscan[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Httptunnel', 'Vía' + el_provider)

        url_provider = 'https://www.proxyscan.io/api/proxy?limit=100&type=socks4,socks5'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '"Ip": "(.*?)".*?"Port":(.*?),')

        for prox, port in enlaces:
            prox = prox.strip()
            port = port.strip()

            if not prox or not port: continue

            proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _proxynova_com(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.proxynova.com/proxy-server-list/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<script>document.write.*?"(.*?)".*?<td align=.*?>(.*?)</td>')

    if enlaces:
        for prox, port in enlaces:
            port = port.strip()

            if prox: proxies.append(prox + ':' + port)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _free_proxy_list(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://free-proxy-list.net/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue

        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _spys_me(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://spys.me/proxy.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    need_ssl = url.startswith('https')

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(\d+\.\d+\.\d+\.\d+)\:(\d+) ([A-Z]{2})-((?:H|A|N){1}(?:!|))(.*?)\n')

    for prox, puerto, pais, tipo, resto in enlaces:
        if need_ssl and '-S' not in resto: continue

        if tipo_proxy != '': 
            if tipo == 'N' and tipo_proxy != 'transparent': continue
            elif tipo == 'A' and tipo_proxy != 'anonymous': continue
            elif tipo == 'H' and tipo_proxy != 'elite': continue

        if pais_proxy != '': 
            if pais != pais_proxy: continue

        proxies.append(prox + ':' + puerto)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _silverproxy_xyz(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    el_provider = '[B][COLOR %s] Rootjazz[/B][/COLOR]' % color_exec
    platformtools.dialog_notification('Silverproxy', 'Vía' + el_provider)

    url_provider = 'https://rootjazz.com/proxies/proxies.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _proxyscrape_com(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://api.proxyscrape.com/v2/?request=displayproxies'

    url_provider += '&protocol=' + ('https' if url.startswith('https') else 'http')
    url_provider += '&ssl=all'

    if tipo_proxy != '': url_provider += '&anonymity=' + tipo_proxy
    if pais_proxy != '': url_provider += '&country=' + pais_proxy

    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    if not resp.data: 
        timeout = config.get_setting('channels_repeat', default=30)
        platformtools.dialog_notification('Proxyscrape', '[COLOR cyan]Re-Intentanto acceso[/COLOR]')

        url_provider = 'https://api.proxyscrape.com/v2/?request=displayproxies'

        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False, timeout=timeout)

    if resp.data:
        if not "<title>404" in str(resp.data): proxies = resp.data.split()

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _proxyservers_pro(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://es.proxyservers.pro/proxy/list?__path2query_param__='
    url_provider += '/protocol/' + ('https' if url.startswith('https') else 'http')
    if tipo_proxy != '': url_provider += '/anonymity/' + tipo_proxy
    if pais_proxy != '': url_provider += '/country/' + pais_proxy
    url_provider += '/order/updated/order_dir/desc/page/1'

    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    chash = scrapertools.find_single_match(str(resp.data), "var chash\s*=\s*'([^']+)")

    def decode_puerto(t, e):
        a = []; r = []
        for n in range(0, len(t), 2): a.append(int('0x' + t[n:n+2], 16))
        for n in range(len(e)): r.append(ord(e[n]))
        for n, val in enumerate(a): a[n] = val ^ r[n % len(r)]
        for n, val in enumerate(a): a[n] = chr(val)
        return ''.join(a)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '(\d+\.\d+\.\d+\.\d+)</a>\s*</td>\s*<td><span class="port" data-port="([^"]+)')

    for prox, puerto in enlaces:
        proxies.append(prox + ':' + decode_puerto(puerto, chash))

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _us_proxy_org(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://www.us-proxy.org/#list'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    block = scrapertools.find_single_match(str(resp.data), 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue

        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _hidester(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://hidester.com/proxydata/php/data.php?mykey=data&offset=0&limit=50&orderBy=latest_check&sortOrder=DESC&country=&port=&type=undefined&anonymity=undefined&ping=undefined&gproxy=2'

    resp = httptools.downloadpage(url_provider, headers={'referer': 'https://hidester.com/proxylist/'}, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '"IP":"(.*?)".*?"PORT":(.*?)"')

    if enlaces:
        for prox, puerto in enlaces:
            if puerto:
                puerto = puerto.replace(',', '')

                proxies.append(prox + ':' + puerto)
    else:
        el_provider = '[B][COLOR %s] Privacyaffairs[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Hidester', 'Vía' + el_provider)

        url_provider = 'https://www.privacyaffairs.com/free-proxy-servers/'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '<tr>(.*?)</tr>')

        for match in enlaces:
           prox = scrapertools.find_single_match(match, '<td style=".*?">(.*?)</td>')
           if not '.' in prox: continue

           puerto = scrapertools.find_single_match(match, '<td style=".*?".*?</td>.*?">(.*?)</td>')
           if not puerto: continue

           proxies.append(prox + ':' + puerto)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _geonode(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc'

    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '"ip":"(.*?)".*?"port":"(.*?)"')

    for prox, puerto in enlaces:
        if puerto:
            puerto = puerto.replace(',', '').strip()

            proxies.append(prox + ':' + puerto)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _proxy_list_download(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    # ~ API: https://www.proxy-list.download/api/v1
    url_provider = 'https://www.proxy-list.download/api/v1/get'
    url_provider += '?type=' + ('https' if url.startswith('https') else 'http')
    if tipo_proxy != '': url_provider += '&anon=' + tipo_proxy
    if pais_proxy != '': url_provider += '&country=' + pais_proxy

    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    if len(resp.data) > 0: proxies = resp.data.split()
    else:
       url_provider = 'https://www.proxy-list.download/'
       url_provider += ('HTTPS' if url.startswith('https') else 'HTTP')
       resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

       block = scrapertools.find_single_match(str(resp.data), '<tbody id="tabli"(.*?)</tbody>')

       enlaces = scrapertools.find_multiple_matches(block, '<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>')

       for prox, puerto in enlaces:
           if puerto: proxies.append(prox + ':' + puerto)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _proxysource_org(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxysource.org/en/freeproxies'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    url_provider_day = scrapertools.find_single_match(str(resp.data), '</p><a href="(.*?)"')

    if url_provider_day:
        if url_provider_day.startswith('/'): url_provider_day = 'https://proxysource.org' + url_provider_day

        resp = httptools.downloadpage(url_provider_day, raise_weberror=False, follow_redirects=False)

        block = scrapertools.find_single_match(str(resp.data), 'class="ant-input">(.*?)</textarea>')

        enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')

        for prox in enlaces:
           if prox == '': continue
           elif  '-' in prox: continue

           proxies.append(prox)

    if not proxies:
        el_provider = '[B][COLOR %s] TheSpeedX-http[/B][/COLOR]' % color_exec
        platformtools.dialog_notification('Spys.one', 'Vía' + el_provider)

        url_provider = 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt'
        resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

        enlaces = scrapertools.find_multiple_matches(str(resp.data), '(.*?)\n')

        for prox in enlaces:
            proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def _proxydb_net(url, tipo_proxy, pais_proxy, max_proxies):
    logger.info()

    proxies = []

    url_provider = 'https://proxydb.net/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False, follow_redirects=False)

    enlaces = scrapertools.find_multiple_matches(str(resp.data), '<a href=.*?">(.*?)</a>')

    for prox in enlaces:
        proxies.append(prox)

    if len(proxies) < 50: proxies = proxytoolsz.plus_proxies(proxies, max_proxies)

    return proxies


def acumulaciones(provider, proxies, all_providers_proxies, max_proxies):
    logger.info()

    acumular = False
    if proxies_auto:
        if proxies_todos: acumular = True
    elif provider == all_providers: acumular = True

    if acumular:
        tot_proxies = len(proxies)

        if tot_proxies >= 50:
            if provider == all_providers:
                if proxies_totales: pass
                else: tot_proxies = 50
        else:
            tot_proxies = proxies_totales_limit

        if max_proxies:
            if proxies_totales: pass
            else: proxies = proxies[:tot_proxies]

        all_providers_proxies = all_providers_proxies + proxies

    return all_providers_proxies


def do_test_proxy(url, proxy, info):
    logger.info()

    try: resp = httptools.downloadpage(url, use_proxy = {'http': proxy, 'https': proxy}, timeout=HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT, raise_weberror=False)
    except: return

    bad_proxy = False

    if '<urlopen error' in str(resp.code): bad_proxy = True

    if not bad_proxy:
        if resp.data:
            if len(resp.data) > 1000:
                proxy_ok = False

                if str(resp.code) == '200': proxy_ok = True

                if not proxy_ok:
                    if (type(resp.code) == int and (resp.code < 200 or resp.code > 399)) or not resp.sucess: proxy_ok = False
                    else: proxy_ok = True

                if proxy_ok:
                    if ' not found' in str(resp.data).lower() or ' bad request' in str(resp.data).lower() or '<title>Site Blocked</title>' in str(resp.data):
                        proxy_ok = False

                if proxy_ok: info['ok'] = True
                else: info['ok'] = False

    info['time'] = resp.time
    info['len'] = len(resp.data)
    info['code'] = str(resp.code)


def testear_lista_proxies(canal, provider, url, proxies=[]):
    logger.info()

    # ~ si venimos de proxysearch
    proxysearch_process = config.get_setting('proxysearch_process')

    if proxysearch_process == True:
        proxysearch_process_proxies = config.get_setting('proxysearch_process_proxies')

        if str(proxysearch_process_proxies) == '[]':
            config.set_setting('proxysearch_process_proxies', str(proxies))

            if str(proxies) == '[]': proxies = scrapertools.find_multiple_matches(str(proxysearch_process_proxies), "'(.*?)'")


    threads = []
    proxies_info = {}

    proceso_test = True

     # ~ float para calcular porcentaje
    num_proxies = float(len(proxies))

    txt_provider = provider

    if txt_provider == 'proxy-list.download': txt_provider = 'proxy-list.d'
    elif txt_provider == 'z-free-proxy-list.anon': txt_provider = 'z-free-proxy-list.a'
    elif txt_provider == 'z-free-proxy-list.com': txt_provider = 'z-free-proxy-list.c'
    elif txt_provider == 'z-free-proxy-list.uk': txt_provider = 'z-free-proxy-list.u'
    elif txt_provider == 'z-proxy-list.org': txt_provider = 'proxy-list.o'

    txt_provider = txt_provider.replace('z-', '').replace('.com', '').replace('.net', '').replace('.name', '').replace('.ge', '').replace('.pro', '').replace('.org', '').replace('.xyz', '').strip().capitalize()

    progreso = platformtools.dialog_progress('Test proxies ' + '[COLOR yellow][B]' + canal.capitalize() + '[/B][/COLOR] con [COLOR red][B]' + txt_provider + '[/B][/COLOR]', '%d proxies a comprobar. [COLOR yellowgreen][B]Cancelar si tarda demasiado[/B][/COLOR].' % num_proxies)

    repeated = 0

    for proxy in proxies:
        # ~ por si hay repetidos
        if proxy in proxies_info:
            if repeated == 0:
                repeated += 1
                platformtools.dialog_notification('Buscar proxies', '[B][COLOR %s]Despreciando repetidos[/COLOR][/B]' % color_avis)
            continue

        proxies_info[proxy] = {'ok': False, 'time': 0, 'len': 0, 'code': ''}

        try:
           t = Thread(target=do_test_proxy, args=[url, proxy, proxies_info[proxy]])
           t.setDaemon(True)
           t.start()
           threads.append(t)
        except:
           proceso_test = False
           logger.info("proxytools-check: Error Thread.start")
           break

        if progreso.iscanceled():
            progreso.close()
            return []

    if proceso_test:
        if PY3: pendent = [a for a in threads if a.is_alive()]
        else: pendent = [a for a in threads if a.isAlive()]

        maxValidos = config.get_setting('proxies_memory', default=5)
        proxies_validos = config.get_setting('proxies_validos', default=True)

        while len(pendent) > 0:
            hechos = num_proxies - len(pendent)
            perc = int(hechos / num_proxies * 100)
            validos = sum([1 for proxy in proxies if proxies_info[proxy]['ok']])

            progreso.update(perc, 'Comprobando el %d de %d proxies. [COLOR gold]Posibles Válidos[/COLOR] %d. [COLOR yellowgreen][B]Cancelar si tarda demasiado[/B][/COLOR] ó [COLOR cyan][B]si ya hay más de uno válido[/B][/COLOR].' % (hechos, num_proxies, validos))

            if proxies_limit:
                if validos >= 10: break # ~ si todos los 10 más rápidos
            elif proxies_validos:
                if validos >= maxValidos: break # ~ valores 3,4,5,6,7,8,9

            if progreso.iscanceled(): break

            time.sleep(0.5)

            if PY3: pendent = [a for a in threads if a.is_alive()]
            else: pendent = [a for a in threads if a.isAlive()]

    progreso.close()

    if not proceso_test:
        if platformtools.dialog_yesno('ERROR Test proxies en [COLOR yellow][B]' + provider.capitalize() + '[/B][/COLOR]', '[COLOR red][B]Sin disponibilidad de suficiente Memoria para este proceso.[/B][/COLOR]', '[COLOR yellow][B]¿ Desea anular el test automatico en TODOS los proveedores para intentar evitar este inconveniente ?[/B][/COLOR]'):
            config.set_setting('proxies_auto', False)

    # ~ Ordenar según proxy válido y tiempo de respuesta
    return sorted(proxies_info.items(), key=lambda x: (-x[1]['ok'], x[1]['time']))


def show_help_proxies():
    logger.info()

    from modules import helper

    if providers_preferred:
        platformtools.dialog_ok(config.__addon_name, 'Tiene informados en sus ajustes [COLOR cyan]Proveedores Preferidos[/COLOR] de proxies.')
        helper.show_help_providers(item)

    helper.show_help_proxies(item)


def exist_yourlist():
    logger.info()

    from core import filetools

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    return existe


def manto_yourlist():
    logger.info()

    from modules import actions
    actions.manto_yourlist(item)


def configuracion_general():
    logger.info()

    config.__settings__.openSettings()

    platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Si efectuó alguna variación el sus ajustes de proxies.', '[COLOR cyan][B]Recuerde, que para que los cambios surtan efecto, deberá abandonar el proceso de configurar proxies e ingresar de nuevo en el.[/B][/COLOR]')

    platformtools.itemlist_refresh()


def obtener_private_list():
    logger.info()

    from core import filetools

    proxies = []

    zip_extract = False

    proxies_file = os.path.join(config.get_data_path(), private_list)
    existe = filetools.exists(proxies_file)

    if not existe:
        if not platformtools.dialog_yesno(config.__addon_name, '[COLOR violet][B]¿ El fichero ya está Des-comprimido ?[/COLOR][/B]'): 
            ubicacion_path_zip = xbmcgui.Dialog().browseSingle(3, 'Seleccionar la [COLOR yellow]Carpeta[/COLOR] ubicación del fichero [COLOR violet]Lista-proxies.zip[/COLOR]', 'files', '', False, False, '')
            if not ubicacion_path_zip: return proxies

            proxies_file_zip = filetools.join(ubicacion_path_zip, 'Lista-proxies.zip')
            existe_zip = filetools.exists(proxies_file_zip)

            if not existe_zip:
                platformtools.dialog_notification('Buscar proxies', '[B][COLOR %s]Fichero .ZIP No localizado[/COLOR][/B]' % color_alert)
                time.sleep(1.0)
                return proxies

            try:
                import zipfile
                dir = zipfile.ZipFile(proxies_file_zip, 'r')
                dir.extractall(ubicacion_path_zip)
                dir.close()
            except:
                import xbmc
                xbmc.executebuiltin('Extract("%s", "%s")' % (proxies_file_zip, ubicacion_path_zip))

            proxies_file = filetools.join(ubicacion_path_zip, private_list)
            existe = filetools.exists(proxies_file)

            if existe:
                zip_extract = True 

                ubicacion_path = ubicacion_path_zip

        if not zip_extract:
            ubicacion_path = xbmcgui.Dialog().browseSingle(3, 'Seleccionar la [COLOR yellow]Carpeta[/COLOR] ubicación del fichero [COLOR yellowgreen]' + private_list + '[/COLOR]', 'files', '', False, False, '')
            if not ubicacion_path: return proxies

        proxies_file = filetools.join(ubicacion_path, private_list)
        existe = filetools.exists(proxies_file)

        if not existe:
            platformtools.dialog_notification('Buscar proxies', '[B][COLOR %s]Fichero Privado No localizado[/COLOR][/B]' % color_alert)
            time.sleep(1.0)
            return proxies

        if platformtools.dialog_yesno(config.__addon_name, '[COLOR cyan][B]¿ Desea Guardar una copia del fichero [COLOR yellow]Lista-proxies.txt[COLOR cyan] en la carpeta por defecto [COLOR chocolate].../addon_data.../plugin.video.balandro[/B][/COLOR] ?'): 
            proxies_file = os.path.join(config.get_data_path(), private_list)

            origen = filetools.join(ubicacion_path, private_list)
            destino = filetools.join(proxies_file)
            if not filetools.copy(origen, destino, silent=False): platformtools.dialog_ok(config.__addon_name, 'Error, no se ha podido copiar el fichero', origen, destino)
            else: platformtools.dialog_notification('Fichero copiado', proxies_file)

    data = filetools.read(proxies_file)
    data = re.sub(r'(?m)^#.*\n?', '', data)
    proxies = data.replace(' ', '').replace(';', ',').replace(',', '\n').split()

    return proxies

