
from functions.download import web
from classes.module import Module
from classes.meeting import Meeting
from datetime import date
import re


def getInfoFromModulePage(m,driver):
    if not m.url:
        return None
    print(f'Visiting {m.url}')
    soup = web.visitPageAndWaitForPolitiekPortaal(driver,m.url)
    if soup is None:
        return
    spans = soup.find('politiek-portaal').find_all('span')
    url= None
    for span in spans:
        if 'Hoofddocument' in span.get_text():
            path = span.parent.find('a')['href']
            url = f'https://raadsinformatie.eindhoven.nl{path}'
            print('Hoofddocument gevonden')
        if 'Raadsbesluit' in span.get_text():
            try:
                path = span.parent.find('a')['href']
                url = f'https://raadsinformatie.eindhoven.nl{path}'
                print('Raadsbesluit gevonden')
            except:
                print('raadsbesluit gevonden, maar kan de link niet achterhalen')


    if url is None:
        print('Geen document gevonden')
    m.pdf_url =  url
    #zoek de bijlages and meeting urls
    linkbox =  soup.find('div', class_='modules-public-app-history-documents')
    if linkbox:
        links = linkbox.findAll('a')
        if isinstance(m.attachment,str):
            current_value = m.attachment
            m.attachment = {}
            m.attachment[current_value] = 'main'
        if not m.attachment:
            m.attachment = {}
        if isinstance(m.videostarttime,int):
            m.videostarttime = {}
        for link in links:
            a_url_end = link.attrs['href']
            a_url = f'http://raadsinformatie.eindhoven.nl{a_url_end}'
            if 'document' in a_url:
                m.attachment[a_url] = link.text
            if 'vergadering' in a_url:
                continue
                #todo: waarom wordt initiatiefcoorstel international beleid geskipped?
                meeting = Meeting(a_url)
                starttime = meeting.getStartTimeFromURLWithId(a_url)
                if isinstance(m.meeting_url,str):
                    room = meeting.whichRoom(a_url)
                    m.meeting_url = {}
                    m.meeting_url[room] = a_url
                meeting.addModuleToAgenda(m)
                m.videostarttime[meeting.meeting_id] = starttime
                m.meeting_id.append(meeting.meeting_id)
                meeting.save()




def get_raadsvoorstellen_from_page(html,driver):
    rows = html.find_all('td', class_='js_expandable')
    count= 0
    for row in rows:
        print(count)
        count += 1

        if count<435:
            continue
            #todo: verwijder



        data_fields = row.find_all('dd')
        try:
            module_id = row.parent['data-id']
        except:
            print(f'skipping {count-1}')
            continue


        m = Module(module_id)
        m.type = 'Raadsvoorstel'
        if m.url is None:
            m.url = row.parent.find('td',class_='item_actions').find('a')['href']

        print('Extracting data from overview')
        #loop over data fields
        for data_field in data_fields:
            try:
                data_id = int(data_field['data-id'])
                value = data_field.text.strip()
            except:
                continue
            if data_id==24:
                m.bst = value
            elif data_id==15:
                m.date = value
            elif data_id==1:
                m.title = value
            elif data_id == 61:
                m.toezegging = value
            elif data_id == 23:
                m.poho = value
            elif data_id == 54:

                for a in data_field.find_all('a'):
                    if 'http' in a ['href']:
                        m.addMeetingLink(a['href'])






                #if a meeting date is given, use that one.
                try:
                    date_pattern = r"\b\d{2}-\d{2}-\d{4}\b"
                    match = re.search(date_pattern,value)
                    m.date = match.group()
                except:
                    print('no meeting found')
            elif data_id == 45:
                m.type = value
            elif data_id == 36:
                m.member = value #WILL BE PARSED INSIDE MODULE VIA m.parse()
            elif data_id == 37:
                m.party == value #SAME ^^
            elif data_id == 62:
                m.result = value
            elif data_id == 2:
                try:
                    m.attachment = data_field.a['href']
                except:
                    m.attachment = None
            elif data_id==71 and m.vote_id is None:
                m.result = value
                print(f'no votes registered for {m.title}')

        print('Extracting data from module page')
        getInfoFromModulePage(m,driver)

        print('Linking json files')
        m.linkToOtherFiles() #this will add ids where possible.
        m.updateScrapeDate()
        m.save()


def download_raadsvoorstellen(driver, fromDate):
 #---- get pages
    print('RIS query for all raadsvoorstellen, this takes a while')

    today = date.today().strftime('%d-%m-%Y')
    beginHere = fromDate.strftime('%d-%m-%Y')
    url = f"https://raadsinformatie.eindhoven.nl/modules/19/Raadsvoorstellen?module_filter%5Bselect%5D%5B71%5D=none&module_filter%5Bselect%5D%5B52%5D=none&module_filter%5Brange%5D%5B15%5D%5Bfrom%5D={beginHere}&module_filter%5Brange%5D%5B15%5D%5Bto%5D=P{today}&module_filter%5Brange%5D%5B15%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B95%5D%5Bdata_type%5D=datetime&module_filter%5Bcheckbox%5D%5B98%5D=0&module_filter%5Bcheckbox%5D%5B97%5D=0&section="

    soup= web.visitPageWithDriver(driver,url)
    print('RIS query complete')

    #---- process page 1.   page 1 also contains everything
    get_raadsvoorstellen_from_page(soup,driver)


    web.teardown_driver(driver)