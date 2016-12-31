'''
Created on Jun 5, 2015

@author: Gideon
'''

#import G4InRow.roomsM_3 as roomsM
import src.globals as gls

def server_pre_game_init(pre_game):
    """currently no init
    """
    return

def server_pre_game(pre_game,rx_message_from_client):
    """let's start with auto /dummy confirmation
    pre_game is the game_instance (srooms.games[room_index])
    """
    if pre_game.state == 0: #wait for clinet authentication
        if True:
            pre_game.state = 10 #successful authentication
            #now move it to a real game
    if pre_game.state==10: #move to the real game
        #delete the old game
        pre_game_room_number = pre_game.room_number #get the old room number

        del pre_game
        ###pre_game.room_status = 0 # the room is empty again

        #set the client to a new room per game
        client_index=pre_game.players[0]
        new_game_type = gls.G4INROW_type #in the future may be requested by client
        result = move_to_real_game (client_index,new_game_type)

    return result

def  move_to_real_game (new_game_type):
    """Find a new room.
    Leave the old room and reset/delete what needed.
    Input: The client index and the requested game type
    """
    return

