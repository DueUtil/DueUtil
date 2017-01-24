
players = dict();

class Player():
    
    def __init__(self,id,name):
        self.name = name;
        self.id = str(id);
        
    def echo_name():
        print(self.name);
        
    @staticmethod
    def find_p(id):
        global players;
        return players[str(id)];
        
def player_join(id,name):
    global players;
    
    p = Player(id,name);
    players[p.id] = p;
    
    print(players);
