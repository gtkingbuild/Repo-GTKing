# -*- coding: utf-8 -*-
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Gracias a la librería plugintools de Jesús (www.mimediacenter.info), PlatformCode y Core del Grupo Balandro (https://linktr.ee/balandro)

import os, sys, urllib, re, shutil, zipfile, base64
#import xbmc, xbmcgui, xbmcaddon, xbmcplugin, requests
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import locale, time, random, plugintools
import resolvers

if sys.version_info[0] < 3:
    import urllib2
else:
    import urllib.error as urllib2

from core import httptools
from core.item import Item
from platformcode.config import WebErrorException


addonName           = xbmcaddon.Addon().getAddonInfo("name")
addonVersion        = xbmcaddon.Addon().getAddonInfo("version")
addonId             = xbmcaddon.Addon().getAddonInfo("id")
addonPath           = xbmcaddon.Addon().getAddonInfo("path")

version="(v1.0.2)"

addonPath           = xbmcaddon.Addon().getAddonInfo("path")
mi_data = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/plugin.video.TorrentsTV/'))
mi_addon = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.TorrentsTV'))

fondo = xbmc.translatePath(os.path.join(mi_addon,'fanart.jpg'))
logoprin = xbmc.translatePath(os.path.join(mi_addon,'icon.png'))

mislogos = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.TorrentsTV/jpg/'))
logobusca = xbmc.translatePath(os.path.join(mislogos , 'buscar.jpg'))
logo_volver = xbmc.translatePath(os.path.join(mislogos , 'volver.png'))
logo_siguiente = xbmc.translatePath(os.path.join(mislogos , 'siguiente.png'))
logo_finpag = xbmc.translatePath(os.path.join(mislogos , 'final.png'))
logo_transparente = xbmc.translatePath(os.path.join(mislogos , 'transparente.png'))
logo_salida = xbmc.translatePath(os.path.join(mislogos , 'salida.png'))
logo_SD = xbmc.translatePath(os.path.join(mislogos , 'logo_SD.png'))
logo_HD = xbmc.translatePath(os.path.join(mislogos , 'logo_HD.jpg'))
logo_4K = xbmc.translatePath(os.path.join(mislogos , 'logo_4K.jpg'))
logo_Genero = xbmc.translatePath(os.path.join(mislogos , 'generos.jpeg'))

usaElementum = False
setting = xbmcaddon.Addon().getSetting
if setting('lanzarCon') == "0":  ##0 = Elementum  1 = Horus+Acestream
    usaElementum = True


datosConf = httptools.downloadpage(base64.b64decode("aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0FjZVRvcnIvZnV0dHJlYW0vbWFpbi9EYXRvc0NvbmY=".encode('utf-8')).decode('utf-8')).data

if not "<TTV>" in datosConf:
    datosConf = httptools.downloadpage(base64.b64decode("aHR0cHM6Ly9yZW50cnkuY28veHM2YmYvcmF3".encode('utf-8')).decode('utf-8')).data

datosTel = plugintools.find_single_match(datosConf,'TTVtel>(.*?)<Fin')
telegram = httptools.downloadpage(datosTel).data

#plugintools.log("*****************TELEGRAM: "+telegram+"********************")
telegram = telegram.replace("(Disponible)" , "DESDE_AQUI")
acotacion = 'DESDE_AQUI'
provisional = plugintools.find_single_match(telegram,acotacion+'(.*?)<i')

web = plugintools.find_single_match(provisional,'href="(.*?)"')
headers = {'Referer': web}
#plugintools.log("*****************WEB: "+web+"********************")


if len(web) == 0:  ##Hay algún problema en el canal Telegram
    web = plugintools.find_single_match(datosConf,'TTV>(.*?)<Fin')
    headers = {'Referer': web}


peliSD = web + "peliculas/page/"
peliHD = web + "peliculas/hd/page/"
peli4K = web + "peliculas/4K/page/"

serieSD = web + "series/page/"
serieHD = web + "series/hd/page/"

horus = "eydhY3Rpb24nOiAncGxheScsICdmYW5hcnQnOiAnJywgJ2ljb24nOiAnTUktSUNPTk8nLCAndXJsJzogJ01JLVRPUlJFTlQnLCAnbGFiZWwnOiAnTUktVElUVUxPJ30="

if not os.path.exists(mi_data):
	os.makedirs(mi_data)  # Si no existe el directorio, lo creo

ult_Busca = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/plugin.video.TorrentsTV/ult_Busca.txt'))
if not os.path.exists(ult_Busca):
    if sys.version_info[0] < 3:
        crear=open(ult_Busca, "w+")
    else:
        crear=open(ult_Busca, "w+", encoding='utf-8')
    crear.close()


cabecera = "[COLOR moccasin][B]      TorrentsTV  "+version+" [COLOR red]        ····[COLOR yellowgreen]by AceTorr[COLOR red]····[/B][/COLOR]"



# Punto de Entrada
def run():
	plugintools.log('[%s %s] Running %s... ' % (addonName, addonVersion, addonName))

	# Obteniendo parámetros...
	params = plugintools.get_params()
    
	
	if params.get("action") is None:
		main_list(params)
	else:
		action = params.get("action")
		exec(action+"(params)")
        

	plugintools.close_item_list()            



# Principal
def main_list(params):
    
    pagina = "1"
    plugintools.add_item(action="",url="",title=cabecera,thumbnail=logoprin,fanart=fondo,folder=False,isPlayable=False)
    plugintools.add_item(action="abre_categoria",url=peliSD,title='[COLOR white]Peliculas SD[/COLOR]' , page=pagina, thumbnail=logo_SD, fanart=fondo, folder=True, isPlayable=False)
    plugintools.add_item(action="abre_categoria",url=peliHD,title='[COLOR white]Peliculas HD[/COLOR]' , page=pagina, thumbnail=logo_HD, fanart=fondo, folder=True, isPlayable=False)
    plugintools.add_item(action="abre_categoria",url=peli4K,title='[COLOR white]Peliculas 4K[/COLOR]' , page=pagina, thumbnail=logo_4K, fanart=fondo, folder=True, isPlayable=False)
    plugintools.add_item(action="lista_generos",url="",title='[COLOR white]Películas por Géneros[/COLOR]' ,thumbnail=logo_Genero, fanart=fondo, page=pagina, folder=True, isPlayable=False)
    datamovie = {}
    datamovie["Plot"]="Buscar Películas por palabras clave."
    plugintools.add_item(action="fBusca",url="",title="[COLOR blue]Búsqueda de Películas[/COLOR]", extra="", plot="Peliculas", thumbnail=logobusca, fanart=fondo, page=pagina, info_labels = datamovie, folder=True, isPlayable=False)

    if usaElementum:
        plugintools.add_item(action="abre_categoria",url=serieSD,title='[COLOR white]Series SD[/COLOR]' , page=pagina, thumbnail=logo_SD, fanart=fondo, folder=True, isPlayable=False)
        plugintools.add_item(action="abre_categoria",url=serieHD,title='[COLOR white]Series HD[/COLOR]' , page=pagina, thumbnail=logo_HD, fanart=fondo, folder=True, isPlayable=False)

    datamovie = {}
    datamovie["Plot"]="Buscar Series por palabras clave."
    plugintools.add_item(action="fBusca",url="",title="[COLOR blue]Búsqueda de Series[/COLOR]", extra="", plot="Series", thumbnail=logobusca, fanart=fondo, page=pagina, info_labels = datamovie, folder=True, isPlayable=False)
    
    datamovie = {}
    datamovie["Plot"]="Salir de TorrentsTV..."
    plugintools.add_item(action="salida",url="",title="[COLOR red]Salir[/COLOR]",thumbnail=logo_salida, extra="", fanart="https://i.imgur.com/Cp1t1lb.png", info_labels = datamovie, folder=False, isPlayable=False)
    
    plugintools.add_item(action="", url="", title="", genre="NOGESTIONAR", thumbnail=logo_transparente, fanart=fondo, folder=False, isPlayable=False)
    mensaje = "[COLOR firebrick]**Este addon se suministra gratuitamente desde [COLOR yellow][B]Kelebek[/B][COLOR firebrick]. Si está en algún otro paquete, es sin la AUTORIZACIÓN de sus creadores.[/COLOR]"
    plugintools.add_item(action="", url="", title=mensaje, genre="NOGESTIONAR", thumbnail=logoprin, fanart=fondo, folder=False, isPlayable=False)



def abre_categoria(params):
    url = params.get("url")
    titu = params.get("title")
    logo1 = params.get("thumbnail")
    extra = params.get("extra")
    pagina = params.get("page")

    xbmcplugin.setContent( int(sys.argv[1]) ,"tvshows" )
    
    esSerie = False
    if "series/" in url:
        esSerie = True
    
    if len(extra) != 0: ## Si trae texto es q viene de llamada recursiva por paginación
        #Entraigo Titulo y logo de 1ª página
        titu = plugintools.find_single_match(extra,'TITU_ORIGEN:(.*?)LOGO_')
        logo1 = plugintools.find_single_match(extra,'LOGO_ORIGEN:(.*?)<Fin')
        #plugintools.log("*****************Titu: "+titu+"********************")
        
    else:
        titu = titu.replace("[COLOR white]" , "[COLOR mediumslateblue]·····  ").replace("[/COLOR]" , "  ·····[/COLOR]")
        #Meto en extra el titulo y el logo por si viene de vuelta en llamada de paginación
        extra = "TITU_ORIGEN:" + titu + "LOGO_ORIGEN:" + logo1 + "<Fin"
    
    plugintools.add_item(action="",url="",title=titu,thumbnail=logo1,fanart=fondo,folder=False,isPlayable=False)
    
    data = ""
    data = httptools.downloadpage(url+pagina, headers=headers).data
    
    acotacion = '<div class="text-center'  ##Acotacion de los grupos de 3
    bloq_videos = plugintools.find_multiple_matches(data,acotacion+'(.*?)</div')

    for bloque in bloq_videos:
        acota2 = '<a href=' ##Acotacion de los 3 videos del bloque
        videos = plugintools.find_multiple_matches(bloque,acota2+'(.*?)<img')
        for item in videos:
            acota3 = '"/'
            url_vid = web + plugintools.find_single_match(item,acota3+'(.*?)"')  ##Obtengo la página donde está todo lo necesario para esa Peli, así q la leo y los obtengo
            #plugintools.log("*****************Item: "+item+"********************")
            data2 = httptools.downloadpage(url_vid, headers=headers).data
            acota4 = 'descargarTitulo"'
            if esSerie:
                acotafin = "h2>"
            else:
                acotafin = "h1>"
                
            titul0 = plugintools.find_single_match(data2,acota4+'(.*?)'+acotafin)
            #plugintools.log("*****************Titu10: "+titul0+"********************")

            if esSerie:
                acota4 = '>'
                titul = plugintools.find_single_match(titul0,acota4+'(.*?)<').replace("por Torrent" , "").title().strip()
                
                acota4 = "Episodios:</b> "
                episodios = plugintools.find_single_match(data2,acota4+"(.*?)<")

                acota4 = "Formato:</b> "
                calidad = plugintools.find_single_match(data2,acota4+"(.*?)</p")

                titulo = titul + "[COLOR orange]   -" + episodios + " Episodios-[/COLOR]" + "   [COLOR blue]" + calidad + "[/COLOR]"

                acota4 = 'image" content="'
                logo = plugintools.find_single_match(data2,acota4+'(.*?)"')
                
                acota4 = 'bold">Descrip'
                sinop = plugintools.find_single_match(data2,acota4+"(.*?)</div>")  ## Primer acercamiento a la sinopsis
                acota4 = '/b>'
                sinopsis = plugintools.find_single_match(sinop,acota4+"(.*?)</p>")  ## Ahora si la tengo
                
            else:
                acota4 = '>Descargar '
                titul = plugintools.find_single_match(titul0,acota4+'(.*?)<').replace("por Torrent" , "").title().strip()
                
                acota4 = "anyo', valor: '"
                anio = plugintools.find_single_match(data2,acota4+"(.*?)'")

                acota4 = "Formato:</b> "
                calidad = plugintools.find_single_match(data2,acota4+"(.*?)</p")

                titulo = titul + "[COLOR orange]   -" + anio + "-[/COLOR]" + "   [COLOR blue]" + calidad + "[/COLOR]"

                acota4 = 'image" content="'
                logo = plugintools.find_single_match(data2,acota4+'(.*?)"')
                
                acota4 = "href='//"
                torrent = "https://" + plugintools.find_single_match(data2,acota4+"(.*?)'")
                
                acota4 = 'bold">Descrip'
                sinop = plugintools.find_single_match(data2,acota4+"(.*?)</div>")  ## Primer acercamiento a la sinopsis
                acota4 = '/b>'
                sinopsis = plugintools.find_single_match(sinop,acota4+"(.*?)</p>")  ## Ahora si la tengo
                
                if usaElementum:
                    mivideo = "plugin://plugin.video.elementum/play?uri=" + torrent
                else:
                    reemplaza = base64.b64decode(horus.encode('utf-8')).decode('utf-8').replace("MI-TORRENT" , torrent)
                    reemplaza = reemplaza.replace("MI-ICONO" , logo)
                    reemplaza = reemplaza.replace("MI-TITULO" , titulo)
                    mivideo = "plugin://script.module.horus/?" + base64.b64encode(reemplaza.encode('utf-8')).decode('utf-8')
            
            titu = '[COLOR white]' + titulo + "[/COLOR]"
            
            datamovie = {}
            datamovie["Plot"] = sinopsis
            if esSerie:
                plugintools.add_item(action="temporada", url=url_vid, title=titu, extra=titulo, genre="NOGESTIONAR", thumbnail=logo, fanart=fondo, info_labels = datamovie, folder=True, isPlayable=False)
            else:
                plugintools.add_item(action="lanza", url=mivideo, title=titu, extra=titulo, genre="NOGESTIONAR", thumbnail=logo, fanart=fondo, info_labels = datamovie, folder=False, isPlayable=False)
            
    pag_actual = pagina
    pagina = str(int(pagina)+1)
    texto = "[COLOR mediumaquamarine]Pág: " + pag_actual + "[COLOR lime]                  Ir a Siguiente >>>[/COLOR]"        
    plugintools.add_item(action="abre_categoria", url=url, title=texto, page = pagina, extra=extra, genre="NOGESTIONAR", thumbnail="", fanart=fondo, folder=True, isPlayable=False)
    plugintools.add_item(action="main_list", url="", title="[COLOR orangered]···· Volver a Menú Principal ····[/COLOR]", extra=extra ,thumbnail=logo_volver, fanart=fondo, folder=True, isPlayable=False)
    


def temporada(params):
    url = params.get("url")
    titu = params.get("title")
    logo1 = params.get("thumbnail")
    extra = params.get("extra")
    pagina = params.get("page")
    
    #Abro la página y capturo los episodios
    data = httptools.downloadpage(url, headers=headers).data
    acotacion = '<tbody><tr>'
    bloq_videos = "<tr>" + plugintools.find_single_match(data,acotacion+'(.*?)</tbody')
    
    acotacion = '<tr>'
    cada_video = plugintools.find_multiple_matches(bloq_videos,acotacion+'(.*?)</tr')

    for item in cada_video:
        lineas = plugintools.find_multiple_matches(item,'<td(.*?)</td')
        
        abuscar = lineas[0] + "<"  ## en la 1ª linea está el nº episodio
        episodio = plugintools.find_single_match(abuscar,'>(.*?)<')

        abuscar = lineas[1] + "<"  ## en la 2ª linea está el torrent
        acotacion = "href='"
        torrent = "https:" + plugintools.find_single_match(abuscar,acotacion+"(.*?)'")

        abuscar = lineas[2] + "<"  ## en la 3ª linea está la fecha del episodio
        fecha = plugintools.find_single_match(abuscar,'>(.*?)<')

        mivideo = "plugin://plugin.video.elementum/play?uri=" + torrent
        titulo = "[COLOR white]" + episodio + "   [COLOR blue](" + fecha + ")[/COLOR]"
       
        plugintools.add_item(action="lanza", url=mivideo, title=titulo, extra=titulo, genre="NOGESTIONAR", thumbnail=logo1, fanart=fondo, folder=False, isPlayable=False)





def lista_generos(params):

    aGen = ['Acción',
            'Animación',
            'Aventuras',
            'Bélica',
            'Biográfica',
            'Ciencia Ficción',
            'Cine Negro',
            'Comedia',
            'Crimen',
            'Documental',
            'Drama',
            'Fantasía',
            'Musical',
            'Romántica',
            'Suspense',
            'Terror',
            'Western']

    for i in range(len(aGen)):
        titu = '[COLOR white]-' + aGen[i] + "[/COLOR]"
        plugintools.add_item(action="generos", url=aGen[i], title=titu, page = "1", extra="", genre="NOGESTIONAR", thumbnail=logoprin, fanart=fondo, folder=True, isPlayable=False)
        

def generos(params):
    elGenero = params.get("url")
    pagina = params.get("page")
    extra = params.get("extra")
    titu = params.get("title")
    logo1 = params.get("thumbnail")

    xbmcplugin.setContent( int(sys.argv[1]) ,"tvshows" )

    if len(extra) != 0: ## Si trae texto es q viene de llamada recursiva por paginación
        #Entraigo Titulo y logo de 1ª página
        titu = plugintools.find_single_match(extra,'TITU_ORIGEN:(.*?)LOGO_')
        logo1 = plugintools.find_single_match(extra,'LOGO_ORIGEN:(.*?)<Fin')
        #plugintools.log("*****************Titu: "+titu+"********************")
        
    else:
        titu = titu.replace("[COLOR white]-" , "[COLOR lime]·····  Género:[B] ").replace("[/COLOR]" , "  [/B]·····[/COLOR]")
        
        #Meto en extra el titulo y el logo por si viene de vuelta en llamada de paginación
        extra = "TITU_ORIGEN:" + titu + "LOGO_ORIGEN:" + logo1 + "<Fin"
    
    plugintools.add_item(action="",url="",title=titu,thumbnail=logo1,fanart=fondo,folder=False,isPlayable=False)

    condicion = "campo=genero&valor=&valor2="+elGenero+"&valor3=&valor4=&pagina="+pagina
    genweb = web + "peliculas/buscar"
    headers = {'Referer': web}

    pagenero = httptools.downloadpage(genweb, post=condicion, headers=headers).data
    acotacion = '<a class="position-relative'
    pelis_gen = plugintools.find_multiple_matches(pagenero,acotacion+'(.*?)</a')
    #plugintools.log("*****************PelisGen: "+str(len(pelis_gen))+"********************")
    
    for item in pelis_gen:
        acota3 = 'href="/'
        url_vid = web + plugintools.find_single_match(item,acota3+'(.*?)"')  ##Obtengo la página donde está todo lo necesario para esa Peli, así q la leo y los obtengo
        
        data2 = httptools.downloadpage(url_vid, headers=headers).data
        acota4 = 'descargarTitulo"'
        titul0 = plugintools.find_single_match(data2,acota4+'(.*?)h1>')
        acota4 = '>Descargar '
        titul = plugintools.find_single_match(titul0,acota4+'(.*?)<').replace("por Torrent" , "").title().strip()
        
        acota4 = "anyo', valor: '"
        anio = plugintools.find_single_match(data2,acota4+"(.*?)'")

        acota4 = "Formato:</b> "
        calidad = plugintools.find_single_match(data2,acota4+"(.*?)</p")

        titulo = titul + "[COLOR orange]   -" + anio + "-[/COLOR]" + "   [COLOR blue]" + calidad + "[/COLOR]"

        acota4 = 'image" content="'
        logo = plugintools.find_single_match(data2,acota4+'(.*?)"')
        
        acota4 = "href='//"
        torrent = "https://" + plugintools.find_single_match(data2,acota4+"(.*?)'")
        
        acota4 = 'bold">Descrip'
        sinop = plugintools.find_single_match(data2,acota4+"(.*?)</div>")  ## Primer acercamiento a la sinopsis
        acota4 = '/b>'
        sinopsis = plugintools.find_single_match(sinop,acota4+"(.*?)</p>")  ## Ahora si la tengo
        
        if usaElementum:
            mivideo = "plugin://plugin.video.elementum/play?uri=" + torrent
        else:
            reemplaza = base64.b64decode(horus.encode('utf-8')).decode('utf-8').replace("MI-TORRENT" , torrent)
            reemplaza = reemplaza.replace("MI-ICONO" , logo)
            reemplaza = reemplaza.replace("MI-TITULO" , titulo)
            mivideo = "plugin://script.module.horus/?" + base64.b64encode(reemplaza.encode('utf-8')).decode('utf-8')
        
        titu = '[COLOR white]' + titulo + "[/COLOR]"
        
        #plugintools.log("*****************Titulo: "+titulo+"********************")
        datamovie = {}
        datamovie["Plot"] = sinopsis
        plugintools.add_item(action="lanza", url=mivideo, title=titu, extra=titulo, genre="NOGESTIONAR", thumbnail=logo, fanart=fondo, info_labels = datamovie, folder=False, isPlayable=False)
        
    pag_actual = pagina
    pagina = str(int(pagina)+1)
    texto = "[COLOR mediumaquamarine]Pág: " + pag_actual + "[COLOR lime]                  Ir a Siguiente >>>[/COLOR]"        
    plugintools.add_item(action="generos", url=elGenero, title=texto, page = pagina, extra=extra, genre="NOGESTIONAR", thumbnail="", fanart=fondo, folder=True, isPlayable=False)
    plugintools.add_item(action="main_list", url="", title="[COLOR orangered]···· Volver a Menú Principal ····[/COLOR]", extra="" ,thumbnail=logo_volver, fanart=fondo, folder=True, isPlayable=False)
  

def fBusca(params):
    url = params.get("url")
    titu = params.get("title")
    logo1 = params.get("thumbnail")
    extra = params.get("extra")
    peliSerie = params.get("plot")
    pagina = params.get("page")

    xbmcplugin.setContent( int(sys.argv[1]) ,"tvshows" )
    
    if len(extra) == 0: ## Si NO trae texto es q viene de Menú Ppal.
        ##Miro si hay guardada una búsqueda anterior y la pongo
        if sys.version_info[0] < 3:
            v = open( ult_Busca, "r" )
        else:
            v = open( ult_Busca, "r", encoding='utf-8' )

        leido = v.read()
        v.close()
        elTexto = plugintools.find_single_match(leido,"INICIO>(.*?)<FIN")
        
        #busqueda = plugintools.keyboard_input('', 'Introduzca [COLOR red]Texto[/COLOR] a Buscar.')
        busqueda = plugintools.keyboard_input(elTexto, 'Introduzca [COLOR red]Texto[/COLOR] a Buscar.')
        if len(busqueda) == 0:
            xbmc.executebuiltin('ActivateWindow(10000,return)')  ##Vuelvo al menú ppal.
        else:  ## Guardo la última búsqueda
            if sys.version_info[0] < 3:
                fichero = open( ult_Busca, "w+" )
            else:
                fichero = open( ult_Busca, "w+", encoding='utf-8' )

            fichero.write("INICIO>"+busqueda+"<FIN")
            fichero.close()
        
        
        
        titu = "[COLOR lime]·····  Buscar:[B]   " + busqueda + "[/B]  ·····[/COLOR]"
        #Meto en extra el titulo y el logo por si viene de vuelta en llamada de paginación
        extra = "TITU_ORIGEN:" + titu + "LOGO_ORIGEN:" + logo1 + "<Fin"
        pagina = "1"
        laBusqueda = "/buscar/" + busqueda.replace(" ", "%20") + "/page/"
        extra = extra + "<Buscapag>" + laBusqueda + "<FinBuscapag>"
        url = web + "buscar/" + busqueda.replace(" ", "%20")
        
    else: ## Si trae texto es q viene de llamada recursiva por paginación
        #Entraigo Titulo y logo de 1ª página
        titu = plugintools.find_single_match(extra,'TITU_ORIGEN:(.*?)LOGO_')
        logo1 = plugintools.find_single_match(extra,'LOGO_ORIGEN:(.*?)<Fin')
        laBusqueda = plugintools.find_single_match(extra,'<Buscapag>(.*?)<FinBuscapag>')

        url = web[:-1]  + laBusqueda + pagina
    

    plugintools.add_item(action="",url="",title=titu,thumbnail=logo1,fanart=fondo,folder=False,isPlayable=False)

    
    pagbusca = httptools.downloadpage(url, headers=headers).data
    acotacion = '<p><span><a'  ##Acotacion de todos los encontrados
    pelis_busca = plugintools.find_multiple_matches(pagbusca,acotacion+'(.*?)</p>')
    

    ##Nos deshacemos de los que no sean "pelicula"... series, docuseries, etc
    for item in pelis_busca:
        if ("/pelicula/" in item) and (peliSerie == "Peliculas"):  ##Es película, por lo q lo cojo
            acota3 = "href='/"
            url_vid = web + plugintools.find_single_match(item,acota3+"(.*?)'")  ##Obtengo la página donde está todo lo necesario para esa Peli, así q la leo y los obtengo
            
            data2 = httptools.downloadpage(url_vid, headers=headers).data
            acota4 = 'descargarTitulo"'
            titul0 = plugintools.find_single_match(data2,acota4+'(.*?)h1>')
            acota4 = '>Descargar '
            titul = plugintools.find_single_match(titul0,acota4+'(.*?)<').replace("por Torrent" , "").title().strip()
            
            acota4 = "anyo', valor: '"
            anio = plugintools.find_single_match(data2,acota4+"(.*?)'")

            acota4 = "Formato:</b> "
            calidad = plugintools.find_single_match(data2,acota4+"(.*?)</p")

            titulo = titul + "[COLOR orange]   -" + anio + "-[/COLOR]" + "[COLOR lime]" +"  Pelicula" + " [COLOR blue]" + calidad + "[/COLOR]"
            
            acota4 = "Formato:</b> "
            calidad = plugintools.find_single_match(data2,acota4+"(.*?)</p")

            acota4 = 'image" content="'
            logo = plugintools.find_single_match(data2,acota4+'(.*?)"')
            
            acota4 = "href='//"
            torrent = "https://" + plugintools.find_single_match(data2,acota4+"(.*?)'")
            
            acota4 = 'bold">Descrip'
            sinop = plugintools.find_single_match(data2,acota4+"(.*?)</div>")  ## Primer acercamiento a la sinopsis
            acota4 = '/b>'
            sinopsis = plugintools.find_single_match(sinop,acota4+"(.*?)</p>")  ## Ahora si la tengo
            
            if usaElementum:
                mivideo = "plugin://plugin.video.elementum/play?uri=" + torrent
            else:
                reemplaza = base64.b64decode(horus.encode('utf-8')).decode('utf-8').replace("MI-TORRENT" , torrent)
                reemplaza = reemplaza.replace("MI-ICONO" , logo)
                reemplaza = reemplaza.replace("MI-TITULO" , titulo)
                mivideo = "plugin://script.module.horus/?" + base64.b64encode(reemplaza.encode('utf-8')).decode('utf-8')
            
            titu = '[COLOR white]' + titulo + "[/COLOR]"
            
            datamovie = {}
            datamovie["Plot"] = sinopsis
            plugintools.add_item(action="lanza", url=mivideo, title=titu, extra=titulo, genre="NOGESTIONAR", thumbnail=logo, fanart=fondo, info_labels = datamovie, folder=False, isPlayable=False)
    
        if ("/serie/" in item) and (peliSerie == "Series") and usaElementum:  ##Es Serie y está elegido como Motor el Elementum, por lo q lo cojo
            acota3 = "href='/"
            url_vid = web + plugintools.find_single_match(item,acota3+"(.*?)'")  ##Obtengo la página donde está todo lo necesario para esa Peli, así q la leo y los obtengo
            
            data2 = httptools.downloadpage(url_vid, headers=headers).data
            acota4 = 'descargarTitulo"'
            acotafin = "h2>"
                
            titul0 = plugintools.find_single_match(data2,acota4+'(.*?)'+acotafin)
            #plugintools.log("*****************Titu10: "+titul0+"********************")

            acota4 = '>'
            titul = plugintools.find_single_match(titul0,acota4+'(.*?)<').replace("por Torrent" , "").title().strip()
            
            acota4 = "Episodios:</b> "
            episodios = plugintools.find_single_match(data2,acota4+"(.*?)<")

            acota4 = "Formato:</b> "
            calidad = plugintools.find_single_match(data2,acota4+"(.*?)</p")

            titulo = titul + "[COLOR orange]   -" + episodios + " Episodios-[/COLOR]" + "[COLOR crimson]" +"  Serie" + " [COLOR blue]" + calidad + "[/COLOR]"

            acota4 = 'image" content="'
            logo = plugintools.find_single_match(data2,acota4+'(.*?)"')
            
            acota4 = 'bold">Descrip'
            sinop = plugintools.find_single_match(data2,acota4+"(.*?)</div>")  ## Primer acercamiento a la sinopsis
            acota4 = '/b>'
            sinopsis = plugintools.find_single_match(sinop,acota4+"(.*?)</p>")  ## Ahora si la tengo
                
            
            titu = '[COLOR white]' + titulo + "[/COLOR]"
            
            datamovie = {}
            datamovie["Plot"] = sinopsis
            plugintools.add_item(action="temporada", url=url_vid, title=titu, extra=titulo, genre="NOGESTIONAR", thumbnail=logo, fanart=fondo, info_labels = datamovie, folder=True, isPlayable=False)
            
    
    if ">Siguiente<" in pagbusca:  ## Hay mas páginas
        pag_actual = pagina
        pagina = str(int(pagina)+1)
        texto = "[COLOR mediumaquamarine]Pág: " + pag_actual + "[COLOR lime]                  Ir a Siguiente >>>[/COLOR]"        
        plugintools.add_item(action="fBusca", url=url, title=texto, page = pagina, extra=extra, plot=peliSerie, thumbnail=logo_siguiente, fanart=fondo, folder=True, isPlayable=False)
        plugintools.add_item(action="main_list", url="", title="[COLOR orangered]···· Volver a Menú Principal ····[/COLOR]", extra=extra ,thumbnail=logo_volver, fanart=fondo, folder=True, isPlayable=False)
            


def lanza(params):
    mivideo = params.get("url")
    logo = params.get("thumbnail")
    titu = params.get("title")
    titulo = params.get("extra")
    
    #xbmc.Player().play(mivideo)
    logo = logo.replace("https://images.weserv.nl/?url=" , "")
    #plugintools.log("*****************Logo: "+logo+"********************")
    li = xbmcgui.ListItem(titu)
    li.setInfo(type='Video', infoLabels="")
    li.setArt({ 'thumb': logo})
    xbmc.Player().play(mivideo, li)
    




def salida(params):

	xbmc.executebuiltin('ActivateWindow(10000,return)')
	



	


	


		
run()

		




	

