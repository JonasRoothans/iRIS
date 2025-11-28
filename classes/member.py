import os
from dataclasses import dataclass
from typing import Optional
import xml.etree.ElementTree as ET
import json
from functions.support import cwdpath
from classes.party import Party
import random

@dataclass
class Member:
    speaker_id: Optional[int] = None
    person_id: Optional[int] = None
    name: Optional[str] = None
    party: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None
    img: Optional[str] = None

    def __init__(self, speaker_id: Optional[int] = None,
                 person_id: Optional[int] = None,
                 name: Optional[str] = None,
                 party: Optional[str] = None,
                 role: Optional[str] = None,
                 url: Optional[str] = None,
                 img: Optional[str] = None,
                 active: Optional[str] = None):
        if speaker_id is not None and person_id is None and name is None and party is None and role is None and url is None:
            self.load_from_json(speaker_id)
        else:
            self.speaker_id = speaker_id
            self.person_id = person_id
            self.name = name
            self.party = party
            self.role = role
            self.url = url
            self.img = img
            self.active = active

    def __str__(self):
        return self.name


    def __repr__(self):
        return f'Member({self.name}, {self.party})'

    def getPohoByName(self,name):
        file_path = cwdpath(os.path.join('json', 'members', 'poho'))
        for filename in os.listdir(file_path):
            if filename.endswith('.json'):
                member = Member(filename)
                if name in member.name:
                    return member

        #doesn't exit yet
        member = Member()
        member.name = name
        member.role = 'Wethouder'
        member.savePoho()
        print('New POHO created. Make sure to manually update info!!')
        return member


    def load_from_json(self, speaker_id):
        if isinstance(speaker_id,str):
            if speaker_id[-5:] == '.json':
                speaker_id = speaker_id[0:-5]



        file_path = cwdpath(os.path.join('json','members','speaker',f'{speaker_id}.json'))
        if not os.path.exists(file_path):
            file_path = cwdpath(os.path.join('json','members','person',f'{speaker_id}.json'))
            if not os.path.exists(file_path):
                file_path = cwdpath(os.path.join('json', 'members', 'poho', f'{speaker_id}.json'))
                if not os.path.exists(file_path):
                    self.name = f'Unknown id: {speaker_id}'
                    self.speaker_id = speaker_id
                    return
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.speaker_id = data['speaker_id']
            self.person_id = data['person_id']
            self.name = data['name']
            self.party = data['party']
            self.role = data['role']
            self.url = data['url']
            if 'img' in data:
                self.img = data['img']
            if 'active' in data:
                self.active = data['active']

    def print_details(self):
        print(f"Speaker ID: {self.speaker_id}")
        print(f"Person ID: {self.person_id}")
        print(f"Name: {self.name}")
        print(f"Party: {self.party}")
        print(f"Role: {self.role}")
        print(f"URL: {self.url}")

    def get_party(self):
        if self.party:
            return Party(self.party.lower().replace(' ',''))
        return None

    def save(self):
        print(f"Saving member: {self.speaker_id} ({self.name})")
        if self.speaker_id is None:
            raise ValueError("Speaker ID must be set to save the Member.")

         # Define the directory path
        directory_path = cwdpath(os.path.join('json','members'))

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        #Settings

        directory_path_speaker = cwdpath(os.path.join('json','members','speaker'))
        directory_path_person =  cwdpath(os.path.join('json','members','person'))
        os.makedirs(directory_path_speaker, exist_ok=True)
        file_path = os.path.join(directory_path_speaker, f"{self.speaker_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=4)

        if self.person_id is not None:
            os.makedirs(directory_path_person, exist_ok=True)
            file_path_person = os.path.join(directory_path_person, f"{self.person_id}.json")
            with open(file_path_person, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, ensure_ascii=False, indent=4)

    def savePoho(self):
        print(f"Saving Poho: ({self.name})")
        if self.speaker_id is None:
            if 'Lanschot' in self.name:
                self.speaker_id = 230019
                self.img = 'https://assets.notubiz.nl/pasfotos/6311cf5a527f6.jpg'
            if 'Strijk' in self.name:
                self.speaker_id = 248564
                self.img = 'https://raadsinformatie.eindhoven.nl/images/anoniem-pasfoto.jpg'
            if 'Verhees' in self.name:
                self.speaker_id = 230023
                self.img = 'https://assets.notubiz.nl/pasfotos/6311cf8a2d695.jpg'
            if 'Thijs' in self.name:
                self.speaker_id = 230014
                self.img = 'https://assets.notubiz.nl/pasfotos/6311e9c0ae8fa.jpg'
            if 'Steenbakkers' in self.name:
                self.speaker_id = 230013
                self.img = 'https://assets.notubiz.nl/pasfotos/6311ec7462709.jpg'
            if 'Toub' in self.name:
                self.speaker_id = 230022
                self.img = 'https://assets.notubiz.nl/pasfotos/6311eb2391cae.jpg'
            if 'Lammers' in self.name:
                self.speaker_id = 230024
                self.img = 'https://assets.notubiz.nl/pasfotos/6311ec3cb376a.jpg'
            if 'Dijsselbloem' in self.name:
                self.speaker_id = 231116
                self.img = 'https://assets.notubiz.nl/pasfotos/64e609b67bf4f.jpg'


         # Define the directory path
        directory_path = cwdpath(os.path.join('json','members'))

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        #Settings

        directory_path= cwdpath(os.path.join('json','members','poho'))
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, f"{self.speaker_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=4)




        
