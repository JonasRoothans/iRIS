class PartyManager():
    def __init__(self):
        self.party_legend = {}
        self.member_manager = None
        self.vote_manager = None
        self.weights = {}

    def get_index(self,party):

        if party not in self.party_legend:
            i = len(self.party_legend)
            self.party_legend[party] = i
        else:
            i = self.party_legend[party]

        return i

    def connect_vm(self,vm):
        if not self.vote_manager:
            self.vote_manager = vm

    def connect_mm(self,mm):
        if not self.member_manager:
            self.member_manager = mm
