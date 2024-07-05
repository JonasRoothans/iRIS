import numpy as np
from classes.vote import Vote

import matplotlib.colors as mcolors
from functions.analysis.plotPCA import plot_pca_scatter
from classes.voteManager import VoteManager



def create_custom_colormap():
    # Create a custom colormap
    cdict = {
        'red': [(0.0, 1.0, 1.0),
                (0.5, 1.0, 1.0),
                (1.0, 0.0, 0.0)],

        'green': [(0.0, 0.0, 0.0),
                  (0.5, 1.0, 1.0),
                  (1.0, 1.0, 1.0)],

        'blue': [(0.0, 0.0, 0.0),
                 (0.5, 0.0, 0.0),
                 (1.0, 0.0, 0.0)]
    }
    return mcolors.LinearSegmentedColormap('CustomMap', segmentdata=cdict, N=256)


#---Initialize
custom_cmapRG = create_custom_colormap()
vote_manager = VoteManager()


#fill up the vote manager
for vote_id in vote_manager.all():
    vote = Vote(vote_id)

    #Only this political cycle
    if vote.date < "2022-04-01":
        continue
    v_index = vote_manager.addvote(vote)
vote_manager.finalize() #strip redundant zeros and convert to ndarray

#Sort columns in chronological order
vote_manager.sort_chronological()

#Sort rows in order of happiness for member and parties
happiness_member = vote_manager.get_majority_maker_per_member()
happiness_party = vote_manager.get_majority_maker_per_party()

vote_manager.sort_members(happiness_member,'Member Happiness')
vote_manager.sort_parties(happiness_party,'Party Happiness')

#Make a diagram
#vote_manager.show_member_votes(custom_cmap=custom_cmapRG)
#vote_manager.show_party_votes(custom_cmap=custom_cmapRG,weight='Party Happiness')
#vote_manager.show_party_similarity()




#plot_similarity_matrix(sorted_data,sorted_member_names)

party_votes = np.nan_to_num(vote_manager.votes_by_party,vote_manager)
conclusions = vote_manager.voting_result
data = np.vstack((conclusions, party_votes))
labels = vote_manager.party_manager.party_legend
labels.insert(0, 'conclusion')

plot_pca_scatter(data,labels)