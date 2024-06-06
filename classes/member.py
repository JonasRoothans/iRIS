import os
from dataclasses import dataclass
from typing import Optional
import xml.etree.ElementTree as ET
import json

@dataclass
class Member:
    speaker_id: Optional[int] = None
    name: Optional[str] = None
    party: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None

    def __init__(self, speaker_id: Optional[int] = None,
                 name: Optional[str] = None,
                 party: Optional[str] = None,
                 role: Optional[str] = None,
                 url: Optional[str] = None):
        if speaker_id is not None and name is None and party is None and role is None and url is None:
            self.load_from_xml(speaker_id)
        else:
            self.speaker_id = speaker_id
            self.name = name
            self.party = party
            self.role = role
            self.url = url

    def load_from_xml(self, speaker_id: int):
        file_path = f'xmls/members/{speaker_id}.xml'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No XML file found for speaker_id {speaker_id}")

        tree = ET.parse(file_path)
        root = tree.getroot()
        self.speaker_id = speaker_id
        self.name = root.find("Name").text
        self.party = root.find("Party").text
        self.role = root.find("Role").text
        self.url = root.find("URL").text

    def load_from_json(self, speaker_id: int):
        file_path = f'json/members/{speaker_id}.json'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No JSON file found for speaker_id {speaker_id}")
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.speaker_id = data['speaker_id']
            self.name = data['name']
            self.party = data['party']
            self.role = data['role']
            self.url = data['url']

    def print_details(self):
        print(f"Speaker ID: {self.speaker_id}")
        print(f"Name: {self.name}")
        print(f"Party: {self.party}")
        print(f"Role: {self.role}")
        print(f"URL: {self.url}")

    def save(self):
        print(f"Saving member: {self.speaker_id}")
        if self.speaker_id is None:
            raise ValueError("Speaker ID must be set to save the Member.")

         # Define the directory path
        directory_path = 'xmls/members'

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        #Settings
        save_as_json = True
        save_as_xml = False

        if save_as_xml:
            # Create XML structure
            member_element = ET.Element("Member")
            ET.SubElement(member_element, "SpeakerID").text = str(self.speaker_id)
            ET.SubElement(member_element, "Name").text = self.name or ""
            ET.SubElement(member_element, "Party").text = self.party or ""
            ET.SubElement(member_element, "Role").text = self.role or ""
            ET.SubElement(member_element, "URL").text = self.url or ""

            # Create a tree from the XML structure and write it to a file
            file_path = os.path.join(directory_path, f"{self.speaker_id}.xml")
            tree = ET.ElementTree(member_element)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
        if save_as_json:
            directory_path = 'json/members'
            os.makedirs(directory_path, exist_ok=True)
            file_path = os.path.join(directory_path, f"{self.speaker_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, ensure_ascii=False, indent=4)



        
