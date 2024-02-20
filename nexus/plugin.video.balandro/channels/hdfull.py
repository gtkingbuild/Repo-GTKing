# -*- coding: utf-8 -*-

import sys

PY3 = sys.version_info[0] >= 3
if PY3: unicode = str

import re, base64, xbmcgui

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, servertools, tmdb


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


# ~ webs para comprobar dominio vigente en actions pero pueden requerir proxies
# ~ webs  0)-'https://dominioshdfull.com/'  1)-'https://new.hdfull.one/'


dominios = [
         'https://hd-full.biz/',
         'https://hd-full.in/',
         'https://hd-full.im/',
         'https://hd-full.one/',
         'https://hdfull.icu/',
         'https://hdfull.quest/',
         'https://hdfull.today/',
         'https://hdfull.sbs/',
         'https://hdfull.store/',
         'https://hdfull.one/',
         'https://hdfull.org/',
         'https://new.hdfull.one/'
         ]


host = config.get_setting('dominio', 'hdfull', default=dominios[0])

ant_hosts = ['https://hdfull.sh/', 'https://hdfull.im/', 'https://hdfull.in/',
             'https://hdfull.pro/', 'https://hdfull.la/', 'https://hdfull.tv/',
             'https://hd-full.cc/', 'https://hdfull.me/', 'https://hdfull.io/',
             'https://hdfull.lv/', 'https://hdfullcdn.cc/', 'https://hdfull.stream/',
             'https://hdfull.click/', 'https://hdfull.link/', 'https://hdfull.lol/',
             'https://hdfull.fun/', 'https://hdfull.top/', 'https://hdfull.vip/',
             'https://hdfull.wtf/', 'https://hdfull.gdn/', 'https://hdfull.cloud/',
             'https://hdfull.video/', 'https://hdfull.work/', 'https://hdfull.life/',
             'https://hdfull.digital/']


if host in str(ant_hosts): config.set_setting('dominio', dominios[0], 'hdfull')


login_ok = '[COLOR chartreuse]HdFull Login correcto[/COLOR]'
start_ses_ok = '[COLOR chartreuse][B]Sesión Iniciada[/B][/COLOR], Por favor [COLOR cyan][B]Retroceda Menús[/B][/COLOR] y acceda de Nuevo al Canal.'

perpage = 20


class login_dialog(xbmcgui.WindowDialog):
    def __init__(self):
        avis = True
        if config.get_setting('hdfull_username', 'hdfull', default=False): 
            if config.get_setting('hdfull_password', 'hdfull', default=False):
                if config.get_setting('hdfull_login', 'hdfull', default=False): avis = False

        if avis:
            self.login_result = False
            platformtools.dialog_ok("Recomendación [B][COLOR yellow]HdFull[/B][/COLOR]", '[B][COLOR yellowgreen]Mejor crear una NUEVA cuenta para registrarse en la web, no deberíais informar ninguna de vuestras cuentas Personales.[/B][/COLOR]', 'Para más detalles al respecto, acceda a la Ayuda, apartado Canales, Información dominios que requieren registrarse.')

        self.background = xbmcgui.ControlImage(250, 150, 800, 355, filename=config.get_thumb('ContentPanel'))
        self.addControl(self.background)
        self.icon = xbmcgui.ControlImage(265, 220, 225, 225, filename=config.get_thumb('hdfull', 'thumb', 'channels'))
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
            config.set_setting('hdfull_username', self.username.getText(), 'hdfull')
            config.set_setting('hdfull_password', self.password.getText(), 'hdfull')
            config.set_setting('hdfull_login', True, 'hdfull')
            self.login_result = True
        else:
            avis = True
            if not self.username.getText():
                if not self.password.getText(): avis = False

            if avis:
                platformtools.dialog_notification('HdFull', '[B][COLOR red]Faltan credenciales[/B][/COLOR]')
                self.login_result = False

    def onControl(self, control):
        control = control.getId()
        if control in range(3000, 30010): self.close()


def do_make_login_logout(url, post=None):
    domain = config.get_setting('dominio', 'hdfull', default=dominios[0])

    hay_proxies = False
    if config.get_setting('channel_hdfull_proxies', default=''): hay_proxies = True

    if not url.startswith(domain):
        data = httptools.downloadpage(url, post=post, raise_weberror=False).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('hdfull', url, post=post, raise_weberror=False).data
        else:
            data = httptools.downloadpage(url, post=post, raise_weberror=False).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        if BR or BR2:
            try:
                ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
                if ck_name and ck_value:
                    httptools.save_cookie(ck_name, ck_value, domain.replace('https://', '')[:-1])

                if not url.startswith(domain):
                    data = httptools.downloadpage(url, post=post, raise_weberror=False).data
                else:
                    if hay_proxies:
                        data = httptools.downloadpage_proxy('hdfull', url, post=post, raise_weberror=False).data
                    else:
                        data = httptools.downloadpage(url, post=post, raise_weberror=False).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    return data


def login(item):
    logger.info()

    status = config.get_setting('hdfull_login', 'hdfull', default=False)

    domain = config.get_setting('dominio', 'hdfull', default=dominios[0])

    username = config.get_setting('hdfull_username', 'hdfull', default='')
    password = config.get_setting('hdfull_password', 'hdfull', default='')

    data = ''

    domain_unknow = False

    if domain:
        if domain in dominios:
            if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', domain, 'hdfull')

            if username:
                if password:
                    data = do_make_login_logout(domain + 'login')
                    if not data: return False
        else:
            domain_unknow = True

    user = scrapertools.find_single_match(data, '<a href="[^"]+" class="tour-join2 join">([^<]+)<\/a>')

    if user:
        if username:
            if username in user:
                if not status: config.set_setting('hdfull_login', True, 'hdfull')

                if not item: platformtools.dialog_notification(config.__addon_name, login_ok)
                else:
                   if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)

                if item:
                    if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' HdFull', start_ses_ok)
                return True

    if not username or not password:
        login = login_dialog()
        if not login.login_result: return False

        if not item:
            if not domain: config.set_setting('dominio', dominios[0], 'hdfull')
            else:
               if not domain in dominios: config.set_setting('dominio', dominios[0], 'hdfull')

            platformtools.dialog_notification(config.__addon_name, '[COLOR yellow]HdFull Credenciales guardadas[/COLOR]')
            return False

    username = config.get_setting('hdfull_username', 'hdfull', default='')
    password = config.get_setting('hdfull_password', 'hdfull', default='')

    url = '%slogin' %(domain)

    data = do_make_login_logout(url)
    if not data:
        if domain_unknow: platformtools.dialog_notification(config.__addon_name + ' - HdFull', 'Comprobar Dominio [COLOR moccasin]' + domain + '[/COLOR]')
        return False

    sid = scrapertools.find_single_match(data, '__csrf_magic.*?value="(.*?)"')
    if sid:
        post = {'__csrf_magic': sid, 'username': username, 'password': password, 'action': 'login'}
        data = do_make_login_logout(url, post=post)

        if 'Bienvenido %s' % username in data or "<script>window.location='/'" in data or "<script>window.location=''" in data:
            if not status:
                config.set_setting('hdfull_login', True, 'hdfull')
                if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)
            else:
                if config.get_setting('notificar_login', default=False): platformtools.dialog_notification(config.__addon_name, login_ok)

            if item:
                if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' HdFull', start_ses_ok)
            return True

    post = {'username': username, 'password': password}

    data = do_make_login_logout(url, post=post)
    if not data:
        if domain_unknow: platformtools.dialog_notification(config.__addon_name + ' - HdFull', 'Comprobar Dominio [COLOR moccasin]' + domain + '[/COLOR]')
        return False

    jdata = jsontools.load(data)

    if jdata:
        try:
            if jdata.get('status') == "OK":
                if not status: config.set_setting('hdfull_login', True, 'hdfull')

                if item:
                    if item.start_ses: platformtools.dialog_ok(config.__addon_name + ' HdFull', start_ses_ok)
                return True
        except:
            pass

    platformtools.dialog_notification(config.__addon_name, '[COLOR red]HdFull Login incorrecto[/COLOR]')
    return False


def logout(item):
    logger.info()

    domain = config.get_setting('dominio', 'hdfull', default=dominios[0])

    url = "%slogout" %(domain)

    data = do_make_login_logout(url)

    config.set_setting('hdfull_login', False, 'hdfull')

    platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]HdFull Sesión cerrada[/COLOR]')

    if item:
        if item.category: 
            platformtools.dialog_ok(config.__addon_name + ' HdFull', '[COLOR yellow][B]Sesión Cerrada[/B][/COLOR].', 'Por favor [COLOR cyan][B]Retroceda Menús[/B][/COLOR] e [COLOR chartreuse][B]Inicie Sesión[/B][/COLOR] de nuevo.')


def item_configurar_dominio(item):
    plot = 'Este canal tiene varios posibles dominios. Si uno no te funciona puedes probar con los otros antes de intentarlo con proxies.'
    return item.clone( title = '[B]Configurar dominio a usar ...[/B]', action = 'configurar_dominio', folder=False, plot=plot, text_color='yellowgreen' )

def configurar_dominio(item):
    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])
    num_dominio = dominios.index(dominio) if dominio in dominios else 0
    ret = platformtools.dialog_select('Dominio a usar HdFull', dominios, preselect=num_dominio)
    if ret == -1: return False

    if not dominio == dominios[ret]:
        if config.get_setting('hdfull_login', 'hdfull', default=False):
            logout(item)

    config.set_setting('dominio', dominios[ret], 'hdfull')

    platformtools.itemlist_refresh()
    return True


def item_configurar_proxies(item):
    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_hdfull_proxies', default=''):
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
    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, dominio)


def do_downloadpage(url, post=None, referer=None):
    username = config.get_setting('hdfull_username', 'hdfull', default='')

    if not username:
        platformtools.dialog_notification('HdFull', '[COLOR red][B]Faltan[COLOR teal][I]Credenciales Cuenta[/I] [/B][/COLOR]')
        return ''

    domain = config.get_setting('dominio', 'hdfull', default=dominios[0])

    # ~ por si viene de enlaces guardados posteriores
    if url.startswith('/'): url = domain + url[1:] # ~ solo v. 2.0.0

    for ant in ant_hosts:
        url = url.replace(ant, domain)

    # ~ por si viene de opcion menu pral. Generos
    if not domain in url:
        for dom in dominios:
            url = url.replace(dom, domain)

    headers = {}

    if referer: headers = {'Referer': referer}
    else: headers = {'Referer': domain}

    hay_proxies = False
    if config.get_setting('channel_hdfull_proxies', default=''): hay_proxies = True

    if not url.startswith(domain):
        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
    else:
        if hay_proxies:
            data = httptools.downloadpage_proxy('hdfull', url, post=post, headers=headers, raise_weberror=False).data
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
                        data = httptools.downloadpage_proxy('hdfull', url, post=post, headers=headers, raise_weberror=False).data
                    else:
                        data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
            except:
                pass

    if '<title>Just a moment...</title>' in data:
        if not 'buscar' in url:
            platformtools.dialog_notification(config.__addon_name, '[COLOR red][B]CloudFlare[COLOR orangered] Protection[/B][/COLOR]')
        return ''

    if '<div id="popup_login_result"></div>' in data:
        if not config.get_setting('hdfull_login', 'hdfull', default=False):
            platformtools.dialog_notification(config.__addon_name, '[COLOR yellow][B]HdFull Debe iniciar Sesión[/B][/COLOR]')

        result = login('')
        if result == True: return do_downloadpage(url, post=post, referer=referer)

    return data


def acciones(item):
    logger.info()
    itemlist = []

    domain_memo = config.get_setting('dominio', 'hdfull', default='')

    if domain_memo: url = domain_memo
    else: url = host

    itemlist.append(Item( channel='actions', action='show_latest_domains', title='[COLOR moccasin][B]Últimos Cambios de Dominios[/B][/COLOR]', thumbnail=config.get_thumb('pencil') ))

    itemlist.append(Item( channel='helper', action='show_help_domains', title='[B]Información Dominios[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    itemlist.append(item.clone( channel='domains', action='test_domain_hdfull', title='Test Web del canal [COLOR yellow][B] ' + url + '[/B][/COLOR]',
                                from_channel='hdfull', folder=False, text_color='chartreuse' ))

    username = config.get_setting('hdfull_username', 'hdfull', default='')

    if username:
        itemlist.append(Item( channel='domains', action='operative_domains_hdfull', title='[B]Dominios Operativos Vigentes[/B]',
                              desde_el_canal = True, thumbnail=config.get_thumb('settings'), text_color='mediumaquamarine' ))

        itemlist.append(Item( channel='domains', action='last_domain_hdfull', title='[B]Comprobar último dominio vigente[/B]',
                              desde_el_canal = True, host_canal = url, thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    if domain_memo: title = '[B]Modificar/Eliminar el dominio memorizado[/B]'
    else: title = '[B]Informar Nuevo Dominio manualmente[/B]'

    itemlist.append(item.clone( channel='domains', action='manto_domain_hdfull', title=title, desde_el_canal = True, folder=False, thumbnail=config.get_thumb('keyboard'), text_color='darkorange' ))

    if not config.get_setting('hdfull_login', 'hdfull', default=False):
        if username:
            itemlist.append(item.clone( title = '[COLOR chartreuse][B]Iniciar sesión[/B][/COLOR]', action = 'login', start_ses = True ))

            itemlist.append(item.clone( title = '[COLOR springgreen][B]Ver las credenciales[/B][/COLOR]', action = 'shuw_credenciales', thumbnail=config.get_thumb('pencil') ))
            itemlist.append(Item( channel='domains', action='del_datos_hdfull', title='[B]Eliminar credenciales cuenta[/B]', thumbnail=config.get_thumb('folder'), text_color='crimson' ))
        else:
            itemlist.append(Item( channel='helper', action='show_help_register', title='[B]Información para registrarse[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

            itemlist.append(item.clone( title = '[COLOR crimson][B]Credenciales cuenta[/B][/COLOR]', action = 'login' ))

    if config.get_setting('hdfull_login', 'hdfull', default=False):
        itemlist.append(item.clone( title = '[COLOR chartreuse][B]Cerrar sesión[/B][/COLOR]', action = 'logout' ))

        itemlist.append(item.clone( title = '[COLOR springgreen][B]Ver las credenciales[/B][/COLOR]', action = 'shuw_credenciales', thumbnail=config.get_thumb('pencil') ))
        itemlist.append(Item( channel='domains', action='del_datos_hdfull', title='[B]Eliminar credenciales cuenta[/B]', thumbnail=config.get_thumb('folder'), text_color='crimson' ))

    itemlist.append(item_configurar_dominio(item))
    itemlist.append(item_configurar_proxies(item))

    itemlist.append(Item( channel='helper', action='show_help_hdfull', title='[COLOR aquamarine][B]Aviso[/COLOR] [COLOR green]Información[/B][/COLOR] canal', thumbnail=config.get_thumb('help') ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('hdfull_login', 'hdfull', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('hdfull_login', 'hdfull', default=False):
        itemlist.append(item.clone( title = '[COLOR teal][B]Menú usuario[/B][/COLOR]', action = 'mainlist_user', search_type = 'all' ))

        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas populares[/B][/COLOR]', action = 'list_listas', target_action = 'top', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

        itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

        itemlist.append(item.clone( title='Novelas', action = 'mainlist_series', text_color = 'limegreen' ))
        itemlist.append(item.clone( title='Doramas', action = 'mainlist_series', text_color = 'firebrick' ))

        if not config.get_setting('descartar_anime', default=False):
            itemlist.append(item.clone( title='Animes', action = 'mainlist_series', text_color = 'springgreen' ))

        itemlist.append(item.clone( title = 'Búsqueda de personas:', action = '', folder=False, text_color='tan' ))

        itemlist.append(item.clone( title = ' - Buscar intérprete ...', action = 'search', group = 'actor', search_type = 'person',
                                    plot = 'Debe indicarse el nombre y apellido/s del intérprete (lo más exacto posible).'))
        itemlist.append(item.clone( title = ' - Buscar dirección ...', action = 'search', group = 'director', search_type = 'person',
                                    plot = 'Debe indicarse el nombre y apellido/s del director (lo más exacto posible).'))

        itemlist.append(item.clone( title = 'Búsqueda en listas populares:', action = '', folder=False, text_color='tan' ))
        itemlist.append(item.clone( title = ' - Buscar lista ...', action = 'search', target_action = 'top', search_type = 'all',
                                    plot = 'Debe indicarse el título de la lista (ó parte del mismo).'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('hdfull_login', 'hdfull', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('hdfull_login', 'hdfull', default=False):
        dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

        if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

        itemlist.append(item.clone( title = '[COLOR teal][B]Menú usuario[/B][/COLOR]', action = 'mainlist_user', search_type = 'movie' ))

        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas populares[/B][/COLOR]', action = 'list_listas', target_action = 'top', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

        itemlist.append(item.clone( action='list_all', title='Catálogo', url = dominio + 'peliculas', search_type = 'movie' ))

        itemlist.append(item.clone( action='list_all', title='Últimos estrenos', url = dominio + 'peliculas-estreno', search_type = 'movie', text_color='cyan' ))
        itemlist.append(item.clone( action='list_all', title='Últimas actualizadas', url = dominio + 'peliculas-actualizadas', search_type = 'movie' ))

        itemlist.append(item.clone( action='list_all', title='Más valoradas', url = dominio + 'peliculas/imdb_rating', search_type = 'movie' ))

        itemlist.append(item.clone( action='list_all', title='Por fecha', url = dominio + 'peliculas/date', search_type = 'movie' ))
        itemlist.append(item.clone( action='list_all', title='Por alfabético', url = dominio + 'peliculas/abc', search_type = 'movie' ))
        itemlist.append(item.clone( action='generos', title='Por género', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('hdfull_login', 'hdfull', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('hdfull_login', 'hdfull', default=False):
        dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

        if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

        itemlist.append(item.clone( title = '[COLOR teal][B]Menú usuario[/B][/COLOR]', action = 'mainlist_user', search_type = 'tvshow' ))

        itemlist.append(item.clone( title = '[COLOR moccasin][B]Listas populares[/B][/COLOR]', action = 'list_listas', target_action = 'top', search_type = 'all' ))

        itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

        itemlist.append(item.clone( action='list_all', title='Catálogo', url = dominio + 'series', search_type = 'tvshow' ))

        itemlist.append(item.clone( action='list_all', title='Últimas', url = dominio + 'series/date', search_type='tvshow', text_color='cyan' ))

        itemlist.append(item.clone( action='list_all', title='Más valoradas', url= dominio + 'series/imdb_rating', search_type = 'tvshow' ))

        itemlist.append(item.clone( action='list_all', title='Novelas', url= dominio + 'tags-tv/soap', search_type = 'tvshow', text_color='limegreen' ))
        itemlist.append(item.clone( action='list_all', title='Doramas', url= dominio + 'tags-tv/dorama', search_type = 'tvshow', text_color='firebrick' ))

        if not config.get_setting('descartar_anime', default=False):
            itemlist.append(item.clone( action='list_all', title='Animes', url= dominio + 'tags-tv/anime', search_type = 'tvshow', text_color='springgreen' ))

        itemlist.append(item.clone( title = 'Episodios:', action = '', folder=False, text_color='tan' ))

        itemlist.append(item.clone( action='list_episodes', title=' - [COLOR cyan]Estreno[/COLOR]', opcion = 'premiere', search_type = 'tvshow' ))

        if not config.get_setting('descartar_anime', default=False):
            itemlist.append(item.clone( action='list_episodes', title=' - [COLOR springgreen]Anime[/COLOR]', opcion = 'anime', search_type = 'tvshow' ))

        itemlist.append(item.clone( action='list_episodes', title=' - [COLOR moccasin]Últimos[/COLOR]', opcion = 'latest', search_type = 'tvshow' ))
        itemlist.append(item.clone( action='list_episodes', title=' - Actualizados', opcion = 'updated', search_type = 'tvshow' ))

        itemlist.append(item.clone( action='series_abc', title='Por letra (A - Z)', search_type = 'tvshow' ))

        itemlist.append(item.clone( action='generos', title='Por género', search_type = 'tvshow' ))

    return itemlist


def mainlist_user(item):
    logger.info()
    itemlist = []

    domain = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    data = do_downloadpage(domain)

    patron = '<a href="[^"]+" class="dropdown-toggle"><b class="caret"><\/b>.*?Mi Cuenta</a>\s*<ul class="dropdown-menu">(.*?)</ul>'

    bloque = scrapertools.find_single_match(data, patron)

    matches = re.compile('<li><a href="([^"]+)">([^<]+)').findall(bloque)

    for url, title in matches:
        if title in ['Pedidos', 'Ajustes', 'Salir']: continue

        if title == 'Mis Peliculas': tipo_list = 'movies'
        elif title == 'Mis Series': tipo_list = 'shows'
        elif title == 'Mis Listas': tipo_list = 'listas'

        if not item.search_type == 'all':
            if item.search_type == 'movie':
                if tipo_list == 'shows': continue
            elif item.search_type == 'tvshow':
                if tipo_list == 'movies': continue

        itemlist.append(item.clone( title = title, url = domain + url if not url.startswith('/') else domain + url[1:],
                                    action = 'user_subsections', search_type = item.search_type, tipo_list = tipo_list, text_color = 'yellow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': text_color = 'deepskyblue'
    else: text_color = 'hotpink'

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    data = do_downloadpage(dominio)

    tipo_gen = 'TV' if item.search_type == 'tvshow' else 'Pel&iacute;culas'

    bloque = scrapertools.find_single_match(data, '<b class="caret"></b>&nbsp;&nbsp;%s</a>\s*<ul class="dropdown-menu">(.*?)</ul>' % tipo_gen)

    matches = re.compile('<li><a href="([^"]+)">([^<]+)', re.DOTALL).findall(bloque)
    for url, title in matches:
        if item.search_type == 'movie':
            if title == 'Novela': continue

        if config.get_setting('descartar_anime', default=False):
            if title == 'Anime': continue

        if url.startswith('/'): url = dominio + url[1:]

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', text_color = text_color ))

    return sorted(itemlist, key=lambda it: it.title)


def series_abc(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    for letra in '9ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        itemlist.append(item.clone( title = letra if letra != '9' else '#', url = dominio + 'series/abc/' + letra, action = 'list_all', text_color = 'hotpink' ))

    return itemlist


def detectar_idiomas(txt):
    languages = []
    if '/spa.png' in txt: languages.append('Esp')
    if '/lat.png' in txt: languages.append('Lat')
    if '/sub.png' in txt: languages.append('Vose')
    if '/eng.png' in txt: languages.append('Eng')
    return languages


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    if item.search_post:
        data = do_downloadpage(item.url, post=item.search_post, referer = item.referer if item.referer else dominio + ('series' if item.search_type == 'tvshow' else 'peliculas'))
    else:
        data = do_downloadpage(item.url)

    patron = '<div class="item"[^>]*">'
    patron += '\s*<a href="([^"]+)"[^>]*>\s*<img class="[^"]*"\s+src="([^"]+)"[^>]*>'
    patron += '\s*</a>\s*</div>\s*<div class="rating-pod">\s*<div class="left">(.*?)</div>'
    patron += '.*? title="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.search_post != '' and item.search_type != 'all':
        matches = list(filter(lambda x: ('/pelicula/' in x[0] and item.search_type == 'movie') or ('/serie/' in x[0] and item.search_type == 'tvshow'), matches))

    num_matches = len(matches)

    for url, thumb, langs, title in matches[item.page * perpage:]:
        title = title.strip()

        languages = detectar_idiomas(langs)

        if url.startswith('/'): url = dominio + url[1:]

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=', '.join(languages), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, languages=', '.join(languages), fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, referer=item.url, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
                buscar_next = False

        if buscar_next:
            next_page_link = scrapertools.find_single_match(data, '<a href="([^"]+)">&raquo;</a>')

            if next_page_link:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page_link, page = 0, action = 'list_all', text_color = 'coral' ))

    return itemlist


def list_episodes(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.opcion: item.opcion = 'latest'
    if not item.desde: item.desde = 0

    post = 'action=%s&start=%d&limit=%d&elang=ALL' % (item.opcion, item.desde, perpage)

    data = jsontools.load(do_downloadpage(dominio + 'a/episodes', post=post, referer = dominio + 'episodios'))

    for epi in data:
        show = epi['show']['title']['es'] if 'es' in epi['show']['title'] and epi['show']['title']['es'] != '' else epi['show']['title']['en'] if 'en' in epi['show']['title'] else ''

        tit = epi['title']['es'] if 'es' in epi['title'] and epi['title']['es'] != '' else epi['title']['en'] if 'en' in epi['title'] else ''
        titulo = '%s %sx%s %s' % (show, epi['season'], epi['episode'], tit)

        langs = ['Vose' if idio == 'ESPSUB' else idio.capitalize() for idio in epi['languages']]
        if langs: titulo += ' [COLOR %s]%s[/COLOR]' % (color_lang, ', '.join(langs))

        thumb = dominio + 'tthumb/220x124/' + epi['thumbnail']

        url_serie = dominio + 'serie/' + epi['show']['permalink']
        url_tempo = url_serie + '/temporada-' + epi['season']
        url = url_tempo + '/episodio-' + epi['episode']

        context = []
        context.append({ 'title': '[B][COLOR pink]Temporada %s[/COLOR][/B]' % epi['season'], 
                         'action': 'episodios', 'url': url_tempo, 'context': '', 'folder': True, 'link_mode': 'update' })

        context.append({ 'title': '[B][COLOR hotpink]Temporadas[/COLOR][/B]',
                         'action': 'temporadas', 'url': url_serie, 'context': '', 'folder': True, 'link_mode': 'update' })

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, context = context,
                                    contentType = 'episode', contentSerieName = show, contentSeason = epi['season'], contentEpisodeNumber = epi['episode'] ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) >= perpage:
            itemlist.append(item.clone( title = 'Siguientes ...', desde = item.desde + perpage, action = 'list_episodes', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    try: tmdb.set_infoLabels(item)
    except: pass

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    data = do_downloadpage(item.url, referer = item.referer if item.referer else '%s/buscar/' % dominio)

    any = scrapertools.find_single_match(data, '<a href="/buscar/year/.*?">(.*?)</a>')

    poster = scrapertools.find_single_match(data, '<div class="show-poster">.*?<img src="(.*?)"')

    sid = scrapertools.find_single_match(data, "var sid = '([^']+)';")

    patron = 'itemprop="season"[^>]*>'
    patron += '\s*<a href=\'([^\']+)\'[^>]*>\s*<img class="[^"]*"\s+original-title="([^"]+)"\s+alt="[^"]*"\s+src="([^"]+)"[^>]*>'
    patron += '\s*<h5[^>]*>([^<]+)</h5>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    # ~  Temporadas ocultas pero son accesibles en la mayoria de los casos
    seasons_hiden = False

    if matches:
        total_temporadas = len(matches)

        try:
            if item.infoLabels['tmdb_id'] and item.infoLabels['number_of_seasons'] and int(item.infoLabels['number_of_seasons']) > total_temporadas:
                base_hiden = str(matches[0])

                base_hiden = base_hiden.replace("'", '').replace('(', '').replace(')', '').strip()

                total_seasons = int(item.infoLabels['number_of_seasons'])

                if "'Temporada 0'" in str(matches): total_seasons =+ 1

                if total_seasons > 99: total_seasons = 99

                i = 1

                while i <= total_seasons:
                   if not "'Temporada " + str(i) + "'" in str(matches):
                       match_hiden_url = scrapertools.find_single_match(base_hiden, '(.*?)/temporada-')

                       match_hiden_url = match_hiden_url + '/temporada-' + str(i)
                       match_hiden_tit = 'Temporada ' + str(i)

                       seasons_hiden = True

                       try:
                            post = 'action=season&show=%s&season=%s' % (sid, str(i))
                            data = jsontools.load(do_downloadpage(dominio + 'a/episodes', post=post, referer=item.url))

                            if not data: break
                       except:
                            pass

                       matches = matches + [(match_hiden_url, match_hiden_tit, '', match_hiden_tit)]

                   i += 1
        except:
            import traceback
            logger.error(traceback.format_exc())


    for url, title, thumb, retitle in matches:
        if title not in ['Especiales', 'Specials']:
            numtempo = scrapertools.find_single_match(title, 'Temporada (\d+)')
            if numtempo == '': numtempo = scrapertools.find_single_match(url, '-(\d+)$')

            if numtempo == '': continue
        else:
            numtempo = 0

        titulo = title
        if retitle != title: titulo += ' - ' + retitle

        if len(matches) == 1:
            if config.get_setting('channels_seasons', default=True):
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.page = 0
            item.referer = item.url
            item.url = url
            item.thumbnail = thumb
            item.sid = sid
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', url = url, title = titulo, thumbnail = thumb, sid = sid, referer = item.url, page = 0,
                                    contentType = 'season', contentSeason = numtempo, text_color = 'tan' ))

    # ~  Temporadas ocultas No detectadas
    if not seasons_hiden:
        if itemlist:
            if sid:
                if poster: thumb = poster
                if not any: any = '-'

                last_tempo = int(numtempo)
                last_url = scrapertools.find_single_match(url, '(.*?)/temporada-')

                try:
                    while last_tempo <= 99:
                        last_tempo = last_tempo + 1

                        post = 'action=season&show=%s&season=%s' % (sid, str(last_tempo))

                        data = jsontools.load(do_downloadpage(dominio + 'a/episodes', post=post, referer=item.url))

                        if not data: break

                        url = last_url + '/temporada-' + str(last_tempo)
                        title = 'Temporada ' + str(last_tempo)

                        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb, page = 0, sid = sid, referer = item.url,
                                                    contentType = 'season', contentSeason = last_tempo, infoLabels={'year': any}, text_color = 'tan' ))
                except:
                    pass

    # Alguna serie de una sola temporada que no la tiene identificada
    if len(itemlist) == 0:
        itemlist.append(item.clone( action='episodios', url = item.url + '/temporada-1', title = 'Temporada 1',
                                    sid = sid, referer = item.url, page = 0, contentType = 'season', contentSeason = 1, text_color = 'tan' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    try:
        if not item.sid:
            data = do_downloadpage(item.url)
            item.sid = scrapertools.find_single_match(data, "var sid = '([^']+)';")
            if not item.sid: return itemlist

        post = 'action=season&show=%s&season=%s' % (item.sid, item.contentSeason)
        data = jsontools.load(do_downloadpage(dominio + 'a/episodes', post=post, referer=item.referer))
    except:
        return itemlist

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(data)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('HdFull', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            item.perpage = sum_parts

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFull', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFull', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]125[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFull', '[COLOR cyan]Cargando 125 elementos[/COLOR]')
                    item.perpage = 125

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('HdFull', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('HdFull', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for epi in data[item.page * item.perpage:]:
        tit = epi['title']['es'] if 'es' in epi['title'] and epi['title']['es'] else epi['title']['en'] if 'en' in epi['title'] and epi['title']['en'] else ''
        titulo = '%sx%s %s' % (epi['season'], epi['episode'], tit)

        langs = ['Vose' if idio == 'ESPSUB' else idio.capitalize() for idio in epi['languages']]
        if langs: titulo += ' [COLOR %s]%s[/COLOR]' % (color_lang, ', '.join(langs))

        thumb = dominio + 'tthumb/220x124/' + epi['thumbnail']
        url = item.url + '/episodio-' + epi['episode']

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = epi['season'], contentEpisodeNumber = epi['episode'] ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(data) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['CAM', 'cam', 'TS', 'ts', 'DVDSCR', 'dvdscr', 'DVDRIP', 'dvdrip', 'HDTV', 'hdtv', 'RHDTV', 'rhdtv', 'HD720', 'hd720', 'HD1080', 'hd1080']
    if txt not in orden: return 0

    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    data_js = do_downloadpage(dominio + 'templates/hdfull/js/jquery.hdfull.view.min.js')

    key = scrapertools.find_single_match(data_js, 'JSON.parse\(atob.*?substrings\((.*?)\)')
    if not key: 
        key = scrapertools.find_single_match(data_js, 'JSON.*?\]\((0x[0-9a-f]+)\)\);')
        if key: key = int(key, 16)
        else: key = scrapertools.find_single_match(data_js, 'JSON.*?\]\(([0-9]+)\)\);')

    data_js = do_downloadpage(dominio + 'js/providers.js')

    # ~ 31/7/2022  "22": {"t": "d", "d": "https://mexa.sh/%s"},
    # ~ 15/8/2022  "7": {"t": "s", "d": "https://watchsb.com/%s.html"},

    provs = {
             "4": {"t": "s", "d": "https://upstream.to/embed-%s.html"}, 
             "5": {"t": "s", "d": "https://cloudvideo.tv/embed-%s.html"},
             "6": {"t": "s", "d": "https://streamtape.com/e/%s"},
             "8": {"t": "d", "d": "https://www.filefactory.com/file/%s"},
             "9": {"t": "d", "d": "https://uploaded.net/f/%s"},
             "10": {"t": "d", "d": "https://rapidgator.net/file/%s.html"},
             "12": {"t": "s", "d": "https://gamovideo.net/embed-%s.html"},
             "14": {"t": "s", "d": "https://vidlox.me/embed-%s.html"},
             "15": {"t": "s", "d": "https://mixdrop.co/e/%s"},
             "16": {"t": "s", "d": "https://videobin.co/embed-%s.html"},
             "23": {"t": "d", "d": "https://1fichier.com/?%s"},
             "24": {"t": "d", "d": "https://katfile.com/%s"},
             "27": {"t": "d", "d": "https://nitroflare.com/%s"},
             "31": {"t": "s", "d": "https://vidoza.net/embed-%s.html"},
             "35": {"t": "s", "d": "https://uptobox.com/%s"},
             "38": {"t": "s", "d": "https://clicknupload.cc/%s"},
             "40": {"t": "s", "d": "https://vidmoly.me/embed-%s.html"},
             "45": {"t": "s", "d": "https://waaw.to/f/%s"}
             }

    # ~ try:
        # ~ provs = balandroresolver.hdfull_providers(data_js)
        # ~ if not provs: return itemlist
    # ~ except:
        # ~ return itemlist

    data = do_downloadpage(item.url, referer = dominio)

    data_obf = scrapertools.find_single_match(data, "var ad\s*=\s*'([^']+)")

    try:
       data_decrypt = jsontools.load(balandroresolver.obfs(base64.b64decode(data_obf), 126 - int(key)))
    except:
       return itemlist

    ses = 0

    matches = []

    for match in data_decrypt:
        if match['provider'] in provs:
            # ~ 31/12/2021
            try:
                embed = provs[match["provider"]]["t"]
                url = provs[match["provider"]]["d"] % match["code"]
                matches.append([match["lang"], match["quality"], url, embed])
            except:
                ses += 1

            # ~ try:
               # ~ embed = provs[match['provider']][0]
               # ~ url = eval(provs[match['provider']][1].replace('_code_', "match['code']"))
               # ~ matches.append([match['lang'], match['quality'], url, embed])
            # ~ except:
               # ~ pass
        else:
            ses += 1

    for idioma, calidad, url, embed in matches:
        ses += 1

        if embed == 'd':
            if not 'uptobox' in url: continue

        elif '/powvideo.' in url: continue
        elif '/streamplay.' in url: continue

        if not PY3: calidad = unicode(calidad, 'utf8').upper().encode('utf8')

        idioma = idioma.capitalize() if idioma != 'ESPSUB' else 'Vose'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, language = idioma, quality = calidad, quality_num = puntuar_calidad(calidad) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def user_subsections(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<a data-action="([^"]+)">([^<]+)').findall(data)

    for action, title in matches:
        if item.search_type == 'movie': text_color = 'deepskyblue'
        elif item.search_type == 'tvshow': text_color = 'hotpink'
        else: text_color = 'tan'

        itemlist.append(item.clone( title = title, target_action = action, action = 'list_user_subsections' if item.tipo_list != 'listas' else 'list_listas', text_color = text_color))

    return itemlist


def list_user_subsections(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    perpage = 28

    domain = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    if item.post:
        post = item.post
        tope = scrapertools.find_single_match(item.post, 'limit=(\d+)')
    else:
        post = "target=%s&action=%s&start=0&limit=28" % (item.tipo_list, item.target_action)
        tope = perpage

    url = "%sa/my?" % domain

    data = do_downloadpage(url, post=post)

    data = jsontools.load(data)

    for match in data:
        title = match.get('title').get('es') if match.get('title').get('es') else match.get('title').get('en')

        season = scrapertools.find_single_match(str(match), "'season':.*?'(.*?)'")
        episode = scrapertools.find_single_match(str(match), "'episode':.*?'(.*?)'")

        epis = False

        if season and episode:
            epis = True

            show_title = scrapertools.find_single_match(str(match), "'show_title':.*?'es':.*?'(.*?)'")
            if not show_title: show_title = scrapertools.find_single_match(str(match), "'show_title':.*?'en':.*?'(.*?)'")

            SerieName = show_title

            if title: title = season + 'x' + episode + ' ' + show_title + '  (' + title + ')'
            else: title = season + 'x' + episode + ' ' + show_title

        thumb = '%sthumb/172x256/%s' % (domain, match.get('thumb'))

        perma = match.get('perma')
        if not perma: perma = match.get('permalink')

        if item.tipo_list == 'movies':
            url = '%spelicula/%s' % (domain, perma)

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        else:
            if epis:
                url = '%sserie/%s/temporada-%s/episodio-%s' % (domain, perma, season, episode)

                itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentSerieName = SerieName,
                                            contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode, infoLabels = {'year': '-'} ))

            else:
                url = '%sserie/%s' % (domain, perma)

                itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, page = 0, contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) >= int(tope):
            next_start = (item.page * perpage)
            next_page = item.page + 1

            next_post = 'target=%s&action=%s&start=%s&limit=28' % (item.tipo_list, item.target_action, next_start)

            itemlist.append(item.clone( title = 'Siguientes ...', post = next_post, page = next_page, pageaction = 'list_user_subsections', text_color = 'coral' ))

    return itemlist


def list_listas(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    perpage = 28

    domain = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    url = '%sa/my?' % domain

    if item.post:
        post = item.post
        tope = scrapertools.find_single_match(item.post, 'limit=(\d+)')
    else:
        post = 'target=lists&action=%s&start=0&limit=28' % (item.target_action)
        tope = perpage

    data = jsontools.load(do_downloadpage(url, post=post))

    for match in data:
        title = match.get('title')
        url = '%slista/%s' % (domain, match.get('permalink'))

        if item.target_action == 'top': text_color = 'moccasin'
        else: text_color = ''

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, page = 0, text_color = text_color ))

    if itemlist:
        if len(itemlist) >= int(tope):
            if not '&search=' in post:
                next_start = (item.page * perpage)
                next_page = item.page + 1

                next_post = 'target=lists&action=%s&start=%s&limit=28' % (item.target_action, next_start)

                itemlist.append(item.clone( title = 'Siguientes ...', post = next_post, page = next_page, pageaction = 'list_listas', text_color = 'coral' ))

    return itemlist


def shuw_credenciales(item):
    logger.info()

    username = config.get_setting('hdfull_username', 'hdfull', default='')
    password = config.get_setting('hdfull_password', 'hdfull', default='')

    platformtools.dialog_ok(config.__addon_name + ' HdFull - Credenciales', 'User..:  [COLOR yellow][B]' + username, '[/B][/COLOR]Pass.:  [COLOR yellow][B]' + password + '[/B][/COLOR]')


def search(item, texto):
    logger.info()

    dominio = config.get_setting('dominio', 'hdfull', default=dominios[0])

    if not config.get_setting('dominio', 'hdfull'): config.set_setting('dominio', dominio, 'hdfull')

    try:
        if item.group:
            item.url = dominio + 'buscar' + '/' + item.group + '/' + texto

        elif item.target_action:
            item.post = 'target=lists&action=search&search=%s&start=0&limit=99' % texto.replace(' ','+')
            return list_listas(item)

        else:
            data = do_downloadpage(dominio)

            magic = scrapertools.find_single_match(data, "name='__csrf_magic'\s*value=\"([^\"]+)")
            if not magic: return []

            item.search_post = '__csrf_magic=%s&menu=search&query=%s' % (magic, texto.replace(' ','+'))
            item.url = dominio + 'buscar'

        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

