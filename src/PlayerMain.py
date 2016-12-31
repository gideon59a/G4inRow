'''
Created on May 9, 2015

@author: Gideon
'''

import socket
import sys
import queue
sys.path.append('../') #this has been added so can be found in cmd window

TCP_PORT=50002

from src.globals import gameover
import src.globals as gls
import src.game as game
import src.connect_tcp as connect_tcp


debug_level=gls.debug_level #0 for no debug, 1 for basic debug, 2 for details


def connect2sever (server_ip_address,destination_port):
    iserver_address = (server_ip_address, destination_port)
    # Create a TCP/IP socket
    isock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    print ('connecting to %s port %s' % iserver_address)
    try:
        isock.connect(iserver_address)
    except:
        print ("error connecting to the server.")
        return -1
    else:
        print ("connected to server: ", isock)
        return isock


##############################
# Real start of execution    #
##############################

#Prepare TCP listener
server_ip_address = 'localhost' #a program argument
destination_port = TCP_PORT
sock=connect2sever(server_ip_address,destination_port) #connection ready
data_stream = str()
rx_queue = queue.Queue(10)

### INIT:
#========
game.palyer_game_init()

#######################################
#       MAIN LOOP                     #
#######################################
# loop while not end of game:
#    transmit_to_server if any
#    receive_from_server()
#    check for error
#    process the received


while gls.gameover==False: #game not over

    #1. Send all messages in tx queue as long as queue is not empty
    while not gls.tx_queue.empty():
        txstr=gls.tx_queue.get_nowait()
        if debug_level>1: print ('%s: sending "%s"' % (sock.getsockname(),  txstr))
        sock.send(str.encode(txstr)) #the message must be byte encoded, utf8 is the default
        print ("message sent.")

    #2. Receive a single message - ***BLOCKING!***
    try:
        data = sock.recv(1024)
    except socket.error:
        print ("error in socket, should be closed")
        data=""
        #NOTE: Data is not read. socket will be closed later by the next if
    if debug_level>1: print ('%s: received "%s"' % (sock.getsockname(), data))

    if not data: #Server closed or error in socket
        print ('closing socket', sock.getsockname())
        sock.close()
        gls.gameover=True

    else:   #3. Process the received string
        #no queue is needed because each message is processed.
        rxstr=data.decode("utf-8")
        data_stream, rx_queue = connect_tcp.extract_message(rxstr, data_stream, rx_queue)
        while not rx_queue.empty():
            rx_message=rx_queue.get_nowait()
            game.play_player(rx_message) #PROCESS THE MESSAGE

        #def wait_for_kbd ():
        #    a=input ("enter something to continue")
        #if debug_level>1:
        #    print ("gameover=",gls.gameover,"wait...")
        #wait_for_kbd()
print ("end.")

