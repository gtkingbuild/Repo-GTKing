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

import xbmcgui

import os

from resources.libs.common.config import CONFIG


def generate_code(url, filename):
    import segno

    if not os.path.exists(CONFIG.QRCODES):
        os.makedirs(CONFIG.QRCODES)
    imagefile = os.path.join(CONFIG.QRCODES, '{0}.png'.format(filename))
    generated_qr = segno.make(url)
    generated_qr.save(imagefile, scale=10)
    return imagefile


def create_code():
    from resources.libs.common import tools

    dialog = xbmcgui.Dialog()

    url = tools.get_keyboard('', "{0}: Inserte la URL del Código QR.".format(CONFIG.ADDONTITLE))
    response = tools.open_url(url, check=True)
    
    if not response:
        if not dialog.yesno(CONFIG.ADDONTITLE,
                                "[COLOR {0}]Parece que la URL que ingresó no es válida o no funciona. Le gustaría crearla de todos modos?[/COLOR]".format(CONFIG.COLOR2)
                                +'\n'+"[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, url),
                                yeslabel="[B][COLOR red]Sí, Crear[/COLOR][/B]",
                                nolabel="[B][COLOR cyan]No, Cancelar[/COLOR][/B]"):
            return
    name = tools.get_keyboard('', "{0}: Inserte el nombre del Código QR.".format(CONFIG.ADDONTITLE))
    name = "QR_Code_{0}".format(tools.id_generator(6)) if name == "" else name
    image = generate_code(url, name)
    dialog.ok(CONFIG.ADDONTITLE,
                  "[COLOR {0}]La imagen del Código QR se ha creado y se encuentra en el directorio addon_data:[/COLOR]".format(CONFIG.COLOR2)
                  +'\n'+"[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, image.replace(CONFIG.HOME, '')))
