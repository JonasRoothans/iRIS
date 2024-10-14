import os
import glob
from classes.module import Module
from functions.download import web

def list_files_with_prefix(directory, prefix):
    full_paths =  glob.glob(os.path.join(directory, f'{prefix}*'))
    filenames = [os.path.basename(path) for path in full_paths]
    return filenames

def find_module_with_title(title):
    folder_path = f'{os.getcwd()}/json/modules'
    modules = os.listdir(folder_path)
    for module_id in modules:
        if module_id.startswith('.'):
            continue

        m = Module(module_id)
        if m.title == title:
            return m.module_id
    print('No match found')
    return None


def extract_real_title(title):
    # Find positions of '-' and '('
    dash_pos = title.find('mendement')+9
    paren_pos = title.find('(')

    # Extract text between '- ' and ' (' (trimming any optional surrounding whitespace)
    if dash_pos != -1 and paren_pos != -1:
        real_title = title[dash_pos + 1:paren_pos].strip()  # Extract part between - and (
    else:
        real_title = title  # If not found, leave the title as it is

    return real_title

def find_attachment_from(id, soup, real_title):
    ancestor = soup.find('div', id=f'chart_{id}').find_parent('div', class_='agenda_item_content')
    docs = ancestor.find('ul',class_='documents').find_all('li')
    for doc in docs:
        if real_title in doc.find('span', class_='document_title').get_text():
            return doc.find('a')['href']

    return None




def download_amendementen(driver):
    files = list_files_with_prefix(f'{os.getcwd()}/json/modules', 'a_')
    for file in files:
        m = Module(file)
        if m.meeting_url is not None:
            soup = web.visitPageWithDriver(driver,m.meeting_url)
            span = soup.find('span',string = m.title)

            title = soup.find('div',id=f'chart_{m.vote_id}').find_parent('li').find_parent('li').attrs['data-title']
            module_id = find_module_with_title(title)
            m.parent = module_id
            parent = Module(m.parent)
            if module_id not in parent.children:
                parent.children.append(m.module_id)
                parent.save()
            if module_id:
                print(f'{m.title} connected to: {title}')
            m.pdf_url = find_attachment_from(m.vote_id, soup, extract_real_title(m.title))
            m.type = 'Amendement'
            m.save()



    print(files)