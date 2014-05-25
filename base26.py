#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""base26.py

Created by Freek Dijkstra on 2010-09-21.
Copyright (c) 2010 Freek Dijkstra. No rights reserved.
License: public domain (there is no need to attribute the author, though you are welcome to do so.)

Convert a number to a alphabet-based name. E.g. A=1, B=2, ..., Z=26, AA=27, ...
"""

import unittest

def spreadshimal(n):
    """Return a number written in semi hexavigesimal (base-26), with A=1, B=2, ..., Z=26, AA=27, ..., AZ=52, BA=53, ..., ZZ=702, AAA=703, etc.
    This is how a typical spreadsheet counts the rows.
    Observe that this is not a proper base system, since that would require 26 to be written with two digits (e.g. as A0)."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    try:
        if n == 0:
            return ''
        elif n < 0:
            h = ['-']
            n = -n
        else:
            h = ['']
        while True:
            n,r = divmod(n-1,26)
            h[1:1] = alphabet[r]
            if n == 0:
                return ''.join(h)
    except TypeError:
        raise ValueError("invalid literal for spreadshimal() with (semi) base 26: %r" % n)

def hexavigesimal(n):
    """Return a number written in base-26, with A=0, B=1, C=2, ..., Z=25, BA=26, ..., BZ=51, CA=52, ..., ZZ=675, BAA=676, etc."""
    try:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if n < 0:
            h = ['-']
            n = -n
        else:
            h = ['']
        while True:
            n,r = divmod(n,26)
            h[1:1] = alphabet[r]
            if n == 0:
                return ''.join(h)
    except TypeError:
        raise ValueError("invalid literal for hexavigesimal() with base 26: %r" % n)

def heptavigesimal(n):
    """Return a number written in base-27, with 0=0, A=1, B=2, ..., Z=26, A0=27, ..., AZ=53, B0=54, ..., ZZ=728, A00=729, etc."""
    try:
        alphabet = "0ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if n < 0:
            h = ['-']
            n = -n
        else:
            h = ['']
        while True:
            n,r = divmod(n,27)
            h[1:1] = alphabet[r]
            if n == 0:
                return ''.join(h)
    except TypeError:
        raise ValueError("invalid literal for heptavigesimal() with base 27: %r" % n)

def spreadshimaltodecimal(n):
    """Interpret a string "A", "B",.., "Z", "AA", as semi hexavigesimal (base-26) notation and return the value.
    This is how a typical spreadsheet counts the rows. e.g. A=1, B=2, ..., Z=26, AA=27, ..., AZ=52, BA=53, ..., ZZ=702, AAA=703, etc.
    Observe that this is not a proper base system, since that would require 26 to be written with two digits (e.g. as A0)."""
    try:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        s = 1
        if n[0] == '-':
            n = n[1:]
            s = -1
        d = 0
        while n != "":
            d = 26*d + alphabet.index(n[0]) + 1
            n = n[1:]
        return s*d
    except TypeError:
        raise ValueError("invalid literal for spreadshimaltodecimal() with (semi) base 26: %r" % n)

def hexavigesimaltodecimal(n):
    """Interpret a string "A", "B",.., "Z", "BA", as hexavigesimal (base-26) notation and return the value.
    e.g. A=0, B=1, C=2, ..., Z=25, BA=26, ..., BZ=51, CA=52, ..., ZZ=675, BAA=676, etc."""
    try:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        s = 1
        if n[0] == '-':
            n = n[1:]
            s = -1
        d = 0
        while n != "":
            d = 26*d + alphabet.index(n[0])
            n = n[1:]
        return s*d
    except TypeError:
        raise ValueError("invalid literal for hexavigesimaltodecimal() with base 26: %r" % n)

def heptavigesimaltodecimal(n):
    """Interpret a string "A", "B",.., "Z", "BA", as heptavigesimal (base-27) notation and return the value.
    e.g. 0=0, A=1, B=2, ..., Z=26, A0=27, ..., AZ=53, B0=54, ..., ZZ=728, A00=729, etc."""
    try:
        alphabet = "0ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        s = 1
        if n[0] == '-':
            n = n[1:]
            s = -1
        d = 0
        while n != "":
            d = 27*d + alphabet.index(n[0])
            n = n[1:]
        return s*d
    except TypeError:
        raise ValueError("invalid literal for heptavigesimaltodecimal() with base 27: %r" % n)


class spreadshimalTests(unittest.TestCase):
    def testOneDigit(self):
        self.assertEquals(spreadshimal(1), "A")
        self.assertEquals(spreadshimal(2), "B")
        self.assertEquals(spreadshimal(3), "C")
        self.assertEquals(spreadshimal(26), "Z")
    def testTwoDigit(self):
        self.assertEquals(spreadshimal(27), "AA")
        self.assertEquals(spreadshimal(28), "AB")
        self.assertEquals(spreadshimal(52), "AZ")
        self.assertEquals(spreadshimal(53), "BA")
        self.assertEquals(spreadshimal(702), "ZZ")
    def testThreeDigit(self):
        self.assertEquals(spreadshimal(703), "AAA")
        self.assertEquals(spreadshimal(18278), "ZZZ")
        self.assertEquals(spreadshimal(18279), "AAAA")
    def testZero(self):
        self.assertEquals(spreadshimal(0), "")
    def testNegativeOneDigit(self):
        self.assertEquals(spreadshimal(-1), "-A")
        self.assertEquals(spreadshimal(-26), "-Z")
    def testNegativeTwoDigit(self):
        self.assertEquals(spreadshimal(-27), "-AA")
        self.assertEquals(spreadshimal(-702), "-ZZ")
    def testInvalidInput(self):
        self.assertRaises(ValueError, spreadshimal, 1.1)
        self.assertRaises(ValueError, spreadshimal, 1j)
        self.assertRaises(ValueError, spreadshimal, "A")

class hexavigesimalTests(unittest.TestCase):
    def testOneDigit(self):
        self.assertEquals(hexavigesimal(1), "B")
        self.assertEquals(hexavigesimal(2), "C")
        self.assertEquals(hexavigesimal(25), "Z")
    def testTwoDigit(self):
        self.assertEquals(hexavigesimal(26), "BA")
        self.assertEquals(hexavigesimal(27), "BB")
        self.assertEquals(hexavigesimal(51), "BZ")
        self.assertEquals(hexavigesimal(52), "CA")
        self.assertEquals(hexavigesimal(675), "ZZ")
    def testThreeDigit(self):
        self.assertEquals(hexavigesimal(676), "BAA")
        self.assertEquals(hexavigesimal(17575), "ZZZ")
        self.assertEquals(hexavigesimal(17576), "BAAA")
    def testZero(self):
        self.assertEquals(hexavigesimal(0), "A")
    def testNegativeOneDigit(self):
        self.assertEquals(hexavigesimal(-1), "-B")
        self.assertEquals(hexavigesimal(-25), "-Z")
    def testNegativeTwoDigit(self):
        self.assertEquals(hexavigesimal(-26), "-BA")
        self.assertEquals(hexavigesimal(-675), "-ZZ")
    def testInvalidInput(self):
        self.assertRaises(ValueError, hexavigesimal, 1.1)
        self.assertRaises(ValueError, hexavigesimal, 1j)
        self.assertRaises(ValueError, hexavigesimal, "A")

class heptavigesimalTests(unittest.TestCase):
    def testOneDigit(self):
        self.assertEquals(heptavigesimal(1), "A")
        self.assertEquals(heptavigesimal(2), "B")
        self.assertEquals(heptavigesimal(3), "C")
        self.assertEquals(heptavigesimal(26), "Z")
    def testTwoDigit(self):
        self.assertEquals(heptavigesimal(27), "A0")
        self.assertEquals(heptavigesimal(28), "AA")
        self.assertEquals(heptavigesimal(53), "AZ")
        self.assertEquals(heptavigesimal(54), "B0")
        self.assertEquals(heptavigesimal(728), "ZZ")
    def testThreeDigit(self):
        self.assertEquals(heptavigesimal(729), "A00")
        self.assertEquals(heptavigesimal(19682), "ZZZ")
        self.assertEquals(heptavigesimal(19683), "A000")
    def testZero(self):
        self.assertEquals(heptavigesimal(0), "0")
    def testNegativeOneDigit(self):
        self.assertEquals(heptavigesimal(-1), "-A")
        self.assertEquals(heptavigesimal(-26), "-Z")
    def testNegativeTwoDigit(self):
        self.assertEquals(heptavigesimal(-27), "-A0")
        self.assertEquals(heptavigesimal(-728), "-ZZ")
    def testInvalidInput(self):
        self.assertRaises(ValueError, heptavigesimal, 1.1)
        self.assertRaises(ValueError, heptavigesimal, 1j)
        self.assertRaises(ValueError, heptavigesimal, "A")

class spreadshimaltodecimalTests(unittest.TestCase):
    def testOneDigit(self):
        self.assertEquals(spreadshimaltodecimal("A"), 1)
        self.assertEquals(spreadshimaltodecimal("B"), 2)
        self.assertEquals(spreadshimaltodecimal("C"), 3)
        self.assertEquals(spreadshimaltodecimal("Z"), 26)
    def testTwoDigit(self):
        self.assertEquals(spreadshimaltodecimal("AA"), 27)
        self.assertEquals(spreadshimaltodecimal("AB"), 28)
        self.assertEquals(spreadshimaltodecimal("AZ"), 52)
        self.assertEquals(spreadshimaltodecimal("BA"), 53)
        self.assertEquals(spreadshimaltodecimal("ZZ"), 702)
    def testThreeDigit(self):
        self.assertEquals(spreadshimaltodecimal("AAA"), 703)
        self.assertEquals(spreadshimaltodecimal("ZZZ"), 18278)
        self.assertEquals(spreadshimaltodecimal("AAAA"), 18279)
    def testZero(self):
        self.assertEquals(spreadshimal(0), "")
    def testNegativeOneDigit(self):
        self.assertEquals(spreadshimaltodecimal("-A"), -1)
        self.assertEquals(spreadshimaltodecimal("-Z"), -26)
    def testNegativeTwoDigit(self):
        self.assertEquals(spreadshimaltodecimal("-AA"), -27)
        self.assertEquals(spreadshimaltodecimal("-ZZ"), -702)
    def testInvalidInput(self):
        self.assertRaises(ValueError, spreadshimaltodecimal, 1.1)
        self.assertRaises(ValueError, spreadshimaltodecimal, 1)
        self.assertRaises(ValueError, spreadshimaltodecimal, "1")
        self.assertRaises(ValueError, spreadshimaltodecimal, "0")

class hexavigesimaltodecimalTests(unittest.TestCase):
    def testOneDigit(self):
        self.assertEquals(hexavigesimaltodecimal("B"), 1)
        self.assertEquals(hexavigesimaltodecimal("C"), 2)
        self.assertEquals(hexavigesimaltodecimal("Z"), 25)
    def testTwoDigit(self):
        self.assertEquals(hexavigesimaltodecimal("BA"), 26)
        self.assertEquals(hexavigesimaltodecimal("BB"), 27)
        self.assertEquals(hexavigesimaltodecimal("BZ"), 51)
        self.assertEquals(hexavigesimaltodecimal("CA"), 52)
        self.assertEquals(hexavigesimaltodecimal("ZZ"), 675)
    def testThreeDigit(self):
        self.assertEquals(hexavigesimaltodecimal("BAA"), 676)
        self.assertEquals(hexavigesimaltodecimal("ZZZ"), 17575)
        self.assertEquals(hexavigesimaltodecimal("BAAA"), 17576)
    def testZero(self):
        self.assertEquals(hexavigesimaltodecimal("A"), 0)
    def testNegativeOneDigit(self):
        self.assertEquals(hexavigesimaltodecimal("-B"), -1)
        self.assertEquals(hexavigesimaltodecimal("-Z"), -25)
    def testNegativeTwoDigit(self):
        self.assertEquals(hexavigesimaltodecimal("-BA"), -26)
        self.assertEquals(hexavigesimaltodecimal("-ZZ"), -675)
    def testInvalidInput(self):
        self.assertRaises(ValueError, hexavigesimaltodecimal, 1.1)
        self.assertRaises(ValueError, hexavigesimaltodecimal, 1)
        self.assertRaises(ValueError, hexavigesimaltodecimal, "1")
        self.assertRaises(ValueError, hexavigesimaltodecimal, "0")

class heptavigesimaltodecimalTests(unittest.TestCase):
    def testOneDigit(self):
        self.assertEquals(heptavigesimaltodecimal("A"), 1)
        self.assertEquals(heptavigesimaltodecimal("B"), 2)
        self.assertEquals(heptavigesimaltodecimal("C"), 3)
        self.assertEquals(heptavigesimaltodecimal("Z"), 26)
    def testTwoDigit(self):
        self.assertEquals(heptavigesimaltodecimal("A0"), 27)
        self.assertEquals(heptavigesimaltodecimal("AA"), 28)
        self.assertEquals(heptavigesimaltodecimal("AZ"), 53)
        self.assertEquals(heptavigesimaltodecimal("B0"), 54)
        self.assertEquals(heptavigesimaltodecimal("ZZ"), 728)
    def testThreeDigit(self):
        self.assertEquals(heptavigesimaltodecimal("A00"), 729)
        self.assertEquals(heptavigesimaltodecimal("ZZZ"), 19682)
        self.assertEquals(heptavigesimaltodecimal("A000"), 19683)
    def testZero(self):
        self.assertEquals(heptavigesimaltodecimal("0"), 0)
    def testNegativeOneDigit(self):
        self.assertEquals(heptavigesimaltodecimal("-A"), -1)
        self.assertEquals(heptavigesimaltodecimal("-Z"), -26)
    def testNegativeTwoDigit(self):
        self.assertEquals(heptavigesimaltodecimal("-A0"), -27)
        self.assertEquals(heptavigesimaltodecimal("-ZZ"), -728)
    def testInvalidInput(self):
        self.assertRaises(ValueError, heptavigesimaltodecimal, 1.1)
        self.assertRaises(ValueError, heptavigesimaltodecimal, 1)
        self.assertRaises(ValueError, heptavigesimaltodecimal, "1")



if __name__ == '__main__':
    unittest.main()