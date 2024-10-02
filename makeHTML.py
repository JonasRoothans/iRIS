import dominate
from dominate.tags import *
import os
from classes.voteManager import VoteManager
from classes.moduleManager import ModuleManager
from classes.vote import Vote
from classes.module import Module


def getbgcolor(m):
    bgcolor = '#fff'
    if m.result == 'Ingetrokken na toezegging':
        bgcolor = '#ffa'
    if m.result == 'Afgerond':
        bgcolor = '#afa'
    if m.result == 'Verworpen' or m.result == 'verworpen':
        bgcolor = '#faa'
    if m.result == 'aangenomen':
        bgcolor = '#afa'
    if m.result == 'Ingetrokken':
        bgcolor = '#aaf'
    if m.type == 'Toezegging':
        bgcolor = '#ddd'
    return bgcolor

def createRow(m, t):
    m.clean()
    with t:
        if m.type == 'Toezegging':
            row = tr(bgcolor=getbgcolor(m),id='toezegging')
        elif m.type == 'Motie':
            row = tr(bgcolor=getbgcolor(m), id='motie')
        elif m.type =='Vrije Motie':
            row = tr(bgcolor=getbgcolor(m), id='vrijemotie')
        elif m.type == 'Raadsvoorstellen':
            row = tr(bgcolor=getbgcolor(m), id='raadsvoorstel')
        elif m.type == 'Amendement':
            row = tr(bgcolor=getbgcolor(m), id='amendement')
        else:
            row = tr(bgcolor=getbgcolor(m))

        row += td(a(m.module_id,href=m.url))
        row += td(a(m.date,href=m.meeting_url))
        row += td(m.title)

        for child in m.children:
            subrow = tr()
            try:
                childModule = Module(child)
            except:
                print(f'module {child} could not be loaded')
                continue
            subrow += td(a(childModule.module_id,href=childModule.url))
            childModule.clean()
            if childModule.type == 'Toezegging':
                subrow['id'] = 'toezegging'
                subrow += td(a('T --->',href=childModule.meeting_url))
                subrow += td(childModule.toezegging,
                             bgcolor=getbgcolor(childModule))
            elif childModule.type == 'Motie':
                subrow['id'] = 'motie'
                subrow += td(a('M --->',href=childModule.meeting_url))
                subrow += td(f'{childModule.result} : {childModule.title} ({childModule.toezegging})',
                             bgcolor=getbgcolor(childModule))
            elif childModule.type == 'Vrije motie':
                subrow['id'] = 'vrijemotie'
                subrow += td(a(childModule.date,href=m.meeting_url))
                subrow += td(f'{childModule.result} : {childModule.title} ({childModule.toezegging})',
                             bgcolor=getbgcolor(childModule))
            elif childModule.type== 'Amendement':
                subrow['id'] = 'amendement'
                subrow += td(a('A --->', href=childModule.meeting_url))
                subrow += td(f'{childModule.result} : {childModule.title}',
                             bgcolor=getbgcolor(childModule))

            else:
                subrow += td(a('? --->', href=childModule.meeting_url))
                subrow += td(f'{childModule.result} : {childModule.title} ({childModule.toezegging})',
                             bgcolor=getbgcolor(childModule))


    return 1



vote_manager = VoteManager()
module_manager = ModuleManager()
module_manager.addall()
module_manager.sort_chronological()
rows = {}

doc = dominate.document(title="iRIS")
with doc.head:
    # Add the hidden class to manage row visibility
    style("""
    .hidden { display: none; }
    button { color: white; padding: 10px 20px; border: none; cursor: pointer; font-size: 14px; }
    """)

    # Link to the external JS file
    script(src="toggleRows.js", type="text/javascript")


with doc.body:
    # List of IDs for which we need buttons
    ids = ['toezegging', 'motie', 'vrijemotie', 'raadsvoorstel', 'amendement']

    # Create a button for each unique id, dynamically calling toggleRowsById
    for id_val in ids:
        button(f'Verberg {id_val}',
               onclick=f'toggleRowsById("{id_val}", this)',
               style="background-color: red; margin-right: 10px;")

    h1('all jsons')
    t =  table().add(tbody())
    with t:
        row = tr()
        row += th('module')
        row += th('___Date___')
        row += th('Content')

    for m in module_manager.modules:
        if m.parent:
            if m.parent in rows:
                row = rows[m.parent]
            else:
                rows[m.parent] = createRow(Module(m.parent),t)
        else:
            if m.module_id not in rows:
                rows[m.module_id] = createRow(m, t)




with open(f'{os.getcwd()}/Presentation/output/index.html', 'w') as f:
    f.write(doc.render())