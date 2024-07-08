import os
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class Module:
    module_id: Optional[int] = None
    vote_id:Optional[int] = None
    title: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None

    def __init__(self, module_id: Optional[int] = None,
                 vote_id: Optional[int] = None,
                 title: Optional[str] = None,
                 url: Optional[str] = None,
                 type: Optional[str] = None):
        if module_id is not None and vote_id is None and title is None and url is None and type is None:
            self.load_from_json(module_id)
        else:
            self.module_id = module_id
            self.vot_id = vote_id
            self.title = title
            self.url = url
            self.type = type

    def __str__(self):
        return self.title


    def __repr__(self):
        return f'Member(name={self.title})'

    def load_from_json(self, module_id: int):
        if module_id[-5:] == '.json':
            module_id = module_id[0:-5]


        file_path = f'json/modules/{module_id}.json'
        if not os.path.exists(file_path):
            self.title = f'Unknown id: {module_id}'
            if module_id[0] in ('a','r','i','m'): #prefix in case it's an amendement. Because for some reason that's not a module.
                self.module_id = module_id
            else:
                self.module_id = int(module_id)

            return
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.module_id = data['module_id']
            self.vote_id = data['vote_id']
            self.title = data['title']
            self.url = data['url']
            self.type = data['type']

    def print_details(self):
        print(f"Module ID: {self.module_id}")
        print(f"Title: {self.title}")
        print(f"URL: {self.url}")
        print(f"Type: {self.type}")

    def save(self):
        print(f"Saving module: {self.module_id}")
        if self.module_id is None:
            raise ValueError("Module ID must be set to save the Member.")

         # Define the directory path
        directory_path = 'json/modules'

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        file_path = os.path.join(directory_path, f"{self.module_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=4)

