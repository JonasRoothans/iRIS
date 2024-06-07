import datetime
from dataclasses import dataclass
from typing import Optional, Dict
import requests
import re
from bs4 import BeautifulSoup
from classes.member import Member

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
    video_id: Optional[int] = None
    title: Optional[str] = None
    text: Optional[Dict[int,str]] = None
    speaker: Optional[Dict[int,Speech]] = None
    api: Optional[str] = None
    meeting_url: Optional[str] = None

    def __post_init__(self):
        self.text = {}
        self.speaker = {}


    def add_srt(self, srt_url: str):
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
            self.text[start_seconds] = speech.replace('\n',' ').replace('...',' ')



    def add_speakers_from_eventAPI(self,event_api: str):
        response = requests.get(event_api)
        response.raise_for_status()
        data = response.json()

        #add api for future reference to the object
        self.api = event_api

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
            raise ValueError("Script tag containing subtitles information not found.")

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
        return int(hours*3600) + int(minutes)*60 + int(seconds)


