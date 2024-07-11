import os
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class Module:
    def __init__(self, module_id=None):
        self.module_id = None
        self.vote_id = None
        self.title = None
        self.url = None
        self.type = None

        if module_id is not None:
            self.load_from_json(module_id)


    def __str__(self):
        return self.title


    def __repr__(self):
        return f'Member(name={self.title})'

    def load_from_json(self, module_id: int):
        if isinstance(module_id,str):
            if module_id[-5:] == '.json':
                module_id = module_id[0:-5]


        file_path = f'json/modules/{module_id}.json'
        if not os.path.exists(file_path):
            self.title = f'Unknown id: {module_id}'
            if module_id[0] in ('a','r','i','m','o'): #prefix in case it's an amendement. Because for some reason that's not a module.
                self.module_id = module_id
            elif module_id[0] =='x':
                uid = int(0)
                while os.path.exists(f'json/modules/{uid : 05d}.json'):
                    uid+=1
                self.module_id = f'x_{uid : 05d}'
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

