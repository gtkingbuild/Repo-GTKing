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
import shutil

from resources.libs.common.config import CONFIG

###########################
#      Fresh Install      #
###########################


def wipe():
    from resources.libs import db
    from resources.libs.common import logging
    from resources.libs import skin
    from resources.libs.common import tools
    from resources.libs import update

    if CONFIG.KEEPTRAKT == 'true':
        from resources.libs import traktit

        traktit.auto_update('all')
        CONFIG.set_setting('traktnextsave', str(tools.get_date(days=3, formatted=True)))
    if CONFIG.KEEPDEBRID == 'true':
        from resources.libs import debridit

        debridit.auto_update('all')
        CONFIG.set_setting('debridnextsave', str(tools.get_date(days=3, formatted=True)))
    if CONFIG.KEEPLOGIN == 'true':
        from resources.libs import loginit

        loginit.auto_update('all')
        CONFIG.set_setting('loginnextsave', str(tools.get_date(days=3, formatted=True)))

    exclude_dirs = CONFIG.EXCLUDES
    exclude_dirs.append('Mis_Builds')
    
    progress_dialog = xbmcgui.DialogProgress()
    
    skin.skin_to_default('Fresh Install')
    
    update.addon_updates('set')
    xbmcPath = os.path.abspath(CONFIG.HOME)
    progress_dialog.create(CONFIG.ADDONTITLE, "[COLOR {0}][B]Calcular archivos y carpetas[/B]".format(CONFIG.COLOR2) + '\n' + '\n' + '[B]Espere por Favor![/B][/COLOR]')
    total_files = sum([len(files) for r, d, files in os.walk(xbmcPath)])
    del_file = 0
    progress_dialog.update(0, "[COLOR {0}]Recopilación de lista de Excluidos.[/COLOR]".format(CONFIG.COLOR2))
    if CONFIG.KEEPREPOS == 'true':
        repos = glob.glob(os.path.join(CONFIG.ADDONS, 'repo*/'))
        for item in repos:
            repofolder = os.path.split(item[:-1])[1]
            if not repofolder == exclude_dirs:
                exclude_dirs.append(repofolder)
    if CONFIG.KEEPSUPER == 'true':
        exclude_dirs.append('plugin.program.super.favourites')
    if CONFIG.KEEPWHITELIST == 'true':
        from resources.libs import whitelist
        
        whitelist = whitelist.whitelist('read')
        if len(whitelist) > 0:
            for item in whitelist:
                try:
                    name, id, fold = item
                except:
                    pass

                depends = db.depends_list(fold)
                for plug in depends:
                    if plug not in exclude_dirs:
                        exclude_dirs.append(plug)
                    depends2 = db.depends_list(plug)
                    for plug2 in depends2:
                        if plug2 not in exclude_dirs:
                            exclude_dirs.append(plug2)
                if fold not in exclude_dirs:
                    exclude_dirs.append(fold)

    for item in CONFIG.DEPENDENCIES:
        exclude_dirs.append(item)

    progress_dialog.update(0, "[COLOR {0}][B]Borrar archivos y carpetas:[/B]".format(CONFIG.COLOR2))
    latestAddonDB = db.latest_db('Addons')
    for root, dirs, files in os.walk(xbmcPath, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in files:
            del_file += 1
            fold = root.replace('/', '\\').split('\\')
            x = len(fold)-1
            if name == 'fuentes.xml' and fold[-1] == 'userdata' and CONFIG.KEEPSOURCES == 'true':
                logging.log("Mantener fuentes.xml: {0}".format(os.path.join(root, name)))
            elif name == 'favoritos.xml' and fold[-1] == 'userdata' and CONFIG.KEEPFAVS == 'true':
                logging.log("Mantener favoritos.xml: {0}".format(os.path.join(root, name)))
            elif name == 'perfiles.xml' and fold[-1] == 'userdata' and CONFIG.KEEPPROFILES == 'true':
                logging.log("Mantener perfiles.xml: {0}".format(os.path.join(root, name)))
            elif name == 'playercorefactory.xml' and fold[-1] == 'userdata' and CONFIG.KEEPPLAYERCORE == 'true':
                logging.log("Mantener playercorefactory.xml: {0}".format(os.path.join(root, name)))
            elif name == 'guisettings.xml' and fold[-1] == 'userdata' and CONFIG.KEEPGUISETTINGS == 'true':
                logging.log("Mantener guisettings.xml: {0}".format(os.path.join(root, name)))
            elif name == 'advancedsettings.xml' and fold[-1] == 'userdata' and CONFIG.KEEPADVANCED == 'true':
                logging.log("Mantener advancedsettings.xml: {0}".format(os.path.join(root, name)))
            elif name in CONFIG.LOGFILES:
                logging.log("Mantener archivo del Log: {0}".format(name))
            elif name.endswith('.db'):
                try:
                    if name == latestAddonDB:
                        logging.log("Ignorando {0} en Kodi{1}".format(name, tools.kodi_version()))
                    else:
                        os.remove(os.path.join(root, name))
                except Exception as e:
                    if not name.startswith('Textures13'):
                        logging.log('Error al eliminar, Purgando DB')
                        logging.log("-> {0}".format(str(e)))
                        db.purge_db_file(os.path.join(root, name))
            else:
                progress_dialog.update(int(tools.percentage(del_file, total_files)), '\n' + '[COLOR {0}][B]Archivo:[/B] [/COLOR][COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name))
                try:
                    os.remove(os.path.join(root, name))
                except Exception as e:
                    logging.log("Error eliminando {0}".format(os.path.join(root, name)))
                    logging.log("-> / {0}".format(str(e)))
        if progress_dialog.iscanceled():
            progress_dialog.close()
            logging.log_notify(CONFIG.ADDONTITLE,
                               "[COLOR {0}]Fresh Start Cancelado[/COLOR]".format(CONFIG.COLOR2))
            return False
    for root, dirs, files in os.walk(xbmcPath, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in dirs:
            progress_dialog.update(100, '\n' + '[B]Limpieza de Carpeta Vacía:[/B] [COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, name))
            if name not in ["Database", "userdata", "temp", "addons", "addon_data"]:
                shutil.rmtree(os.path.join(root, name), ignore_errors=True, onerror=None)
        if progress_dialog.iscanceled():
            progress_dialog.close()
            logging.log_notify(CONFIG.ADDONTITLE,
                               "[COLOR {0}]Fresh Start Cancelado[/COLOR]".format(CONFIG.COLOR2))
            return False
            
    progress_dialog.close()
    CONFIG.clear_setting('build')


def fresh_start(install=None, over=False):
    from resources.libs.common import logging
    from resources.libs.common import tools

    dialog = xbmcgui.Dialog()
    
    if CONFIG.KEEPTRAKT == 'true':
        from resources.libs import traktit

        traktit.auto_update('all')
        CONFIG.set_setting('traktnextsave', str(tools.get_date(days=3, formatted=True)))
    if CONFIG.KEEPDEBRID == 'true':
        from resources.libs import debridit

        debridit.auto_update('all')
        CONFIG.set_setting('debridnextsave', str(tools.get_date(days=3, formatted=True)))
    if CONFIG.KEEPLOGIN == 'true':
        from resources.libs import loginit

        loginit.auto_update('all')
        CONFIG.set_setting('loginnextsave', str(tools.get_date(days=3, formatted=True)))

    if over:
        yes_pressed = 1

    elif install == 'restore':
        yes_pressed = dialog.yesno(CONFIG.ADDONTITLE,
                                       "[COLOR {0}][B]Desea restaurar su[/B]".format(CONFIG.COLOR2)
                                       +'\n'+"[B]Configuración de Kodi a la configuración predeterminada[/B]"
                                       +'\n'+"[B]¿Antes de instalar la copia de seguridad local?[/B][/COLOR]",                                       
									   nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',
                                       yeslabel='[B][COLOR cyan]Continuar[/COLOR][/B]')
    elif install:
        yes_pressed = dialog.yesno(CONFIG.ADDONTITLE, "[COLOR {0}][B]Desea restaurar su[/B]".format(CONFIG.COLOR2)
                                       +'\n'+"[B]Configuración de Kodi a la configuración predeterminada[/B]"
                                       +'\n'+"[B]Antes de instalar[/B] [COLOR {0}]{1}[/COLOR][B]?[/B]".format(CONFIG.COLOR1, install),
                                       nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',
                                       yeslabel='[B][COLOR cyan]Continuar[/COLOR][/B]')
    else:
        yes_pressed = dialog.yesno(CONFIG.ADDONTITLE, "[COLOR {0}][B]Desea restaurar su[/B]".format(CONFIG.COLOR2) +' \n' + "[B]Configuración de Kodi a la configuración predeterminada[/B][/COLOR]", nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]', yeslabel='[B][COLOR cyan]Continuar[/COLOR][/B]')
    if yes_pressed:
        wipe()
        
        if over:
            return True
        elif install == 'restore':
            return True
        elif install:
            from resources.libs.wizard import Wizard

            Wizard().build('normal', install, over=True)
        else:
            dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}][B]Para guardar los cambios, ahora necesita Forzar el Cierre de Kodi, Presione [COLOR azure]OK[/COLOR] para Forzar el Cierre de Kodi[/B][/COLOR]".format(CONFIG.COLOR2))
            from resources.libs import update
            update.addon_updates('reset')
            tools.kill_kodi(over=True)
    else:
        if not install == 'restore':
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}][B]Instalación Nueva:[/B] Cancelada![/COLOR]'.format(CONFIG.COLOR2))
            xbmc.executebuiltin('Container.Refresh()')


def choose_file_manager():
    if not xbmc.getCondVisibility('System.HasAddon(script.kodi.android.update)'):
        from resources.libs.gui import addon_menu
        addon_menu.install_from_kodi('script.kodi.android.update')
    
    try:
        updater = xbmcaddon.Addon('script.kodi.android.update')
    except RuntimeError as e:
        return False
        
    updater.setSetting('File_Manager', '1')
    
    CONFIG.open_settings('script.kodi.android.update', 0, 4, True)
    

def install_apk(name, url):
    from resources.libs.downloader import Downloader
    from resources.libs.common import logging
    from resources.libs.common import tools
    from resources.libs.gui import window

    dialog = xbmcgui.Dialog()
    progress_dialog = xbmcgui.DialogProgress()
    
    addon = xbmcaddon.Addon()
    path = addon.getSetting('apk_path')
    apk = os.path.basename(url).replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
    apk = apk if apk.endswith('.apk') else '{}.apk'.format(apk)
    lib = os.path.join(path, apk)
    
    if not xbmc.getCondVisibility('System.HasAddon(script.kodi.android.update)'):
        from resources.libs.gui import addon_menu
        addon_menu.install_from_kodi('script.kodi.android.update')
        
    try:
        updater = xbmcaddon.Addon('script.kodi.android.update')
    except RuntimeError as e:
        return False
        
    file_manager = int(updater.getSetting('File_Manager'))
    custom_manager = updater.getSetting('Custom_Manager')
    use_manager = {0: 'com.android.documentsui', 1: custom_manager}[file_manager]
    
    if tools.platform() == 'android':
        redownload = True
        yes = True
        if os.path.exists(lib):
            redownload = dialog.yesno(CONFIG.ADDONTITLE, '[COLOR {}]{}[/COLOR] ya existe. Te gustaría volver a descargarlo?'.format(CONFIG.COLOR1, apk),
                               yeslabel="[B]Volver a descargar[/B]",
                               nolabel="[B]Instalar[/B]")
            yes = False
        else:
            yes = dialog.yesno(CONFIG.ADDONTITLE,
                                   "[COLOR {0}]Le gustaría descargar e instalar: ".format(CONFIG.COLOR2)
                                   +'\n'+"[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, name),
                                   yeslabel="[B][COLOR cyan]Descargar[/COLOR][/B]",
                                   nolabel="[B][COLOR red]Cancelar[/COLOR][/B]")
                                   
            if not yes:
                logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]ERROR: Instalación Cancelada[/COLOR]'.format(CONFIG.COLOR2))
                return
        
        if yes or redownload:
            response = tools.open_url(url, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]APK Instalador: Apk Url Invalida![/COLOR]'.format(CONFIG.COLOR2))
                return
                
            progress_dialog.create(CONFIG.ADDONTITLE,
                          '[COLOR {0}][B]Descargando:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, apk)
                          +'\n'+''
                          +'\n'+'Espere por favor')
            
            try:
                os.remove(lib)
            except:
                pass
            Downloader().download(url, lib)
            xbmc.sleep(100)
            progress_dialog.close()
                
        dialog.ok(CONFIG.ADDONTITLE, '[COLOR {}]{}[/COLOR] descargado a [COLOR {}]{}[/COLOR]. Si la instalación no comienza por sí sola, navegue hasta esa ubicación para instalar el APK.'.format(CONFIG.COLOR1, apk, CONFIG.COLOR1, path))
        
        logging.log('Opening {} with {}'.format(lib, use_manager), level=xbmc.LOGINFO)
        xbmc.executebuiltin('StartAndroidActivity({},,,"content://{}")'.format(use_manager, lib))
    else:
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]ERROR: Ningun Dispositivo Android[/COLOR]'.format(CONFIG.COLOR2))
