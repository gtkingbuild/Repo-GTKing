from flask import Flask, request, Response, jsonify
#from werkzeug.serving import make_server
import urllib.parse
import requests
import binascii
import os
import re
import time
import logging
from urllib.parse import urljoin
from requests.exceptions import ConnectionError, RequestException
from urllib3.exceptions import IncompleteRead
from doh import DNSOverrideDoH


PORT = 8088

app = Flask(__name__)
app.debug = True

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

IP_CACHE_TS = {}
IP_CACHE_MP4 = {}
AGENT_OF_CHAOS = {}
COUNT_CLEAR = {}

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_ip():
    forwarded_for = request.headers.get("X-Forwarded-For")
    real_ip = request.headers.get("X-Real-IP")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    elif real_ip:
        ip = real_ip
    else:
        ip = request.remote_addr
    return ip

def get_cache_key(client_ip: str, url: str) -> str:
    return f"{client_ip}:{url}"

def rewrite_m3u8_urls(playlist_content: str, base_url: str) -> str:
    def replace_url(match):
        segment_url = match.group(0).strip()
        if segment_url.startswith('#') or not segment_url or segment_url == '/':
            return segment_url
        try:
            absolute_url = urljoin(base_url + '/', segment_url)
            if not (absolute_url.endswith('.ts') or '/hl' in absolute_url.lower() or absolute_url.endswith('.m3u8')):
                logging.debug(f"[HLS Proxy] Ignorando URL inválida no m3u8: {absolute_url}")
                return segment_url
            scheme = request.scheme
            host = request.host
            proxied_url = f"{scheme}://{host}/hlsretry?url={urllib.parse.quote(absolute_url)}"
            return proxied_url
        except ValueError as e:
            logging.debug(f"[HLS Proxy] Erro ao resolver URL {segment_url}: {e}")
            return segment_url

    return re.sub(r'^(?!#)\S+', replace_url, playlist_content, flags=re.MULTILINE)

def stream_response(response, client_ip, url, headers, sess):
    cache_key = get_cache_key(client_ip, url) if any(ext in url.lower() for ext in ['.mp4', '.m3u8']) else client_ip
    mode_ts = False

    def generate_chunks():
        nonlocal mode_ts
        bytes_read = 0
        try:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    bytes_read += len(chunk)
                    if '.mp4' in url.lower():
                        IP_CACHE_MP4.setdefault(cache_key, []).append(chunk)
                        if len(IP_CACHE_MP4[cache_key]) > 20:
                            IP_CACHE_MP4[cache_key].pop(0)
                    elif '.ts' in url.lower() or '/hl' in url.lower():
                        mode_ts = True
                        IP_CACHE_TS.setdefault(cache_key, []).append(chunk)
                        if len(IP_CACHE_TS[cache_key]) > 20:
                            IP_CACHE_TS[cache_key].pop(0)
                    yield chunk
        except (IncompleteRead, ConnectionError) as e:
            logging.debug(f"[HLS Proxy] Erro ao processar chunks (bytes lidos: {bytes_read}): {e}")
            cache = IP_CACHE_TS if mode_ts else IP_CACHE_MP4
            for chunk in cache.get(cache_key, [])[-5:]:
                yield chunk
        finally:
            try:
                sess.close()
            except:
                pass

    return generate_chunks()

def stream_cache(client_ip, url):
    if url:
        cache_key = get_cache_key(client_ip, url) if any(ext in url.lower() for ext in ['.mp4', '.m3u8']) else client_ip
        if '.mp4' in url.lower():
            cache = IP_CACHE_MP4
        elif '.ts' in url.lower() or '/hl' in url.lower():
            cache = IP_CACHE_TS
        else:
            cache = None
        if cache:
            def generate_cached_chunks():
                if cache_key in cache:
                    for chunk in cache.get(cache_key, [])[-5:]:
                        yield chunk
                else:
                    logging.debug(f"[HLS Proxy] Cache vazio para {cache_key}")
            return generate_cached_chunks()
    return None

@app.route("/hlsretry")
def hls_retry():
    DNSOverrideDoH()
    url = request.args.get('url')
    client_ip = get_ip()
    cache_key = get_cache_key(client_ip, url) if url and any(x in url.lower() for x in ['.mp4', '.m3u8']) else client_ip

    if not url:
        return jsonify({"detail": "No URL provided"}), 400

    session = requests.Session()
    headers_master = dict(request.headers)
    original_headers = {}
    headers = {}
    for k, v in headers_master.items():
        if k.lower() == 'host':
            continue
        else:
            headers[k] = v
            original_headers[k] = v 
    max_retries = 7
    attempts = 0
    tried_without_range = False
    change_user_agent = False

    media_type = (
        'video/mp4' if '.mp4' in url.lower()
        else 'video/mp2t' if '.ts' in url.lower() or '/hl' in url.lower()
        else 'application/octet-stream'
    )
    response_headers = {}
    status = 200

    while attempts < max_retries:
        try:
            range_header = headers.get('Range')
            if '.mp4' in url.lower() and range_header and tried_without_range:
                headers.pop('Range', None)

            if AGENT_OF_CHAOS.get(cache_key) and not '.ts' in url.lower() and not '/hl' in url.lower():
                if not change_user_agent:
                    headers['User-Agent'] = original_headers.get('User-Agent', DEFAULT_USER_AGENT)
                else:
                    headers['User-Agent'] = AGENT_OF_CHAOS[cache_key]
            if '.ts' in url.lower() or '/hl' in url.lower():
                if change_user_agent or not headers.get('User-Agent'):
                    headers['User-Agent'] = binascii.b2a_hex(os.urandom(20))[:32]
                else:
                    headers['User-Agent'] = original_headers.get('User-Agent', DEFAULT_USER_AGENT)

            response = session.get(url, headers=headers, allow_redirects=True, stream=True, timeout=9)

            if response.status_code in (200, 206):
                if '.mp4' in url.lower() or '.m3u8' in url.lower():
                    url = response.url
                change_user_agent = False
                if client_ip in COUNT_CLEAR:
                    if COUNT_CLEAR.get(client_ip, 0) > 4:
                        #logging.debug('LIMPANDO CACHES')
                        try:
                            if cache_key in AGENT_OF_CHAOS:
                                del AGENT_OF_CHAOS[cache_key]
                            # Limpar caches quando a requisição for bem-sucedida
                            if cache_key in IP_CACHE_MP4:
                                del IP_CACHE_MP4[cache_key]
                            if cache_key in IP_CACHE_TS:
                                del IP_CACHE_TS[cache_key]
                        except:
                            pass
                if not client_ip in COUNT_CLEAR:
                    COUNT_CLEAR[client_ip] = 0
                elif int(COUNT_CLEAR.get(client_ip, 0) > 4):
                    #logging.debug('ZERANDO COUNT CLEAR')
                    COUNT_CLEAR[client_ip] = 0
                else:
                    if client_ip in COUNT_CLEAR:
                        COUNT_CLEAR[client_ip] = COUNT_CLEAR.get(client_ip, 0) + 1                    
                content_type = response.headers.get("content-type", "").lower()

                if "mpegurl" in content_type or ".m3u8" in url.lower():
                    base_url = url.rsplit('/', 1)[0]
                    playlist_content = response.content.decode('utf-8', errors='ignore')
                    rewritten = rewrite_m3u8_urls(playlist_content, base_url)
                    return Response(rewritten, content_type="application/x-mpegURL")
                
                # expirimental segment
                if '/hl' in url.lower() and '_' in url.lower() and '.ts' in url.lower():
                    try:
                        seg_ = re.findall(r'_(.*?)\.ts', url)[0]
                        seg_before = f'_{seg_}.ts'
                        seg_after = f'_{str(int(seg_) + 1)}.ts'
                        url = url.replace(seg_before, seg_after)
                    except:
                        pass

                media_type = (
                    'video/mp4' if '.mp4' in url.lower()
                    else 'video/mp2t' if '.ts' in url.lower() or '/hl' in url.lower()
                    else response.headers.get("content-type", "application/octet-stream")
                )

                response_headers = {
                    k: v for k, v in response.headers.items()
                    if k.lower() in ['content-type', 'accept-ranges', 'content-range']
                }

                status = 206 if response.status_code == 206 else 200

                return Response(
                    stream_response(response, client_ip, url, headers, session),
                    headers=response_headers,
                    content_type=media_type,
                    status=status
                )

            elif response.status_code == 416 and range_header and not tried_without_range:
                tried_without_range = True
                continue
            else:
                change_user_agent = True
                logging.debug(f"Erro código {response.status_code}, tentativa {attempts}")
                AGENT_OF_CHAOS[cache_key] = binascii.b2a_hex(os.urandom(20))[:32]
                time.sleep(3)
                attempts += 1
                if '.ts' in url.lower() or '/hl' in url.lower() or '.mp4' in url.lower():
                    return Response(
                        stream_cache(client_ip, url),
                        headers=response_headers,
                        content_type=media_type,
                        status=status
                    )                       
        except RequestException as e:
            change_user_agent = True
            logging.debug(f"Erro desconhecido: {e}")
            AGENT_OF_CHAOS[cache_key] = binascii.b2a_hex(os.urandom(20))[:32]
            time.sleep(3)
            attempts += 1
            if '.ts' in url.lower() or '/hl' in url.lower() or '.mp4' in url.lower():
                return Response(
                    stream_cache(client_ip, url),
                    headers=response_headers,
                    content_type=media_type,
                    status=status
                )              

    return jsonify({"detail": "Falha ao conectar após múltiplas tentativas"}), 502


@app.route("/tsdownloader")
def ts_downloader():
    DNSOverrideDoH()
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    
    headers_master = dict(request.headers)
    headers = {}
    for k, v in headers_master.items():
        if k.lower() == 'host':
            continue
        else:
            headers[k] = v 

    stop_ts = False

    #session = requests.Session()
    last_url = ''

    def generate_ts():
        nonlocal last_url
        nonlocal stop_ts
        while not stop_ts:
            try:                
                # headers = {
                #     "User-Agent": binascii.b2a_hex(os.urandom(20))[:32],
                #     "Accept-Encoding": "identity",
                #     "Accept": "*/*",
                #     "Connection": "keep-alive"
                # } 
                if not last_url:
                    last_url = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=5).url 
                with requests.get(last_url, headers=headers, stream=True, timeout=15) as response:
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=4096):
                            if stop_ts:
                                logging.warning("[TS Downloader] Stream interrompido pelo cliente.")
                                return
                            if chunk:
                                try:
                                    yield chunk
                                except (ConnectionResetError, BrokenPipeError, GeneratorExit) as e:
                                    stop_ts = True
                                    logging.warning(f"[TS Downloader] Cliente desconectou: {e}")
                                    return
                    else:
                        logging.warning(f"[TS Downloader] Resposta HTTP {response.status_code}")
            except Exception as e:
                logging.warning(f"[TS Downloader] Erro no stream: {e}")
        logging.warning(f"[TS Downloader] Stream encerrado pelo cliente")

    resp = Response(generate_ts(), content_type='video/mp2t')

    @resp.call_on_close
    def on_close():
        nonlocal stop_ts
        logging.info("Cliente desconectado (on_close).")
        stop_ts = True

    return resp



@app.route("/")
def index():
    return jsonify({"message": "F4MTESTER PROXY v4.2.5"})


def server_run():
    app.run(host='127.0.0.1', port=PORT, debug=False)



