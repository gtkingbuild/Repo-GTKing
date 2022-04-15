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
import shutil

from datetime import datetime
from datetime import timedelta

import sqlite3 as database

from resources.libs.common.config import CONFIG
from resources.libs.common import logging
from resources.libs.common import tools


def get_cache_size():
    from resources.libs.common import tools

    PROFILEADDONDATA = os.path.join(CONFIG.PROFILE, 'addon_data')

    dbfiles = [
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'cache.meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'cache.meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'cache.meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'cache.meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'cache.meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'meta.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'torrentScrape.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.module.simplecache', 'simplecache.db'))]
    cachelist = [
        CONFIG.ADDON_DATA,
        (os.path.join(CONFIG.HOME, 'cache')),
        (os.path.join(CONFIG.HOME, 'temp')),
        (os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')),
        (os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')),
        (os.path.join(CONFIG.ADDON_DATA,'script.module.simple.downloader')),
        (os.path.join(CONFIG.ADDON_DATA,'plugin.video.itv','Images')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'images')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'TheMovieDB')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'YouTube')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.program.autocompletion', 'Google')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.program.autocompletion', 'Bing')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.openmeta', '.storage'))]
    if not PROFILEADDONDATA == CONFIG.ADDON_DATA:
        cachelist.append(os.path.join(PROFILEADDONDATA, 'script.module.simple.downloader'))
        cachelist.append(os.path.join(PROFILEADDONDATA, 'plugin.video.itv','Images'))
        cachelist.append(os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'images'))
        cachelist.append(os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'TheMovieDB')),
        cachelist.append(os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'YouTube')),
        cachelist.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.program.autocompletion', 'Google')),
        cachelist.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.program.autocompletion', 'Bing')),
        cachelist.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.openmeta', '.storage')),
        cachelist.append(PROFILEADDONDATA)

    totalsize = 0

    for item in cachelist:
        if not os.path.exists(item):
            continue
        if item not in [CONFIG.ADDON_DATA, PROFILEADDONDATA]:
            totalsize = tools.get_size(item, totalsize)
        else:
            for root, dirs, files in os.walk(item):
                for d in dirs:
                    if 'cache' in d.lower() and d.lower() not in ['meta_cache']:
                        totalsize = tools.get_size(os.path.join(root, d), totalsize)

    if CONFIG.INCLUDEVIDEO == 'true':
        files = []
        if CONFIG.INCLUDEALL == 'true':
            files = dbfiles
        else:
            if CONFIG.INCLUDEEXODUSREDUX == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'providers.13.db'))
            if CONFIG.INCLUDEVENOM == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'providers.13.db'))
            if CONFIG.INCLUDENUMBERS == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'providers.13.db'))
            if CONFIG.INCLUDESCRUBS == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'providers.13.db'))
            if CONFIG.INCLUDEGAIA == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'meta.db'))
            if CONFIG.INCLUDESEREN == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'torrentScrape.db'))
            if CONFIG.INCLUDETHECREW == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'providers.13.db'))
        if len(files) > 0:
            for item in files:
                if not os.path.exists(item):
                    continue
                totalsize += os.path.getsize(item)
        else:
            logging.log("Eliminar Cache: Eliminar Cache de Video No Habilitado")

    return totalsize


def clear_packages(over=None):
    from resources.libs.common import tools

    if os.path.exists(CONFIG.PACKAGES):
        try:
            for root, dirs, files in os.walk(CONFIG.PACKAGES):
                file_count = 0
                file_count += len(files)
                if file_count > 0:
                    size = tools.convert_size(tools.get_size(CONFIG.PACKAGES))
                    if over:
                        yes = 1
                    else:
                        dialog = xbmcgui.Dialog()
                    
                        yes = dialog.yesno("[COLOR {0}]Eliminar Archivos de Paquete[/COLOR]".format(CONFIG.COLOR2), "[COLOR {0}]{1}[/COLOR] archivos encontrados / [COLOR {2}]{3}[/COLOR] en tamaño.".format(CONFIG.COLOR1, str(file_count),CONFIG.COLOR1, size) + '\n' + "Quieres eliminarlos?", nolabel='[B][COLOR red]No Eliminar[/COLOR][/B]', yeslabel='[B][COLOR cyan]Eliminar Paquetes[/COLOR][/B]')
                    if yes:
                        for f in files:
                            os.unlink(os.path.join(root, f))
                        for d in dirs:
                            shutil.rmtree(os.path.join(root, d))
                        logging.log_notify(CONFIG.ADDONTITLE,
                                  '[COLOR {0}]Eliminar Paquetes: Correcto![/COLOR]'.format(CONFIG.COLOR2))
                else:
                    logging.log_notify(CONFIG.ADDONTITLE,
                              '[COLOR {0}]Eliminar Paquetes: Ninguno Encontrado![/COLOR]'.format(CONFIG.COLOR2))
        except Exception as e:
            logging.log_notify(CONFIG.ADDONTITLE,
                      '[COLOR {0}]Eliminar Paquetes: Error![/COLOR]'.format(CONFIG.COLOR2))
            logging.log("Error Eliminar Paquetes: {0}".format(str(e)), level=xbmc.LOGERROR)
    else:
        logging.log_notify(CONFIG.ADDONTITLE,
                  '[COLOR {0}]Eliminar Paquetes: Ninguno Encontrado![/COLOR]'.format(CONFIG.COLOR2))


def clear_packages_startup():
    from resources.libs.common import tools

    start = datetime.utcnow() - timedelta(minutes=3)
    file_count = 0
    cleanupsize = 0
    if os.path.exists(CONFIG.PACKAGES):
        pack = os.listdir(CONFIG.PACKAGES)
        pack.sort(key=lambda f: os.path.getmtime(os.path.join(CONFIG.PACKAGES, f)))
        try:
            for item in pack:
                file = os.path.join(CONFIG.PACKAGES, item)
                lastedit = datetime.utcfromtimestamp(os.path.getmtime(file))
                if lastedit <= start:
                    if os.path.isfile(file):
                        file_count += 1
                        cleanupsize += os.path.getsize(file)
                        os.unlink(file)
                    elif os.path.isdir(file):
                        cleanupsize += tools.get_size(file)
                        cleanfiles, cleanfold = tools.clean_house(file)
                        file_count += cleanfiles + cleanfold
                        try:
                            shutil.rmtree(file)
                        except Exception as e:
                            logging.log("No se pudo eliminar {0}: {1}".format(file, str(e), xbmc.LOGERROR))
            if file_count > 0:
                logging.log_notify(CONFIG.ADDONTITLE,
                          '[COLOR {0}]Eliminar Paquetes: Correcto: {1}[/COLOR]'.format(CONFIG.COLOR2, tools.convert_size(cleanupsize)))
            else:
                logging.log_notify(CONFIG.ADDONTITLE,
                          '[COLOR {0}]Eliminar Paquetes: Ninguno Encontrado![/COLOR]'.format(CONFIG.COLOR2))
        except Exception as e:
            logging.log_notify(CONFIG.ADDONTITLE,
                      '[COLOR {0}]Eliminar Paquetes: Error![/COLOR]'.format(CONFIG.COLOR2))
            logging.log("Error Eliminar Paquetes: {0}".format(str(e)), level=xbmc.LOGERROR)
    else:
        logging.log_notify(CONFIG.ADDONTITLE,
                  '[COLOR {0}]Eliminar Paquetes: Ninguno Encontrado![/COLOR]'.format(CONFIG.COLOR2))


def clear_archive():
    dialog = xbmcgui.Dialog()

    if dialog.yesno(CONFIG.ADDONTITLE,
                        '[COLOR {0}]Le gustaria Eliminar la carpeta \'Archive_Cache \'?[/COLOR]'.format(CONFIG.COLOR2),
                        nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',
                        yeslabel='[B][COLOR cyan]Si Eliminar[/COLOR][/B]'):
        if os.path.exists(CONFIG.ARCHIVE_CACHE):
            from resources.libs.common import tools
            tools.clean_house(CONFIG.ARCHIVE_CACHE)


def clear_function_cache(over=False):
    dialog = xbmcgui.Dialog()

    if not over:
        if dialog.yesno(CONFIG.ADDONTITLE,
                            '[COLOR {0}]Le gustaria eliminar las caches de la función de resolución?[/COLOR]'.format(CONFIG.COLOR2),
                            nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',
                            yeslabel='[B][COLOR cyan]Eliminar Cache[/COLOR][/B]'):
            clear = True
    else:
        clear = True
        
    if clear:
        if xbmc.getCondVisibility('System.HasAddon(script.module.resolveurl)'):
                xbmc.executebuiltin('RunPlugin(plugin://script.module.resolveurl/?mode=reset_cache)')
        if xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)'):
            xbmc.executebuiltin('RunPlugin(plugin://script.module.urlresolver/?mode=reset_cache)')


def clear_cache(over=None):
    PROFILEADDONDATA = os.path.join(CONFIG.PROFILE, 'addon_data')
    dbfiles = [
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'meta.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'meta.5.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'cache.providers.13.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'cache.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'torrentScrape.db')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.module.simplecache', 'simplecache.db'))]

    cachelist = [
        PROFILEADDONDATA,
        CONFIG.ADDON_DATA,
        (os.path.join(CONFIG.HOME, 'cache')),
        (os.path.join(CONFIG.HOME, 'temp')),
        (os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')),
        (os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.module.simple.downloader')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.itv', 'Images')),
        (os.path.join(PROFILEADDONDATA, 'script.module.simple.downloader')),
        (os.path.join(PROFILEADDONDATA, 'plugin.video.itv', 'Images')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'images')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'TheMovieDB')),
        (os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'YouTube')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.program.autocompletion', 'Google')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.program.autocompletion', 'Bing')),
        (os.path.join(CONFIG.ADDON_DATA, 'plugin.video.openmeta', '.storage'))]

    delfiles = 0
    excludes = ['meta_cache', 'archive_cache']
    for item in cachelist:
        if not os.path.exists(item):
            continue
        if item not in [CONFIG.ADDON_DATA, PROFILEADDONDATA]:
            for root, dirs, files in os.walk(item):
                dirs[:] = [d for d in dirs if d not in excludes]
                file_count = 0
                file_count += len(files)
                if file_count > 0:
                    for f in files:
                        if f not in CONFIG.LOGFILES:
                            try:
                                os.unlink(os.path.join(root, f))
                                logging.log("[Limpiado] {0}".format(os.path.join(root, f)))
                                delfiles += 1
                            except:
                                pass
                        else:
                            logging.log('Ignorar Archivo de Registro: {0}'.format(f))
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                            delfiles += 1
                            logging.log("[Correcto] borro {0} archivos de {1}".format(str(file_count), os.path.join(item, d)),
                                        level=xbmc.LOGINFO)
                        except:
                            logging.log("[Error] al Eliminar la cache en: {0}".format(os.path.join(item, d)),
                                        level=xbmc.LOGINFO)
        else:
            for root, dirs, files in os.walk(item):
                dirs[:] = [d for d in dirs if d not in excludes]
                for d in dirs:
                    if not str(d.lower()).find('cache') == -1:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                            delfiles += 1
                            logging.log("[Correcto] Limpiado{0} ".format(os.path.join(root, d)))
                        except:
                            logging.log("[Fallido] para limpiar la cache en: {0}".format(os.path.join(item, d)))

    if CONFIG.INCLUDEVIDEO == 'true' and over is None:
        files = []
        if CONFIG.INCLUDEALL == 'true':
            files = dbfiles
        else:
            if CONFIG.INCLUDEEXODUSREDUX == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.exodusredux', 'providers.13.db'))
            if CONFIG.INCLUDEVENOM == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.venom', 'providers.13.db'))
            if CONFIG.INCLUDENUMBERS == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.numbersbynumbers', 'providers.13.db'))
            if CONFIG.INCLUDESCRUBS == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.scrubsv2', 'providers.13.db'))
            if CONFIG.INCLUDETHECREW == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'meta.5.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thecrew', 'providers.13.db'))
            if CONFIG.INCLUDEGAIA == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.gaia', 'meta.db'))
            if CONFIG.INCLUDESEREN == 'true':
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'cache.db'))
                files.append(os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'torrentScrape.db'))
        if len(files) > 0:
            for item in files:
                if os.path.exists(item):
                    delfiles += 1
                    try:
                        textdb = database.connect(item)
                        textexe = textdb.cursor()
                    except Exception as e:
                        logging.log("DB Error de conexion: {0}".format(str(e)), level=xbmc.LOGERROR)
                        continue
                    if 'Database' in item:
                        try:
                            textexe.execute("ELIMINAR DE url_cache")
                            textexe.execute("VACUUM")
                            textdb.commit()
                            textexe.close()
                            logging.log("[Correcto] limpiado {0}".format(item))
                        except Exception as e:
                            logging.log("[Fallido] limpiado {0}: {1}".format(item, str(e)))
                    else:
                        textexe.execute("SELECCIONE el nombre de sqlite_master DONDE tipo = 'table'")
                        for table in textexe.fetchall():
                            try:
                                textexe.execute("ELIMINAR DE {0}".format(table[0]))
                                textexe.execute("VACUUM")
                                textdb.commit()
                                logging.log("[Correcto] limpiado {0} en {1}".format(table[0], item))
                            except Exception as e:
                                try:
                                    logging.log("[Fallido] limpiado {0} en {1}: {2}".format(table[0], item, str(e)))
                                except:
                                    pass
                        textexe.close()
        else:
            logging.log("Eliminar Cache: Eliminar Cache de Video No Habilitado")
    logging.log_notify(CONFIG.ADDONTITLE,
                       '[COLOR {0}]Eliminar Cache: Archivos {1} Eliminados[/COLOR]'.format(CONFIG.COLOR2, delfiles)) 


def old_thumbs():
    from resources.libs import db
    from resources.libs.common import tools

    dbfile = os.path.join(CONFIG.DATABASE, db.latest_db('Textures'))
    use = 30
    week = tools.get_date(days=-7)
    ids = []
    images = []
    size = 0
    if os.path.exists(dbfile):
        try:
            textdb = database.connect(dbfile, isolation_level=None)
            textexe = textdb.cursor()
        except Exception as e:
            logging.log("DB Error de Conexion: {0}".format(str(e)), level=xbmc.LOGERROR)
            return False
    else:
        logging.log('{0} no encontrado.'.format(dbfile), level=xbmc.LOGERROR)
        return False
    textexe.execute("SELECT idtexture FROM sizes WHERE usecount < ? AND lastusetime < ?", (use, str(week)))
    found = textexe.fetchall()
    for rows in found:
        idfound = rows[0]
        ids.append(idfound)
        textexe.execute("SELECT cachedurl FROM texture WHERE id = ?", (idfound, ))
        found2 = textexe.fetchall()
        for rows2 in found2:
            images.append(rows2[0])
    logging.log("{0} total de pulgares limpios.".format(str(len(images))))
    for id in ids:
        textexe.execute("DELETE FROM sizes WHERE idtexture = ?", (id, ))
        textexe.execute("DELETE FROM texture WHERE id = ?", (id, ))
    textexe.execute("VACUUM")
    textdb.commit()
    textexe.close()
    for image in images:
        path = os.path.join(CONFIG.THUMBNAILS, image)
        try:
            imagesize = os.path.getsize(path)
            os.remove(path)
            size += imagesize
        except:
            pass
    removed = tools.convert_size(size)
    if len(images) > 0:
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]Pulgares Borrados: {1} Archivos / {2} MB[/COLOR]!'.format(CONFIG.COLOR2, str(len(images)), removed))
    else:
        logging.log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]Pulgares Borrados: Ninguno Encontrado![/COLOR]'.format(CONFIG.COLOR2))


def clear_crash():
    files = []
    for file in glob.glob(os.path.join(CONFIG.LOGPATH, '*crashlog*.*')):
        files.append(file)
    if len(files) > 0:
        dialog = xbmcgui.Dialog()

        if dialog.yesno(CONFIG.ADDONTITLE,
                            '[COLOR {0}]Le gustaria eliminar el Crash logs?'.format(CONFIG.COLOR2)
                            +'\n'+'[COLOR {0}]{1}[/COLOR] Archivos Encontrados[/COLOR]'.format(CONFIG.COLOR1, len(files)),
                            yeslabel="[B][COLOR cyan]Eliminar Logs[/COLOR][/B]",
                            nolabel="[B][COLOR red]Mantener Logs[/COLOR][/B]"):
            for f in files:
                os.remove(f)
            logging.log_notify('[COLOR {0}]Eliminar Crash Logs[/COLOR]'.format(CONFIG.COLOR1),
                               '[COLOR {0}]{1} Crash Logs Eliminado[/COLOR]'.format(CONFIG.COLOR2, len(files)))
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Eliminar Crash Logs Cancelado[/COLOR]'.format(CONFIG.COLOR2))
    else:
        logging.log_notify('[COLOR {0}]Eliminar Crash Logs[/COLOR]'.format(CONFIG.COLOR1),
                           '[COLOR {0}]No se Encontraron Crash Logs[/COLOR]'.format(CONFIG.COLOR2))


def force_text():
    tools.clean_house(CONFIG.TEXTCACHE)
    logging.log_notify(CONFIG.ADDONTITLE,
                       '[COLOR {0}]Archivos de Texto Descargados![/COLOR]'.format(CONFIG.COLOR2))


def toggle_cache(state):
    cachelist = ['includevideo', 'includeall', 'includeexodusredux', 'includegaia', 'includenumbers', 'includescrubs', 'includeseren', 'includethecrew', 'includevenom']
    titlelist = ['Include Video Addons', 'Include All Addons', 'Include Exodus Redux', 'Include Gaia', 'Include NuMb3r5', 'Include Scrubs v2', 'Include Seren', 'Include THE CREW', 'Include Venom']
    if state in ['true', 'false']:
        for item in cachelist:
            CONFIG.set_setting(item, state)
    else:
        if state not in ['includevideo', 'includeall'] and CONFIG.get_setting('includeall') == 'true':
            try:
                dialog = xbmcgui.Dialog()

                item = titlelist[cachelist.index(state)]
                dialog.ok(CONFIG.ADDONTITLE,
                              "[COLOR {0}]Debera desactivar [COLOR {1}]Incluir Todos los Addons[/COLOR] para deshabilitar[/COLOR] [COLOR {2}]{3}[/COLOR]".format(CONFIG.COLOR2, CONFIG.COLOR1, CONFIG.COLOR1, item))
            except:
                logging.log_notify("[COLOR {0}]Alternar Cache[/COLOR]".format(CONFIG.COLOR1),
                                   "[COLOR {0}]Invalido Add-on ID: {1}[/COLOR]".format(CONFIG.COLOR2, state))
        else:
            new = 'true' if CONFIG.get_setting(state) == 'false' else 'false'
            CONFIG.set_setting(state, new)


def total_clean():
    dialog = xbmcgui.Dialog()

    if dialog.yesno(CONFIG.ADDONTITLE,
                        '[COLOR {0}]Le gustaria eliminar la cache, los paquetes y las miniaturas?[/COLOR]'.format(CONFIG.COLOR2),
                        nolabel='[B][COLOR red]Cancelar Proceso[/COLOR][/B]',
                        yeslabel='[B][COLOR cyan]Eliminar Todo[/COLOR][/B]'):
        clear_archive()
        clear_cache()
        clear_function_cache(over=True)
        clear_packages('total')
        clear_thumbs('total')


def clear_thumbs(type=None):
    from resources.libs import db
    
    dialog = xbmcgui.Dialog()

    thumb_locations = {CONFIG.THUMBNAILS,
                       os.path.join(CONFIG.ADDON_DATA, 'script.module.metadatautils', 'animatedgifs'),
                       os.path.join(CONFIG.ADDON_DATA, 'script.extendedinfo', 'images')}

    latest = db.latest_db('Textures')
    if type is not None:
        choice = 1
    else:
        choice = dialog.yesno(CONFIG.ADDONTITLE, '[COLOR {0}]Le gustaria eliminar {1} y las carpetas de miniaturas relacionadas?'.format(CONFIG.COLOR2, latest) + '\n' + "Ellas se repoblarán en la próxima puesta en marcha.[/COLOR]", nolabel='[B][COLOR red]No Eliminar[/COLOR][/B]', yeslabel='[B][COLOR cyan]Eliminar Pulgares[/COLOR][/B]')
    if choice == 1:
        try:
            tools.remove_file(os.path.join(CONFIG.DATABASE, latest))
        except:
            logging.log('Error al eliminar, Purgando DB.')
            db.purge_db_file(latest)
        for i in thumb_locations:
            tools.remove_folder(i)
    else:
        logging.log('Eliminar nombres en miniatura cancelados')

    tools.redo_thumbs()


def remove_addon(addon, name, over=False, data=True):
    import sqlite3
    from resources.libs import db
    
    if over:
        yes = 1
    else:
        dialog = xbmcgui.Dialog()
        
        yes = dialog.yesno(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Estas seguro de que quieres eliminar el add-on:'.format(CONFIG.COLOR2)
                               +'\n'+'Name: [COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, name)
                               +'\n'+'ID: [COLOR {0}]{1}[/COLOR][/COLOR]'.format(CONFIG.COLOR1, addon),
                               yeslabel='[B][COLOR cyan]Eliminar Add-on[/COLOR][/B]',
                               nolabel='[B][COLOR red]No Eliminar[/COLOR][/B]')
    if yes == 1:
        folder = os.path.join(CONFIG.ADDONS, addon)
        logging.log("Eliminando Add-on: {0}".format(addon))

        from resources.libs.common import tools
        tools.clean_house(folder)
        xbmc.sleep(200)
        
        xbmc.executebuiltin('StopScript({0})'.format(addon))
        
        sqldb = sqlite3.connect(os.path.join(CONFIG.DATABASE, db.latest_db('Addons')))
        sqlexe = sqldb.cursor()
        query = "DELETE FROM {0} WHERE addonID = '{1}'"
        
        for table in ['addons', 'installed', 'package']:
            sqlexe.execute(query.format(table, addon))
        
        try:
            shutil.rmtree(folder)
        except Exception as e:
            logging.log("Error al eliminar {0}: {1}".format(addon, str(e)))
        
        if data:
            remove_addon_data(addon)
            
        return True
            
    if not over:
        logging.log_notify(CONFIG.ADDONTITLE,
                           "[COLOR {0}]{1} Eliminando[/COLOR]".format(CONFIG.COLOR2, name))


def remove_addon_data(addon):
    dialog = xbmcgui.Dialog()

    if addon == 'all':  # clear ALL addon data
        if dialog.yesno(CONFIG.ADDONTITLE,
                            '[COLOR {0}]Le gustaria eliminar [COLOR {1}]TODOS[/COLOR] los datos de los addons almacenados en su carpeta de datos de usuario para los addons desinstalados?[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1),
                            yeslabel='[B][COLOR cyan]Eliminar Datos[/COLOR][/B]',
                            nolabel='[B][COLOR red]No Eliminar[/COLOR][/B]'):
            tools.clean_house(CONFIG.ADDON_DATA)
        else:
            logging.log_notify('[COLOR {0}]Eliminar Datos de Addons[/COLOR]'.format(CONFIG.COLOR1),
                               '[COLOR {0}]Cancelado![/COLOR]'.format(CONFIG.COLOR2))
    elif addon == 'desinstalado':  # clear addon data for uninstalled addons
        if dialog.yesno(CONFIG.ADDONTITLE,
                            '[COLOR {0}]Le gustaría eliminar [COLOR {1}]TODOS[/COLOR] los datos de los addons almacenados en su carpeta de datos de usuario para los addons desinstalados?[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1),
                            yeslabel='[B][COLOR cyan]Eliminar Datos[/COLOR][/B]',
                            nolabel='[B][COLOR red]No Eliminar[/COLOR][/B]'):
                            
            total = 0
            
            for folder in glob.glob(os.path.join(CONFIG.ADDON_DATA, '*')):
                foldername = folder.replace(CONFIG.ADDON_DATA, '').replace('\\', '').replace('/', '')
                if foldername in CONFIG.EXCLUDES:
                    pass
                elif os.path.exists(os.path.join(CONFIG.ADDONS, foldername)):
                    pass
                elif os.path.isdir(folder):
                    tools.clean_house(folder)
                    total += 1
                    logging.log(folder)
                    shutil.rmtree(folder)
            logging.log_notify('[COLOR {0}]Limpiar Desinstalado[/COLOR]'.format(CONFIG.COLOR1),
                               '[COLOR {0}]{1} Carpetas(s) Eliminada[/COLOR]'.format(CONFIG.COLOR2, total))
        else:
            logging.log_notify('[COLOR {0}]Eliminar Datos de Add-ons[/COLOR]'.format(CONFIG.COLOR1),
                               '[COLOR {0}]Cancelado![/COLOR]'.format(CONFIG.COLOR2))
    elif addon == 'empty':  # clear empty folders from addon_data
        if dialog.yesno(CONFIG.ADDONTITLE,
                            '[COLOR {0}]Le gustaria eliminar [COLOR {1}] TODAS [/COLOR] las carpetas de datos de addons vacias en su carpeta de datos de usuario?[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1),
                            yeslabel='[B][COLOR cyan]Eliminar Datos[/COLOR][/B]',
                            nolabel='[B][COLOR red]No Eliminar[/COLOR][/B]'):
            total = tools.empty_folder(CONFIG.ADDON_DATA)
            logging.log_notify('[COLOR {0}]Eliminar Carpetas Vacias[/COLOR]'.format(CONFIG.COLOR1),
                               '[COLOR {0}]{1} Carpeta(s) Eliminada[/COLOR]'.format(CONFIG.COLOR2, total))
        else:
            logging.log_notify('[COLOR {0}]Eliminar Carpetas Vacias[/COLOR]'.format(CONFIG.COLOR1),
                               '[COLOR {0}]Cancelado![/COLOR]'.format(CONFIG.COLOR2))
    else:  # clear addon data for a specific addon
        addon_data = os.path.join(CONFIG.ADDON_DATA, addon)
        if addon in CONFIG.EXCLUDES:
            logging.log_notify("[COLOR {0}]Plugin Protegido[/COLOR]".format(CONFIG.COLOR1),
                               "[COLOR {0}]No se permite eliminar datos de los add-ons[/COLOR]".format(CONFIG.COLOR2))
        elif os.path.exists(addon_data):
            if dialog.yesno(CONFIG.ADDONTITLE, '[COLOR {0}]Tambien le gustaria eliminar los datos de los add-ons para:[/COLOR]'.format(CONFIG.COLOR2) + '\n' + '[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, addon), yeslabel='[B][COLOR cyan]Quitar datos[/COLOR][/B]', nolabel='[B][COLOR red]No Quitar[/COLOR][/B]'):
                tools.clean_house(addon_data)
                try:
                    shutil.rmtree(addon_data)
                except:
                    logging.log("Error al eliminar: {0}".format(addon_data))
            else:
                logging.log('No se eliminaron los datos {0} Add-ons para'.format(addon))
    xbmc.executebuiltin('Container.Refresh()')

    
def remove_addon_menu():
    from resources.libs.common import logging
    from resources.libs.common import tools
    from resources.libs import update
    
    from xml.etree import ElementTree
    
    dialog = xbmcgui.Dialog()

    addonfolders = glob.iglob(os.path.join(CONFIG.ADDONS, '*/'))
    addonnames = []
    addonids = []
    
    for folder in addonfolders:
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
            
            try:
                addonnames.append(addonname)
                addonids.append(addonid)
            except:
                pass
                
    if len(addonnames) == 0:
        logging.log_notify(CONFIG.ADDONTITLE,
                           "[COLOR {0}]No hay Addons Para Eliminar[/COLOR]".format(CONFIG.COLOR2))
        return
    selected = dialog.multiselect("{0}: Seleccione los Addons que desea eliminar.".format(CONFIG.ADDONTITLE), addonnames)
    if not selected:
        return
    if len(selected) > 0:
        update.addon_updates('set')
        for addon in selected:
            remove_addon(addon=addonids[addon], name=addonnames[addon], over=True)

        xbmc.sleep(500)

        dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}]Para guardar los cambios, ahora necesita Forzar el Cierre de Kodi, Presione OK para Forzar el Cierre de Kodi[/COLOR]".format(CONFIG.COLOR2))
        
        update.addon_updates('reset')
        tools.kill_kodi(over=True)
