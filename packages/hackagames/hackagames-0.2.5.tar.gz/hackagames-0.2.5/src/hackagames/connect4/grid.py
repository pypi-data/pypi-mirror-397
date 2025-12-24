"""
HackaGame - Connect4 - Grid 
"""
import sys

sys.path.insert( 1, __file__.split('hackagames')[0] )
import hacka as hk

playerSymbols= [" ", "O", "X"]

class Grid() :

    # Initialization:
    def __init__(self, nbColumn=7, height=6 ) :
        self._max= height
        self._pos= [ [ 0 for i in range(self._max) ] for j in range(nbColumn) ]
    
    # Accessors:
    def columnSize(self) :
        return len( self._pos )
    
    def heightMax(self) :
        return self._max
    
    def column(self, iColumn) :
        return self._pos[iColumn]
    
    def position(self, c, h) :
        return self._pos[c][h]
    
    def height(self, iColumn) :
        h= 0
        while( h < self.heightMax() and self.position( iColumn, h ) != 0 ) :
            h+= 1
        return h
    
    def playerPlay(self, iPlayer, letter) :
        iColumn= ord(letter)-ord('A')
        h= self.height( iColumn )
        if h < self.heightMax() :
            self._pos[iColumn][h]= iPlayer
            return True
        return False
    
    # PodInterface:
    def asPod(self):
        pod= hk.Pod().initialize("Connect4")
        for i in range( self.columnSize() ) :
            pod.append( hk.Pod().initialize( f"column-{chr(ord('A')+i)}", self._pos[i]) )
        return pod
    
    def initializeFrom(self, pod):
        self._max= len( pod.child(1).integers() )
        self._pos= []
        for kid in pod.children() :
            self._pos.append( [ kid.integer(i) for i in range(1, self._max+1) ] )
        return self

    def copy(self):
        return Grid().initializeFrom( self.asPod() )

    # Tools:
    def verticals(self):
        columnSize= self.columnSize()
        heightMax= self.heightMax()
        coords= []
        for i in range( columnSize ) :
            coords.append( [ (i, h) for h in range(heightMax) ] )
        return coords
    
    def horizontals(self):
        columnSize= self.columnSize()
        heightMax= self.heightMax()
        coords= []
        for h in range( heightMax ) :
            coords.append( [ (i, h) for i in range(columnSize) ] )
        return coords
        
    def diagonals(self):
        coords= []
        for i, h in self.diagonalPosStarts() :
            coords.append( self.diagonalFrom(i, h) )
        for i, h in self.diagonalNegStarts() :
            coords.append( self.diagonalFrom(i, h, -1) )
        return coords
    
    def diagonalPosStarts(self):
        columnSize= self.columnSize()
        heightMax= self.heightMax()
        coords= []
        for h in range( heightMax-3 ) :
            coords.append( (0, h) )
        for i in range( 1, columnSize-3 ) :
            coords.append( (i, 0) )
        return coords
    
    def diagonalNegStarts(self):
        columnSize= self.columnSize()
        heightMax= self.heightMax()
        coords= []
        for h in range( heightMax-3, heightMax ) :
            coords.append( (0, h) )
        for i in range( 1, columnSize-3 ) :
            coords.append( (i, heightMax-1) )
        return coords
    
    def diagonalFrom(self, i, h, sign= +1):
        columnSize= self.columnSize()
        heightMax= self.heightMax()
        coords= []
        while 0 <= i and i < columnSize and 0 <= h and h < heightMax : 
            coords.append( (i, h) )
            i+= 1
            h+= sign
        return coords
    
    def winner(self) :
        # test list of coords:
        for coords in self.verticals() + self.horizontals() + self.diagonals() :
            player= 0
            lengh= 1
            for i, h in coords :
                # increment lengh counter:
                p= self._pos[i][h]
                if p != 0 and player == self._pos[i][h] :
                    lengh+= 1
                else :
                    player= self._pos[i][h]
                    lengh= 1
                # Breack:
                if lengh == 4 :
                    return player
        return 0
    
    def possibilities(self) :
        listMove= []
        a= ord('A')
        for i in range( self.columnSize() ) :
            if self.height( i ) < self.heightMax() :
                listMove.append( chr(a+i) )
        return listMove

    def countTriple(self, iPlayer):
        nbColumns= self.columnSize()
        nbLines= self.heightMax()
        count= 0
        # Columns :
        for il in range(1, nbLines-1) :
            for ic in range(nbColumns) :
                if ( self.position(ic, il) == iPlayer
                     and self.position(ic, il-1) == iPlayer
                     and self.position(ic, il+1) == iPlayer ) :
                    count+= 1
        # Lines :
        for ic in range(1, nbColumns-1) :
            for il in range(nbLines) :
                if ( self.position(ic, il) == iPlayer
                     and self.position(ic-1, il) == iPlayer
                     and self.position(ic+1, il) == iPlayer ) :
                    count+= 1
        # Diaginals :
        for ic in range(1, nbColumns-1) :
            for il in range(1, nbLines-1) :
                if self.position(ic, il) == iPlayer :
                     if self.position(ic-1, il-1) == iPlayer and self.position(ic+1, il+1) == iPlayer :
                        count+= 1
                     if self.position(ic+1, il-1) == iPlayer and self.position(ic-1, il+1) == iPlayer :
                        count+= 1
        return count

    # String:
    def columnStr(self, iLine) :
        line= [ playerSymbols[ self._pos[i][iLine]  ] for i in range( self.columnSize() ) ]
        return "| " + " | ".join( line ) + " |"
    
    def __str__(self) :
        letters= []
        for i in range(self.columnSize()) :
            if self.height(i) < self.heightMax() :
                letters.append( chr( ord('A')+i ) )
            else :
                letters.append(" ")
        s= "  "+ "   ".join( letters ) +"\n"
        iLine= self.heightMax()-1
        while iLine >= 0 :
            s+= self.columnStr( iLine ) +"\n"
            iLine+= -1

        s+= "--" + "---".join( [ "-" for i in range( self.columnSize() ) ] ) + "--"
        return s