'''
Created on May 10, 2015

@author: Gideon
'''
import queue
#from G4InRow.boardClass import Board ???qqq

#GAME SCALE
#==========
max_clients=4
MAX_ROOMS = 3

debug_level=2 #0 for no debug, 1 for basic debug, 2 for details

SOM="[[[" #Start of message delimiter
EOM="]]]" #End of message delimiter
sub_delimiter = "--" #TLV sub string delimiter

#Session types
#=============
PREGAME_type   = 1 #this is not a game but the validation stage
G4INROW_type   = 2

#for players (not server)
tx_queue=queue.Queue(4) #used only by the player
my_role = "" #A client can have role of "A" or "B" (for server="S" but actually not used).
gameover=False
turn_is = "A"

#for server only
server_tx_queues= [queue.Queue(10) for i in range(max_clients)] #List of queues at server, one per each client

