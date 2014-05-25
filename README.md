Puzzle Code
===========

Miscellaneous Python code for solving diverse puzzles.

This code was writen to solve programming puzzles, such as those published by 
Project Euler (www.projecteuler.net) or CheckIO (www.checkio.org). It does not 
give solutions for individual puzzles, but does provide some re-usable code 
that may make it easier to solve these puzzles.

puzzle.py
---------

Generic Puzzle Solving Framework

A breadth-first search that iterates over all states of a puzzle.

Based on Raymond Hettinger's short library 
(http://users.rcn.com/python/download/python.htm)

pathfind.py
-----------

Implementation of the following path finding algorithms:
* Dijkstra: the path finding algorithm by Edsgar W. Dijkstra
* Astar (A*): Dijkstra with distance lower boundary to increase speed
* Bellman–Ford: Dijkstra with support for negative weigth edges)
* Breadth-First Search (= Dijkstra on an unweighted graph with a FIFO queue)
* Depth-First Search (= Dijkstra on an unweighted graph with a LIFO queue)
* Bhandari: edge disjoint pathfinding (find multiple paths)
* Suurballe: node disjoint pathfinding (find multiple paths)

primes.py
---------

Helper function to calculate prime numbers and divisors.

contfract.py
------------

Helper function to calculate continued fractions.

Continued fractions are useful for solving the Pell equation: x² - D·y² = ±1


sudoku.py
---------

Solver for Sudoku and Sudoku-like puzzles (e.g. with diagonals, or 6x6 frames).
It deploys 6 strategies roughly in the same way a human would use, so it is well 
suited for getting hints.

base26.py
---------

Not-so-serious code to generate hexavigesimal (base-26), heptavigesimal 
(base-27), and semi hexavigesimal (what I coined spreadshimal, since it 
is used in spreadsheets) numbering systems.


License
=======

The code in this repository is contributed to the public domain. 
You may modify or redistribute it in any way you see fit. Any acknowledgements 
to the author(s) is appreciated, but not required. All code is provided as-is, 
without any guarantee as to proper operations or fitness for a particular purpose.
