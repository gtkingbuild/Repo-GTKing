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

version="(v0.0.2)"

addonPath           = xbmcaddon.Addon().getAddonInfo("path")
mi_data = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/plugin.video.TorrentAcestream/'))
mi_addon = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.TorrentAcestream'))

fondo = xbmc.translatePath(os.path.join(mi_addon,'fanart.jpg'))
logoprin = xbmc.translatePath(os.path.join(mi_addon,'icon.png'))

mislogos = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.TorrentAcestream/jpg/'))
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

setting = xbmcaddon.Addon().getSetting
marcar_visto = False
pregunta_marcar = False
if setting('marcar_visto') == "true":
    marcar_visto = True
if setting('pregunta_marcar') == "true":
    pregunta_marcar = True    

web = plugintools.find_single_match(httptools.downloadpage(base64.b64decode("aHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3LzVxV3dTQ3FF".encode('utf-8')).decode('utf-8')).data,'xxx(.*?)xxx')
headers = {'Referer': web}

peliSD = web + "peliculas/page/"
peliHD = web + "peliculas/hd/page/"
peli4K = web + "peliculas/4K/page/"

horus = "eydhY3Rpb24nOiAncGxheScsICdmYW5hcnQnOiAnJywgJ2ljb24nOiAnTUktSUNPTk8nLCAndXJsJzogJ01JLVRPUlJFTlQnLCAnbGFiZWwnOiAnTUktVElUVUxPJ30="

if not os.path.exists(mi_data):
	os.makedirs(mi_data)  # Si no existe el directorio, lo creo

vistos = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/plugin.video.TorrentAcestream/vistos.db'))
if not os.path.exists(vistos):
    if sys.version_info[0] < 3:
        crear=open(vistos, "w+")
    else:
        crear=open(vistos, "w+", encoding='utf-8')
    crear.close()

cabecera = "[COLOR mediumslateblue][B]      Torrents-Acestream  "+version+" [COLOR red]        ····[COLOR yellowgreen]by AceTorr[COLOR red]····[/B][/COLOR]"
	
#Para comprobar los videos que ya estén vistos y así marcarlos como vistos.
if marcar_visto:
    #v=open(vistos, "r")
    if sys.version_info[0] < 3:
        v = open( vistos, "r" )
    else:
        v = open( vistos, "r", encoding='utf-8' )

    pelis_vistas = v.read()
    v.close()



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
    plugintools.add_item(action="lista_generos",url="",title='[COLOR white]Géneros[/COLOR]' ,thumbnail=logo_Genero, fanart=fondo, page=pagina, folder=True, isPlayable=False)

    datamovie = {}
    datamovie["Plot"]="Buscar Peliculas por palabras clave."
    plugintools.add_item(action="fBusca",url="",title="[COLOR blue]Búsqueda[/COLOR]",extra="", show="", thumbnail=logobusca, fanart=fondo, page=pagina, info_labels = datamovie, folder=True, isPlayable=False)
    datamovie = {}
    datamovie["Plot"]="Salir de TorrentAcestream..."
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
            
            #reemplaza = base64.b64decode(horus.encode('utf-8')).decode('utf-8').replace("MI-TORRENT" , "https://bit.ly/3DAMgUo")
            reemplaza = base64.b64decode(horus.encode('utf-8')).decode('utf-8').replace("MI-TORRENT" , torrent)
            reemplaza = reemplaza.replace("MI-ICONO" , logo)
            reemplaza = reemplaza.replace("MI-TITULO" , titulo)
            mivideo = "plugin://script.module.horus/?" + base64.b64encode(reemplaza.encode('utf-8')).decode('utf-8')
            
            #Comprobamos si alguno está en la BD de vistos, y si es así lo marco como visto.
            marcalo = ""
            if marcar_visto:
                if titulo in pelis_vistas:
                    marcalo = "[COLOR green][B]√[/B][/COLOR]"
        
            titu = '[COLOR white]' + titulo + "[/COLOR]"
            titu = marcalo + titu
            
            datamovie = {}
            datamovie["Plot"] = sinopsis
            plugintools.add_item(action="lanza", url=mivideo, title=titu, extra=titulo, genre="NOGESTIONAR", thumbnail=logo, fanart=fondo, info_labels = datamovie, folder=False, isPlayable=False)
            
    pag_actual = pagina
    pagina = str(int(pagina)+1)
    texto = "[COLOR mediumaquamarine]Pág: " + pag_actual + "[COLOR lime]                  Ir a Siguiente >>>[/COLOR]"        
    plugintools.add_item(action="abre_categoria", url=url, title=texto, page = pagina, extra=extra, genre="NOGESTIONAR", thumbnail="", fanart=fondo, folder=True, isPlayable=False)
    plugintools.add_item(action="main_list", url="", title="[COLOR orangered]···· Volver a Menú Principal ····[/COLOR]", extra=extra ,thumbnail=logo_volver, fanart=fondo, folder=True, isPlayable=False)
    



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
        #acota2 = 'style="right:6px;bottom:-383%">'
        #calidad = plugintools.find_single_match(item,acota2+'(.*?)</span')
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
        
        reemplaza = base64.b64decode(horus.encode('utf-8')).decode('utf-8').replace("MI-TORRENT" , torrent)
        reemplaza = reemplaza.replace("MI-ICONO" , logo)
        reemplaza = reemplaza.replace("MI-TITULO" , titulo)
        mivideo = "plugin://script.module.horus/?" + base64.b64encode(reemplaza.encode('utf-8')).decode('utf-8')
        
        #Comprobamos si alguno está en la BD de vistos, y si es así lo marco como visto.
        marcalo = ""
        if marcar_visto:
            if titulo in pelis_vistas:
                marcalo = "[COLOR green][B]√[/B][/COLOR]"
    
        titu = '[COLOR white]' + titulo + "[/COLOR]"
        titu = marcalo + titu
        
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
    pagina = params.get("page")

    xbmcplugin.setContent( int(sys.argv[1]) ,"tvshows" )
    
    #plugintools.log("*****************Pag: "+pagina+"********************")

    if len(extra) == 0: ## Si NO trae texto es q viene de Menú Ppal.
        busqueda = plugintools.keyboard_input('', 'Introduzca [COLOR red]Texto[/COLOR] a Buscar.')
        if len(busqueda) == 0:
            xbmc.executebuiltin('ActivateWindow(10000,return)')  ##Vuelvo al menú ppal.
        
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
        if "/pelicula/" in item:  ##Es película, por lo q lo cojo
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

            titulo = titul + "[COLOR orange]   -" + anio + "-[/COLOR]" + "   [COLOR blue]" + calidad + "[/COLOR]"
            
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
            
            reemplaza = base64.b64decode(horus.encode('utf-8')).decode('utf-8').replace("MI-TORRENT" , torrent)
            reemplaza = reemplaza.replace("MI-ICONO" , logo)
            reemplaza = reemplaza.replace("MI-TITULO" , titulo)
            mivideo = "plugin://script.module.horus/?" + base64.b64encode(reemplaza.encode('utf-8')).decode('utf-8')
            
            #Comprobamos si alguno está en la BD de vistos, y si es así lo marco como visto.
            marcalo = ""
            if marcar_visto:
                if titulo in pelis_vistas:
                    marcalo = "[COLOR green][B]√[/B][/COLOR]"
        
            titu = '[COLOR white]' + titulo + "[/COLOR]"
            titu = marcalo + titu
            
            datamovie = {}
            datamovie["Plot"] = sinopsis
            plugintools.add_item(action="lanza", url=mivideo, title=titu, extra=titulo, genre="NOGESTIONAR", thumbnail=logo, fanart=fondo, info_labels = datamovie, folder=False, isPlayable=False)
    
    if ">Siguiente<" in pagbusca:  ## Hay mas páginas
        pag_actual = pagina
        pagina = str(int(pagina)+1)
        texto = "[COLOR mediumaquamarine]Pág: " + pag_actual + "[COLOR lime]                  Ir a Siguiente >>>[/COLOR]"        
        plugintools.add_item(action="fBusca", url=url, title=texto, page = pagina, extra=extra, thumbnail=logo_siguiente, fanart=fondo, folder=True, isPlayable=False)
        plugintools.add_item(action="main_list", url="", title="[COLOR orangered]···· Volver a Menú Principal ····[/COLOR]", extra=extra ,thumbnail=logo_volver, fanart=fondo, folder=True, isPlayable=False)
            


def lanza(params):
    mivideo = params.get("url")
    logo = params.get("thumbnail")
    titu = params.get("title")
    titulo = params.get("extra")
    
    xbmc.Player().play(mivideo)

    if marcar_visto:
        import time
        time.sleep(80)  # Para darle tiempo a q el .isPlaying pueda detectar que está reproduciendo
        while xbmc.Player().isPlaying():
            time.sleep(1)

        if  not "[COLOR green][B]" in titu:  # El video NO está marcado aún como "Visto", así q lo marco
            marcar = True
            if pregunta_marcar:
                marcar  = xbmcgui.Dialog().yesno("¡¡Atención!!", "¿Desea Marcar como 'VISTO' este Video?:"+"\n\n"+titulo )
            if marcar:
                if sys.version_info[0] < 3:
                    fichero = open( vistos, "a" )
                else:
                    fichero = open( vistos, "a", encoding='utf-8' )

                fichero.write(titulo+"\n")  # Añado todo el Titulo completo del video al final del fichero de control
                fichero.close()




def salida(params):

	xbmc.executebuiltin('ActivateWindow(10000,return)')
	



	


	


		
run()

		




	

