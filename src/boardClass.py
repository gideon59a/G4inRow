''' G4inRow
Created on Apr 12, 2015
Contains the 4 in a row board class, plus its basic testing when run as main.
@author: Gideon
'''
import sys
sys.path.append('../') #this has been added so can be found in cmd window

import src.globals as gls  #(old:) import G4inRow.globals as gls

#create a class that is the board State
class Board:
    '''
    The board class contians the board content plus the game status.
    A board matrix cell can be filled with "A" or "B" or null ("-"), while A and B are the players.
    '''
    num_rows = 8
    num_cols = 7

    def __init__(self):
        '''
        Constructor: Fill the board and init game status
        '''

        self.player = "A" #init the first player
        self.winner = "" #equals to A, B, Tie, or null

        self.nextrow = [0 for i in range (self.num_cols)] #init the next row available for each col

        #the following is used just for user info sent back to the players
        self.last_player = " " #init.
        self.last_move_row = 0 #init. This is the row of the last move in range 1..number of rows
        self.last_move_col = 0 #init. This is the col of the last move in range 1..number of cols

        # Creates a board matrix with empty cells.
        # The board is a matrix of lines and columns, each cell is a single character
        # The characters used are A,B, and "-" for empty cell
        self.matrix = [["-" for x in range(self.num_cols)] for x in range(self.num_rows)]
        print ("board initialized")

        #for i in range (4)
        #    teststr

    def tst_print_matrix(self):
        print (self.matrix)

    def print_board (self):
        #print (self.matrix)
        #print (self.num_rows)
        #print self.matrix[i][j]
        print("******* printing board ********")
        for i in range (self.num_rows):
            for j in range (self.num_cols):
                print (self.matrix[self.num_rows-1-i][j], end="") #the end= is to avoid CRs
            print ("")
        return ()
    #print (self.num_rows) ### NOT WORKING

    def new_move (self, locat_col):
        #get just the column of the new move
        #the implied row = self.nextrow[locat_col]

        #check if not error move
        if locat_col>(self.num_cols-1) or (locat_col<0):
            #print ("Illegal move: No such column")
            return -1
        if self.nextrow[locat_col] == self.num_rows:
            #print ("Illegal move: Column is full")
            return -2

        #update the board per the player's move
        self.matrix[self.nextrow[locat_col]][locat_col] = self.player

        #to send the info to the players
        self.last_player = self.player
        self.last_move_col = locat_col
        self.last_move_row=self.nextrow[locat_col]

        #validate move (check if game status is changed)
        val_result = self.validate_move(locat_col)
        #print ("val_result",val_result)

        #prepare for next move
        self.nextrow[locat_col] += 1 #the next row to put in (if col is not full)
        if self.player=="A":  #select next player
            self.player = "B"
        else: self.player = "A"

        return val_result #continue or end game per the result

    def validate_move (self,locat_col):
        #check if the last move wins the game, i.e. if there is a 4-in-a-line state

        #There are 4 options to win. Prepare 4 strings for it.
        #The strings are:
        #teststr[0] for 4 in a row
        #teststr[1] for 4 in a column
        #teststr[2] for 4 i a diagonal that goes up to the right (45 degrees)
        #teststr[3] for 4 i a diagonal that goes up to the left (135 degrees)

        locat_row=self.nextrow[locat_col] #(shortcut) Row number of the last move

        #step 1: Prepare strings for the 4 options to win and check them
        teststr= ["","","",""]

        # The row string
        teststr[0] = "".join(self.matrix[locat_row]) #the row string
        print ("teststr[0]: ",teststr[0]) #for debug

        # The column string
        for i in range (self.num_rows):
            teststr[1] += self.matrix[i][locat_col]
            #print ("teststr[1]: ",teststr[1]) #for debug

        #The diagonal from down to right
        # calc the span of the diagonal
        getdown = min(locat_row, locat_col)
        row2start=locat_row - getdown #the row to start from
        getup = min (self.num_cols -1 -locat_col, self.num_cols -1 -locat_row )
        #xx row2start = locat_row - getdown
        row2end = locat_row + getup
        col2start = locat_col - (locat_row - row2start)
        #self.print_board()
        #print ("played by ",self.player,)
        #print ("locat_row2, locat_col2:", locat_row, locat_col)
        #print ("getdown2: ",getdown, "getup: ", getup)
        #print ("row2start2: ",row2start, "row2end3: ", row2end, "col2start: ",col2start )

        #create the string for the diagonal to the left
        teststr[2] = "" #init the diagonal
        irow = row2start #the first row of the string
        icol = col2start
        while irow <= row2end:
            teststr[2] += self.matrix[irow][icol]
            irow += 1
            icol += 1
        #print ("teststr[2]: ",teststr[2])



        #The diagonal from down to left
        # calc the span of the diagonal
        getdown = min(locat_row, (self.num_cols -1 - locat_col))
        row2start=locat_row - getdown #the row to start from
        getup = min (self.num_rows -1 -locat_row, locat_col)
        row2start = locat_row - getdown
        row2end = locat_row + getup
        col2start = locat_col + (locat_row - row2start)
        #self.print_board()
        #print ("played by ",self.player,)
        #print ("locat_row3, locat_col3:", locat_row, locat_col)
        #print ("getdown3: ",getdown, "getup: ", getup)
        #print ("row2start3: ",row2start, "row2end3: ", row2end)

        #create the string for the diagonal to the left
        teststr[3] = "" #init the diagonal
        irow = row2start #the first row of the string
        icol = col2start
        while irow <= row2end:
            teststr[3] += self.matrix[irow][icol]
            irow += 1
            icol -= 1
        #print ("teststr[3]: ",teststr[3])

        #check if the is a winner in one of the 4 strings
        awins = "AAAA"
        bwins = "BBBB"
        for i in range(4):
            if (teststr[i].find(awins) != -1):
                #print("A is the winner")
                self.winner = "A"
                return 1 #with a winner
            if (teststr[i].find(bwins) != -1):
                #print("B is the winner")
                self.winner = "B"
                return 1 #with a winner

        #If we arrive here it means there is no winner, yet the game may be over:
        #If the highest row is full and there is no winner then it is a Tie
        rstring = "".join(self.matrix[7])
        #print (rstring)
        #a=rstring.find("-")
        #print (a)
        if rstring.find("-") == -1 : #highest row doesn't contain any empty place
            #print ("Game over - Tie")
            self.winner = "Tie"
            return 1 #end of game

        return 0 #no winner or end of game

    def matrix2str (self):
        ''' Convert the board matrix to string.
        '''
        boardstr=""
        for i in range(self.num_rows):
            boardstr += "".join([self.matrix[i][j] for j in range(self.num_cols)])
            #print ("boardstr",boardstr)
        return boardstr

    def str2matrix (self,instr):
        ''' Converts / set the board matrix per the input string named instr
        '''
        for i in range(self.num_rows):
            self.matrix[i] = list(instr[i*self.num_cols:(i*self.num_cols+7)])

    def get_last_move_details (self): #used by server to read the details to be sent to players
        last_move_str = self.last_player + gls.sub_delimiter  + str(self.last_move_row+1) +  gls.sub_delimiter  + str(self.last_move_col+1)
        return last_move_str

if __name__ == '__main__':
    print ("Testing boardClass:")
    board1 = Board()
    move=board1.new_move(4)
    print (move)
    board1.new_move(5)
    board1.new_move(4)
    move=board1.new_move(77)
    print (move)
    board1.print_board()
    board1.tst_print_matrix()

