from functions.download import web
from classes.module import Module
from datetime import date

def get_letters_from_page(html):
    done = 0
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

            if data_id==15:
                m.date = value
            elif data_id==1:
                m.title = value
            elif data_id==44:
                m.date = value
            elif data_id==5:
                m.bst = value
            elif data_id == 61:
                m.text = value
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
                    m.pdf_url = data_field.a['href']
                except:
                    m.pdf_url = None
        if m.date is None:
            print('stophier')
        m.save()
    return False #false, because it has not reached the limit.

def download_brieven(driver, fromDate):
 #---- get pages
    print('RIS query for all letters, this takes a while')
    today = date.today().strftime('%d-%m-%Y')
    beginHere = fromDate.strftime('%d-%m-%Y')
    #url = "https://raadsinformatie.eindhoven.nl/modules/6/Moties/view?month=all&year=all&week=all&module_filter%5Bselect%5D%5B45%5D=none&module_filter%5Bselect%5D%5B26%5D=none&module_filter%5Brange%5D%5B15%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B28%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B17%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B16%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B39%5D%5Bdata_type%5D=datetime&module_filter%5Bcheckbox%5D%5B17%5D=0&module_filter%5Bcheckbox%5D%5B21%5D=0&module_filter%5Bcheckbox%5D%5B20%5D=0&section="
    url = f'https://raadsinformatie.eindhoven.nl/modules/6/Moties?module_filter%5Bselect%5D%5B45%5D=none&module_filter%5Bselect%5D%5B26%5D=none&module_filter%5Brange%5D%5B15%5D%5Bfrom%5D={beginHere}&module_filter%5Brange%5D%5B15%5D%5Bto%5D={today}&module_filter%5Brange%5D%5B15%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B28%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B17%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B16%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B39%5D%5Bdata_type%5D=datetime&module_filter%5Bcheckbox%5D%5B17%5D=0&module_filter%5Bcheckbox%5D%5B21%5D=0&module_filter%5Bcheckbox%5D%5B20%5D=0&section=&sort=&sort_dir=asc'

    url = f'https://raadsinformatie.eindhoven.nl/modules/8/Bestuursdocumenten?module_filter%5Bselect%5D%5B45%5D=none&module_filter%5Bselect%5D%5B52%5D=none&module_filter%5Brange%5D%5B44%5D%5Bfrom%5D={beginHere}&module_filter%5Brange%5D%5B44%5D%5Bto%5D={today}&module_filter%5Brange%5D%5B44%5D%5Bdata_type%5D=datetime&module_filter%5Brange%5D%5B7%5D%5Bdata_type%5D=datetime&section=&sort=&sort_dir=asc'


    soup= web.visitPageWithDriver(driver,url)
    print('RIS query complete')

    #---- process page 1
    get_letters_from_page(soup)

    #--- loop remaning pages
    pages = soup.find_all('li',class_='page')
    for page in pages:
        try:
            url_page = page['href']
        except:
            continue
        if url_page=="":
            continue #firstpage is done.
        soup_page = web.visitPageWithDriver(driver,url_page)
        done = get_letters_from_page(soup_page)
        if done:
            break


    #---- eixt
    web.teardown_driver(driver)