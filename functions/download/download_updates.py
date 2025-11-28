from classes.moduleManager import ModuleManager
from classes.module import Module
from functions.download import web
from datetime import datetime, timedelta

def update(m,driver):
    # Get today's date
    today = datetime.now()

    if m.meeting_url == m.url:
        m.url = None
        return
    if 'brief' in m.type.lower():
        return
    print(m.url)

    if m.lastScrapeDate:
        parsed_date = datetime.strptime(m.lastScrapeDate, "%d-%m-%Y")
        difference = today - parsed_date
        if difference < timedelta(days=7):
            print('too soon')
            return

    soup = web.visitPageAndWaitMetaInfo(driver, m.url)
    if soup is None:
        return
    data = soup.find('dl')
    if data:
        for dt in data.findAll('dt'):
            if dt.text == 'Portefeuillehouder':
                m.poho = dt.next_sibling.text
            if dt.text == 'Stand van zaken':
                m.svz = dt.next_sibling.text
            if dt.text == 'Termijn afdoening':
                m.afgedaan = dt.next_sibling.text

    # Get today's date
    m.lastScrapeDate = today.strftime("%d-%m-%Y")

    m.save()




def download_updates(driver, fromDate):
    print('jahoor')
    mm = ModuleManager()
    mm.addall()
    #mm.sort_chronological()
    for m in mm.modules:
        if m.get_date() > fromDate.date():
            update(m,driver)

def download_update(driver,id):
    m = Module(id)
    update(m,driver)