from datetime import datetime
from classes.meeting import Meeting
from classes.meetingManager import MeetingManager
import requests
from functions.download import web
import re


def getData(fromDate,today,gremium):
    organisation = 686
    page = 1

    api_url = "https://api.notubiz.nl/events?organisation_id=" + str(organisation) + "&gremia_ids[]=" + str(
        gremium) + "&date_from=" + fromDate + "%2000:00:00&date_to=" + today + "%2023:59:59&version=1.10.8&page=" + str(
        page) + '&format=json'

    # get data
    return api(api_url)

def api(api_url):
    if not api_url.startswith('http'):
        api_url = f'http://{api_url}'
    if not api_url.endswith('json'):
        api_url = f'{api_url}?&format=json'
    response = requests.get(api_url)
    if response.status_code == 400:
        return None
    data = response.json()
    return data

def convert_to_seconds(time_str:str)->int:
    hours,minutes,seconds = time_str.split(':')
    seconds, milliseconds = seconds.split(',')
    return int(hours)*3600 + int(minutes)*60 + int(seconds)


def get_srt_url_from_soup(soup):
    script_tag = soup.find('script', text=re.compile(r'subtitles_file\s*:\s*'))
    if script_tag:
        script_content = script_tag.string
    else:
        return None

    # Step 4: Use regular expressions to find the subtitles file URL
    pattern = re.compile(r'subtitles_file\s*:\s*"([^"]+)"')
    match = pattern.search(script_content)

    if match:
        subtitles_url = match.group(1)
        print(f"Subtitles file URL: {subtitles_url}")
        return subtitles_url
    else:
        print("Subtitles file URL not found.")
        return None

def get_srt_url(m):
    if m.meeting_subid is None:
        soup = web.visitPage(m.meeting_url)
        url = get_srt_url_from_soup(soup)
    else:
        url = {}
        for room in m.meeting_subid:
            submeeting_url = m.getsubmeeting_url(room)
            soup = web.visitPage(submeeting_url)
            url[room] = get_srt_url_from_soup(soup)
    return url


def get_srt(m,srt_url):
    subtitles = {}
    response = requests.get(srt_url)
    response.raise_for_status()
    srt_content = response.text

    # parse the .srt file
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)',
                         re.DOTALL)
    matches = pattern.findall(srt_content)
    for match in matches:
        index, start_time, end_time, speech = match
        start_seconds = convert_to_seconds(start_time)
        subtitles[start_seconds] = speech.replace('\n', ' ').replace('...', ' ')
    return subtitles

def add_srt(m,srt_url):
    if srt_url is None:
        print(f' skipping {m.meeting_id}')
        return

    if m.subtitles is None:
        m.subtitles = {}

    if isinstance(srt_url,dict):
        for room in srt_url:
            if srt_url[room]:
                m.subtitles[room] = get_srt(m,srt_url[room])
            else:
                m.subtitles[room] = None
                print(f'No subs for: {room}')
    elif isinstance(srt_url,str):
        m.subtitles['Raadzaal'] = get_srt(m,srt_url)



def add_speakers_from_url(m,url,room):
    if room is None:
        room = 'Raadzaal'

    soup = web.visitPage(url)


    for speaker in soup.findAll('li', class_='speaker_index'):
        mic = m.addMic(int(speaker.attrs['data-start_offset']),room)
        mic.end = int(speaker.attrs['data-end_offset'])
        mic.id = int(speaker.attrs['data-speaker_id'])

    # making use of that soup is loaded:
    if m.title is None or 'Unknown' in m.title or str(m.meeting_id) in m.title:
        m.title = {}

    if isinstance(m.title,str):
        m.title = {}
    m.title[room] = soup.find('title').text


def add_speakers(m):
    if m.speakers is None:
        m.speakers = {}

    if m.meeting_subid is not None:
        for room in m.meeting_subid:
            add_speakers_from_url(m,m.getsubmeeting_url(room),room)
    else:
        add_speakers_from_url(m,m.meeting_url,'Raadzaal')


def update_meetings(fromDate):
    MeeMa = MeetingManager()
    MeeMa.addall()
    MeeMa.sort_chronological()
    #for meeting in MeeMa.meetings:
    #misschien een andere keer afmaken




def download_meetings(fromDate):
    today = datetime.today().strftime('%Y-%m-%d')
    fromDate = fromDate.strftime('%Y-%m-%d')
    gremia = [1011,12330]  #1101: raadsvergadering,  12330:raadsavond

    for gremium in gremia:
        data = getData(fromDate,today,gremium)
        for event in data['events']:
            m=Meeting(event['id'])
            m.api_url = event['self']
            m.meeting_url = f'https://raadsinformatie.eindhoven.nl/vergadering/{m.meeting_id}/'
            m.type = event['attributes'][0]['value']
            m.date = event['plannings'][0]['start_date']



            api_info = api(m.api_url)
            if api_info is None:
                continue
            #get video
            if gremium==1011: #raadsvergadering heeft 1 stream
                location = 'Raadzaal'

                try:
                    httpstreamer = api_info['event'][0]['media']['video'][0]['httpstreamer']
                    httpname = api_info['event'][0]['media']['video'][0]['httpstreamname']
                    if isinstance(m.video_url,str) or m.video_url is None:
                        m.video_url = {}
                    m.video_url['Raadzaal'] = f'{httpstreamer}/{httpname}'
                except:
                    print('video link via API failed, trying soup now')
                    m.getVideolinkFromURL(m.meeting_url)
                    print('Soup was succesful')


                #Add full agenda:
                for ai in api_info['event'][0]['agenda']['agendaitem']:
                    key = ai['@attributes']['start_offset']
                    value = {}
                    value['title'] = ai['title']
                    value['id'] = ai['@attributes']['id']
                    value['module_id'] = []

                    if m.agenda is None:
                        m.agenda = {}
                        m.agenda['Raadzaal'] = {}
                    m.agenda['Raadzaal'][key] = value

            elif gremium == 12330:
                if 'rooms' in api_info['event'][0]:
                    for room in api_info['event'][0]['rooms']['room']:
                        for event in room['events']['event']:
                            if 'media' in event:
                                httpstreamer = event['media']['video'][0]['httpstreamer']
                                httpname = event['media']['video'][0]['httpstreamname']
                                location = event['location']
                                if m.video_url is None:
                                    m.video_url = {}
                                m.video_url[location] = f'{httpstreamer}/{httpname}'

                                if m.meeting_subid is None:
                                    m.meeting_subid = {}
                                m.meeting_subid[location] = event['@attributes']['id']

                                # Add full agenda:
                                for ai in event['agenda']['agendaitem']:
                                    key = ai['@attributes']['start_offset']
                                    value = {}
                                    value['title'] = ai['title']
                                    value['id'] = ai['@attributes']['id']
                                    value['module_id'] = []

                                    if m.agenda is None:
                                        m.agenda = {}

                                    if location not in m.agenda:
                                        m.agenda[location] = {}

                                    m.agenda[location][key] = value

            #Add subtitles:
            if location and not m.subtitles:
                m.subtitles = {}
                m.subtitles[location] = None
            if location and not m.subtitles[location]:
                srt_url = get_srt_url(m)
                if srt_url:
                    add_srt(m,srt_url)
            add_speakers(m)

            m.save()



