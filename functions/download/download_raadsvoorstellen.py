
from functions.download import web
from classes.module import Module
from datetime import date



def get_raadsvoorstellen_from_page(html):
    rows = html.find_all('td', class_='js_expandable')
    count= 0
    for row in rows:
        print(count)
        count += 1

        data_fields = row.find_all('dd')
        try:
            module_id = row.parent['data-id']
        except:
            print(f'skipping {count-1}')
            continue


        m = Module(module_id)
        if m.url is None:
            m.url = row.parent.find('td',class_='item_actions').find('a')['href']

        #loop over data fields
        for data_field in data_fields:
            try:
                data_id = int(data_field['data-id'])
                value = data_field.text.strip()
            except:
                print(f'skipping datafield')
                continue
            if data_id==24:
                m.bst = value
            if data_id==15:
                m.date = value
            elif data_id==1:
                m.title = value
            elif data_id == 61:
                m.toezegging = value
            elif data_id == 23:
                m.poho = value
            elif data_id == 54:
                try:
                    m.meeting_url = data_field.find('a')['href']
                except:
                    m.meeting_url = None
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
                print(f'no votes registered for {m.title}')
        m.linkToOtherFiles() #this will add ids where possible.
        m.save()


def download_raadsvoorstellen(driver):
 #---- get pages
    print('RIS query for all raadsvoorstellen, this takes a while')


    today = date.today().strftime('%d-%m-%Y')
    url = f"https://raadsinformatie.eindhoven.nl/modules/19/Raadsvoorstellen?module_filter%5Bselect%5D%5B71%5D=none&module_filter%5Bselect%5D%5B52%5D=none&module_filter%5Brange%5D%5B15%5D%5Bfrom%5D=01-01-2022&module_filter%5Brange%5D%5B15%5D%5Bto%5D=P{today}&module_filter%5Brange%5D%5B15%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B95%5D%5Bdata_type%5D=datetime&module_filter%5Bcheckbox%5D%5B98%5D=0&module_filter%5Bcheckbox%5D%5B97%5D=0&section="
    #url = "https://raadsinformatie.eindhoven.nl/modules/19/Raadsvoorstellen/view?month=7&year=2024&week=all&module_filter%5Bselect%5D%5B71%5D=none&module_filter%5Bselect%5D%5B52%5D=none&module_filter%5Brange%5D%5B15%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B95%5D%5Bdata_type%5D=datetime&module_filter%5Bcheckbox%5D%5B98%5D=0&module_filter%5Bcheckbox%5D%5B97%5D=0&section="
    #driver = web.setup_driver()


    soup= web.visitPageWithDriver(driver,url)
    print('RIS query complete')

    #---- process page 1
    get_raadsvoorstellen_from_page(soup)

    #--- loop remaning pages <<VOLGENS MIJ STAAN ALLE HITS AL OP DE EERSTE PAGINA, ALLEEN NOG NIET ZICHTBAAR>>
    #pages = soup.find_all('li',class_='page')
    #for page in pages:
     #   if page.a['href']=='':
     #       # firstpage is done.
     #       continue
     #   url_page = page.a['href']
      #  soup_page = web.visitPageWithDriver(driver,f'https://raadsinformatie.eindhoven.nl{url_page}')
     #   get_raadsvoorstellen_from_page(soup_page)

    #---- eixt
    web.teardown_driver(driver)