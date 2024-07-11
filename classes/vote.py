import os
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from typing import Dict, Optional, Union
from classes.module import Module

class Vote:
    vote_id: Optional[int] = None
    module_id: Optional[int] = None
    date: Optional[str] = None
    description: Optional[str] = None
    result: Optional[str] = None
    url: Optional[str] = None
    member_votes: Optional[Dict[int, str]] = None

    def __init__(self, vote_id: Optional[Union[int, str]] = None,
                 module_id: Optional[int] = None,
                 date: Optional[str] = None,
                 description: Optional[str] = None,
                 result: Optional[str] = None,
                 url: Optional[str] = None,
                 member_votes: Optional[Dict[int, str]] = None):
        if isinstance(vote_id, str) and vote_id.startswith('vote_'):
            vote_id = int(vote_id.replace('vote_', ''))
        if isinstance(vote_id,str) and vote_id.endswith('.json'):
            vote_id = int(os.path.splitext(vote_id)[0])


        self.vote_id = vote_id
        self.module_id =module_id
        self.date = date
        self.description = description
        self.result = result
        self.url = url
        self.member_votes = member_votes if member_votes is not None else {}

        if vote_id is not None and module_id is None and date is None and description is None and result is None and not member_votes:
            #print(f'Calling for Vote {vote_id}')
            self.load_from_json(vote_id)
            #self.load_from_xml(vote_id)

    def __eq__(self,other):
        if isinstance(other,Vote):
            return self.vote_id==other.vote_id
        return False

    def __hash__(self):
        return hash((self.vote_id,self.date))


    def load_from_json(self,vote_id:int):
        file_path = f'json/votes/{vote_id}.json'
        if os.path.exists(file_path):
            #print(f'Loading JSON for Vote {vote_id}')
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.vote_id = data['vote_id']
                self.module_id = data['module_id']
                self.date = data['date']
                self.description = data['description']
                self.result = data['result']
                self.url = data['url']
                self.member_votes = data['member_votes']


    def load_from_xml(self, vote_id: int):
        file_path = f'xmls/votes/{vote_id}.xml'
        if  os.path.exists(file_path):
            print(f'Loading XML for Vote {vote_id}')
            tree = ET.parse(file_path)
            root = tree.getroot()
            self.vote_id = vote_id
            if root.find("Date").text:
                self.date = root.find("Date").text

            if root.find("Description").text:
                self.description = root.find("Description").text

            if root.find("Result").text:
                self.result = root.find("Result").text

            self.member_votes = {}
            member_votes_element = root.find("MemberVotes")
            if member_votes_element is not None:
                for mv_element in member_votes_element.findall("MemberVote"):
                    member_id = int(mv_element.find("MemberID").text)
                    vote = mv_element.find("Vote").text
                    self.member_votes[member_id] = vote
    def save(self):
        if self.vote_id is None:
            raise ValueError("Vote ID must be set to save the Vote.")

        #Settings
        save_as_json = True
        save_as_xml = False

        if save_as_xml:
            print(f'Saving Vote {self.vote_id}')
            directory_path = 'xmls/votes'
            os.makedirs(directory_path, exist_ok=True)

            vote_element = ET.Element("Vote")
            ET.SubElement(vote_element, "VoteID").text = str(self.vote_id)
            ET.SubElement(vote_element, "Date").text = self.date or ""
            ET.SubElement(vote_element, "Description").text = self.description or ""
            ET.SubElement(vote_element, "Result").text = self.result or ""

            member_votes_element = ET.SubElement(vote_element, "MemberVotes")
            for member_id, vote in self.member_votes.items():
                mv_element = ET.SubElement(member_votes_element, "MemberVote")
                ET.SubElement(mv_element, "MemberID").text = str(member_id)
                ET.SubElement(mv_element, "Vote").text = vote

            file_path = os.path.join(directory_path, f"{self.vote_id}.xml")
            tree = ET.ElementTree(vote_element)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
        if save_as_json:
            directory_path = 'json/votes'
            os.makedirs(directory_path, exist_ok=True)
            file_path = os.path.join(directory_path, f"{self.vote_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__ ,f, ensure_ascii=False, indent=4)


    def add_membervote(self, member_id: int, vote: str):
        if member_id not in self.member_votes:
            self.member_votes[member_id] = vote
        self.save()

    def vote_as_int_for_member(self, member:int) -> Optional[int]:
        if self.member_votes[member] == 'voor':
            return 1
        elif self.member_votes[member] == 'afwezig':
            return None
        else:
            return -1
    def get_module(self):
        if self.module_id:
            return Module(self.module_id)
        else:
            return Module

    def print_details(self):
        print(f"Vote ID: {self.vote_id}")
        print(f"Model ID: {self.module_id}")
        print(f"Date: {self.date}")
        print(f"Description: {self.description}")
        print(f"Result: {self.result}")
        print(f"URL: {self.url}")
        print("Member Votes:")
        for member_id, vote in self.member_votes.items():
            print(f"  Member ID: {member_id}, Vote: {vote}")

    def __repr__(self):
        return (f"Vote(vote_id={self.vote_id}, module = {self.module_id}, date={self.date}, description={self.description}, "
                f"result={self.result}, member_votes={self.member_votes})")

# Example usage
if __name__ == "__main__":
    # Create a new vote and save to XML
    new_vote = Vote(vote_id=12345, date='2024-05-13', description="Some description", result="Passed", url="www.test.com",member_votes={1: "Yea", 2: "Nay"})
    new_vote.save()

    # Load a vote from XML using an integer ID
    loaded_vote = Vote(12345)
    loaded_vote.print_details()

    # Load a vote from XML using a string ID with prefix
    loaded_vote_string = Vote("vote_12345")
    loaded_vote_string.print_details()

    # Add a member vote and save
    loaded_vote.add_membervote(3, "Abstain")
    loaded_vote.print_details()
