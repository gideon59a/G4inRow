'''
Created on May 17, 2015

@author: Gideon
'''

import queue
import src.globals as gls
import src.game as game


def extract_message(rx_str_from_client, data_stream, rx_queue):
    """ get the data and extract the message from it.
        inputs:
            rx_str_from_client - the last received data (in string format)
            data_stream - the aggregated stream (in string format)
            s_index - the index of the user

        Returns the updated rx queue which includes the received message(s)
        as well as the updated data stream =
        = previous data stream PLUS new data MINUS the extracted packet.

        The queue contains the received str without the SOM,EOM delimiters.
        The data stream may contain more than one message.
        The message length is not checked here, because parsing is not part of this function

        Note: I didn't manage to pass the queue to the function, so I use the globals...
    """
    if gls.debug_level>0: print ("extract:",rx_str_from_client, data_stream, rx_queue)
    data_stream += rx_str_from_client #add the received chunk

    search=True
    while search==True:
        position_debug=data_stream.find (gls.SOM)
        if gls.debug_level>1: print ("position_debug=",position_debug)
        if data_stream.find (gls.SOM) > 0: #if found not at start of data it implies error in data
            data_stream="" #clear data, hoping it is some error rather than a bug
            # a better way could be cutting the data until the next SOM
            print ("Error in parsing received message:",data_stream)
            search=False
            #break
        elif data_stream.find (gls.SOM)==0: # SOM found at start of data, now look for EOM
            end_position=data_stream.find (gls.EOM)
            if gls.debug_level>1: print ("end_position=",end_position)
            if end_position != -1: #message found, starting with SOM and ending in SOM
                rx_message=data_stream[3:end_position]
                data_stream=data_stream[end_position+3:]
                if gls.debug_level>1: print ("packet=",rx_message," Remaining data",data_stream)
                if data_stream:
                    print ("two messages merged. The remaining chunk=",data_stream)
                #game.server_rx_queues[s_index].put_nowait(rx_message)
                rx_queue.put_nowait(rx_message)

            else: #no message found
                search=False
        else: #simply not found
            search=False #stop searching

    return data_stream,rx_queue

#def stam (input_queue):
#    a=input_queue.put_nowait("a")
#    #a=queue.Queue(10)
#    #a.put_nowait("a")
#    return a


if __name__ == '__main__':
    pass
