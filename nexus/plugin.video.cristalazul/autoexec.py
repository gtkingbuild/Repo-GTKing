# -*- coding: UTF-8 -*-


#######################################################################
#
# autoexec cristalazul
# ----------------------------------------------------------------------------
# Modificación eliminar indigo del sistema. Proveedor: CTA
# ----------------------------------------------------------------------------
#######################################################################

import shutil
import six
from kodi_six import xbmc,xbmcvfs,xbmcgui
TRANSLATEPATH = xbmc.translatePath if six.PY2 else xbmcvfs.translatePath

try:
    addon_path2 = TRANSLATEPATH(('special://home/addons/plugin.video.blackghost'))
    addon_path2 = six.ensure_str(addon_path2)
    shutil.rmtree(addon_path2, ignore_errors=True)
except:
    pass
	
instalado = xbmc.getCondVisibility('System.HasAddon(script.module.resolveurl)')
if instalado==0:
    xbmc.executebuiltin('InstallAddon(script.module.resolveurl)')
instalado2 = xbmc.getCondVisibility('System.HasAddon(plugin.program.kodispainwizard)')
if instalado2==1:
    xbmcgui.Dialog().ok('[COLOR aqua]CRISTAL AZUL[/COLOR]',
                'Este es un software [COLOR red][B]gratuito[/B][/COLOR][CR][COLOR red][B]Pero no se permite[/B][/COLOR] '
                'su distribuicion preinstalada en ningun tipo de dispositivo ni tampoco su inclusion total o parcial en '
                'cualquier paquete de software y/o hardware por el que el usuario final le pidan [COLOR red][B]pagar o hacer'
                ' una donacion[/B][/COLOR], por su adquisicion, por su uso o por recibir asistencia.[CR]Si cree que '
                'alguna de estas normas no se esta¡ cumpliendo pongase en contacto con nosotros.')