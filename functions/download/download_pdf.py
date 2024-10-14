from pypdf import PdfReader
from classes.moduleManager import ModuleManager
from classes.module import Module
import requests
import io


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
    #bijv. de eerste indiener
    return


def download_pdf():
    mm = ModuleManager()
    all_modules = mm.all()

    for m in all_modules:
        module = Module(m)
        if module.pdf_url:
            pdf = getPDF(module.pdf_url)
            text = readPDF(pdf)

            module.pdf_text = text
            extractInfoFromPDF(module) #doet nog niks

            module.save()
