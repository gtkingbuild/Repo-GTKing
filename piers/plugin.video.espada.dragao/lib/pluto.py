# -*- coding: utf-8 -*-

try:
    from lib.helper import *
except:
    from helper import *
import uuid
from datetime import datetime, timedelta
try:
    from lib.ClientScraper import cfscraper, USER_AGENT
except ImportError:
    from ClientScraper import cfscraper, USER_AGENT



#from_date = datetime.utcnow()
def get_current_time():
    response = requests.get('http://worldtimeapi.org/api/timezone/America/Sao_Paulo')
    if response.status_code == 200:
        data = response.json()
        datetime_str = data['datetime']
        # Ajusta o fuso horário para o formato padrão (corrige o erro do fuso horário)
        if datetime_str.endswith('-03:0'):
            datetime_str = datetime_str[:-1] + '0'
        elif datetime_str.endswith('-03:0'):
            datetime_str = datetime_str[:-1] + '00'
        elif datetime_str.endswith('+00:0'):
            datetime_str = datetime_str[:-1] + '00'
        
        # Converte a string em datetime
        current_time = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        return current_time
    else:
        raise Exception("Failed to get time from API")


def playlist_pluto():
    channels_kodi = []
    channels_info = []

    try:
        deviceid = str(uuid.uuid4())
        days_to_add = 1
        time_brazil = get_current_time()
        from_date = time_brazil
        # from_date2 = datetime.utcnow()
        to_date = from_date + timedelta(days=days_to_add)
        from_str = from_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        to_str = to_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = "http://api.pluto.tv/v2/channels?start={}&stop={}".format(from_str, to_str)
        channels = cfscraper.get(url).json()
        
        for channel in channels:
            if channel.get('number', 0) > 0:
                channel_info = {
                    'name': channel.get('name'),
                    'thumbnail': channel.get('logo', {}).get('path'),
                    'current_program': None,
                    'next_program': None,
                    'url': None
                }
                
                url = channel.get('stitched', {}).get('urls', [{}])[0].get('url')
                if url:
                    url = url.replace('&deviceMake=', '&deviceMake=Firefox')
                    url = url.replace('&deviceType=', '&deviceType=web')
                    url = url.replace('&deviceId=unknown', '&deviceId={0}'.format(deviceid))
                    url = url.replace('&deviceModel=', '&deviceModel=web')
                    url = url.replace('&deviceVersion=unknown', '&deviceVersion=82.0')
                    url = url.replace('&appName=&', '&appName=web&')
                    url = url.replace('&appVersion=&', '&appVersion=5.9.1-e0b37ef76504d23c6bdc8157813d13333dfa33a3')
                    url = url.replace('&sid=', '&sid={0}&sessionID={1}'.format(deviceid,deviceid))
                    url = url.replace('&deviceDNT=0', '&deviceDNT=false')
                    url = "{0}&serverSideAds=false&terminate=false&clientDeviceType=0&clientModelNumber=na&clientID={1}".format(url,deviceid)
                    url = url + '|User-Agent=' + quote_plus(USER_AGENT)
                    
                    channel_info['url'] = url

                now = None
                for timeline in channel.get('timelines', []):
                    current_program_start = datetime.fromisoformat(timeline['start'].replace('Z', '+00:00'))
                    current_program_end = datetime.fromisoformat(timeline['stop'].replace('Z', '+00:00'))
                    if current_program_start <= time_brazil <= current_program_end:
                        now = current_program_end
                        channel_info['current_program'] = {
                            'title': timeline['episode']['name'],
                            'description': timeline['episode'].get('description', ''),
                            'start_time': current_program_start.isoformat(),
                            'end_time': current_program_end.isoformat()
                        }
                    if now:
                        if current_program_start <= now < current_program_end:
                            channel_info['next_program'] = {
                            'title': timeline['episode']['name'],
                            'description': timeline['episode'].get('description', ''),
                            'start_time': current_program_start.isoformat(),
                            'end_time': current_program_end.isoformat()
                            }              

                channels_info.append(channel_info)
    except:
        pass
    time_format = "%Y-%m-%dT%H:%M:%S%z"
    if channels_info:
        for n, channel in enumerate(channels_info):
            desc = ''
            number = str(n+1)
            channel_name = channel.get('name', number)
            thumbnail = channel.get('thumbnail', '')
            stream = channel.get('url', '')
            current_program = channel.get('current_program', '')
            program_now = current_program.get('title', '')
            program_now_start = current_program.get('start_time', '')
            desc_program_now = current_program.get('description', '')
            program_end = channel.get('next_program', '')
            program_end_title = program_end.get('title', '')
            program_end_start = program_end.get('start_time', '')
            desc_program_end = program_end.get('description', '')

            if program_now_start:
                time_obj = datetime.strptime(program_now_start, time_format)
                new_time_obj = time_obj - timedelta(hours=3)
                start = new_time_obj.strftime("%H:%M")
                desc += '[COLOR yellow][{0}] {1}[/COLOR]\n({2})\n'.format(start,program_now,desc_program_now)
            if program_end:
                time_obj_ = datetime.strptime(program_end_start, time_format)
                new_time_obj_ = time_obj_ - timedelta(hours=3)
                start_ = new_time_obj_.strftime("%H:%M")
                desc += '[COLOR yellow][{0}] {1}[/COLOR]\n({2})\n'.format(start_,program_end_title,desc_program_end)
            if program_now:
                channel_name = channel_name + ' - [COLOR yellow]' + program_now + '[/COLOR]'
            channels_kodi.append((channel_name,desc,thumbnail,stream))
    return channels_kodi

