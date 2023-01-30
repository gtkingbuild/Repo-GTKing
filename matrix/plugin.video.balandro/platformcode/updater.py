# -*- coding: utf-8 -*-

import os, xbmc, time, traceback

from platformcode import config, logger, platformtools
from core import httptools, jsontools, filetools, downloadtools, scrapertools


ant_repos = ['2.0.0', '1.0.5', '1.0.3'] 

ver_repo_balandro = 'repository.balandro-3.0.0.zip'

REPO_ID = 'repository.balandro'

REPO_BALANDRO = 'https://raw.githubusercontent.com/balandro-tk/balandro/main/' + ver_repo_balandro


ADDON_UPDATES_JSON = 'https://raw.githubusercontent.com/balandro-tk/addon_updates/main/updates.json'
ADDON_UPDATES_ZIP  = 'https://raw.githubusercontent.com/balandro-tk/addon_updates/main/updates.zip'

ADDON_VERSION = 'https://raw.githubusercontent.com/balandro-tk/balandro/main/addons.xml'


addon_update_verbose = config.get_setting('addon_update_verbose', default=False)
addon_update_domains = config.get_setting('addon_update_domains', default=False)

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


def check_repo(force=False):
    logger.info()

    if not config.get_setting('check_repo', default=True): return

    addons_path = os.path.join(filetools.translatePath("special://home/addons"))
    packages_path = os.path.join(filetools.translatePath("special://home/addons/packages"))
    path_repo = os.path.join(filetools.translatePath("special://home/addons/repository.balandro"))

    instalar_repo = False
    re_install_repo = False

    if os.path.isdir(path_repo) == True:
        try:
            import xbmcaddon

            repo_version = xbmcaddon.Addon(REPO_ID).getAddonInfo("version").strip()

            for ant in ant_repos:
                if ant == repo_version:
                    logger.info('Balandro Repo obsoleto')
                    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Balandro Repo Obsoleto[/COLOR][/B]' % color_alert)
                    instalar_repo = True
        except:
            re_install_repo = True

    if os.path.isdir(path_repo) == False: instalar_repo = True

    if instalar_repo:
        repo_zip = os.path.join(packages_path, ver_repo_balandro)

        if os.path.exists(repo_zip): os.remove(repo_zip)

        down_stats = downloadtools.do_download(REPO_BALANDRO, packages_path, ver_repo_balandro, silent=True, resume=False)

        if down_stats['downloadStatus'] != 2:
            logger.error('No se pudo descargar Balandro Repo')
            return

        try:
            import zipfile
            dir = zipfile.ZipFile(repo_zip, 'r')
            dir.extractall(addons_path)
            dir.close()
        except:
            xbmc.executebuiltin('Extract("%s", "%s")' % (repo_zip, addons_path))

        time.sleep(2)
        logger.info('Instalando Balandro Repo')
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Instalando Balandro Repo[/COLOR][/B]' % color_infor)

        try:
            xbmc.executebuiltin('UpdateLocalAddons')
            time.sleep(2)

            xbmc.executeJSONRPC('{"jsonrpc": "3.0", "id": 1, "method": "Addons.SetAddonEnabled", "params": {"addonid": "repository.balandro", "enabled": true}}')

            xbmc.executebuiltin('UpdateAddonRepos')
            time.sleep(2)

            logger.info('Balandro Repo activado')
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Balandro Repo activado[/COLOR][/B]' % color_avis)

            if instalar_repo: time.sleep(6)
        except:
            logger.error('Error activación Balandro Repo')
            logger.error(traceback.format_exc())
            return False

    else:
        if os.path.isdir(path_repo) == True:
            if re_install_repo == False:
                try:
                    if xbmc.getCondVisibility('System.HasAddon("%s")' % (REPO_ID)): return

                    try:
                        if xbmc.executebuiltin('InstallAddon(%s)' % (REPO_ID)) == 0: return
                        return
                    except RuntimeError:
                        logger.error('Balandro Repo No instalado')
                        return

                except:
                    pass

        xbmc.executeJSONRPC('{"jsonrpc": "3.0", "id": 1, "method": "Addons.SetAddonEnabled", "params": {"addonid": "repository.balandro", "enabled": true}}')

        xbmc.executebuiltin('UpdateAddonRepos')
        time.sleep(2)

        logger.info('Balandro Repo Re-activado')
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Balandro Repo [COLOR %s]Re-activado[/COLOR][/B]' % (color_adver, color_avis))


def check_addon_updates(verbose=False, force=False):
    logger.info()

    check_repo()

    get_last_chrome_list()

    try:
        last_fix_json = os.path.join(config.get_runtime_path(), 'last_fix.json')

        if force and os.path.exists(last_fix_json): os.remove(last_fix_json)

        data = httptools.downloadpage(ADDON_UPDATES_JSON, timeout=2).data

        if data == '':
            logger.error('No localizado addon_updates')

            if verbose: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No localizado addon_updates[/COLOR][/B]' % color_alert)
            return False

        data = jsontools.load(data)

        if 'addon_version' not in data or 'fix_version' not in data:
            logger.info('Sin Fix pendientes')

            if verbose: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Fix pendientes[/COLOR][/B]' % color_adver)
            return False

        current_version = config.get_addon_version(with_fix=False)
        if current_version != data['addon_version']:
            logger.info('Versión Incorrecta NO se actualizan Fixes para la versión %s' % current_version)

            if verbose: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Versión incorrecta NO se actualizan Fixes[/COLOR][/B]' % color_alert)
            return False

        if os.path.exists(last_fix_json):
            lastfix = jsontools.load(filetools.read(last_fix_json))

            if lastfix['addon_version'] == data['addon_version'] and lastfix['fix_version'] == data['fix_version']:
                logger.info('Está actualizado. Versión %s.fix%d' % (data['addon_version'], data['fix_version']))

                if verbose:
                    tex = '[B][COLOR %s]Está actualizado versión %s.fix%d[/COLOR][/B]' % (color_adver, data['addon_version'], data['fix_version'])
                    platformtools.dialog_notification(config.__addon_name, tex)

                return False

        localfilename = os.path.join(config.get_data_path(), 'temp_updates.zip')

        if os.path.exists(localfilename): os.remove(localfilename)

        down_stats = downloadtools.do_download(ADDON_UPDATES_ZIP, config.get_data_path(), 'temp_updates.zip', silent=True, resume=False)

        if down_stats['downloadStatus'] != 2:
            logger.error('No se pudo descargar la actualización')

            if verbose: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se pudo descargar la actualización[/COLOR][/B]' % color_alert)
            return False

        try:
            import zipfile
            dir = zipfile.ZipFile(localfilename, 'r')
            dir.extractall(config.get_runtime_path())
            dir.close()
        except:
            xbmc.executebuiltin('Extract("%s", "%s")' % (localfilename, config.get_runtime_path()))

        time.sleep(2)

        os.remove(localfilename)

        filetools.write(last_fix_json, jsontools.dump(data))

        logger.info('Addon actualizado correctamente a %s.fix%d' % (data['addon_version'], data['fix_version']))

        if addon_update_verbose:
            from modules import helper
            helper.show_last_fix('')

        if addon_update_domains:
            from modules import actions
            actions.show_latest_domains('')

        if verbose:
            tex = '[B][COLOR %s]Actualizado a la versión %s.fix%d[/COLOR][/B]' % (color_avis, data['addon_version'], data['fix_version'])
            platformtools.dialog_notification(config.__addon_name, tex)

        return True

    except:
        logger.error('Error comprobación actualizaciones!')
        logger.error(traceback.format_exc())

        if verbose: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Error comprobación actualizaciones[/COLOR][/B]' % color_alert)
        return False


def get_last_chrome_list():
    logger.info()

    ver_stable_chrome = config.get_setting("ver_stable_chrome", default=True)

    if ver_stable_chrome:
        try:
            data = httptools.downloadpage('https://omahaproxy.appspot.com/all?csv=1').data
            web_last_ver_chrome = scrapertools.find_single_match(data, "win64,stable,([^,]+),")
        except:
            web_last_ver_chrome = ''

        if not web_last_ver_chrome == '':  config.set_setting('chrome_last_version', web_last_ver_chrome)


def check_addon_version():
    logger.info()

    from xml.etree import ElementTree

    repo_data = httptools.downloadpage(ADDON_VERSION, timeout=10).data

    xml = ElementTree.fromstring(repo_data)
    addon = list(filter(lambda x: x.get("id") == config.__addon_id, xml.findall('addon')))[0]

    if addon.get('version') == config.get_addon_version(False): return True

    return False
