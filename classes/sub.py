import datetime
from dataclasses import dataclass
from typing import Optional, Dict
import requests
import re
from bs4 import BeautifulSoup
from classes.member import Member
import json
import os
from functions.support import cwdpath

@dataclass
class Speech:
    speech_id: Optional[int]
    speaker_id: Optional[int]
    start_time: Optional[int]
    url: Optional[str]
    topic:[str]

    def print(self,last_topic:Optional[str]):
        # Check if last_topic is provided and different from the current topic
        if last_topic is not None and last_topic != self.topic:
            print('###############################')
            print(f'##   NEW TOPIC: {self.topic}')
            print('###############################')

        speaker = Member(self.speaker_id)

        print(f'\n-------')
        if speaker.party is None and speaker.role is not None:
            print(f'{speaker.name} ({speaker.role})')
        else:
            print(f'{speaker.name} ({speaker.party})')
        print(f'-------')
        return self.topic

@dataclass
class Sub:
    meeting_id: Optional[int] = None
    video_url: Optional[int] = None
    title: Optional[str] = None
    text: Optional[Dict[int,str]] = None
    speaker: Optional[Dict[int,Speech]] = None
    api: Optional[str] = None
    meeting_url: Optional[str] = None
    date: Optional[str] = None

    def __init__(self, meeting_id:Optional[int] = None,
                 video_url:Optional[int] = None,
                 title:Optional[int] = None,
                 text:Optional[Dict[int,str]] = None,
                 speaker:Optional[Dict[int,Speech]] = None,
                 api:Optional[str] = None,
                 meeting_url:Optional[str] = None,
                 date:Optional[str] = None):
        if meeting_id is not None and video_url is None and title is None and text is None and speaker is None and api is None and meeting_url is None and date is None:
            self.load_from_json(meeting_id)

    def load_from_json(self, meeting_id: int):
        file_path = cwdpath(os.path.join('json','subs',f'{meeting_id}.json'))
        if os.path.exists(file_path):
            #print(f'Loading JSON for subs {meeting_id}')
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.meeting_id = data['meeting_id']
                self.video_url = data['video_url']
                self.title = data['title']
                self.text = data['text']
                self.speaker = data['speaker']
                self.api = data['api']
                self.meeting_url = data['meeting_url']
                self.date = data['date']

            for timestamp in self.speaker:
                s = Speech(None, None, None, None, None)
                for property in self.speaker[timestamp]:
                    setattr(s, property, self.speaker[timestamp][property])
                self.speaker[timestamp] = s

        return True




    def __post_init__(self):
        self.text = {}
        self.speaker = {}

    def serialize(self):
        all_text = ''
        for timestamp in self.text:
            all_text += ' ' + self.text[timestamp]
        return all_text

    def contains_keyword(self, keyword: str):
        first = True
        for timestamp in self.text:
            if keyword in self.text[timestamp]:
                if first:
                    print(self.date)
                    first = False
                speaker = self._find_speaker_at_timestamp(timestamp)
                #speaker.print(None)

                all_keys = list(self.text.keys())
                match = all_keys.index(timestamp)
                #print(self.text[all_keys[match - 1]])
                print(f'{Member(speaker.speaker_id).name}: {self.text[all_keys[match]]}')
                #print(self.text[all_keys[match + 1]])


    def save(self):
        print(f"Saving subs: {self.meeting_id}")
        if self.meeting_id is None:
            print("Meeting ID must be set to save the subs.")
            return

        directory_path = cwdpath(os.path.join('json','subs'))
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, f"{self.meeting_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)


    def to_dict(self):
        dict = self.__dict__
        if 'speaker' in dict:
            for key in dict["speaker"]:
                dict["speaker"][key] = dict["speaker"][key].__dict__
        else:
            dict['speaker'] = None


        return dict

    def _find_speaker_at_timestamp(self,timestamp: int):
        all_keys = self.speaker.keys()
        speaker_timestamp = 0
        for n in all_keys:
            if int(speaker_timestamp) < int(n) < int(timestamp):
                speaker_timestamp = n

        return self.speaker[speaker_timestamp]


    def add_srt(self, srt_url: str):
        if srt_url is None:
            print('No SRT url provided')
            return None
        response = requests.get(srt_url)
        response.raise_for_status()
        srt_content = response.text

        #parse the .srt file
        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)',
                             re.DOTALL)
        matches = pattern.findall(srt_content)
        for match in matches:
            index,start_time,end_time,speech = match
            start_seconds = self._convert_to_seconds(start_time)
            if self.text is None:
                self.text = {}
            self.text[start_seconds] = speech.replace('\n',' ').replace('...',' ')

    def _get_meta_info_from_api(self, data ):
        self.meeting_id = data['event'][0]['@attributes']['id']
        self.title = data['event'][0]['title']
        self.date  = data['event'][0]['@attributes']['date']
        if 'media' in data['event'][0]:
            self.video_url = data['event'][0]['media']['video'][0]['download']
        else:
            self.video_url = None
            print(f'No video for:{self.meeting_id}')


    def add_speakers_from_eventAPI(self,event_api: str):
        print(event_api)
        try:
            response = requests.get(event_api)
            response.raise_for_status()
            data = response.json()
        except:
            print('INVALID')
            return

        #add api for future reference to the object
        self.api = event_api

        #add meeting,  video id and date
        self._get_meta_info_from_api(data)

        #add speakers
        for agenda_item in data['event'][0]['agenda']['agendaitem']:
            topic = agenda_item['title']
            if 'speaker_indexation' not in agenda_item:
                continue

            for entry in agenda_item['speaker_indexation']['speaker_index']:
                url = entry['url']
                speech_id = entry['@attributes']['id']
                speaker_id = entry['@attributes']['speaker_id']
                start_time = entry['@attributes']['start_time']

                speech = Speech(
                    speech_id=speech_id,
                    speaker_id = speaker_id,
                    start_time = start_time,
                    url = url,
                    topic = topic)
                if self.speaker is None:
                    self.speaker = {}
                self.speaker[start_time] = speech

        #add text
        #srt can be found on the html

        meeting_url =data['event'][0]['url']
        self.meeting_url = meeting_url
        srt_url = self._extract_srt_url_from_api()
        self.add_srt(srt_url)

    def print(self, n: int):

        printed_speech = 0
        t = 0
        last_topic = None

        while printed_speech < n:
            if t in self.speaker:
                last_topic = self.speaker[t].print(last_topic =last_topic)
            if t in self.text:
                print(self.text[t])
                printed_speech += 1

            t += 1

    def _extract_srt_url_from_api(self):
        response_meeting = requests.get(self.meeting_url)
        response_meeting.raise_for_status()

        soup = BeautifulSoup(response_meeting.content, 'html.parser')

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

    def _convert_to_seconds(self,time_str:str)->int:
        hours,minutes,seconds = time_str.split(':')
        seconds, milliseconds = seconds.split(',')
        return int(hours)*3600 + int(minutes)*60 + int(seconds)


