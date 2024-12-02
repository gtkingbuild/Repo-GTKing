import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import os
import urllib.request
import zipfile
import json
from urllib.parse import urlencode, parse_qsl

# Configuración para la gestión de dependencias
LIBRARIES_ZIP_URL = "https://hparlon6.github.io/bibliotecas.zip"
LIBRARIES_ZIP_PATH = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'bibliotecas.zip')
LIBRARIES_PATH = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'lib')
FIRST_RUN_FILE = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), "first_run.txt")

# Define el handle del addon
addon_handle = int(sys.argv[1])
BASE_URL = sys.argv[0]

# Obtener el addon y la ruta del addon
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
RESOURCES_PATH = os.path.join(addon_path, 'resources')

# Verificar si las bibliotecas ya están instaladas
def check_and_install_libraries():
    if not os.path.exists(LIBRARIES_PATH):
        xbmcgui.Dialog().notification("Instalando bibliotecas", "Descargando bibliotecas necesarias...", xbmcgui.NOTIFICATION_INFO)
        try:
            urllib.request.urlretrieve(LIBRARIES_ZIP_URL, LIBRARIES_ZIP_PATH)
            with zipfile.ZipFile(LIBRARIES_ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(LIBRARIES_PATH)
            os.remove(LIBRARIES_ZIP_PATH)
            xbmcgui.Dialog().notification("Addon", "Bibliotecas instaladas correctamente", xbmcgui.NOTIFICATION_INFO)
        except Exception as e:
            xbmcgui.Dialog().notification("Error", f"Error al instalar las bibliotecas: {str(e)}", xbmcgui.NOTIFICATION_ERROR)
            sys.exit()

# Verificar si es la primera ejecución e instalar bibliotecas
def verificar_prime_inicio():
    if not os.path.exists(FIRST_RUN_FILE):
        check_and_install_libraries()
        with open(FIRST_RUN_FILE, "w") as f:
            f.write("Primer inicio completado")

# Llamar a la función de verificación
verificar_prime_inicio()

# Agregar las bibliotecas a sys.path
sys.path.insert(0, LIBRARIES_PATH)

# Intentar importar los módulos requeridos
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    xbmcgui.Dialog().notification("Error", f"No se pudieron importar los módulos: {e}", xbmcgui.NOTIFICATION_ERROR)
    sys.exit()

# Función para construir URLs
def build_url(query):
    return BASE_URL + '?' + urlencode(query)

# Define categories with automatic icon path
CATEGORIES = [
    {"name": "AGENDA", "subcategories": [], "icon": f"{RESOURCES_PATH}/agenda.png"},
    {"name": "DEPORTES", "subcategories": [], "icon": f"{RESOURCES_PATH}/deportes.png"},
    {"name": "FÚTBOL", "subcategories": [], "icon": f"{RESOURCES_PATH}/futbol.png"},
    {"name": "CHAMPIONS", "subcategories": [], "icon": f"{RESOURCES_PATH}/champions.png"},
    {"name": "GOLF", "subcategories": [], "icon": f"{RESOURCES_PATH}/golf.png"},
    {"name": "DAZN", "subcategories": [], "icon": f"{RESOURCES_PATH}/dazn.png"},
    {"name": "F1", "subcategories": [], "icon": f"{RESOURCES_PATH}/f1.png"},
    {"name": "BALONCESTO", "subcategories": [], "icon": f"{RESOURCES_PATH}/baloncesto.png"},
]

# Define AceStream channels
ACESTREAM_CHANNELS = [
    # ... your existing AceStream channel definitions here ...
    {"name": "F1 | DAZN F1 1080", "url": "acestream://d6281d4e6310269b416180442a470d23a4a99dc9"},
    {"name": "F1 | DAZN F1 1080 | OPCION 2", "url": "acestream://2c6e4c897661e6b0257bfe931b66d20b2ec763b6"},
    {"name": "F1 | DAZN F1 1080 | OPCION 3", "url": "acestream://71eef80158aa8b37f3dc59f6793c6696df9a2dfa"},
    {"name": "F1 | DAZN F1 720", "url": "acestream://268289e7a3c5209960b53b4d43c8c65fab294b85"},
    {"name": "FÚTBOL | M. LA LIGA 1080", "url": "acestream://94d34491106e00394835c8cb68aa94481339b53f"},
    {"name": "FÚTBOL | M. LA LIGA 1080 | OPCION 2", "url": "acestream://d3de78aebe544611a2347f54d5796bd87f16c92d"},
    {"name": "FÚTBOL | M. LA LIGA 1080 | OPCION 3", "url": "acestream://6d05b31e5e8fdae312fbd57897363a7b10ddb163"},
    {"name": "FÚTBOL | M. LA LIGA 720", "url": "acestream://1bc437bce57b4b0450f6d1f8d818b7e97000745e"},
    {"name": "FÚTBOL | M. LA LIGA 2 1080", "url": "acestream://83c6c4942d69f4aa324aa746c5d7dbfd7d1572b3"},
    {"name": "FÚTBOL | M. LA LIGA 2 720", "url": "acestream://f31a586422c9244196c810c84b6c85da350318a5"},
    {"name": "FÚTBOL | M. LA LIGA 3 1080", "url": "acestream://ebe14f1edeb49f2253e3b355a8beeadc9b4f0bc4"},
    {"name": "FÚTBOL | LA LIGA BAR 1080", "url": "acestream://608b0faf7d3d25f6fe5dba13d5e4b4142949990e"},
    {"name": "FÚTBOL | LA LIGA BAR 1080 | OPCION 2", "url": "acestream://94d34491106e00394835c8cb68aa94481339b53f"},
    {"name": "FÚTBOL | DAZN LaLiga 1080", "url": "acestream://110d441ddc9713a7452588770d2bc85504672f47"},
    {"name": "FÚTBOL | DAZN LaLiga 1080 | OPCION 2", "url": "acestream://ec29289b0b14756e686c03a501bae1efa05be70c"},
    {"name": "FÚTBOL | DAZN LaLiga 1080 | OPCION 3", "url": "acestream://6de4794cd02f88f14354b5996823413a59a1de0f"},
    {"name": "FÚTBOL | DAZN LaLiga 720", "url": "acestream://8c8c1e047a1c5ed213ba74722a5345dc55c3c0eb"},
    {"name": "FÚTBOL | DAZN LaLiga 2 1080", "url": "acestream://97ba38d47680954be40e48bd8f43e17222fefecb"},
    {"name": "FÚTBOL | DAZN LaLiga 2 720", "url": "acestream://51dbbfb42f8091e4ea7a2186b566a40e780953d9"},
    {"name": "FÚTBOL | LaLiga Smartbank 1080", "url": "acestream://b2706a7ffbea236a3b398139a3a606ada664c0eb"},
    {"name": "FÚTBOL | LaLiga Smartbank 720", "url": "acestream://121f719ebb94193c6086ef92865cf9b197750980"},
    {"name": "FÚTBOL | LaLiga Smartbank 2 1080", "url": "acestream://0cfdfde1b70623b8c210b0f7301be2a87456481d"},
    {"name": "FÚTBOL | LaLiga Smartbank 2 720", "url": "acestream://0a335406bad0b658aeddb2d38f8c0614b2e5623a"},
    {"name": "FÚTBOL | LaLiga Smartbank 3", "url": "acestream://fefd45ed6ff415e05f1341b7d9da2988eacd13ea"},
    {"name": "DEPORTES | M.Plus 1080", "url": "acestream://56ac8e227d526e722624675ccdd91b0cc850582f"},
    {"name": "FÚTBOL | Copa 1080", "url": "acestream://f6beccbc4eea4bc0cda43b3e8ac14790a98b61b4"},
    {"name": "FÚTBOL | Copa 720", "url": "acestream://b51f2d9a15b6956a44385b6be531bcabeb099d9d"},
    {"name": "DEPORTES | #VAMOS 1080", "url": "acestream://d03c13b6723f66155d7a0df3692a3b073fe630f2"},
    {"name": "DEPORTES| #VAMOS 720", "url": "acestream://12ba546d229bc39f01c3c18988a034b215fe6adb"},
    {"name": "FÚTBOL | #ELLAS 1080", "url": "acestream://d8c2ed470e847154a88f011137cc206319f6bed5"},
    {"name": "DEPORTES | M. DEPORTES 1080", "url": "acestream://55d4602cb22b0d8a33c10c2c2f42dae64a9e8895"},
    {"name": "DEPORTES | M. DEPORTES 720", "url": "acestream://3a74d9869b13e763476800740c6625e715a39879"},
    {"name": "DEPORTES | M. DEPORTES 2 1080", "url": "acestream://639c561dd57fa3fc91fde715caeb696c5efb7ce7"},
    {"name": "DEPORTES | M. DEPORTES 3 1080", "url": "acestream://571bff4d12b1791eb99dbf20bec38e630693a6a3"},
    {"name": "DEPORTES | M. DEPORTES 4 1080", "url": "acestream://b4d1308a61e4caf8c06ac3d6ce89d165c015c2fb"},
    {"name": "DEPORTES | M. DEPORTES 5 1080", "url": "acestream://fcc0fd75bf1dba40b108fcf0d3514e0e549bfbac"},
    {"name": "DEPORTES | M. DEPORTES 6 1080", "url": "acestream://cc5782d37ae6b6e0bab396dd64074982d0879046"},
    {"name": "DEPORTES | M. DEPORTES 7 1080", "url": "acestream://070f82d6443a52962d6a2ed9954c979b29404932"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 1080 MULTIAUDIO", "url": "acestream://0a26e20f39845e928411e09a124374fccb6e1478"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 1080 MULTIAUDIO", "url": "acestream://775abd8697715c48a357906d40734ccd2a10513c"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 720", "url": "acestream://8edb264520569b2280c5e86b2dc734e120032903"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 2 1080", "url": "acestream://c070cdb701fc46bb79d17568d99fc64620443d63"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 2 720", "url": "acestream://abdf9058786a48623d0de51a3adb414ae10b6e72"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 3 1080", "url": "acestream://3618edda333dad5374ac2c801f5f14483934b97d"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 3 720", "url": "acestream://0b348cc1ae499e810729661878764a0fab88ab69"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 4 1080", "url": "acestream://65a18a6bd83918a9586b673fec12405aaf4e9f7d"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 5 1080", "url": "acestream://11744c25a594e17d587ed0871fe40ff21b4bd1e0"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 6 1080", "url": "acestream://fdda1f0dd8c33fbdc5a66ab98e291f570cae67cd"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 7 1080", "url": "acestream://b7f47db93dced60f54e8f89e2366ed061b534049"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 8 1080", "url": "acestream://d298c6e5c8be71f5995b45289c6388b225318b3c"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 9 SD", "url": "acestream://2d7c4cfb3987b652a779afc894cca2fccbbacf21"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 10 SD", "url": "acestream://c056f9e180cd7d40963129a17ff54f4ee8259353"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 11 SD", "url": "acestream://a12a16f74cf12799d4475ae867dc61eb60e1ba2e"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 12 SD", "url": "acestream://df7d145fcaf0566db4098d2f10236185d92bc9fd"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 13 SD", "url": "acestream://bdfe9ebe62d690c1b13eef4346d72e618cfbe804"},
    {"name": "GOLF | M. GOLF 1080", "url": "acestream://f41f1096862767289620be5bd85727f946a434db"},
    {"name": "GOLF | M. GOLF2 1080", "url": "acestream://e258e75e0e802afa5fcc53d46b47d8801a254ad5"},
    {"name": "DAZN 1 1080", "url": "acestream://7cf0086fa7d478f51dbba952865c79e66cb9add5"},
    {"name": "DAZN 1 720", "url": "acestream://35c7f0c966ecde3390f4510bb4caded40018c07a"},
    {"name": "DAZN 2 1080", "url": "acestream://ca923c9873fd206a41c1e83ff8fc40e3cf323c9a"},
    {"name": "DAZN 2 720", "url": "acestream://a929eeec1268d69d1556a2e3ace793b2577d8810"},
    {"name": "DAZN 3 1080", "url": "acestream://19cd05c7ae26f22737ae5728b571ca36abd8a2e8"},
    {"name": "DAZN 4 1080", "url": "acestream://4e83f23945ab3e43982045f88ec31daaa4683102"},
    {"name": "DEPORTES | EUROSPORT 1 1080", "url": "acestream://16ffa1713f42aa27317ee039a2bd0cdbc89a1580"},
    {"name": "DEPORTES | EUROSPORT 2 1080", "url": "acestream://98784fa0714190de289f42eb5b84e405df7e685a"},
    {"name": "DEPORTES | REAL MADRID TV 1080", "url": "acestream://0ec3f3786318acd8dca2588f74c3759cda76cd11"},
    {"name": "DEPORTES | REAL MADRID TV 720", "url": "acestream://0827cf7d290967985892965c6e61244a479d6dcd"},
    {"name": "DEPORTES | WIMBLEDON UHD", "url": "acestream://78aa81aedb1e2b6a9ba178398148940857155f6a"},
    {"name": "DEPORTES | MUNDO TORO HD", "url": "acestream://f763ab71f6f646e6c993f37e237be97baf2143ef"},
    {"name": "BALONCESTO | NBA", "url": "acestream://e72d03fb9694164317260f684470be9ab781ed95"},
    {"name": "BALONCESTO | NBA USA 1", "url": "acestream://39db49bc89dcc3c8797566231f869dca57f1a47e"},
    {"name": "BALONCESTO | NBA USA 2", "url": "acestream://f1c84ec8ea0c0bfff8a24272b66c64354a522110"},
    {"name": "DEPORTES | RED BULL TV", "url": "acestream://6994af284ecab2996f9b140ef44b8da8bfee0006"},
    {"name": "DEPORTES | UFC CHANNEL", "url": "acestream://7cf437be950f3525e735be57c63f7824cab822c9"},
    {"name": "DEPORTES | FOX SPORTS 2", "url": "acestream://ad6f4e8e329d6a97c7e7d7b0b8e5d04d8dd0bb48"},
]

# Define HTML5 channels
HTML5_CHANNELS = [
    # ... add more HTML5 channels here ...
]

# Función para construir URLs
def build_url(query):
    return BASE_URL + '?' + urlencode(query)

# Buscar enlace AceStream por nombre
def buscar_enlace_por_nombre(nombre):
    nombre = nombre.lower()
    for canal in ACESTREAM_CHANNELS:
        if nombre in canal["name"].lower():
            return canal["url"]
    return None

def list_categories():
    for category in CATEGORIES:
        list_item = xbmcgui.ListItem(label=category["name"])
        list_item.setArt({"icon": category["icon"]})
        url = build_url({"action": "list_channels", "category": category["name"]})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_channels(category):
    selected_category = next((cat for cat in CATEGORIES if cat["name"] == category), None)
    if not selected_category:
        xbmcgui.Dialog().notification("Error", "Categoría no encontrada", xbmcgui.NOTIFICATION_ERROR)
        return
    if category == "AGENDA":
        list_agenda_events()
        return
    for channel in ACESTREAM_CHANNELS:
        if channel["name"].upper().startswith(category.upper()):
            list_item = xbmcgui.ListItem(label=channel["name"])
            url = build_url({"action": "play_acestream", "url": channel["url"]})
            list_item.setInfo("video", {"title": channel["name"]})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)

def obtener_eventos_desde_html():
    url = "http://141.145.210.168"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        eventos = []
        tabla_eventos = soup.find('table', class_='styled-table')
        for fila in tabla_eventos.find_all('tr')[1:]:
            columnas = fila.find_all('td')
            if len(columnas) >= 5:
                hora = columnas[0].text.strip()
                categoria = columnas[1].text.strip()
                equipo_1 = columnas[2].text.strip()
                equipo_2 = columnas[3].text.strip()
                enlaces = [{"name": enlace.text.strip(), "url": enlace['href']} for enlace in columnas[4].find_all('a')]
                if enlaces:
                    eventos.append({
                        'hora': hora,
                        'categoria': categoria,
                        'evento': f"{equipo_1} vs {equipo_2}",
                        'enlaces': enlaces
                    })
        return eventos
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().notification("Error", f"Error al obtener eventos: {e}", xbmcgui.NOTIFICATION_ERROR)
        return []

def list_agenda_events():
    eventos = obtener_eventos_desde_html()
    if not eventos:
        xbmcgui.Dialog().notification("Agenda", "No hay eventos disponibles", xbmcgui.NOTIFICATION_INFO)
        return
    for evento in eventos:
        titulo = f"{evento['hora']} | {evento['categoria']} | {evento['evento']}"
        list_item = xbmcgui.ListItem(label=titulo)
        url = build_url({"action": "mostrar_enlaces_evento", "enlaces": json.dumps(evento["enlaces"])})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def mostrar_enlaces_evento(enlaces):
    enlaces = json.loads(enlaces)
    for enlace in enlaces:
        list_item = xbmcgui.ListItem(label=enlace["name"])
        url = build_url({"action": "play_acestream", "url": enlace["url"]})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)

def play_html5(url):
    try:
        xbmc.Player().play(url)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)

# Reproducir enlace AceStream
def play_acestream(url):
    """
    Reproduce un enlace AceStream utilizando el addon Horus.
    """
    try:
        # Extraer solo el ID del enlace AceStream (eliminar 'acestream://')
        acestream_id = url.replace("acestream://", "")
        
        # Construir la URL para el addon Horus
        horus_url = f"plugin://script.module.horus/?action=play&id={acestream_id}"
        
        # Reproducir utilizando Horus
        xbmc.Player().play(horus_url)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", f"Error al reproducir: {e}", xbmcgui.NOTIFICATION_ERROR)

if __name__ == '__main__':
    args = dict(parse_qsl(sys.argv[2][1:]))
    action = args.get("action")
    if action == "list_channels":
        category = args.get("category")
        if category == "AGENDA":
            list_agenda_events()
        else:
            list_channels(category)
    elif action == "mostrar_enlaces_evento":
        mostrar_enlaces_evento(args["enlaces"])
    elif action == "play_html5":
        play_html5(args["url"])
    elif action == "play_acestream":
        play_acestream(args["url"])
    else:
        list_categories()