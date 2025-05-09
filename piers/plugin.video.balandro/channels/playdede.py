# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, xbmcgui

from platformcode import config, logger, platformtools, dynamic
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


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


host = 'https://www9.playdede.link/'


# ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
# ~ webs  0)-https://privacidad.me/@playdede  1)-https://entrarplaydede.com  2)-X https://x.com/playdedesocial


# ~ por si viene de enlaces guardados posteriores
ant_hosts = ['https://playdede.com/', 'https://playdede.org/', 'https://playdede.nu/',
             'https://playdede.to/', 'https://playdede.us/', 'https://playdede.eu/',
             'https://playdede.me/', 'https://playdede.in/', 'https://playdede.link/',
             'https://www1.playdede.link/', 'https://www2.playdede.link/', 'https://www3.playdede.link/',
             'https://www4.playdede.link/', 'https://www5.playdede.link/', 'https://www6.playdede.link/',
             'https://www7.playdede.link/', 'https://www8.playdede.link/']


domain = config.get_setting('dominio', 'playdede', default='')

if domain:
    if domain == host: config.set_setting('dominio', '', 'playdede')
    elif domain in str(ant_hosts): config.set_setting('dominio', '', 'playdede')
    else: host = domain


_dynamic = False
if not config.get_setting('developer_mode', default=False):
    cur_host = host
    new_host = dynamic.host(host)

    if not cur_host == new_host:
        _dynamic = True
        config.set_setting('dominio', new_host, 'playdede')


elepage = 42

perpage = 21

login_ok = '[COLOR chartreuse]PlayDede Login correcto[/COLOR]'
login_ko = '[COLOR red][B]PlayDede Login incorrecto[/B][/COLOR]'
no_login = '[COLOR orangered][B]PlayDede Sin acceso Login[/B][/COLOR]'
start_ses_ok = '[COLOR chartreuse][B]Sesión Iniciada[/B][/COLOR], Por favor, si fuera necesario, [COLOR cyan][B]Retroceda Menús[/B][/COLOR] y acceda de Nuevo al Canal.'

datos_ko = '>Registrarme<'

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
    hay_proxies = False
    if config.get_setting('channel_playdede_proxies', default=''): hay_proxies = True

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
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
       if username:
           userint = int(username)

           if userint:
               platformtools.dialog_ok(config.__addon_name + ' PlayDede', '[COLOR red][B]El Usuario NO puede ser sólo números.[/B][/COLOR]', '[COLOR cyan][B]Credenciales[/B] [/COLOR][COLOR chartreuse][B]Anuladas[/B][/COLOR]')
               config.set_setting('channel_playdede_playdede_username', '')
               config.set_setting('channel_playdede_playdede_password', '')
               config.set_setting('channel_playdede_playdede_login', False)
               return False
    except:
       pass

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

                   if item:
                       if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' PlayDede', start_ses_ok)
                   return True

       if 'UserOn' in data:
           if not status:
               config.set_setting('playdede_login', True, 'playdede')
               if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)

               if item:
                   if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' PlayDede', start_ses_ok)
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

                   if item:
                       if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' PlayDede', start_ses_ok)
               return True

       elif 'alert' in str(jdata):
           if not jdata['alert']:
               if not status:
                   config.set_setting('playdede_login', True, 'playdede')
                   if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)

                   if item:
                       if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' PlayDede', start_ses_ok)
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

            if item:
                if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' PlayDede', start_ses_ok)
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

            if item:
                if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' PlayDede', start_ses_ok)
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

        if config.get_setting('notificar_login', default=False):
            platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Sesión cerrada[/COLOR]')

            if item:
                if item.category: 
                    platformtools.dialog_ok(config.__addon_name + ' PlayDede', '[COLOR yellow][B]Sesión Cerrada[/B][/COLOR].', 'Por favor, si fuera necesario,  [COLOR cyan][B]Retroceda Menús[/B][/COLOR] e [COLOR chartreuse][B]Inicie Sesión[/B][/COLOR] de nuevo.')
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

    hay_proxies = False
    if config.get_setting('channel_playdede_proxies', default=''): hay_proxies = True

    timeout = None
    if '?genre=' in url: timeout = config.get_setting('channels_repeat', default=30)

    if not url.startswith(host):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data

    if not data:
        if '?genre=' in url:
            if config.get_setting('channels_re_charges', default=True): platformtools.dialog_notification('PlayDede Error', '[COLOR cyan]Espere y Re-intentelo otra vez[/COLOR]')

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])

                if not url.startswith(host):
                    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not 'search/?s=' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

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

    itemlist.append(item.clone( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_playdede', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='playdede', folder=False, text_color='chartreuse' ))

    username = config.get_setting('playdede_username', 'playdede', default='')

    if username:
        itemlist.append(item.clone( action='show_current_domain', title='[B]Dominio Actual[COLOR dodgerblue] entrarplaydede.com[/B][/COLOR]',
                                    text_color='darkgoldenrod' ))

        itemlist.append(item.clone( channel='domains', action='operative_domains_playdede', title='[B]Dominio Operativo Vigente' + '[COLOR dodgerblue] privacidad.me/@playdede[/B][/COLOR]',
                                    desde_el_canal = True, host_canal = url, text_color='mediumaquamarine' ))

        itemlist.append(item.clone( channel='domains', action='last_domain_playdede', title='[B]Comprobar último dominio vigente[/B]',
                                    desde_el_canal = True, host_canal = url, text_color='chocolate' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_playdede', title=title, desde_el_canal = True, host_canal = url, folder=False, text_color='darkorange' ))

    if not config.get_setting('playdede_login', 'playdede', default=False):
        if username:
            itemlist.append(item.clone( title = '[COLOR chartreuse][B]Iniciar sesión[/B][/COLOR]', action = 'login', start_ses = True ))

            itemlist.append(item.clone( channel='submnuctext', action='_credenciales_playdede', title= 'Test [COLOR cyan][B]Login[/B][/COLOR] Credenciales' ))

            itemlist.append(item.clone( title = '[COLOR springgreen][B]Credenciales[/B][/COLOR]', action = 'show_credenciales' ))
            itemlist.append(item.clone( channel='domains', action='del_datos_playdede', title='[B]Eliminar Credenciales[/B]', text_color='crimson' ))
        else:
            itemlist.append(item.clone( channel='helper', action='show_help_register', title='Información para [COLOR violet][B]Registrarse[/B][/COLOR]',                            desde_el_canal = True, channel_id='playdede', text_color='green' ))

            itemlist.append(item.clone( title = '[COLOR crimson][B]Informar Credenciales Cuenta[/B][/COLOR]', action = 'login', thumbnail=config.get_thumb('pencil') ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR chartreuse][B]Cerrar sesión[/B][/COLOR]', action = 'logout' ))

        itemlist.append(item.clone( channel='submnuctext', action='_credenciales_playdede', title= 'Test [COLOR cyan][B]Login[/B][/COLOR] Credenciales' ))

        itemlist.append(item.clone( title = '[COLOR springgreen][B]Credenciales[/B][/COLOR]', action = 'show_credenciales' ))
        itemlist.append(item.clone( channel='domains', action='del_datos_playdede', title='[B]Eliminar Credenciales[/B]', text_color='crimson' ))

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone(channel='helper', action = 'show_help_playdede_media_center', title = '[COLOR aquamarine][B]Aviso[/COLOR] [COLOR violet][B]Ubicación[/B][/COLOR] Media Center',  thumbnail=config.get_thumb('mediacenter') ))

    itemlist.append(item.clone( channel='helper', action='show_help_playdede_bloqueo', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR yellowgreen][B]Bloqueo[/B][/COLOR] Operadoras' ))

    itemlist.append(item.clone( channel='helper', action='show_help_playdede', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal' ))

    if not _dynamic:
        itemlist.append(item.clone( channel='actions', action='show_old_domains', title='[COLOR coral][B]Historial Dominios[/B][/COLOR]', channel_id = 'playdede' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR teal][B]Menú usuario[/B][/COLOR]', action = 'mainlist_user', search_type = 'all' ))

        itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

        itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

        if not config.get_setting('descartar_anime', default=False):
            itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

        itemlist.append(item.clone( title = 'Búsqueda en listas populares:', action = '', folder=False, text_color='greenyellow' ))
        itemlist.append(item.clone( title = ' - Buscar lista ...', action = 'search', target_action = 'top', search_type = 'all', search_pop = 'pop',
                                    plot = 'Indicar el título de la lista (ó parte del mismo).'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR teal][B]Menú usuario[/B][/COLOR]', action = 'mainlist_user', search_type = 'all' ))

        itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

        itemlist.append(item.clone( title = 'Buscar lista ...', action = 'search', target_action = 'top', search_type = 'all', search_pop = 'pop', text_color = 'greenyellow' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, _type = 'movies', nro_pagina = 1, search_type = 'movie', text_color='cyan' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'peliculas?orderBy=last_update', slug = 'peliculas',
                                    nro_pagina = 1, order = '?orderBy=last_update', search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Cartelera', action = 'list_all', url = host + 'peliculas?orderBy=now_playing', slug = 'peliculas',
                                    nro_pagina = 1, order = '?orderBy=now_playing', search_type = 'movie', text_color = 'moccasin' ))

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
        itemlist.append(item.clone( title = '[COLOR teal][B]Menú usuario[/B][/COLOR]', action = 'mainlist_user', search_type = 'all' ))

        itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

        itemlist.append(item.clone( title = 'Buscar lista ...', action = 'search', target_action = 'top', search_type = 'all', search_pop = 'pop', text_color = 'greenyellow' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_last', url = host, _type = 'episodes', nro_pagina = 1, search_type = 'tvshow', text_color = 'cyan' ))

        itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, _type = 'series', nro_pagina = 1, search_type = 'tvshow', text_color = 'yellowgreen' ))

        if not config.get_setting('descartar_anime', default=False):
            itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'series?orderBy=last_update', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=last_update', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'series?orderBy=airing_today', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=airing_today', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'series?orderBy=popular', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=popular', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series?orderBy=score', slug = 'series',
                                    nro_pagina = 1, order = '?orderBy=score', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por plataforma', action= 'plataformas', slug = 'series', nro_pagina = 1, search_type='tvshow', text_color = 'moccasin' ))

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
        itemlist.append(item.clone( title = '[COLOR teal][B]Menú usuario[/B][/COLOR]', action = 'mainlist_user', search_type = 'all' ))

        itemlist.append(item.clone( title = '[COLOR greenyellow][B]Listas populares[/B][/COLOR]', action = 'list_listas', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

        itemlist.append(item.clone( title = 'Buscar lista ...', action = 'search', target_action = 'top', search_type = 'all', search_pop = 'pop', text_color = 'greenyellow' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes/', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'animes?orderBy=last_update', slug = 'animes',
                                    nro_pagina = 1, order = '?orderBy=last_update', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'animes?orderBy=popular', slug = 'animes',
                                    nro_pagina = 1, order = '?orderBy=popular', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'animes?orderBy=score', slug = 'animes',
                                    nro_pagina = 1, order = '?orderBy=score', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por plataforma', action= 'plataformas', group = 'anime', slug = 'animes', nro_pagina = 1, search_type='tvshow', text_color = 'moccasin' ))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por país', action = 'paises', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

    return itemlist


def mainlist_user(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = '[COLOR green][B]Información [COLOR teal][B]Menú Usuario[/B][/COLOR]', action = 'show_help_usuario' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes':
        url_plataformas = url = host + 'animes/'
        text_color = 'springgreen'
    else:
        url_plataformas = url = host + 'series/'
        text_color = 'hotpink'

    url = url_plataformas

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'const networkDict(.*?)let dropdownSorting')

    bloque = bloque.replace(';', ',')

    matches = re.compile('"(.*?)":(.*?),').findall(str(bloque))

    for title, id_network in matches:
        title = clean_title(title, '').strip()

        title = title.capitalize()

        itemlist.append(item.clone(title=title, action = 'list_network', url=url, id_network=id_network, slug=item.slug, text_color=text_color ))

    return sorted(itemlist, key=(lambda x: x.title))


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

    url = url_generos

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'const genreDict(.*?)const years')

    matches = re.compile("'(.*?)':(.*?),").findall(str(bloque))

    for title, genre in matches:
        if item.group == 'anime':
            if title == 'Documental': continue

        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        genre = genre.strip()

        genre = '?genre=' + genre

        itemlist.append(item.clone( title=title, action = 'list_all', genre=genre, text_color=text_color ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.slug == 'animes': text_color = 'springgreen'
    else:
       if item.search_type == 'movie': text_color = 'deepskyblue'
       else: text_color = 'hotpink'

    if item.group == 'anime': url_years = host + 'animes/'
    else:
        if item.search_type == 'movie': url_years = host + 'peliculas/'
        else: url_years = host + 'series/'

    url = url_years

    if item.search_type == 'movie': tope_year = 1934
    else: tope_year = 1969

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        year = '?year=' + str(x)

        itemlist.append(item.clone( title=str(x), url=url, year=year, action = 'list_all', text_color=text_color ))

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

    url = url_idiomas

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'const languageDict(.*?)const qualityDict')

    matches = re.compile('"(.*?)":.*?"(.*?)",').findall(str(bloque))

    for title, idioma in matches:
        itemlist.append(item.clone( title=title, action = 'list_all', url=url, lang=idioma, text_color=text_color ))

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

    url = url_calidades

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'const qualityDict(.*?)const networkDict')

    bloque = bloque.replace('};', ',')

    matches = re.compile('"(.*?)":.*?"(.*?)",').findall(str(bloque))

    for calidad, title in matches:
        title = title.capitalize()

        itemlist.append(item.clone( title=title, action = 'list_all', url=url, qlty=calidad, text_color=text_color ))

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

    url = url_paises

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'const countriesDict(.*?)const genreDict')

    bloque = bloque.replace('};', ',')

    matches = re.compile('"(.*?)":.*?"(.*?)",').findall(str(bloque))

    for title, pais in matches:
        title = clean_title(title, '')

        title = title.replace('á', 'Á').replace('é', 'É').replace('i', 'Í').replace('ó', 'Ó').replace('ú', 'Ú').replace('Í', 'i').replace('ñ', 'Ñ')

        itemlist.append(item.clone( title=title, action = 'list_all', url=url, country=pais, text_color=text_color ))

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

    if item.lang: url = host + 'ajax.php/?lang='+ item.lang
    elif item.qlty: url = host + 'ajax.php/?qlty=' + item.qlty
    elif item.country: url = host + 'ajax.php/?country=' + item.country
    elif item.order: url = host + 'ajax.php' + item.order
    else: url = host + 'ajax.php' + item.genre + item.year

    data = do_downloadpage(url, post=post, referer=item.url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

                    if data:
                        data = do_downloadpage(url, post=post, referer=item.url)

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
        elif '/extraiptv.' in url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if year:
            if ',' in year: year = scrapertools.find_single_match(year, ',(.*?)$').strip()
        else: year = '-'

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

    url = host + 'ajax.php'

    data = do_downloadpage(url, post=post)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

                    if data:
                        data = do_downloadpage(url, post=post)

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
        elif '/extraiptv.' in url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if year:
            if ',' in year: year = scrapertools.find_single_match(year, ',(.*?)$').strip()
        else: year = '-'

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

            titulo = titulo.replace(str(season) + 'x' + str(epis), '').strip()
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

            if len(epis) == 2:
                if epis.startswith("0"): epis = epis.replace('0', '')

            titulo = str(season) + 'x' + str(epis) + ' ' + titulo.replace(str(season) + 'x' + str(epis), '')

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

    if not item.url: url_listas = host + 'listas/'
    else: url_listas = item.url

    url = url_listas

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article>.*?<a href="([^"]+)"[^<]+<h2>([^<]+)</h2>').findall(data)

    for url, title in matches:
        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        itemlist.append(item.clone( action = 'list_search', title = title, url = url, text_color='greenyellow' ))

    if itemlist:
        if '<div class="pagPlaydede">' in data:
            if 'Pagina Anterior' in data: patron = '<div class="pagPlaydede">.*?Pagina Anterior.*?<a href="([^"]+)'
            else: patron = '<div class="pagPlaydede"><a href="([^"]+)'

            next_page = scrapertools.find_single_match(data, patron)

            if next_page:
                if '?q=' in item.url:
                    target_action = scrapertools.find_single_match(item.url, 'q=(.*?)$')
                    next_page = next_page + '?q=' + target_action

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_listas', text_color = 'coral' ))

    return itemlist


def list_network(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if not item.post:
        post = {'_method': 'items', 'page': item.nro_pagina, 'network': item.id_network, 'ajaxName': 'main', 'slug': item.slug, 'orderBy=': item.order}
    else:
        post = item.post

    url_post = item.url.replace('/series', '/ajax.php')

    url_post = url_post + '?network=' + item.id_network

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

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        title = clean_title(title, url)

        if 'Tu directorio de' in title: continue
        elif '/extraiptv.' in url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if year:
            if ',' in year: year = scrapertools.find_single_match(year, ',(.*?)$').strip()
        else: year = '-'

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

            post = {'_method': 'items', 'page': item.nro_pagina, 'network': item.id_network, 'ajaxName': 'main', 'slug': item.slug, 'orderBy=': item.order}

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_network', url = item.url, nro_pagina = item.nro_pagina, post = post, page = 0, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    url = item.url

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    matches = re.compile('<div class="clickSeason.*?data-season="(.*?)"', re.DOTALL).findall(data)
    if not matches: matches = re.compile("<div class='clickSeason.*?data-season='(.*?)'", re.DOTALL).findall(data)

    if len(matches) > 25: platformtools.dialog_notification('PlayDede', '[COLOR blue][B]Cargando Temporadas[/B][/COLOR]')

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
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

    url = item.url

    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

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

        if config.get_setting('channels_charges', default=True):
            item.perpage = sum_parts
            if sum_parts >= 100:
                platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
        elif tvdb_id:
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

    url = item.url

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    # ~ Reproductor
    matches = re.compile('<div class="playerItem(.*?)</div></div>', re.DOTALL).findall(data)

    for match in matches:
        sid = scrapertools.find_single_match(match, 'data-loadPlayer="(.*?)"')
        if not sid: sid = scrapertools.find_single_match(match, "data-loadplayer='(.*?)'")

        server = scrapertools.find_single_match(match, '<h3>(.*?)</h3>').lower().strip()

        if not server or not sid: continue

        if server == 'alternativo': continue

        ses += 1

        if server == 'powvideo': continue
        elif server == 'streamplay': continue

        lang = scrapertools.find_single_match(match, 'data-lang="(.*?)"')

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        qlty = scrapertools.find_single_match(match, '">Calidad:.*?">(.*?)</span>')

        if server == 'filelions': other = 'Filelions'
        elif server == 'filemoon': other = 'Filemoon'
        elif server == 'streamwish': other = 'Streamwish'
        elif server == 'streamhub': other = 'Streamhub'
        elif server == 'uploaddo': other = 'Uploaddo'
        elif server == 'vembed': other = 'Vidguard'
        elif server == 'hexupload': other = 'Hexupload'
        elif server == 'userload': other = 'Userload'
        elif server == 'streamruby': other = 'Streamruby'
        elif server == 'streamsilk': other = 'Streamsilk'

        elif server == 'luluvideo':
              server = 'various'
              other = 'Lulustream'

        else: other = ''

        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', id = sid, language = lang, quality = qlty, other = other ))

    # ~ Enlaces
    bloque = scrapertools.find_single_match(data, '<div class="linkSorter">(.*?)<div class="contEP contepID_3">')

    matches = re.compile('data-quality="(.*?)".*?data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        if not url or not server: continue

        if server == 'alternativo': continue

        ses += 1

        server = server.lower().strip()

        if server == 'powvideo': continue
        elif server == 'streamplay': continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        if server == 'filelions': other = 'Filelions'
        elif server == 'filemoon': other = 'Filemoon'
        elif server == 'streamwish': other = 'Streamwish'
        elif server == 'streamhub': other = 'Streamhub'
        elif server == 'uploaddo': other = 'Uploaddo'
        elif server == 'vembed': other = 'Vidguard'
        elif server == 'hexupload': other = 'Hexupload'
        elif server == 'userload': other = 'Userload'
        elif server == 'streamruby': other = 'Streamruby'
        elif server == 'streamsilk': other = 'Streamsilk'

        elif server == 'luluvideo':
              server = 'various'
              other = 'Lulustream'

        else: other = 'E'

        server = servertools.corregir_servidor(server)

        if server == 'zures': other = servertools.corregir_zures(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, quality = qlty, other = other ))

    # ~ Descargas
    bloque = scrapertools.find_single_match(data, '<div class="contEP contepID_3">(.*?)$')

    matches = re.compile('data-quality="(.*?)".*?data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        if not url or not server: continue

        if '>recomendado<' in server: continue
        elif server == 'alternativo': continue

        ses += 1

        server = server.lower().strip()

        if '/ul.' in url: continue
        elif '/1fichier.' in url: continue
        elif '/ddownload.' in url: continue
        elif '/clk.' in url: continue
        elif '/rapidgator' in url: continue
        elif '/katfile' in url: continue
        elif '/nitro' in url: continue
        elif '/ouo.' in url: continue

        if 'https://netload.cc/st?' in url:
             url = scrapertools.find_single_match(url, '&url=(.*?)$')
             if not url: continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        server = servertools.corregir_servidor(server)

        other = 'D'

        if not server == 'directo':
            if server == 'various': other = servertools.corregir_other(server)
            elif server == 'zures': other = servertools.corregir_zures(url).capitalize()

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, quality = qlty, other = other ))

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

            if not url_play: url_play = scrapertools.find_single_match(data, 'var url = "(.*?)"')
            if not url_play: url_play = scrapertools.find_single_match(data, "var url = '(.*?)'")

    else:
        url_play = item.url

    if url_play:
        url_play = url_play.replace("\\/", "/")

        servidor = servertools.get_server_from_url(url_play)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url_play)

        if servidor == 'directo':
            new_server = servertools.corregir_other(url_play).lower()
            if new_server.startswith("http"): servidor = new_server

        itemlist.append(item.clone(url = url_play, server = servidor))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    username = config.get_setting('playdede_username', 'playdede', default='')

    if not username: return []

    if not item.page: item.page = 0

    url = item.url

    data = do_downloadpage(url)

    # ~ si se perdio la sesion (utoken)
    if data:
        if datos_ko in str(data):
            logout(item)
            login(item)
            data = do_downloadpage(url)

            if data:
                username = config.get_setting('playdede_username', 'playdede', default='')

                if not username in data:
                    logout(item)
                    login(item)
                    data = do_downloadpage(url)

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

        title = clean_title(title, url)

        if 'Tu directorio de' in title: continue
        elif '/extraiptv.' in url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>.*?, (\d+)</p>')
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

                next_page = scrapertools.find_single_match(data, patron)

                if next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_search', page = 0, text_color = 'coral' ))

    return itemlist


def clean_title(title, url):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u').replace('\\u00e0', 'a')

    title = title.replace('\\u2019', "'")

    title = title.replace('\\u00c0', "A").replace('\\u010c0', "C").replace('\\u00c5l', "Islas Al")

    if '\\u' in title:
        if url:
            data = do_downloadpage(url)
            data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

            titulo = scrapertools.find_single_match(data, "<h1>(.*?)</h1>")
            if not titulo: titulo = scrapertools.find_single_match(data, "<title>(.*?)</title>")

            titulo = titulo.replace('Ver película:', '').replace('Ver serie:', '').replace('Ver anime:', '').strip()

            if titulo: title = titulo

    return title


def show_current_domain(item):
    logger.info()

    current_domain = ''

    try:
        data = httptools.downloadpage('https://entrarplaydede.com/').data

        current_domain = scrapertools.find_single_match(data, '>Dirección actual:.*?<a href="(.*?)"')
        if not current_domain: current_domain = scrapertools.find_single_match(data, '>Dirección actual:.*?">(.*?)</a>').strip()

        if current_domain:
            current_domain = current_domain.lower()

            if not 'playdede' in current_domain: current_domain = ''

        if current_domain:
            if not 'https' in current_domain: current_domain  = 'https://' + current_domain
            if not current_domain.endswith('/'): current_domain = current_domain + '/'
    except:
        pass

    if not current_domain:
        platformtools.dialog_notification(config.__addon_name + ' - PlayDede', '[B][COLOR red]No se pudo comprobar[/B][/COLOR]')
        return

    domain = config.get_setting('dominio', 'playdede', default='')
    if not domain: domain = host

    if domain == current_domain:
        platformtools.dialog_ok(config.__addon_name + ' - PlayDede', '[COLOR gold][B]El dominio/host del canal es correcto.[/B]', '[COLOR cyan][B]' + current_domain + '[/B][/COLOR]')
        return

    procesar = True
    if domain == host: procesar = False

    if platformtools.dialog_yesno(config.__addon_name + ' - Nuevo Dominio PlayDede', '¿ [COLOR red][B]Nuevo Dominio[/B][/COLOR], Desea cambiarlo ?', 'Memorizado:  [COLOR yellow][B]' + domain + '[/B][/COLOR]', 'Actual..........:  [COLOR cyan][B]' + current_domain + '[/B][/COLOR]'):
        if procesar:
            logout(item)

        config.set_setting('dominio', current_domain, 'playdede')

        if procesar:
            login(item)

        platformtools.dialog_ok(config.__addon_name + ' - Playdede', '[COLOR yellow][B]Dominio Actual Memorizado, pero aún NO guardado.[/B][/COLOR]', 'Por favor,  [COLOR cyan][B]Retroceda Menús[/B][/COLOR] y acceda de Nuevo al Canal.')


def show_help_usuario(item):
    logger.info()

    preferidos = False
    if not config.get_setting('mnu_simple', default=False):
        if config.get_setting('mnu_preferidos', default=True):
            preferidos = True

    txt = '[COLOR red][B]Restricciones:[/B][/COLOR][CR]'
    txt += ' - [COLOR yellow][B]No se Gestionan las Referencias que tenga Asignadas en la Web, en sus Opciones de Usuario.[/B][/COLOR][CR]'
    txt += '   Respecto al Seguimiento de [COLOR deepskyblue][B]Películas[/B][/COLOR], [COLOR hotpink][B]Series[/B][/COLOR], [COLOR springgreen][B]Animes[/B][/COLOR] y [COLOR greenyellow][B]Listas[/B][/COLOR][CR]'

    txt += '[CR][COLOR cyan][B]Recomendación:[/B][/COLOR][CR]'

    txt += '   Si lo que desea es hacer un Seguimiento Completo de sus Listas,[CR]'

    txt += '   le sugerimos asigne cada Referencia a la opción [COLOR wheat][B]Preferidos[/B][/COLOR][CR]'

    if not preferidos:
        txt += '[CR][COLOR yellowgreen][B]Aviso:[/B][/COLOR][CR]'

        txt += '   No tiene Activada la Opción [COLOR wheat][B]Preferidos[/B][/COLOR] en sus [COLOR chocolate][B]Ajustes[/B][/COLOR] preferencias (categoría [COLOR tan][B]Menú[/B][/COLOR])'

    platformtools.dialog_textviewer('Información Menú Usuario', txt)


def show_credenciales(item):
    logger.info()

    domain = config.get_setting('dominio', 'playdede', default='')

    if not domain: domain = host

    if config.get_setting('playdede_login', 'playdede', default=False):
       domain += '[I][COLOR teal] (sesion)[/I][/COLOR]'
    else:
       domain += '[I][COLOR teal] (login)[/I][/COLOR]'

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    platformtools.dialog_ok(config.__addon_name + ' PlayDede - Credenciales', 'Domain.:  [COLOR cyan][B]' + domain + '[/B][/COLOR]', 'User......:  [COLOR yellow][B]' + username, '[/B][/COLOR]Pass.....:  [COLOR yellow][B]' + password + '[/B][/COLOR]')


def search(item, texto):
    logger.info()

    try:
        if item.search_type == 'all':
            if item.search_pop: config.set_setting('search_last_list', texto)

        if item.target_action == 'top':
            item.url = host + 'listas?q=' + texto.replace(" ", "+")
            return list_listas(item)
        else:
            item.url = host + 'search/?s=' + texto.replace(" ", "+")
            return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

