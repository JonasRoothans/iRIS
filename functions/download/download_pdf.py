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
    #Connect members
    folder_path = cwdpath(os.path.join('json', 'members', 'person'))
    members = os.listdir(folder_path)
    for member_id in members:
        m = Member(member_id)
        if m.name in module.pdf_text:
            if m.person_id not in module.member_id:
                print(f'---added {m.name} to {module.title}')
                module.member_id.append(int(m.person_id))
                module.party_list.append(m.party)
    return


def download_pdf():
    mm = ModuleManager()
    all_modules = mm.all()

    for m in all_modules:
        module = Module(m)
        if module.pdf_url:
            pdf = getPDF(module.pdf_url)
            try:
                text = readPDF(pdf)
            except:
                text = ''
                print('stop')

            module.pdf_text = text
            extractInfoFromPDF(module) #doet nog niks

            module.save()
