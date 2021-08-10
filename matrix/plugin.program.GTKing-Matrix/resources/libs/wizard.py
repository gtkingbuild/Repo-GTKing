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

import os

from resources.libs import check
from resources.libs import db
from resources.libs import extract
from resources.libs import install
from resources.libs import skin
from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.common.config import CONFIG
from resources.libs.downloader import Downloader


class Wizard:

    def __init__(self):
        tools.ensure_folders(CONFIG.PACKAGES)
        
        self.dialog = xbmcgui.Dialog()
        self.dialogProgress = xbmcgui.DialogProgress()

    def _prompt_for_wipe(self):
        # Should we wipe first?
        if self.dialog.yesno(CONFIG.ADDONTITLE,
                           "[COLOR {0}]Desea restaurar su".format(CONFIG.COLOR2) +'\n' + "configuración de Kodi a la configuración predeterminada" + '\n' + "Antes de instalar la Copia de Seguridad de la Build?[/COLOR]",
                           nolabel='[B][COLOR red]No[/COLOR][/B]',
                           yeslabel='[B][COLOR cyan]Si[/COLOR][/B]'):
            install.wipe()

    def build(self, name, over=False):
        # if action == 'normal':
            # if CONFIG.KEEPTRAKT == 'true':
                # from resources.libs import traktit
                # traktit.auto_update('all')
                # CONFIG.set_setting('traktnextsave', tools.get_date(days=3, formatted=True))
            # if CONFIG.KEEPDEBRID == 'true':
                # from resources.libs import debridit
                # debridit.auto_update('all')
                # CONFIG.set_setting('debridnextsave', tools.get_date(days=3, formatted=True))
            # if CONFIG.KEEPLOGIN == 'true':
                # from resources.libs import loginit
                # loginit.auto_update('all')
                # CONFIG.set_setting('loginnextsave', tools.get_date(days=3, formatted=True))

        temp_kodiv = int(CONFIG.KODIV)
        buildv = int(float(check.check_build(name, 'kodi')))

        if not temp_kodiv == buildv:
            warning = True
        else:
            warning = False

        if warning:
            yes_pressed = self.dialog.yesno("[B]{0} - [COLOR red]ADVERTENCIA!![/COLOR][/B]".format(CONFIG.ADDONTITLE), '[COLOR {0}]Exíste la posibilidad de que el Skin no se vea correctamente'.format(CONFIG.COLOR2) + '\n' + 'Al instalar una {0} Build en un Kodi {1} instalado'.format(check.check_build(name, 'kodi'), CONFIG.KODIV) + '\n' + 'Todavía te gustaría instalar: [COLOR {0}]{1} v{2}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name, check.check_build(name, 'version')), nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]', yeslabel='[B][COLOR cyan]Si, Instalar[/COLOR][/B]')
        else:
            if over:
                yes_pressed = 1
            else:
                yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE, '[COLOR red][B]AVISO!![/B]'.format(CONFIG.ADDONTITLE)  + '\n' + '[COLOR {0}][B]La Instalación Sobreescribirá los datos de su Kodi Actual![/B]'.format(CONFIG.COLOR2)  + '\n\n' + '[COLOR {0}][B]Le gustaría Descargar e Instalar:[/B] '.format(CONFIG.COLOR2) + '[B][COLOR {0}]{1} v{2}[/COLOR]?[/B][/COLOR]'.format(CONFIG.COLOR1, name, check.check_build(name,'version')), nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]', yeslabel='[B][COLOR cyan]Si, Instalar[/COLOR][/B]')
        if yes_pressed:
            CONFIG.clear_setting('build')
            buildzip = check.check_build(name, 'url')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Descargando:[/B][/COLOR] [COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version')) + '\n' + 'Espere por Favor')

            lib = os.path.join(CONFIG.MYBUILDS, '{0}.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(buildzip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
                
            install.wipe()
                
            skin.look_and_feel_data('save')
            
            title = '[COLOR {0}][B]Instalando:[/B][/COLOR] [COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version'))
            self.dialogProgress.update(0, title + '\n' + 'Espere por Favor')
            percent, errors, error = extract.all(lib, CONFIG.HOME, title=title)
            
            skin.skin_to_default('Install Build')

            if int(float(percent)) > 0:
                db.fix_metas()
                CONFIG.set_setting('buildname', name)
                CONFIG.set_setting('buildversion', check.check_build(name, 'version'))
                CONFIG.set_setting('buildtheme', '')
                CONFIG.set_setting('latestversion', check.check_build(name, 'version'))
                CONFIG.set_setting('nextbuildcheck', tools.get_date(days=CONFIG.UPDATECHECK, formatted=True))
                CONFIG.set_setting('installed', 'true')
                CONFIG.set_setting('extract', percent)
                CONFIG.set_setting('errors', errors)
                logging.log('INSTALADO {0}: [ERRORES:{1}]'.format(percent, errors))

                try:
                    os.remove(lib)
                except:
                    pass

                if int(float(errors)) > 0:
                    yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                       '[COLOR {0}][COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version')) +'\n\n' + '[B]Completado:[/B] [COLOR {0}]{1}{2}[/COLOR] [B][Errores:[/B][COLOR {3}]{4}[/COLOR]]'.format(CONFIG.COLOR1, percent, '%', CONFIG.COLOR1, errors) + '\n' + '[B]Le gustaría ver los errores?[/B][/COLOR]',
                                       nolabel='[B][COLOR red]No, Gracias[/COLOR][/B]',
                                       yeslabel='[B][COLOR cyan]Ver Errores[/COLOR][/B]')
                    if yes_pressed:
                        from resources.libs.gui import window
                        window.show_text_box("[B]Visualización de Errores de Instalación de la Build[/B]", error)
                self.dialogProgress.close()

                from resources.libs.gui.build_menu import BuildMenu
                themecount = BuildMenu().theme_count(name)

                if themecount > 99:
                    self.theme(name)

                db.addon_database(CONFIG.ADDON_ID, 1)
                db.force_check_updates(over=True)
                if os.path.exists(os.path.join(CONFIG.USERDATA, '.enableall')):
                	CONFIG.set_setting('enable_all', 'true')

                self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}][B]Para guardar los cambios, ahora necesita Forzar el Cierre de Kodi.[/B] \n\nPresione [B]OK[/B] para Forzar el Cierre de Kodi.[/COLOR]".format(CONFIG.COLOR2))
                tools.kill_kodi(over=True)
            else:
                from resources.libs.gui import window
                window.show_text_box("[B]Visualización de Errores de Instalación de la Build[/B]", error)
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Instalación Build:[/COLOR] [COLOR gold]Cancelado![/COLOR]'.format(CONFIG.COLOR2))

    def gui(self, name, over=False):
        if name == CONFIG.get_setting('buildname'):
            if over:
                yes_pressed = 1
            else:
                yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                   '[COLOR {0}][B]Le gustaría aplicar la Corrección de la interfaz gráfica de usuario para:'.format(CONFIG.COLOR2) + '\n' + '[COLOR {0}]{1}[/COLOR]?[/B][/COLOR]'.format(CONFIG.COLOR1, name),
                                   nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',
                                   yeslabel='[B][COLOR cyan]Aplicar Corrección[/COLOR][/B]')
        else:
            yes_pressed = self.dialog.yesno("[B]{0} - [COLOR red]ADVERTENCIA!![/COLOR][/B]".format(CONFIG.ADDONTITLE),
                               "[COLOR {0}][COLOR {1}]{2}[/COLOR] [B]La Build de la comunidad no está instalada actualmente.".format(CONFIG.COLOR2, CONFIG.COLOR1, name) + '\n' + "Le gustaría aplicar la Corrección Gui ([COLOR azure]de la interfaz gráfica de usuario[/COLOR]) de todos modos?[/B][/COLOR]",
                               nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',
                               yeslabel='[B][COLOR cyan]Aplicar Corrección[/COLOR][/B]')
        if yes_pressed:
            guizip = check.check_build(name, 'gui')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            response = tools.open_url(guizip, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Corrección Gui:[/COLOR] [COLOR gold]Url Zip Inválido![/COLOR]'.format(CONFIG.COLOR2))
                return

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Descargando Corrección Gui:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name), '', 'Espere por Favor')

            lib = os.path.join(CONFIG.PACKAGES, '{0}_guisettings.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(guizip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
            
            title = '[COLOR {0}][B]Instalando:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name)
            self.dialogProgress.update(0, title + '\n' + 'Espere por Favor')
            extract.all(lib, CONFIG.USERDATA, title=title)
            self.dialogProgress.close()
            skin.skin_to_default('Build Install')
            skin.look_and_feel_data('save')
            installed = db.grab_addons(lib)
            db.addon_database(installed, 1, True)

            self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}][B]Para guardar los cambios, ahora necesita Forzar el Cierre de Kodi.[/B] \n\nPresione [B]OK[/B] para Forzar el Cierre de Kodi.[/COLOR]".format(CONFIG.COLOR2))
            tools.kill_kodi(over=True)
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Corrección Gui:[/COLOR] [COLOR gold]Cancelado![/COLOR]'.format(CONFIG.COLOR2))

    def theme(self, name, theme='', over=False):
        installtheme = True

        if not theme:
            themefile = check.check_build(name, 'theme')

            response = tools.open_url(themefile, check=True)
            if response:
                from resources.libs.gui.build_menu import BuildMenu
                themes = BuildMenu().theme_count(name, False)
                if len(themes) > 0:
                    if self.dialog.yesno(CONFIG.ADDONTITLE, "[COLOR {0}][B]La Build [COLOR {1}]{2}[/COLOR] viene con [COLOR {3}]{4}[/COLOR] Parche de actualización[/B]".format(CONFIG.COLOR2, CONFIG.COLOR1, name, CONFIG.COLOR1, len(themes)) + '\n\n' + "[B]Le gustaría instalar el Parche de actualización ahora?[/B][/COLOR]",
                                    yeslabel="[B][COLOR cyan]Instalar Parche[/COLOR][/B]",
                                    nolabel="[B][COLOR red]Cancelar Parche[/COLOR][/B]"):
                        logging.log("Lista de Parches: {0}".format(str(themes)))
                        ret = self.dialog.select(CONFIG.ADDONTITLE, themes)
                        logging.log("[B]Selecciona un Parche para Instalar:[/B] {0}".format(ret))
                        if not ret == -1:
                            theme = themes[ret]
                            installtheme = True
                        else:
                            logging.log_notify(CONFIG.ADDONTITLE,
                                               '[COLOR {0}]Instalación:[/COLOR] [COLOR gold]Cancelado![/COLOR]'.format(CONFIG.COLOR2))
                            return
                    else:
                        logging.log_notify(CONFIG.ADDONTITLE,
                                           '[COLOR {0}]Instalación Parche:[/COLOR] [COLOR gold]Cancelado![/COLOR]'.format(CONFIG.COLOR2))
                        return
            else:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Instalación Parche:[/COLOR] [COLOR gold]Nada Encontrado![/COLOR]'.format(CONFIG.COLOR2))
        else:
            installtheme = self.dialog.yesno(CONFIG.ADDONTITLE, '[COLOR {0}][B]Te gustaría instalar uno de los Parches que hay en:[/B]'.format(CONFIG.COLOR2) +' \n' + '[COLOR dodgerblue][B]PARCHES MATRIX[/B][/COLOR]'.format(CONFIG.COLOR1, theme) + '\n' + '[B]para [COLOR {0}]{1} v{2}[/COLOR]?[/B][/COLOR]'.format(CONFIG.COLOR1, name, check.check_build(name,'version')),yeslabel="[B][COLOR cyan]Instalar Parche[/COLOR][/B]", nolabel="[B][COLOR red]Cancelar Parche[/COLOR][/B]")
                                        
        if installtheme:
            themezip = check.check_theme(name, theme, 'url')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            response = tools.open_url(themezip, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Instalación Parche:[/COLOR] [COLOR gold]Url Zip Inválido![/COLOR]'.format(CONFIG.COLOR2))
                return False

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Descargando:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, zipname) +' \n' + 'Espere por Favor')

            lib = os.path.join(CONFIG.PACKAGES, '{0}.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(themezip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
            
            self.dialogProgress.update(0, '\n' + "Instalando {0}".format(name))

            test1 = False
            test2 = False
            
            from resources.libs import skin
            from resources.libs import test
            test1 = test.test_theme(lib) if CONFIG.SKIN not in skin.DEFAULT_SKINS else False
            #test2 = test.test_gui(lib) if CONFIG.SKIN not in skin.DEFAULT_SKINS else False

            if test1:
                skin.look_and_feel_data('save')
                xbmc.log('test1= ' + str(test1), xbmc.LOGINFO)
                swap = skin.skin_to_default('Theme Install')

                if not swap:
                    return False

                xbmc.sleep(500)

            title = '[COLOR {0}][B]Instalando Parche:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, theme)
            self.dialogProgress.update(0, title + '\n' + 'Espere por Favor')
            percent, errors, error = extract.all(lib, CONFIG.HOME, title=title)
            CONFIG.set_setting('buildtheme', theme)
            logging.log('INSTALADO {0}: [ERRORES:{1}]'.format(percent, errors))
            self.dialogProgress.close()

            #db.force_check_updates(over=True)
            installed = db.grab_addons(lib)
            db.addon_database(installed, 1, True)

            self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}][B]Para guardar los cambios, ahora necesita Forzar el Cierre de Kodi.[/B] \n\nPresione [B]OK[/B] para Forzar el Cierre de Kodi.[/COLOR]".format(CONFIG.COLOR2))
            tools.kill_kodi(over=True)
            
            if test2:
                skin.look_and_feel_data('save')
                xbmc.log('test2= ' + str(test2), xbmc.LOGINFO)
                skin.skin_to_default("Theme Install")
                gotoskin = CONFIG.get_setting('defaultskin')
                skin.switch_to_skin(gotoskin, "Theme Installer")
                skin.look_and_feel_data('restore')
            elif test1:
                #skin.look_and_feel_data('save')
                #skin.skin_to_default("Theme Install")
                gotoskin = CONFIG.get_setting('default.skin')
                skin.switch_to_skin(gotoskin, "Theme Installer")
                skin.look_and_feel_data('restore')
                if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
                	xbmc.executebuiltin('SendClick(yesnodialog, 11)')
            else:
                xbmc.executebuiltin("ReloadSkin()")
                xbmc.sleep(1000)
                xbmc.executebuiltin("Container.Refresh()")
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Instalación Parche:[/COLOR] [COLOR gold]Cancelado![/COLOR]'.format(CONFIG.COLOR2))


def wizard(action, name, url):
    cls = Wizard()

    if action in ['fresh', 'normal']:
        cls.build(action, name)
    elif action == 'gui':
        cls.gui(name)
    elif action == 'theme':
        cls.theme(name, url)
