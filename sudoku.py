#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""sudoku.py

Sudoku solver in Python.

This library intends to solve sudoku, and sudoku-like puzzles using logic only. 
It is capable of solving any single-solution sudoku, as well as sudoku-like puzzles
(e.g. with diagonals, or 6x6 frames).

Since the library uses the same logic that humans apply, it is very well suited for 
getting hints.

Sudokus are solves by applying different strategies in order:
- Find fields with only a single candidate left
- Find singles in a block (a single is the is only field in a block where a given element can occur)
- Find naked pairs/triplets/quads (see http://www.sudokuwiki.org/Naked_Candidates)
- Find hidden pairs/triplets/quads (see http://www.sudokuwiki.org/Hidden_Candidates)
- Find pointing pairs/triplets (see http://www.sudokuwiki.org/Intersection_Removal)
- Compute all strong and weak links, and find truths and negatives by making assumptions
  - Determine that an assumption is wrong since it leads to a contradiction
  - Determine that a consequence is true, since both an assumption and the inverse of the 
    assumption lead to the same consequnce.

Created by Freek Dijkstra on 2010-08-04. Licensed under the 2-clause BSD license.
"""

from __future__ import print_function, unicode_literals

import math
import itertools
try:
    from collections import UserList    # python 3
except ImportError:
    from UserList import UserList       # python 2


class Stuck(Exception):
    """Raised when a solution may exist, but it can not be found"""
    pass

class Unsolvable(Exception):
    """Raised when no solution exists"""
    pass

class NoField(object):
    """A coordinate on a board that is not part of the game."""
    def __init__(self, x=1, y=1):
        self.x = x
        self.y = y
    def ingame(self):
        return False
    def solved(self):
        return True
    def newsolution(self):
        return False
    def __str__(self):
        return " "
    def __repr__(self):
        return "%s(%d,%d)" % (self.__class__.__name__, self.x, self.y)
    

class Field(NoField):
    """An coordinate on a board in a sudoku game."""
    def __init__(self, x=1, y=1, solution=None, candidates=None):
        NoField.__init__(self, x, y)
        if solution != None:
            self.candidates = [solution]
            # Do not yet set self.solution, so newsolution() is still True
        else:
            self.candidates = candidates[:] # make a copy of the candidates list
        self.solution = None
        self.blocks = []
    def ingame(self):
        return True
    def solved(self):
        return self.solution != None
    def newsolution(self):
        return self.solution == None and len(self.candidates) == 1
    def unsolvable(self):
        return len(self.candidates) == 0
    def solve(self, element=None):
        assert self.solution == None, "%s already solved" % repr(self)
        if element == None:
            assert len(self.candidates) == 1
            element = self.candidates[0]
        self.solution = element
        self.candidates = [element]
        for block in self.blocks:
            block.solve(self)
    def addblock(self, block):
        assert self in block
        self.blocks.append(block)
    def omit(self, element):
        try:
            self.candidates.remove(element)
            return True
        except ValueError:
            return False
    def __contains__(self, elt):
        return elt in self.candidates
    def __str__(self):
        if self.solved():
            return u"%s" % self.solution
        elif self.newsolution():
            return u"■"
            # bad markers (too wide): ☆ ⊠ ▣ ◉ ◎ ⊗ ⊕ ⊙ ☉ ◼ ╳ ⑴ ①
            # good markers: = □ ■ ◍ ! ◍
        else:
            return u"□"
    def __repr__(self):
        if self.solved():
            return "%s(%d,%d,solution=%s)" % (self.__class__.__name__,self.x, self.y,self.solution)
        else:
            return "%s(%d,%d,candidates=%s)" % (self.__class__.__name__,self.x, self.y,self.candidates)
    

class Block(UserList):
    """A restriction in the game. A block of fields each of which must have an unique element."""
    def __init__(self, fields, elements):
        self.elements = elements[:] # list of unsolved elements
        self.data = fields
        for field in self.data:
            field.addblock(self)
    def solved(self):
        return len(self.elements) == 0
    def solve(self, field):
        assert field in self.data
        for item in self.data:
            if item != field:
                item.omit(field.solution)
        assert field.solution in self.elements, "can't remove %s from block of %s" % (str(field.solution), self.elements)
        self.elements.remove(field.solution)
    def unsolvedelements(self):
        return self.elements
    def filter(self, element):
        """Return the fields which contain a given elements"""
        return [field for field in self.data if element in field]
    def __str__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self.data, self.elements)

class Option(object):
    """Solution assumption: a candidate in a certain field. (E.g. Field(1,1) = 3). The option contains strong links and weak links. Option objects are only used for more complex strategies involving assumptions."""
    def __init__(self, field, element):
        self.field = field
        self.element = element
        self.stronglinks = []
        self.weaklinks = []
    def alllinks(self):
        return self.stronglinks + self.weaklinks
    
    def addStrongLink(self, link):
        """Strong links are mutualy exclusive options. Meaning, (if self then not link) AND (if link then not self)"""
        if link not in self.stronglinks:
            self.stronglinks.append(link)
            link.addStrongLink(self)
    def addWeakLink(self, link):
        """Strong links are directed exclusive options. Meaning, (if self then not link). The reverse (if link then not self) does NOT apply."""
        if link not in self.weaklinks:
            self.weaklinks.append(link)
            link.addWeakLink(self)
    def __str__(self):
        return "%s(%s = %s)" % (self.__class__.__name__, repr(self.field), str(self.element))

class Assumption(object):
    """Assuming a given option is either true or false, allow to walk all logic by following weak and strong links."""
    def __init__(self, option):
        if not isinstance(option, (list, set)):
            option = set([option])
        self.assumptions = option
        self.iftrue_truths    = set(option)
        self.iftrue_negatives = set()
        self.iffalse_truths   = set()
        if len(self.iftrue_truths) == 1:
            self.iffalse_negatives = set(option)
        else:
            # if a set of more assumptions is False, not every item need to be False.
            self.iffalse_negatives   = set()
        self.newiftrue_truths  = set(self.iftrue_truths)
        self.newiftrue_negatives    = set(self.iftrue_negatives)
        self.newiffalse_truths = set(self.iffalse_truths)
        self.newiffalse_negatives   = set(self.iffalse_negatives)
        self.logic  = None  # set to True or False if the assumption must be True or False
        self.negatives   = set() # list of options which must be False, regardless id the assumption is True or False
        self.truths = set() # list of options which must be True, regardless id the assumption is True or False
        self.itercount = 0
    
    def setLogic(self, logic):
        self.logic = logic
        if logic:
            self.truths.update(self.iftrue_truths)
            self.negatives.update(self.iftrue_negatives)
        else:
            self.truths.update(self.iffalse_truths)
            self.negatives.update(self.iffalse_negatives)
    
    def addiftrue_truth(self, option):
        """Add an option which must be True is the assumption is True"""
        if option in self.iftrue_truths:
            return
        self.iftrue_truths.add(option)
        self.newiftrue_truths.add(option)
        if option in self.iffalse_truths:
            self.truths.add(option)
        if option in self.iftrue_negatives:
            self.setLogic(False)
            # raise Unsolvable()
    
    def addiftrue_negative(self, option):
        """Add an option which must be False is the assumption is True"""
        if option in self.iftrue_negatives:
            return
        self.iftrue_negatives.add(option)
        self.newiftrue_negatives.add(option)
        if option in self.iffalse_negatives:
            self.negatives.add(option)
        if option in self.iftrue_truths:
            self.setLogic(False)
            # raise Unsolvable()
    
    def addiffalse_truth(self, option):
        """Add an option which must be False is the assumption is False"""
        if option in self.iffalse_truths:
            return
        self.iffalse_truths.add(option)
        self.newiffalse_truths.add(option)
        if option in self.iftrue_truths:
            self.truths.add(option)
        if option in self.iffalse_negatives:
            self.setLogic(True)
    
    def addiffalse_negative(self, option):
        """Add an option which must be False is the assumption is False"""
        if option in self.iffalse_negatives:
            return
        self.iffalse_negatives.add(option)
        self.newiffalse_negatives.add(option)
        if option in self.iftrue_negatives:
            self.negatives.add(option)
        if option in self.iffalse_truths:
            self.setLogic(True)
    
    def hasanswer(self):
        return self.logic != None
    
    def hastruths(self):
        return len(self.truths) > 0
    
    def solveiter(self):
        if self.itercount % 2 == 0:
            assert len(self.newiftrue_negatives) == 0
            assert len(self.newiffalse_truths) == 0
            while len(self.newiftrue_truths) > 0:
                option = self.newiftrue_truths.pop()
                for invoption in option.alllinks():
                    self.addiftrue_negative(invoption)
            while len(self.newiffalse_negatives) > 0:
                option = self.newiffalse_negatives.pop()
                for invoption in option.stronglinks:
                    self.addiffalse_truth(invoption)
            newcount = len(self.newiftrue_negatives) + len(self.newiffalse_truths)
        else:
            assert len(self.newiftrue_truths) == 0
            assert len(self.newiffalse_negatives) == 0
            while len(self.newiftrue_negatives) > 0:
                option = self.newiftrue_negatives.pop()
                for invoption in option.stronglinks:
                    self.addiftrue_truth(invoption)
            while len(self.newiffalse_truths) > 0:
                option = self.newiffalse_truths.pop()
                for invoption in option.alllinks():
                    self.addiffalse_negative(invoption)
            newcount = len(self.newiftrue_truths) + len(self.newiffalse_negatives)
        self.itercount += 1
        return newcount
    def __str__(self):
        optionstr = "; ".join(["Field(%d,%d) = %s" % (o.field.x, o.field.y, o.element) for o in self.assumptions])
        return "%s(%s) [iteration %d; logic=%s; %d truths (%d if true; %d if false); %d refutes (%d if true; %d if false)]" % \
                (self.__class__.__name__, optionstr, self.itercount, self.logic, len(self.truths), len(self.iftrue_truths), \
                len(self.iffalse_truths), len(self.negatives), len(self.iftrue_negatives), len(self.iffalse_negatives))

class Sudoku(object):
    def __init__(self, numbers, elements=None):
        """Solve the given sudoku, in the same way a human would solve it.
        elements is all possible element to be filled in (1...9 by default)
        numbers is a 2-dimensional array with either:
        - a number in elements for pre-filled number
        - the element None for fields not participating in the problem
        - 0 for elements which need to be solved
        blocks is a list of a set of coordinates (x,y). Each set must only contain different numbers.
        The length of each set MUST be the same as the length of elements.
        """
        if elements == None:
            self.dim = len(numbers[0])
            self.elements = list(range(1,self.dim+1))
        else:
            self.dim = len(elements)
            self.elements = elements
        
        self.fields = []
        for i,numrow in enumerate(numbers):
            fieldrow = []
            for j,element in enumerate(numrow):
                if element == None:
                    field = NoField(i,j)
                elif element == 0:
                    field = Field(i,j,candidates=self.elements)
                else:
                    assert element in self.elements, "%s is not a valid element in a sudoku" % (element)
                    field = Field(i,j,solution=element)
                fieldrow.append(field)
            self.fields.append(fieldrow)
        
        allblockcoords = self.defaultblockcoords()
        self.blocks = []
        for blockcoords in allblockcoords:
            assert len(blockcoords) == self.dim, "every block must have length %d" % (self.dim)
            fields = []
            for coord in blockcoords:
                try:
                    field = self.fields[coord[0]][coord[1]]
                except IndexError:
                    raise IndexError("field(%d,%d) does not exist." % coord)
                assert field.x == coord[0] and field.y == coord[1]
                assert field.ingame()
                fields.append(field)
            block = Block(fields, self.elements)
            self.blocks.append(block)
    
    def maxblockoverlap(self):
        if not hasattr(self, '_maxblockoverlap'):
            self._maxblockoverlap = 0
            for block in self.blocks:
                for block2 in self.blocks:
                    overlap = 0
                    for field in block:
                        if field in block2:
                            overlap += 1
                    if overlap > self._maxblockoverlap:
                        self._maxblockoverlap = overlap
        return self._maxblockoverlap
    
    def gamefields(self):
        for row in self.fields:
            for field in row:
                if field.ingame():
                    yield field
    
    def solvefields(self):
        """Find fields with a single candidate
        Trivial strategy.
        Loop through all fields, checking if only one option remains. If so, list it a the solution and remove that option from the block."""
        count = 0
        for field in self.gamefields():
            if field.unsolvable():
                raise Unsolvable("No solutions left for %d,%d" % (field.x,field.y))
            if field.newsolution():
                field.solve()
                count += 1
        return count
    
    def solveblockssingles(self):
        """Find singles in a block
        Basic strategy.
        Loop through all blocks and elements, checking if only one available field remains for a given element. If so, solve that field by assigning this element."""
        count = 0
        for block in self.blocks:
            for element in block.unsolvedelements():
                fields = block.filter(element)
                if len(fields) == 1:
                    count += 1
                    field = fields[0]
                    fields[0].solve(element)
        return count
    
    def solvenakedpairs(self):
        """Find naked pairs/triplets/quads
        Basic strategy. See http://www.sudokuwiki.org/Naked_Candidates
        Loop through all blocks and elements, compare all sets of 2, 3 or 4 fields. If these fields have the same set of 2, 3 or 4 candidates, these fields. If so, these elements can only use occur at these field. Omit these elements from all other fields.
        """
        count = 0
        for block in self.blocks:
            unsolvedelements = block.unsolvedelements()
            # check for pairs, triplets, quadruplets, etc.
            for i in range(2,1+len(unsolvedelements)//2):
                # find fields with i elements
                fields = []
                for field in block:
                    if len(field.candidates) == i:
                        fields.append(field)
                # For example, we may now have for 4 fields, with candidates:
                # [1,4],[2,3],[2,3],[1,4]
                # meaning that 1,4 can only occur in these four fields.
                # meaning that 2,3 can only occur in these four fields.
                # Take size-i combinations from fields, and see if the candidates are equals.
                for fieldspair in itertools.combinations(fields, i):
                    # Take the first fields
                    elements = fieldspair[0].candidates
                    # check if the remaining i-1 fields are the same.
                    c = 1
                    for j in range(1,i):
                        if fieldspair[j].candidates == elements:
                            c += 1
                    if c == i:
                        # We have a pair/triple/quad!
                        # onlyfieldpairs may contain elements.
                        success = False
                        for field in block:
                            if field not in fieldspair:
                                for element in elements:
                                    if field.omit(element):
                                        success = True
                        if success:
                            count += 1  # only report success if elements are removed from fields
        return count
    
    def solvehiddenpairs(self):
        """Find hidden pairs/triplets/quads
        Basic strategy. See http://www.sudokuwiki.org/Hidden_Candidates
        Loop through all blocks and elements. This yields a (small) set of fields. Loop through all other blocks, and see if all these fields occur in this second block. The given element can only occur in the found fields, and can thus be removed from the other fields in the second block."""
        count = 0
        for block in self.blocks:
            # Store element -> [list of fields that contain element]
            elementfields = {}
            for element in block.unsolvedelements():
                elementfields[element] = block.filter(element)
            # check for pairs, triplets, quadruplets, etc.
            for i in range(2,len(elementfields)//2):
                # find elements which only occur in i fields.
                elements = []
                for element, fields in elementfields.items():
                    if len(fields) == i:
                        elements.append(element)
                # For example, we may now have for i=2: elements=[1,3,5,6]
                # meaning that 1,3,5 and 6 only occur in two fields.
                # Take size-i combinations from elements, and see if the fields are equals.
                for elementpairs in itertools.combinations(elements, i):
                    # Take the first fields
                    fields = elementfields[elementpairs[0]]
                    # check if the remaining i-1 fields are the same.
                    c = 1
                    for j in range(1,i):
                        if elementfields[elementpairs[j]] == fields:
                            c += 1
                    if c == i:
                        # We have a pair/triple/quad!
                        # fields may only contain elements.
                        success = False
                        for field in fields:
                            for element in block.unsolvedelements():
                                if element not in elements:
                                    if field.omit(element):
                                        success = True
                        if success:
                            count += 1  # only report success if elements are removed from fields
        return count
    
    def solvesubsection(self):
        """Find subsection pairs/triplets
        Basic strategy. Aka pointing pairs. See http://www.sudokuwiki.org/Intersection_Removal
        Loop through all blocks and elements. This yields a (small) set of fields. Loop through all other blocks, and see if all these fields occur in this second block. The given element can only occur in the found fields, and can thus be removed from the other fields in the second block."""
        count = 0
        for block in self.blocks:
            for element in block.unsolvedelements():
                fields = block.filter(element)
                l = len(fields)
                if l > self.maxblockoverlap():
                    continue
                for extblock in self.blocks:
                    if extblock == block:
                        continue
                    if element not in extblock.unsolvedelements():
                        continue
                    c = 0
                    for field in fields:
                        if field in extblock:
                            c += 1
                    if c == l:
                        # We have an intersection!
                        # fields in extblock, but not in fields may not contain element.
                        success = False
                        for extfield in extblock:
                            if extfield not in fields:
                                if extfield.omit(element):
                                    success = True
                        if success:
                            count += 1  # only report success if elements are removed from fields
        return count
    
    def getoption(self, field, element):
        if (field, element) not in self.options:
            assert not field.solved()
            self.options[(field,element)] = Option(field,element)
        return self.options[(field,element)]
    
    def buildoptions(self):
        """Compute strong and weak links (for advanced strategies)
        Create a complete set of options, including strong and weak links between the options. This set is required for the more advanced strategies."""
        self.options = {}
        for field in self.gamefields():
            if field.solved():
                continue
            for element in field.candidates:
                option = self.getoption(field, element)
                # Set strong and weak links
                # For links across a block
                for block in field.blocks:
                    extfields = block.filter(element)
                    strong = len(extfields) == 2
                    for extfield in extfields:
                        if extfield == field:
                            continue
                        extoption = self.getoption(extfield, element)
                        if strong:
                            option.addStrongLink(extoption)
                        else:
                            option.addWeakLink(extoption)
                strong = len(field.candidates) == 2
                for extelement in field.candidates:
                    if extelement == element:
                        continue
                    extoption = self.getoption(field, extelement)
                    if strong:
                        option.addStrongLink(extoption)
                    else:
                        option.addWeakLink(extoption)
        return 0
    
    def solvewithassumptions(self, maxoptions=None, maxiter=None):
        """Find truths and negatives with assumptions
        Though strategy. See http://www.sudokuwiki.org/X_Wing_Strategy
        Loop through all blocks and elements. This yields a (small) set of fields. Loop through all other blocks, and see if all these fields occur in this second block. The given element can only occur in the found fields, and can thus be removed from the other fields in the second block."""
        count = 0
        if maxoptions == None:
            maxoptions = len(self.options)
        fieldcount = 0
        if maxiter == None:
            maxiter = 2*len(self.options)
        # print()
        # print("%d options" % len(self.options))
        options = sorted(self.options.values(), reverse=True,
                key=lambda option: (len(option.stronglinks),len(option.weaklinks)))
        for optioncount in range(maxoptions):
            option = options[optioncount]
            assumption = Assumption(option)
            # print()
            # print(option,len(option.stronglinks),len(option.weaklinks))
            for itercount in range(maxiter):
                c = assumption.solveiter()
                # print(assumption, c)
                if assumption.hasanswer() or assumption.hastruths() or c == 0:
                    break
            # print("strong",len(option.stronglinks),"weak",len(option.weaklinks),assumption)
            for option in assumption.truths:
                if option.field.solved():
                    continue
                option.field.solve(option.element)
                count += 1
            for option in assumption.negatives:
                if option.field.omit(option.element):
                    count += 1
        return count
    
    def solvewithassumptions_20_10(self):
        """Find truths and negatives with assumptions (max 10 iterations)"""
        return self.solvewithassumptions(20,10)
    
    def solveiter(self, debug=1):
        """Iterate over a given game, applying a single strategy over the whole board; if that fails, try a slightly more complex strategy over the whole board, and so on till we found a change in the board."""
        strategies = [
            self.solvefields,
            self.solveblockssingles,
            self.solvenakedpairs,
            self.solvehiddenpairs,
            self.solvesubsection,
            self.buildoptions,
            # self.solvewithassumptions_20_10,
            self.solvewithassumptions,
        ]
        
        res = 0
        for strategy in strategies:
            if debug:
                line = strategy.__doc__.splitlines()[0]
                print(line + " ... ", end="")
            res = strategy()
            # res = timing.runfunc(strategy, ())
            if debug:
                print("%d found\n" % res, end="")
            if res > 0:
                break
        
        return res > 0
    
    def solve(self, debug=1):
        while not self.solved():
            if debug > 1:
                print(self.longstr())
            elif debug:
                print(self.mediumstr())
            if not self.solveiter(debug):
                raise Stuck()
        if debug > 1:
            print(self.longstr())
        elif debug:
            print(self.mediumstr())
        self.solution = []
        for row in self.fields:
            solrow = []
            for num in row:
                solrow.append(num.solution)
            self.solution.append(solrow)
        return self.solution
    
    def solved(self):
        for field in self.gamefields():
            if not field.solved():
                return False
        return True
    
    def rowcoords(self, row, column=0, length=9):
        """Return the coordinates of a row from (row,column) up to inclusive (row,column+length-1)"""
        block = []
        for j in range(length):
            block.append((row,column+j))
        return block
    
    def columncoords(self, column, row=0, length=9):
        """Return the coordinates of a columns from (row, column) up to inclusive (row+length-1,column)"""
        block = []
        for i in range(length):
            block.append((row+i,column))
        return block
    
    def SEdiagonalcoords(self, row=0, column=0, length=9):
        """Return the coordinates of a diagonal from top left (row,column) to bottom right (row+length-1, column+lenght-1)"""
        block = []
        for j in range(length):
            block.append((row+j,column+j))
        return block
    
    def SWdiagonalcoords(self, row=0, column=0, length=9):
        """Return the coordinates of a diagonal from top right (row,column+lenght-1) to bottom left (row+length-1, column)"""
        block = []
        for j in range(length):
            block.append((row+j,column+lenght-j))
        return block
    
    def squarecoords(self, row, column, rowlength=3, columnlength=3):
        """Return the coordinates of a square of size rowlength × columnlength, with (start, column) the top-left position"""
        block = []
        for i in range(row,row+rowlength):
            for j in range(column,column+columnlength):
                block.append((i,j))
        return block
    
    def defaultblockcoords(self, rows=True, columns=True, diagonals=False, squares=True, insetsquares=False):
        blocks = []
        if rows:
            for i in range(self.dim):
                blocks.append(self.rowcoords(row=i, length=self.dim))
        if columns:
            for j in range(self.dim):
                blocks.append(self.columncoords(column=j, length=self.dim))
        if diagonals:
            blocks.append(self.SEdiagonalcoords(length=self.dim))
            blocks.append(self.SWdiagonalcoords(length=self.dim))
        if squares:
            sl = int(math.sqrt(self.dim))
            assert sl**2 == self.dim, "l, the side of a sudoku, must be a square (4x4, 9x9, etc)"
            for i in range(0,self.dim,sl):
                for j in range(0,self.dim,sl):
                    blocks.append(self.squarecoords(i,j,sl,sl))
        if insetsquares:
            sl = int(math.sqrt(self.dim))
            assert sl**2 == self.dim, "l, the side of a sudoku, must be a square (4x4, 9x9, etc)"
            blocks.append(self.squarecoords(1,1,sl,sl))
            blocks.append(self.squarecoords(self.dim-1-sl,1,sl,sl))
            blocks.append(self.squarecoords(1,self.dim-1-sl,sl,sl))
            blocks.append(self.squarecoords(self.dim-1-sl,self.dim-1-sl,sl,sl))
        return blocks
    
    def shortstr(self):
        """Return an unicode string with a short overview of the solving progress. e.g.
        □ □ ■ □ ■ □ ■ □ □
        ■ □ □ ■ □ ■ □ □ ■
        □ □ ■ ■ □ ■ ■ □ □
        □ □ ■ ■ □ ■ ■ □ □
        ■ □ □ □ □ □ □ □ ■
        □ □ ■ ■ □ ■ ■ □ □
        □ □ ■ ■ □ ■ ■ □ □
        ■ □ □ ■ □ ■ □ □ ■
        □ □ ■ □ ■ □ ■ □ □
        out = u"""
        for row in self.fields:
            for num in row:
                out += u"%s " % (num)
            out += u"\n"
        return out
    
    def mediumstr(self):
        """Return an unicode string with a short but slightly formated overview of the solving progress. e.g.
        ┌─────┬─────┬─────┐
        │□ □ ■│□ ■ □│■ □ □│
        │■ □ □│■ □ ■│□ □ ■│
        │□ □ ■│■ □ ■│■ □ □│
        ├─────┼─────┼─────┤
        │□ □ ■│■ □ ■│■ □ □│
        │■ □ □│□ □ □│□ □ ■│
        │□ □ ■│■ □ ■│■ □ □│
        ├─────┼─────┼─────┤
        │□ □ ■│■ □ ■│■ □ □│
        │■ □ □│■ □ ■│□ □ ■│
        │□ □ ■│□ ■ □│■ □ □│
        └─────┴─────┴─────┘"""
        sl = int(math.sqrt(self.dim))
        sep = u"┌" + (sl*(u"┬" + (2*sl-1)*u"─"))[1:] + u"┐\n"
        out = sep
        sep = u"├" + (sl*(u"┼" + (2*sl-1)*u"─"))[1:] + u"┤\n"
        for i,row in enumerate(self.fields):
            if (i % sl) == 0 and (i > 0):
                out += sep
            for j,num in enumerate(row):
                if (j % sl) == 0:
                    out += u"│%s" % (num)
                else:
                    out += u" %s" % (num)
            out += u"│\n"
        sep = u"└" + (sl*(u"┴" + (2*sl-1)*u"─"))[1:] + u"┘\n"
        out += sep
        return out
    
    def longstr(self):
        """Return an unicode string with details on the current solving progress. e.g.
           0     1     2     3     4     5     6     7     8
          ╔═════╤═════╤═════╦═════╤═════╤═════╦═════╤═════╤═════╗
        0 ║12345│12345│     ║12345│12345│     ║12345│12345│     ║
          ║6789□│6789■│  8 ■║6789□│6789■│  8 ■║6789□│6789■│  8 ■║
          ╟─────┼─────┼─────╫─────┼─────┼─────╫─────┼─────┼─────╢
        1 ║12345│12345│  9  ║12345│12345│  9  ║12345│12345│  9  ║
          ║6789■│6789■│     ║6789■│6789■│     ║6789■│6789■│     ║
          ╟─────┼─────┼─────╫─────┼─────┼─────╫─────┼─────┼─────╢
        2 ║12345│12345│12345║12345│12345│12345║12345│12345│12345║
          ║6789■│6789■│6789■║6789■│6789■│6789■║6789■│6789■│6789■║
          ╠═════╪═════╪═════╬═════╪═════╪═════╬═════╪═════╪═════╣
        3 ║12345│12345│     ║12345│12345│     ║12345│12345│     ║
          ║6789□│6789■│  8 ■║6789□│6789■│  8 ■║6789□│6789■│  8 ■║
          ╟─────┼─────┼─────╫─────┼─────┼─────╫─────┼─────┼─────╢
        4 ║12345│12345│  9  ║12345│12345│  9  ║12345│12345│  9  ║
          ║6789■│6789■│     ║6789■│6789■│     ║6789■│6789■│     ║
          ╟─────┼─────┼─────╫─────┼─────┼─────╫─────┼─────┼─────╢
        5 ║12345│12345│12345║12345│12345│12345║12345│12345│12345║
          ║6789■│6789■│6789■║6789■│6789■│6789■║6789■│6789■│6789■║
          ╠═════╪═════╪═════╬═════╪═════╪═════╬═════╪═════╪═════╣
        6 ║12345│12345│     ║12345│12345│     ║12345│12345│     ║
          ║6789□│6789■│  8 ■║6789□│6789■│  8 ■║6789□│6789■│  8 ■║
          ╟─────┼─────┼─────╫─────┼─────┼─────╫─────┼─────┼─────╢
        7 ║12345│12345│  9  ║12345│12345│  9  ║12345│12345│  9  ║
          ║6789■│6789■│     ║6789■│6789■│     ║6789■│6789■│     ║
          ╟─────┼─────┼─────╫─────┼─────┼─────╫─────┼─────┼─────╢
        8 ║12345│12345│12345║12345│12345│12345║12345│12345│12345║
          ║6789■│6789■│6789■║6789■│6789■│6789■║6789■│6789■│6789■║
          ╚═════╧═════╧═════╩═════╧═════╧═════╩═════╧═════╧═════╝"""
        # determine box height and box width.
        # ratio between the height and width of a character on screen.
        # in practice, this is about 7 by 3 = 2.33. The given ratio is an upper limit. 
        # Values between 2.0 and 3.0 give good results.
        ratio = 2.33
        # The formula is an approximation which gives best results
        # The size of the box must fit all elements +1.
        bh = int(math.sqrt((len(self.elements)+1)/ratio)+0.7)
        bw = int(math.ceil(float(len(self.elements)+1)/bh))
        # sl is the lenght of a box (3 for a 9x9 sudoku)
        sl = int(math.sqrt(self.dim))
        # center line (0-based) and center character
        cl = (bh-1) // 2
        cc = bw // 2
        # Since the elements are distributed over multiple lines, keep track 
        # of the starting element for each line. Also store the spaces between the last 
        # element and the status indicator
        eltidx = list(range(0,self.dim,bw))
        assert len(eltidx) == bh
        spaces = (bh*bw-self.dim-1)*u" "  # use non breaking spaces
        topsep = u"╔" + (sl*(u"╦" + (sl*(u"╤" + bw*u"═"))[1:]))[1:] + u"╗\n"
        numsep = u"╟" + (sl*(u"╫" + (sl*(u"┼" + bw*u"─"))[1:]))[1:] + u"╢\n"
        boxsep = u"╠" + (sl*(u"╬" + (sl*(u"╪" + bw*u"═"))[1:]))[1:] + u"╣\n"
        botsep = u"╚" + (sl*(u"╩" + (sl*(u"╧" + bw*u"═"))[1:]))[1:] + u"╝\n"
        out = topsep
        for i,row in enumerate(self.fields):
            if (i % sl) > 0:
                out += numsep
            elif i > 0:
                out += boxsep
            for l in range(bh):
                for j,num in enumerate(row):
                    if (j % sl) == 0:
                        out += u"║"
                    else:
                        out += u"│"
                    if num.solved():
                        if l == cl:
                            out += cc*u" " + (u"%s" % num.solution) + (bw-cc-1)*u" "
                        else:
                            out += bw*u" "
                    else:
                        for e in range(bw*l,min(self.dim,bw*(l+1))):
                            if self.elements[e] in num:
                                out += u"%s" % (self.elements[e])
                            else:
                                out += u" "
                        if l+1 == bh:
                            out += spaces
                            out += u"%s" % (num)
                out += u"║\n"
        out += botsep
        return out
    
    def __str__(self):
        return self.longstr()
    


if __name__ == '__main__':
    u"""Solution a: Solve a sudoku in the same way a human would."""
    numbers = [
        # near insolvable
        [0,9,0,0,0,0,0,2,0],
        [5,0,0,3,0,2,0,0,0],
        [0,0,4,0,1,0,0,9,5],
        [0,0,0,2,0,9,0,0,0],
        [9,0,7,0,5,0,6,0,2],
        [0,0,0,1,0,6,0,0,0],
        [1,8,0,0,6,0,9,0,0],
        [0,0,0,5,0,1,0,0,6],
        [0,3,0,0,0,0,0,7,0],
    ]
    try:
        s = Sudoku(numbers)
        s.solve(debug=1)
    except Stuck as e:
        print("  #####                             ### ")
        print(" #     # ##### #    #  ####  #    # ### ")
        print(" #         #   #    # #    # #   #  ### ")
        print("  #####    #   #    # #      ####    #  ")
        print("       #   #   #    # #      #  #       ")
        print(" #     #   #   #    # #    # #   #  ### ")
        print("  #####    #    ####   ####  #    # ### ")
    else:
        for row in s.solution:
            print(row)

