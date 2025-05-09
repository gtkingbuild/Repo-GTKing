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
import xbmcaddon
import xbmcgui
import xbmcvfs

import glob
import os
import re

try:  # Python 3
    from urllib.parse import quote_plus
    from urllib.request import urlretrieve
except ImportError:  # Python 2
    from urllib import quote_plus
    from urllib import urlretrieve

from resources.libs.common import directory
from resources.libs.common.config import CONFIG


###########################
#      Menu Items         #
###########################

def check_for_fm():
    if not xbmc.getCondVisibility('System.HasAddon(script.kodi.android.update)'):
        from resources.libs.gui import addon_menu
        addon_menu.install_from_kodi('script.kodi.android.update')
    
    try:
        updater = xbmcaddon.Addon('script.kodi.android.update')
    except RuntimeError as e:
        return False
        
    fm = int(updater.getSetting('File_Manager'))
    apps = xbmcvfs.listdir('androidapp://sources/apps/')[1]
    
    if fm == 0 and 'com.android.documentsui' not in apps:
        dialog = xbmcgui.Dialog()
        choose = dialog.yesno(CONFIG.ADDONTITLE, 'Parece que su dispositivo no tiene un administrador de archivos predeterminado. ¿Le gustaría establecer uno ahora?')
        if not choose:
            dialog.ok(CONFIG.ADDONTITLE, 'Si se descarga un APK, pero no se abre para la instalación, intente cambiar su administrador de archivo\'s en {} "Configuración de instalación".'.format(CONFIG.ADDONTITLE))
        else:
            from resources.libs import install
            install.choose_file_manager()
            
    return True


def apk_menu(url=None):
    from resources.libs.common import logging
    from resources.libs.common import tools

    if check_for_fm():
        directory.add_dir('[B]APK\'s OFICIAL DE KODI[/B]', {'mode': 'kodiapk'}, icon=CONFIG.ICONAPK, themeit=CONFIG.THEME1)
        directory.add_separator('[B]DESCARGAR APLICACIONES[/B]')

    response = tools.open_url(CONFIG.APKFILE)
    url_response = tools.open_url(url)

    if response:
        TEMPAPKFILE = tools.clean_text(url_response.text if url else response.text)

        if TEMPAPKFILE:
            match = re.compile('name="(.+?)".+?ection="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?dult="(.+?)".+?escription="(.+?)"').findall(TEMPAPKFILE)
            if len(match) > 0:
                x = 0
                for name, section, url, icon, fanart, adult, description in match:
                    if not CONFIG.SHOWADULT == 'true' and adult.lower() == 'yes':
                        continue
                    if section.lower() == 'yes':
                        x += 1
                        directory.add_dir("[B]{0}[/B]".format(name), {'mode': 'apk', 'name': name, 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
                    else:
                        x += 1
                        directory.add_file(name, {'mode': 'apkinstall', 'name': name, 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME2)
                    if x == 0:
                        directory.add_file("¡Todavía no se agregaron addons a este menú!", themeit=CONFIG.THEME2)
            else:
                logging.log("[APK Menu] ERROR: [COLOR gold]Formato inválido..[/COLOR]", level=xbmc.LOGERROR)
        else:
            logging.log("[APK Menu] ERROR: [COLOR gold]La URL de la lista de apk no funciona.[/COLOR]", level=xbmc.LOGERROR)
            directory.add_file('La URL del archivo txt no es válida', themeit=CONFIG.THEME3)
            directory.add_file('{0}'.format(CONFIG.APKFILE), themeit=CONFIG.THEME3)
    else:
        logging.log("[APK Menu] No se agregó ninguna lista de APK.")


def youtube_menu(url=None):
    from resources.libs.common import logging
    from resources.libs.common import tools

    response = tools.open_url(CONFIG.YOUTUBEFILE)
    url_response = tools.open_url(url)

    if response:
        TEMPYOUTUBEFILE = url_response.text if url else response.text

        if TEMPYOUTUBEFILE:
            link = TEMPYOUTUBEFILE.replace('\n', '').replace('\r', '').replace('\t', '')
            match = re.compile('name="(.+?)".+?ection="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(link)
            if len(match) > 0:
                for name, section, url, icon, fanart, description in match:
                    if section.lower() == "sí":
                        directory.add_dir("[B]{0}[/B]".format(name), {'mode': 'youtube', 'name': name, 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
                    else:
                        directory.add_file(name, {'mode': 'viewVideo', 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME2)
            else:
                logging.log("[YouTube Menu] ERROR: [COLOR gold]Formato inválido.[/COLOR]")
        else:
            logging.log("[YouTube Menu] ERROR: [COLOR gold]La URL de la lista de YouTube no funciona.[/COLOR]")
            directory.add_file('La URL del archivo txt no es válida', themeit=CONFIG.THEME3)
            directory.add_file('{0}'.format(CONFIG.YOUTUBEFILE), themeit=CONFIG.THEME3)
    else:
        logging.log("[YouTube Menu] No se agregó ninguna lista de YouTube.")

#########################################NET TOOLS#############################################


def net_tools():
    directory.add_dir('[B]Prueba de Velocidad[/B]', {'mode': 'speedtest'}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME1)
    if CONFIG.HIDESPACERS == 'No':
        directory.add_separator()
    directory.add_dir('[B]Ver Dirección IP y Dirección MAC[/B]', {'mode': 'viewIP'}, icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME1)


def view_ip():
    from resources.libs import speedtest

    mac, inter_ip, ip, city, state, country, isp = speedtest.net_info()
    directory.add_file('[COLOR {0}]MAC:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, mac), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]IP Interna:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, inter_ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]IP Externa:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Ciudad:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, city), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Estado:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, state), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]País:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, country), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]ISP:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, isp), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)


def speed_test():
    from datetime import date

    directory.add_file('Prueba de Velocidad de Ejecución', {'mode': 'speedtest'}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)
    if os.path.exists(CONFIG.SPEEDTEST):
        speedimg = glob.glob(os.path.join(CONFIG.SPEEDTEST, '*.png'))
        speedimg.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        if len(speedimg) > 0:
            directory.add_file('Borrar Resultados', {'mode': 'clearspeedtest'}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)
            directory.add_separator('Ejecuciones Anteriores', icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)
            for item in speedimg:
                created = date.fromtimestamp(os.path.getmtime(item)).strftime('%d/%m/%Y %H:%M:%S')
                img = item.replace(os.path.join(CONFIG.SPEEDTEST, ''), '')
                directory.add_file('[B]{0}[/B]: [I]Corrió {1}[/I]'.format(img, created), {'mode': 'viewspeedtest', 'name': img}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)


def clear_speed_test():
    from resources.libs.common import tools

    speedimg = glob.glob(os.path.join(CONFIG.SPEEDTEST, '*.png'))
    for file in speedimg:
        tools.remove_file(file)


def view_speed_test(img=None):
    from resources.libs.gui import window

    img = os.path.join(CONFIG.SPEEDTEST, img)
    window.show_speed_test(img)


def run_speed_test():
    from resources.libs.common import logging
    from resources.libs import speedtest

    try:
        found = speedtest.speedtest()
        if not os.path.exists(CONFIG.SPEEDTEST):
            os.makedirs(CONFIG.SPEEDTEST)
        urlsplits = found[0].split('/')
        dest = os.path.join(CONFIG.SPEEDTEST, urlsplits[-1])
        urlretrieve(found[0], dest)
        view_speed_test(urlsplits[-1])
    except Exception as e:
        logging.log("[Prueba de Velocidad] [COLOR gold]Error al Ejecutar la Prueba de Velocidad {0}[/COLOR]".format(e), level=xbmc.LOGDEBUG)
        pass


def system_info():
    from resources.libs.common import logging
    from resources.libs.common import tools
    from resources.libs import speedtest

    infoLabel = ['System.FriendlyName', 'System.BuildVersion', 'System.CpuUsage', 'System.ScreenMode',
                 'Network.IPAddress', 'Network.MacAddress', 'System.Uptime', 'System.TotalUptime', 'System.FreeSpace',
                 'System.UsedSpace', 'System.TotalSpace', 'System.Memory(free)', 'System.Memory(used)',
                 'System.Memory(total)']
    data = []
    x = 0
    for info in infoLabel:
        temp = tools.get_info_label(info)
        y = 0
        while temp == "Ocupado" and y < 10:
            temp = tools.get_info_label(info)
            y += 1
            logging.log("{0} sleep {1}".format(info, str(y)))
            xbmc.sleep(200)
        data.append(temp)
        x += 1
    storage_free = data[8] if '' in data[8] else tools.convert_size(int(float(data[8][:-8])) * 1024 * 1024)
    storage_used = data[9] if '' in data[9] else tools.convert_size(int(float(data[9][:-8])) * 1024 * 1024)
    storage_total = data[10] if '' in data[10] else tools.convert_size(int(float(data[10][:-8])) * 1024 * 1024)
    ram_free = tools.convert_size(int(float(data[11][:-2])) * 1024 * 1024)
    ram_used = tools.convert_size(int(float(data[12][:-2])) * 1024 * 1024)
    ram_total = tools.convert_size(int(float(data[13][:-2])) * 1024 * 1024)

    picture = []
    music = []
    video = []
    programs = []
    repos = []
    scripts = []
    skins = []

    fold = glob.glob(os.path.join(CONFIG.ADDONS, '*/'))
    for folder in sorted(fold, key = lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername == 'packages': continue
        xml = os.path.join(folder, 'addon.xml')
        if os.path.exists(xml):
            prov = re.compile("<provides>(.+?)</provides>").findall(tools.read_from_file(xml))
            if len(prov) == 0:
                if foldername.startswith('skin'):
                    skins.append(foldername)
                elif foldername.startswith('repo'):
                    repos.append(foldername)
                else:
                    scripts.append(foldername)
            elif not (prov[0]).find('executable') == -1:
                programs.append(foldername)
            elif not (prov[0]).find('video') == -1:
                video.append(foldername)
            elif not (prov[0]).find('audio') == -1:
                music.append(foldername)
            elif not (prov[0]).find('image') == -1:
                picture.append(foldername)

    directory.add_file('[B]Información del Centro de Medios:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Nombre:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[0]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]Versión:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[1]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]Plataforma:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, tools.platform().title()), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]Uso de CPU:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[2]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]Modo de Pantalla:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[3]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)

    directory.add_file('[B]Tiempo de Actividad:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Tiempo de Actividad Actual:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[6]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Tiempo de Actividad Total:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[7]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    directory.add_file('[B]Almacenamiento Local:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Memoria Usada:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_used), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Memoria Libre:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_free), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Memoria Total:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_total), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    directory.add_file('[B]Uso de Ram:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Memoria Usada:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_free), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Memoria Libre:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_used), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Memoria Total:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_total), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    mac, inter_ip, ip, city, state, country, isp = speedtest.net_info()
    directory.add_file('[B]Network:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Mac:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, mac), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]IP Interna:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, inter_ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]IP Externa:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Ciudad:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, city), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Estado:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, state), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]País:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, country), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]ISP:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, isp), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    totalcount = len(picture) + len(music) + len(video) + len(programs) + len(scripts) + len(skins) + len(repos)
    directory.add_file('[B]Addons([COLOR {0}]{1}[/COLOR]):[/B]'.format(CONFIG.COLOR1, totalcount), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Addons de Video:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(video))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Addons de Programa:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(programs))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Addons de Música:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(music))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Addons de Imagen:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(picture))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Repositorios:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(repos))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Skins:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(skins))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Scripts/Modules:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(scripts))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)


def save_menu():
    on = '[COLOR cyan]ON[/COLOR]'
    off = '[COLOR red]OFF[/COLOR]'

    trakt = 'true' if CONFIG.KEEPTRAKT == 'true' else 'false'
    debrid = 'true' if CONFIG.KEEPDEBRID == 'true' else 'false'
    login = 'true' if CONFIG.KEEPLOGIN == 'true' else 'false'
    sources = 'true' if CONFIG.KEEPSOURCES == 'true' else 'false'
    advanced = 'true' if CONFIG.KEEPADVANCED == 'true' else 'false'
    profiles = 'true' if CONFIG.KEEPPROFILES == 'true' else 'false'
    playercore = 'true' if CONFIG.KEEPPLAYERCORE == 'true' else 'false'
    guisettings = 'true' if CONFIG.KEEPGUISETTINGS == 'true' else 'false'
    favourites = 'true' if CONFIG.KEEPFAVS == 'true' else 'false'
    repos = 'true' if CONFIG.KEEPREPOS == 'true' else 'false'
    super = 'true' if CONFIG.KEEPSUPER == 'true' else 'false'
    whitelist = 'true' if CONFIG.KEEPWHITELIST == 'true' else 'false'

    directory.add_dir('Manterner Datos Trakt', {'mode': 'trakt'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME1)
    directory.add_dir('Mantener Debrid', {'mode': 'realdebrid'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME1)
    directory.add_dir('Mantener Información del Login', {'mode': 'login'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME1)
    directory.add_file('Importar Datos Guardados', {'mode': 'managedata', 'name': 'import'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Exportar Datos Guardados', {'mode': 'managedata', 'name': 'export'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('[B][COLOR white]-[/COLOR] Haga Clic para Cambiar la Configuración [COLOR white]-[/COLOR][/B]', themeit=CONFIG.THEME3)
    directory.add_file('Guardar Trakt: {0}'.format(trakt.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keeptrakt'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME1)
    directory.add_file('Guardar Debrid: {0}'.format(debrid.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepdebrid'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME1)
    directory.add_file('Guardar Información de: {0}'.format(login.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keeplogin'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME1)
    directory.add_file('Mantener \'Fuentes.xml\': {0}'.format(sources.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepsources'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener \'Perfiles.xml\': {0}'.format(profiles.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepprofiles'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener \'playercorefactory.xml\': {0}'.format(playercore.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepplayercore'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener \'guisettings.xml\': {0}'.format(guisettings.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepguiseettings'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener \'Advancedsettings.xml\': {0}'.format(advanced.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepadvanced'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener \'Favoritos.xml\': {0}'.format(favourites.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepfavourites'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener Super Favoritos: {0}'.format(super.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepsuper'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener Repo\'s Instalados: {0}'.format(repos.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keeprepos'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('Mantener Mi \'Lista Blanca\': {0}'.format(whitelist.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepwhitelist'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    if whitelist == 'true':
        directory.add_file('Editar Mi Lista Blanca', {'mode': 'whitelist', 'name': 'edit'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('Ver Mi Lista Blanca', {'mode': 'whitelist', 'name': 'view'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('Borrar Mi Lista Blanca', {'mode': 'whitelist', 'name': 'clear'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('Importar Mi Lista Blanca', {'mode': 'whitelist', 'name': 'import'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('Exportar Mi Lista Blanca', {'mode': 'whitelist', 'name': 'export'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)


def trakt_menu():
    from resources.libs import traktit

    keep_trakt = '[COLOR azure]ON[/COLOR]' if CONFIG.KEEPTRAKT == 'true' else '[COLOR red]OFF[/COLOR]'
    last = str(CONFIG.TRAKTSAVE) if not CONFIG.TRAKTSAVE == '' else 'Trakt hasn\'t been saved yet.'
    directory.add_file('[I][COLOR azure]Registre una cuenta GRATIS en[/COLOR] [COLOR turquoise] https://www.trakt.tv/[/COLOR][/I]', icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('[B]Guardar Datos de Trakt:[/B] [COLOR azure]{0}[/COLOR]'.format(keep_trakt), {'mode': 'togglesetting', 'name': 'keeptrakt'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    if CONFIG.KEEPTRAKT == 'true':
        directory.add_file('[B]Ultimo Guardado:[/B] [COLOR azure]{0}[/COLOR]'.format(str(last)), icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_separator(icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)

    for trakt in traktit.ORDER:
        if xbmc.getCondVisibility('System.HasAddon({0})'.format(traktit.TRAKTID[trakt]['plugin'])):
            name = traktit.TRAKTID[trakt]['name']
            path = traktit.TRAKTID[trakt]['path']
            saved = traktit.TRAKTID[trakt]['saved']
            file = traktit.TRAKTID[trakt]['file']
            user = CONFIG.get_setting(saved)
            auser = traktit.trakt_user(trakt)
            icon = traktit.TRAKTID[trakt]['icon'] if os.path.exists(path) else CONFIG.ICONTRAKT
            fanart = traktit.TRAKTID[trakt]['fanart'] if os.path.exists(path) else CONFIG.ADDON_FANART
            menu = create_addon_data_menu('Trakt', trakt)
            menu2 = create_save_data_menu('Trakt', trakt)
            menu.append((CONFIG.THEME2.format('{0} [COLOR azure]Ajustes[/COLOR]'.format(name)), 'RunPlugin(plugin://{0}/?mode=opensettings&name={1}&url=trakt)'.format(CONFIG.ADDON_ID, trakt)))

            directory.add_file('[B][+]->[/B] [B]{0}[/B]'.format(name), icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
            if not os.path.exists(path):
                directory.add_file('[B][COLOR red]Datos adicionales:[/COLOR][/B] [COLOR azure]No Instalado[/COLOR]', icon=icon, fanart=fanart, menu=menu)
            elif not auser:
                directory.add_file('[B][COLOR red]Datos adicionales:[/COLOR][/B] [COLOR azure]No Registrado[/COLOR]', {'mode': 'authtrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu)
            else:
                directory.add_file('[B][COLOR cyan]Datos adicionales:[/COLOR][/B] [COLOR azure]{0}[/COLOR]'.format(auser), {'mode': 'authtrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu)
            if user == "":
                if os.path.exists(file):
                    directory.add_file('[B][COLOR red]Datos Guardados:[/COLOR][/B] [COLOR azure]Guardar archivo encontrado(Importar datos)[/COLOR]', {'mode': 'importtrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu2)
                else:
                    directory.add_file('[B][COLOR red]Datos Guardados:[/COLOR][/B] [COLOR azure]No Guardado[/COLOR]', {'mode': 'savetrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu2)
            else:
                directory.add_file('[B][COLOR cyan]Datos Guardados:[/COLOR][/B] [COLOR azure]{0}[/COLOR]'.format(user), icon=icon, fanart=fanart, menu=menu2)

    directory.add_separator()
    directory.add_file('[COLOR azure]Guardar Todos los Datos de Trakt[/COLOR]', {'mode': 'savetrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Recuperar Todos los Datos Guardados de Trakt[/COLOR]', {'mode': 'restoretrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Importar Datos de Trakt[/COLOR]', {'mode': 'importtrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Borrar Todos los Datos de Trakt Adicionales[/COLOR]', {'mode': 'addontrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Borrar Todos los Datos de Trakt Guardados[/COLOR]', {'mode': 'cleartrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)


def debrid_menu():
    from resources.libs import debridit

    keep_debrid = '[COLOR azure]ON[/COLOR]' if CONFIG.KEEPDEBRID == 'true' else '[COLOR red]OFF[/COLOR]'
    last = str(CONFIG.DEBRIDSAVE) if not CONFIG.DEBRIDSAVE == '' else '[COLOR azure]Las autorizaciones de Debrid aún no se han guardado.[/COLOR]'
    directory.add_file('[I][COLOR turquoise]https://www.real-debrid.com/[/COLOR] [COLOR azure]es un servicio [COLOR azure]PAGADO.[/COLOR][/I]', icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('[I][COLOR turquoise]https://www.premiumize.me/[/COLOR] [COLOR azure]es un servicio PAGADO.[/COLOR][/I]', icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('[B]Guardar Datos Debrid:[/B] [COLOR azure]{0}[/COLOR]'.format(keep_debrid), {'mode': 'togglesetting', 'name': 'keepdebrid'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    if CONFIG.KEEPDEBRID == 'true':
        directory.add_file('[B]Ultimo Guardado:[/B][COLOR azure] {0}[/COLOR]'.format(str(last)), icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_separator(icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)

    for debrid in debridit.ORDER:
        if xbmc.getCondVisibility('System.HasAddon({0})'.format(debridit.DEBRIDID[debrid]['plugin'])):
            name = debridit.DEBRIDID[debrid]['name']
            path = debridit.DEBRIDID[debrid]['path']
            saved = debridit.DEBRIDID[debrid]['saved']
            file = debridit.DEBRIDID[debrid]['file']
            user = CONFIG.get_setting(saved)
            auser = debridit.debrid_user(debrid)
            icon = debridit.DEBRIDID[debrid]['icon'] if os.path.exists(path) else CONFIG.ICONDEBRID
            fanart = debridit.DEBRIDID[debrid]['fanart'] if os.path.exists(path) else CONFIG.ADDON_FANART
            menu = create_addon_data_menu('Debrid', debrid)
            menu2 = create_save_data_menu('Debrid', debrid)
            menu.append((CONFIG.THEME2.format('{0} [COLOR azure]Ajustes[/COLOR]'.format(name)), 'RunPlugin(plugin://{0}/?mode=opensettings&name={1}&url=debrid)'.format(CONFIG.ADDON_ID, debrid)))

            directory.add_file('[B][+]->[/B] [B]{0}[/B]'.format(name), icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
            if not os.path.exists(path):
                directory.add_file('[B][COLOR red]Datos adicionales:[/COLOR][/B] [COLOR azure]No Instalado[/COLOR]', icon=icon, fanart=fanart, menu=menu)
            elif not auser:
                directory.add_file('[B][COLOR red]Datos adicionales:[/COLOR][/B] [COLOR azure]No Registrado[/COLOR]', {'mode': 'authdebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu)
            else:
                directory.add_file('[B][COLOR cyan]Datos adicionales:[/COLOR][/B] [COLOR azure]{0}[/COLOR]'.format(auser), {'mode': 'authdebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu)
            if user == "":
                if os.path.exists(file):
                    directory.add_file('[B][COLOR red]Datos Guardados:[/COLOR][/B] [COLOR azure]Guardar archivo encontrado(Importar datos)[/COLOR]', {'mode': 'importdebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu2)
                else:
                    directory.add_file('[B][COLOR red]Datos Guardados:[/COLOR][/B] [COLOR azure]No Guardado[/COLOR]', {'mode': 'savedebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu2)
            else:
                directory.add_file('[B][COLOR cyan]Datos Guardados:[/COLOR][/B] [COLOR azure]{0}[/COLOR]'.format(user), icon=icon, fanart=fanart, menu=menu2)

    directory.add_separator(themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Guardar todos los datos de Debrid[/COLOR]', {'mode': 'savedebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Recuperar Todos los Datos de Debrid Guardados[/COLOR]', {'mode': 'restoredebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Importar Datos de Debrid[/COLOR]', {'mode': 'importdebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Borrar Todos los Datos de Debrid Adicionales[/COLOR]', {'mode': 'addondebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Borrar Todos los Datos de Debrid Guardados[/COLOR]', {'mode': 'cleardebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)


def login_menu():
    from resources.libs import loginit

    keep_login = '[COLOR azure]ON[/COLOR]' if CONFIG.KEEPLOGIN == 'true' else '[COLOR red]OFF[/COLOR]'
    last = str(CONFIG.LOGINSAVE) if not CONFIG.LOGINSAVE == '' else '[COLOR azure]Los Datos de Login aún no se han Guardado.[/COLOR]'
    directory.add_file('[I][COLOR turquoise]Varios de estos addons son servicios[/COLOR] [COLOR azure]PAGADOS.[/COLOR][/I]', icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('[B]Guardar Claves API:[/B] [COLOR azure]{0}[/COLOR]'.format(keep_login), {'mode': 'togglesetting', 'name': 'keeplogin'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    if CONFIG.KEEPLOGIN == 'true':
        directory.add_file('[B]Ultimo Guardado:[/B] [COLOR azure]{0}[/COLOR]'.format(str(last)), icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_separator(icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)

    for login in loginit.ORDER:
        if xbmc.getCondVisibility('System.HasAddon({0})'.format(loginit.LOGINID[login]['plugin'])):
            name = loginit.LOGINID[login]['name']
            path = loginit.LOGINID[login]['path']
            saved = loginit.LOGINID[login]['saved']
            file = loginit.LOGINID[login]['file']
            user = CONFIG.get_setting(saved)
            auser = loginit.login_user(login)
            icon = loginit.LOGINID[login]['icon'] if os.path.exists(path) else CONFIG.ICONLOGIN
            fanart = loginit.LOGINID[login]['fanart'] if os.path.exists(path) else CONFIG.ADDON_FANART
            menu = create_addon_data_menu('Login', login)
            menu2 = create_save_data_menu('Login', login)
            menu.append((CONFIG.THEME2.format('{0} [COLOR azure]Ajustes[/COLOR]'.format(name)), 'RunPlugin(plugin://{0}/?mode=opensettings&name={1}&url=login)'.format(CONFIG.ADDON_ID, login)))

            directory.add_file('[B][+]->[/B] [B]{0}[/B]'.format(name), icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
            if not os.path.exists(path):
                directory.add_file('[B][COLOR red]Datos adicionales:[/COLOR][/B] [COLOR azure]No Instalado[/COLOR]', icon=icon, fanart=fanart, menu=menu)
            elif not auser:
                directory.add_file('[B][COLOR red]Datos adicionales:[/COLOR][/B] [COLOR azure]No Registrado[/COLOR]', {'mode': 'authlogin', 'name': login}, icon=icon, fanart=fanart, menu=menu)
            else:
                directory.add_file('[B][COLOR cyan]Datos adicionales:[/COLOR][/B] [COLOR azure]{0}[/COLOR]'.format(auser), {'mode': 'authlogin', 'name': login}, icon=icon, fanart=fanart, menu=menu)
            if user == "":
                if os.path.exists(file):
                    directory.add_file('[B][COLOR red]Datos Guardados:[/COLOR][/B] [COLOR azure]Guardar archivo encontrado(Importar datos)[/COLOR]', {'mode': 'importlogin', 'name': login}, icon=icon, fanart=fanart, menu=menu2)
                else:
                    directory.add_file('[B][COLOR red]Datos Guardados:[/COLOR][/B] [COLOR azure]No Guardado[/COLOR]', {'mode': 'savelogin', 'name': login}, icon=icon, fanart=fanart, menu=menu2)
            else:
                directory.add_file('[B][COLOR cyan]Datos Guardados:[/COLOR][/B] [COLOR azure]{0}[/COLOR]'.format(user), icon=icon, fanart=fanart, menu=menu2)

    directory.add_separator(themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Guardar Toda la Info del Login[/COLOR]', {'mode': 'savelogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Recuperar Toda la Info del Login Guardada[/COLOR]', {'mode': 'restorelogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Importar la Info del Login[/COLOR]', {'mode': 'importlogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Borrar Toda la Info del Login del Addon[/COLOR]', {'mode': 'addonlogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR azure]Borrar Toda la Info del Login Guardada[/COLOR]', {'mode': 'clearlogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)


def enable_addons(all=False):
    from resources.libs.common import tools
    
    from xml.etree import ElementTree

    fold = glob.glob(os.path.join(CONFIG.ADDONS, '*/'))
    addonnames = []
    addonids = []
    for folder in sorted(fold, key=lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername in CONFIG.EXCLUDES:
            continue
        elif foldername in CONFIG.DEFAULTPLUGINS:
            continue
        elif foldername == 'packages':
            continue
        xml = os.path.join(folder, 'addon.xml')
        if os.path.exists(xml):
            root = ElementTree.parse(xml).getroot()
            addonid = root.get('id')
            addonname = root.get('name')
            addonids.append(addonid)
            addonnames.append(addonname)
    if not all:
        if len(addonids) == 0:
            directory.add_file("No se encontrado Addons para habilitar o deshabilitar..", icon=CONFIG.ICONMAINT)
        else:
            directory.add_file("[I][B][COLOR red]!!AVISO: Desactivar Algunos Addons Puede Causar Problemas!![/COLOR][/B][/I]", icon=CONFIG.ICONMAINT)
            directory.add_dir('Habilitar Todos los Addons', {'mode': 'enableall'}, icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
            for i in range(0, len(addonids)):
                folder = os.path.join(CONFIG.ADDONS, addonids[i])
                icon = os.path.join(folder, 'icon.png') if os.path.exists(os.path.join(folder, 'icon.png')) else CONFIG.ADDON_ICON
                fanart = os.path.join(folder, 'fanart.jpg') if os.path.exists(os.path.join(folder, 'fanart.jpg')) else CONFIG.ADDON_FANART
                if tools.get_addon_info(addonids[i], 'name'):
                    state = "[COLOR cyan][Habilitado][/COLOR]"
                    goto = "false"
                else:
                    state = "[COLOR red][Deshabilitado][/COLOR]"
                    goto = "true"

                directory.add_file("{0} {1}".format(state, addonnames[i]), {'mode': 'toggleaddon', 'name': addonids[i], 'url': goto}, icon=icon, fanart=fanart)
    else:
        from resources.libs import db
        for addonid in addonids:
            db.toggle_addon(addonid, 'true')
        xbmc.executebuiltin('Container.Refresh()')


def remove_addon_data_menu():
    if os.path.exists(CONFIG.ADDON_DATA):
        directory.add_file('[COLOR red][B][ELIMINAR][/B][/COLOR] Todos los Addon_Data', {'mode': 'removedata', 'name': 'all'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][ELIMINAR][/B][/COLOR] Todos los Addon_Data para Addons Desinstalados', {'mode': 'removedata', 'name': 'uninstalled'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][ELIMINAR][/B][/COLOR] Todas las Carpetas Vacías en Addon_Data', {'mode': 'removedata', 'name': 'empty'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][ELIMINAR][/B][/COLOR] {0} Addon_Data'.format(CONFIG.ADDONTITLE), {'mode': 'resetaddon'}, themeit=CONFIG.THEME2)
        directory.add_separator(themeit=CONFIG.THEME3)
        fold = glob.glob(os.path.join(CONFIG.ADDON_DATA, '*/'))
        for folder in sorted(fold, key = lambda x: x):
            foldername = folder.replace(CONFIG.ADDON_DATA, '').replace('\\', '').replace('/', '')
            icon = os.path.join(folder.replace(CONFIG.ADDON_DATA, CONFIG.ADDONS), 'icon.png')
            fanart = os.path.join(folder.replace(CONFIG.ADDON_DATA, CONFIG.ADDONS), 'fanart.png')
            folderdisplay = foldername
            replace = {'audio.': '[COLOR orange][AUDIO] [/COLOR]', 'metadata.': '[COLOR cyan][METADATA] [/COLOR]',
                       'module.': '[COLOR orange][MODULE] [/COLOR]', 'plugin.': '[COLOR blue][PLUGIN] [/COLOR]',
                       'program.': '[COLOR orange][PROGRAM] [/COLOR]', 'repository.': '[COLOR gold][REPO] [/COLOR]',
                       'script.': '[COLOR cyan][SCRIPT] [/COLOR]',
                       'service.': '[COLOR cyan][SERVICE] [/COLOR]', 'skin.': '[COLOR dodgerblue][SKIN] [/COLOR]',
                       'video.': '[COLOR orange][VIDEO] [/COLOR]', 'weather.': '[COLOR yellow][WEATHER] [/COLOR]'}
            for rep in replace:
                folderdisplay = folderdisplay.replace(rep, replace[rep])
            if foldername in CONFIG.EXCLUDES:
                folderdisplay = '[COLOR cyan][B][PROTEGER][/B][/COLOR] {0}'.format(folderdisplay)
            else:
                folderdisplay = '[COLOR red][B][ELIMINAR][/B][/COLOR] {0}'.format(folderdisplay)
            directory.add_file(' {0}'.format(folderdisplay), {'mode': 'removedata', 'name': foldername}, icon=icon, fanart=fanart, themeit=CONFIG.THEME2)
    else:
        directory.add_file('No se encontró ninguna carpeta de datos de Addon.', themeit=CONFIG.THEME3)


def change_freq():
    from resources.libs.common import logging

    dialog = xbmcgui.Dialog()

    change = dialog.select("[COLOR {0}]Con qué frecuencia incluiría en la lista Auto Limpieza al Iniciar?[/COLOR]".format(CONFIG.COLOR2), CONFIG.CLEANFREQ)
    if not change == -1:
        CONFIG.set_setting('autocleanfreq', str(change))
        logging.log_notify('[COLOR {0}]Limpieza Automática[/COLOR]'.format(CONFIG.COLOR1),
                           '[COLOR {0}]Frecuencia Ahora {1}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.CLEANFREQ[change]))


def developer():
    directory.add_file('Crear Código QR', {'mode': 'createqr'}, themeit=CONFIG.THEME1)
    directory.add_file('Notificaciones de Prueba', {'mode': 'testnotify'}, themeit=CONFIG.THEME1)
    directory.add_file('Actualización de Prueba', {'mode': 'testupdate'}, themeit=CONFIG.THEME1)
    directory.add_file('Solicitud de Compilación de Prueba', {'mode': 'testbuildprompt'}, themeit=CONFIG.THEME1)
    directory.add_file('Probar la Configuración de Guardar Datos', {'mode': 'testsavedata'}, themeit=CONFIG.THEME1)
    directory.add_file('Prueba de Detección Binaria', {'mode': 'binarycheck'}, themeit=CONFIG.THEME1)


###########################
#      Misc Functions     #
###########################


def create_addon_data_menu(add='', name=''):
    menu_items = []

    add2 = quote_plus(add.lower().replace(' ', ''))
    add3 = add.replace('Debrid', 'Real Debrid')
    name2 = quote_plus(name.lower().replace(' ', ''))
    name = name.replace('url', 'URL Resolver')
    menu_items.append((CONFIG.THEME2.format(name.title()), ' '))
    menu_items.append((CONFIG.THEME3.format('Guardar {0} Datos'.format(add3)), 'RunPlugin(plugin://{0}/?mode=save{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('Restaurar {0} Datos'.format(add3)), 'RunPlugin(plugin://{0}/?mode=restore{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('Eliminar {0} Datos'.format(add3)), 'RunPlugin(plugin://{0}/?mode=clear{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))

    menu_items.append((CONFIG.THEME2.format('{0} Ajustes'.format(CONFIG.ADDONTITLE)), 'RunPlugin(plugin://{0}/?mode=settings)'.format(CONFIG.ADDON_ID)))

    return menu_items


def create_save_data_menu(add='', name=''):
    menu_items = []

    add2 = quote_plus(add.lower().replace(' ', ''))
    add3 = add.replace('Debrid', 'Real Debrid')
    name2 = quote_plus(name.lower().replace(' ', ''))
    name = name.replace('url', 'URL Resolver')
    menu_items.append((CONFIG.THEME2.format(name.title()), ' '))
    menu_items.append((CONFIG.THEME3.format('Registrar {0}'.format(add3)), 'RunPlugin(plugin://{0}/?mode=auth{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('Guardar {0} Datos'.format(add3)), 'RunPlugin(plugin://{0}/?mode=save{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('Restaurar {0} Datos'.format(add3)), 'RunPlugin(plugin://{0}/?mode=restore{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('Importar {0} Datos'.format(add3)), 'RunPlugin(plugin://{0}/?mode=import{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('Eliminar Addon {0} Datos'.format(add3)), 'RunPlugin(plugin://{0}/?mode=addon{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))

    menu_items.append((CONFIG.THEME2.format('{0} Ajustes'.format(CONFIG.ADDONTITLE)), 'RunPlugin(plugin://{0}/?mode=settings)'.format(CONFIG.ADDON_ID)))

    return menu_items
