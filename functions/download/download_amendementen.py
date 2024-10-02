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
        m = Module(module_id)
        if m.title == title:
            return m.module_id
    print('No match found')
    return None




def download_amendementen(driver):
    files = list_files_with_prefix(f'{os.getcwd()}/json/modules', 'a_')
    for file in files:
        m = Module(file)
        if m.url is not None:
            soup = web.visitPageWithDriver(driver,m.url)
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
            m.save()



    print(files)