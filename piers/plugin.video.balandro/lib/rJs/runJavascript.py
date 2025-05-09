## SJR : Simple Javascript Runner 0.2 ##
# 1) Filter:
# - Remove from Js code to run the key words 'let' y "const" to maximize JS compatibility
# - Replace some browser DOM functions using our lib.js (for now: btoa(), window.btoa(), atob(), window.atob())
#   For more functions check (and translate to more standard JS) JS on: https://github.com/jsdom/jsdom
#   It could be interesting including part of the DOMJs library: https://github.com/jsdom/jsdom
# 2) How to use:
# - Once the JS lib is merged with the Js code to run it is launched no Js2Py

import os

import js2py
class runJs:
    def __init__(self):
        pass
    def __removeParts(self, strJs, parts):
        ret = strJs
        for part in parts:
            for prefix in ['\t', '\r', '\n', ' ', ';']:
                ret = ret.replace(prefix + part, prefix)
            if ret.startswith(part):
                ret = ret[len(part):]
        return ret
    def __filterJsFile(self, strJs, strictFilter):
        if strictFilter:
            ret = self.__removeParts(strJs, ['let ', 'const '])
        else:
            ret = strJs
        if '${' in ret and '`' in ret:
            raise Exception('\n\n# Error! Not supported by ECMA 5.1.: You should replace your dollar-variables for their values.\n# Workaround example:   `${a}2${b}`   could become the string   a+"2"+b   ')
        elif '`' in ret:
            raise Exception('\n\n# Error! Not supported by ECMA 5.1.: Replace your characters "`" by "\'" or "\""')
        else:
            return ret
    ## Run JS String ##
    def runJsString(self, jsString, strictFilter):
        libJs = ''
        with open(os.path.dirname(__file__) + '/lib.js', 'r') as fileLib:
            libJs = fileLib.read()
            dataJs = self.__filterJsFile(jsString, strictFilter)
            bb = libJs + dataJs
            return js2py.eval_js(bb)
    ## Run JS file ##
    def runJsFile(self, jsFilepath, strictFilter):
        with open(jsFilepath, 'r') as fileJs:
            jsString = fileJs.read()
            return self.runJsString(jsString, strictFilter)

## Use example
# Example 1: Run JS existing file
#   print(runJavascript.runJs().runJsFile('js.js', True))
# Example 2: Run JS string
#   print(runJavascript.runJs().runJsString('var a = "Hello World"', True))
