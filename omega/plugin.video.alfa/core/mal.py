# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# mal
# ------------------------------------------------------------
# Proveedor de información de MyAnimeList mediante la API Jikan v3
# Utilizado para obtener datos de animes para la videoteca
# del addon, infoLabels y también para Kodi.
#
# Parte del código ha sido tomado de los scrapers existentes
# de TMDb y TVDb, crédito a quienes corresponda.
#
# ------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


from builtins import range
from builtins import object

import re
import time
import copy

from core import httptools
from core import scrapertools
from core.item import InfoLabels
from platformcode import config
from platformcode import logger

omal_global = None


def set_infoLabels(source, seek=True, include_hentai=False):
    """
        Dependiendo del tipo de source obtiene y establece los datos extras
        de animes o capítulos en los item.infoLabels

        @param source: Variable que contiene la información para establecer infoLabels
        @type source: list, item

        @param seek: Si es True, busca datos adicionales en myanimelist.net-
                     En caso contrario, obtiene los datos del propio Item.
        @type seek: bool

        @param include_hentai: Determina si se incluirá hentai (contenido +18) en la búsqueda
        @type include_hentai: bool

        @return: un número o lista de números con el resultado de las llamadas a set_infoLabels_item
        @rtype: int, list
    """
    logger.info()
    start_time = time.time()
    if isinstance(source, list):
        ret = set_infoLabels_itemlist(source, seek, include_hentai)
        logger.debug("Se han obtenido los datos de {} enlaces en {} segundos".format(len(source), time.time() - start_time))
    else:
        ret = set_infoLabels_item(source, seek, include_hentai)
        logger.debug("Se han obtenido los datos del enlace en {} segundos".format(time.time() - start_time))
    return ret


def set_infoLabels_itemlist(item_list, seek=False, include_hentai=False):
    """
        De manera concurrente, obtiene los datos de los items incluidos en la lista item_list.

        La API no tiene un límite definido, pero se recomiendan 2 peticiones por IP por segundo
        por lo que no se recomienda utillizar esta función para obtener datos generales de anime.
        Esto es, obtener datos de 20 pelis/animes/ovas a la vez, debido a que los tiempos de espera
        son equivalentes la mitad de items (ej. 20 items en 10 segundos) lo que alarga bastante los
        tiempos de espera para listar.

        @param item_list: listado de objetos Item que representan animes, temporadas o capítulos.
                        Las temporadas son tratadas como entradas/series individuales. El atributo infoLabels
                        de cada objeto Item sera modificado con los obtenidos de la web.
        @type item_list: list

        @param seek: Si es True hace una búsqueda en myanimelist.net para obtener los datos, en caso contrario
                    obtiene los datos del propio Item si existen.
        @type seek: bool

        @param include_hentai: Determina si se incluirá hentai (contenido +18) en la búsqueda (solo búsquedas por texto)
        @type include_hentai: bool

        @return: Una lista de números cuyo valor absoluto representa la cantidad de elementos incluidos en el
                atributo infoLabels de cada Item. Este número sera positivo si se han obtenido los datos desde
                myanimelist satisfactoriamente y negativo en caso contrario.
        @rtype: list
    """
    logger.info()
    import threading

    semaforo = threading.Semaphore(2)
    lock = threading.Lock()
    r_list = list()
    i = 0
    l_hilo = list()

    def sub_thread(_item, _i, _seek, _include_hentai):
        semaforo.acquire()
        ret = set_infoLabels_item(_item, _seek, _include_hentai, lock)
        semaforo.release()
        r_list.append((_i, _item, ret))

    for item in item_list:
        t = threading.Thread(target=sub_thread, args=(item, i, seek, include_hentai))
        t.start()
        i += 1
        l_hilo.append(t)

    # esperar q todos los hilos terminen
    for x in l_hilo:
        x.join()

    # Ordenar lista de resultados por orden de llamada para mantener el mismo orden q item_list
    r_list.sort(key=lambda i: i[0])

    # Reconstruir y devolver la lista solo con los resultados de las llamadas individuales
    return [ii[2] for ii in r_list]


def set_infoLabels_item(item, seek=True, include_hentai=False, lock=None):
    """
        Obtiene y fija (item.infoLabels) los datos extras de una serie, capitulo o pelicula.

        @param item: Objeto Item que representa un pelicula, serie o capitulo. El atributo infoLabels sera modificado
                    incluyendo los datos extras localizados.
        @type item: Item

        @param seek: Si es True hace una búsqueda en myanimelist.net para obtener los datos, en caso contrario
                    obtiene los datos del propio Item si existen.
        @type seek: bool

        @param include_hentai: Determina si se incluirá hentai (contenido +18) en la búsqueda (solo búsquedas por texto)
        @type include_hentai: bool

        @param lock: Para adquisición de threads al llamarse desde set_infoLabels_itemlist.

        @return: Una lista de números cuyo valor absoluto representa la cantidad de elementos incluidos en el
                atributo infoLabels de cada Item. Este número sera positivo si se han obtenido los datos desde
                myanimelist satisfactoriamente y negativo en caso contrario.
        @rtype: list
    """
    logger.info()

    #===========================================================================#
      #   NOTA IMPORTANTE: El contentType debe ser uno de los soportados      #
      #   por MyAnimeList para correcta asignación de infoLabels aquí         #
      #                                                                       #
      #   Estos son: "ova", "ona", "special", "tv", "movie".                  #
      #                                                                       #
      #   También se puede llamar sin especificar alguno válido (o ninguno)   #
      #   pero en esos casos se buscará sin contentType, pudiendo llevar      #
      #   a búsquedas un poco imprecisas. Esto afecta particularmente         #
      #   a las OVA/ONA que pueden ser tanto series como pelis                #
      #                                                                       #
      #   Cabe notar, que el contentType será reasignado a movie/tv en        #
      #   función de lo que se scrapee de MAL                                 #
    #===========================================================================#

    global omal_global

    tipos_busqueda_validos = ["ova", "ona", "special", "movie", "tv"]
    if item.contentType in tipos_busqueda_validos:
        tipo_busqueda = item.contentType
    elif item.contentType in ["tvshow"]:
        tipo_busqueda = "tv"
    else:
        tipo_busqueda = ""

    if tipo_busqueda in ["tv"] or item.contentSerieName:
        texto_buscado = item.contentSerieName
    elif item.contentTitle:
        texto_buscado = item.contentTitle
    else:
        texto_buscado = item.title

    def __leer_datos(omal_aux):
        item.infoLabels = omal_aux.get_infoLabels(item.infoLabels)
        if item.infoLabels['thumbnail']:
            item.thumbnail = item.infoLabels['thumbnail']
        if item.infoLabels['fanart']:
            item.fanart = item.infoLabels['fanart']

    logger.info("seek: "+str(seek))
    if seek:
        # Estamos buscando datos de episodio o temporada
        if 'season' in item.infoLabels.keys():
            try:
                numtemporada = int(item.infoLabels['season'])
            except ValueError:
                logger.debug("El numero de temporada no es valido")
                return -1 * len(item.infoLabels)

            # Bloqueamos el thread
            if lock:
                lock.acquire()

            # Si aún no tenemos datos sobre el anime, buscamos
            if not omal_global or (item.infoLabels['mal_id'] and str(omal_global.result.get("mal_id")) != item.infoLabels['mal_id']) \
                               or (omal_global.texto_buscado and omal_global.texto_buscado != item.infoLabels['tvshowtitle']):
                if item.infoLabels.get('mal_id'):
                    omal_global = MAL(mal_id=item.infoLabels['mal_id'])
                else:
                    omal_global = MAL(texto_buscado=texto_buscado, tipo=tipo_busqueda, year=item.infoLabels['year'], include_hentai=include_hentai)

                __leer_datos(omal_global)

            # Si hay nº de episodio en el item, estamos buscando + info. de episodios
            if item.infoLabels.get('episode'):
                try:
                    episode = int(item.infoLabels['episode'])
                except ValueError:
                    logger.debug("El número de episodio (%s) no es valido" % repr(item.infoLabels['episode']))
                    return -1 * len(item.infoLabels)

                # Tenemos número de temporada y episodio válidos
                # Buscamos los datos del episodio
                item.infoLabels['mediatype'] = 'episode'
                episodio = omal_global.get_episodio(numtemporada, episode)

                if episodio:
                    # Actualizar datos
                    __leer_datos(omal_global)
                    item.infoLabels['title'] = episodio['episodio_titulo']
                    if episodio['episodio_air_date']:
                        item.infoLabels['aired'] = episodio['episodio_air_date']

                    return len(item.infoLabels)

            # Sino, estamos buscando datos de temporada. (Se pasa lo del anime porque datos de temporada pues no hay 🤷‍♂️)
            else:
                item.infoLabels['mediatype'] = 'season'
                temporada = omal_global.get_temporada(numtemporada)

                # Función heredada (tmdb)
                # Si tenemos datos de temporada, los asignamos a infoLabels
                if temporada:
                    __leer_datos(omal_global)
                    item.infoLabels['title'] = temporada['name']
                    if temporada['air_date']:
                        item.infoLabels['aired'] = temporada['air_date']
                    return len(item.infoLabels)

            # Liberamos el thread
            if lock and lock.locked():
                lock.release()
        # Estamos buscando datos generales de un anime
        else:
            # Bloqueamos el thread
            if lock:
                lock.acquire()

            omal = copy.copy(omal_global)
            # Búsqueda por ID de MyAnimeList
            if item.infoLabels.get('mal_id'):
                omal = MAL(mal_id=item.infoLabels['mal_id'])

            # No hay ID de MAL; buscamos por título
            if not item.infoLabels.get('mal_id'):
                # Búsqueda por tipo (si hay)
                if tipo_busqueda:
                    omal = MAL(texto_buscado=texto_buscado, tipo=tipo_busqueda, year=item.infoLabels['year'], include_hentai=include_hentai)
                # Búsqueda genérica (adivinemos)
                else:
                    omal = MAL(texto_buscado=texto_buscado, year=item.infoLabels.get('year', ''), include_hentai=include_hentai)

            if lock and lock.locked():
                lock.release()

            # Si hay resultado de búsqueda válido (hay ID de MAL), procesamos y retornamos de éxito
            if omal is not None and omal.get_id():
                __leer_datos(omal)
                return len(item.infoLabels)

            # Liberamos el thread
            if lock and lock.locked():
                lock.release()

    # La búsqueda falló en alguna parte. Esto no es común en MAL, verificar por si acaso.
    # item.contentType = item.infoLabels['mediatype']
    return -1 * len(item.infoLabels)


def find_and_set_infoLabels(item):
    logger.info()
    global omal_global
    mal_result = None

    tipos_busqueda_validos = ["ova", "ona", "special", "movie", "tv"]
    if item.contentType in tipos_busqueda_validos:
        tipo_busqueda = item.contentType
    elif item.contentType in ["tvshow"]:
        tipo_busqueda = "tv"
    else:
        tipo_busqueda = ""

    if tipo_busqueda in ["movie", "special"] or item.contentTitle:
        tipo_contenido = config.get_localized_string(70283)
        title = item.contentTitle
    elif tipo_busqueda in ["tv"] or item.contentSerieName:
        tipo_contenido = config.get_localized_string(60245)
        title = item.contentSerieName
    else:
        tipo_contenido = ""
        title = item.title

    # Si el titulo incluye el (año) se lo quitamos
    year = scrapertools.find_single_match(title, "^.+?\s*(\(\d{4}\))$")
    if year:
        title = title.replace(year, "").strip()
        item.infoLabels['year'] = year[1:-1]
    
    # Si no tenemos ID de MAL, buscamos por texto
    if not item.infoLabels.get("mal_id"):
        omal_global = MAL(texto_buscado=title, tipo=tipo_busqueda, year=item.infoLabels['year'])

    # Si hay ID de MAL pero no se ha buscado o el ID de MAL no coincide con el del resultado, buscamos por ID
    elif not omal_global or str(omal_global.result.get("mal_id")) != item.infoLabels['mal_id']:
        omal_global = MAL(id_mal=item.infoLabels['mal_id'])

    results = omal_global.get_results_list()

    # Si hay más de un resultado, preguntamos cuál es el correcto
    # Esta acción ocurrirá siempre que no se provea un mal_id (por el contenido relacionado que devuelve)
    if len(results) > 1:
        from platformcode import platformtools
        mal_result = platformtools.show_video_info(results, item=item, caption=config.get_localized_string(60247) % (title, tipo_contenido))

    # Si solo hay un resultado, lo seleccionamos
    elif len(results) > 0:
        mal_result = results[0]

    # Comprobaciones
    if isinstance(item.infoLabels, InfoLabels):
        infoLabels = item.infoLabels
    else:
        infoLabels = InfoLabels()

    if mal_result:
        infoLabels['mal_id'] = mal_result['mal_id']
        item.infoLabels = infoLabels
        set_infoLabels_item(item)
        return True

    else:
        item.infoLabels = infoLabels
        return False


# def get_nfo(item):
    # """
        # Devuelve la información necesaria para que se scrapee el resultado en la videoteca de kodi,

        # @param item: elemento que contiene los datos necesarios para generar la info
        # @type item: Item
        # @rtype: str
        # @return:
    # """

    # if "season" in item.infoLabels and "episode" in item.infoLabels:
        # info_nfo = "http://thetvdb.com/?tab=episode&seriesid=%s&seasonid=%s&id=%s\n" \
                   # % (item.infoLabels['tvdb_id'], item.season_id, item.episode_id)
    # else:
        # info_nfo = ', '.join(item.infoLabels['url_scraper']) + "\n"

    # return info_nfo


def completar_codigos(item):
    """
        Si es necesario comprueba si existen identificadores externos y si no existen los busca
        @param item: tipo item
        @type item: Item
    """
    # if not item.infoLabels['tmdb_id']:
        # listsources = [(item.infoLabels['tvdb_id'], "tvdb_id")]
        # if item.infoLabels['imdb_id']:
            # listsources.append((item.infoLabels['imdb_id'], "imdb_id"))

        # from core.tmdb import Tmdb
        # ob = Tmdb()

        # for external_id, external_source in listsources:
            # ob.search_by_id(id=external_id, source=external_source, tipo='tv')

            # item.infoLabels['tmdb_id'] = ob.get_id()
            # if item.infoLabels['tmdb_id']:
                # url_scraper = "https://www.themoviedb.org/tv/%s" % item.infoLabels['tmdb_id']
                # item.infoLabels['url_scraper'].append(url_scraper)
                # break
    pass

# ---------------------------------------------------------------------------------------------------------------
# class MAL:
#   Scraper de anime para el addon basado en el Api de https://jikan.moe/ (API no oficial de MyAnimeList)
#   version 0.1:
#       - Liberación inicial
#
#
# Usos:
#   Método constructor:
#       MAL(texto_buscado)
#           Parámetros:
#               texto_buscado:(str) Texto o parte del texto a buscar
#               (opcional) tipo: ("ova", "ona", "special", "tv", "movie", "music") El tipo de contenido. Por defecto "tv"
#               (opcional) year: (str) Año entre el que buscar (toma prioridad sobre fecha_inicial).
#               (opcional) fecha_inicial: (str) Buscar con esta fecha inicial en formato yyyy-mm-dd.
#               (opcional) fecha_final: (str) Buscar con esta fecha final en formato yyyy-mm-dd.
#               (opcional) estado: ("airing", "completed", "to_be_aired") Estado de transmisión.
#               (opcional) page: (int) Cuando hay muchos resultados para una búsqueda, estos se organizan por páginas.
#                                      Podemos cargar la página que deseemos, aunque por defecto siempre es la primera.
#               (opcional) include_hentai: (bool) Si se incluye contenido +18 (hentai) en los resultados. Solo aplica para búsquedas por texto.
#               (opcional) orden: ("title", "start_date", "end_date", "type", "id", "episodes", "score") Orden de los resultados (si hay más de 1).
#               (opcional) direccion: ("asc", "desc") Dirección (ascendente o descendente) para los resultados (si hay más de 1).
#
#           Return:
#               Devuelve un objeto MAL con la primera página del resultado de la búsqueda de 'texto_buscado'
#               en myanimelist.net. Cuantos más parámetros opcionales se incluyan, mas precisa sera la búsqueda.
#               Además, el objeto está inicializado con el primer resultado de la primera página de resultados.
#
#       MAL(mal_id=ID)
#           Parametros:
#               ID: (int o str) Identificador de un anime en MyAnimeList
#           Return:
#               Esta llamada devuelve un objeto MAL con el resultado asociado al identificador
#               correspondiente de MyAnimeList, o un resultado vacío si no existe
#
#
#   Metodos principales:
#       get_id(): Retorna un str con el identificador de MAL asociado al anime o una cadena vacía si no hubiese nada cargado
#       get_temporada(temporada): Obtiene un diccionario con datos especificos de la temporada.
#       get_episodio(temporada, capitulo): Obtiene un diccionario con datos especificos del episodio.
#       get_generos(): Retorna un str con la lista de géneros asociados al anime.
#
#
#   Otros metodos:
#       load_resultado(resultado, page): Cuando la busqueda devuelve varios resultados podemos seleccionar que resultado
#       concreto y de que pagina cargar los datos.
#
#   Limitaciones:
#       Se recomienda no exceder 2 peticiones por segundo (1 cada 0.5s) para evitar un bloqueo
# Informacion sobre la api : https://jikan.docs.apiary.io
# -------------------------------------------------------------------------------------------------------------------


class MAL(object):
    def __init__(self, **kwargs):
        # Variables iniciales
        self.page = kwargs.get('page', 1)
        self.orden = kwargs.get('orden', '')
        self.direccion_orden = kwargs.get('direccion', '')
        self.results = []
        self.result = {}
        self.list_episodes = {}
        self.episodes = {}
        self.temporada = {}

        self.busqueda_id = str(kwargs.get('mal_id', ''))
        self.busqueda_texto = re.sub('\[\\\?(B|I|COLOR)\s?[^\]]*\]', '', kwargs.get('texto_buscado', '')).strip() # Limpiamos el texto
        self.busqueda_tipo = kwargs.get('tipo', '')
        self.busqueda_fecha_inicio = scrapertools.find_single_match(kwargs.get('fecha_inicial', ''), '\d{4}-[0-1][0-9]-\d{2}') # Validamos la fecha estilo yyyy-mm-dd
        self.busqueda_fecha_fin = scrapertools.find_single_match(kwargs.get('fecha_final', ''), '\d{4}-[0-1][0-9]-\d{2}') # Validamos la fecha estilo yyyy-mm-dd
        self.busqueda_hentai = kwargs.get("include_hentai", False)
        if kwargs.get('year', ''):
            self.busqueda_fecha_inicio = "{}-01-01".format(kwargs.get('year', ''))
            self.direccion_orden ='desc'
        self.busqueda_estado = kwargs.get('estado', '')

        # Si hay, buscamos por id de MAL
        if self.busqueda_id:
            self.__by_id()

        # Sino, buscamos por texto
        elif self.busqueda_texto:
            self.__search(page=self.page)

        # Si no hay resultados de la búsqueda...
        if not self.result:
            if self.busqueda_id:
                msg = config.get_localized_string(70266) % ("{} en MyAnimeList".format(self.busqueda_id))
            else:
                msg = config.get_localized_string(70266) % ("'{}' en MyAnimeList".format(self.busqueda_texto))
            logger.debug(msg)

    @staticmethod
    def get_json(url):
        try:
            result = httptools.downloadpage(url, cookies=False, ignore_response_code=True, hide_infobox=True)
            res_headers = result.headers
            dict_data = result.json

            # Pasamos solo los resultados sin paginación
            if "results" in dict_data and isinstance(dict_data.get("results"), list) or isinstance(dict_data.get("results"), dict):
                dict_data = dict_data["results"]
            # Pasamos solo los episodios sin tags adicionales
            elif "episodes" in dict_data and isinstance(dict_data.get("episodes"), list) or isinstance(dict_data.get("episodes"), dict):
                dict_data = dict_data["episodes"]
            # Pasamos tal cual el dict e informamos de error en el log
            elif "error" in dict_data:
                logger.debug("\nError de MAL: {} {}".format(dict_data["error"], dict_data["message"]))

        except Exception as ex:
            # Hubo un error al obtener los datos, hay que ver si hubo cambios
            message = "An exception of type {} occured. Arguments:\n{}".format(type(ex).__name__, repr(ex.args))
            logger.error("Error en: {}".format(message))
            dict_data = {}

        return dict_data

    def __search(self, index_results=0, page=1):
        """
            Busca una anime dados ciertos parámetros.

            @param name: nombre a buscar
            @type name: str

            @param status: estado de emisión
            @type status: str

            @param type: tipo de contenido (ej. ova, ona, special, tv, movie, music)
            @type type: str

            @param start_date: fecha de primera emisión al formato yyyy-mm-dd
            @type start_date: str

            @param end_date: fecha de última emisión al formato yyyy-mm-dd
            @type end_date: str

            @param mal_id: id de MyAnimeList (si se conoce)
            @type mal_id: str
        """
        logger.info()
        result = {}

        # Buscamos según la información proporcionada
        if self.busqueda_texto:
            url = 'https://api.jikan.moe/v3/search/anime?q={}'.format(self.busqueda_texto)

            # Desactivado da mejores resultados
            # if self.busqueda_tipo == "movie":
                # url += '&type={}'.format(self.busqueda_tipo)

            if self.busqueda_hentai:
                url += '&rated=rx'

            if self.busqueda_estado:
                url += '&status={}'.format(self.busqueda_estado)

            # Dan problemas en ocasiones
            # if self.busqueda_fecha_inicio:
                # url += '&start_date={}'.format(self.busqueda_fecha_inicio)
            # if self.busqueda_fecha_fin:
                # url += '&end_date={}'.format(self.busqueda_fecha_fin)
            # if self.orden:
                # url += '&order_by={}'.format(self.orden)
            # if self.direccion_orden:
                # url += '&sort={}'.format(self.direccion_orden)

            if page > 1:
                url += '&page={}'.format(page)

            logger.debug("[Mal.py] Buscando {}:\n{}".format(self.busqueda_texto, url))
            results = self.get_json(url)

        if isinstance(results, list) or not (isinstance(results, dict) and results.get("error")):
            if index_results >= len(results):
                # Se ha solicitado un índice de resultado mayor de los que se obtuvieron
                logger.error("La busqueda de '{}' dio {} resultados para la pagina {}\nImposible mostrar el resultado numero {}".format(
                        self.busqueda_texto, len(results), page, index_results))
                return 0

            # Devolvemos el número de resultados de esta página
            self.results = results
            self.result = self.results[index_results]
            self.busqueda_id = self.result["mal_id"]
            return len(self.results)

        else:
            # Hubo errores al consultar, verificar la consulta
            msg = "La busqueda de '{}' no dio resultados para la pagina {}".format(self.busqueda_texto, page)
            logger.error(msg)
            return 0

    def __by_id(self, mal_id=None):
        """
            Busca una anime según su ID de MyAnimeList.

            @param mal_id: id de MyAnimeList
            @type mal_id: str
        """
        logger.info()
        if not mal_id and self.busqueda_id:
            mal_id = self.busqueda_id

        # Si hay id,solicitamos los datos asociados directamente
        if mal_id:
            url = 'https://api.jikan.moe/v3/anime/{}'.format(mal_id)
            buscando = "mal_id: {}".format(mal_id)

            logger.debug("[Mal.py] Buscando {}:\n{}".format(buscando, url))
            result = self.get_json(url)

            # Se obtuvo el resultado sin errores
            if result and (isinstance(result, list) or isinstance(result, dict)) and not "error" in result:
                self.results = [result]
                self.total_results = 1
                self.total_pages = 1
                self.result = result

            # El ID NO existe o hubo errores al procesar
            else:
                msg = "La busqueda de {} no dio resultados.".format(mal_id)
                logger.debug(msg)

    def get_id(self):
        """
            :return:
            Devuelve el identificador de MyAnimeList o una cadena vacia en caso de que no hubiese
            nada cargado. Se puede utilizar este método para saber si una búsqueda ha dado resultado.

            :rtype: str
        """
        logger.info()
        return str(self.result.get('mal_id', ''))

    def get_results_list(self, num_result=25):
        logger.info()
        result_list = []

        # Limitamos los resultados si son más del máximo establecido
        if num_result <= 0:
            num_result = self.total_results
        num_result = min([num_result, len(self.results)])

        for res in self.results:
            result = res
            result.update({"type": self.get_contentType(res),
                           "title": res.get("title", ""),
                           "original_title": res.get("title_japanese", ""),
                           "date": self.get_airdate(res),
                           "plot": res.get("synopsis", ""),
                           "thumbnail": res.get("image_url", "")})
            result_list.append(result)

        return result_list

    def get_contentType(self, result=None):
        """
            Obtiene el contentType de un anime basado en ciertos criterios
        """
        if not result:
            result = self.result

        if result["type"] == "TV" or result["episodes"] > 1:
            contentType = "tv"
        else:
            contentType = "movie"
        return contentType

    def get_airdate(self, origen=None):
        """
            Obtiene la fecha de lanzamiento según la información del resultado
        """
        if not origen:
            origen = self.result
        if origen.get("start_date"):
            date = scrapertools.find_multiple_matches(origen.get("start_date"), "(\d{4}).(\d{2}).(\d{2})")
            if len(date) > 0:
                date = date[0]
            air_date = "{}/{}/{}".format(date[0], date[1], date[2])
        elif origen.get("airing") and not isinstance(origen.get("airing"), bool):
            try:
                start_date = origen["airing"].get('prop', {}).get('from', {})
                air_date = '{}/{}/{}'.format(start_date.get('year'), start_date.get('month'), start_date.get('day'))
            except:
                logger.error("airing: {}".format(origen['airing']))
                air_date = ""
        else:
            air_date = ""
        return air_date

    def get_generos(self, origen=None):
        """
            Función de relleno que acomoda los géneros. Se podría localizar/traducir después...
        """

        generos = ""
        if origen is None:
            origen = self.result
        if "genres" in origen:
            ", ".join(i["name"] for i in origen["genres"])
        return generos

    def get_temporada(self, numtemporada=1):
        """
            Devuelve una temporada concreta. Función de "placebo" porque MAL no clasifica temporadas (pone todos los episodios "de jalón")
            NOTA: MAL clasifica temporadas diferentes como elementos diferentes, por lo que si hay algún anime que se categoriza
            como el mismo pero 2da temporada, habrá problemas si no se busca con el nombre de temporada (resultados inexactos)

            Devuelve un dict con el mismo nº de temporada y obtiene los episodios del anime (para uso con get_episodio)

            El parámetro numtemporada se ignora y se mantiene por compatibilidad (aunque se valida por si acaso)
        """
        logger.info()

        # Si no hay id o no es serie, devolvemos un dict vacío
        if not self.busqueda_id or self.busqueda_tipo == "movie":
            return {}

        numtemporada = int(numtemporada)

        # if numtemporada > 1:
        #     if not self.result:
        #         self.__by_id()
        #     self.busqueda_texto = "{} season {}".format(self.result["title"], numtemporada)
        #     self.__search()

        # Si aún no se han obtenido los episodios, los obtenemos
        if not self.temporada.get(numtemporada, {}):
            air_date = self.get_airdate(self.result)
            self.temporada[numtemporada] = {"season": numtemporada, "name": config.get_localized_string(60027) % numtemporada, "air_date": air_date}
            url = 'https://api.jikan.moe/v3/anime/{}/episodes'.format(self.busqueda_id)
            buscando = "id_MAL: {} temporada: {}\nURL: {}".format(self.busqueda_id, numtemporada, url)
            logger.debug("[Mal.py] Buscando {}".format(buscando))
            episodios = self.get_json(url)

            if episodios.get("error"):
                self.temporada[numtemporada].update(episodios)
            else:
                self.temporada[numtemporada]["episodes"] = episodios


        return {"season": numtemporada}

    def get_episodio(self, numtemporada=1, capitulo=1):
        """
            Parámetros:
                numtemporada(no utilizar): (int) Número de temporada. Por defecto 1.
                capitulo: (int) Número de capítulo. Por defecto 1.
            Return: (dic)
                Devuelve un dicionario con los siguientes datos:
                    "episodio_titulo", "episodio_titulo_original", "episodio_air_date"
        """

        # Si no hay id o no es serie, salimos
        if not self.result["mal_id"] or self.busqueda_tipo != "tv":
            return {}

        # Validamos nº de capítulo
        try:
            capitulo = int(capitulo)
        except ValueError:
            logger.debug("El número de episodio no es válido")
            return {}

        # Obtenemos la temporada
        temporada = self.get_temporada(numtemporada)
        if not temporada:
            # No se pudo obtener la temporada, salimos
            return {}

        # Obtenemos los datos del capítulo
        if capitulo != -1:
            episodio = temporada["episodes"][capitulo - 1]
            ret_dic["episodio_titulo"] = episodio.get("title", "")
            ret_dic["episodio_titulo_original"] = episodio.get("title_japanese", "")
            # No hay reseñas en la API que usamos 🙁
            # ret_dic["episodio_sinopsis"] = episodio["synopsis"]
            date = scrapertools.find_single_match(episodio["aired"], "\d{4}-\d{2}-\d{2}")
            ret_dic["episodio_air_date"] = date[2] + "/" + date[1] + "/" + date[0]
        return ret_dic

    def get_infoLabels(self, infoLabels=None, origen=None):
        """
            :param infoLabels: Informacion extra del anime
            :type infoLabels: Dict

            :param origen: Diccionario desde donde se obtienen los infoLabels, por defecto self.result
            :type origen: Dict

            :return: Devuelve la información extra obtenida del objeto actual. Si se paso el parametro infoLabels, el valor
            devuelto sera el leído como parámetro debidamente actualizado.
            :rtype: Dict
        """
        logger.info()

        if not "request_hash" in self.result:
            self.__by_id()

        if infoLabels:
            ret_infoLabels = InfoLabels(infoLabels)
        else:
            ret_infoLabels = InfoLabels()

        if not origen:
            origen = self.result

        items = list(origen.items())

        # Información de temporada/episodio
        if isinstance(ret_infoLabels.get('season'), int):
            if self.temporada.get(ret_infoLabels['season']):
                # Si hay datos cargados de la temporada indicada
                episodio = -1
                if ret_infoLabels.get('episode'):
                    episodio = ret_infoLabels['episode']

                items.extend(list(self.get_episodio(ret_infoLabels['season'], episodio).items()))

        for key, value in items:
            if not value:
                continue
            elif isinstance(value, str):
                value = re.sub(r"\n|\r|\t", "", value)
                # fix
                if value == "None":
                    continue

            if key == 'synopsis':
                ret_infoLabels['plot'] = value

            elif key == 'type':
                ret_infoLabels['mediatype'] = self.get_contentType(origen)
                ret_infoLabels['type'] = value
                if ret_infoLabels['mediatype'] == "movie":
                    ret_infoLabels.pop("tvshowtitle", "")

            elif key == 'duration':
                duration = 0
                time = scrapertools.find_single_match(value, "(?:(\d+).hr.+?|)(\d+).min")
                if time[0]:
                    duration += int(time[0] * 60)
                duration += int(time[1])
                ret_infoLabels['duration'] = int(duration * 60)

            elif key in ['aired', "start_date"]:
                ret_infoLabels['year'] = self.get_airdate(origen).split("/")[0]
                ret_infoLabels['release_date'] = self.get_airdate(origen)
                ret_infoLabels['aired'] = ret_infoLabels['release_date']
                ret_infoLabels['premiered'] = ret_infoLabels['release_date']

            elif key == 'image_url':
                ret_infoLabels['thumbnail'] = value

            elif key == 'background' and value:
                ret_infoLabels['fanart'] = value

            elif key == 'mal_id':
                ret_infoLabels['code'] = value
                ret_infoLabels['mal_id'] = value
                ret_infoLabels['id'] = value

            elif key == 'genres':
                ret_infoLabels['genre'] = self.get_generos(origen)

            elif key == 'name' or key == 'title':
                ret_infoLabels['title'] = value

            elif key == 'studios':
                ret_infoLabels['studio'] = ", ".join(i['name'] for i in value)

            elif key == 'trailer_url':
                ret_infoLabels['trailer'] = value

            elif key in ['title_japanese']:
                ret_infoLabels['originaltitle'] = value

            elif key == 'score':
                ret_infoLabels['rating'] = float(value)

            elif key == 'scored_by':
                ret_infoLabels['votes'] = value

            elif isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                ret_infoLabels[key] = value

            else:
                # logger.debug("Atributos no añadidos: " + key +'= '+ str(v))
                pass

        if ret_infoLabels["mediatype"] == "movie" and "episodes" in ret_infoLabels:
            ret_infoLabels.pop("episodes", "")

        return ret_infoLabels
