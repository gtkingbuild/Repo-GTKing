# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import os, re, xbmcgui

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


LINUX = False
BR = False
BR2 = False

if PY3:
    try:
       import xbmc
       if xbmc.getCondVisibility("system.platform.Linux.RaspberryPi") or xbmc.getCondVisibility("System.Platform.Linux"): LINUX = True
    except: pass

try:
   if LINUX:
       try:
          from lib import balandroresolver2 as balandroresolver
          BR2 = True
       except: pass
   else:
       if PY3:
           from lib import balandroresolver
           BR = true
       else:
          try:
             from lib import balandroresolver2 as balandroresolver
             BR2 = True
          except: pass
except:
   try:
      from lib import balandroresolver2 as balandroresolver
      BR2 = True
   except: pass


useragent = httptools.get_user_agent()

custom_headers = dict()
custom_headers["User-Agent"] = useragent

custom_headers["Accept"] = "application/json"
custom_headers["Accept-Encoding"] = "gzip, deflate, br"
custom_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
custom_headers["Connection"] = "keep-alive"
custom_headers["Content-Type"] = "application/json"

custom_headers["Sec-Fetch-Dest"] = "empty"
custom_headers["Sec-Fetch-Mode"] = "cors"
custom_headers["Sec-Fetch-Site"] = "same-origin"


dominios = [
         'https://nextdede.tv'
         ]


host = config.get_setting('dominio', 'nextdede', default=dominios[0])


ant_hosts = ['https://nextdede.com', 'https://nextdede.top']


if host in str(ant_hosts): config.set_setting('dominio', dominios[0], 'nextdede')

useragent = httptools.get_user_agent()


login_ok = '[COLOR chartreuse]NextDede Login correcto[/COLOR]'
login_ko = '[COLOR red][B]NextDede Login incorrecto[/B][/COLOR]'
no_login = '[COLOR orangered][B]NextDede Sin acceso Login[/B][/COLOR]'
start_ses_ok = '[COLOR chartreuse][B]Sesión Iniciada[/B][/COLOR], Por favor [COLOR cyan][B]Retroceda Menús[/B][/COLOR] y acceda de Nuevo al Canal.'


class login_dialog(xbmcgui.WindowDialog):
    def __init__(self):
        avis = True
        if config.get_setting('nextdede_email', 'nextdede', default=False): 
            if config.get_setting('nextdede_password', 'nextdede', default=False):
                if config.get_setting('nextdede_username', 'nextdede', default=False):
                    if config.get_setting('nextdede_login', 'nextdede', default=False): avis = False

        if avis:
            self.login_result = False
            platformtools.dialog_ok("Recomendación [B][COLOR yellow]NextDede[/B][/COLOR]", '[B][COLOR yellowgreen]Mejor crear una NUEVA cuenta para registrarse en la web, no deberíais informar ninguna de vuestras cuentas Personales.[/B][/COLOR]', 'Para más detalles al respecto, acceda a la Ayuda, apartado Canales, Información dominios que requieren registrarse.')

        self.background = xbmcgui.ControlImage(250, 150, 800, 355, filename=config.get_thumb('ContentPanel'))
        self.addControl(self.background)
        self.icon = xbmcgui.ControlImage(265, 220, 225, 225, filename=config.get_thumb('nextdede', 'thumb', 'channels'))
        self.addControl(self.icon)

        self.email = xbmcgui.ControlEdit(530, 320, 400, 120, 'E-mail', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))

        self.addControl(self.email)

        if platformtools.get_kodi_version()[1] >= 18:
            self.password = xbmcgui.ControlEdit(530, 320, 400, 120, 'Contraseña', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        else:
            self.password = xbmcgui.ControlEdit(530, 320, 400, 120, 'Contraseña', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'), isPassword=True)

        self.username = xbmcgui.ControlEdit(530, 320, 400, 120, 'Usuario', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))

        self.buttonOk = xbmcgui.ControlButton(588, 460, 125, 25, 'Confirmar', alignment=6, focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        self.buttonCancel = xbmcgui.ControlButton(720, 460, 125, 25, 'Cancelar', alignment=6, focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))

        self.addControl(self.password)
        self.password.setVisible(True)
        self.password.controlUp(self.email)

        self.addControl(self.username)
        self.username.controlUp(self.password)

        self.addControl(self.buttonOk)
        self.username.controlDown(self.buttonOk)

        self.email.setLabel('E-mail')
        if int(platformtools.get_kodi_version()[1]) >= 18: self.email.setType(xbmcgui.INPUT_TYPE_TEXT, 'Indicar el E-Mail')

        self.password.setLabel('Contraseña')
        if int(platformtools.get_kodi_version()[1]) >= 18: self.password.setType(xbmcgui.INPUT_TYPE_PASSWORD, 'Indicar la Contraseña')

        self.username.setLabel('Usuario')
        if int(platformtools.get_kodi_version()[1]) >= 18: self.username.setType(xbmcgui.INPUT_TYPE_TEXT, 'Indicar el Usuario')

        self.setFocus(self.email)

        self.email.controlUp(self.buttonOk)
        self.email.controlDown(self.password)

        self.password.controlUp(self.email)
        self.password.controlDown(self.username)

        self.username.controlUp(self.password)
        self.username.controlDown(self.buttonOk)

        self.buttonOk.controlUp(self.username)
        self.buttonOk.controlDown(self.email)
        self.buttonOk.controlRight(self.buttonCancel)
        self.buttonOk.controlLeft(self.buttonCancel)
        self.addControl(self.buttonCancel)
        self.buttonCancel.controlRight(self.buttonOk)
        self.buttonCancel.controlLeft(self.buttonOk)

        self.email.setPosition(500, 210)
        self.email.setWidth(500)
        self.email.setHeight(50)

        self.password.setPosition(500, 300)
        self.password.setWidth(500)
        self.password.setHeight(50)

        self.username.setPosition(500, 400)
        self.username.setWidth(500)
        self.username.setHeight(50)

        self.doModal()

        if self.email.getText() and self.password.getText() and self.username.getText():
            config.set_setting('nextdede_email', self.email.getText(), 'nextdede')
            config.set_setting('nextdede_password', self.password.getText(), 'nextdede')
            config.set_setting('nextdede_username', self.username.getText(), 'nextdede')
            config.set_setting('nextdede_login', True, 'nextdede')
            self.login_result = True
        else:
            avis = True
            if not self.email.getText():
                if not self.password.getText():
                   if not self.username.getText(): avis = False

            if avis:
                platformtools.dialog_notification('NextDede', '[B][COLOR red]Faltan credenciales[/B][/COLOR]')
                self.login_result = False

    def onControl(self, control):
        control = control.getId()
        if control in range(3000, 30010): self.close()


def do_make_login_logout(url, post=None, headers=None):
    domain = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not headers:
        headers = custom_headers
        headers["Referer"] = domain + '/acceder'

    hay_proxies = False
    if config.get_setting('channel_nextdede_proxies', default=''): hay_proxies = True

    if not url.startswith(domain):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('nextdede', url, post=post, headers=headers, raise_weberror=False).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, domain.replace('https://', '')[:-1])

                if not url.startswith(domain):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('nextdede', url, post=post, headers=headers, raise_weberror=False).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    elif '"Recaptcha v3 site key"' in data:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]ReCaptcha[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def login(item):
    logger.info()

    status = config.get_setting('nextdede_login', 'nextdede', default=False)

    domain = config.get_setting('dominio', 'nextdede', default=dominios[0])

    email = config.get_setting('nextdede_email', 'nextdede', default='')
    password = config.get_setting('nextdede_password', 'nextdede', default='')
    username = config.get_setting('nextdede_username', 'nextdede', default='')

    data = ''

    domain_unknow = False

    if domain:
        if domain in dominios:
            if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', domain, 'nextdede')

            if username:
                if password:
                    post = {'email': email, 'password': password, 'remember': 'true'}

                    headers = custom_headers
                    headers["Referer"] = domain + '/acceder'

                    data = do_make_login_logout(domain + '/auth/login', post=post, headers=headers)
                    if not data: return False
        else:
            domain_unknow = True

    if not email or not password or not username:
        login = login_dialog()
        if not login.login_result: return False

        if not item:
            if not domain: config.set_setting('dominio', dominios[0], 'nextdede')
            else:
               if not domain in dominios: config.set_setting('dominio', dominios[0], 'nextdede')

            platformtools.dialog_notification(config.__addon_name, '[COLOR yellow]NextDede Credenciales guardadas[/COLOR]')
            return False

    email = config.get_setting('nextdede_email', 'nextdede', default='')
    password = config.get_setting('nextdede_password', 'nextdede', default='')
    username = config.get_setting('nextdede_username', 'nextdede', default='')

    token = ''
    data = ''

    try:
       headers = custom_headers
       headers["Referer"] = ''

       data1 = do_make_login_logout(domain, headers = {})
       if not data1:
           if domain_unknow: platformtools.dialog_notification(config.__addon_name + ' - NextDede', 'Comprobar Dominio [COLOR moccasin]' + domain + '[/COLOR]')
           return False

       token = scrapertools.find_single_match(data1, '"csrf_token":"(.*?)"')

       if username:
           if password:
               post = {'email': email, 'password': password, 'remember': 'true'}

               headers = custom_headers
               headers["Referer"] = domain + '/acceder'

               data = do_make_login_logout(domain + '/auth/login', post=post, headers=headers)

       user = scrapertools.find_single_match(data, username).strip()

       if user:
           if username:
               if username in user:
                   if not status: config.set_setting('nextdede_login', True, 'nextdede')

                   if not item: platformtools.dialog_notification(config.__addon_name, login_ok)
                   else:
                      if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)

                   if item:
                       if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' NextDede', start_ses_ok)
                   return True

    except:
       platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]NextDede Sin acceso Web[/B][/COLOR]')
       return False

    if not token:
        platformtools.dialog_notification(config.__addon_name, no_login)
        return False

    post = {'email': email, 'password': password, 'remember': 'true'}

    headers = custom_headers
    headers["Referer"] = domain + '/acceder'

    data = do_make_login_logout(domain + '/auth/login', post=post, headers=headers)

    if not data: return False

    if username in data:
        config.set_setting('nextdede_login', True, 'nextdede')
        if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)

        if item:
            if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' NextDede', start_ses_ok)
        return True

    platformtools.dialog_notification(config.__addon_name, login_ko)
    return False


def logout(item):
    logger.info()

    domain = config.get_setting('dominio', 'nextdede', default=dominios[0])

    email = config.get_setting('nextdede_email', 'nextdede', default='')

    if email:
        headers = custom_headers
        headers["Referer"] = domain + '/'

        data = do_make_login_logout(domain + '/logout', headers = headers)

        config.set_setting('nextdede_login', False, 'nextdede')
        platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]NextDede Sesión cerrada[/COLOR]')

        if item:
            if item.category: 
                platformtools.dialog_ok(config.__addon_name + ' NextDede', '[COLOR yellow][B]Sesión Cerrada[/B][/COLOR].', 'Por favor [COLOR cyan][B]Retroceda Menús[/B][/COLOR] e [COLOR chartreuse][B]Inicie Sesión[/B][/COLOR] de nuevo.')
        return True

    platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]NextDede Sin cerrar la Sesión[/B][/COLOR]')
    return False


def item_configurar_dominio(item):
    plot = 'Este canal tiene varios posibles dominios. Si uno no te funciona puedes probar con los otros antes de intentarlo con proxies.'
    return item.clone( title = '[B]Configurar dominio a usar ...[/B]', action = 'configurar_dominio', folder=False, plot=plot, text_color='yellowgreen' )

def configurar_dominio(item):
    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])
    num_dominio = dominios.index(dominio) if dominio in dominios else 0
    ret = platformtools.dialog_select('Dominio a usar NextDede', dominios, preselect=num_dominio)
    if ret == -1: return False

    if not dominio == dominios[ret]:
        if config.get_setting('nextdede_login', 'nextdede', default=False):
            logout(item)

    config.set_setting('dominio', dominios[ret], 'nextdede')

    platformtools.itemlist_refresh()
    return True


def item_configurar_proxies(item):
    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_nextdede_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + dominio + ' necesitarás un proxy.'
    return item.clone( title = '[B]Configurar proxies a usar ...[/B]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, dominio)


def do_downloadpage(url, post=None, headers=None, referer=None):
    username = config.get_setting('nextdede_username', 'nextdede', default='')

    if not username:
        platformtools.dialog_notification('NextDede', '[COLOR red][B]Faltan[COLOR teal][I]Credenciales Cuenta[/I] [/B][/COLOR]')
        return ''

    domain = config.get_setting('dominio', 'nextdede', default=dominios[0])

    # ~ por si viene de enlaces guardados posteriores
    for ant in ant_hosts:
        url = url.replace(ant, domain)

    # ~ por si viene de opcion menu pral. Generos
    if not domain in url:
        for dom in dominios:
            url = url.replace(dom, domain)

    if not headers: headers= {'Referer': domain}

    hay_proxies = False
    if config.get_setting('channel_nextdede_proxies', default=''): hay_proxies = True

    if not url.startswith(domain):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('nextdede', url, post=post, headers=headers, raise_weberror=False).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, domain.replace('https://', '')[:-1])

                if not url.startswith(domain):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('nextdede', url, post=post, headers=headers, raise_weberror=False).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
            except:
                pass

    if not '/search/' in url:
        if '<title>Just a moment...</title>' in data:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
            return ''

        elif '"Recaptcha v3 site key"' in data:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]ReCapctha[COLOR orangered] Protection[/B][/COLOR]')
            return ''

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'nextdede', default='')

    if domain_memo: url = domain_memo
    else: url = host

    email = config.get_setting('nextdede_email', 'nextdede', default='')

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_nextdede', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='nextdede', folder=False, text_color='chartreuse' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_nextdede', title=title, desde_el_canal = True, folder=False, thumbnail=config.get_thumb('keyboard'), text_color='darkorange' ))

    if not config.get_setting('nextdede_login', 'nextdede', default=False):
        if email:
            itemlist.append(item.clone( title = '[COLOR chartreuse][B]Iniciar sesión[/B][/COLOR]', action = 'login', start_ses = True ))

            itemlist.append(item.clone( title = '[COLOR springgreen][B]Ver las credenciales[/B][/COLOR]', action = 'shuw_credenciales', thumbnail=config.get_thumb('pencil') ))
            itemlist.append(Item( channel='domains', action='del_datos_nextdede', title='[B]Eliminar credenciales cuenta[/B]', thumbnail=config.get_thumb('folder'), text_color='crimson' ))
        else:
            itemlist.append(Item( channel='helper', action='show_help_register', title='[B]Información para registrarse[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

            itemlist.append(item.clone( title = '[COLOR crimson][B]Credenciales cuenta[/B][/COLOR]', action = 'login' ))

    if config.get_setting('nextdede_login', 'nextdede', default=False):
        itemlist.append(item.clone( title = '[COLOR chartreuse][B]Cerrar sesión[/B][/COLOR]', action = 'logout' ))

        itemlist.append(item.clone( title = '[COLOR springgreen][B]Ver las credenciales[/B][/COLOR]', action = 'shuw_credenciales', thumbnail=config.get_thumb('pencil') ))
        itemlist.append(Item( channel='domains', action='del_datos_nextdede', title='[B]Eliminar credenciales cuenta[/B]', thumbnail=config.get_thumb('folder'), text_color='crimson' ))

    itemlist.append(item_configurar_dominio(item))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_nextdede', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('nextdede_login', 'nextdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('nextdede_login', 'nextdede', default=False):
        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas colecciones[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

        itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('nextdede_login', 'nextdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('nextdede_login', 'nextdede', default=False):
        dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

        if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas colecciones[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = dominio + '/discovery?filter={"type": "movie", "sorting": "newest"}', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = dominio + '/movies', search_type = 'movie', text_color='cyan' ))

        itemlist.append(item.clone( title = 'Últimas agregadas', action = 'list_last', url = dominio + '/trends', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Recientes', action = 'list_all', url = dominio + '/movies?filter={"sorting":"newest"}', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = dominio + '/movies?filter={"sorting":"released"}', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = dominio + '/movies?filter={"sorting":"popular"}', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = dominio + '/movies?filter={"sorting":"imdb"}', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Sagas', action = 'list_listas', url = dominio + '/services', search_type = 'movie', text_color = 'moccasin' ))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('nextdede_login', 'nextdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('nextdede_login', 'nextdede', default=False):
        dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

        if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas colecciones[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = dominio + '/discovery?filter={"type": "serie", "sorting": "newest"}', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Nuevas', action = 'list_all', url = dominio + '/series', search_type = 'tvshow', text_color = 'moccasin' ))

        itemlist.append(item.clone( title = 'Últimas agregadas', action = 'list_last', url = dominio + '/trends', search_type = 'tvshow', text_color = 'cyan' ))

        itemlist.append(item.clone( title = 'Recientes', action = 'list_all', url = dominio + '/series?filter={"sorting":"newest"}', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = dominio + '/series?filter={"sorting":"released"}', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = dominio + '/series?filter={"sorting":"popular"}', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = dominio + '/series?filter={"sorting":"imdb"}', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def list_listas(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    if not item.url: url = dominio + '/collections'
    else: url = item.url

    data = do_downloadpage(url)

    data = re.sub('\\n|\\r|\\t|\\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="collection-container">.*?<a href="(.*?)".*?class="list-title">(.*?)</a>').findall(data)

    for url, title in matches:
        title = title.strip()

        if not title: title = url.replace('collection/saga-', '').replace('collection/', '')

        url = dominio + '/' + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    data = do_downloadpage(dominio + '/categories')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div style="margin-.*?<a href="(.*?)".*?<b>(.*?)</b>').findall(data)

    for url, title in matches:
        if item.search_type == 'movie': url = url + '?filter={"type":"movie","sorting":"newest"}'
        else: url = url + '?filter={"type":"serie","sorting":"newest"}'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, text_color = text_color ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': url = dominio + '/discovery?filter={"type": "movie", "sorting": "newest"}'
    else: url = dominio + '/discovery?filter={"type": "serie", "sorting": "newest"}'

    itemlist.append(item.clone( title = '2020 - ' + str(current_year), url = url + '"released":"2020-"' + str(current_year) + ',"sorting":"newest"}', action = 'list_all', text_color = text_color ))

    itemlist.append(item.clone( title = '2010 - 2019', url = url + '"released":"2010-2019","sorting":"newest"}', action = 'list_all', text_color = text_color ))
    itemlist.append(item.clone( title = '2000 - 2009', url = url + '"released":"2000-2009","sorting":"newest"}', action = 'list_all', text_color = text_color ))
    itemlist.append(item.clone( title = '1990 - 1999', url = url + '"released":"1990-1999","sorting":"newest"}', action = 'list_all', text_color = text_color ))
    itemlist.append(item.clone( title = '1980 - 1989', url = url + '"released":"1980-1989","sorting":"newest"}', action = 'list_all', text_color = text_color ))
    itemlist.append(item.clone( title = '1970 - 1979', url = url + '"released":"1970-1979","sorting":"newest"}', action = 'list_all', text_color = text_color ))

    if item.search_type == 'movie':
        itemlist.append(item.clone( title = '1960 - 1969', url = url + '"released":"1960-1969","sorting":"newest"}', action = 'list_all', text_color = text_color ))
        itemlist.append(item.clone( title = '1950 - 1959', url = url + '"released":"1950-1959","sorting":"newest"}', action = 'list_all', text_color = text_color ))
        itemlist.append(item.clone( title = '1940 - 1949', url = url + '"released":"1940-1949","sorting":"newest"}', action = 'list_all', text_color = text_color ))
        itemlist.append(item.clone( title = '1900 - 1939', url = url + '"released":"1900-1939","sorting":"newest"}', action = 'list_all', text_color = text_color ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('div class="list-movie">(.*?)</div></div></div>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'class="list-title">(.*?)</a>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<div class="list-year".*?">(.*?)<div').strip()
        if not year: year = '-'

        qlty = scrapertools.find_single_match(match, '<div class="quality">(.*?)</div>').strip()

        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, qualities=qlty, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, qualities=qlty, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination' in data:
            next_page = scrapertools.find_single_match(data, '<li class="page-item active">.*?</a>.*?' + "href='(.*?)'")
            if not next_page: next_page = scrapertools.find_single_match(data, '<li class="page-item active">.*?</a>.*?href="(.*?)"')

            if next_page:
                if '&page=' in next_page:
                    next_page = next_page.replace('&quot;', '"').strip()

                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Últimas Agregadas<(.*?)</script>')

    matches = re.compile('<a (.*?)</a>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="list-title">(.*?)</div>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<div class="list-year".*?">(.*?)</div')
        if not year: year = '-'

        if '/movie/' in url:
            if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        if '/serie/' in url:
            if item.search_type == "movie": continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    data = do_downloadpage(item.url)

    matches = re.compile('aria-controls="season-(.*?)"', re.DOTALL).findall(data)

    for tempo in matches:
        if not tempo: tempo = '0'

        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = tempo, text_color='tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if str(item.contentSeason) == '0':
        bloque = scrapertools.find_single_match(data, 'aria-labelledby="season--tab">(.*?)</a></div>')
    else:
        bloque = scrapertools.find_single_match(data, '<div class="tab-pane " id="season-%s"(.*?)</div></div></div></div></div></div></div></div>' % (item.contentSeason))
        if not bloque: bloque = scrapertools.find_single_match(data, '<div class="tab-pane show active" id="season-%s"(.*?)</div></div></div></div></div></div></div></div>' % (item.contentSeason))

    matches = re.compile('<img src="(.*?)".*?<div class="w-full flex-none text-.*?">(.*?)</div>.*?<span>(.*?)</span>.*?<a href="(.*?)"', re.DOTALL).findall(bloque)

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('NextDede', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NextDede', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NextDede', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NextDede', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('NextDede', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('NextDede', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for thumb, name, temp_epis, url in matches[item.page * item.perpage:]:
        temp_epis = temp_epis.strip()

        season = scrapertools.find_single_match(temp_epis, "T(.*?)-").strip()
        if not season: season = '0'

        episode = scrapertools.find_single_match(temp_epis, " - E(.*?)$")

        name = name.strip()

        title = str(season) + 'x' + str(episode) + ' ' + name

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

    IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Ingles': 'Ing', 'VOSE': 'Vose', 'VOS': 'Vos'}

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # ~ Enlaces
    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = re.compile('<tr>.*?<a href="(.*?)".*?<span class="text-quality">(.*?)</span>.*?title="(.*?)".*?</tr>', re.DOTALL).findall(bloque)

    ses = 0

    for url, qlty, lang in matches:
        ses += 1

        if '/powvideo.' in url or '/streamplay.' in url: continue

        lang = IDIOMAS.get(lang, lang)

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if not servidor == 'directo':
            other = ''

            if servidor == 'various': other = servertools.corregir_other(url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = qlty, other = other ))

    # ~ Descargar
    bloque = scrapertools.find_single_match(data, '<div class="links-modal-body"><table>(.*?)</table>')

    matches = re.compile('<tr>.*?<a href="(.*?)".*?<span class="text-quality">(.*?)</span>.*?title="(.*?)".*?</tr>', re.DOTALL).findall(bloque)

    for url, qlty, lang in matches:
        ses += 1

        if '/ul.' in url: continue
        elif '/1fichier.' in url: continue

        lang = IDIOMAS.get(lang, lang)

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servertools.is_server_available(servidor):
            if not servertools.is_server_enabled(servidor): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if not servidor == 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = qlty, other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def shuw_credenciales(item):
    logger.info()

    email = config.get_setting('nextdede_email', 'nextdede', default='')
    password = config.get_setting('nextdede_password', 'nextdede', default='')
    username = config.get_setting('nextdede_username', 'nextdede', default='')

    platformtools.dialog_ok(config.__addon_name + ' NextDede - Credenciales', 'Email:  [COLOR yellow][B]' + email, '[/B][/COLOR]Pass.:  [COLOR yellow][B]' + password, '[/B][/COLOR]User..:  [COLOR yellow][B]' + username + '[/B][/COLOR]')


def search(item, texto):
    logger.info()

    dominio = config.get_setting('dominio', 'nextdede', default=dominios[0])

    if not config.get_setting('dominio', 'nextdede'): config.set_setting('dominio', dominio, 'nextdede')

    try:
        item.url = dominio + '/search/' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

