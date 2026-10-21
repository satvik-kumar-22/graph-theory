from __future__ import annotations
from itertools import product
from functools import lru_cache
from collections.abc import Callable
from collections import deque

class Digraph:

    """A mutable data structure that represents a directed graph through
    an adjacency matrix. It also only allows for simple digraphs. If the adjacency
    matrix of a non-simple digraph is provided, it is simplified.

    The class provides methods for operations such as:

    - Calculating the underlying graph of a digraph
    - Calculating the subdigraph induced by a set of vertices
    - Finding indegree and outdegree
    - Counting k-paths between two vertices
    - Depth-first and breadth-first search
    - Checking whether two vertices are connected (path from i to j)
    - Determining whether a digraph is strongly connected (Kosaraju's algorithm)
    - Finding strongly connected components
    - Calculating the condensation of a digraph

    It also provides methods for converting graphs into:

    - Incidence matrices
    - Adjacency lists
    - Edge lists

    Some features that are coming soon are:

    - Random graph support
    - Checking whether a graph is bipartite
    - Checking whether two graphs are isomorphic
    - Finding cycles in a graph
    - Finding articulation points in a graph
    - Finding minimal spanning trees

    as well as a __str__ method that cleanly renders the graph in ASCII using force-directed graph drawing.
    """

    class TargetError(Exception): pass;

    def __init__(self, adjacency_matrix: list[list[int]]):

        if not isinstance(adjacency_matrix, list):
            raise TypeError("adjacency_matrix must be a list")

        if not all(isinstance(row, list) for row in adjacency_matrix):
            raise TypeError("All rows in adjacency_matrix must be lists")

        first = True
        width = 0
        for row in adjacency_matrix:

            if first:
                width = len(row)
                first = False
            elif len(row) != width:
                raise ValueError("Width of rows in matrix must be uniform")

            for entry in row:
                if not isinstance(entry, int):
                    raise TypeError("All entries in adjacency_matrix must be integers")
                elif entry < 0:
                    raise ValueError("All entries in adjacency_matrix must be nonnegative")

        if width != len(adjacency_matrix):
            raise ValueError("adjacency_matrix must be a square matrix")

        adjacency_matrix = [row.copy() for row in adjacency_matrix]

        for i, j in product(range(width), range(width)):
            adjacency_matrix[i][j] = 0 if i == j else min(adjacency_matrix[i][j], 1)

        self.adj = adjacency_matrix

    @staticmethod
    def __NOTHING_1(v: int):
        return
    @staticmethod
    def __NOTHING_2(v1: int, v2: int):
        return

    @classmethod
    def edgeless(cls, vertex_number: int):

        return cls([[0 for _ in range(vertex_number)] for __ in range(vertex_number)])

    @property
    def edge_number(self):

        return sum(sum(row) for row in self.adj)

    @property
    def vertex_number(self):

        return len(self.adj)

    def is_undirected(self):

        result = True

        for i in range(self.vertex_number):
            for j in range(i + 1, self.vertex_number):

                if self[i, j] != self[j, i]:
                    result = False

        return result

    def is_vertex(self, vertex: int):

        return isinstance(vertex, int) and 0 <= vertex < self.vertex_number

    def add_vertex(self):

        vertex_number = self.vertex_number

        for row in self.adj:
            row.append(0)

        self.adj.append([0 for _ in range(vertex_number + 1)])

    def remove_vertex(self, vertex: int):

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        del self.adj[vertex]
        for row in self.adj:
            del row[vertex]

    def __str__(self):

        return "\n".join(" ".join(map(str, row)) for row in self.adj)

    def __getitem__(self, _t: tuple):

        if not isinstance(_t, tuple):
            raise TypeError(f"Expected tuple, received {type(_t).__name__}")
        if len(_t) != 2:
            raise ValueError(f"Expected two vertices, received {len(_t)}")
        if not all(self.is_vertex(v) for v in _t):
            raise ValueError("Received invalid vertex names")

        i, j = _t

        return self.adj[i][j]

    def __setitem__(self, _t: tuple, num_edges: int):

        if not isinstance(_t, tuple):
            raise TypeError(f"Expected tuple, received {type(_t).__name__}")
        if len(_t) != 2:
            raise ValueError(f"Expected two vertices, received {len(_t)}")
        if not all(self.is_vertex(v) for v in _t):
            raise ValueError("Received invalid vertex names")
        if not isinstance(num_edges, int):
            raise TypeError(f"Expected int, received {type(num_edges).__name__}")
        if num_edges < 0:
            raise ValueError("New value for number of edges must be nonnegative")

        i, j = _t

        self.adj[i][j] = num_edges

    def are_adjacent(self, i: int, j: int):

        if not self.is_vertex(i) or not self.is_vertex(j):
            raise ValueError("Received invalid vertex names")

        return (self[i, j] > 0) or (self[j, i] > 0)

    def neighbors(self, vertex: int):

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return {i for i in range(self.vertex_number) if self.are_adjacent(vertex, i)}

    def outneighbors(self, vertex: int):

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return {i for i in range(self.vertex_number) if self[vertex, i]}

    def inneighbors(self, vertex: int):

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return {i for i in range(self.vertex_number) if self[i, vertex]}

    def indegree(self, vertex: int):

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return sum(map(lambda row: row[vertex], self.adj))

    def outdegree(self, vertex: int):

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return sum(self.adj[vertex])

    @classmethod
    def K(cls, m: int, n: int):

        edgeless = cls.edgeless(m + n)

        for i in range(m):
            for j in range(m, m + n):
                edgeless[i, j] = 1

        return edgeless

    def induced_subdigraph(self, vertex_set: set[int]):

        if not isinstance(vertex_set, set):
            raise TypeError(f"Expected set, received {type(vertex_set).__name__}")
        if not all(self.is_vertex(vertex) for vertex in vertex_set):
            raise ValueError("Received invalid vertex name(s)")

        new_adj = [
            [entry for i, entry in enumerate(row) if i in vertex_set]
            for j, row in enumerate(self.adj) if j in vertex_set
        ]

        return type(self)(new_adj)

    def underlying_graph(self):

        new_adj = self.adj.copy()

        for i in range(self.vertex_number):
            for j in range(i + 1, self.vertex_number):
                edge = int(self.are_adjacent(i, j))
                new_adj[i][j] = edge
                new_adj[j][i] = edge

        return Graph(new_adj)

    def as_incidence_matrix(self):

        new_incidence = [[0 for _ in range(self.edge_number)] for __ in range(self.vertex_number)]

        edge_counter = 0

        for i, j in product(range(self.vertex_number), range(self.vertex_number)):

            if self[i, j] == 1:

                new_incidence[i][edge_counter] = -1
                new_incidence[j][edge_counter] = 1

                edge_counter += 1

        return new_incidence

    def as_adjacency_list(self):

        return [
            [j for j in range(self.vertex_number) if self[i, j]]
            for i in range(self.vertex_number)
        ]

    def as_edge_list(self):

        return [
            (i, j) for i, j in product(range(self.vertex_number), range(self.vertex_number))
            if self[i, j]
        ]

    @lru_cache(maxsize=None)
    def num_paths(self, k: int, i: int, j: int):

        if not isinstance(k, int):
            raise TypeError("k (length of path) must be integer")
        elif k < 0:
            raise ValueError("k (length of path) must be positive")

        if not self.is_vertex(i):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(j):
            raise ValueError("Received invalid vertex name")

        if k == 0:
            return 1
        if k == 1:
            return self[i, j]

        else:
            return sum(
                self[p, j] * self.num_paths(k - 1, i, p)
                for p in range(self.vertex_number)
            )

    def skeletal_dfs(self, start: int, *,
                     neighbor_function: Callable[[int], set[int]] | None=None,
                     visited_function: Callable[[int, int], ...] | None=None,
                     edge_function: Callable[[int, int], ...] | None=None,
                     finishing_function: Callable[[int], ...] | None=None
                     ) -> set[int]:

        if not self.is_vertex(start):
            raise ValueError("Received invalid vertex name")
        if neighbor_function is None:
            neighbor_function = self.outneighbors
        if visited_function is None:
            visited_function = Digraph.__NOTHING_2
        if edge_function is None:
            edge_function = Digraph.__NOTHING_2
        if finishing_function is None:
            finishing_function = Digraph.__NOTHING_1

        visited = set()

        def dfs(_start: int):

            visited.add(_start)

            neighbor_set = neighbor_function(_start)

            for vertex in neighbor_set:

                if vertex in visited:

                    # for example, marking arrows when generating strong orientations
                    visited_function(_start, vertex)
                    continue

                else:
                    # for example, marking traversed edges when generating a spanning tree
                    edge_function(_start, vertex)
                    dfs(vertex)

            finishing_function(_start)

        dfs(start)

        return set(visited)

    def skeletal_bfs(self, start: int, edge_function: Callable[[int, int], ...] | None=None):

        if not self.is_vertex(start):
            raise ValueError("Received invalid vertex name")
        if edge_function is None:
            edge_function = Digraph.__NOTHING_2

        visited = {start,}
        ring = {start,}

        while ring:

            new_ring = set()
            for vertex in ring:
                for n in self.outneighbors(vertex):

                    if n not in visited:

                        edge_function(vertex, n)
                        new_ring.add(n)
                        visited.add(n)

            ring = new_ring

        return visited

    def dfs_tree(self, start: int):

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_function(_start, vertex):
            new_graph[_start, vertex] = 1

        self.skeletal_dfs(start, edge_function=edge_function)

        return new_graph

    def bfs_tree(self, start: int):

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_function(_start, vertex):
            new_graph[_start, vertex] = 1

        self.skeletal_bfs(start, edge_function=edge_function)

        return new_graph

    def dfs_forest(self):

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_function(_start, vertex):
            new_graph[_start, vertex] = 1

        vertices_left = set(range(self.vertex_number))

        while vertices_left:

            root = next(iter(vertices_left))
            vertices_left -= self.skeletal_dfs(root, edge_function=edge_function)

        return new_graph

    def bfs_forest(self):

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_function(_start, vertex):
            new_graph[_start, vertex] = 1

        vertices_left = set(range(self.vertex_number))

        while vertices_left:

            root = next(iter(vertices_left))
            vertices_left -= self.skeletal_bfs(root, edge_function=edge_function)

        return new_graph

    def strongly_connected_components(self) -> list[set[int]]:

        remaining_vertices = set(range(self.vertex_number))

        ranking = deque()

        while remaining_vertices:

            root = next(iter(remaining_vertices))

            remaining_vertices -= self.skeletal_dfs(root,
                                            neighbor_function=lambda x: {n for n in self.outneighbors(x) if n in remaining_vertices},
                                            finishing_function=ranking.appendleft
                                            )

        sccs = []

        traversed = set()

        while ranking:
            root = ranking.popleft()
            if root in traversed:
                continue

            scc = self.skeletal_dfs(root, neighbor_function=lambda x: {n for n in self.inneighbors(x) if n not in traversed})
            sccs.append(scc)
            traversed |= scc

        return sccs

    def path(self, v1: int, v2: int) -> list[int] | None:

        if not self.is_vertex(v1):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(v2):
            raise ValueError("Received invalid vertex name")

        if v1 == v2:
            return [v1]

        predecessors = {}

        def edge_function(start, vertex):

            predecessors[vertex] = start
            if vertex == v2:
                raise Digraph.TargetError

        try:
            self.skeletal_dfs(v1, edge_function=edge_function)
        except Digraph.TargetError:
            path = [v2]

            while True:
                predecessor = predecessors[path[-1]]
                path.append(predecessor)
                if predecessor == v1:
                    break

            return path[::-1]

    def shortest_path(self, v1: int, v2: int) -> list[int] | None:

        if not self.is_vertex(v1):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(v2):
            raise ValueError("Received invalid vertex name")

        if v1 == v2:
            return [v1]

        predecessors = {}

        def edge_function(start, vertex):

            predecessors[vertex] = start
            if vertex == v2:
                raise Digraph.TargetError

        try:
            self.skeletal_bfs(v1, edge_function=edge_function)
        except Digraph.TargetError:
            path = [v2]

            while True:
                predecessor = predecessors[path[-1]]
                path.append(predecessor)
                if predecessor == v1:
                    break

            return path[::-1]

    def path_exists(self, v1: int, v2: int) -> bool:

        if not self.is_vertex(v1):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(v2):
            raise ValueError("Received invalid vertex name")

        if v1 == v2:
            return True

        class TargetError(Exception): pass;

        def edge_function(_, vertex):

            if vertex == v2:
                raise TargetError

        try:
            self.skeletal_dfs(v1, edge_function=edge_function)
        except TargetError:
            return True

        return False

    def condensation(self):

        sccs = self.strongly_connected_components()

        vertex_to_scc_num = {}

        scc_count = 0

        for scc_num, scc in enumerate(sccs):
            scc_count += 1

            for vertex in scc:
                vertex_to_scc_num[vertex] = scc_num

        cond = Digraph.edgeless(scc_count)

        for v1, v2 in product(range(self.vertex_number), range(self.vertex_number)):

            scc_num1, scc_num2 = vertex_to_scc_num[v1], vertex_to_scc_num[v2]

            if self[v1, v2] and scc_num1 != scc_num2:
                cond[scc_num1, scc_num2] = 1

        return cond

class Graph(Digraph):

    """A subclass of Digraph that specifically represents undirected graphs
    (digraphs with symmetric adjacency matrices) as opposed to general digraphs.
    This allows us to override the methods for edge lists and incidence matrices,
    as well as implementing the following methods:

    - Checking whether a graph is connected
    - Finding connected components
    - Locating bridges within a graph (Tarjan's algorithm)
    - Finding a strong orientation of a graph

    Some features that might be coming soon are:

    - Planarity of graphs
    - Vertex coloring (chromatic numbers)
    - Eulerian and Hamiltonian paths
    """

    def __init__(self, adjacency_matrix: list[list[int]]):

        super().__init__(adjacency_matrix)

        if not self.is_undirected():
            raise ValueError("Adjacency matrix is not symmetric.")

    def is_connected(self):

        return len(self.skeletal_dfs(0)) == self.vertex_number

    def connected_components(self):

        vertices_left = set(range(self.vertex_number))

        result = []

        while vertices_left:

            root = next(iter(vertices_left))
            result.append(self.skeletal_dfs(root))

        return result

    def _bridges_on_connected_component(self, start: int):

        disc: list[int] = [0] * self.vertex_number
        low: list[int] = [0] * self.vertex_number

        current_timestamp = 0

        child_to_parent: dict[int, int] = {}
        tree_edges: set[tuple[int, int]] = set()

        def edge_function(_start, vertex):

            nonlocal current_timestamp

            tree_edges.add((_start, vertex))

            child_to_parent[vertex] = _start
            current_timestamp += 1
            disc[vertex] = current_timestamp
            low[vertex] = current_timestamp

        def visited_function(_start, vertex):

            if _start == start or vertex != child_to_parent[_start]:
                low[_start] = min(low[_start], disc[vertex])

        def finishing_function(child):

            if child != start:
                parent = child_to_parent[child]
                low[parent] = min(low[parent], low[child])

        vertices_explored = self.skeletal_dfs(start, edge_function=edge_function, visited_function=visited_function, finishing_function=finishing_function)

        return vertices_explored, [{i, j} for i, j in tree_edges if low[j] > disc[i]]

    def bridges(self):

        vertices_left = set(range(self.vertex_number))

        result = []

        while vertices_left:

            root = next(iter(vertices_left))

            vertices_explored, local_bridges = self._bridges_on_connected_component(root)
            vertices_left -= vertices_explored
            result.extend(local_bridges)

        return result

    def as_edge_list(self):

        return [
            {i, j} for i, j in product(range(self.vertex_number), range(self.vertex_number))
            if self[i, j]
        ]

    def as_incidence_matrix(self):

        new_incidence = [[0 for _ in range(self.edge_number)] for __ in range(self.vertex_number)]

        edge_counter = 0

        for i, j in product(range(self.vertex_number), range(self.vertex_number)):

            if self[i, j] == 1:

                new_incidence[i][edge_counter] = 1
                new_incidence[j][edge_counter] = 1

                edge_counter += 1

        return new_incidence

    @classmethod
    def complete(cls, vertex_number: int):

        # Implicitly removes loops
        return Graph([[1 for _ in range(vertex_number)] for __ in range(vertex_number)])

    @classmethod
    def bipartite(cls, v1: int, v2: int):

        new_graph = Graph.edgeless(v1 + v2)
        for i in range(v1):
            for j in range(v1, v1 + v2):
                new_graph[i, j] = 1
                new_graph[j, i] = 1

        return new_graph

    def strong_orientation(self) -> Digraph:

        if self.bridges():
            raise ValueError("This graph has a bridge: by Robbins' theorem, it is not strongly orientable")

        digraph = Digraph.edgeless(self.vertex_number)

        def edge_function(_start, vertex):
            digraph[_start, vertex] = 1

        def visited_function(_start, vertex):
            digraph[vertex, _start] = 1

        vertices_left = set(range(self.vertex_number))

        while vertices_left:

            root = next(iter(vertices_left))

            vertices_left -= self.skeletal_dfs(root, edge_function=edge_function, visited_function=visited_function)

        return digraph
