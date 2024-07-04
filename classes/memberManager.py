from classes.partyManager import PartyManager
class MemberManager():
    def __init__(self):
        self.member_legend = {}
        self.vote_manager = None
        self.party_manager = None
        self.weights = {}


    def get_index(self,member):
        """
               Returns the index of the member. If the member is not present in
               member_legend, it will be added to member_legend and member_names.

               Args:
                   member: The member object to find or add.

               Returns:
                   The index of the member.
               """
        if member not in self.member_legend:
            i = len(self.member_legend)
            self.member_legend[member] = i
        else:
            i = self.member_legend[member]

        return i
    def connect_vm(self,vm):
        if not self.vote_manager:
            self.vote_manager = vm

    def connect_pm(self,pm):
        if not self.party_manager:
            self.party_manager = pm
