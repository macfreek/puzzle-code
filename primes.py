#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""primes.py
Helper function to calculate prime numbers.

Created by Freek Dijkstra on 2008-11-06. Contributed to the public domain, so far as possible (most of the code is inspired by others).
"""

import math
import itertools
import sys

def fastprimes(max = None):
    """Find all prime numbers, or all prime numbers bellow a certain threshold.
    Uses an moderately fast version of the Sieve of Erathosthenes.
    Take from 'Computing Prime Numbers' in the Python Cookbook.
    Credit: David Eppstein, Tim Peters, Alex Martelli, Wim Stolker, Kazuo Moriwaka, Hallvard Furuseth, Pierre Denis, Tobias Klausmann, David Leem Raymond Hettinger.
    """
    D = {}  # map each composite integer to its first-found prime factor
    if max and max < 2:
        raise StopIteration
    yield 2
    if max:
        max -= 2
    for q in itertools.islice(itertools.count(3), 0, max, 2):  # loop odd numbers 3, 5, 7, 9, 11, ...
        p = D.pop(q, None)
        if p is None:
            # q is not a key in D, so q is prime, therefore, yield it
            yield q
            # mark q squared as not-prime, with q as first-found prime factor
            D[q*q] = 2*q  # store 2*p instead of p, since we only use 2*p for calculations later on.
        else:
            # let x <- smallest (N*p)+q which wasn't yet known to be composite
            # we just learned x is composite, with p first-found prime factor,
            # since p is the first-found prime factor of q -- find and mark it.
            # since p and q are always odd, we only need to increase by 2*p. That is what we stored in D.
            x = q + p
            while x in D:
                x += p
            D[x] = p

def primelist(max): 
    """Returns a list of prime numbers from 2 to < n using a sieve algorithm. 
    Code taken from http://code.activestate.com/recipes/366178/. 
    This code is very fast if you require a list of primes up to a maximum value;
    it is not a generator that yields indefinitely.
    """
    if max == 2: return [2]
    elif max < 2: return []
    try:
        s = range(3, max+1, 2)
    except OverflowError,e:
        print e
        raise OverflowError("primelist: max %d is too large" % max)
    mroot = int(max ** 0.5)  # n**0.5 may be slightly faster than math.sqrt(n)
    half = (max+1)//2 - 1
    i = 0
    m = 3
    while m <= mroot:
        if s[i]:
            j = (m*m-3) // 2  # double slash means: round down to int
            s[j] = 0
            while j < half:
                s[j] = 0
                j += m
        i = i+1
        m = 2*i+3
    return [2] + [x for x in s if x]


def factorize(num):
    """Return an ordered list of prime factors of number num."""
    factors = []
    assert num > 0
    maxroot = int(math.sqrt(num))
    for p in fastprimes(max = maxroot):
        while num % p == 0:  # num is dividable by p
            factors.append(p)
            num = int(num / p)
        if num == 1:
            break
    if num > 1:
        factors.append(num)
    return factors

def uniquefactors(num):
    """Return an ordered list of prime factors with exponent of number num."""
    factors = []
    assert num > 0
    maxroot = int(math.sqrt(num))
    for p in primelist(max = maxroot):
        count = 0
        while num % p == 0:  # num is dividable by p
            count += 1
            num = int(num / p)
        if count:
            factors.append((p, count))
        if num == 1:
            break
    if num > 1:
        factors.append((num,1))
    return factors

def phi(n):
    """Return φ(n), the Euler totient of n, the number of integers < n that are relative prime to n."""
    result = 1
    for factor,power in uniquefactors(n):
        result *= (factor - 1) * factor**(power-1)
    return result

def divisors(num):
    """Return a list of all divisors of num, numbers that evenly divide num without leaving a remainder. Divisors are also called factors, and do not need to be prime.
    """
    factors = []
    for j in range(1,1+int(math.sqrt(num))):
        if num % j == 0:
            factors.append(j)
            high = num//j
            if high != j:  # happens only if num is a square.
                factors.append(high)
    return sorted(factors)

def divisors_min_max(num, mindiv = None, maxdiv = None):
    """Iterate over all divisors d of num which satisfy min ≤ d ≤ max. Divisors are numbers that evenly divide num without leaving a remainder. Divisors are also called factors, and do not need to be prime.
    """
    if mindiv == None:
        mindiv = 1
    if maxdiv == None:
        maxdiv = num
    start = min(mindiv, num//maxdiv)
    half = min(max(maxdiv, num//mindiv), int(sqrt(num)))
    factors = []
    for j in range(start,1+half):
        if num % j == 0:
            if mindiv <= j <= maxdiv:
                yield j
            high = num//j
            if high != j and mindiv <= high <= maxdiv:
                factors.append(high)
    while len(factors) > 0:
        yield factors.pop()

def unorderedfactorizations(num, min=None):
    """Given a number num, iterate over all possible unordered factorizations of num. 
    That is, all sets with items > 1 whose product is equal to num. 
    Unordered factorization is also known as Multiplicative partition or Factorisatio Numerorum.
    For example, unorderedfactorizations(24) yields [2, 2, 2, 3], [2, 2, 6], [2, 3, 4], [2, 12], [3, 8], [4, 6], and [24]
    By convention, the only Unordered Factorization of 1 is [1].
    See: http://mathworld.wolfram.com/UnorderedFactorization.html
    https://en.wikipedia.org/wiki/Multiplicative_partition
    http://www.mathematica-journal.com/issue/v10i1/contents/Factorizations/Factorizations_3.html
    """
    if min == None:
        if num == 1:
            yield [1]
        min = 2
    for d in divisors_min_max(num, min, num):
        if d == num:
            yield [d]
        else:
            for uf in unorderedfactorizations(num//d, d):
                yield [d] + uf

def divisors2(num):
    """Alternative to divisors(). Both functions are roughly as fast, so I prefer the 
    less complex one (divisors())
    Return a list of all divisors of num, numbers that evenly divide num without leaving a remainder. Divisors are also called factors, and do not need to be prime.
    """
    factors = uniquefactors(num)
    nfactors = len(factors)
    f = [0] * nfactors
    while True:
        yield reduce(lambda x, y: x*y, [factors[x][0]**f[x] for x in range(nfactors)], 1)
        i = 0
        while True:
            f[i] += 1
            if f[i] <= factors[i][1]:
                break
            f[i] = 0
            i += 1
            if i >= nfactors:
                return


def divisors3(num):
    """Alternative to divisors(). Both functions are roughly as fast, so I prefer the 
    less complex one (divisors())
    Return a list of all divisors of num, numbers that evenly divide num without leaving a remainder. Divisors are also called factors, and do not need to be prime.
    """
    primes = primelist(int(math.sqrt(num)))
    
    # int sum, lastsum, ip, p;
    n = num
    sum = 1;
    ip = 0
    while True:
        p = primes[ip]
        if( p*p>n ):
            break;
        lastsum = sum;
        while( n%p==0 ):
            n /= p;
            sum = sum*p + lastsum;
        ip += 1
    if( n>1 ):
        sum *= (n+1);
    return sum-num;


def numdivisors(num):
    """Return the amount of divisors of num, numbers that evenly divide num without leaving a remainder. Divisors are also called factors, and do not need to be prime.
    """
    total = 1
    for factor, count in uniquefactors(num):
        total *= (count+1)
    return total


def isPrime(num, cache={1:False, 2:True, 3:True, 4:False, 5:True, 6:False, 7:True, 8:False, 9:False, 10:False, 11:True, 12:False, 13:True}):
    """Not so fast method to check if an integer is prime.
    1 is not a prime. 
    All primes except 2 are odd. 
    All primes greater than 3 can be written in the form  6k+/-1. 
    Any number n can have only one primefactor greater than n. 
    The consequence for primality testing of a number n is: if we cannot find a number less than 
    or equal n that divides n then n is prime: the only primefactor of n is n itself"""
    if num in cache:
        return cache[num]
    elif not (num & 1):
        return False    # no even numbers
    elif num < 2:
        return False
    elif num % 3 == 0:
        return False
    else:
        maxroot = int(math.sqrt(num))
        f = 5
        while f <= maxroot:
            if num % f == 0:
                return False
            if num % (f+2) == 0:
                return False
            f += 6
    return True


def gcd(num1, num2):
    """Return the greatest common denominator of num1 and num2, using the Euclidian algorithm, which uses the fact that gcd(a,b) = gcd(a-b,b)."""
    # make sure num1 >= num2 throughout the calculation
    if num2 > num1:
        num1, num2 = num2, num1
    while num2 != 0:
        num1, num2 = num2, num1 % num2
    return num1

# from fractions import gcd

def slowgcd(num1, num2):
    """Return the greatest common denominator of num1 and num2, by explicitly factorizing each number."""
    fact1 = factorize(num1)
    fact2 = factorize(num2)
    denom = []
    for f in fact1[:]:
        if f in fact2:
            fact1.remove(f)
            fact2.remove(f)
            denom.append(f)
    return reduce(lambda x,y: x*y, denom)


