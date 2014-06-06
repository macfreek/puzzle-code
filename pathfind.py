#!/usr/bin/env python3.3
# -*- coding: utf-8 -*-

"""Implementation of the following path finding algorithms:
* Dijkstra
* Astar (A*) Dijkstra with distance lower boundary (for speed)
* Bellman–Ford (actually Dijkstra with support for negative weigth edges)
* Breadth-First Search (= Dijkstra on an unweighted graph with a FIFO queue)
* Depth-First Search (= Dijkstra on an unweighted graph with a LIFO queue)
* Bhandari: edge disjoint pathfinding (find multiple paths)
* Suurballe: node disjoint pathfinding (find multiple paths)
"""

"""
                queue       stop        sort
default         LIFO        first       yes
Dijkstra        LIFO        first       yes
Astar           LIFO        first       yes
BellmanFord     LIFO        all         yes
BFS             FIFO        first       no
DFS             LIFO        first       no
"""

"""
The algorithm used here is originally developed by J.W. Suurballe.
Please note that the information on Wikipedia, 
https://en.wikipedia.org/wiki/Suurballe%27s_algorithm, is incorrect: 
the algorithm described there describes a simplified variant, as published by 
Ramesh Bhandari. This finds multiple *edge* disjoint paths. Thus paths that 
do not share any edge. For this problem we need to find multiple *node* 
disjoint paths. This stricter requirement forces us to use a more complex 
algorithm. The algorithm used here is based on an improved to Suurballe's 
algorithm by R.E. Tarjan. Unlike Suurballe-Tarjan, it does not modify the 
graph, but instead modifies the neighbour detection part of the algorithm and 
selectively leave out edges or insert special edge objects: either an 
Inverse Edge (which annuls an edge that is already part of the graph) or a 
Double Edge (which is two edge in sequence, which enforces that a specific 
edge is taken depending on the previous edge).

Changes to the described algorithm:
* both disjoint edges and disjoint nodes, by keeping track of used edges and nodes.
* use A* instead of Dijkstra's algorithm.
"""

from collections import UserList
from itertools import chain

class Edge(object):
    """An edge is a unidirectional link between two nodes in a graph."""
    def __init__(self, source, destination, ref=None, weight=1):
        self.source = source
        self.destination = destination
        self.ref = ref
        self.weight = weight
    def __str__(self):
        if self.weight == 1:
            return "%s(%s, %s, %r)" % (self.__class__.__name__, \
                str(self.source), str(self.destination), self.ref)
        else:
            return "%s(%s, %s, %r, %r)" % (self.__class__.__name__, \
                str(self.source), str(self.destination), self.ref, self.weight)
    __repr__ = __str__

class Node(object):
    """A node (or vertex) in a graph."""
    def __init__(self, ref=None, weight=0, edges=[]):
        self.ref = ref
        self.weight = weight
        self.edges = edges[:]
    def add_edge(self, neighbour, ref=None, weight=1):
        edge = Edge(self, neighbour, ref, weight)
        self.edges.append(edge)
        return edge
    def add_bidirectional_edge(self, neighbour, ref=None, weight=1):
        edge1 = self.add_edge(neighbour, ref, weight)
        edge2 = neighbour.add_edge(self, ref, weight)
        return (edge1,edge2)
    def neigbours(self):
        return [edge.destination for edge in self.edges]
    def __str__(self):
        if self.weight:
            return "%s(%r, %r)" % (self.__class__.__name__, self.ref, self.weight)
        else:
            return "%s(%r)" % (self.__class__.__name__, self.ref)
    __repr__ = __str__

class Graph(UserList):
    """A directed graph is a list of nodes, which have associated edges."""
    def __init__(self):
        UserList.__init__(self)
        self._noderefs = {}
    def add_node(self, ref=None, weight=0):
        n = Node(ref=ref, weight=weight)
        if ref != None:
            self._noderefs[ref] = n
        self.append(n)
        return n
    def get_node(self, ref):
        return self._noderefs[ref]
    # __getitem__ = get_node
    def nodes(self):
        return self
    def edges(self):
        edges = []
        for node in self:
            edges.extend(node.edges)
        return edges
    def copy(self):
        """Return a copy of the graph, with other node and edge objects."""
        g = Graph()
        nodes = {node: g.add_node(node.ref, node.weight) for node in self}
        for oldnode, newnode in nodes.items():
            for oldedge in oldnode.edges:
                newneighbour = nodes[oldedge.destination]
                newnode.add_edge(newneighbour, oldedge.ref, oldedge.weight)
        return g

class NoPath(Exception):
    """Raised if not path exists between a given source and destination"""
    def __init__(self, source, destination, k=None):
        self.source = source
        self.destination = destination
        self.k = k
    def __str__(self):
        if self.k:
            return "No %d paths exist between %s and %s." % \
                    (self.k, self.source, self.destination)
        else:
            return "No path exists between %s and %s." % \
                    (self.source, self.destination)

class _InverseEdge(Edge):
    """An inverse edge annuls a forward edge from s to d, and behaves as a 
    regular edge from d to s with negative weight. It is used for Bhandari's
    and Suurballe's algorithms."""
    def __init__(self, edge):
        self.edge = edge
        self.source = edge.destination
        self.destination = edge.source
        self.ref = edge.ref
        self.weight = -edge.weight
    def __str__(self):
        return "%s(%s, %s, %r, %r)" % (self.__class__.__name__, \
            str(self.source), str(self.destination), self.ref, self.weight)

class _DoubleEdge(Edge):
    """A double edge behaves as tow consecutive edges.
    It is used for Suurballe's algorithm."""
    def __init__(self, edge1, edge2):
        self.edge1 = edge1
        self.edge2 = edge2
        assert edge1.destination == edge2.source
        self.source = edge1.source
        self.destination = edge2.destination
        self.ref = edge1.ref
        self.weight = edge1.weight + edge2.weight
    def __str__(self):
        return "%s(%s, %s, %r, %r)" % (self.__class__.__name__, \
            str(self.source), str(self.destination), self.ref, self.weight)

class PathFinder(object):
    """Implmentation of the A* shortest path finding algorithm. 
    This is a variant of Edsgar W. Dijkstra's shortest path algorithm, with 
    a heuristic based on the mimimum distance between two points."""
    debug = 0  # 0...5
    LIFO = -1  # constant: last in first out
    FIFO = 0   # constant: first in first out
    queue_type = LIFO
    stop_first_answer = True # Set to False for negative weights
    sort_queue = True # Set to False if the tree can be looped in any order
    def __init__(self, graph, start=None, destination=None, \
                 heurist_lower_boundary=None, debug=0):
        self.graph = graph      # list of all nodes
        self.path = None        # list of edges in the shortest path
        self.hops = None        # list of node in the shortest path
        self.cost = None        # cost of the shortest path
        self.iterations = 0
        if heurist_lower_boundary:
            self.heurist_lower_boundary = heurist_lower_boundary
        self.debug = debug
        if start and destination:
            self.solve(start, destination)
    def heurist_lower_boundary(self, node1, node2):
        """heurist_lower_boundary returns a lower boundary of the distance
        between node1 and node2. In case this function always returns 0, the 
        A* algorithm is the same as the Dijkstra algorithm.
        """
        return 0
    def solve(self, start, destination):
        """Calculate a shortest path"""
        self.create_tree(start, destination)
        if destination not in self._prev:
            raise NoPath(start, destination)
        self.trace_path(destination)
    def initialise_path_find(self, start, destination=None):
        self._prev = {start: None}
        """self._prev[node]: previous node for minimum cost path"""
        self._mincost = {start: start.weight}
        """self._mincost[node]: minumum cost from start to 'node'"""
        self._minpathcost = {start: start.weight + \
                self.heurist_lower_boundary(start, destination)}
    def _get_edges(self, node):
        return node.edges
    def _add_to_queue(self, queue, node, cost, trace, destination):
        """Add node to the queue with given <cost> from start to the node.
        trace is the edge that has been followed"""
        self._mincost[node] = cost
        self._minpathcost[node] = cost + \
                 self.heurist_lower_boundary(node, destination)
        self._prev[node] = trace
        if self.debug > 2:
            print("  append %s with cost: %d" % (node, cost))
        # Do not reinsert if it is already in the queue!
        if node not in queue:
            queue.append(node)
    def _better_path(self, node, cost):
        try:
            curcost = self._mincost[node]
        except KeyError:
            return True
        if self.debug > 4 and cost >= curcost:
            print("  skip %s (cost %d >= %d)" % (node, cost, curcost))
        return cost < curcost
    def create_tree(self, start, destination=None):
        """Calculate a shortest path"""
        if self.debug > 0:
            if destination:
                print("Find a path", start, "-->", destination)
            else:
                print("Find a tree from", start)
        self.initialise_path_find(start, destination)
        queue = [start]
        while queue:
            self.iterations += 1
            if self.sort_queue:
                queue.sort(key = lambda n: self._minpathcost[n], reverse=True)
            if self.debug > 3:
                print("queue:",queue)
            try:
                node = queue.pop(self.queue_type)
            except IndexError: # queue is empty
                break
            curcost = self._mincost[node]
            if self.debug > 1:
                print("iteration %d: pop node %s cost: %s" % \
                        (self.iterations, node, curcost))
            # Original Dijkstra algorithm stops at the first answer.
            # Continue to support negative weights
            if self.stop_first_answer and node == destination:
                break
            # assert curcost > -5
            
            for edge in self._get_edges(node):
                neighbour = edge.destination
                totalcost = curcost + edge.weight + neighbour.weight
                if not self._better_path(neighbour, totalcost):
                    continue
                self._add_to_queue(queue, neighbour, totalcost, edge, destination)
    def trace_path(self, destination):
        # path is a list of edges
        # hops is a list of nodes
        try:
            self.cost = self._mincost[destination]
            edge = self._prev[destination]
        except KeyError:
            raise NoPath(None, destination)
        self.path = []
        self.hops = [destination]
        while edge != None:
            self.path = [edge] + self.path
            self.hops = [edge.source] + self.hops
            edge = self._prev[edge.source]

class BreadthFirstSearch(PathFinder):
    queue_type = PathFinder.FIFO
    sort_queue = False

class DepthFirstSearch(PathFinder):
    queue_type = PathFinder.LIFO
    sort_queue = False

class Dijkstra(PathFinder):
    stop_first_answer = True
    sort_queue = True

class BellmanFord(PathFinder):
    queue_type = PathFinder.LIFO
    stop_first_answer = False # Support for negative weights

class AStar(PathFinder):
    queue_type = PathFinder.LIFO
    stop_first_answer = True
    sort_queue = True

# TODO: implement variant as described on https://en.wikipedia.org/wiki/Suurballe%27s_algorithm (which is faster as it may use Dijkstra instead of Bellman-Ford the second path find)

class Bhandari(PathFinder):
    """Implmentation of the Bhandari edge disjoint path finding algorithm. 
    This algorithm finds <k> different, edge disjoint path."""
    stop_first_answer = False
    def __init__(self, graph, start=None, destination=None, k=2, \
                 heurist_lower_boundary=None, debug=0):
        self.graph = graph      # list of nodes
        self.path = []          # list of all found shortest paths
        self.hops = []          # list of hops in each shortest path
        self.cost = []          # list of the cost of each shortest path
        self.iterations = 0
        if heurist_lower_boundary:
            self.heurist_lower_boundary = heurist_lower_boundary
        self.debug = debug
        if start and destination:
            self.solve(start, destination, k)
    def solve(self, start, destination, k=2):
        """Calculate a shortest path"""
        _orig_stop_first_answer = self.stop_first_answer
        for c in range(k):
            self.create_tree(start, destination)
            if destination not in self._prev:
                self.stop_first_answer = _orig_stop_first_answer # reset to original value
                raise NoPath(start, destination, k)
            self.trace_path(destination)
            self.untangle_paths()
            self.stop_first_answer = False # required for negative weights
        self.stop_first_answer = _orig_stop_first_answer # reset to original value
    def initialise_path_find(self, start, destination=None):
        self._prev = {start: None}
        """self._prev[node]: previous node for minimum cost path"""
        self._mincost = {start: start.weight}
        """self._mincost[node]: minumum cost from start to 'node'"""
        self._minpathcost = {start: start.weight + \
                self.heurist_lower_boundary(start, destination)}
        """self._minpathcost[node]: lower boundary of cost from start via 
        'node' to destination"""
        self._forward_edges = set(chain(*self.path))
        """Edges used in previous found shortest paths"""
        self._inverse_edges = {}
        """Inverse of the edges in _forward_edges"""
        for k, path in enumerate(self.path):
            for i, edge in enumerate(path):
                hop = edge.destination
                if hop == destination:
                    # Suurballe prevents hops from occuring in multiple paths.
                    # However, the destination (and source) are exempt from
                    # this requirement (they obviously occur in all paths.)
                    # So don't include the destination in _inverse_edges.
                    continue
                assert hop not in self._inverse_edges
                self._inverse_edges[hop] = _InverseEdge(edge)
    def _get_edges(self, node):
        # Both:
        # remove edges in self.path
        # add inverse edges for edges in self.path
        # TODO: shouldn't the cost of the node also be taken into account?
        for edge in node.edges:
            if edge not in self._forward_edges:
                yield edge
            elif self.debug > 4:
                print("  skip edge already in use", edge)
        if self.debug > 4 and node in self._inverse_edges:
            print("  add inverse edge", self._inverse_edges[node])
        try:
            yield self._inverse_edges[node]
        except KeyError:
            pass
    def _path_edge_index(self, edge):
        """Given an edge, return the indexes (k, i) for the path and location 
        in that path where this edge is located. 
        Raises ValueError if the edge can't be found."""
        for k, path in enumerate(self.path):
            try:
                i = path.index(edge)
            except ValueError:
                continue
            else:
                return k,i
        raise ValueError("edge %s not part of any path" % edge)
    def _update_hops(self, k):
        self.hops[k] = [self.path[k][0].source] + \
                       [e.destination for e in self.path[k]]
        self.cost[k] = sum(e.weight for e in self.path[k]) + \
                       sum(n.weight for n in self.hops[k])
    def trace_path(self, destination):
        """Trace a path from the destination back to start."""
        # path is a list of edges
        # hops is a list of nodes
        try:
            edge = self._prev[destination]
        except KeyError:
            raise NoPath(None, destination)
        path = []
        while edge != None:
            assert edge not in path
            if isinstance(edge, _DoubleEdge):
                path = [edge.edge1, edge.edge2] + path
            else:
                path = [edge] + path
            edge = self._prev[edge.source]
        self.path.append(path)
        self.hops.append(None)
        self.cost.append(None)
        if self.debug > 3:
            self._update_hops(-1)
            print("Found (raw) path:", self.hops[-1])
    def untangle_paths(self):
        """Untangle path by eliminating any occurance of _InverseEdge()
        in the last found path. This may change multiple paths."""
        k = len(self.path)-1 # path to check for InverseEdges..
        dirty_paths = set([k])
        path = self.path[k]
        for i in range(len(path)-1, -1, -1):
            edge = path[i]
            if isinstance(edge, _InverseEdge):
                # Don't store in which path the forward edge is located
                # in the _InverseEdge(), since it changes with each untangle.
                l,j = self._path_edge_index(edge.edge)
                if self.debug > 3:
                    print("Untangle paths %d and %d at %s" % \
                            (l, k, edge.edge))
                dirty_paths.add(l)
                # somehow the trick a,b = b,a did not work.
                # Note: this also works if k == l.
                _path = self.path[k][:i] + self.path[l][j+1:]
                self.path[l] = self.path[l][:j] + self.path[k][i+1:]
                self.path[k] = _path
        for l in dirty_paths:
            self._update_hops(l)
        if self.debug > 0:
            for l in sorted(dirty_paths - {k}):
                print("Reroute path %d: %s" % (l, self.hops[l]))
            print("Found path %d: %s" % (k, self.hops[k]))

class Suurballe(Bhandari):
    """Implmentation of the Suurballe node disjoint path finding algorithm. 
    This algorithm finds <k> different, node disjoint path."""
    def _add_to_queue(self, queue, node, cost, trace, destination):
        """Add node to the queue with given <cost> from start to the node.
        trace is the edge that has been followed"""
        if not isinstance(trace, _InverseEdge) and node in self._inverse_edges:
            # Suurballe specific: whenever a node in a current path in the tree,
            # make sure it is followed by a InverseEdge, so thst the node will
            # be eliminated from either one of the paths during untangelment.
            assert node != destination
            edge2 = self._inverse_edges[node]
            if self.debug > 4:
                print("  edge %s must be followed by %s" % (trace, edge2))
            node = edge2.destination
            cost += edge2.weight + node.weight
            trace = _DoubleEdge(trace, edge2)
            if not self._better_path(node, cost):
                return None
        self._mincost[node] = cost
        self._minpathcost[node] = cost + \
                 self.heurist_lower_boundary(node, destination)
        self._prev[node] = trace
        if self.debug > 2:
            print("  append %s with cost: %d" % (node, cost))
        # Do not reinsert if it is already in the queue!
        if node not in queue:
            queue.append(node)


if __name__ == '__main__':
    import unittest
    
    def five_by_five():
        """Create a graph with 5x5 nodes arranged in a square matrix."""
        graph = Graph()
        # create nodes
        for i in range(5):
            for j in range(5):
                node = graph.add_node((i, j))
                try:
                    north = graph.get_node((i-1, j))
                    node.add_edge(north, "N", 1)
                    north.add_edge(node, "S", 1)
                except KeyError:
                    pass
                try:
                    west = graph.get_node((i, j-1))
                    node.add_edge(west, "W", 1)
                    west.add_edge(node, "E", 1)
                except KeyError:
                    pass
        start = graph.get_node((0,2))
        destination = graph.get_node((4,2))
        return graph, start, destination

    def planar_coord_distance(node1, node2):
        """Heuristic method that returns a lower boundary of the distance
        between node1 and node2."""
        return abs(node1.ref[0] - node2.ref[0]) + abs(node1.ref[1] - node2.ref[1])

    def two_paths(ef_weight=1, cd_weight=1, df_weight=1):
        """Create a graph with two disjoint paths between start A and destination H.
          B--C
         /    \
        A--E---D--H
            \ /  /
             F--G
        """
        graph = Graph()
        # create nodes
        a = graph.add_node('A')
        b = graph.add_node('B')
        c = graph.add_node('C')
        d = graph.add_node('D')
        e = graph.add_node('E')
        f = graph.add_node('F')
        g = graph.add_node('G')
        h = graph.add_node('H')
        # create edges
        a.add_bidirectional_edge(b, 'AB', weight=1)
        a.add_bidirectional_edge(e, 'AE', weight=1)
        b.add_bidirectional_edge(c, 'BC', weight=1)
        # dynamic weight, to test edge versus node-disjoint solutions.
        if cd_weight < 0:
            # make sure there is no cycle with negative cost.
            c.add_edge(d, 'CD', weight=cd_weight)
            d.add_edge(c, 'DC', weight=-cd_weight)
        else:
            c.add_bidirectional_edge(d, 'CD', weight=cd_weight)
        d.add_bidirectional_edge(e, 'DE', weight=1)
        if df_weight < 0:
            d.add_edge(f, 'DF', weight=df_weight)
            f.add_edge(d, 'FD', weight=-df_weight)
        else:
            d.add_bidirectional_edge(f, 'DF', weight=df_weight)
        d.add_bidirectional_edge(h, 'DH', weight=1)
        if ef_weight < 0:
            e.add_edge(f, 'EF', weight=ef_weight)
            f.add_edge(e, 'FE', weight=-ef_weight)
        else:
            e.add_bidirectional_edge(f, 'EF', weight=ef_weight)
        f.add_bidirectional_edge(g, 'FG', weight=1)
        g.add_bidirectional_edge(h, 'GH', weight=1)
        return graph, a, h
    def two_intertwined_paths():
        """Create a graph with two disjoint paths between start A and destination P.
          B---C       M---N---O
         /     \     /         \ 
        A---E---D---L---K---J---P
             \             /
              F---G---H---I
        """
        graph = Graph()
        # create nodes
        for n in 'ABCDEFGHIJKLMNOP':
            graph.add_node(n)
        for n,m in ('AB', 'AE', 'BC', 'CD', 'DE', 'DL', 'EF', 'FG', 'GH', 'HI', \
                  'IJ', 'JK', 'JP', 'KL', 'LM', 'MN', 'NO', 'OP'):
            graph.get_node(n).add_bidirectional_edge(graph.get_node(m), n+m)
        return graph, graph.get_node('A'), graph.get_node('P')


    class GraphProperties(unittest.TestCase):
        def testGraph1(self):
            g, s, d = five_by_five()
            self.assertEqual(len(g), 25)
            self.assertEqual(len(g.nodes()), 25)
            self.assertEqual(len(g.edges()), 80) # 40 undirected = 80 directed

    class GraphCopy(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.g, s, d = five_by_five()
        def setUp(self):
            self.c = self.g.copy()
        def testNewGraphObject(self):
            g, c = self.g, self.c
            self.assertNotEqual(id(g), id(c))
            self.assertNotEqual(id(g.nodes()), id(c.nodes()))
            # explicitly keep both edge structures in memory
            ge = g.edges()
            ce = c.edges()
            self.assertNotEqual(id(ge), id(ce))
            # The following statement failed, becuase the one structure was released
            # before the other was created, and they occupied the same memory location!
            # self.assertNotEqual(id(g.edges()), id(c.edges()))
        def testEqualProperty(self):
            g, c = self.g, self.c
            self.assertEqual(len(g.nodes()), len(c.nodes()))
            self.assertEqual(len(g.edges()), len(c.edges()))
        def testGetNode(self):
            g, c = self.g, self.c
            node = g[0] # just a random note
            try:
                node = c.get_node(node.ref)
            except KeyError as e:
                raise AssertionError() from e
        def testNodesCopied(self):
            g, c = self.g, self.c
            gid = [id(n) for n in g]
            for n in c:
                self.assertNotIn(id(n), gid)
        def testSameNodeRefs(self):
            g, c = self.g, self.c
            g_refs = [n.ref for n in g]
            c_refs = [n.ref for n in c]
            self.assertCountEqual(g_refs, c_refs)
        def testEdgesCopied(self):
            g, c = self.g, self.c
            gid = [id(e) for e in g.edges()]
            for e in c.edges():
                self.assertNotIn(id(e), gid)
        def testSameEdgeRefs(self):
            g, c = self.g, self.c
            g_refs = [e.ref for e in g.edges()]
            c_refs = [e.ref for e in c.edges()]
            self.assertCountEqual(g_refs, c_refs)
            

    class PathFindTests(unittest.TestCase):
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = PathFinder(g, s, d)
            self.assertEqual(a.hops[0], s)
            self.assertEqual(a.hops[-1], d)
            self.assertEqual(len(a.path), a.cost)
            self.assertEqual(len(a.hops), a.cost + 1)
            for i, n in enumerate(a.hops[1:-1]):
                self.assertEqual(a.path[i].destination, n)
                self.assertEqual(a.path[i+1].source, n)
        def test_two_paths(self):
            g, s, d = two_paths()
            a = PathFinder(g, s, d)
            self.assertEqual(a.hops[0], s)
            self.assertEqual(a.hops[-1], d)
            self.assertEqual(len(a.path), a.cost)
            self.assertEqual(len(a.hops), a.cost + 1)
            for i, n in enumerate(a.hops[1:-1]):
                self.assertEqual(a.path[i].destination, n)
                self.assertEqual(a.path[i+1].source, n)
        def test_node_cost(self):
            g = Graph()
            s = g.add_node('S', weight = 1)
            d = g.add_node('D', weight = 1)
            e = s.add_edge(d, weight = 2)
            a = PathFinder(g, s, d)
            self.assertEqual(a.path, [e])
            self.assertEqual(a.hops, [s, d])
            self.assertEqual(a.cost, 4)
        def test_one_node(self):
            g = Graph()
            s = g.add_node('S')
            a = PathFinder(g, s, s)
            self.assertEqual(a.path, [])
            self.assertEqual(a.hops, [s])
            self.assertEqual(a.cost, 0)

    class BreadthFirstSearchTests(unittest.TestCase):
        # Note: same as Dijkstra if edge cost is always 1.
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = BreadthFirstSearch(g, s, d)
            self.assertEqual(''.join(e.ref for e in a.path), 'SSSS')
            self.assertEqual([n.ref for n in a.hops], [(0,2), (1,2), (2,2), (3,2), (4,2)])
            self.assertEqual(a.cost, 4)
            self.assertGreaterEqual(a.iterations, 15)
            self.assertLessEqual(a.iterations, 19)
        def test_two_paths(self):
            g, s, d = two_paths(ef_weight = 2)
            a = BreadthFirstSearch(g, s, d)
            self.assertEqual(''.join(n.ref for n in a.hops), 'AEDH')
            self.assertEqual(a.cost, 3)
            # BFS should ignore weight, otherwise it only takes 6 iterations.
            self.assertGreaterEqual(a.iterations, 7)
            self.assertLessEqual(a.iterations, 8)

    class DepthFirstSearchTests(unittest.TestCase):
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = DepthFirstSearch(g, s, d)
            # Answer could be more or less anything. Just check utter basics.
            self.assertGreaterEqual(a.cost, 4)
            self.assertLessEqual(a.iterations, 25)
        def test_two_paths(self):
            g, s, d = two_paths(ef_weight = 2)
            a = DepthFirstSearch(g, s, d)
            # Answer could be more or less anything
            self.assertIn(''.join(n.ref for n in a.hops), ('AEDH', 'ABCDH', \
                            'AEFGH', 'AEFDH', 'AEDFGH', 'ABCDFGH', 'ABCDEFGH'))
            self.assertGreaterEqual(a.cost, 3)
            self.assertLessEqual(a.iterations, 8)

    class DijkstraTests(unittest.TestCase):
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = Dijkstra(g, s, d)
            self.assertEqual(''.join(e.ref for e in a.path), 'SSSS')
            self.assertEqual([n.ref for n in a.hops], [(0,2), (1,2), (2,2), (3,2), (4,2)])
            self.assertEqual(a.cost, 4)
            self.assertGreaterEqual(a.iterations, 15)
            self.assertLessEqual(a.iterations, 19)
        def test_two_paths(self):
            g, s, d = two_paths()
            a = Dijkstra(g, s, d)
            self.assertEqual(''.join(n.ref for n in a.hops), 'AEDH')
            self.assertEqual(a.cost, 3)
            self.assertGreaterEqual(a.iterations, 7)
            self.assertLessEqual(a.iterations, 8)
        def test_two_paths_cost(self):
            g, s, d = two_paths(ef_weight = 2)
            a = Dijkstra(g, s, d)
            self.assertEqual(''.join(n.ref for n in a.hops), 'AEDH')
            self.assertEqual(a.cost, 3)
            # nodes F and G are never processed.
            self.assertEqual(a.iterations, 6)

    class BellmanFordTests(unittest.TestCase):
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = BellmanFord(g, s, d)
            self.assertEqual(''.join(e.ref for e in a.path), 'SSSS')
            self.assertEqual([n.ref for n in a.hops], [(0,2), (1,2), (2,2), (3,2), (4,2)])
            self.assertEqual(a.cost, 4)
            self.assertEqual(a.iterations, 25)
        def test_two_paths(self):
            g, s, d = two_paths()
            a = BellmanFord(g, s, d)
            self.assertEqual(''.join(n.ref for n in a.hops), 'AEDH')
            self.assertEqual(a.cost, 3)
            self.assertEqual(a.iterations, 8)
        def test_two_paths_negative(self):
            g, s, d = two_paths(ef_weight = -1)
            a = BellmanFord(g, s, d)
            self.assertIn(''.join(n.ref for n in a.hops), ('AEFGH', 'AEFDH'))
            self.assertEqual(a.cost, 2)
            # self.assertEqual(a.mincost[g.get_node('D')], 1)
            # while Bellman-Ford may reintroduce nodes in the queue, 
            # it should not happen in this particular graph.
            self.assertEqual(a.iterations, 8)
        def test_two_paths_reinsert(self):
            g, s, d = two_paths(cd_weight = -2, ef_weight = -1)
            a = BellmanFord(g, s, d)
            self.assertEqual(''.join(n.ref for n in a.hops), 'ABCDH')
            self.assertEqual(a.cost, 1)
            # self.assertEqual(a.mincost[g.get_node('D')], 0)
            # node D is processed twice in this graph
            # node H may also be processed twice.
            self.assertGreaterEqual(a.iterations, 9)
            self.assertLessEqual(a.iterations, 10)

    class AStarTests(unittest.TestCase):
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = AStar(g, s, d, heurist_lower_boundary=planar_coord_distance)
            self.assertEqual(''.join(e.ref for e in a.path), 'SSSS')
            self.assertEqual([n.ref for n in a.hops], [(0,2), (1,2), (2,2), (3,2), (4,2)])
            self.assertEqual(a.cost, 4)
            self.assertEqual(a.iterations, 5)

    class BhandariTests(unittest.TestCase):
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = Bhandari(g, s, d, k=3)
            self.assertEqual(len(a.path), 3)
            paths = set([''.join(e.ref for e in path) for path in a.path])
            self.assertSetEqual(paths, set(('SSSS', 'ESSSSW', 'WSSSSE')))
            self.assertEqual(a.cost[0], 4)
            self.assertEqual(a.cost[1], 6)
            self.assertEqual(a.cost[2], 6)
        def test_not_so_many_paths(self):
            g, s, d = five_by_five()
            # only 3 paths exist, not 4.
            self.assertRaises(NoPath, Bhandari, g, s, d, k=4)
        def test_two_paths(self):
            g, s, d = two_paths()
            a = Bhandari(g, s, d)
            self.assertEqual(len(a.path), 2)
            self.assertEqual(''.join(n.ref for n in a.hops[0]), 'AEFGH')
            self.assertEqual(a.cost[0], 4)
            self.assertEqual(''.join(n.ref for n in a.hops[1]), 'ABCDH')
            self.assertEqual(a.cost[1], 4)
        def test_two_paths_common_node(self):
            g, s, d = two_paths(ef_weight=3)
            a = Bhandari(g, s, d)
            self.assertEqual(len(a.path), 2)
            self.assertEqual(''.join(n.ref for n in a.hops[0]), 'AEDH')
            self.assertEqual(a.cost[0], 3)
            self.assertEqual(''.join(n.ref for n in a.hops[1]), 'ABCDFGH')
            self.assertEqual(a.cost[1], 6)
        def test_two_intertwined_paths(self):
            g, s, d = two_intertwined_paths()
            a = Bhandari(g, s, d)
            self.assertEqual(len(a.path), 2)
            self.assertEqual(''.join(n.ref for n in a.hops[0]), 'AEFGHIJP')
            self.assertEqual(a.cost[0], 7)
            self.assertEqual(''.join(n.ref for n in a.hops[1]), 'ABCDLMNOP')
            self.assertEqual(a.cost[1], 8)
    class SuurballeTests(unittest.TestCase):
        def test_five_by_five(self):
            g, s, d = five_by_five()
            a = Suurballe(g, s, d, k=3)
            self.assertEqual(len(a.path), 3)
            paths = set([''.join(e.ref for e in path) for path in a.path])
            self.assertSetEqual(paths, set(('SSSS', 'ESSSSW', 'WSSSSE')))
            self.assertEqual(a.cost[0], 4)
            self.assertEqual(a.cost[1], 6)
            self.assertEqual(a.cost[2], 6)
        def test_not_so_many_paths(self):
            g, s, d = five_by_five()
            # only 3 paths exist, not 4.
            self.assertRaises(NoPath, Suurballe, g, s, d, k=4)
        def test_two_paths(self):
            # Suurballe takes the longer route via D-E-F instead of D-F
            # to avoid a common node in both paths.
            g, s, d = two_paths(ef_weight=3)
            a = Suurballe(g, s, d)
            self.assertEqual(len(a.path), 2)
            self.assertEqual(''.join(n.ref for n in a.hops[0]), 'AEFGH')
            self.assertEqual(a.cost[0], 6)
            self.assertEqual(''.join(n.ref for n in a.hops[1]), 'ABCDH')
            self.assertEqual(a.cost[1], 4)
        def test_two_intertwined_paths(self):
            g, s, d = two_intertwined_paths()
            # Add many more edges, which can be used because that would 
            # cause the paths to share a node.
            for n,m in ('BE', 'CE', 'DF', 'DG', 'GL', 'HL', 'IK', 'JN', 'JO', 'KM'):
                g.get_node(n).add_bidirectional_edge(g.get_node(m), n+m)
            a = Suurballe(g, s, d)
            self.assertEqual(len(a.path), 2)
            self.assertEqual(''.join(n.ref for n in a.hops[0]), 'AEFGHIJP')
            self.assertEqual(a.cost[0], 7)
            self.assertEqual(''.join(n.ref for n in a.hops[1]), 'ABCDLMNOP')
            self.assertEqual(a.cost[1], 8)

    unittest.main()
