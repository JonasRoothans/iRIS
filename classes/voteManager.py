import numpy as np
import os
from classes.vote import Vote
from classes.member import Member
from classes.memberManager import MemberManager
from classes.partyManager import PartyManager
from datetime import datetime
from typing import List
import matplotlib.pyplot as plt
from functions.support import cwdpath


class VoteManager:
    def __init__(self):
        self.votes = [] #will contain a list of Vote objects
        self.votes_by_member = np.zeros((1000,1000))
        self.votes_by_party = np.zeros((1000,1000))
        self.voting_result = np.zeros(1000)
        self.member_manager = MemberManager()
        self.party_manager = PartyManager()

        #--crosslink managers
        self.member_manager.connect_pm(self.party_manager)
        self.member_manager.connect_vm(self)
        self.party_manager.connect_mm(self.member_manager)
        self.party_manager.connect_vm(self)

        #-- Set to nan
        self.votes_by_party[:] = np.nan
        self.votes_by_member[:] = np.nan


    def connect(self,mm):
        if not self.member_manager:
            self.member_manager = mm
            mm.connect(self)

    def all(self):
        # Get all vote ids
        folder_path = cwdpath(os.path.join('json','votes'))
        return os.listdir(folder_path)

    def addvote(self,vote:Vote):
        if vote in self.votes:
            return self.votes.index(vote)

        #add the object
        self.votes.append(vote)
        index = len(self.votes) -1
        print(index)

        # save the conclusion
        self.voting_result[index] = 1 if vote.result =='aangenomen' else -1

        #add the info to the lists for each member
        for member in vote.member_votes:
            member_index = self.member_manager.get_index(member)
            vote_value = vote.vote_as_int_for_member(member)

            #record individual member vote
            self.votes_by_member[member_index][index] = vote_value

            #record party vote
            party_index = self.party_manager.get_index(Member(member).party)
            party_vote_value = self.votes_by_party[party_index][index]

            if np.isnan(party_vote_value):
                self.votes_by_party[party_index][index] = vote_value
            elif int(self.votes_by_party[party_index][index]) != vote_value:
                self.votes_by_party[party_index][index] = 0

        return index

    def sort_chronological(self):
        # Extract dates and their corresponding indices
        dates_with_indices = [(datetime.strptime(vote.date, '%Y-%m-%d'), index) for index, vote in
                              enumerate(self.votes)]
        # Sort the list of tuples by the date
        sorted_dates_with_indices = sorted(dates_with_indices)

        # Extract the new order of indices
        sorted_indices = [index for _, index in sorted_dates_with_indices]

        # Reorder votes, votes_by_member, and voting_result
        self.votes = [self.votes[i] for i in sorted_indices]
        self.votes_by_member = self.votes_by_member[:, sorted_indices]
        self.votes_by_party = self.votes_by_party[:,sorted_indices]
        self.voting_result = [self.voting_result[i] for i in sorted_indices]

    @staticmethod
    def calculate_similarity(row1: List[int], row2: List[int]) -> float:
        if isinstance(row1, list):
            row1 = np.array(row1)
        if isinstance(row2, list):
            row2 = np.array(row2)

        valid_mask = ~np.isnan(row1) * ~np.isnan(row2)
        valid_row1 = np.array(row1)[valid_mask]
        valid_row2 = np.array(row2)[valid_mask]

        if len(valid_row1)==0:
            return 0

        matching_elements = np.sum(valid_row1==valid_row2)
        similarity_percentage = (matching_elements / len(valid_row1))*100
        return similarity_percentage

    def get_majority_maker_per_member(self):
        similarities = []
        for member_votes in self.votes_by_member:
            similarity = VoteManager.calculate_similarity(member_votes,self.voting_result)
            similarities.append(similarity)
        return similarities

    def get_majority_maker_per_party(self):
        similarities = []
        for party_votes in self.votes_by_party:
            similarity = VoteManager.calculate_similarity(party_votes,self.voting_result)
            similarities.append(similarity)
        return similarities

    def finalize(self):
        self.votes_by_member = np.array(self.votes_by_member, dtype=float)[0:len(self.member_manager.member_legend),0:len(self.votes)]
        self.votes_by_party = np.array(self.votes_by_party, dtype=float)[0:len(self.party_manager.party_legend),0:len(self.votes)]
        self.voting_result = np.array(self.voting_result, dtype=int)[0:len(self.votes)]

    def sort_members(self,order,label):
        #zip data together for joined sorting
        similarity_row_member_pairs = list(zip(order, self.votes_by_member, self.member_manager.member_legend))

        # Sort these pairs based on the similarity scores in descending order
        similarity_row_member_pairs.sort(key=lambda x: x[0], reverse=True)

        # Extract the rows and member names in sorted order
        self.votes_by_member = np.array([row for _, row, _ in similarity_row_member_pairs])
        self.member_manager.member_legend = [member for similarity, _, member in similarity_row_member_pairs]
        self.member_manager.weights[label] = np.array([order for order, _, _ in similarity_row_member_pairs])

    def sort_parties(self, order, label):
        # zip data together for joined sorting
        similarity_row_party_pairs = list(zip(order, self.votes_by_party, self.party_manager.party_legend))

        # Sort these pairs based on the similarity scores in descending order
        similarity_row_party_pairs.sort(key=lambda x: x[0], reverse=True)

        # Extract the rows and member names in sorted order
        self.votes_by_party = np.array([row for _, row, _ in similarity_row_party_pairs])
        self.party_manager.party_legend = [party for similarity, _, party in similarity_row_party_pairs]
        self.party_manager.weights[label] = np.array([order for order, _, _ in similarity_row_party_pairs])


    def show_member_votes(self,custom_cmap = None):
        # Prepend the conclusion_vector to the sorted_data
        sorted_data = np.vstack((self.voting_result,self.votes_by_member))

        ylabels = [f'{Member(i)}' for i in self.member_manager.member_legend]
        ylabels.insert(0,'conclusion')

        # Create the figure with calculated size
        fig, ax1 = plt.subplots(figsize=(5,5))

        # Plot using imshow
        if custom_cmap:
            cax = ax1.imshow(sorted_data, aspect='auto', interpolation='none', cmap=custom_cmap)
        else:
            cax = ax1.imshow(sorted_data, aspect='auto', interpolation='none')

        # Define the y-tick positions and labels
        ax1.set_yticks(np.arange(len(ylabels)))
        ax1.set_yticklabels(ylabels)

        # Display the plot
        plt.show()

    def show_party_votes(self,custom_cmap=None,weight=None,fig_title=''):
        # Prepend the conclusion_vector to the sorted_data
        sorted_data = np.vstack((self.voting_result, self.votes_by_party))

        if weight is None:
            ylabels = [f'{i}' for i in self.party_manager.party_legend]
        else:
            ylabels = [f'{party} ({self.party_manager.weights[weight][index]:.0f}%)'
                   for index, party in enumerate(self.party_manager.party_legend)]


        ylabels.insert(0, 'conclusion')

        # Create the figure with calculated size
        fig, ax1 = plt.subplots(figsize=(5, 5))

        # Plot using imshow
        if custom_cmap:
            cax = ax1.imshow(sorted_data, aspect='auto', interpolation='none', cmap=custom_cmap)
        else:
            cax = ax1.imshow(sorted_data, aspect='auto', interpolation='none')

        # Define the y-tick positions and labels
        ax1.set_yticks(np.arange(len(ylabels)))
        ax1.set_yticklabels(ylabels)
        ax1.set_title(fig_title)

        def format_coord(x,y):
            title = self.votes[int(np.round(x))].description
            date = self.votes[int(np.round(x))].date
            return f'{date}:{title.strip()}'


        ax1.format_coord = format_coord

        # Display the plot
        plt.show()


    def show_party_similarity(self,fig_title):
        n_parties = len(self.party_manager.party_legend)
        similarities = np.zeros((n_parties,n_parties))
        similarities[:] = np.nan

        for a,party_votes_A in enumerate(self.votes_by_party):
            for b,party_votes_B in enumerate(self.votes_by_party):
                similarities[a,b] = self.calculate_similarity(party_votes_A,party_votes_B)

        fig, ax = plt.subplots(figsize=(10, 8))

        # Display the heatmap
        cax = ax.imshow(similarities, aspect='auto', interpolation='none', cmap='coolwarm')

        # Add colorbar
        cbar = fig.colorbar(cax, ax=ax)
        cbar.set_label('Similarity (%)')

        # Print similarity values inside the cells
        for i in range(similarities.shape[0]):
            for j in range(similarities.shape[1]):
                ax.text(j, i, f"{similarities[i, j]:.1f}%", ha='center', va='center', color='black')

        # Set the ticks and labels for x and y axes
        party_names = self.party_manager.party_legend
        ax.set_xticks(np.arange(len(party_names)))
        ax.set_yticks(np.arange(len(party_names)))
        ax.set_xticklabels(party_names, rotation=45, ha='right')
        ax.set_yticklabels(party_names)
        ax.set_title(fig_title)

        # Set axis labels
        ax.set_xlabel('Party')
        ax.set_ylabel('Party')

        plt.show()


