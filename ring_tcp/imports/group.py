
class Group:

    def __init__(self, name):
        self.name = name;
        self.party_members = [];
        self.ip_list = [];

    def get_name(self):
        return self.name;

    def add_member(self, party):
        self.party_members.append(party);

    def add_ip(self, ip):
        self.ip_list.append(ip);
        
    def get_members(self):
        return self.party_members;

    def get_ip_list(self):
        return self.ip_list;

    

