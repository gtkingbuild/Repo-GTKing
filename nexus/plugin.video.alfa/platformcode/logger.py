# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Logger (kodi)
# --------------------------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int
    
import inspect

import xbmc
import xbmcaddon

__settings__ = xbmcaddon.Addon(id="plugin.video.alfa")
loggeractive = __settings__.getSetting("debug")
if loggeractive == "true": loggeractive = True
elif loggeractive == "false":  loggeractive = False


def encode_log(message=""):
    
    # Unicode to utf8
    if isinstance(message, unicode):
        message = message.encode("utf8")
        if PY3: message = message.decode("utf8")

    # All encodings to utf8
    elif not PY3 and isinstance(message, str):
        message = unicode(message, "utf8", errors="replace").encode("utf8")
    
    # Bytes encodings to utf8
    elif PY3 and isinstance(message, bytes):
        message = message.decode("utf8")

    # Objects to string
    else:
        message = str(message)

    return message


def get_caller(message=None):
    
    if message and isinstance(message, unicode):
        message = message.encode("utf8")
        if PY3: message = message.decode("utf8")
    elif message and PY3 and isinstance(message, bytes):
        message = message.decode("utf8")
    elif message and not PY3:
        message = unicode(message, "utf8", errors="replace").encode("utf8")
    elif message:
        message = str(message) 
    
    module = inspect.getmodule(inspect.currentframe().f_back.f_back)

    if module == None:
        module = "None"
    else:
        module = module.__name__

    function = inspect.currentframe().f_back.f_back.f_code.co_name

    if module == "__main__":
        module = "alfa"
    else:
        module = "alfa." + module
    if message:
        if module not in message:
            if function == "<module>":
                return module + " " + message
            else:
                return module + " [" + function + "] " + message
        else:
            return message
    else:
        if function == "<module>":
            return module
        else:
            return module + "." + function


def info(texto="", force=False):
    if loggeractive or force:
        if PY3:
            xbmc.log(get_caller(encode_log(texto)), xbmc.LOGINFO)
        else:
            xbmc.log(get_caller(encode_log(texto)), xbmc.LOGNOTICE)


def debug(texto="", force=False):
    if loggeractive or force:
        texto = "    [" + get_caller() + "] " + encode_log(texto)

        if PY3:
            xbmc.log("######## DEBUG #########", xbmc.LOGINFO)
            xbmc.log(texto, xbmc.LOGINFO)
        else:
            xbmc.log("######## DEBUG #########", xbmc.LOGNOTICE)
            xbmc.log(texto, xbmc.LOGNOTICE)


def error(texto="", force=False):
    texto = "    [" + get_caller() + "] " + encode_log(texto)

    xbmc.log("######## ERROR #########", xbmc.LOGERROR)
    xbmc.log(texto, xbmc.LOGERROR)


class WebErrorException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
