import os
from dataclasses import dataclass
from typing import Optional
import xml.etree.ElementTree as ET

@dataclass
class Member:
    speaker_id: Optional[int] = None
    name: Optional[str] = None
    party: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None

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



        
