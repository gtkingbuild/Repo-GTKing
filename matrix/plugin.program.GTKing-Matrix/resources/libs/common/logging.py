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
import xbmcvfs

import os
import re
import time

import _strptime

from resources.libs.common import tools
from resources.libs.common.config import CONFIG

try:  # Python 3
    from urllib.parse import urlencode
    from urllib.request import FancyURLopener
except ImportError:  # Python 2
    from urllib import urlencode
    from urllib import FancyURLopener


URL = 'https://t.me/beelinkking'
EXPIRATION = 2592000
REPLACES = (('//.+?:.+?@', '//USER:PASSWORD@'), ('<user>.+?</user>', '<user>USER</user>'), ('<pass>.+?</pass>',
                                                                                            '<pass>PASSWORD</pass>'),)


def log(msg, level=xbmc.LOGDEBUG):
    if CONFIG.DEBUGLEVEL == '0':  # No Logging
        return False
    if CONFIG.DEBUGLEVEL == '1':  # Normal Logging
        pass
    if CONFIG.DEBUGLEVEL == '2':  # Full Logging
        level = xbmc.LOGINFO
    
    xbmc.log('{0}: {1}'.format(CONFIG.ADDONTITLE, msg), level)
    if CONFIG.ENABLEWIZLOG == 'true':
        if not os.path.exists(CONFIG.WIZLOG):
            with open(CONFIG.WIZLOG, 'w+') as f:
                f.close()

        lastcheck = CONFIG.NEXTCLEANDATE if not CONFIG.NEXTCLEANDATE == 0 else tools.get_date()
        if CONFIG.CLEANWIZLOG == 'true' and time.mktime(time.strptime(lastcheck, "%Y-%m-%d %H:%M:%S")) <= tools.get_date():
            check_log()

        line = "[{0}] {1}".format(tools.get_date(formatted=True), msg)
        line = line.rstrip('\r\n') + '\n'
        tools.write_to_file(CONFIG.WIZLOG, line, mode='a')


def check_log():
    next = tools.get_date(days=1, formatted=True)
    lines = tools.read_from_file(CONFIG.WIZLOG).split('\n')

    if CONFIG.CLEANWIZLOGBY == '0':  # By Days
        keep = tools.get_date(days=-CONFIG.MAXWIZDATES[int(float(CONFIG.CLEANDAYS))])
        x = 0
        for line in lines:
            if str(line[1:11]) >= str(keep):
                break
            x += 1
        newfile = lines[x:]
        tools.write_to_file(CONFIG.WIZLOG, '\n'.join(newfile))
    elif CONFIG.CLEANWIZLOGBY == '1':  # By Size
        maxsize = CONFIG.MAXWIZSIZE[int(float(CONFIG.CLEANSIZE))]*1024
        if os.path.getsize(CONFIG.WIZLOG) >= maxsize:
            start = int(len(lines)/2)
            newfile = lines[start:]
            tools.write_to_file(CONFIG.WIZLOG, '\n'.join(newfile))
    elif CONFIG.CLEANWIZLOGBY == '2':  # By Lines
        maxlines = CONFIG.MAXWIZLINES[int(float(CONFIG.CLEANLINES))]
        if len(lines) > maxlines:
            start = len(lines) - int(maxlines/2)
            newfile = lines[start:]
            tools.write_to_file(CONFIG.WIZLOG, '\n'.join(newfile))
    CONFIG.set_setting('nextwizcleandate', next)


def log_notify(title, message, times=2000, icon=CONFIG.ADDON_ICON, sound=False):
    dialog = xbmcgui.Dialog()
    dialog.notification(title, message, icon, int(times), sound)


def grab_log(file=False, old=False, wizard=False):
    if wizard:
        if os.path.exists(CONFIG.WIZLOG):
            return CONFIG.WIZLOG if file else tools.read_from_file(CONFIG.WIZLOG)
        else:
            return False
                
    logsfound = []

    for item in [file for file in os.listdir(CONFIG.LOGPATH) if os.path.basename(file).startswith('kodi')]:
        if item.endswith('.log'):
            if (old and 'old' in item) or (not old and 'old' not in item):
                logsfound.append(os.path.join(CONFIG.LOGPATH, item))

    if len(logsfound) > 0:
        logsfound.sort(key=lambda f: os.path.getmtime(f))
        if file:
            return logsfound[-1]
        else:
            return tools.read_from_file(logsfound[-1])
    else:
        return False


def upload_log():
    files = get_files()
    for item in files:
        filetype = item[0]
        if filetype == 'log':
            log = os.path.basename(grab_log(file=True))
            name = log if log else "kodi.log"
            error = "Error al publicar el {0} archivo".format(name)
        elif filetype == 'oldlog':
            log = os.path.basename(grab_log(file=True, old=True))
            name = log if log else "kodi.old.log"
            error = "Error al publicar el {0} archivo".format(name)
        elif filetype == 'wizlog':
            name = "wizard.log"
            error = "Error al publicar el {0} archivo".format(name)
        elif filetype == 'crashlog':
            name = "crash log"
            error = "Error al publicar el archivo de registro de fallos"
        succes, data = read_log(item[1])
        if succes:
            content = clean_log(data)
            succes, result = post_log(content, name)
            if succes:
                msg = "Publique esta URL o escanee el código QR para su [COLOR {0}]{1}[/COLOR]," \
                      " junto con una descripción del problema:[CR][COLOR {2}]{3}[/COLOR]".format(
                    CONFIG.COLOR1, name, CONFIG.COLOR1, result)

                # if len(self.email) > 5:
                # em_result, em_msg = self.email_Log(self.email, result, name)
                # if em_result == 'message':
                # msg += "[CR]%s" % em_msg
                # else:
                # msg += "[CR]Email ERROR: %s" % em_msg

                show_result(msg, result)
            else:
                show_result('{0}[CR]{1}'.format(error, result))
        else:
            show_result('{0}[CR]{1}'.format(error, result))


def get_files():
    logfiles = []
    kodilog = grab_log(file=True)
    old = grab_log(file=True, old=True)
    wizard = False if not os.path.exists(CONFIG.WIZLOG) else CONFIG.WIZLOG
    if kodilog:
        if os.path.exists(kodilog):
            logfiles.append(['log', kodilog])
        else:
            show_result("No se encontró ningún archivo de registro")
    else:
        show_result("No se encontró ningún archivo de registro")
    if CONFIG.KEEPOLDLOG:
        if old:
            if os.path.exists(old):
                logfiles.append(['oldlog', old])
            else:
                show_result("No se encontró ningún archivo de registro antiguo")
        else:
            show_result("No se encontró ningún archivo de registro antiguo")
    if CONFIG.KEEPWIZLOG:
        if wizard:
            logfiles.append(['wizlog', wizard])
        else:
            show_result("No se encontró ningún archivo de registro del wizard")
    if CONFIG.KEEPCRASHLOG:
        crashlog_path = ''
        items = []
        if xbmc.getCondVisibility('system.platform.osx'):
            crashlog_path = os.path.join(os.path.expanduser('~'), 'Library/Logs/DiagnosticReports/')
            filematch = 'Kodi'
        elif xbmc.getCondVisibility('system.platform.ios'):
            crashlog_path = '/var/mobile/Library/Logs/CrashReporter/'
            filematch = 'Kodi'
        elif tools.platform() == 'linux':
            # not 100% accurate (crashlogs can be created in the dir kodi was started from as well)
            crashlog_path = os.path.expanduser('~')
            filematch = 'kodi_crashlog'
        elif tools.platform() == 'windows':
            log("Los registros de fallos de Windows no son compatibles, desactive esta opción en la configuración del add-on")
        elif tools.platform() == 'android':
            log("Los registros de fallos de Android no son compatibles, desactive esta opción en la configuración del add-on")
        if crashlog_path and os.path.isdir(crashlog_path):
            dirs, files = xbmcvfs.listdir(crashlog_path)
            for item in files:
                if filematch in item and os.path.isfile(os.path.join(crashlog_path, item)):
                    items.append(os.path.join(crashlog_path, item))
                    items.sort(key=lambda f: os.path.getmtime(f))
                    lastcrash = items[-1]
                    logfiles.append(['crashlog', lastcrash])
        if len(items) == 0:
            log("No se encontró ningún archivo de registro de fallos")
    return logfiles


def read_log(path):
    try:
        lf = xbmcvfs.File(path)
        content = lf.read()
        if content:
            return True, content
        else:
            log('el archivo está vacío')
            return False, "El Archivo está Vacío"
    except Exception as e:
        log('imposible leer el archivo: {0}'.format(e))
        return False, "Imposible Leer el Archivo"


def clean_log(content):
    for pattern, repl in REPLACES:
        content = re.sub(pattern, repl, content)
        return content


def post_log(data, name):
    params = {'poster': CONFIG.BUILDERNAME, 'content': data, 'syntax': 'text', 'expiration': 'week'}
    params = urlencode(params)

    try:
        page = LogURLopener().open(URL, params)
    except Exception as e:
        a = 'error al conectar con el servidor'
        log("{0}: {1}".format(a, str(e)), level=xbmc.LOGERROR)
        return False, a

    try:
        page_url = page.url.strip()
        # copy_to_clipboard(page_url)
        log("URL para {0}: {1}".format(name, page_url))
        return True, page_url
    except Exception as e:
        a = 'no se puede recuperar la URL pegada'
        log("{0}: {1}".format(a, str(e)), level=xbmc.LOGERROR)
        return False, a


# CURRENTLY NOT IN USE
def copy_to_clipboard(txt):
    import subprocess

    platform = tools.platform()
    if platform == 'windows':
        try:
            cmd = 'echo ' + txt.strip() + '|clip'
            return subprocess.check_call(cmd, shell=True)
            pass
        except:
            pass
    elif platform == 'linux':
        try:
            from subprocess import Popen, PIPE

            p = Popen(['xsel', '-pi'], stdin=PIPE)
            p.communicate(input=txt)
        except:
            pass
    else:
        pass


# CURRENTLY NOT IN USE
# def email_log(email, results, file):
    # URL = 'http://aftermathwizard.net/mail_logs.php'
    # data = {'email': email, 'results': results, 'file': file, 'wizard': CONFIG.ADDONTITLE}
    # params = urlencode(data)

    # try:
        # result = LogURLopener().open(URL, params)
        # returninfo = result.read()
        # log(str(returninfo))
    # except Exception as e:
        # a = 'failed to connect to the server'
        # log("{0}: {1}".format(a, str(e)), level=xbmc.LOGERROR)
        # return False, a

    # try:
        # return True, "Emailing logs is currently disabled."
        # # js_data = json.loads(returninfo)

        # # if 'type' in js_data:
            # # return js_data['type'], str(js_data['text'])
        # # else:
            # # return str(js_data)
    # except Exception as e:
        # log("ERROR: {0}".format(str(e)), level=xbmc.LOGERROR)
        # return False, "Error Sending Email."


class LogURLopener(FancyURLopener):
    version = '{0}: {1}'.format(CONFIG.ADDON_ID, CONFIG.ADDON_VERSION)


def show_result(message, url=None):
    from resources.libs.gui import window

    dialog = xbmcgui.Dialog()

    if url:
        try:
            from resources.libs import qr
            
            fn = url.split('/')[-2]
            imagefile = qr.generate_code(url, fn)
            window.show_qr_code("loguploader.xml", imagefile, message)
            try:
                os.remove(imagefile)
            except:
                pass
        except Exception as e:
            log(str(e), xbmc.LOGINFO)
            confirm = dialog.ok(CONFIG.ADDONTITLE, "[COLOR %s]%s[/COLOR]" % (CONFIG.COLOR2, message))
    else:
        confirm = dialog.ok(CONFIG.ADDONTITLE, "[COLOR %s]%s[/COLOR]" % (CONFIG.COLOR2, message))


def view_log_file():
    from resources.libs.gui import window

    mainlog = grab_log(file=True)
    oldlog = grab_log(file=True, old=True)
    wizlog = grab_log(file=True, wizard=True)
    
    choices = []
    logfiles = {'mainlog': "View {0}".format(os.path.basename(mainlog)), 'oldlog': "View {0}".format(os.path.basename(oldlog)), 'wizlog': "View {0}".format(os.path.basename(wizlog))}
    
    which = 0
    logtype = oldlog
    msg = grab_log(old=True)
    
    if mainlog:
        choices.append(logfiles['mainlog'])
    if oldlog:
        choices.append(logfiles['oldlog'])
    if wizlog:
        choices.append(logfiles['wizlog'])

    dialog = xbmcgui.Dialog()

    if len(choices) > 0:
        which = dialog.select(CONFIG.ADDONTITLE, choices)
        if which == -1:
            log_notify('[COLOR {0}]Ver Registro[/COLOR]'.format(CONFIG.COLOR1),
                       '[COLOR {0}]Ver Registro Cancelado![/COLOR]'.format(CONFIG.COLOR2))
            return
        elif which == 0:
            logtype = mainlog
        elif which == 1:
            logtype = oldlog
        elif which == 2:
            logtype = wizlog
    elif len(choices) == 0:
        log_notify('[COLOR {0}]Ver Registro[/COLOR]'.format(CONFIG.COLOR1),
                   '[COLOR {0}]No se Encontró Ningún Archivo de Registro![/COLOR]'.format(CONFIG.COLOR2))
        return
    else:
        if mainlog:
            logtype = mainlog
        elif oldlog:
            logtype = oldlog
        elif wizlog:
            logtype = wizlog

    window.show_log_viewer("[B][COLOR azure]Ver Archivo de Registro[/COLOR][/B]", log_file=logtype, ext_buttons=True)


def swap_debug():
    import threading

    new = '"debug.showloginfo"'
    query = '{{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{{"setting":{0}}}, "id":1}}'.format(new)
    response = xbmc.executeJSONRPC(query)
    log("Configuración de Obtención del Registro de Depuración: {0}".format(str(response)))
    if 'false' in response:
        value = 'true'
        threading.Thread(target=_dialog_watch).start()
        xbmc.sleep(200)
        query = '{{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{{"setting":{0},"value":{1}}}, "id":1}}'.format(
            new, value)
        response = xbmc.executeJSONRPC(query)
        log_notify(CONFIG.ADDONTITLE,
                           '[COLOR {0}]Registro de Depuración:[/COLOR] [COLOR {1}]Activado[/COLOR]'.format(CONFIG.COLOR1,
                                                                                                   CONFIG.COLOR2))
        log("Configuración del Conjunto de Registros de Depuración: {0}".format(str(response)))
    elif 'true' in response:
        value = 'false'
        threading.Thread(target=_dialog_watch).start()
        xbmc.sleep(200)
        query = '{{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{{"setting":{0},"value":{1}}}, "id":1}}'.format(
            new, value)
        response = xbmc.executeJSONRPC(query)
        log_notify(CONFIG.ADDONTITLE,
                   '[COLOR {0}]Registro de Depuración:[/COLOR] [COLOR {1}]Desactivado[/COLOR]'.format(CONFIG.COLOR1,
                                                                                         CONFIG.COLOR2))
        log("Configuración del Conjunto de Registros de Depuración: {0}".format(str(response)))


def _dialog_watch():
    x = 0
    while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 100:
        x += 1
        xbmc.sleep(100)

    if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
        xbmc.executebuiltin('SendClick(yesnodialog, 11)')
        return True
    else:
        return False


def error_list(file):
    errors = []
    b = tools.read_from_file(file).replace('\n', '[CR]').replace('\r', '')

    match = re.compile("-->Python callback/script returned the following error<--(.+?)-->End of Python script error report<--").findall(b)
    for item in match:
        errors.append(item)
    return errors


def error_checking(log=None, count=None, last=None):
    errors = []
    error1 = []
    error2 = []
    if log is None:
        curr = grab_log(file=True)
        old = grab_log(file=True, old=True)
        if not old  and not curr:
            if count is None:
                log_notify('[COLOR {0}]Ver Registro de Errores[/COLOR]'.format(CONFIG.COLOR1),
                           '[COLOR {0}]No se Encontró Ningún Archivo de Registro![/COLOR]'.format(CONFIG.COLOR2))
                return
            else:
                return 0
        if curr:
            error1 = error_list(curr)
        if old:
            error2 = error_list(old)
        if len(error2) > 0:
            for item in error2:
                errors = [item] + errors
        if len(error1) > 0:
            for item in error1:
                errors = [item] + errors
    else:
        error1 = error_list(log)
        if len(error1) > 0:
            for item in error1:
                errors = [item] + errors

    if count is not None:
        return len(errors)
    elif len(errors) > 0:
        from resources.libs.gui import window
        
        if last is None:
            i = 0
            string = ''
            for item in errors:
                i += 1
                string += "[B][COLOR red]ERROR NÚMERO {0}:[/B][/COLOR] [COLOR silver]{1}[/COLOR]\n".format(str(i), item.replace(CONFIG.HOME, '/').replace('                                        ', ''))
            window.show_log_viewer("[B][COLOR azure]Visualización de Errores en el Registro[/COLOR][/B]", string)
        else:
           string = "[B][COLOR red]Último Error en el Registro:[/B][/COLOR] [COLOR teal]{0}[/COLOR]\n".format(errors[0].replace(CONFIG.HOME, '/').replace('                                        ', ''))
           window.show_log_viewer("[B][COLOR azure]Visualización del Último Error en el Registro[/COLOR][/B]", string)

    else:
        log_notify('[COLOR {0}]Ver Error de Registro[/COLOR]'.format(CONFIG.COLOR1),
                   '[COLOR {0}]No se encontraron errores![/COLOR]'.format(CONFIG.COLOR2))

