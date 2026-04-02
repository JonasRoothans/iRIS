from classes.moduleManager import ModuleManager
from classes.member import Member
from classes.vote import Vote
from classes.voteManager import VoteManager
from collections import defaultdict

def partij_analyse_per_partij(mm,partijfilter):
    type = 'Raadsvoorstel'
    vote_manager = VoteManager()

    # fill up the vote manager
    for vote_id in vote_manager.all():
        vote = Vote(vote_id)

        # Only this political cycle
        if not vote.date:
            continue
        if vote.date < "2022-04-01":
            continue

        #if vote.get_module().type != type:  # 'Raadsvoorstel':#'Amendement': #Moties en toezeggingen':#Raadsvoorstellen
         #   continue

        fig_title = type

        v_index = vote_manager.addvote(vote)
    vote_manager.finalize()  # strip redundant zeros and convert to ndarray

    # Sort columns in chronological order
    vote_manager.sort_chronological()


    analysis = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    coalitie = ['GroenLinks', 'PvdA', 'D66', 'CDA']
    for m in mm.modules:
        if not m.type:
            continue
        if 'motie' in m.type.lower():
            type = 'Motie'
        elif 'amendement' in m.type.lower():
            type = 'Amendement'
        else:
            continue

        if not m.eersteIndiener:
            continue
        partij = Member(m.eersteIndiener).party

        if not partij or not partijfilter in partij:
            continue
        if not m.vote_id:
            continue

        votes = vote_manager.getVotesOfPartiesForVoteID(m.vote_id)
        if not votes:
            print('stop')
        for partij in votes:
            if votes[partij]>0.5:
                voortegen = 'voor'
            elif votes[partij]<-0.5:
                voortegen = 'tegen'
            else:
                voortegen = 'gemengd'


            if not analysis[type][partij][voortegen]:
                analysis[type][partij][voortegen] = [m.module_id]
            else:
                if not isinstance(analysis[type][partij][voortegen], list):
                    analysis[type][partij][voortegen] = [analysis[type][partij][voortegen]]
                analysis[type][partij][voortegen].append(m.module_id)

            if partij in coalitie:
                if not analysis[type]['coalitie'][voortegen]:
                    analysis[type]['coalitie'][voortegen] = [m.module_id]
                else:
                    if not isinstance(analysis[type]['coalitie'][voortegen], list):
                        analysis[type]['coalitie'][voortegen] = [analysis[type]['coalitie'][voortegen]]
                    analysis[type]['coalitie'][voortegen].append(m.module_id)
            else:
                if not analysis[type]['oppositie'][voortegen]:
                    analysis[type]['oppositie'][voortegen] = [m.module_id]
                else:
                    if not isinstance(analysis[type]['oppositie'][voortegen], list):
                        analysis[type]['oppositie'][voortegen] = [analysis[type]['oppositie'][voortegen]]
                    analysis[type]['oppositie'][voortegen].append(m.module_id)

    return analysis


def partij_analyse(mm):

    analysis = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    coalitie = ['GroenLinks', 'PvdA', 'D66', 'CDA']
    for m in mm.modules:
        if not m.type:
            continue
        if 'motie' in m.type.lower():
            type = 'Motie'
        elif 'amendement' in m.type.lower():
            type = 'Amendement'
        elif 'raadsvraag' in m.type.lower():
            type = 'Raadsvraag'
        else:
            continue


        if not m.eersteIndiener:
            continue
        partij = Member(m.eersteIndiener).party


        if 'toezegging' in m.result.lower():
            result = 'toezegging'
        elif 'ingetrokken' in m.result.lower():
            result  = 'ingetrokken'
        elif 'verworpen' in m.result.lower():
            result = 'verworpen'
        elif 'aangenomen' in m.result.lower():
            result = 'aangenomen'
        else:
            result = 'onbekend'

        if not analysis[type][partij][result]:
            analysis[type][partij][result] = [m.module_id]
        else:
            if not isinstance(analysis[type][partij][result], list):
                analysis[type][partij][result] = [analysis[type][partij][result]]
            analysis[type][partij][result].append(m.module_id)

        if partij in coalitie:
            if not analysis[type]['coalitie'][result]:
                analysis[type]['coalitie'][result] = [m.module_id]
            else:
                if not isinstance(analysis[type]['coalitie'][result], list):
                    analysis[type]['coalitie'][result] = [analysis[type]['coalitie'][result]]
                analysis[type]['coalitie'][result].append(m.module_id)
        else:
            if not analysis[type]['oppositie'][result]:
                analysis[type]['oppositie'][result] = [m.module_id]
            else:
                if not isinstance(analysis[type]['oppositie'][result], list):
                    analysis[type]['oppositie'][result] = [analysis[type]['oppositie'][result]]
                analysis[type]['oppositie'][result].append(m.module_id)





    return analysis










