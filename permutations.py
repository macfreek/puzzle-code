#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = "1.1"

"""permutations.py
Generators for calculating a) the permutations of a sequence and
b) the combinations and selections of a number of elements from a
sequence.

Keywords: generator, combination, permutation, selection

See also: http://code.activestate.com/recipes/190465/
See also: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/105962
See also: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66463
See also: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66465
"""

import itertools

# NOTE: while all functions are very similar, we do not refactor them for speed.
# For example, permutations(items) could simply `return combinations(items, len(items))`, 
# but that would yield about 20% overhead.

# The uniqueSelections() and rotations() are additions to the original version 1.0.

def rotations(items):
    """Rotations takes alle elements, and rotates the starting item.
    Example: Rotations of 'ABCD':
    ABCD BCDA CDAB DABC
    """
    for l in range(len(items)):
        yield items[l:]+items[:l]

def permutations(items):
    """permutations takes all elements from the sequence, in all possible orders.
    permutations without replacement.
    Example: Permutations of 'ABCD':
    ABCD ABDC ACBD ACDB ADBC ADCB BACD BADC BCAD BCDA BDAC BDCA CABD CADB CBAD CBDA CDAB CDBA DABC DACB DBAC DBCA DCAB DCBA
    permutations(items) is equal to combinatons(items, len(items))
    """
    n = len(items)
    if n==0: 
        yield []
    else:
        for i in range(len(items)):
            for cc in permutations(items[:i] + items[i+1:]):
                yield [items[i]]+cc

from math import factorial
# def factorial(n):
#     return reduce(lambda x,y: x*y, range(1,n+1), 1)

def numuniquepermutations(items):
    """Return the number of unique permutations"""
    n = factorial(len(items))
    # find duplicate items
    c = 0
    previtem = None
    for item in sorted(items):
        if item != previtem:
            n /= factorial(c)
            c = 0
            previtem = item
        c += 1
    n /= factorial(c)
    return n

def combinations(items, n):
    """combinations takes an ordered set of n distinct elements from the sequence.
    permutation without replacement
    Example: Combinations of 2 letters from 'ABCD':
    AB AC AD BA BC BD CA CB CD DA DB DC
    combinations() is similar to itertools.permutations(), but is guaranteed to 
    work for infinite iterators. 
    For example, an iteration of 3-dimensional integers yields
    (1 2 3) (2 1 3) (1 3 2) (2 3 1) (3 1 2) (3 2 1) (1 2 4) (2 1 4) (1 4 2) ...
    Compare this to itertools.permutations(), which would yield 
    (1,2,3) (1,2,4) (1,2,5) (1,2,6) (1,2,7) .... and never reach e.g. (1,3,4).
    """
    for ss in uniqueCombinations(items, n):
        for p,g in itertools.groupby(sorted(itertools.permutations(ss))):
            yield p


def uniqueCombinations(items, n):
    """uniqueCombinations takes an unordered set of n distinct elements from the sequence.
    combination without replacement
    Example: Unique Combinations of 2 letters from 'ABCD':
    AB AC AD BC BD CD
    uniqueCombinations() is similar to itertools.combinations(), but is guaranteed to 
    work for infinite iterators. 
    For example, an iteration of 3-dimensional integers yields
    (1,2,3) (1,2,4) (1,3,4) (2,3,4) (1,2,5) (1,3,5) (2,3,5) (1,4,5) (2,4,5) (3,4,5) ...
    Compare this to itertools.combinations(), which would yield 
    (1,2,3) (1,2,4) (1,2,5) (1,2,6) (1,2,7) .... and never reach e.g. (1,3,4).
    """
    if n==0: 
        yield []
    else:
        saved = []
        for item in items:
            for cc in uniqueCombinations(saved, n-1):
                yield cc+[item]
            saved.append(item)


def selections(items, n):
    """selections takes an ordered set of n elements (not necessarily distinct) from the sequence.
    permutation with replacement
    Example: Selections of 2 letters from 'ABCD':
    AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD
    selections() is similar to itertools.product(), but is guaranteed to 
    work for infinite iterators. 
    For example, an iteration of 3-dimensional integers yields
    (1,1,1) (1,1,2) (1,2,1) (2,1,1) (1,2,2) (2,1,2) (2,2,1) (2,2,2) (1,1,3) (1,3,1) ...
    Compare this to itertools.product(), which would yield 
    (1,1,1) (1,1,2) (1,1,3) (1,1,4) (1,1,5) .... and never reach e.g. (1,2,1).
    """
    for ss in uniqueSelections(items, n):
        for p,g in itertools.groupby(sorted(itertools.permutations(ss))):
            yield p


def uniqueSelections(items, n):
    """selections takes an unordered set of n elements (not necessarily distinct) from the sequence.
    combination with replacement
    Example: Selections of 2 letters from 'ABCD':
    AA AB AC AD BB BC BD CC CD DD
    combinations() is similar to itertools.combinations_with_replacement(), but is guaranteed to 
    work for infinite iterators. 
    For example, an iteration of 3-dimensional integers yields
    (1,1,1) (1,1,2) (1,2,2) (2,2,2) (1,1,3) (1,2,3) (2,1,3) (2,2,3) (1,3,3) (2,3,3) ...
    Compare this to itertools.combinations_with_replacement(), which would yield 
    (1,1,1) (1,1,2) (1,1,3) (1,1,4) (1,1,5) .... and never reach e.g. (1,2,1).
    """
    if n==0: 
        yield []
    else:
        saved = []
        for item in items:
            saved.append(item)
            for cc in uniqueSelections(saved, n-1):
                yield cc+[item]


def undirected_cyclic_permutations(items, n):
    """undirected_cyclic_permutations takes an ordered cyclic set of n 
    distinct elements from the sequence. permutation without replacement, 
    E.g. ('ABCDE', 4) yields: ABCD ABCE ABDC ABDE ABEC ABED ACBD ACBE ACDE 
    ACED ADBE ADCE BCDE BCED.
    ABCD is considered the same cycle as BCDA CDAB DABC DCBA CBAD BADC ADCB.
    """
    if n == 0:
        yield []
    elif n == 1:
        for first in items:
            yield [first]
    else:
        for cc in directed_cyclic_permutations(range(len(items)), n):
            if cc[1] <= cc[-1]:
                yield [items[i] for i in cc]


def directed_cyclic_permutations(items, n):
    """directed_cyclic_permutations takes an ordered cyclic set of n 
    distinct elements from the sequence. permutation without replacement, 
    E.g. ('ABCDE', 4) yields: 
    ABCD ABCE ABDC ABDE ABEC ABED ACBD ACBE ACDB ACDE 
    ACEB ACED ADBC ADBE ADCB ADCE ADEB ADEC AEBC AEBD 
    AECB AECD AEDB AEDC BCDE BCED BDCE BDEC BECD BEDC.
    ABCD is considered the same cycle as BCDA CDAB DABC.
    """
    if n == 0:
        yield []
    else:
        for i,first in enumerate(items):
            for cc in itertools.permutations(items[i+1:], n-1):
                yield [first] + list(cc)


def mutations(items, n, replaceitems):
    """mutations are sequences where n items are replaced by other items, given in replaceitems.
    Example: Mutations of 2 letters from 'ABCD', with 'G','H' as possible replacements:
    GGCD GHCD GBGD GBHD GBCG GBCH HGCD HHCD HBGD HBHD HBCG HBCH AGGD AGHD AGCG AGCH AHGD AHHD AHCG AHCH ABGG ABGH ABHG ABHH
    """
    if n == 0:
        yield items
    elif n == 1:
        for i in range(len(items)):
            for alt in replaceitems:
                yield items[:i] + [alt] + items[i+1:]
    else:  # n > 1
        for i in range(len(items)):
            for alt in replaceitems:
                for mm in mutations(items[i+1:],n-1,replaceitems):
                    yield items[:i] + [alt] + mm


def homogeneousMutations(items, n, replaceitems):
    """homogeneousMutations are sequences where n items are replaced by the same other item, given in replaceitems.
    Example: Mutations of 2 letters from 'ABCD', with 'G','H' as possible replacements:
    GGCD HHCD GBGD HBHD GBCG HBCH AGGD AHHD AGCG AHCH ABGG ABHH
    """
    if n == 0:
        yield items
    else:
        idx = range(len(items))
        for p in uniqueCombinations(idx,n):
            for alt in replaceitems:
                newitems = items[:]
                for i in p:
                    newitems[i] = alt
                yield newitems



if __name__=="__main__":
    print ("Rotations of 'love'")
    for p in rotations(['l','o','v','e']): print (''.join(p))
    
    print ()
    print ("Permutations of 'love'")
    for p in permutations(['l','o','v','e']): print (''.join(p))
    
    print ()
    print ("Combinations of 4 letters from 'love'")
    for c in combinations(['l','o','v','e'],4): print (''.join(c))
    
    print ()
    print ("Combinations of 2 letters from 'love'")
    for c in combinations(['l','o','v','e'],2): print (''.join(c))
    
    print()
    print ("Unique Combinations of 2 letters from 'love'")
    for uc in uniqueCombinations(['l','o','v','e'],2): print (''.join(uc))
    
    print()
    print ("Selections of 2 letters from 'love'")
    for s in selections(['l','o','v','e'],2): print (''.join(s))
    
    print()
    print ("Unique Selections of 3 letters from 'love'")
    for s in uniqueSelections(['l','o','v','e'],3): print (''.join(s))
    
    print()
    print ("Directed Cyclic Permutations of 3 letters from 'love'")
    for s in directed_cyclic_permutations('love',3): print (''.join(s))
    
    print()
    print ("Undirected Cyclic Permutations of 3 letters from 'love'")
    for s in undirected_cyclic_permutations('love',3): print (''.join(s))
    
    print()
    print ("Mutation of 2 letters from 'love' with 'me'")
    for s in mutations(['l','o','v','e'],2,['m','e']): print (''.join(s))
    
    print()
    print ("Homogenous mutation of 2 letters from 'love' with 'me'")
    for s in homogeneousMutations(['l','o','v','e'],2,['m','e']): print (''.join(s))

