################################################################################
#      Copyright (C) 2019 drinfernoo                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc
import xbmcgui

import glob
import os
import re
import sys

try:
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    from urllib2 import urlopen
    from urllib2 import Request

from resources.libs.common.config import CONFIG


def check_paths():
    from resources.libs.common import logging

    dialog = xbmcgui.Dialog()
    
    logging.log("[Path Check] Started")
    path = CONFIG.ADDON_PATH
    pathclean = CONFIG.ADDON_PATH.replace('\\','/')
    folderpath = pathclean.split('/')[-2]
    if not CONFIG.ADDON_ID == folderpath:
        dialog.ok(CONFIG.ADDONTITLE,
                      '[COLOR {0}]Asegúrese de que la carpeta del plugin sea la misma que la id del add-on.[/COLOR]'.format(CONFIG.COLOR2) + '\n' + '[COLOR {0}]ID Plugin:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, CONFIG.ADDON_ID) + '\n' + '[COLOR {0}]Carpeta Plugin:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, path))
        logging.log("[Path Check] ADDON_ID y la carpeta del plugin no coincide. {0} / {1} ".format(CONFIG.ADDON_ID, path))
    else:
        logging.log("[Path Check] Bueno!")


def check_build(name, ret):
    from resources.libs.common import tools

    response = tools.open_url(CONFIG.BUILDFILE)

    if not response:
        return False

    link = response.text.replace('\n', '').replace('\r', '').replace('\t', '')\
        .replace('gui=""', 'gui="http://"').replace('theme=""', 'theme="http://"')
    match = re.compile('name="%s".+?ersion="(.+?)".+?rl="(.+?)".+?inor="(.+?)".+?ui="(.+?)".+?odi="(.+?)".+?heme="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?review="(.+?)".+?dult="(.+?)".+?nfo="(.+?)".+?escription="(.+?)"' % name.replace('[', '\[').replace(']', '\]')).findall(link)
    if len(match) > 0:
        for version, url, minor, gui, kodi, theme, icon, fanart, preview, adult, info, description in match:
            if ret == 'version':
                return version
            elif ret == 'url':
                return url
            elif ret == 'minor':
                return minor
            elif ret == 'gui':
                return gui
            elif ret == 'kodi':
                return kodi
            elif ret == 'theme':
                return theme
            elif ret == 'icon':
                return icon
            elif ret == 'fanart':
                return fanart
            elif ret == 'preview':
                return preview
            elif ret == 'adult':
                return adult
            elif ret == 'description':
                return description
            elif ret == 'info':
                return info
            elif ret == 'all':
                return name, version, url, minor, gui, kodi, theme, icon, fanart, preview, adult, info, description
    else:
        return False


def check_info(name):
    from resources.libs.common import tools

    link = name.replace('\n', '').replace('\r', '').replace('\t', '')
    match = re.compile('.+?ame="(.+?)".+?xtracted="(.+?)".+?ipsize="(.+?)".+?kin="(.+?)".+?reated="(.+?)".+?rograms="(.+?)".+?ideo="(.+?)".+?usic="(.+?)".+?icture="(.+?)".+?epos="(.+?)".+?cripts="(.+?)".+?inaries="(.+?)"').findall(link)
    if len(match) > 0:
        for name, extracted, zipsize, skin, created, programs, video, music, picture, repos, scripts, binaries in match:
            return name, extracted, zipsize, skin, created, programs, video, music, picture, repos, scripts, binaries
    else:
        return False


def check_theme(name, theme, ret):
    from resources.libs.common import tools

    themeurl = check_build(name, 'theme')
    response = tools.open_url(themeurl)

    if not response:
        return False

    link = response.text.replace('\n', '').replace('\r', '').replace('\t', '')
    match = re.compile('name="{0}".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?dult=(.+?).+?escription="(.+?)"'.format(theme.replace('[', '\[').replace(']', '\]'))).findall(link)
    if len(match) > 0:
        for url, icon, fanart, adult, description in match:
            if ret == 'url':
                return url
            elif ret == 'icon':
                return icon
            elif ret == 'fanart':
                return fanart
            elif ret == 'adult':
                return adult
            elif ret == 'description':
                return description
            elif ret == 'all':
                return name, theme, url, icon, fanart, adult, description


def check_wizard(ret):
    from resources.libs.common import tools

    response = tools.open_url(CONFIG.BUILDFILE)

    if not response:
        return False

    link = response.text.replace('\n', '').replace('\r', '').replace('\t', '')
    match = re.compile('id="{0}".+?ersion="(.+?)".+?ip="(.+?)"'.format(CONFIG.ADDON_ID)).findall(link)
    if len(match) > 0:
        for version, zip in match:
            if ret == 'version':
                return version
            elif ret == 'zip':
                return zip
            elif ret == 'all':
                return CONFIG.ADDON_ID, version, zip
    else:
        return False


def check_build_update():
    from resources.libs.common import logging
    from resources.libs.common import tools
    from resources.libs.gui import window

    response = tools.open_url(CONFIG.BUILDFILE)

    if not response:
        return

    link = response.text.replace('\n', '').replace('\r', '').replace('\t', '')
    match = re.compile('name="%s".+?ersion="(.+?)".+?con="(.+?)".+?anart="(.+?)"' % CONFIG.BUILDNAME.replace('[', '\[').replace(']', '\]')).findall(link)
    if len(match) > 0:
        version = match[0][0]
        icon = match[0][1]
        fanart = match[0][2]
        CONFIG.set_setting('latestversion', version)
        if version > CONFIG.BUILDVERSION:
            if CONFIG.DISABLEUPDATE == 'false':
                logging.log("[Revisa Actualizaciones] [Versión Instalada: {0}] [Versión Actual: {1}] Abrir Ventana de Actualización".format(CONFIG.BUILDVERSION, version))
                window.show_update_window(CONFIG.BUILDNAME, CONFIG.BUILDVERSION, version, icon, fanart)
            else:
                logging.log("[Revisa Actualizaciones] [Versión Instalada: {0}] [Versión Actual: {1}] Ventana de Actualización Deshabilitada".format(CONFIG.BUILDVERSION, version))
        else:
            logging.log("[Revisa Actualizaciones] [Versión Instalada: {0}] [Versión Actual: {1}]".format(CONFIG.BUILDVERSION, version))
    else:
        logging.log("[Revisa Actualizaciones] ERROR: No se puede encontrar la versión de la Build en el archivo de texto", level=xbmc.LOGERROR)


def check_skin():
    from resources.libs.common import logging
    from resources.libs.common import tools

    dialog = xbmcgui.Dialog()
    
    logging.log("[Verificación Build] Inicio de Comprobación del Skin Inválido")
    
    gotoskin = False
    if not CONFIG.DEFAULTSKIN == '':
        if os.path.exists(os.path.join(CONFIG.ADDONS, CONFIG.DEFAULTSKIN)):
            if dialog.yesno(CONFIG.ADDONTITLE,
                                "[COLOR {0}]Parece que el skin se ha vuelto a poner [COLOR {1}]{2}[/COLOR]".format(CONFIG.COLOR2, CONFIG.COLOR1, CONFIG.SKIN[5:].title()) + '\n' + "Le gustaría volver a poner el skin en:[/COLOR]" + '\n' + '[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.DEFAULTNAME)):
                gotoskin = CONFIG.DEFAULTSKIN
                gotoname = CONFIG.DEFAULTNAME
            else:
                logging.log("El Skin no se reseteó")
                CONFIG.set_setting('defaultskinignore', 'true')
                gotoskin = False
        else:
            CONFIG.set_setting('defaultskin', '')
            CONFIG.set_setting('defaultskinname', '')
            CONFIG.DEFAULTSKIN = ''
            CONFIG.DEFAULTNAME = ''
    if CONFIG.DEFAULTSKIN == '':
        skinname = []
        skinlist = []
        for folder in glob.glob(os.path.join(CONFIG.ADDONS, 'skin.*/')):
            xml = "{0}/addon.xml".format(folder)
            if os.path.exists(xml):
                g = tools.read_from_file(xml).replace('\n', '').replace('\r', '').replace('\t', '')
                match = tools.parse_dom(g, 'addon', ret='id')
                match2 = tools.parse_dom(g, 'addon', ret='name')
                logging.log("{0}: {1}".format(folder, str(match[0])))
                if len(match) > 0:
                    skinlist.append(str(match[0]))
                    skinname.append(str(match2[0]))
                else:
                    logging.log("ID no encontrado para {0}".format(folder))
            else:
                logging.log("ID no encontrado para {0}".format(folder))
        if len(skinlist) > 0:
            if len(skinlist) > 1:
                if dialog.yesno(CONFIG.ADDONTITLE,
                                    "[COLOR {0}]Parece que el skin se ha vuelto a poner [COLOR {1}]{2}[/COLOR]".format(CONFIG.COLOR2, CONFIG.COLOR1, CONFIG.SKIN[5:].title()) + '\n' + "Le gustaría ver una lista de skins disponibles?[/COLOR]"):
                    choice = dialog.select("Seleccione el skin para cambiarlo!", skinname)
                    if choice == -1:
                        logging.log("El Skin no se reseteó")
                        CONFIG.set_setting('defaultskinignore', 'true')
                    else:
                        gotoskin = skinlist[choice]
                        gotoname = skinname[choice]
                else:
                    logging.log("El Skin no se reseteó")
                    CONFIG.set_setting('defaultskinignore', 'true')
            else:
                if dialog.yesno(CONFIG.ADDONTITLE,
                                    "[COLOR {0}]Parece que el skin se ha vuelto a poner [COLOR {1}]{2}[/COLOR]".format(CONFIG.COLOR2, CONFIG.COLOR1, CONFIG.SKIN[5:].title()) + '\n' + "Le gustaría volver a poner el skin en:[/COLOR]" + '\n' + '[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, skinname[0])):
                    gotoskin = skinlist[0]
                    gotoname = skinname[0]
                else:
                    logging.log("El Skin no se reseteó")
                    CONFIG.set_setting('defaultskinignore', 'true')
        else:
            logging.log("No se encontraron skins en la carpeta de addons.")
            CONFIG.set_setting('defaultskinignore', 'true')
            gotoskin = False
    if gotoskin:
        from resources.libs import skin

        if skin.switch_to_skin(gotoskin):
            skin.look_and_feel_data('restore')
    logging.log("[Verificación Build] Fin de Comprobación del Skin Invalido")


def check_sources():
    from resources.libs.common import logging
    from resources.libs.common import tools

    dialog = xbmcgui.Dialog()
    progress_dialog = xbmcgui.DialogProgress()
    
    if not os.path.exists(CONFIG.SOURCES):
        logging.log_notify(CONFIG.ADDONTITLE,
                           "[COLOR {0}]No se ha Encontrado Ningún Archivo Fuentes.xml!![/COLOR]".format(CONFIG.COLOR2))
        return False
    x = 0
    bad = []
    remove = []
    a = tools.read_from_file(CONFIG.SOURCES)
    temp = a.replace('\r', '').replace('\n', '').replace('\t', '')
    match = re.compile('<files>.+?</files>').findall(temp)

    if len(match) > 0:
        match2 = re.compile('<source>.+?<name>(.+?)</name>.+?<path pathversion="1">(.+?)</path>.+?<allowsharing>(.+?)</allowsharing>.+?</source>').findall(match[0])
        progress_dialog.create(CONFIG.ADDONTITLE, "[COLOR {0}]Escaneo de Fuentes en Busca de enlaces Rotos[/COLOR]".format(CONFIG.COLOR2))
        for name, path, sharing in match2:
            x += 1
            perc = int(tools.percentage(x, len(match2)))
            progress_dialog.update(perc,
                          '' + '\n' + "[COLOR {0}]Comprobando [COLOR {1}]{2}[/COLOR]:[/COLOR]".format(CONFIG.COLOR2, CONFIG.COLOR1, name) + '\n' + "[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, path))
                          
            working = tools.open_url(path, check=True)
            if not working:
                bad.append([name, path, sharing, working])

        logging.log("Fuentes Malas: {0}".format(len(bad)))
        if len(bad) > 0:
            choice = dialog.yesno(CONFIG.ADDONTITLE, "[COLOR {0}]{1}[/COLOR][COLOR {2}] Fuente(s) se han encontrado Rotas".format(CONFIG.COLOR1, len(bad), CONFIG.COLOR2) + '\n' + "Le gustaría Eliminar todos o elegir uno por uno?[/COLOR]",
                                      yeslabel="[B][COLOR dodgerblue]Eliminar Todo[/COLOR][/B]",
                                      nolabel="[B][COLOR red]Elija Eliminar[/COLOR][/B]")
            if choice == 1:
                remove = bad
            else:
                for name, path, sharing, working in bad:
                    logging.log("{0} fuentes: {1}, {2}".format(name, path, working))
                    if dialog.yesno(CONFIG.ADDONTITLE,
                                        "[COLOR {0}]{1}[/COLOR][COLOR {2}] se informó que no funciona".format(CONFIG.COLOR1, name, CONFIG.COLOR2) + '\n' + "[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, path) + '\n' + "[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, working),
                                        yeslabel="[B][COLOR dodgerblue]Eliminar Fuente[/COLOR][/B]",
                                        nolabel="[B][COLOR red]Mantener Fuente[/COLOR][/B]"):
                        remove.append([name, path, sharing, working])
                        logging.log("Eliminando Fuente {0}".format(name))
                    else:
                        logging.log("La Fuente {0} no se eliminó".format(name))
            if len(remove) > 0:
                for name, path, sharing, working in remove:
                    a = a.replace('\n<source>\n<name>{0}</name>\n<path pathversion="1">{1}</path>\n<allowsharing>{2}</allowsharing>\n</source>'.format(name, path, sharing), '')
                    logging.log("Eliminando Fuente {0}".format(name))

                tools.write_to_file(CONFIG.SOURCES, str(a))
                alive = len(match) - len(bad)
                kept = len(bad) - len(remove)
                removed = len(remove)
                dialog.ok(CONFIG.ADDONTITLE,
                              "[COLOR {0}]La Comprobación de las fuentes en busca de rutas rotas ha finalizado.".format(CONFIG.COLOR2) + '\n' + "Funciona: [COLOR {0}]{1}[/COLOR] | Conservo: [COLOR {2}]{3}[/COLOR] | Eliminado: [COLOR {4}]{5}[/COLOR][/COLOR]".format(CONFIG.COLOR2, CONFIG.COLOR1, alive, CONFIG.COLOR1, kept, CONFIG.COLOR1, removed))
            else:
                logging.log("No hay Fuentes Malas que eliminar.")
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               "[COLOR {0}]Todas las Fuentes están Funcionando[/COLOR]".format(CONFIG.COLOR2))
    else:
        logging.log("No se Encontraron Fuentes")


def check_repos():
    from resources.libs.common import logging
    from resources.libs.common import tools

    progress_dialog = xbmcgui.DialogProgress()
    
    progress_dialog.create(CONFIG.ADDONTITLE, '[COLOR {0}]Comprobación de Repositorios...[/COLOR]'.format(CONFIG.COLOR2))
    badrepos = []
    xbmc.executebuiltin('UpdateAddonRepos')
    repolist = glob.glob(os.path.join(CONFIG.ADDONS, 'repo*'))
    if len(repolist) == 0:
        progress_dialog.close()
        logging.log_notify(CONFIG.ADDONTITLE,
                           "[COLOR {0}]No se Encontraron Repositorios![/COLOR]".format(CONFIG.COLOR2))
        return
    sleeptime = len(repolist)
    start = 0
    while start < sleeptime:
        start += 1
        if progress_dialog.iscanceled():
            break
        perc = int(tools.percentage(start, sleeptime))
        progress_dialog.update(perc,
                      '\n' + '[COLOR {0}]Comprobando: [/COLOR][COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, repolist[start-1].replace(CONFIG.ADDONS, '')[1:]))
        xbmc.sleep(1000)
    if progress_dialog.iscanceled():
        progress_dialog.close()
        logging.log_notify(CONFIG.ADDONTITLE,
                           "[COLOR {0}]Habilitación de Addons Cancelado[/COLOR]".format(CONFIG.COLOR2))
        sys.exit()
    progress_dialog.close()
    logfile = logging.grab_log()
    fails = re.compile('CRepositoryUpdateJob(.+?)failed').findall(logfile)
    for item in fails:
        logging.log("Repositorio Incorrecto: {0} ".format(item))
        brokenrepo = item.replace('[', '').replace(']', '').replace(' ', '').replace('/', '').replace('\\', '')
        if brokenrepo not in badrepos:
            badrepos.append(brokenrepo)
    if len(badrepos) > 0:
        msg = "[COLOR {0}]A continuación se muestra una lista de Repositorios que no se resolvieron.  Esto no significa que estén Depreciados, a veces los hosts caen por un período corto de tiempo.  Realice varios escaneos de su lista de repositorios antes de eliminar un repositorio, solo para asegurarse de que esté roto.[/COLOR][CR][CR][COLOR {1}]".format(CONFIG.COLOR2, CONFIG.COLOR1)
        msg += '[CR]'.join(badrepos)
        msg += '[/COLOR]'
        window.show_text_box("Visualización de Repositorios Rotos", msg)
    else:
        logging.log_notify(CONFIG.ADDONTITLE,
                           "[COLOR {0}]Todos los Repositorios Funcionan![/COLOR]".format(CONFIG.COLOR2))


def build_count():
    from resources.libs import test
    from resources.libs.common import tools

    response = tools.open_url(CONFIG.BUILDFILE)

    total = 0
    count20 = 0
    hidden = 0
    adultcount = 0

    if not response:
        return total, count20, adultcount, hidden

    link = response.text.replace('\n', '').replace('\r', '').replace('\t', '')
    match = re.compile('name="(.+?)".+?odi="(.+?)".+?dult="(.+?)"').findall(link)

    if len(match) > 0:
        for name, kodi, adult in match:
            if not CONFIG.SHOWADULT == 'true' and adult.lower() == 'yes':
                hidden += 1
                adultcount += 1
                continue
            if not CONFIG.DEVELOPER == 'true' and test.str_test(name):
                hidden += 1
                continue
            kodi = int(float(kodi))
            total += 1
            if kodi == 20:
                count20 += 1
    return total, count20, adultcount, hidden


