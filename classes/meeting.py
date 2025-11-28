import os
from dataclasses import dataclass, asdict, field
from classes.member import Member
from functions.support import cwdpath
from datetime import datetime
from functions.download import web
import re
import yake
import json
from typing import Optional, Dict

@dataclass
class Mic:
    start: Optional[int] = None
    end: Optional[int]= None
    id: Optional[int] = None

@dataclass
class Meeting:
    meeting_id: Optional[int] = None
    meeting_subid: Optional[int] = None
    subtitles: Optional[str] = None
    speakers: Optional[Dict[int,Mic]] = None
    title: Optional[str] = None
    meeting_url: Optional[str] = None
    video_url: Optional[str] = None
    api_url: Optional[str] = None
    date: Optional[str] = None
    type: Optional[str] = None
    agenda: Optional[Dict[int, str]] = None

    def __init__(self,meeting_id):
        super().__init__
        # Add custom initialization logic
        if meeting_id is not None:
            self.meeting_id = meeting_id
            self.load_from_json(meeting_id)

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Meeting(name={self.title})'

    def __eq__(self, other):
        if isinstance(other, Meeting):
            return self.meeting_id == other.meeting_id
        return False
    
    def load_from_json(self, meeting_id: str):
        if isinstance(meeting_id,str):
            if meeting_id[-5:] == '.json':
                meeting_id = meeting_id[0:-5]
            if 'vergadering' in meeting_id:
                meeting_id = int(meeting_id.split('vergadering/')[1].split('/')[0].split('#')[0])


        file_path = cwdpath(os.path.join('json','meetings',f'{meeting_id}.json'))

        #Check if filepath exists
        if not os.path.exists(file_path):
            from classes.meetingManager import MeetingManager
            #check if id is a subid:
            MeMa = MeetingManager()
            MeMa.addall()
            found_match = 0
            for parentmeeting in MeMa.meetings:
                if meeting_id in list(parentmeeting.meeting_subid.values()):
                    file_path = cwdpath(os.path.join('json', 'meetings', f'{parentmeeting.meeting_id}.json'))
                    if os.path.exists(file_path):
                        found_match = 1
                        break #subid was found

            if not found_match:
                self.title = f'Vergadering: {meeting_id}'
                print(f'New meeting created: {meeting_id}')
                self.meeting_id = int(meeting_id)
                return
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except:
                print(f'FILE CORRUPTED ---------> {file}')
                return None
            self.meeting_id = data['meeting_id']
            if 'meeting_subid' in data:
                self.meeting_subid = data['meeting_subid']
            if 'subtitles' in data:
                self.subtitles = data['subtitles']
            if 'speakers' in data:
                self.speakers = {}
                speakers = data['speakers']
                if speakers is not None:
                    for room in speakers:
                        self.speakers[room] = {}
                        for timestamp in speakers[room]:
                            s = Mic(None, None, None)
                            for property in speakers[room][timestamp]:
                                setattr(s, property, speakers[room][timestamp][property])
                            self.speakers[room][int(timestamp)] = s
            if 'title' in data:
                self.title = data['title']

            if 'meeting_url' in data:
                self.meeting_url = data['meeting_url']
            if 'video_url' in data:
                if isinstance(data['video_url'],str):
                    video_url = {}
                    video_url['Raadzaal'] = self.video_url #todo: huisvestingsverordening heeft Nonetype?
                else:
                    video_url = data['video_url']

                self.video_url = video_url
                for room in self.video_url:
                    if self.video_url[room] and '_definst_Eindhoven' in self.video_url[room]:
                        self.video_url[room] = self.video_url[room].replace('_definst_Eindhoven','_definst_/Eindhoven')
            if 'api_url' in data:
                self.api_url = data['api_url']
            if 'date' in data:
                self.date = data['date']
            if 'type' in data:
                self.type = data['type']
            if 'agenda' in data:
                self.agenda = data['agenda']

            #make sure that in case no subid exists, the master is there.
            if not self.meeting_subid and self.meeting_id:
                id = self.meeting_id
                self.meeting_subid = {}
                self.meeting_subid['Raadzaal'] = id


            return self


    def getsubmeeting_url(self,room):
        if self.meeting_subid is None:
            return None
        if room not in self.meeting_subid:
            return None
        subid = self.meeting_subid[room]
        return f'https://raadsinformatie.eindhoven.nl/vergadering/{subid}/{room}'

    def whichRoom(self,urlorid):
        if isinstance(urlorid,str):
            if 'vergadering' in urlorid:
                urlorid = int(urlorid.split('vergadering/')[1].split('/')[0].split('#')[0])
        room = next((room for room, subid in self.meeting_subid.items() if subid == urlorid), None)
        return room


    def print_details(self):
        print(f"meeting ID: {self.meeting_id}")
        print(f"Title: {self.title}")
        print(f"URL: {self.meeting_url}")
        print(f"Type: {self.type}")

    def addMic(self,timestamp,room):
        if room is None:
            room = 'Raadzaal'
        if not isinstance(self.speakers,dict):
            self.speakers = {}

        if room not in self.speakers:
            self.speakers[room] = {}

        self.speakers[room][int(timestamp)] = Mic(int(timestamp),None,None)
        return self.speakers[room][int(timestamp)]

    def speaking(self,time,room):
        if self.speakers is None or not self.speakers:
            return None

        if room is None:
            room = 'Raadzaal'
        if isinstance(time,str):
            time = int(time)

        if not room in self.speakers:
            return None


        keys = list(self.speakers[room].keys())
        delta = [abs(int(key) - time) for key in keys]
        index = min(range(len(delta)), key=delta.__getitem__)
        attempt = 0
        while attempt <5 and index >= 0:
            if self.speakers[room][keys[index]].start > time:
                index -= 1
                attempt+=1
                continue
            if self.speakers[room][keys[index]].end < time:
                index -=1
                attempt+=1
                continue
            return Member(self.speakers[room][keys[index]].id)
        return None


    def getStartTimeFromURLWithId(self,meeting_url):
        soup = web.visitPage(meeting_url)
        self.title = soup.find('title').text

        #get date from URL (not from title, for robustness
        meta = soup.findAll('meta')
        for field in meta:
            if 'name' in field.attrs and field['name']=='date':
                self.date = field['content']
                break
        if '#' not in meeting_url:
            print('No # in url')
            return
        id = meeting_url.split('#')[1]



        playerid = soup.find('li', id=f'player_{id}')
        if playerid and playerid['data-start_offset']:
            return int(playerid['data-start_offset'])

        else:
            print('No start time available')
            return None

    def addModuleToAgenda(self,module):
        for id in module.meeting_url:
            if int(id) not in list(self.meeting_subid.values()):
                continue
            if not '#ai' in module.meeting_url[id]:
                continue

            ai = module.meeting_url[id].split('#ai_')[1]


            room = self.whichRoom(module.meeting_url[id])
            if ai and room and self.agenda and self.agenda[room]:
                for timestamp in self.agenda[room]:
                    if self.agenda[room][timestamp]['id'] == int(ai):
                        if isinstance(self.agenda[room][timestamp]['module_id'],int):
                            value= self.agenda[room][timestamp]['module_id']
                            self.agenda[room][timestamp]['module_id'] = list()
                            self.agenda[room][timestamp]['module_id'].append(value)
                        if module.module_id not in self.agenda[room][timestamp]['module_id']:
                            self.agenda[room][timestamp]['module_id'].append(module.module_id)
                            print(f'Added module to agenda in {room}')

            else:
                print(f'could not find agenda or ai for: {self.title} - {self.meeting_id}')
        self.save()



    def getVideolinkFromURL(self,url):
        soup = web.visitPage(url)
        self.getVideolinkFromSoup(soup)


    def getVideolinkFromSoup(self,soup):
        # -- get video link:
        media_file_pattern = r"pubpoint:\s*[\"'](.*?)['\"],\s*streamname:\s*[\"'](.*?\.mp4)['\"]"

        for script in soup.findAll('script'):
            if script.contents:
                html = script.contents[0]
                match = re.search(media_file_pattern, html)

                if match:
                    pubpoint = match.group(1)
                    streamname = match.group(2)
                    print(f"Pubpoint: {pubpoint}")
                    print(f"Streamname: {streamname}")
                    self.video_url = f'{pubpoint}/{streamname}/playlist.m3u8'.replace('rtmp', 'https')
                    break
        self.save()




    def save(self):
        print(f"Saving meeting: {self.title}")
        if self.meeting_id is None:
            print('No meeting id, so it will not be saved!!!!')
            return

         # Define the directory path
        directory_path = cwdpath(os.path.join('json','meetings'))

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        # Cleaning:
        if isinstance(self.meeting_id,str) and 'http' in self.meeting_id:
            print(f'Something has gone horribly wrong: {self.meeting_id}')
        #Saving:
        file_path = os.path.join(directory_path, f"{self.meeting_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
            f.flush() #some files were truncated, hopefully this helps

        if Meeting(self.meeting_id) is None:
            print('It cannot load itself?!')
            print('stop')

    def to_dict(self):
        dict = self.__dict__
        if 'speakers' in dict and dict['speakers']: #it should be there, but also not be None
            for room in dict['speakers']:
                speakers_in_room= {}
                for key in dict['speakers'][room]:
                    speakers_in_room[key] = dict["speakers"][room][key].__dict__
                dict["speakers"][room] = speakers_in_room

        else:
            dict['speakers'] = None


        return dict

            
