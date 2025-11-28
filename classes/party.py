import os
from dataclasses import dataclass
from functions.support import cwdpath
from datetime import datetime
from functions.download import web
import re
import yake
import json

class Party:
    def __init__(self, id=None):
        self.color = None
        self.id = ''
        self.fullName = ''
        self.shortName = ''

        if id is not None:
            self.load_from_json(id)

    def load_from_json(self,id):
        if isinstance(id,str):
            if id[-5:] == '.json':
                id = id[0:-5]


        file_path = cwdpath(os.path.join('json','parties',f'{id}.json'))
        if not os.path.exists(file_path):
            self.id = id
            print(f'New module created: {id}')
            return

        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except:
                print(f'FILE CORRUPTED ---------> {file}')
                return None
            self.color = data['color']
            self.id = data['id']
            self.fullName = data['fullName']
            self.shortName = data['shortName']

    def save(self):
        print(f"Saving party: {self.id}")

        # Define the directory path
        directory_path = cwdpath(os.path.join('json', 'parties'))

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        file_path = os.path.join(directory_path, f"{self.id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=4)
            f.flush()  # some files were truncated, hopefully this helps


