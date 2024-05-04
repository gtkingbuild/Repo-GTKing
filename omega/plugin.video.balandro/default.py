# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urllib2
else:
    import urllib.error as urllib2


import os

from platformcode import config, logger, platformtools, updater
from core.item import Item

from platformcode.config import WebErrorException


logger.info('[COLOR blue]Starting with %s[/COLOR]' % sys.argv[1])

# ~ Obtener parámetros de lo que hay que ejecutar

if sys.argv[2]:
    item = Item().fromurl(sys.argv[2])
else:
    item = Item(channel='mainmenu', action='mainlist')

sys.path.append(os.path.join(config.get_runtime_path(), 'lib'))


# ~ Establecer si channel es un canal web o un módulo

tipo_channel = ''

if item.channel == '' or item.action == '':
    logger.info('Empty channel/action, nothing to do')

else:
    # ~ channel puede ser un canal web o un módulo
    path = os.path.join(config.get_runtime_path(), 'channels', item.channel + ".py")
    if os.path.exists(path):
        tipo_channel = 'channels.'
    else:
        path = os.path.join(config.get_runtime_path(), 'modules', item.channel + ".py")
        if os.path.exists(path):
            tipo_channel = 'modules.'
        else:
            logger.error('Channel/Module not found, nothing to do')


# ~ Ejecutar según los parámetros recibidos

if tipo_channel != '':
    try:
        canal = __import__(tipo_channel + item.channel, fromlist=[''])

        # ~ findvideos se considera reproducible y debe acabar haciendo play (o play_fake en su defecto)
        if item.action == 'findvideos':
            if hasattr(canal, item.action):
                itemlist = canal.findvideos(item)
            else:
                from core import servertools
                itemlist = servertools.find_video_items(item)

            platformtools.play_from_itemlist(itemlist, item)

        else:
            # ~ search pide el texto a buscar antes de llamar a la rutina del canal (pasar item.buscando para no mostrar diálogo)
            if item.action == 'search':
                if item.buscando != '':
                    tecleado = item.buscando
                else:
                    last_search = config.get_last_search(item.search_type)

                    search_type = ''

                    if item.search_type == 'movie': search_type = 'para [COLOR yellow]Películas[/COLOR]'
                    elif item.search_type == 'tvshow': search_type = 'para [COLOR yellow]Series[/COLOR]'
                    elif item.search_type == 'documentary': search_type = 'para [COLOR yellow]Documentales[/COLOR]'
                    elif item.search_type == 'person': search_type = 'para [COLOR yellow]Personas[/COLOR]'

                    elif item.search_special == 'anime': search_type = 'para [COLOR yellow]Animes[/COLOR]'
                    elif item.search_special == 'dorama': search_type = 'para [COLOR yellow]Doramas[/COLOR]'

                    tecleado = platformtools.dialog_input(last_search, 'Texto a buscar ' + search_type)

                if tecleado is not None and tecleado != '':
                    itemlist = canal.search(item, tecleado)
                    if item.buscando == '': config.set_last_search(item.search_type, tecleado)
                else:
                    itemlist = []
                    # ~ (desactivar si provoca ERROR: GetDirectory en el log)
                    item.folder = False
                    itemlist = False

            # ~ cualquier otra acción se ejecuta en el canal, y se renderiza si devuelve una lista de items
            else:
                if hasattr(canal, item.action):
                    func = getattr(canal, item.action)
                    itemlist = func(item)
                else:
                    # ~ Si item.folder kodi espera un listado
                    logger.info('Action not found in channel')
                    itemlist = [] if item.folder else False

            if type(itemlist) == list:
                logger.info('renderizar itemlist')
                platformtools.render_items(itemlist, item)

            elif itemlist == None:
                # ~ Si kodi espera un listado (desactivar si provoca ERROR: GetDirectory en el log)
                logger.info('sin renderizar')
                platformtools.render_no_items()

            elif itemlist == True:
                logger.info('El canal ha ejecutado correctamente una acción que no devuelve ningún listado.')

            elif itemlist == False:
                logger.info('El canal ha ejecutado una acción que no devuelve ningún listado.')

    except urllib2.URLError as e:
        import traceback
        logger.error(traceback.format_exc())

        # ~ Grab inner and third party errors
        if hasattr(e, 'reason'):
            logger.error("Razon del error, codigo: %s | Razon: %s" % (str(e.reason[0]), str(e.reason[1])))
            texto = "No se puede conectar con el servidor ó con el sitio web"
            platformtools.dialog_ok(config.__addon_name, texto)

        # ~ Grab server response errors
        elif hasattr(e, 'code'):
            logger.error("Codigo de error HTTP : %d" % e.code)
            platformtools.dialog_ok(config.__addon_name, "El sitio web no funciona correctamente (error http %d)" % e.code)

    except WebErrorException as e:
        import traceback
        logger.error(traceback.format_exc())

        # ~ Ofrecer buscar en otros canales o en el mismo canal, si está activado en la configuración
        if item.contentType in ['movie', 'tvshow', 'season', 'episode'] and config.get_setting('tracking_weberror_dialog', default=True):
            if item.action == 'findvideos': platformtools.play_fake()

            item_search = platformtools.dialogo_busquedas_por_fallo_web(item)
            if item_search is not None:
                platformtools.itemlist_update(item_search)

        else:
            try: last_ver = updater.check_addon_version()
            except: last_ver = True

            if not last_ver: last_ver = '[I](desfasada)[/I]'
            else: last_ver = ''

            release = '[COLOR goldenrod][B]' + config.get_addon_version().replace('.fix', '-Fix') + str(last_ver) + ' '

            platformtools.dialog_ok(release + '[COLOR red][B]Error en el canal [COLOR yellow]' + item.channel.capitalize() + '[/B][/COLOR]', 
                                    '[COLOR yellowgreen][B]La web asociada a este canal, parece no estar disponible[/B][/COLOR], puede volver a intentarlo pasados unos minutos, y si el problema persiste compruebe mediante un navegador de internet la web: [COLOR cyan][B]%s[/B][/COLOR]' % (e) )

    except:
        import traceback
        logger.error(traceback.format_exc())

        try: last_ver = updater.check_addon_version()
        except: last_ver = True

        if not last_ver: last_ver = '[I](desfasada)[/I]'
        else: last_ver = ''

        release = '[COLOR goldenrod][B]' + config.get_addon_version().replace('.fix', '-Fix') + str(last_ver) + ' '

        if not item.channel in ['mainmenu', 'actions', 'domains', 'downloads', 'favoritos', 'filmaffinitylists', 'filters', 'generos', 'groups', 'helper', 'proxysearch', 'search', 'submnuctext', 'submnuteam', 'tester', 'tmdblists', 'tracking']:
            platformtools.dialog_ok(release + ' [COLOR red]Error inesperado en [COLOR yellow]' + item.channel.capitalize() + '[/B][/COLOR]',
                                    '[COLOR moccasin][B]Quizás puede deberse a un fallo de conexión[/B][/COLOR], [COLOR cyan][B]ó que la web asociada a este canal ha variado su estructura[/B][/COLOR], ó bien ser un error interno del Add-On. [COLOR yellowgreen][B]Para saber más detalles, consulta el fichero Log de su Media Center.[/B][/COLOR]')
        else:
            platformtools.dialog_ok(release + '[COLOR red][B]Error inesperado en [COLOR gold]' + item.channel.capitalize() + '[/B][/COLOR]',
                                    '[COLOR moccasin][B]Podría estar corrupto su fichero de Ajustes de Balandro[/B][/COLOR], de ser así, [COLOR cyan][B]pruebe a Re-Instalar el Add-On[/B][/COLOR], ó bien ser un error interno del Add-On/Modulo. [COLOR yellowgreen][B]Para saber más detalles, consulta el fichero Log de su Media Center.[/B][/COLOR]')


logger.info('[COLOR blue]Ending with %s[/COLOR]' % sys.argv[1])
