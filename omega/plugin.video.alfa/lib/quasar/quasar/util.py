import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import platform
import xbmc
import xbmcgui
from quasar.logger import log
from quasar.osarch import PLATFORM
from quasar.addon import ADDON, ADDON_NAME, ADDON_ICON


def notify(message, header=ADDON_NAME, time=5000, image=ADDON_ICON):
    sound = ADDON.getSetting('do_not_disturb') == 'false'
    dialog = xbmcgui.Dialog()
    return dialog.notification(toUtf8(header), toUtf8(message), toUtf8(image), time, sound)

def getLocalizedLabel(label):
    try:
        if "LOCALIZE" not in label:
            return label
        if ";;" not in label and label.endswith(']'):
            return getLocalizedString(int(label[9:-1]))
        else:
            parts = label.split(";;")
            translation = getLocalizedString(int(parts[0][9:14]))
            for i, part in enumerate(parts[1:]):
                if part[0:8] == "LOCALIZE":
                    parts[i + 1] = getLocalizedString(int(part[9:14]))

            if not PY3:
                return (translation.decode('utf-8', 'replace') % tuple(parts[1:])).encode('utf-8', 'ignore')
            else:
                return translation % tuple(parts[1:])
    except:
        return label

def getLocalizedString(stringId):
    try:
        if not PY3:
            return ADDON.getLocalizedString(stringId).encode('utf-8', 'ignore')
        else:
            return ADDON.getLocalizedString(stringId)
    except:
        return stringId

def toUtf8(string):
    if isinstance(string, unicode):
        string = string.encode("utf8", 'ignore')
        if PY3: string = string.decode("utf8")
    elif PY3 and isinstance(string, bytes):
        string = string.decode("utf8")
    return string

def system_information():
    build = xbmc.getInfoLabel("System.BuildVersion")
    log.info("System information: %(os)s_%(arch)s %(version)s" % PLATFORM)
    log.info("Kodi build version: %s" % build)
    log.info("OS type: %s" % platform.system())
    log.info("uname: %s" % repr(platform.uname()))
    return PLATFORM

def getShortPath(path):
    if PLATFORM["os"] == "windows":
        return getWindowsShortPath(path)
    return path

def getWindowsShortPath(path):
    try:
        import ctypes
        import ctypes.wintypes

        ctypes.windll.kernel32.GetShortPathNameW.argtypes = [
            ctypes.wintypes.LPCWSTR,  # lpszLongPath
            ctypes.wintypes.LPWSTR,  # lpszShortPath
            ctypes.wintypes.DWORD  # cchBuffer
        ]
        ctypes.windll.kernel32.GetShortPathNameW.restype = ctypes.wintypes.DWORD

        buf = ctypes.create_unicode_buffer(1024)  # adjust buffer size, if necessary
        ctypes.windll.kernel32.GetShortPathNameW(path, buf, len(buf))

        return buf.value
    except:
        return path
