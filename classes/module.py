import os
from dataclasses import dataclass
from classes.member import Member
from classes.meeting import Meeting
from functions.support import cwdpath
from datetime import datetime
from functions.download import web
import re
import yake


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
        self.text = None
        self.pdf_url = None
        self.pdf_text = None
        self.bst = None
        self.related = None
        self.videostarttime = None
        self.videolink = None
        self.keywords = {}
        self.svz = None
        self.afgedaan = None
        self.eersteIndiener = None
        self.lastScrapeDate = None
        self.meeting_id = []


        if module_id is not None:
            self.load_from_json(module_id)


    def __str__(self):
        return self.title


    def __repr__(self):
        return f'Module(name={self.title})'

    def __eq__(self,other):
        if isinstance(other,Module):
            return self.module_id == other.module_id
        return False


    def extract_keywords(self):
        innertext = self.text or ""
        title = self.title or ""
        pdf = self.pdf_text or ""



        text = title + " " + pdf + " " + innertext
        self.keywords = {}
        language = "nl"
        max_ngram_size = 2
        deduplication_threshold = 0.5
        deduplication_algo = 'seqm'
        windowSize = 1
        numOfKeywords = 100

        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                                    dedupFunc=deduplication_algo, windowsSize=windowSize,
                                                    top=numOfKeywords,
                                                    features=None)
        keywords = custom_kw_extractor.extract_keywords(text)
        for kw in keywords:
            if kw[0] in title:
                bonus = 1
            else:
                bonus = 0
            if kw[1]<0.5:
                self.keywords[kw[0]] = 1-kw[1]+bonus




    def load_from_json(self, module_id: str):
        if isinstance(module_id,str):
            if module_id[-5:] == '.json':
                module_id = module_id[0:-5]


        file_path = cwdpath(os.path.join('json','modules',f'{module_id}.json'))
        if not os.path.exists(file_path):
            self.title = f'Unknown id: {module_id}'
            print(f'New module created: {module_id}')
            if isinstance(module_id,str):
                if module_id[0] in ('a','r','i','m','o'): #prefix in case it's an amendement. Because for some reason that's not a module.
                    self.module_id = module_id
                elif module_id[0] =='x':
                    uid = int(0)
                    while os.path.exists(cwdpath(os.path.join('json','modules',f'{uid:05d}.json'))):
                        uid+=1
                    self.module_id = f'x_{uid:05d}'
                else:
                    self.module_id = int(module_id)
            else:
                self.module_id = int(module_id)
            return
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except:
                print(f'FILE CORRUPTED ---------> {file}')
                return None
            self.module_id = data['module_id']
            self.vote_id = data['vote_id']
            self.member_id = data['member_id']
            self.party_list = data['party_list']
            self.poho_id = data['poho_id']
            self.poho = data['poho']
            self.title = data['title']
            self.url = data['url']
            self.type = data['type']
            self.member = data['member']
            self.party = data['party']
            self.result = data['result']
            if not self.result:
                self.result = ''
            if 'date' in data:
                self.date = data['date']
            if 'meeting_url' in data:
                self.meeting_url = data['meeting_url']
            self.attachment = data['attachment']
            self.parent = data['parent']
            self.children = data['children']
            if 'text' in data:
                self.text = data['text']
            if 'pdf_url' in data:
                self.pdf_url = data['pdf_url']
            if 'pdf_text' in data:
                self.pdf_text = data['pdf_text']
            if 'bst' in data:
                self.bst = data['bst']
            if 'related' in data:
                self.related = data['related']
            if 'videostarttime' in data:
                self.videostarttime = data['videostarttime']
            if 'videolink' in data:
                self.videolink = data['videolink']
            if 'keywords' in data:
                self.keywords = data['keywords']
            if 'svz' in data:
                self.svz = data['svz']
            if 'afgedaan' in data:
                self.afgedaan = data['afgedaan']
            if 'eersteIndiener' in data:
                self.eersteIndiener = data['eersteIndiener']
            if 'lastScrapeDate' in data:
                self.lastScrapeDate = data['lastScrapeDate']
            if 'meeting_id' in data:
                if isinstance(data['meeting_id'],int):
                    self.meeting_id = [data['meeting_id']]
                else:
                    self.meeting_id = data['meeting_id']
            else:
                if self.meeting_url and isinstance(self.meeting_url,dict):
                    self.meeting_id = list(self.meeting_url.keys())


            return self

    def print_details(self):
        print(f"Module ID: {self.module_id}")
        print(f"Title: {self.title}")
        print(f"URL: {self.url}")
        print(f"Type: {self.type}")

    def uniqueChildren(self):
        new_children = list(set(self.children))
        removed_items = len(self.children) - len(new_children)
        if removed_items:
            self.children = new_children


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
        directory_path = cwdpath(os.path.join('json','modules'))

        # Ensure the directory exists
        os.makedirs(directory_path, exist_ok=True)

        # Cleaning:
        self.clean()







        file_path = os.path.join(directory_path, f"{self.module_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=4)
            f.flush() #some files were truncated, hopefully this helps

        if Module(self.module_id) is None:
            print('It cannot load itself?!')
            print('stop')

    def add_children(self):
        from functions.download import web
        if self.url is None:
            return None
        if self.type:
            if self.type.lower() == 'motie' or self.type.lower() == 'amendement' or self.type.lower() == "toezegging" or self.type.lower() == "vrije motie":
                return None

        #children can only be found via the agenda
        #use the value behind the '#ai' as an indicator for the active agenda item
        if self.meeting_url and '#' not in self.meeting_url or self.meeting_url is None:
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
                        if '(VM' in childModule.title:
                            childModule.parent = None
                            childModule.save()
                            self.children.remove(child_id)
                            self.save()
                        else:
                            print(f'!! CONFLICTING HIERARCHY FOR MODULE {self.module_id} and {child_id}')


    def add_parent(self):
        from functions.download import web
        if self.meeting_url is None:
            return None
        if self.type == 'Raadsvoorstellen' or self.type == 'Raadsvoorstel':
            return None
        if 'vrije motie' in self.title.lower() and self.type.lower() != 'toezegging':
            return None

        #parent can only be found via the agenda
        #use the value behind the '#ai' as an indicator for the active agenda item

        parent_id = None
        try:
            agenda_item = self.meeting_url.split('#')[1]
        except:
            return
        soup = web.visitPage(self.meeting_url)

    #backup:
        if soup.find('li', id=agenda_item) is None:
            return
        parent_id = int(soup.find('li', id=agenda_item).find('ul', class_='module_items').contents[1].attrs[
                            'data-module_item_id'])
        parent_title = soup.find('li', id=agenda_item).find('ul', class_='module_items').contents[1].attrs[
            'data-title']
        parent_url = soup.find('li', id=agenda_item).find('ul', class_='module_items').contents[1].find('a')['href']

    #optimization:
        module_list = soup.find('li', id=agenda_item).find('ul', class_='module_items').find_all('li')
        for module_candidate in module_list:
            if module_candidate is not None:
                if 'data-title' in module_candidate.attrs:
                    module_candidate_name = module_candidate.attrs['data-title']
                    if 'voorstel' in module_candidate_name:
                        parent_title = module_candidate_name
                        parent_id = int(module_candidate.attrs['data-module_item_id'])
                        parent_url = module_candidate.find('a')['href']
                        break

        if parent_id is not None:
            if 'vragenhalfuur' in soup.find('li', id=agenda_item).find('ul', class_='module_items').parent.text.lower():
                    parent_title = 'Vragenhalfuur'
            if parent_id == self.module_id:
                print('! parent id and module id are similar. Adding agenda-item as parent')
                li = soup.find('li', id=agenda_item)
                if 'data-title' in li.attrs:
                    #make agenda item module:
                    aimodule = Module(agenda_item)
                    aimodule.title = li['data-title']
                    aimodule.meeting_url = self.meeting_url
                    aimodule.type = 'Agenda'
                    aimodule.date = self.date
                    aimodule.poho = self.poho
                    aimodule.save()
                    parent_id = agenda_item

            #add parent
            self.parent = parent_id

            #add child to parent
            parent = Module(parent_id)
            parent.children.append(self.module_id) #duplicates can be fixed later
            print(f' + connected {self.title} to parent: {parent.title}')
            parent.title = parent_title
            parent.url = parent_url
            if len(self.children):
                for child in self.children:
                    print('child')
                    grandchild = Module(child)
                    parent.children.append(grandchild.module_id)
                    grandchild.parent = parent.module_id
                    parent.save()
                    try:
                        grandchild.save()
                    except:
                        print('debug')
            self.children = []



            #exchange poho between parent and child
            if parent.poho is not None and self.poho is None:
                self.poho = parent.poho
            if parent.poho is None and self.poho is not None:
                parent.poho = self.poho

            parent.save()
            self.save()
        return parent_id


    def linkToOtherFiles(self):
        from classes.vote import Vote
        #--- connect to members
        if len(self.member_id)==0 and self.member is not None:
            #search through all members for a match
            # Get all vote ids
            folder_path = cwdpath(os.path.join('json','members','person'))
            members = os.listdir(folder_path)
            print(self.title)
            for member_id in members:
                m = Member(member_id)
                if m.name in self.member:
                    print(f'---added {m.name}')
                    self.member_id.append(int(m.person_id))
                    self.party_list.append(m.party)

        #--- connect to votes
        if self.vote_id is None and self.type != 'Toezegging':
            folder_path = cwdpath(os.path.join('json','votes'))
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
        if self.result is None:
            if self.vote_id is not None:
                v = Vote(vote_id)
                if v.result is not None:
                    self.result = v.result


        #-- discover hierarchy
        self.add_parent()
        self.add_children()

    def clean(self):
        if self.title is None:
            self.title = ''




        self.uniqueChildren()
        if self.url and self.url == self.meeting_url:
            if '/vergadering/' in self.url:
                self.url = ''
        if self.url is not None and self.url != '':
            if self.url[0] == '/':
                self.url = f'https://raadsinformatie.eindhoven.nl{self.url}'
        if self.meeting_url is not None:
            if isinstance(self.meeting_url,dict):
                for room in self.meeting_url:
                    if self.meeting_url[room].startswith('/'):
                        self.meeting_url[room] = f'https://raadsinformatie.eindhoven.nl{self.meeting_url}'
            else:
                if self.meeting_url.startswith('/'):
                    id = int(self.meeting_url.split('vergadering/')[1].split('/')[0])
                    value = f'https://raadsinformatie.eindhoven.nl{self.meeting_url}'
                    self.meeting_url = {}
                    self.meeting_url[id] = value

        if self.meeting_url and not self.meeting_id and 'vergadering' in self.meeting_url:
            Meeting(self.meeting_url).save()
        if self.parent==self.module_id:
            self.parent= None
        if self.type == 'Raadsvoorstellen':
            self.type = 'Raadsvoorstel'
        if self.type is None and 'Raadsvoorstel' in self.title:
            self.type = 'Raadsvoorstel'
        if self.member_id:
            self.member_id = list(set(self.member_id))
        if self.party_list:
            self.party_list = list(set(self.party_list))
        if self.meeting_id:
            self.meeting_id = list(set(self.meeting_id))

        if self.date is None:
            if self.children:
                for child in self.children:
                    childDate = Module(child).date
                    if childDate is not None:
                        self.date = childDate
        else:
            if self.date[4]=='-' or self.date.startswith('-'):
                self.date = datetime.strptime(self.date, "%Y-%m-%d").strftime("%d-%m-%Y")
        self.uniqueChildren()

        #-- Wel een POHO naam, maar geen POHO id
        if not self.poho_id and self.poho:
            poho = Member()
            poho = poho.getPohoByName(self.poho)
            self.poho_id = poho.speaker_id

        #-- ALs er geen formele POHO is, maar een POHO wel wordt genoemd
        if not self.poho and self.text:
            match = re.search(r"Wethouder (.*?) ", self.text)

            if match:
                name = match.group(1)  # Extract the name that was matched
                poho = Member()
                poho = poho.getPohoByName(name)
                if poho.role:
                    self.poho_id = poho.speaker_id
                    self.poho = poho.name

        #geen video maar wel children met een video
        if not self.videolink:
            if self.children:
                for child in self.children:
                    childModule = Module(child)
                    if childModule.videolink:
                        self.videolink = childModule.videolink
                        self.videostarttime = childModule.videostarttime
                        break

        return self


    def updateScrapeDate(self):
        self.lastScrapeDate = datetime.now().strftime ("%d-%m-%Y")

    def get_date(self):
        try:
            return datetime.strptime(self.date,'%d-%m-%Y').date()
        except:
            print('stop')

    def connectToMeeting(self):
        id = int(self.meeting_url.split('vergadering/')[1].split('/')[0].split('#')[0])
        if isinstance(self.meeting_id,int):
            self.meeting_id = [self.meeting_id]
        if self.meeting_id is None or id not in self.meeting_id:
            self.meeting_id.append(id)
        MeetingObj = Meeting(id)
        if MeetingObj.meeting_url is None:
            MeetingObj.meeting_url = f'https://raadsinformatie.eindhoven.nl/{id}'
            MeetingObj.save()

    def addMeetingLink(self,link):
        #videoLink should be a dictionary
        if not (isinstance(self.meeting_url, dict)):
            self.meeting_url = {}
        if not (isinstance(self.videostarttime, dict)):
            self.videostarttime = {}

        #get Meeting
        MeetingObj = Meeting(link)

        # get sub id
        submeetingid = int(link.split('/')[-1].split('#')[0])

        #Update Module:
        self.meeting_url[submeetingid] = link

        if MeetingObj.agenda:
            self.videostarttime[submeetingid] = MeetingObj.getStartTimeFromURLWithId(link)

            #Update Meeting:
            MeetingObj.addModuleToAgenda(self)










    def getvideostarttime(self):
        try:
            MeetingObj = Meeting(self.meeting_url)
            if MeetingObj.meeting_id not in self.meeting_id:
                self.meeting_id.append(MeetingObj.meeting_id)

            if not isinstance(self.videostarttime, dict):
                self.videostarttime = {}

            if MeetingObj.meeting_id not in self.videostarttime:
                self.videostarttime[MeetingObj.meeting_id] = MeetingObj.getStartTimeFromURLWithId(self.meeting_url)
                print('added videolink')

        except:
            self.videostarttime = None
            self.videolink = None
        self.save()

    def getMeetingUrl(self):
        #Ik kies nu gewoon de eerste, hier kan meer slimmigheid komen
        if isinstance(self.meeting_url,dict) and len(self.meeting_url)>0:
            meeting_ids = list(self.meeting_url.keys())
            return self.meeting_url[meeting_ids[0]]

    def chooseVideolink(self):
        #ik kies nu gewoon de eerste
        index = 0
        if self.meeting_id:
            meeting = Meeting(self.meeting_id[index])
            if meeting.date:
                room = meeting.whichRoom(self.meeting_id[index])
                url  = meeting.video_url[room]
                if url:
                    return url.replace('http','https')
        if self.videostarttime and isinstance(self.videostarttime,dict):
            keys = list(self.videostarttime.keys())
            meeting = Meeting(int(keys[0]))
            if meeting.date:
                room = meeting.whichRoom(int(keys[0]))
                if room:
                    url = meeting.video_url[room]
                    if url:
                        return url.replace('http','https')
        return ''


    def chooseVideostarttime(self):
        if self.videostarttime and isinstance(self.videostarttime,dict):
            index = 0
            key = list(self.videostarttime.keys())
            return self.videostarttime[key[index]]
        if self.videostarttime and isinstance(self.videostarttime,int):
            return self.videostarttime
        else:
            return 0


    def getPdfUrlFromMeetingUrl(self):
        if not self.meeting_url:
            return
        if self.type =='Agenda' or self.type=='Raadsvoorstel' or self.type=='Ordevoorstel':
            return
        if isinstance(self.meeting_url,dict):
            key = list(self.meeting_url.keys())[0]
            url = self.meeting_url[key]
        else:
            url = self.meeting_url
        soup = web.visitPage(url)

        if '-' in self.title:
            lastPartOfTitle = self.title.split('-')[-1]
        else:
            #splits op A1, A3 etc.
            match = re.findall(r'(A\d+)', self.title)

            if match:
                lastPartOfTitle = match[-1]  # Take the last occurrence if found
            else:
                lastPartOfTitle = self.title


        for documents in soup.findAll('span','document_title'):
            if lastPartOfTitle in documents.text:
                if 'href' in documents.parent.attrs:
                    self.pdf_url = documents.parent['href']
                    return
                else:
                    sublink = documents.parent.find('a')
                    if sublink and 'href' in sublink.attrs:
                        self.pdf_url = sublink['href']
                        return





        print(f'no pdf was found for {self.module_id} {self.title}')












