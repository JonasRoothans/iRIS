import os
from dataclasses import dataclass
from typing import Optional
import xml.etree.ElementTree as ET
import json

@dataclass
class Member:
    speaker_id: Optional[int] = None
    person_id: Optional[int] = None
    name: Optional[str] = None
    party: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None

    def __init__(self, speaker_id: Optional[int] = None,
                 person_id: Optional[int] = None,
                 name: Optional[str] = None,
                 party: Optional[str] = None,
                 role: Optional[str] = None,
                 url: Optional[str] = None):
        if speaker_id is not None and person_id is None and name is None and party is None and role is None and url is None:
            self.load_from_json(speaker_id)
        else:
            self.speaker_id = speaker_id
            self.person_id = person_id
            self.name = name
            self.party = party
            self.role = role
            self.url = url

    def __str__(self):
        return self.name


    def __repr__(self):
        return f'Member({self.name}, {self.party})'

    def load_from_json(self, speaker_id):
        if isinstance(speaker_id,str):
            if speaker_id[-5:] == '.json':
                speaker_id = speaker_id[0:-5]



        file_path = f'{os.getcwd()}/json/members/speaker/{speaker_id}.json'
        if not os.path.exists(file_path):
            file_path = f'{os.getcwd()}/json/members/person/{speaker_id}.json'
            if not os.path.exists(file_path):
                self.name = f'Unknown id: {speaker_id}'
                return
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.speaker_id = data['speaker_id']
            self.person_id = data['person_id']
            self.name = data['name']
            self.party = data['party']
            self.role = data['role']
            self.url = data['url']

    def print_details(self):
        print(f"Speaker ID: {self.speaker_id}")
        print(f"Person ID: {self.person_id}")
        print(f"Name: {self.name}")
        print(f"Party: {self.party}")
        print(f"Role: {self.role}")
        print(f"URL: {self.url}")

    def save(self):
        print(f"Saving member: {self.speaker_id} ({self.name})")
        if self.speaker_id is None:
            raise ValueError("Speaker ID must be set to save the Member.")

         # Define the directory path
        directory_path = 'xmls/members'

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        #Settings

        directory_path_speaker = 'json/members/speaker'
        directory_path_person =  'json/members/person'
        os.makedirs(directory_path_speaker, exist_ok=True)
        file_path = os.path.join(directory_path_speaker, f"{self.speaker_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=4)

        if self.person_id is not None:
            os.makedirs(directory_path_person, exist_ok=True)
            file_path_person = os.path.join(directory_path_person, f"{self.person_id}.json")
            with open(file_path_person, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, ensure_ascii=False, indent=4)



        
