import numpy as np
import os
from classes.module import Module
from datetime import datetime

class ModuleManager:
    def __init__(self):
        self.modules = [] #will contain a list of Module objects

    def all(self):
        # Get all vote ids
        folder_path = f'{os.getcwd()}/json/modules'
        fnames = os.listdir(folder_path)
        fnames = [fn for fn in fnames if not fn.startswith('.')]
        return fnames

    def addall(self):
        for m_id in self.all():
            if m_id[0]=='.':
                continue
            try:
                self.addmodule(m_id)
            except:
                print(f'{m_id} skipped')

    def addmodule(self,m_id):
        m = Module(m_id)
        if m in self.modules:
            return self.modules.index(m)

        #add the object
        if m.date is None:
            if m.parent is not None:
                p = Module(m.parent)
                if  p.date is not None:
                    m.date = p.date
                    m.save()
        if m.date is None: #still none? then skip
            print(f'Module {m_id} ({m.title}) could not be added because a date is missing')
            return None
        if m.date[4]=='-': #dash in this position indicates it starts with YYYY
            m.date = datetime.strptime(m.date, '%Y-%m-%d').strftime('%d-%m-%Y')


        self.modules.append(m)

    def sort_chronological(self):
        # Extract dates and their corresponding indices
        dates_with_indices = [(datetime.strptime(module.date, '%d-%m-%Y'), index) for index, module in
                              enumerate(self.modules)]
        # Sort the list of tuples by the date
        sorted_dates_with_indices = sorted(dates_with_indices, reverse=True)

        # Extract the new order of indices
        sorted_indices = [index for _, index in sorted_dates_with_indices]

        # Reorder votes, votes_by_member, and voting_result
        self.modules = [self.modules[i] for i in sorted_indices]

