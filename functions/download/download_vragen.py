
from functions.download import web
from classes.module import Module
from datetime import date
import re

def getMostRelevantPDF(m,driver):


    if not m.url:
        return None
    soup = web.visitPageAndWaitForVraag(driver, m.url)
    if soup is None:
        return
    spans = soup.find('politiek-portaal').find_all('span')
    url= None
    for span in spans:
        if 'Vraag' in span.get_text():
            path = span.parent.find('a')['href']
            url = f'https://raadsinformatie.eindhoven.nl{path}'
            print('Vraag')
        if 'antwoord' in span.get_text():
            try:
                path = span.parent.find('a')['href']
                url = f'https://raadsinformatie.eindhoven.nl{path}'
                print('Antwoord')
            except:
                print('raadsbesluit gevonden, maar kan de link niet achterhalen')

            return url
    if url is None:
        print('Geen document gevonden')
    return url



def get_vragen_from_page(html,driver):
    rows = html.find_all('td', class_='js_expandable')
    count = 0
    for row in rows:
        print(count)
        count += 1

        # if count < 336:
        #   continue
        data_fields = row.find_all('dd')
        try:
            module_id = row.parent['data-id']
        except:
            print(f'skipping {count - 1}')
            continue

        m = Module(module_id)
        m.type = 'Raadsvraag'
        if m.url is None:
            m.url = row.parent.find('td', class_='item_actions').find('a')['href']

        # loop over data fields
        for data_field in data_fields:
            try:
                data_id = int(data_field['data-id'])
                value = data_field.text.strip()
            except:
                print(f'skipping datafield')
                continue
            if data_id == 24:
                m.bst = value
            elif data_id == 15: #28: datum afdoening
                m.date = value
            elif data_id == 1:
                m.title = value
            elif data_id == 2:
                try:
                    m.attachment = data_field.a['href']
                except:
                    m.attachment = None
            elif data_id == 36:
                m.member = value #WILL BE PARSED INSIDE MODULE VIA m.parse()
            elif data_id == 37:
                m.party == value #SAME ^^
        m.pdf_url = getMostRelevantPDF(m, driver)
        m.linkToOtherFiles()  # this will add ids where possible.
        m.updateScrapeDate()
        m.save()




def download_vragen(driver,fromDate):
 #---- get pages
    print('RIS query for all raadsvoorstellen, this takes a while')


    today = date.today().strftime('%d-%m-%Y')
    beginHere = fromDate.strftime('%d-%m-%Y')
    url = f"https://raadsinformatie.eindhoven.nl/modules/19/Raadsvoorstellen?module_filter%5Bselect%5D%5B71%5D=none&module_filter%5Bselect%5D%5B52%5D=none&module_filter%5Brange%5D%5B15%5D%5Bfrom%5D={beginHere}&module_filter%5Brange%5D%5B15%5D%5Bto%5D=P{today}&module_filter%5Brange%5D%5B15%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B95%5D%5Bdata_type%5D=datetime&module_filter%5Bcheckbox%5D%5B98%5D=0&module_filter%5Bcheckbox%5D%5B97%5D=0&section="
    url = f"https://raadsinformatie.eindhoven.nl/modules/4/Raadsvragen?module_filter%5Bselect%5D%5B71%5D=none&module_filter%5Bselect%5D%5B52%5D=none&module_filter%5Brange%5D%5B15%5D%5Bfrom%5D={beginHere}&module_filter%5Brange%5D%5B15%5D%5Bto%5D=P{today}&module_filter%5Brange%5D%5B15%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B95%5D%5Bdata_type%5D=datetime&module_filter%5Bcheckbox%5D%5B98%5D=0&module_filter%5Bcheckbox%5D%5B97%5D=0&section="

    #driver = web.setup_driver()


    soup= web.visitPageWithDriver(driver,url)
    print('RIS query complete')

    #---- process page 1
    get_vragen_from_page(soup,driver)