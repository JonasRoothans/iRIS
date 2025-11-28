from pypdf import PdfReader
from classes.moduleManager import ModuleManager
from classes.module import Module
from classes.member import Member
import requests
import io
import os
from functions.support import cwdpath


def getPDF(url):
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        return None

def readPDF(pdf):
    reader = PdfReader(pdf)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def extractInfoFromPDF(module):
    if not module.pdf_text:
        return
    if not ('motie' in module.type.lower() or 'amendement' in module.type.lower() or 'raadsvraag' in module.type.lower()):
        return
    #Connect members
    folder_path = cwdpath(os.path.join('json', 'members', 'person'))
    members = os.listdir(folder_path)
    textblock = module.pdf_text.replace(' ','').replace('\n','').replace('ş','s').lower()
    first_index = 100000000000
    for member_id in members:
        m = Member(member_id)
        name = m.name.replace(' ','').lower().replace('ş','s')
        if name in textblock:
            first_index_new = textblock.find(m.name.lower().replace(' ','').replace('ş','s'))
            if first_index_new < first_index:
                module.eersteIndiener = int(m.person_id)
                module.party_list.append(m.party)
                first_index = first_index_new
            if int(m.person_id) not in module.member_id:
                print(f'---added {m.name} to {module.title}')
                module.member_id.append(int(m.person_id))
                module.party_list.append(m.party)
    return


def download_pdf(start_date):
    mm = ModuleManager()
    mm.add2022()
    mm.sort_chronological()

    for module in mm.modules:
        if module.get_date() < start_date.date():
            continue

        if not module.pdf_url and not module.type=='Toezegging':
            module.getPdfUrlFromMeetingUrl()
        if module.pdf_url and not module.pdf_text:
            pdf = getPDF(module.pdf_url)
            try:
                text = readPDF(pdf)
            except:
                text = ''
                print('stop')

            module.pdf_text = text
            module.extract_keywords()
        extractInfoFromPDF(module)
        try:
            module.save()
        except:
            print('stop')


