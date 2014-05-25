#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""primes.py
Helper function to calculate continued fractions.

Continued fractions are useful for solving the Pell equation: x² - D·y² = ±1

The continued fraction of r is givens as the sequence a₀, a₁, a₂, a₃, ..., such that:

                   1
   r = a₀ + ――――――――――――――――――
                      1
            a₁ + ―――――――――――――
                         1
                 a₂ + ――――――――
                      a₃ + ...

For example, the continued fraction of √2 is:

                  1
   √2 = 1 + ―――――――――――――――――――
                     1
            2 + ―――――――――――――――
                        1
                2 + ―――――――――――
                           1
                    2 + ―――――――
                        2 + ...

The continued fractions of all irrational square roots (quadraric surds) are repeating. For conciseness, we use the notation √2 = (1,[2]), to indicate that the block [2] repeats indefinitely.

The continued fraction of a quadratic surd always becomes periodic at some term a_(r+1), where a_(r+1) = 2·a_0, with the terms a_1 thru a_r the repeating terms.

A continued fraction r = (a₀, a₁, a₂, a₃, ...) convergates to r.
The fraction (a₀, a₁, a₂, a₃, ..., a_n) is the n-th convergant of the continued fraction (a₀, a₁, a₂, a₃, ...).

For example, the first to nineth convergant of √2 = (1, [2]) are:

convergant 1 of √2 ≈ 1 / 1
convergant 2 of √2 ≈ 3 / 2
convergant 3 of √2 ≈ 7 / 5
convergant 4 of √2 ≈ 17 / 12
convergant 5 of √2 ≈ 41 / 29
convergant 6 of √2 ≈ 99 / 70
convergant 7 of √2 ≈ 239 / 169
convergant 8 of √2 ≈ 577 / 408
convergant 9 of √2 ≈ 1393 / 985

Similarly, the first to nineth convergant of √23 = (4, [1,3,1,8]) are:

convergant 1 of √23 ≈ 4 / 1
convergant 2 of √23 ≈ 5 / 1
convergant 3 of √23 ≈ 19 / 4
convergant 4 of √23 ≈ 24 / 5
convergant 5 of √23 ≈ 211 / 44
convergant 6 of √23 ≈ 235 / 49
convergant 7 of √23 ≈ 916 / 191
convergant 8 of √23 ≈ 1151 / 240
convergant 9 of √23 ≈ 10124 / 2111

Convergants of √D can be used to solve the Pell equation x² - D·y² = 1
x² - D·y² = 1 has solutions if and only if D is a quadratic surd, thus if D is not quadratic.

If the lenght of the 


Each is a solution of the Pell equation x² - 2·y² = 1:

 1² - 2·1² = -1
 3² - 2·2² = 1
 7² - 2·5² = -1
 17² - 2·12² = 1
 41² - 2·29² = -1
 99² - 2·70² = 1
 239² - 2·169² = -1
 577² - 2·408² = 1
 1393² - 2·985² = -1

 4² - 23·1² = 
 5² - 23·2² = 
 19² - 23·4² = 
 24² - 23·5² = 
 41² - 23·29² = 
 99² - 23·70² = 
 239² - 23·169² = -1
 577² - 23·408² = 1
 1393² - 23·985² = -1

# TODO: what are the solutions for x² - 2·y² = +1 instead of x² - 2·y² = -1


Created by Freek Dijkstra on 2010-07-28. Contributed to the public domain, so far as possible (most of the code is inspired by others).
"""

import math
import itertools
import sys

def quadsurdfraction(r,c,d):
    """Given the quadratic surd (quadratic irrational) (√r + c) / d, return the 
    quadratic surd of the first fraction, so that
    (√r + c) / d = a' + 1 / d', with d' = (√r + c') / d'   (with d' > 1)
    """
    b = (math.sqrt(r) + c) / d
    a1 = int(b)
    c1 = a1*d - c
    d1, remainder = divmod(r - c1*c1, d)
    assert remainder == 0
    return a1, c1, d1

def rootfractionalcycle(r):
    """Given the square root of r, return its fractional cycle.
    For example, rootfractionalcycle(7) returns (2, [1,1,1,4]).
    As the continued fraction of √7 is 2,1,1,1,4,1,1,1,4,1,1,1,4,...
    """
    c,d = 0,1
    alist = []
    cdlist = []
    while True: # assume all square roots 
        a,c,d = quadsurdfraction(r,c,d)
        # print a,c,d
        alist.append(a)
        if d == 0: # finite list
            assert len(alist) == 1
            return alist[0], []
        if len(cdlist) and (c,d) == cdlist[0]:
            # assume that the repeat always occurs at a_1.
            return alist[0], alist[1:]
        cdlist.append((c,d))

def contfractroot(r):
    """Iterate over the terms in the continued fraction of √r"""
    base,contfrac = rootfractionalcycle(r)
    yield base
    if len(contfrac):
        while True:
            for i in contfrac:
                yield i

def contfracte():
    """Iterate over the terms in the continued fraction of e"""
    yield 2
    n = 2
    while True:
        yield 1
        yield n
        yield 1
        n += 2

def convergants(contfract):
    """Given the continued fraction iterator, iterate over the convergants for this sequence."""
    # p0 =  1 a0 + 0
    # p1 = p0 a1 + 1
    # p2 = p1 a2 + p0
    # p3 = p2 a3 + p1
    # p_n = p_(n-1) * a_n + p_(n-2)
    # For p, we could simply define p_(-2) = 0, and p_(-1) = 1 and use the generic formula for all parameters.
    # 
    # q0 =  1
    # q1 =  1 a1 + 0
    # q2 = q0 a2 + q1
    # q3 = q1 a3 + q2
    # q_n = q_(n-1) * a_n + q_(n-2)
    # For q, we can NOT simply use the formula for q1, since that would yield q1 = 1 a1 + 1, which is wrong.
    # Instead, we treat q0 special, and then use q0 = 0, q_-1 = 1 for the rest of the formula.
    a = contfract.next()
    yield (a,1)
    # prefill p_(n-1), p_(n-2), q_(n-1), and q_(n-2)
    p_1 = a   # p_(n-1), for n =1: p_0
    p_2 = 1   # p_(n-2), for n =1: p_-1
    q_1 = 1   # q_(n-1), for n =1: q_0, but mockup value, so we can use the generic formula
    q_2 = 0   # q_(n-2), for n =1: q_-1
    for a in contfract:
        p = a*p_1 + p_2
        q = a*q_1 + q_2
        yield (p,q)
        p_2 = p_1; p_1 = p
        q_2 = q_1; q_1 = q

def pellsolutions(d, c=1):
    """Iterate over all solutions of the generalized Pell equation x² - D·y² = c.
    Note: this algortihm only works if |c| < √D.
    If D is square, there are no solutions
    If c = -1, there are no solutions if the periode of the continued fraction is even.
    """
    assert d >= 1, "algorithm for finding solutions x² - %d·y² = %d only works for %d > 0" % (d,c,d)
    assert c**2 < d, "algorithm for finding solutions x² - %d·y² = %d only works for |%d| < √%d" % (d,c,c,d)
    base,contfrac = rootfractionalcycle(d)
    i = 0
    maxi = 1+2*len(contfrac)
    hassolution = False
    for p,q in convergants(contfractroot(d)):
        a = p**2 - d*q**2
        if a == c:
            hassolution = True
            yield (p,q)
        if not hassolution and i == maxi:
            break  # numbers are repeating, but no solution was found. No solution will follow. break.
            # (This will yield a StopIteration)
        i += 1


def quadtraticsolutions(a,b,c,d,e,f):
    """Given the Diophantine (meaning x,y ∈ ℤ) equation
    A·x² + B·xy + C·y² + D·x + E·y + F = 0
    yield solutions x,y (in increasing order of ???)
    
    Solution based on http://www.alpertron.com.ar/METHODS.HTM
    Multiplying the equation by 4A:
    
    4A²·x² + 4AB·xy + 4AC·y² + 4AD·x + 4AE·y + 4AF = 0
    (2A·x + B·y + D)² - (B·y + D)² + 4AC·y² + 4AE·y + 4AF = 0
    (2A·x + B·y + D)² + (4AC - B²)y² + (4AE - 2BD)y + (4AF - D²) = 0
    
    Define:
    g := gcd(4AC - B², 2AE - BD).
    x₁ := 2A·x + B·y + D
    y₁ = (4AC - B²)/g·y + (2AE - BD)/g
    
    Multiplying by (4AC - B²)/g:
    
    (4AC - B²)/g·x₁² + (4AC - B²)²/g·y² + 2(4AC - B²) (2AE - BD)/g·y + (4AC - B²) (4AF - D²)/g = 0
    
    (4AC - B²)/g·x₁² + g·y₁² + (4AC - B²) (4AF - D²) - (2AE - BD)²/g = 0
    
    (4AC - B²)/g·x₁² + g·y₁² + 4A(4ACF - AE² - B²F + BDE - CD²)/g = 0
    
    where:
    
    
    """
    pass



# DEMO functions below

def printcontfractions(d, maxn=12):
    print u"√%d =" % (d),rootfractionalcycle(d)
    for i,(p,q) in enumerate(convergants(contfractroot(d))):
        if i > maxn:
            break
        print u"convergant %d of √%d ≈ %d / %d" % (i,d,p,q)
    for i,(p,q) in enumerate(convergants(contfractroot(d))):
        if i > maxn:
            break
        print u"%d² - %d·%d² = %d" % (p,d,q,p**2 - d*q**2)

def printpellsolutions(d, c=1, maxn=12):
    for i,(p,q) in enumerate(pellsolutions(d,c)):
        if i > maxn:
            break
        print u"%d² - %d·%d² = %d" % (p,d,q,c)


if __name__ == '__main__':
    print __doc__
    for d in range(2,25):
        printcontfractions(d)
    for d in range(2,25):
        printpellsolutions(d, 1)
        printpellsolutions(d, -1)
    sys.exit(0)

