import os
from dataclasses import dataclass
from classes.member import Member

from typing import Optional
import json

@dataclass
class Module:
    def __init__(self, module_id=None):
        self.module_id = None
        self.vote_id = None
        self.member_id = []
        self.party_list = []
        self.poho_id = []
        self.title = None
        self.url = None
        self.type = None
        self.member = None
        self.party = None
        self.poho = None
        self.result = None
        self.date = None
        self.meeting_url = None
        self.attachment = None
        self.parent = None
        self.children = []

        if module_id is not None:
            self.load_from_json(module_id)


    def __str__(self):
        return self.title


    def __repr__(self):
        return f'Module(name={self.title})'

    def load_from_json(self, module_id: str):
        if isinstance(module_id,str):
            if module_id[-5:] == '.json':
                module_id = module_id[0:-5]


        file_path = f'{os.getcwd()}/json/modules/{module_id}.json'
        if not os.path.exists(file_path):
            self.title = f'Unknown id: {module_id}'
            print(f'New module created: {module_id}')
            if isinstance(module_id,str):
                if module_id[0] in ('a','r','i','m','o'): #prefix in case it's an amendement. Because for some reason that's not a module.
                    self.module_id = module_id
                elif module_id[0] =='x':
                    uid = int(0)
                    while os.path.exists(f'json/modules/{uid:05d}.json'):
                        uid+=1
                    self.module_id = f'x_{uid:05d}'
            else:
                self.module_id = int(module_id)
            return
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.module_id = data['module_id']
            self.vote_id = data['vote_id']
            self.member_id = data['member_id']
            self.party_list = data['party_list']
            self.poho_id = data['poho_id']
            self.title = data['title']
            self.url = data['url']
            self.type = data['type']
            self.member = data['member']
            self.party = data['party']
            self.result = data['result']
            if 'date' in data:
                self.date = data['date']
            if 'meeting_url' in data:
                self.meeting_url = data['meeting_url']
            self.attachment = data['attachment']
            self.parent = data['parent']
            self.children = data['children']

    def print_details(self):
        print(f"Module ID: {self.module_id}")
        print(f"Title: {self.title}")
        print(f"URL: {self.url}")
        print(f"Type: {self.type}")

    def save(self):
        print(f"Saving module: {self.title}")
        if self.module_id is None:

            #--try to recover ID from url:
            if self.url is not None:
                try:
                    self.module_id = int(self.url.split('/')[-1])
                    print(f'module id {self.module_id} recovered from url.')
                except:
                    print('!!!!Module ID is not set. Saving is not possible. IGNORING CASE AND HOPE FOR THE BEST')
                    return
            else:
                print('!!!!Module ID is not set. Saving is not possible. IGNORING CASE AND HOPE FOR THE BEST')
                return



         # Define the directory path
        directory_path = f'{os.getcwd()}/json/modules'

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        # Cleaning:
        if self.url is not None:
            if self.url[0] == '/':
                self.url = f'https://raadsinformatie.eindhoven.nl{self.url}'
        if self.meeting_url is not None:
            if self.meeting_url[0] == '/':
                self.meeting_url = f'https://raadsinformatie.eindhoven.nl{self.meeting_url}'
        if self.parent_id==self.module_id:
            self.parent_id = None



        file_path = os.path.join(directory_path, f"{self.module_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=4)

    def add_children(self):
        from functions.download import web
        if self.url is None:
            return None
        if self.type == 'Motie' or self.type == 'Amendement' or self.type == "Toezegging" or self.type == "Vrije motie":
            return None

        #children can only be found via the agenda
        #use the value behind the '#ai' as an indicator for the active agenda item
        if '#' not in self.meeting_url:
            return
        agenda_item = self.meeting_url.split('#')[1]
        soup = web.visitPage(self.meeting_url)

        try:
            other_elements_in_block = soup.find('li', id=f'module_item_{self.module_id}').find_next_siblings()
        except:
            return

        for element in other_elements_in_block:
            try:
                child_id = int(element.attrs['data-module_item_id'])
            except:
                child_id = None

            #if connection does not exist yet:
            if child_id is not None and child_id not in self.children:
                self.children.append(child_id)
                childModule = Module(child_id)
                if childModule.parent is None:
                    childModule.parent = self.module_id
                    # exchange poho between parent and child
                    if childModule.poho is not None and self.poho is None:
                        self.poho = childModule.poho
                    if childModule.poho is None and self.poho is not None:
                        childModule.poho = self.poho
                    childModule.save()
                else:
                    if childModule.parent is not self.module_id:
                        print(f'!! CONFLICTING HIERARCHY FOR MODULE {self.module_id} and {child_id}')


    def add_parent(self):
        from functions.download import web
        if self.meeting_url is None:
            return None
        if self.type == 'Raadsvoorstellen':
            return None
        if 'Vrije Motie' in self.title:
            return None

        #parent can only be found via the agenda
        #use the value behind the '#ai' as an indicator for the active agenda item

        try:
            agenda_item = self.meeting_url.split('#')[1]
            soup = web.visitPage(self.meeting_url)
            parent_id = int(soup.find('li', id=agenda_item).find('ul', class_='module_items').contents[1].attrs['data-module_item_id'])

            if parent_id is not None:
                if parent_id == self.module_id:
                    print('! parent id and module id are similar.')
                #add parent
                self.parent = parent_id

                #add child to parent
                parent = Module(parent_id)
                if self.module_id not in parent.children:
                    parent.children.append(self.module_id)
                    print(f' + connected {self.title} to parent: {parent.title}')

                #exchange poho between parent and child
                if parent.poho is not None and self.poho is None:
                    self.poho = parent.poho
                if parent.poho is None and self.poho is not None:
                    parent.poho = self.poho

                parent.save()
        except:
            parent_id = None
        return parent_id


    def linkToOtherFiles(self):
        from classes.vote import Vote
        #--- connect to members
        if len(self.member_id)==0 and self.member is not None:
            #search through all members for a match
            # Get all vote ids
            folder_path = f'{os.getcwd()}/json/members/person'
            members = os.listdir(folder_path)
            print(self.title)
            for member_id in members:
                m = Member(member_id)
                if m.name in self.member:
                    print(f'---added {m.name}')
                    self.member_id.append(int(m.person_id))
                    self.party_list.append(m.party)

        #--- connect to votes
        if self.vote_id is None:
            folder_path = f'{os.getcwd()}/json/votes'
            votes = [v for v in os.listdir(folder_path) if v.endswith('.json')]
            sorted_files = sorted(votes, key=lambda x: int(x.split('.')[0]), reverse=True)
            for vote_id in sorted_files:
                v = Vote(vote_id)
                if v.description in self.title:
                    print(f'--- connected to vote {v.vote_id}')
                    self.vote_id = v.vote_id
                    v.module_id = self.module_id
                    v.save()
                elif v.date < self.date:
                    break


        #-- discover hierarchy
        self.add_parent()
        self.add_children()













