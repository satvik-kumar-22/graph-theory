from __future__ import annotations
from itertools import product
from functools import lru_cache
from collections.abc import Callable
from collections import deque
from typing import Any, Self, Iterator, Literal

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

    Another possible idea is a __str__ method that cleanly renders the graph in ASCII
    using force-directed graph drawing.
    """

    # An exception that occurs during depth-first and breadth-first search
    # when a target vertex is found, stopping execution of the algorithm.

    class TargetError(Exception): pass

    def __init__(self, adjacency_matrix: list[list[int]]) -> None:

        """Initialize a Digraph object from an adjacency matrix. The
        __init__ method verifies that the adjacency matrix is of the correct
        type, and it also simplifies the graph by deleting loops and
        multiple edges."""

        if not isinstance(adjacency_matrix, list):
            raise TypeError("adjacency_matrix must be a list")

        if not all(isinstance(row, list) for row in adjacency_matrix):
            raise TypeError("All rows in adjacency_matrix must be lists")

        if not adjacency_matrix:
            raise TypeError("Digraph does not support the null graph")

        # Verify that rows have uniform width

        width = len(adjacency_matrix[0])

        for row in adjacency_matrix:

            if len(row) != width:
                raise ValueError("Width of rows in matrix must be uniform")

            for entry in row:
                if not isinstance(entry, int):
                    raise TypeError("All entries in adjacency_matrix must be integers")
                elif entry < 0:
                    raise ValueError("All entries in adjacency_matrix must be nonnegative")

        if width != len(adjacency_matrix):
            raise ValueError("adjacency_matrix must be a square matrix")

        # Create copy of matrix
        adjacency_matrix = [row.copy() for row in adjacency_matrix]

        # Simplify matrix
        for i, j in self.indices():
            adjacency_matrix[i][j] = 0 if i == j else min(adjacency_matrix[i][j], 1)

        self.adj = adjacency_matrix

    # Functions that do not do anything, which are default values for DFS and BFS hooks.

    @staticmethod
    def __NOTHING_1(vertex: int) -> None: return # Arity 1

    @staticmethod
    def __NOTHING_2(vertex_1: int, vertex_2: int) -> None: return # Arity 2

    @classmethod
    def edgeless(cls, vertex_number: int) -> Self:

        """A class constructor that returns a graph of size vertex_number
        with no edges."""

        return cls([[0 for _ in range(vertex_number)] for __ in range(vertex_number)])

    @property
    def edge_number(self) -> int:

        """Returns the number of edges in the graph."""

        return sum(sum(row) for row in self.adj)

    @property
    def vertex_number(self) -> int:

        """Returns the number of vertices in the graph."""

        return len(self.adj)

    def indices(self) -> Iterator[tuple[int, int]]:

        """An iterator that runs through all pairs (i, j) of vertices in the
        digraph."""

        return product(range(self.vertex_number), range(self.vertex_number))

    def is_undirected(self) -> bool:

        """Verify whether a digraph is undirected (every edge points both ways).
        This is equivalent to verifying that self.adj is a symmetric matrix."""

        result = True

        for i in range(self.vertex_number):
            for j in range(i + 1, self.vertex_number):

                if self[i, j] != self[j, i]:
                    result = False

        return result

    def is_vertex(self, vertex: Any) -> bool:

        """Check if an object is a vertex in the digraph. This is used
        in defensive measures when a vertex is passed to a method."""

        return isinstance(vertex, int) and 0 <= vertex < self.vertex_number

    def add_vertex(self) -> None:

        """Adds a new vertex to the graph. If there
        are currently n vertices in the graph, numbered
        0, 1, 2, ..., n - 1, then this new vertex is
        set to be number n."""

        vertex_number = self.vertex_number

        # Pad the matrix with 0s along the end vertically.
        for row in self.adj:
            row.append(0)

        # Add a zero row at the end.
        self.adj.append([0 for _ in range(vertex_number + 1)])

    def remove_vertex(self, vertex: int) -> None:

        """Removes all connections between a vertex and
        other vertices. It does not fully remove the vertex
        from the graph, as doing so would shift the names
        of preexisting vertices. Instead, it is orphaned
        and considered to be invisible, although it is still
        present in the graph."""

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        del self.adj[vertex]
        for row in self.adj:
            del row[vertex]

    def __str__(self) -> str:

        """A rudimentary string representation that prints
        out the adjacency matrix."""

        return "\n".join(" ".join(map(str, row)) for row in self.adj)

    def __getitem__(self, _t: tuple) -> Literal[0, 1]:

        """This method implements the graph[i, j] syntax for checking
        whether a vertex i is adjacent to j. It takes in a tuple
        of two vertices and outputs 1 if they are adjacent and 0 otherwise."""

        if not isinstance(_t, tuple):
            raise TypeError(f"Expected tuple, received {type(_t).__name__}")
        if len(_t) != 2:
            raise ValueError(f"Expected two vertices, received {len(_t)}")
        if not all(self.is_vertex(v) for v in _t):
            raise ValueError("Received invalid vertex names")

        i, j = _t

        return self.adj[i][j]

    def __setitem__(self, _t: tuple, num_edges: Literal[0, 1]) -> None:

        """This method implements the graph[i, j] = 0 or 1 syntax for setting
        edges between two vertices. It takes in a tuple of two vertices and
        a number of edges (must be 0 or 1) and updates the corresponding
        entry in the adjacency matrix."""

        if not isinstance(_t, tuple):
            raise TypeError(f"Expected tuple, received {type(_t).__name__}")
        if len(_t) != 2:
            raise ValueError(f"Expected two vertices, received {len(_t)}")
        if not all(self.is_vertex(v) for v in _t):
            raise ValueError("Received invalid vertex names")
        if not isinstance(num_edges, int):
            raise TypeError(f"Expected int, received {type(num_edges).__name__}")
        if num_edges not in range(2):
            raise ValueError("New value for number of edges must be 0 or 1")

        i, j = _t

        self.adj[i][j] = num_edges

    def are_adjacent(self, i: int, j: int) -> bool:

        """Checks whether two vertices i and j are adjacent (either i
        is adjacent to j or j is adjacent to i)."""

        if not self.is_vertex(i) or not self.is_vertex(j):
            raise ValueError("Received invalid vertex names")

        return (self[i, j] > 0) or (self[j, i] > 0)

    def neighbors(self, vertex: int) -> set[int]:

        """This function finds all neighbors of a vertex, inneighbors
        or outneighbors, and returns a set of integers corresponding
        to neighboring vertices."""

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return {i for i in range(self.vertex_number) if self.are_adjacent(vertex, i)}

    def outneighbors(self, vertex: int) -> set[int]:

        """This function returns a set of integers corresponding to outneighbors
        of a vertex. Outneighbors of a vertex i are any other vertices j such that
        i is adjacent to j."""

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return {i for i in range(self.vertex_number) if self[vertex, i]}

    def inneighbors(self, vertex: int):

        """This function returns a set of integers corresponding to inneighbors
        of a vertex. Outneighbors of a vertex i are any other vertices j such that
        i is adjacent from j."""

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return {i for i in range(self.vertex_number) if self[i, vertex]}

    def outdegree(self, vertex: int) -> int:

        """Returns the outdegree of a vertex by summing along a row
        of the adjacency matrix."""

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return sum(self.adj[vertex])

    def indegree(self, vertex: int) -> int:

        """Returns the indegree of a vertex by summing along a column
        of the adjacency matrix."""

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return sum(map(lambda row: row[vertex], self.adj))

    @classmethod
    def K(cls, m: int, n: int) -> Self:

        """Creates a complete directed bipartite graph K(m, n). A complete directed
        bipartite graph is a graph with m + n vertices, where the vertices can be
        partitioned into sets M and N where |M| = m and |N| = n, and every vertex in M
        is connected to every vertex in N. Furthermore, the only edges in the graph
        are ones created by these connections."""

        edgeless = cls.edgeless(m + n)

        for i in range(m):
            for j in range(m, m + n):
                edgeless[i, j] = 1

        return edgeless

    def induced_subdigraph(self, vertex_set: set[int]) -> Self:

        """From a set of vertices, creates a new digraph that represents
        the subdigraph of 'self' induced by the set of vertices provided."""

        if not isinstance(vertex_set, set):
            raise TypeError(f"Expected set, received {type(vertex_set).__name__}")
        if not all(self.is_vertex(vertex) for vertex in vertex_set):
            raise ValueError("Received invalid vertex name(s)")

        new_adj = [
            [entry for i, entry in enumerate(row) if i in vertex_set]
            for j, row in enumerate(self.adj) if j in vertex_set
        ]

        return type(self)(new_adj)

    def underlying_graph(self) -> Graph:

        """Creates a new Graph object by turning the
        directed edges in the digraph into undirected edges,
        also known as the underlying graph of a digraph."""

        new_adj = self.adj.copy()

        for i in range(self.vertex_number):
            for j in range(i + 1, self.vertex_number):

                # Take possible pairs of i and j and check if they are adjacent
                edge = int(self.are_adjacent(i, j))

                new_adj[i][j] = edge
                new_adj[j][i] = edge

        return Graph(new_adj)

    def as_incidence_matrix(self) -> list[list[int]]:

        """Creates the incidence matrix associated with a digraph as a list.
        For digraphs, note that incidence matrices represent the initial vertex
        with a -1 and the terminal vertex with a 1 for every edge."""

        # Initialize blank 2D list with dimensions
        new_incidence = [[0 for _ in range(self.edge_number)] for __ in range(self.vertex_number)]

        edge_counter = 0

        for i, j in self.indices():

            if self[i, j] == 1:

                new_incidence[i][edge_counter] = -1
                new_incidence[j][edge_counter] = 1

                edge_counter += 1

        return new_incidence

    def as_adjacency_list(self):

        """Creates the adjacency list associated with a digraph. The adjacency list
        stores the outneighbors of every single vertex in the graph."""

        return [
            [j for j in range(self.vertex_number) if self[i, j]]
            for i in range(self.vertex_number)
        ]

    def as_edge_list(self):

        """Creates the edge list associated with a digraph, where every
        edge is represented as an ordered pair (i, j) and i is adjacent
        to j."""

        return [
            (i, j) for i, j in self.indices() if self[i, j]
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

        for v1, v2 in self.indices():

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

    @property
    def edge_number(self):

        return super().edge_number // 2

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
            {i, j} for i, j in self.indices() if self[i, j]
        ]

    def as_incidence_matrix(self):

        new_incidence = [[0 for _ in range(self.edge_number)] for __ in range(self.vertex_number)]

        edge_counter = 0

        for i, j in self.indices():

            if self[i, j] == 1:

                new_incidence[i][edge_counter] = 1
                new_incidence[j][edge_counter] = 1

                edge_counter += 1

        return new_incidence

    @classmethod
    def K(cls, *sizes: int):

        if not all(isinstance(size, int) and size > 0 for size in sizes):
            raise ValueError("All arguments provided must be positive integers")

        if len(sizes) == 2: # Complete bipartite graph

            m, n = sizes

            new_graph = Graph.edgeless(m + n)
            for i in range(m):
                for j in range(m, m + n):
                    new_graph[i, j] = 1
                    new_graph[j, i] = 1

            return new_graph

        elif len(sizes) == 1: # Complete graph

            n = sizes[0]

            # Implicitly removes loops
            return Graph([[1 for _ in range(n)] for __ in range(n)])

        else:
            raise ValueError("Number of arguments provided must be 1 or 2")

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
