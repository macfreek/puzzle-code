from itertools import chain
import sys
import re
import time


class Pentas():
    """There are 12 possible figures ("pentagrams") consisting of 5 adjacent boxes in a grid. This class lists these 12, including rotations and mirrors."""
    def __init__(self, width):
        # NOTE: for efficiency, the regular expression is shared among all instances
        self.width = width
    pentas = [
        # each penta has multiple variants based on orientation (rotation / mirror)
        # each variant consists of multiple lines
        (
            (
                '0000000',
                '0111110',
                '0000000'
            ),(
                '000',
                '010',
                '010',
                '010',
                '010',
                '010',
                '000'
            ),
        ),(
            (
                '000',
                '010000',
                '011110',
                '000000'
            ),(
                '...000',
                '000010',
                '011110',
                '000000'
            ),(
                '000000',
                '011110',
                '010000',
                '000'
            ),(
                '000000',
                '011110',
                '000010',
                '...000'
            ),(
                '0000',
                '0110',
                '0100',
                '010',
                '010',
                '000'
            ),(
                '0000',
                '0110',
                '0010',
                '.010',
                '.010',
                '.000'
            ),(
                '000',
                '010',
                '010',
                '0100',
                '0110',
                '0000'
            ),(
                '.000',
                '.010',
                '.010',
                '0010',
                '0110',
                '0000'
            ),
        ),(
            (
                '.000',
                '001000',
                '011110',
                '000000'
            ),(
                '..000',
                '000100',
                '011110',
                '000000'
            ),(
                '000000',
                '011110',
                '001000',
                '.000'
            ),(
                '000000',
                '011110',
                '000100',
                '..000'
            ),(
                '000',
                '0100',
                '0110',
                '0100',
                '010',
                '000'
            ),(
                '.000',
                '0010',
                '0110',
                '0010',
                '.010',
                '.000'
            ),(
                '000',
                '010',
                '0100',
                '0110',
                '0100',
                '000'
            ),(
                '.000',
                '.010',
                '0010',
                '0110',
                '0010',
                '.000'
            ),
        ),(
            (
                '0000',
                '011000',
                '001110',
                '.00000'
            ),(
                '..0000',
                '000110',
                '011100',
                '00000'
            ),(
                '.00000',
                '001110',
                '011000',
                '0000'
            ),(
                '00000',
                '011100',
                '000110',
                '..0000'
            ),(
                '.000',
                '0010',
                '0110',
                '0100',
                '010',
                '000'
            ),(
                '000',
                '0100',
                '0110',
                '0010',
                '.010',
                '.000'
            ),(
                '000',
                '010',
                '0100',
                '0110',
                '0010',
                '.000'
            ),(
                '.000',
                '.010',
                '0010',
                '0110',
                '0100',
                '000'
            ),
        ),(
            (
                '000',
                '0100',
                '01100',
                '00110',
                '.0000'
            ),(
                '..000',
                '.0010',
                '00110',
                '01100',
                '0000'
            ),(
                '.0000',
                '00110',
                '01100',
                '0100',
                '000'
            ),(
                '0000',
                '0110',
                '00110',
                '.0010',
                '..000'
            ),
        ),(
            (
                '000',
                '010',
                '01000',
                '01110',
                '00000'
            ),(
                '..000',
                '..010',
                '00010',
                '01110',
                '00000'
            ),(
                '00000',
                '01110',
                '01000',
                '010',
                '000'
            ),(
                '00000',
                '01110',
                '00010',
                '..010',
                '..000'
            ),
        ),(
            (
                '00000',
                '01110',
                '00100',
                '.010',
                '.000'
            ),(
                '.000',
                '.010',
                '00100',
                '01110',
                '00000'
            ),(
                '000',
                '01000',
                '01110',
                '01000',
                '000'
            ),(
                '..000',
                '00010',
                '01110',
                '00010',
                '..000'
            ),
        ),(
            (
                '.000',
                '00100',
                '01110',
                '00100',
                '.000'
            ),
        ),(
            (
                '.0000',
                '.0110',
                '00100',
                '0110',
                '0000'
            ),(
                '0000',
                '0110',
                '00100',
                '.0110',
                '.0000'
            ),(
                '..000',
                '00010',
                '01110',
                '01000',
                '000'
            ),(
                '000',
                '01000',
                '01110',
                '00010',
                '..000'
            ),
        ),(
            (
                '.0000',
                '00110',
                '01100',
                '0010',
                '.000'
            ),(
                '0000',
                '01100',
                '00110',
                '.010',
                '.000'
            ),(
                '.000',
                '0010',
                '01100',
                '00110',
                '.0000'
            ),(
                '.000',
                '00100',
                '00110',
                '01100',
                '0000'
            ),(
                '..000',
                '00010',
                '01110',
                '00100',
                '.000'
            ),(
                '000',
                '01000',
                '01110',
                '0010',
                '.000'
            ),(
                '.000',
                '0010',
                '01110',
                '01000',
                '000'
            ),(
                '.000',
                '00100',
                '01110',
                '00010',
                '..000'
            ),
        ),(
            (
                '0000',
                '0110',
                '0110',
                '0100',
                '000'
            ),(
                '0000',
                '0110',
                '0110',
                '0010',
                '.000'
            ),(
                '000',
                '0100',
                '0110',
                '0110',
                '0000'
            ),(
                '.000',
                '0010',
                '0110',
                '0110',
                '0000'
            ),(
                '.0000',
                '00110',
                '01110',
                '00000'
            ),(
                '0000',
                '01100',
                '01110',
                '00000'
            ),(
                '00000',
                '01110',
                '01100',
                '0000'
            ),(
                '00000',
                '01110',
                '00110',
                '.0000'
            )
        ),(
            (
                '0000',
                '0110',
                '0100',
                '0110',
                '0000'
            ),(
                '0000',
                '0110',
                '0010',
                '0110',
                '0000'
            ),(
                '00000',
                '01110',
                '01010',
                '00000'
            ),(
                '00000',
                '01010',
                '01110',
                '00000'
            )
        )
    ]

    def __init__(self, width):
        self.width = width
        self.penta_re = {}
        self.set_penta_regexps()
    def set_penta_regexps(self):
        """penta_re stores compiled regular expressions to find each penta variant in a grid.
        Assumes the grid is stored in a single string with each row appended to the next row."""
        print('init penta_re')
        for penta in chain.from_iterable(self.pentas):
            p_regexp = ''
            for l,line in enumerate(penta):
                p_regexp += r'('+line+r')'
                if l != len(penta)-1:
                    p_regexp += (self.width-len(line))*r'.'
            if p_regexp.count('1') != 5:
                print(p_regexp)
                print(penta)
                sys.exit()
            p_regexp = p_regexp.replace('0',r'[ ?]')
            p_regexp = p_regexp.replace('1',r'[xX?]')
            self.penta_re[penta] = re.compile(r'(?='+p_regexp+')')

#!/usr/bin/env python3
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
    strategy = BREADTH_FIRST
    def __init__(self, pos = None):
        if pos:
            self.pos = pos
    def __str__(self):          # returns a string representation of the position for printing the object
        return str(self.pos)
    def canonical(self):        # returns a string representation after adjusting for symmetry
        return str(self)
    def isgoal(self):
        return self.pos == self.goal
    def __iter__(self):         # yields all possible next move, reachable from the current state
        raise StopIteration
    def print_progress(self, itercount, queue):
        print('iter', itercount, 'queue len', len(queue))
    def solve(self):
        queue = []
        solution = []
        trail = { self.canonical(): None }
        state = self
        itercount = 0
        while not state.isgoal():
            itercount += 1
            for nextmove in state:
                c = nextmove.canonical()
                if c in trail:
                    continue
                trail[c] = state
                queue.append(nextmove)
            #print("queue length", len(queue))
            if len(state.pentas) < 5:
                print(state)
                #time.sleep(5)
                state.print_progress(itercount, queue)
            elif itercount % 1000 == 0:
                state.print_progress(itercount, queue)
            if len(queue) == 0:
                raise NoSolution() # unsolvable
            state = queue.pop(state.strategy)
        while state:
            solution.insert(0, state)
            state = trail[state.canonical()]
        return solution


class PentaPuzzle(Puzzle):
    """
    A penta puzzle is a grid which will be filled with 60 or 120 black boxes, each horizontally
    or vertically connected with 4 other boxes forming a figure ("pentagram") of 5 boxes. The rest
    of the grid remains empty.
    
    There are 12 possible figures ("pentagrams") consisting of 5 boxes in a grid. See Pentas class.
    
    Constraints:
    * Two pentagrams may not touch, also not diagonaly
    * The 120 boxes form 24 pentagrams. These 24 pentagrams form 2 sets of all possible pentagrams
    * The number of filled boxes in each row and each column is given.
    * For each pentagram, exactly two boxes are already given (prefilled).

    Symbols in the grid:
    ❔: unknown
    🟫: pre-filled box, not processed yet
    ⬛️: pre-filled box, part of a pentagram
    🔳: filled box
    ▫️: empty box
    ?: unknown
    x: pre-filled box, not processed yet
    X: filled box
     : empty box
     an empty border is added to the diagram to easy placing the required empty borders around pentas.
    """
    pos = '                    ' \
          ' x?????????x?????x? ' \
          ' ??x???x?XxX??x???? ' \
          ' ????????????????x? ' \
          ' x???x???????x????? ' \
          ' ??x?????????????x? ' \
          ' ???????xXx???????? ' \
          ' x?x??x??????x?x?x? ' \
          ' ?????????????????? ' \
          ' ??x???Xx??Xx?XXxxX ' \
          ' ??????????X??????? ' \
          ' ??x???x??xX??x???x ' \
          ' ????????????????x? ' \
          ' x?x??????????x???? ' \
          ' ?????x???????????? ' \
          ' ????????x??????x?? ' \
          ' x?????????xX?x???? ' \
          ' ???????x?????????x ' \
          ' x??x?x?????x?x???? ' \
          '                    '
    row_counts = [0,6,10,6,7,4,8,10,1,13,2,8,6,5,2,8,9,6,9,0]
    col_counts = [0,11,6,10,5,2,10,5,5,7,3,6,6,7,10,3,6,10,8,0]
    width  = 20
    height = 20
    size   = 20*20
    blank  = ' ' # '▫️'
    unknown = '?' # '❔'
    filled_single = 'X'
    filled_final = '#' # '🔳'
    prefilled = 'x' # '⬛️'
    #unprocessed = '🟫'
    #current_block = '🟥'
    strategy = DEPTH_FIRST
    penta_types = Pentas(width)
    pentas = list(range(12)) + list(range(12))
    def __init__(self, pos=None, pentas=None):
        if pos:
            self.pos = pos
        if pentas is not None:
            self.pentas = pentas
        self.treepos = []
    def __str__( self ):
        return '\n'.join(self.pos[l*self.width:(l+1)*self.width] for l in range(self.height))
    def isgoal(self):
        return len(self.pentas) == 0
    def check_rowcol_constraints(self, pos):
        # pos is a list and will be modified if constraints allow that
        for r in range(self.height):
            max_filled = self.row_counts[r]
            max_blank = self.width - max_filled
            rowcol = pos[r*self.width:(r+1)*self.width]
            unknown_count = rowcol.count(self.unknown)
            #if unknown_count == 0: continue
            blank_count = rowcol.count(self.blank)
            filled_count = len(rowcol) - blank_count - unknown_count
            if filled_count > max_filled: return False
            if blank_count > max_blank: return False
            if filled_count == max_filled:
                for i in range(r*self.width, (r+1)*self.width):
                    if pos[i] == self.unknown:
                        pos[i] = self.blank
            if blank_count == max_blank:
                for i in range(r*self.width, (r+1)*self.width):
                    if pos[i] == self.unknown:
                        pos[i] = self.filled_single
        for c in range(self.width):
            max_filled = self.col_counts[c]
            max_blank = self.height - max_filled
            rowcol = pos[c:-1:self.width]
            unknown_count = rowcol.count(self.unknown)
            #if unknown_count == 0: continue
            blank_count = rowcol.count(self.blank)
            filled_count = len(rowcol) - blank_count - unknown_count
            if filled_count > max_filled: return False
            if blank_count > max_blank: return False
            if filled_count == max_filled:
                for i in range(c, -1, self.width):
                    if pos[i] == self.unknown:
                        pos[i] = self.blank
            if blank_count == max_blank:
                for i in range(c, -1, self.width):
                    if pos[i] == self.unknown:
                        pos[i] = self.filled_single
        return True
    def __iter__( self ):
        min_solutions = None
        min_solution_penta = None
        min_solution_count = self.size*10
        for penta_i in set(self.pentas):
            solutions = {}
            for variant in self.penta_types.pentas[penta_i]:
                r = self.penta_types.penta_re[variant]
                solutions[variant] = list(r.finditer(self.pos))
            solution_count = sum(len(s) for s in solutions.values())
            if solution_count == 0: return
            if solution_count < min_solution_count:
                min_solutions = solutions
                min_solution_penta = penta_i
                min_solution_count = solution_count
            # print('penta %2d has %3d solutions %s' % (penta_i,solution_count,str([len(s) for s in solutions.values()])))
        prefilled_count = 0
        newpentas = self.pentas[:]
        newpentas.remove(min_solution_penta)
        nextstates = []
        for variant in self.penta_types.pentas[min_solution_penta]:
            # print('variant:')
            # for l in variant: print(l)
            for solution in min_solutions[variant]:
                variant_s = ''.join(variant)
                solution_s = ''.join(solution.groups())
                existing = [s for i,s in enumerate(solution_s) if variant_s[i] == '1']
                assert len(existing) == 5, (variant_s,solution_s,existing)
                # For each pentagram, exactly two boxes are already given (prefilled).
                if existing.count(self.prefilled) != 2: continue
                prefilled_count += 1

                newpos = list(self.pos)
                # loop rows and cols (r,c) in variant. p is the position in pos.
                for r in range(len(variant)):
                    for c,p in enumerate(range(solution.start(r+1), solution.end(r+1))):
                        v = variant[r][c]
                        if v == '0':
                            newpos[p] = self.blank
                        elif v == '1':
                            newpos[p] = self.filled_final
                        else:
                            assert v == '.', variant
                
                if self.check_rowcol_constraints(newpos):
                    nextstates.append(self.__class__(''.join(newpos), newpentas))
        new_solution_count = len(nextstates)
        for i, newstate in enumerate(nextstates[::-1]):
            newstate.treepos = self.treepos + [(new_solution_count-i, new_solution_count)]
            yield newstate
        # print('penta %2d (id %02d): %2d places -> %2d two prefilled ->%2d row/col count. queue %d iter %d' % \
        #     (len(self.pentas), min_solution_penta, min_solution_count, prefilled_count, new_solution_count, self.queuelen))
    def print_progress(self, itercount, queue):
        print('iter', itercount, 'queue len', len(queue), 'tree', ' '.join(str(p[0])+'/'+str(p[1]) for p in self.treepos))


def Show(cls):
    import time
    print(cls.__name__, cls.__doc__)
    t = time.time()
    solution = cls().solve()
    for s in solution:
        print(s)
    d = time.time() - t
    print("Duration: %d ms" % (d*1000))
    print()

if __name__ == '__main__':
    Show(PentaPuzzle)

