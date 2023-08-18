# -*- coding: utf-8 -*-

import os, re, xbmcgui

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


host = 'https://playdede.us/'


# ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
# ~ webs  0)-'https://dominiosplaydede.com/'


# ~ por si viene de enlaces guardados posteriores
ant_hosts = ['https://playdede.com/', 'https://playdede.org/', 'https://playdede.nu/',
             'https://playdede.to/']


domain = config.get_setting('dominio', 'playdede', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'playdede')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'playdede')
    else: host = domain


elepage = 42

perpage = 21

login_ok = '[COLOR chartreuse]PlayDede Login correcto[/COLOR]'
login_ko = '[COLOR red][B]PlayDede Login incorrecto[/B][/COLOR]'
no_login = '[COLOR orangered][B]PlayDede Sin acceso Login[/B][/COLOR]'

datos_ko = '>Registrarme<'
close_open = '[COLOR cyan][B]Cierre la sesión e Iniciela de nuevo[/B][/COLOR]'

notification_d_ok = config.get_setting('notification_d_ok', default=True)

color_adver = config.get_setting('notification_adver_color', default='violet')


class login_dialog(xbmcgui.WindowDialog):
    def __init__(self):
        avis = True
        if config.get_setting('playdede_username', 'playdede', default=False): 
            if config.get_setting('playdede_password', 'playdede', default=False):
                if config.get_setting('playdede_login', 'playdede', default=False): avis = False

        if avis:
            self.login_result = False
            platformtools.dialog_ok("Recomendación [B][COLOR yellow]PlayDede[/B][/COLOR]", '[B][COLOR yellowgreen]Mejor crear una NUEVA cuenta para registrarse en la web, no deberíais informar ninguna de vuestras cuentas Personales.[/B][/COLOR]', 'Para más detalles al respecto, acceda a la Ayuda, apartado Canales, Información dominios que requieren registrarse.')

        self.background = xbmcgui.ControlImage(250, 150, 800, 355, filename=config.get_thumb('ContentPanel'))
        self.addControl(self.background)
        self.icon = xbmcgui.ControlImage(265, 220, 225, 225, filename=config.get_thumb('playdede', 'thumb', 'channels'))
        self.addControl(self.icon)
        self.username = xbmcgui.ControlEdit(530, 320, 400, 120, 'Usuario', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))

        self.addControl(self.username)

        if platformtools.get_kodi_version()[1] >= 18:
            self.password = xbmcgui.ControlEdit(530, 320, 400, 120, 'Contraseña', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        else:
            self.password = xbmcgui.ControlEdit(530, 320, 400, 120, 'Contraseña', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'), isPassword=True)

        self.buttonOk = xbmcgui.ControlButton(588, 460, 125, 25, 'Confirmar', alignment=6, focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        self.buttonCancel = xbmcgui.ControlButton(720, 460, 125, 25, 'Cancelar', alignment=6, focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))

        self.addControl(self.password)
        self.password.setVisible(True)
        self.password.controlUp(self.username)
        self.addControl(self.buttonOk)
        self.password.controlDown(self.buttonOk)

        self.username.setLabel('Usuario')
        if int(platformtools.get_kodi_version()[1]) >= 18: self.username.setType(xbmcgui.INPUT_TYPE_TEXT, 'Indicar el Usuario')

        self.password.setLabel('Contraseña')
        if int(platformtools.get_kodi_version()[1]) >= 18: self.password.setType(xbmcgui.INPUT_TYPE_PASSWORD, 'Indicar la Contraseña')

        self.setFocus(self.username)

        self.username.controlUp(self.buttonOk)
        self.username.controlDown(self.password)
        self.buttonOk.controlUp(self.password)
        self.buttonOk.controlDown(self.username)
        self.buttonOk.controlRight(self.buttonCancel)
        self.buttonOk.controlLeft(self.buttonCancel)
        self.addControl(self.buttonCancel)
        self.buttonCancel.controlRight(self.buttonOk)
        self.buttonCancel.controlLeft(self.buttonOk)
        self.username.setPosition(500, 210)
        self.username.setWidth(500)
        self.username.setHeight(50)
        self.password.setPosition(500, 300)
        self.password.setWidth(500)
        self.password.setHeight(50)

        self.doModal()

        if self.username.getText() and self.password.getText():
            config.set_setting('playdede_username', self.username.getText(), 'playdede')
            config.set_setting('playdede_password', self.password.getText(), 'playdede')
            config.set_setting('playdede_login', True, 'playdede')
            self.login_result = True
        else:
            avis = True
            avis = True
            if not self.username.getText():
                if not self.password.getText(): avis = False

            if avis:
                platformtools.dialog_notification('PlayDede', '[B][COLOR red]Faltan credenciales[/B][/COLOR]')
                self.login_result = False

    def onControl(self, control):
        control = control.getId()
        if control in range(3000, 30010): self.close()


def do_make_login_logout(url, post=None, headers=None):
    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
    else:
        data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
                else:
                    data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False).data
        except:
            pass

    if '<title>Just a moment...</title>' in data:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def login(item):
    logger.info()

    status = config.get_setting('playdede_login', 'playdede', default=False)

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    if not username or not password:
        login = login_dialog()
        if not login.login_result: return False

        if not item:
            platformtools.dialog_notification(config.__addon_name, '[COLOR yellow]PlayDede Credenciales guardadas[/COLOR]')
            return False

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    try:
       data = do_make_login_logout(host)
       if not data: return False

       user = scrapertools.find_single_match(data, username).strip()

       if user:
           if username:
               if username in user:
                   if not status: config.set_setting('playdede_login', True, 'playdede')

                   if not item: platformtools.dialog_notification(config.__addon_name, login_ok)
                   else:
                      if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)
                   return True

       if 'UserOn' in data:
           if not status:
               config.set_setting('playdede_login', True, 'playdede')
               if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)
           return True
    except:
       platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]PlayDede Sin acceso Web[/B][/COLOR]')
       return False

    post = {'user': username, 'pass': password, '_method': 'auth/login'}

    try:
       headers = {'Referer': host + 'login'}
       data = do_make_login_logout(host + 'ajax.php', post=post, headers=headers)

       if not data: return False

       jdata = jsontools.load(data)

       if 'reload' in str(jdata):
           if jdata['reload']:
               if not status:
                   config.set_setting('playdede_login', True, 'playdede')
                   if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)
               return True

       elif 'alert' in str(jdata):
           if not jdata['alert']:
               if not status:
                   config.set_setting('playdede_login', True, 'playdede')
                   if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)
               return True

       else:
           if not host in str(data): platformtools.dialog_notification(config.__addon_name, no_login)
           else: platformtools.dialog_notification(config.__addon_name, login_ko)

           return False
    except:
       platformtools.dialog_notification(config.__addon_name, no_login)
       return False

    if not httptools.get_cookie(host, 'MoviesWebsite'): do_make_login_logout(host)

    if httptools.get_cookie(host, 'utoken'):
        if not status:
            config.set_setting('playdede_login', True, 'playdede')
            if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)
        return True

    try:
       headers = {'Referer': host + 'login'}
       data = do_make_login_logout(host + 'ajax.php', post=post, headers=headers)

       if not data: return False
    except:
       platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]PlayDede Sin acceso al Login[/B][/COLOR]')
       return False

    if httptools.get_cookie(host, 'utoken'):
        if not status:
            config.set_setting('playdede_login', True, 'playdede')
            if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)
        return True

    if not host in str(data): platformtools.dialog_notification(config.__addon_name, no_login)
    else: platformtools.dialog_notification(config.__addon_name, login_ko)

    return False


def logout(item):
    logger.info()

    username = config.get_setting('playdede_username', 'playdede', default='')

    if username:
        data = do_make_login_logout(host + 'user/' + username + '/salir/')

        config.set_setting('playdede_login', False, 'playdede')
        platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Sesión cerrada[/COLOR]')
        return True

    platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]PlayDede Sin cerrar la Sesión[/B][/COLOR]')
    return False


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_playdede_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar ...[/B]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, referer=None):
    username = config.get_setting('playdede_username', 'playdede', default='')

    if not username:
        platformtools.dialog_notification('PlayDede', '[COLOR red][B]Faltan[COLOR teal][I]Credenciales Cuenta[/I] [/B][/COLOR]')
        return ''

    # ~ por si viene de enlaces guardados posteriores
    if url.startswith('/'): url = host + url[1:] # ~ solo v. 2.0.0

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not referer: referer = host

    timeout = None
    if '?genre=' in url: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data
    else:
        data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data

    if "data-showform='login'" in data:
        if not config.get_setting('playdede_login', 'playdede', default=False):
            platformtools.dialog_notification(config.__addon_name, '[COLOR yellow][B]PlayDede Debe iniciar la Sesión[/B][/COLOR]')

        result = login('')

        if result == True: return do_downloadpage(url, post=post, referer=referer)

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'playdede', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_playdede', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='playdede', folder=False, text_color='chartreuse' ))

    username = config.get_setting('playdede_username', 'playdede', default='')

    if username:
        itemlist.append(Item( channel='domains', action='operative_domains_playdede', title='[B]Dominio Operativo Vigente[/B]',
                              desde_el_canal = True, host_canal = url, thumbnail=config.get_thumb('settings'), text_color='mediumaquamarine' ))

        itemlist.append(Item( channel='domains', action='last_domain_playdede', title='[B]Comprobar último dominio vigente[/B]',
                              desde_el_canal = True, host_canal = url, thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_playdede', title=title, desde_el_canal = True, host_canal = url, folder=False, thumbnail=config.get_thumb('keyboard'), text_color='darkorange' ))

    if not config.get_setting('playdede_login', 'playdede', default=False):
        if username:
            itemlist.append(item.clone( title = '[COLOR chartreuse][B]Iniciar sesión[/B][/COLOR]', action = 'login' ))
            itemlist.append(Item( channel='domains', action='del_datos_playdede', title='[B]Eliminar credenciales cuenta[/B]', thumbnail=config.get_thumb('folder'), text_color='crimson' ))
        else:
            itemlist.append(Item( channel='helper', action='show_help_register', title='[B]Información para registrarse[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

            itemlist.append(item.clone( title = '[COLOR crimson][B]Credenciales cuenta[/B][/COLOR]', action = 'login' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR chartreuse][B]Cerrar sesión[/B][/COLOR]', action = 'logout' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_playdede', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

        itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, _type = 'movies', nro_pagina = 1, search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'peliculas?orderBy=item_date', slug = 'peliculas',
                                    nro_pagina = 1, order = '?orderBy=item_date', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'En cartelera', action = 'list_all', url = host + 'peliculas?orderBy=now_playing', slug = 'peliculas',
                                    nro_pagina = 1, order = '?orderBy=now_playing', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'peliculas?orderBy=popular', slug = 'peliculas',
                                    nro_pagina = 1, order = '?orderBy=popular', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas?orderBy=score', slug = 'peliculas',
                                    nro_pagina = 1, order = '?orderBy=score', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))
        itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))
        itemlist.append(item.clone( title = 'Por país', action = 'paises', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Nuevos episodios', action = 'list_last', url = host, _type = 'episodes', nro_pagina = 1, search_type = 'tvshow', text_color = 'olive' ))

        itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, _type = 'series', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'series?orderBy=last_update', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=last_update', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'series?orderBy=airing_today', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=airing_today', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'series?orderBy=popular', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=popular', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series?orderBy=score', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=score', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

        itemlist.append(item.clone( title = 'Por plataforma', action= 'plataformas', slug = 'series', nro_pagina = 1, search_type='tvshow'))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por país', action = 'paises', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))

    return itemlist


def mainlist_animes(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes/', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'animes?orderBy=last_update', slug = 'animes',
                                    nro_pagina = 1, order = '?orderBy=last_update', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'animes?orderBy=popular', slug = 'animes',
                                    nro_pagina = 1, order = '?orderBy=popular', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'animes?orderBy=score', slug = 'animes',
                                    nro_pagina = 1, order = '?orderBy=score', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por plataforma', action= 'plataformas', group = 'anime', slug = 'animes', nro_pagina = 1, search_type='tvshow'))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por país', action = 'paises', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes':
        url = url = host + 'animes/'
        text_color = 'springgreen'
    else:
        url = url = host + 'series/'
        text_color = 'hotpink'

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('data-network="(.*?)".*?<img src="(.*?)"').findall(data)

    for id_network, thumb in matches:
        title = scrapertools.find_single_match(thumb, '/network/(.*?).png')
        title = title.capitalize()

        itemlist.append(item.clone(title = title, action = 'list_plataforma', thumbnail = thumb, url = url, id_network = id_network, slug = item.slug, text_color = text_color ))

    return sorted(itemlist, key=(lambda x: x.title))


def list_plataforma(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else: text_color = 'hotpink'

    data = do_downloadpage(item.url)
    data = re.sub('\\n|\\r|\\t|\\s{2}|&nbsp;', '', data)

    matches = re.compile('<a href="([^"]+)"><i class[^<]+</i>([^<]+)').findall(data)

    for url, title in matches:
        title = title.capitalize()

        url = url.replace('?orderBy=last_update', '?network=' + item.id_network + '&orderBy=last_update')
        url = url.replace('?orderBy=airing_today', '?network=' + item.id_network + '&orderBy=airing_today')
        url = url.replace('?orderBy=popular', '?network=' + item.id_network + '&orderBy=popular')
        url = url.replace('?orderBy=score', '?network=' + item.id_network + '&orderBy=score')

        if '=score' in url: order = 'score'
        elif '=popular' in url: order = 'popular'
        elif '=airing_today' in url: order = 'airing_today'
        else: order = 'last_update'

        itemlist.append(item.clone(title = title, action = 'list_network', url = url, order = order, slug = item.slug, text_color = text_color ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_generos = host + 'animes/'
    else:
        if item.search_type == 'movie': url_generos = host + 'peliculas/'
        else: url_generos = host + 'series/'

    data = do_downloadpage(url_generos)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(url_generos)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="cfilter.*?data-type="genre".*?data-value="(.*?)">.*?<b>(.*?)</b>').findall(data)

    for genre, title in matches:
        if item.group == 'anime':
            if title == 'Documental': continue

        genre = '?genre=' + genre

        itemlist.append(item.clone( title = title, action = 'list_all', genre = genre, text_color = text_color ))

    if itemlist:
        if item.search_type == 'movie':
            itemlist.append(item.clone( title = 'Aventura', action = 'list_all', genre = '?genre=aventura', text_color = text_color ))
            itemlist.append(item.clone( title = 'Fantasía', action = 'list_all', genre = '?genre=fantasia', text_color = text_color ))
            itemlist.append(item.clone( title = 'Historia', action = 'list_all', genre = '?genre=historia', text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.search_type == 'movie': tope_year = 1934
    else: tope_year = 1969

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        year = '?year=' + str(x)

        itemlist.append(item.clone( title = str(x), year = year, action = 'list_all', text_color = text_color ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_idiomas = host + 'animes/'
    else:
        if item.search_type == 'movie': url_idiomas = host + 'peliculas/'
        else: url_idiomas = host + 'series/'

    data = do_downloadpage(url_idiomas)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(url_idiomas)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="Alenguajes Ageneros">(.*?)<ul class="Acalidades Ageneros">')

    matches = re.compile("<li class='cfilter.*?data-type='lang'.*?data-value='(.*?)'>(.*?)</li>").findall(bloque)

    for idioma, title in matches:
        url = url_idiomas + '?lang=' + idioma

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, lang = idioma, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def calidades(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_calidades = host + 'animes/'
    else:
        if item.search_type == 'movie': url_calidades = host + 'peliculas/'
        else: url_calidades = host + 'series/'

    data = do_downloadpage(url_calidades)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(url_calidades)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="Acalidades Ageneros">(.*?)<select id="countries"')

    matches = re.compile("<li class='cfilter.*?data-type='qlty'.*?data-value='(.*?)'>(.*?)</li>").findall(bloque)

    for calidad, title in matches:
        url = url_calidades + '?qlty=' + calidad

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, qlty = calidad, text_color = text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def paises(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_paises = host + 'animes/'
    else:
        if item.search_type == 'movie': url_paises = host + 'peliculas/'
        else: url_paises = host + 'series/'

    data = do_downloadpage(url_paises)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(url_paises)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<select id="countries"(.*?)<div class="selDf">')

    matches = re.compile("<option class='cfilter.*?data-type='country'.*?data-value='(.*?)'.*?>(.*?)</option>").findall(bloque)

    for pais, title in matches:
        if not pais: continue

        title = title.replace('á', 'Á').replace('é', 'É').replace('i', 'Í').replace('ó', 'Ó').replace('ú', 'Ú')

        url = url_paises + '?country=' + pais

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, country = pais, text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    # ~ Si venimos del menu pral. Grupos o Generos
    if not item.slug:
       if item.search_type == 'movie': item.slug = 'peliculas'
       elif item.search_type == 'tvshow': item.slug = 'series'

       if not item.genre:
          genre = scrapertools.find_single_match(item.url, '/?genre=(.*?)&')
          if genre: item.genre = '?genre=' + genre

       if not item.nro_pagina: item.nro_pagina = 1

    if not item.post:
       if item.lang:
           post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug, 'lang': item.lang}
       elif item.qlty:
           post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug, 'qlty': item.qlty}
       elif item.country:
           post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug, 'country': item.country}
       elif item.order:
           post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug}
       else:
           post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug}

    else: post = item.post

    if item.lang:
        data = do_downloadpage(host + 'ajax.php?lang=' + item.lang, post=post, referer=item.url)
    elif item.qlty:
        data = do_downloadpage(host + 'ajax.php?qlty=' + item.qlty, post=post, referer=item.url)
    elif item.country:
        data = do_downloadpage(host + 'ajax.php?country=' + item.country, post=post, referer=item.url)
    elif item.order:
        data = do_downloadpage(host + 'ajax.php' + item.order, post=post, referer=item.url)
    else:
        data = do_downloadpage(host + 'ajax.php' + item.genre + item.year, post=post, referer=item.url)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)

        if item.lang:
            data = do_downloadpage(host + 'ajax.php?lang=' + item.lang, post=post, referer=item.url)
        elif item.qlty:
            data = do_downloadpage(host + 'ajax.php?qlty=' + item.qlty, post=post, referer=item.url)
        elif item.country:
            data = do_downloadpage(host + 'ajax.php?country=' + item.country, post=post, referer=item.url)
        elif item.order:
            data = do_downloadpage(host + 'ajax.php' + item.order, post=post, referer=item.url)
        else:
            data = do_downloadpage(host + 'ajax.php' + item.genre + item.year, post=post, referer=item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('\\/', '/')

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        match = match.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        title = clean_title(title, url)

        if 'Tu directorio de' in title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if not year: year = '-'

        if '/pelicula/' in url:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
                buscar_next = False

        if num_matches < elepage: buscar_next = False

        if buscar_next:
             item.nro_pagina = item.nro_pagina + 1

             if item.lang:
                 post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug, 'lang': item.lang}
             elif item.qlty:
                 post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug, 'qlty': item.qlty}
             elif item.country:
                 post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug, 'country': item.country}
             else:
                 post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug}

             itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = item.url, nro_pagina = item.nro_pagina, post = post, page = 0, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if not item.post: post = {'_method': 'items', 'type': item._type, 'async': 'true', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': ''}
    else: post = item.post

    data = do_downloadpage(host + 'ajax.php', post=post)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(host + 'ajax.php', post=post)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('\\/', '/')

    i = 0

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        match = match.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if item._type == 'episodes': title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        title = clean_title(title, url)

        if 'Tu directorio de' in title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if not year: year = '-'

        if '/pelicula/' in url:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        elif '/serie/' in url:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        else:
            titulo = scrapertools.find_single_match(match, '<a href="(.*?)"')

            titulo = titulo.replace('/episodios/', '').replace('_1', '').replace('_', ' ').replace('-', ' ').strip()
            titulo = titulo.replace('//', '').strip()

            titulo = titulo.capitalize()

            thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
            thumb = thumb.replace('http:', 'https:')

            s_e = scrapertools.get_season_and_episode(title)

            try:
               season = int(s_e.split("x")[0])
               epis = s_e.split("x")[1]
            except:
               i += 1
               season = 0
               epis = i

            title = title.replace('/', '').strip()

            titulo = titulo.replace(str(season) + 'x' + epis, '').strip()
            titulo = titulo.replace(title, '').strip()

            if not 'Episodio' in title: titulo = titulo +  ' ' + title

            SerieName = titulo

            del_temp_epis = ''
            del_titulo = ''
            del_num_url = ''

            if '_' in url:
                del_num_url = scrapertools.find_single_match(url, '_(.*?)-').strip()
                if not del_num_url: del_num_url = scrapertools.find_single_match(del_num_url, '_(.*?)$').strip()

                if '_' in del_num_url:
                    del_num_url = scrapertools.find_single_match(del_num_url, '_(.*?)$').strip()

                    if '_' in del_num_url:
                        while '_' in del_num_url:
                           del_num_url = scrapertools.find_single_match(del_num_url, '_(.*?)$').strip()

                try:
                   del_num_url = int(del_num_url)
                   titulo = titulo.replace(str(del_num_url), '').strip()
                except:
                   del_num_url = ''

            if ':' in title: del_temp_epis = scrapertools.find_single_match(title, ':(.*?)$').strip()

            if ':' in titulo:
                del_titulo = scrapertools.find_single_match(titulo, ':(.*?)$').strip()
                titulo = titulo.replace(del_titulo, '').strip()
                titulo = titulo.replace(':', '').strip()

            if del_temp_epis:
                SerieName = SerieName.replace(del_temp_epis, '').strip()
                SerieName = SerieName.replace(':', '').strip()

            if del_num_url:
                ini_SerieName = SerieName
                SerieName = SerieName.replace(str(del_num_url), '').strip()

                if ini_SerieName == SerieName:
                    del_num_url = str(del_num_url)[1:]

                    if del_num_url:
                        SerieName = SerieName.replace(str(del_num_url), '').strip()

                        if del_num_url in titulo: titulo = titulo.replace(str(del_num_url), '').strip()

            titulo = titulo.replace('  ', ' ')

            if not 'x' in titulo: titulo = titulo + ' ' + str(season) + 'x' + str (epis)

            SerieName = SerieName.replace('  ', ' ')

            itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_last', text_color = 'coral' ))

    return itemlist


def list_listas(item):
    logger.info()
    itemlist = []

    if not item.url: url = host + 'listas/'
    else: url = item.url

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article>.*?<a href="([^"]+)"[^<]+<h2>([^<]+)</h2>').findall(data)

    for url, title in matches:
        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        itemlist.append(item.clone( action = 'list_search', title = title, url = url, text_color='moccasin' ))

    if itemlist:
        if '<div class="pagPlaydede">' in data:
            if 'Pagina Anterior' in data: patron = '<div class="pagPlaydede">.*?Pagina Anterior.*?<a href="([^"]+)'
            else: patron = '<div class="pagPlaydede"><a href="([^"]+)'

            next_url = scrapertools.find_single_match(data, patron)

            if next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_listas', text_color = 'coral' ))

    return itemlist


def list_network(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if not item.post:
        post = {'_method': 'items', 'page': item.nro_pagina, 'networks': item.id_network, 'ajaxName': 'main', 'slug': item.slug, 'orderBy=': item.order}
    else:
        post = item.post

    url_post = item.url.replace('/series', '/ajax.php')

    data = do_downloadpage(url_post, post=post, referer=item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('\\/', '/')

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        match = match.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        if 'Tu directorio de' in title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        title = clean_title(title, url)

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_network', text_color = 'coral' ))
                buscar_next = False

        if num_matches < elepage: buscar_next = False

        if buscar_next:
            item.nro_pagina = item.nro_pagina + 1

            post = {'_method': 'items', 'page': item.nro_pagina, 'networks': item.id_network, 'ajaxName': 'main', 'slug': item.slug, 'orderBy=': item.order}

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_network', url = item.url, nro_pagina = item.nro_pagina, post = post, page = 0, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="clickSeason.*?data-season="(.*?)"', re.DOTALL).findall(data)
    if not matches: matches = re.compile("<div class='clickSeason.*?data-season='(.*?)'", re.DOTALL).findall(data)

    if len(matches) > 25: platformtools.dialog_notification('PlayDede', '[COLOR blue][B]Cargando Temporadas[/B][/COLOR]')

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = int(tempo), text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="se-c".*?data-season="%d"(.*?)<\/div><\/div>' % (item.contentSeason))
    if not bloque: bloque = scrapertools.find_single_match(data, "<div class='se-c'.*?data-season='%d'(.*?)<\/div><\/div>" % (item.contentSeason))

    patron = '<a href="([^"]+)"><div class="imagen">'
    patron += '.*?src="([^"]+)"><\/div>.*?<div class="epst">([^<]+)'
    patron += '<\/div>.*?<div class="numerando">([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for url, thumb, titulo, name in matches[item.page * item.perpage:]:
        s_e = scrapertools.get_season_and_episode(name)
        season = int(s_e.split("x")[0])
        episode = s_e.split("x")[1]

        title = str(season) + 'x' + str(episode) + ' ' + titulo

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # ~ Reproductor
    matches = re.compile('<div class="playerItem(.*?)</div></div>', re.DOTALL).findall(data)

    ses = 0

    for match in matches:
        ses += 1

        sid = scrapertools.find_single_match(match, 'data-loadPlayer="(.*?)"')
        if not sid: sid = scrapertools.find_single_match(match, 'data-loadplayer="(.*?)"')

        server = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not server or not sid: continue

        if server == 'waaw': continue
        elif server == 'powvideo': continue
        elif server == 'streamplay': continue
        elif server == 'alternativo': continue
        elif server == 'userload': continue

        lang = scrapertools.find_single_match(match, 'data-lang="(.*?)"')

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        qlty = scrapertools.find_single_match(match, '">Calidad:.*?">(.*?)</span>')

        if server == 'filemoon': other = 'Filemoon'
        elif server == 'streamwish': other = 'Streamwish'
        else: other = ''

        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', id = sid, language = lang, quality = qlty, other = other ))

    # ~ Enlaces
    bloque = scrapertools.find_single_match(data, '<div class="linkSorter">(.*?)<div class="contEP contepID_3">')

    matches = re.compile('data-quality="(.*?)".*?data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        ses += 1

        if not url or not server: continue

        if server == 'waaw': continue
        elif server == 'powvideo': continue
        elif server == 'streamplay': continue
        elif server == 'alternativo': continue
        elif server == 'userload': continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        if server == 'filemoon': other = 'Filemoon'
        elif server == 'streamwish': other = 'Streamwish'
        else: other = 'E'

        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, quality = qlty, other = other ))

    # ~ Descargas
    bloque = scrapertools.find_single_match(data, '<div class="contEP contepID_3">(.*?)$')

    matches = re.compile('data-quality="(.*?)".*?data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        ses += 1

        if not url or not server: continue

        if '/ul.' in url: continue
        elif '/1fichier.' in url: continue
        elif '/ddownload.' in url: continue
        elif '/userload.' in url: continue

        if 'https://netload.cc/st?' in url:
             url = scrapertools.find_single_match(url, '&url=(.*?)$')
             if not url: continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, quality = qlty, other = 'D' ))


    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url_play = ''

    if item.id:
        post = {'_method': 'getPlayer', 'id': item.id}
        data = do_downloadpage(host + 'ajax.php', post=post)

        url = scrapertools.find_single_match(data, "src='([^']+)")
        url = url.replace('\\/', '/')

        if url:
            data = do_downloadpage(url)

            url_play = scrapertools.find_single_match(data, '<iframe src="(.*?)"')
            if not url_play: url_play = scrapertools.find_single_match(data, "<iframe src='(.*?)'")

    else:
        url_play = item.url

    if url_play:
        itemlist.append(item.clone(url = url_play.replace("\\/", "/")))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    username = config.get_setting('playdede_username', 'playdede', default='')

    if not username: return []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    # ~ si se perdio la sesion (utoken)
    if datos_ko in str(data):
        logout(item)
        login(item)
        data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        if not item.search_type == "all":
            if item.search_type == "movie":
                if '/serie/' in url: continue
            else:
                if '/pelicula/' in url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>, (\d+)</p>')
        if not year: year = '-'

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo, contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo, contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_search', text_color = 'coral' ))
                buscar_next = False

        if num_matches < elepage: buscar_next = False

        if buscar_next:
            if '<div class="pagPlaydede">' in data:
                if 'Pagina Anterior' in data: patron = '<div class="pagPlaydede">.*?Pagina Anterior.*?<a href="([^"]+)'
                else: patron = '<div class="pagPlaydede"><a href="([^"]+)'

                next_url = scrapertools.find_single_match(data, patron)

                if next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_search', page = 0, text_color = 'coral' ))

    return itemlist


def clean_title(title, url):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a')

    if '\\u' in title:
        data = do_downloadpage(url)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        titulo = scrapertools.find_single_match(data, "<h1>(.*?)</h1>")
        if not titulo: titulo = scrapertools.find_single_match(data, "<title>(.*?)</title>")

        titulo = titulo.replace('Ver película:', '').replace('Ver serie:', '').replace('Ver anime:', '').strip()

        if titulo: title = titulo

    return title


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

