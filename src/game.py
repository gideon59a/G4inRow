'''
Created on May 9, 2015

@author: Gideon
'''
import sys
#xx from G4InRow.Server_2 import clients_list
sys.path.append('../') #this has been added so can be found in cmd window

####xx from G4InRow.Server_2 import game_instance

if __name__ == '__main__':
    pass

'''
Created on May 8, 2015 @author: Gideon
The message (what each entity sends):
 Player A             Player B              Server
 ========             ========              ======
 connect
 (O)my_info
                                        to A your_role=A (to B your_role=B)
                                        (O)to A game_status=W (wait for opponent)
                     connect
                     (O)my_info
                                        (O)to A&B game_status=S (started)
                                        (O)to A&B game_info=players (names,...)
                                        to A&B play_command=A to play (so game starts)
 my_move (okay)
                                        to A&B game_board
                                        to A&B play_command=B to play
 my_move with error
                                        send message to A
                                        to A&B play_command=A to play
 my_move (ends game)
                                        to A&B play_command=A is the winner (game over)


TLV Type,        len,   Value1 and          Value2:
===================================================
from server:
-----------
your_role,       len,   A or B,             null
(O)game_status,  len,   W (wait)            null
(O)game_status,  len,   S (started),        null
game_status,     len,   Z (game over),      A or B or T (tie) or E (error)
play_command,    len,   A (meaning A play), null
play_command,    len,   B (meaning B play), null
game_board,      len,   last move details,  board string
text_message,    len,   text line,          text line : Note: text must not include "," ! because is a delimiter...

form player:
-----------
my_info,        len,   null,                 name
my_move,        len,   A or B,               column

'''

import re
import queue
from src import boardClass
#from FourInRowGame.boardClass import Board
import src.globals as gls
#from FourInRowGame.gls import turn_is as turn_is
####from G4InRow.Server_2 import clients

######################################################################################################################
#enumerations
my_info     =0 #info the client sends to the server
my_move     =1
play_command=2
game_board  =3
players_info=4
your_role   =5
game_status =6
text_message=7
tlv_value_fieldLen={my_info:10,my_move:2,play_command:2,game_board:56,players_info:20,your_role:2,game_status:6,text_message:100} #TLV value len per type

debug_level=gls.debug_level

class tlv:
    """
    The tlv has 4 fields: type, len (of values), value 1 and value2
    """
    #global my_info, play_command, my_move, game_board, end_command
    #(my_info, play_command, my_move, game_board, end_command) = (range(5)) #TLV types enumeration

    #print ("tlv class:",myinfo, tlv_value_fieldLen[my_info]) #debug
    def __init__(self, tlv_type=0, tlv_value1="",tlv_value2=""):
        self.tlv_type   = tlv_type # An integer for enumeration
        #if tlv_len==0:
        #    self.tlv_len=self.tlv_value_fieldLen[self.tlv_type] # An integer for enumeration
        #else: #if len is received when tlv is created
        #    self.tlv_len=tlv_len
        self.tlv_len    = tlv_value_fieldLen[self.tlv_type]
        self.tlv_value1 = tlv_value1 #string
        self.tlv_value2 = tlv_value2 #string

    def print_tlv(self):
        if debug_level>1: print ("Type=",self.tlv_type,"Len=",self.tlv_len,"Val1=",self.tlv_value1,"val2=",self.tlv_value2)

    def tlv2str(self):
        #strset=str(type)+","+str(self.tlv_value_fieldLen[type])+","+str(value1)+","+str(value2)
        strset = str(self.tlv_type)+","+str(self.tlv_len)+","+str(self.tlv_value1)+","+str(self.tlv_value2)
        strset = gls.SOM + strset + gls.EOM #encapsulate message string with SOM and EOM
        return strset

    def str2tlv (self,istr):
        rxtlv_list = re.split(',',istr) #convert the received string to a list (of characters)
        if debug_level>0: print ("rxtlv_list",rxtlv_list)
        self.tlv_type = int(rxtlv_list[0])
        self.tlv_len =  int(rxtlv_list[1])
        self.tlv_value1 =   rxtlv_list[2]
        self.tlv_value2 =   rxtlv_list[3]


##### GAME INIT ########!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def palyer_game_init():
    global my_board
    my_board    = boardClass.Board()
    server_board= boardClass.Board()
    gls.turn_is = "A" #"A" is the first to play

def player_index (turn_char):
    if turn_char=="A":  return 0
    else:               return 1


def play_player (rxstr):

    rxtlv=tlv()
    rxtlv.str2tlv(rxstr)

    #### Client processing ########
    #=============================#
    if  rxtlv.tlv_type == your_role:
        gls.my_role = rxtlv.tlv_value1 #update my role
        print ("I'm player",gls.my_role)
        if gls.my_role=="A": print ("Waiting for player B to connect")
    elif rxtlv.tlv_type == play_command:  #At client: your turn to play (tlv_vlaue are ignored)
        #get input from user if it is my turn:
        if rxtlv.tlv_value1 == gls.my_role :
            while True:#loop until the user enters a valid value
                try:
                    print ("Player",rxtlv.tlv_value1,"please select column: ",end="")
                    colmove = int(input()) # the col number (1 to n)
                    break
                except ValueError:
                    print ("Oops!  column number must be an integer.")
            #Build the TLV to send
            txtlv=tlv(my_move,rxtlv.tlv_value1,colmove)
            txstr=txtlv.tlv2str()
            #put into queue:
            if debug_level>1: print (txstr,"put in tx queue")
            gls.tx_queue.put_nowait(txstr)
        else:
            print ("Opponent's turn.")
    elif rxtlv.tlv_type == game_board: #At client: Got the board from the server
        my_board.str2matrix(rxtlv.tlv_value2) #convert rxtlv_value2 to board per the board string in value2

        #print last move
        last_move_list = re.split (gls.sub_delimiter,rxtlv.tlv_value1)
        print ("last_move_list",last_move_list) #qqq
        print ("Last move: Player",last_move_list[0],": Row",last_move_list[1],"Col",last_move_list[2])
        my_board.print_board() #debug

    elif rxtlv.tlv_type == game_status:
        if rxtlv.tlv_value1 == "Z" : #gameover
            if rxtlv.tlv_value2 == "T": print ("gameover, Tie ")
            if rxtlv.tlv_value2 == "A" or "B": print ("gameover, Winner is",rxtlv.tlv_value2 )
            if rxtlv.tlv_value2 == "E": print ("gameover, ERROR")
            gls.gameover=True

    elif rxtlv.tlv_type == text_message:
        print (rxtlv.tlv_value1)
        print (rxtlv.tlv_value2)

    elif gls.my_role != "S" : #error
        print ("BUG")

def put_server_str_to_queues (s_txtlv,clients_list):

    s_txstr=[s_txtlv[0].tlv2str()    ,s_txtlv[1].tlv2str()] #the two strings to send to the two players
    gls.server_tx_queues[clients_list[0]].put_nowait(s_txstr[0]) # A's tx queue
    gls.server_tx_queues[clients_list[1]].put_nowait(s_txstr[1]) # A's tx queue
    ##if gls.debug_level>2: print ("tx queue:", gls.server_tx_queues[clients_list[1]])


def server_game_start(game_i):
    #send to the players their role
    s_txtlv=[tlv(your_role,"A","") , tlv(your_role,"B","")] #set the tlv command to send to the two players
    #qqq room_index=game_i.room_number
    clients_list =  game_i.get_players_list() #the clients indices
    put_server_str_to_queues (s_txtlv,clients_list)

    #send to the players the play command
    s_txtlv=[tlv(play_command,game_i.turn_is,"") , tlv(play_command,game_i.turn_is,"")] #set the tlv command to send to the two players
    put_server_str_to_queues (s_txtlv,clients_list)

def play_server (game_i, rxstr):

    #qqqroom_index=game_i.room_number
    clients_list =  game_i.get_players_list() #the clients indices

    #### Server processing ########
    #=============================#
    rxtlv=tlv()
    rxtlv.str2tlv(rxstr)

    if rxtlv.tlv_type == my_move: #At server. Check the move the client sent and update the board.

        #1.Perform next move
        result = game_i.board.new_move(int(rxtlv.tlv_value2)-1) #-1 because user counts from 1
        #there are four codes that can return:
        # 0 : move has been processed okay
        # 1 : game ended (winner or tie)
        #minus for errors

        if result >= 0: ##move was okay, update board (also if game ended)
            #Send updated board
            test_str=game_i.board.get_last_move_details()
            print (">>>>>>>>>> test_str")
            s_txtlv=[tlv(game_board,game_i.board.get_last_move_details(),game_i.board.matrix2str()) ,
                     tlv(game_board,game_i.board.get_last_move_details(),game_i.board.matrix2str())]
            put_server_str_to_queues (s_txtlv,clients_list)
            game_i.board.print_board() #print also in the server

        if result==0: #move was okay and processed, not end of game
            game_i.swap_turn() #Swap players turn between A and B

            #send to the players the play command. This is true also in input error
            #set the tlv command to send to the two players and add to tx queues
            s_txtlv=[tlv(play_command,game_i.turn_is,"") , tlv(play_command,game_i.turn_is,"")]
            print ("***clinets list:",clients_list)
            put_server_str_to_queues (s_txtlv,clients_list)

        elif result==1: #game ended
            print ("the winner is", game_i.board.winner)
            game_i.gameover=True #end of game
            #a. send the end message
            s_txtlv=[tlv(game_status,"Z",game_i.board.winner) , tlv(game_status,"Z",game_i.board.winner)] #set the tlv command to send to the two players
            put_server_str_to_queues (s_txtlv,clients_list)


        elif result <0: #error in move
            if result==-1:
                result_str_error = "Illegal move: Column range is between 1 and "+ str(game_i.board.num_cols)
                if debug_level>0: print (result_str_error)
                #print ("Illegal move: Column range is between 1 and",server_board.num_cols)
            elif result==-2:
                result_str_error = "Illegal move: A full column. Select another column"
                if debug_level>0: print (result_str_error)
                #print ("Illegal move: full column. Select another column")
        else: print ("BUG")

        if result < 0: #send error message just to the current player
            player_index_in_game=player_index(game_i.turn_is)#the 0..1 index of the player
            #client_index = game_i.get_client_index(player_index_in_game)
            cl_index=clients_list[player_index_in_game]

            #send the error message
            tlv_to_send = tlv (text_message,"",result_str_error)
            str_to_send = tlv_to_send.tlv2str()
            gls.server_tx_queues[cl_index].put_nowait(str_to_send) # A's tx queue

            #send the play command message
            tlv_to_send = tlv (play_command,game_i.turn_is,"")
            str_to_send = tlv_to_send.tlv2str()
            gls.server_tx_queues[cl_index].put_nowait(str_to_send) # A's tx queue

    else: print ("???? no such message from client is coded in the server")

