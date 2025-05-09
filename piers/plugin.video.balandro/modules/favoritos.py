# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    PY3 = True

    unicode = str
    unichr = chr

    import urllib.parse as urllib
else:
    PY3 = False

    import urllib


from platformcode import config, logger, platformtools
from core import filetools, scrapertools
from core.item import Item


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


plugin_addon = 'plugin://plugin.video.balandro/'

favourites_path = filetools.translatePath('special://profile/favourites.xml')


context_favoritos = []

tit = '[COLOR %s][B]Quitar de Favoritos[/B][/COLOR]' % color_alert
context_favoritos.append({'title': tit, 'channel': 'favoritos', 'action': '_delFavourite'})

tit = '[COLOR %s][B]Renombrar Favorito[/B][/COLOR]' % color_adver
context_favoritos.append({'title': tit, 'channel': 'favoritos', 'action': '_renameFavourite'})

tit = '[COLOR %s]Ajustes categoría menú[/COLOR]' % color_exec
context_favoritos.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})


def mainlist(item):
    logger.info()
    itemlist = []

    matches = readFavourites()

    if not matches:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Favoritos[/COLOR][/B]' % color_exec)
        return

    itemlist.append(item.clone( action='', title='[B]FAVORITOS:[/B]', folder=False, text_color='plum' ))

    ses = 0

    for title, thumb, data in matches:
        if plugin_addon in data:
            ses += 1

            url = scrapertools.find_single_match(data, plugin_addon + '\?([^;]*)').replace('&quot', '')

            item = Item().fromurl(url)

            item.title = title
            item.titulo = title
            item.from_title = title

            item.thumbnail = thumb

            item.languages = ''

            if type(item.context) == str: item.context = item.context.split('|')
            elif type(item.context) != list: item.context = []

            item.context = context_favoritos

            itemlist.append(item)

    if itemlist:
        if ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR %s][B]Sin Favoritos de Balandro[/B][/COLOR]' % color_adver)

    return itemlist


def readFavourites():
    logger.info()

    favourites_list = []

    if filetools.exists(favourites_path):
        data = filetools.read(favourites_path)

        bloque = scrapertools.find_single_match(data, '<favourites>(.*?)</favourites>')

        matches = scrapertools.find_multiple_matches(bloque, '<favourite([^<]*)</favourite>')

        if len(matches) > 99: platformtools.dialog_notification(config.__addon_name, '[COLOR %s][B]Cargando Favoritos[/B][/COLOR]' % color_avis)

        for match in matches:
            name = scrapertools.find_single_match(match, 'name="([^"]*)')
            thumb = scrapertools.find_single_match(match, 'thumb="([^"]*)')
            data = scrapertools.find_single_match(match, '[^>]*>([^<]*)')

            favourites_list.append((name, thumb, data))

    return favourites_list


def saveFavourites(favourites_list):
    logger.info()

    fav = '<favourites>' + chr(10)

    for name, thumb, data in favourites_list:
        fav += '    <favourite name="%s" thumb="%s">%s</favourite>' % (name, thumb, data) + chr(10)

    fav += '</favourites>' + chr(10)

    return filetools.write(favourites_path, fav)


def addFavourite(item):
    logger.info()

    if item.from_action: item.__dict__["action"] = item.__dict__.pop("from_action")

    if item.from_channel: item.__dict__["channel"] = item.__dict__.pop("from_channel")

    favourites_list = readFavourites()

    data = 'ActivateWindow(10025,&quot;' + plugin_addon + '?' + item.tourl() + "&quot;,return)"

    titulo = item.title.replace('"', "'")

    favourites_list.append((titulo, item.thumbnail, data))

    if saveFavourites(favourites_list):
        platformtools.dialog_ok(config.__addon_name, '[COLOR yellow][B]' + titulo + '[/B][/COLOR]', 'Guardado en Favoritos')
        return True

    return False


def delFavourite(item):
    logger.info()

    if item.from_title: item.title = item.from_title

    favourites_list = readFavourites()

    for fav in favourites_list:
        if plugin_addon in str(fav):
            if fav[0] == item.title or fav[0] == item.titulo:
                if platformtools.dialog_yesno(config.__addon_name, '[COLOR red][B]¿ Confirma eliminar de Favoritos ?[/B][/COLOR]', '[COLOR yellow][B]' + item.titulo + '[/B][/COLOR]'):
                    favourites_list.remove(fav)

                    if saveFavourites(favourites_list):
                        platformtools.dialog_notification(config.__addon_name, '[COLOR %s][B]Eliminado de Favoritos[/B][/COLOR]' % color_exec)
                        return True

    return False


def renameFavourite(item):
    logger.info()

    favourites_list = readFavourites()

    for i, fav in enumerate(favourites_list):
        if plugin_addon in str(fav):
            if fav[0] == item.from_title or fav[0] == item.titulo:
                new_title = platformtools.dialog_input(item.from_title, item.title)

                if new_title:
                    favourites_list[i] = (new_title, fav[1], fav[2])

                    if saveFavourites(favourites_list):
                        platformtools.dialog_ok(config.__addon_name + ' - Favorito', '[COLOR yellow][B]' + item.titulo + '[/B][/COLOR]', 'Renombrado como: ', '[COLOR cyan][B]' + new_title + '[/B][/COLOR]')
                        return True

    return False


def _delFavourite(item):
    proceso = delFavourite(item)

    if proceso:
        from modules import submnuctext
        submnuctext._refresh_menu(item)


def _renameFavourite(item):
    proceso = renameFavourite(item)


    if proceso:
        from modules import submnuctext
        submnuctext._refresh_menu(item)
