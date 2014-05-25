#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Generic Puzzle Solving Framework

Based on: version 9, (27-Mar-2002) of Raymond Hettinger's short library'
http://users.rcn.com/python/download/python.htm

Modified by Freek Dijkstra for Python 3.

License:  Public Domain
"""

""" Simple Instructions:

Create your puzzle as a subclass of Puzzle().
The first step is to choose a representation of the problem
state preferably stored as a string.  Set 'pos' to the starting
position and 'goal' to the ending position.  Create a genmoves()
method that computes all possible new puzzle states reachable from
the current state.  Call the .solve() method to solve the puzzle.

Important Note:

The __iter__() method must return a list of puzzle instances, not
their representations.  It should be written as a generator, returning
its results through yield.

Advanced Instructions:

1. .solve(pop_pos=DEPTH_FIRST) will override the default breadth first search.
Use depth first when the puzzle known to be solved in a fixed number
of moves (for example, the eight queens problem is solved only when
the eighth queen is placed on the board; also, the triangle tee problem
removes one tee on each move until all tees are removed).  Breadth first
is ideal when the shortest path solution needs to be found or when
some paths have a potential to wander around infinitely (i.e. you can
randomly twist a Rubik's cube all day and never come near a solution).

2. Define __str__ for a pretty printed version of the current position.
The state for the Tee puzzle looks best when the full triangle is drawn.

3. If the goal state can't be defined as a string, override the isgoal()
method.  For instance, the block puzzle is solved whenever block 1 is
in the lower left, it doesn't matter where the other pieces are; hence,
isgoal() is defined to check the lower left corner and return a boolean.

4. Some puzzle's can be simplified by treating symmetric positions as
equal.  Override the .canonical() method to pick one of the equilavent
positions as a representative.  This allows the solver to recognize paths
similar ones aleady explored.  In tic-tac-toe an upper left corner on
the first move is symmetrically equivalent to a move on the upper right;
hence there are only three possible first moves (a corner, a midde side,
or in the center).
"""

DEPTH_FIRST = -1
BREADTH_FIRST = 0

class NoSolution(Exception):
    """Raised if no solution can be found"""
    pass

class Puzzle:
    """The class represents a puzzle, and all instances represent a state of the puzzle."""
    pos = ""                    # default starting position
    goal = ""                   # ending position used by isgoal()
    def __init__(self, pos = None):
        if pos: self.pos = pos
    def __str__(self):          # returns a string representation of the position for printing the object
        return str(self.pos)
    def canonical(self):        # returns a string representation after adjusting for symmetry
        return str(self.pos)
    def isgoal(self):
        return self.pos == self.goal
    def __iter__(self):         # yields all possible next move, reachable from the current state
        raise StopIteration
    def solve(pos, pop_pos = BREADTH_FIRST):
        queue, solution = [], []
        trail = { pos.canonical(): None }
        while not pos.isgoal():
            for nextmove in pos:
                c = nextmove.canonical()
                if c in trail:
                    continue
                trail[c] = pos
                queue.append(nextmove)
            if len(queue) == 0:
                raise NoSolution() # unsolvable
            pos = queue.pop(pop_pos)
        while pos:
            solution.insert(0, pos)
            pos = trail[pos.canonical()]
        return solution

# Sample Puzzles start here

class JugFill3( Puzzle ):
    """
    Given a two empty jugs with 3 and 5 liter capacities and a full
    jug with 8 liters, find a sequence of pours leaving four liters
    in the two largest jugs
    """
    pos = (8,0,0)
    capacity = (8,3,5)
    goal = (4,0,4)
    def __iter__(self):
        for i in range(len(self.pos)):
            for j in range(len(self.pos)):
                if i==j: continue
                qty = min( self.pos[i], self.capacity[j] - self.pos[j] )
                if not qty: continue
                dup = list( self.pos )
                dup[i] -= qty
                dup[j] += qty
                yield self.__class__(tuple(dup))

class JugFill5( Puzzle ):
    """
    Given a four empty jugs with 3,6 11, and 14 liter capacities and a full
    jug with 16 liters, find a sequence of pours leaving four liters
    in the four largest jugs
    """
    pos = (0,0,0,0,16)
    capacity = (3,6,11,14,16)
    goal = (0,4,4,4,4)
    def __iter__(self):
        for i in range(len(self.pos)):
            for j in range(len(self.pos)):
                if i==j: continue
                qty = min( self.pos[i], self.capacity[j] - self.pos[j] )
                if not qty: continue
                dup = list( self.pos )
                dup[i] -= qty
                dup[j] += qty
                yield self.__class__(tuple(dup))

class EightQueens( Puzzle ):
    """
    Place 8 queens on chess board such that no two queens attack each other
    """
    pos = ()
    def isgoal(self):
        return len(self.pos) == 8
    def __str__(self):
        return ' '.join([p[1]+str(p[0]+1) for p in zip(self.pos,'ABCDEFGH')])
    def __iter__( self ):
        x = len(self.pos)
        for y in range(8):
            if y in self.pos: continue
            for xp,yp in enumerate(self.pos):
                if abs(x-xp) == abs(y-yp):
                    break
            else:
                yield self.__class__(self.pos + (y,))


class TriPuzzle( Puzzle ):
    """
    Triangle Tee Puzzle
    Tees are arranged in holes on a 5x5 equalateral triangle except for the
    top center which left open.  A move consist of a checker style jump of
    one tee over the next into an open hole and removed the jumped tee. Find
    a sequence of jumps leaving the last tee in the top center position.
    """
    pos = '011111111111111'
    goal = '100000000000000'
    triples = [[0,1,3], [1,3,6], [3,6,10], [2,4,7], [4,7,11], [5,8,12],
               [10,11,12], [11,12,13], [12,13,14], [6,7,8], [7,8,9], [3,4,5],
               [0,2,5], [2,5,9], [5,9,14], [1,4,8], [4,8,13], [3,7,12]]
    def __iter__( self ):
        for t in self.triples:
            if self.pos[t[0]]=='1' and self.pos[t[1]]=='1' and self.pos[t[2]]=='0':
                yield self.__class__(self.produce(t,'001'))
            if self.pos[t[0]]=='0' and self.pos[t[1]]=='1' and self.pos[t[2]]=='1':
                yield self.__class__(self.produce(t,'100'))
    def produce( self, t, sub ):
        return self.pos[:t[0]] + sub[0] + self.pos[t[0]+1:t[1]] + sub[1] + self.pos[t[1]+1:t[2]] + sub[2] + self.pos[t[2]+1:]
    def canonical( self ):
        return self.pos
    def __str__( self ):
        return '        %s\n      %s   %s\n    %s   %s   %s\n  %s   %s   %s   %s\n%s   %s   %s   %s   %s\n' % tuple(self.pos)

class MarblePuzzle( Puzzle ):
    """
    Black/White Marble
    Given eleven slots in a line with four white marbles in the leftmost
    slots and four black marbles in the rightmost, make moves to put the
    white ones on the right and the black on the left.  A valid move for
    a while marble is to shift right into an empty space or hop over a single
    adjacent black marble into an adjacent empty space -- don't hop over
    your own color, don't hop into an occupied space, don't hop over more
    than one marble.  The valid black moves are in the opposite direction.
    Alternate moves between black and white marbles.

    In the tuple representation below, zeros are open holes, ones are whites,
    negative ones are blacks, and the outer tuple tracks whether it is
    whites move or blacks.
    """
    pos = (1,(1,1,1,1,0,0,0,-1,-1,-1,-1))
    goal =  (-1,-1,-1,-1,0,0,0,1,1,1,1)
    def isgoal( self ):
        return self.pos[1] == self.goal
    def __iter__( self ):
        (m,b) = self.pos
        for i in range(len(b)):
            if b[i] != m: continue
            if 0<=i+m+m<len(b) and b[i+m] == 0:
                newmove = list(b)
                newmove[i] = 0
                newmove[i+m] = m
                yield self.__class__((-m,tuple(newmove)))
                continue
            if 0<=i+m+m<len(b) and b[i+m]==-m and b[i+m+m]==0:
                newmove = list(b)
                newmove[i] = 0
                newmove[i+m+m] = m
                yield self.__class__((-m,tuple(newmove)))
                continue
    def __str__( self ):
        s = ''
        for p in self.pos[1]:
            if p==1: s='b'+s
            elif p==0: s='.'+s
            else: s='w'+s
        return s

class RowboatPuzzle( Puzzle ):
    """
    Rowboat problem:  Man, Dog, Cat, Squirrel
    Cross the river two at a time, don't leave the dog alone with the
    cat or the cat alone with the squirrel.

    The bitmap representation shows who is on the opposite side.
    Bit 1 is the squirrel, bit 2 is the cat, bit 3 is the dog, bit 4 is the man.
    Genmoves takes the current position and flips any two bits which is the
    same as moving those two creatures to the opposite shore.  It then
    filters out any moves which leave the dog and cat together or the
    cat and squirrel.
    """
    pos = 0
    goal = 15
    def __iter__( self ):
        for m in [8,12,10,9]:
            n = self.pos ^ m
            if ((n>>1)&1 == (n>>3)&1) or ( (n>>2)&1 != (n>>1)&1 != (n&1) ):
                yield self.__class__(n)
    def __str__( self ):
        v = ','
        if self.pos&8: v=v+'M'
        else: v='M'+v
        if self.pos&4: v=v+'D'
        else: v='D'+v
        if self.pos&2: v=v+'C'
        else: v='C'+v
        if self.pos&1: v=v+'S'
        else: v='S'+v
        return v

import re
import string


def findall(pattern, string):
    pos = 0
    while True:
        pos = string.find(pattern, pos)
        if pos < 0:
            break
        yield pos
        pos += 1

class BlockSlidePuzzle( Puzzle ):
    """
    This sliding block puzzle has 9 blocks of varying sizes:
    one 2x2, four 1x2, two 2x1, and two 1x1.  The blocks are
    on a 5x4 grid with two empty 1x1 spaces.  Starting from
    the position shown, slide the blocks around until the
    2x2 is in the lower left:

        1122
        1133
        45
        6788
        6799
    """
    pos = '11221133450067886799'
    width  = 4
    height = 5
    blank  = '0'
    goal = re.compile( r'................1...' )
    def isgoal(self):
        return self.goal.search(self.pos) != None
    def __str__( self ):
        pos = self.pos.replace( '0', '.' )
        ans = ''
        for i in range(0,self.width*self.height,self.width):
            ans = ans + pos[i:i+self.width] + '\n'
        return ans
    xlat = str.maketrans('38975','22264')
    def canonical( self ):
        return self.pos.translate( self.xlat )
    def __iter__( self ):
        size = self.width*self.height
        for dest in findall(self.blank, self.pos):
            for adj in [-self.width,-1,1,self.width]:
                row,col = divmod(dest, self.width)
                # skip blanks at the edges:
                if dest+adj < 0 or dest+adj >= size: continue
                if (col == 0 and adj == -1) or (col == self.width-1 and adj == 1): continue
                piece = self.pos[dest+adj]
                if piece == self.blank: continue
                # copy self.pos, remove the current block
                newmove = self.pos.replace(piece, self.blank)
                # insert the block at the new place
                for i in range(max(0,-adj),min(size,size-adj)):
                    if self.pos[i+adj]==piece:
                        newmove = newmove[:i] + piece + newmove[i+1:]
                # make sure there was no overlap of the new block
                if newmove.count(self.blank) != self.pos.count(self.blank): continue
                yield self.__class__(newmove)



class HVBlockSlidePuzzle( Puzzle ):
    """
    This sliding block puzzle has blocks of size 1x2 or 1x3.
    Horizontally orientated blocks can only move horizontally.
    Vertically orientated blocks can only move vertically.

        1112  
        3  245
        3 0045
        667 45
        897AA 
        89BBCC
    """
    pos =   '1112  '\
            '34 256'\
            '340056'\
            '778 56'\
            '9 8AA '\
            '9BBB  '
    width  = 6
    height = 6
    blank  = ' '
    def isgoal(self):
        row = 2
        return self.pos[(row+1)*self.width-2:(row+1)*self.width] == '00'
    def __str__( self ):
        return '\n'.join([self.pos[i:i+self.width] for i in range(0,self.width*self.height,self.width)])+'\n'
    def __iter__( self ):
        size = self.width*self.height
        for dest in findall(self.blank, self.pos):
            for adj in [-self.width,-1,1,self.width]:
                row,col = divmod(dest, self.width)
                # skip blanks at the edges:
                if dest+2*adj < 0 or dest+2*adj >= size: continue
                if (col < 2 and adj == -1) or (col >= self.width-2 and adj == 1): continue
                piece = self.pos[dest+adj]
                if self.pos[dest+2*adj] != piece: continue
                if piece == self.blank: continue
                # copy self.pos, remove the current block
                newmove = self.pos.replace(piece, self.blank)
                # insert the block at the new place
                for i in range(max(0,-adj),min(size,size-adj)):
                    if self.pos[i+adj]==piece:
                        newmove = newmove[:i] + piece + newmove[i+1:]
                # make sure there was no overlap of the new block
                if newmove.count(self.blank) != self.pos.count(self.blank): continue
                yield self.__class__(newmove)


def Show(cls, search_method = BREADTH_FIRST):
    import time
    print(cls.__name__, cls.__doc__)
    t = time.time()
    solution = cls().solve(search_method)
    for s in solution:
        print(s)
    d = time.time() - t
    print("Duration: %d ms" % (d*1000))
    print()

if __name__ == '__main__':
    Show(JugFill3)
    Show(JugFill5)
    Show(EightQueens, DEPTH_FIRST)
    Show(TriPuzzle)
    Show(MarblePuzzle, DEPTH_FIRST)
    Show(RowboatPuzzle)
    Show(BlockSlidePuzzle)
    Show(HVBlockSlidePuzzle)
    
