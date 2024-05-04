import xbmc
import sys
import platform

def get_platform():
    build = xbmc.getInfoLabel("System.BuildVersion")
    kodi_version = int(build.split()[0][:2])
    ret = {
        "auto_arch": sys.maxsize > 2 ** 32 and "64-bit" or "32-bit",
        "arch": sys.maxsize > 2 ** 32 and "x64" or "x86",
        "os": "",
        "version": platform.release(),
        "kodi": kodi_version,
        "build": build
    }
    if xbmc.getCondVisibility("system.platform.android"):
        ret["os"] = "android"
        if "arm" in platform.machine() or "aarch" in platform.machine():
            ret["arch"] = "arm"
            if "64" in platform.machine() and ret["auto_arch"] == "64-bit":
                ret["arch"] = "arm"
                #ret["arch"] = "x64"                #The binary is corrupted in install package
    elif xbmc.getCondVisibility("system.platform.linux"):
        ret["os"] = "linux"
        if "aarch" in platform.machine() or "arm64" in platform.machine():
            if xbmc.getCondVisibility("system.platform.linux.raspberrypi"):
                ret["arch"] = "armv7"
            elif ret["auto_arch"] == "32-bit":
                ret["arch"] = "armv7"
            elif ret["auto_arch"] == "64-bit":
                ret["arch"] = "arm64"
            elif platform.architecture()[0].startswith("32"):
                ret["arch"] = "arm"
            else:
                ret["arch"] = "arm64"
        elif "armv7" in platform.machine():
            ret["arch"] = "armv7"
        elif "arm" in platform.machine():
            ret["arch"] = "arm"
    elif xbmc.getCondVisibility("system.platform.xbox"):
        ret["os"] = "windows"
        ret["arch"] = "x64"
    elif xbmc.getCondVisibility("system.platform.windows"):
        ret["os"] = "windows"
        if platform.machine().endswith('64'):
            ret["arch"] = "x64"
    elif xbmc.getCondVisibility("system.platform.osx"):
        ret["os"] = "darwin"
        ret["arch"] = "x64"
    elif xbmc.getCondVisibility("system.platform.ios"):
        ret["os"] = "ios"
        ret["arch"] = "arm"
    return ret


PLATFORM = get_platform()
