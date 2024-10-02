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

def createRow(vm,i, t):
    v = vm.votes[i]
    with t:

        try:
            print(v.module_id)
            m = v.get_module()
        except:
            print(f'failed for{v.module_id}')
            return 0

        row = tr()
        row += td(v.vote_id)
        row += td(a(m.module_id,href=m.url))
        row += td(a(m.date,href=m.meeting_url))
        if m.type == 'Raadsvoorstellen':
            row += td('R')
            row['id'] = 'college'
        elif m.type == 'Amendement':
            row += td('A')
            row['id'] = 'raad'
        elif m.type =='Motie':
            row += td('M')
            row ['id'] = 'raad'
        elif m.type == 'Ordevoorstel':
            row += td('O')
            row['id'] = 'raad'
        elif m.type == 'Vrije motie':
            row += td('VM')
            row['id'] = 'raad'
        elif m.type == 'Initiatiefvoorstel':
            row += td('I')
            row['id'] = 'raad'
        else:
            row += td('?')


        row += td(m.title)
        if v.result == 'aangenomen':
            row += td(v.result, id='aangenomen')
        elif v.result == 'verworpen':
            row += td(v.result, id='verworpen')
        else:
            row += td('?')

        iP =0
        while iP < len(vm.party_manager.party_legend):
            if vm.votes_by_party[iP, i] == 1:
                row += td('Voor', id='voor')
            elif vm.votes_by_party[iP, i] == -1:
                row += td('Tegen', id='tegen')
            elif vm.votes_by_party[iP, i] == 0:
                row += td('Gemengd', id='gemengd')
            else:
                row +=td('?')

            iP+=1





    return 1


#----- code:

vote_manager = VoteManager()


#fill up the vote manager
for vote_id in vote_manager.all():
    vote = Vote(vote_id)


    v_index = vote_manager.addvote(vote)
vote_manager.finalize() #strip redundant zeros and convert to ndarray

#Sort columns in chronological order
vote_manager.sort_chronological()

#Sort rows in order of happiness for parties
happiness_party = vote_manager.get_majority_maker_per_party()
vote_manager.sort_parties(happiness_party,'Party Happiness')


rows = {}

doc = dominate.document(title="iRIS")
with doc.head:
    # Add the hidden class to manage row visibility
    style("""
    .hidden { display: none; }
    button { color: white; padding: 10px 20px; border: none; cursor: pointer; font-size: 14px; }
    #voor { background-color : green; color: white}
    #tegen { background-color : red; color: white}
    #gemengd { background-color: yellow; color: black}
    #aangenomen {color: green}
    #verworpen {color: red}
    """)

    # Link to the external JS file
    script(src="toggleRows.js", type="text/javascript")


with doc.body:
    # List of IDs for which we need buttons
    ids = ['college', 'raad']

    # Create a button for each unique id, dynamically calling toggleRowsById
    for id_val in ids:
        button(f'Verberg {id_val}',
               onclick=f'toggleRowsById("{id_val}", this)',
               style="background-color: red; margin-right: 10px;")

    h1('last update: 30 sep 2024')
    t =  table().add(tbody())
    with t:
        row = tr()
        row += th('vote_id')
        row += th('module')
        row += th('___Date___')
        row += th('type')
        row += th('Content')
        row += th('result')

        iP =0
        while iP < len(vote_manager.party_manager.party_legend):
            row += th(vote_manager.party_manager.party_legend[iP])
            iP+=1

    iV = 0
    while iV < len(vote_manager.votes):
        v = vote_manager.votes[iV]
        rows[v.vote_id] = createRow(vote_manager, iV, t)
        iV += 1




with open(f'{os.getcwd()}/Presentation/output/index2.html', 'w') as f:
    f.write(doc.render())