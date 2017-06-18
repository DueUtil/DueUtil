from fun.game import players
import discord

"""
MUMMY MUMMY LOOK AT ME!!!!

I'm UNIT TESTING


Mum: That's nice dear
"""

test_player = Player(discord.Member(user={"id":"000TEST","name":"Testy Mc Test Face"}),no_save=True)

def test(expect=None):
    
    def tester(test_func):
              
        output = test_func()
        if output != expect:
            print("TEST FAILED!")
            print("EXPECTED")
            print(expect)
            print("GOT")
            print(output)
        else:
            print("Test passed")
    
    return tester
            
@test(expect="Testy Mc Test Face")  
def name_test():
    return test_player.name
    
@test(expect="000TEST")  
def id_test():
    return test_player.id
        
