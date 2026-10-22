from __future__ import annotations
from itertools import product
from functools import lru_cache
from collections.abc import Callable
from collections import deque
from typing import Any, Self, Iterator, Literal, cast

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
    - Computing the reachability matrix
    - Topologically sorting a graph
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

        self.adj = adjacency_matrix

        # Simplify matrix
        for i, j in self.indices():
            adjacency_matrix[i][j] = 0 if i == j else min(adjacency_matrix[i][j], 1)

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

        return cast(Self, type(self)(new_adj))

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
    def num_paths(self, k: int, vertex_1: int, vertex_2: int) -> int:
        
        """Recursively computes the number of paths of length k
        from one vertex to another. This is akin to performing matrix
        multiplication on the adjacency matrix. We also cache
        previous values to avoid computing the same numbers repeatedly."""

        if not isinstance(k, int):
            raise TypeError("k (length of path) must be integer")
        elif k < 0:
            raise ValueError("k (length of path) must be positive")

        if not self.is_vertex(vertex_1):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(vertex_2):
            raise ValueError("Received invalid vertex name")

        if k == 0:
            return 1
        if k == 1:
            return self[vertex_1, vertex_2]

        else:
            return sum(
                self[p, vertex_2] * self.num_paths(k - 1, vertex_1, p)
                for p in range(self.vertex_number)
            )

    def skeletal_dfs(self, root: int, *,
                     neighbor_function: Callable[[int], set[int]] | None=None,
                     visited_hook: Callable[[int, int], ...] | None=None,
                     edge_hook: Callable[[int, int], ...] | None=None,
                     finishing_hook: Callable[[int], ...] | None=None
                     ) -> set[int]:

        """Runs the depth-first search algorithm starting at a root vertex, returning
        the set of vertices visited once the algorithm finishes. It also provides
        four optional arguments to control what happens at every step of the algorithm.
        This prevents users from re-implementing DFS logic over and over again,
        distilling different variations of the algorithm to what they do when:

        - Finding neighbors (neighbor_function)
        - Encountering an already visited vertex again (visited_hook)
        - Traversing an edge in the DFS tree (edge_hook)
        - A vertex finishes (finishing_hook)

        neighbor_function() specifically takes in a vertex and outputs a set
        of other vertices (by default, set to self.outneighbors).
        visited_hook() expects two vertices, the one you are currently at
        and the already visited neighbor you are looking at.
        edge_hook() expects two vertices, the one you are currently at
        and the one you are about to traverse.
        finishing_hook() expects one vertex only: the one that is currently finishing.
        """

        if not self.is_vertex(root):
            raise ValueError("Received invalid vertex name")
        if neighbor_function is None:
            neighbor_function = self.outneighbors
        if visited_hook is None:
            visited_hook = Digraph.__NOTHING_2
        if edge_hook is None:
            edge_hook = Digraph.__NOTHING_2
        if finishing_hook is None:
            finishing_hook = Digraph.__NOTHING_1

        visited = set()

        def dfs(_start: int):

            visited.add(_start)

            # Get neighboring vertices
            neighbor_set = neighbor_function(_start)

            for vertex in neighbor_set:

                if vertex in visited:

                    # for example, marking arrows when generating strong orientations
                    visited_hook(_start, vertex)
                    continue

                else:
                    # for example, marking traversed edges when generating a spanning tree
                    edge_hook(_start, vertex)
                    dfs(vertex)

            # for example, generating rankings in Kosaraju's algorithm
            finishing_hook(_start)

        dfs(root)

        return set(visited)

    def skeletal_bfs(self, root: int, edge_hook: Callable[[int, int], ...] | None=None) -> set[int]:

        """Runs the breadth-first search algorithm starting at a root vertex. There is an
        optional function parameter edge_hook, which acts the same as what was described
        in skeletal_bfs. Note that this BFS implementation is iterative, whereas the DFS
        implementation above is recursive."""

        if not self.is_vertex(root):
            raise ValueError("Received invalid vertex name")
        if edge_hook is None:
            edge_hook = Digraph.__NOTHING_2

        # The total area covered
        visited = {root,}
        # The boundary of the area covered from which we push forward
        ring = {root,}

        while ring:

            new_ring = set()

            # Populate new_ring with unvisited neighbors of vertices currently in ring
            for vertex in ring:

                for n in self.outneighbors(vertex):
                    if n not in visited:

                        edge_hook(vertex, n)
                        new_ring.add(n)
                        visited.add(n)

            ring = new_ring

        return visited

    def dfs_tree(self, root: int) -> Digraph:

        """Creates a directed spanning tree by running DFS on a root.
        It defines a custom edge_hook, which adds a directed edge
        on the new graph whenever a new vertex is explored. Note
        that this just creates a tree; if you want a forest that
        spans the entire digraph, use dfs_forest."""

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_hook(_start, vertex):
            new_graph[_start, vertex] = 1

        self.skeletal_dfs(root, edge_hook=edge_hook)

        return new_graph

    def bfs_tree(self, root: int) -> Digraph:

        """Creates a directed spanning tree by running BFS on a root.
        It defines a custom edge_hook, similar to dfs_tree. If you want
        a forest that spans the entire digraph, use bfs_forest."""

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_hook(_start, vertex):
            new_graph[_start, vertex] = 1

        self.skeletal_bfs(root, edge_hook=edge_hook)

        return new_graph

    def dfs_forest(self) -> Digraph:

        """Creates a directed spanning forest by repeatedly
        creating DFS trees."""

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_hook(_start, vertex):
            new_graph[_start, vertex] = 1

        vertices_left = set(range(self.vertex_number))

        while vertices_left:

            root = next(iter(vertices_left))
            vertices_left -= self.skeletal_dfs(root, edge_hook=edge_hook)

        return new_graph

    def bfs_forest(self) -> Digraph:

        """Creates a directed spanning forest by repeatedly
        creating BFS trees."""

        new_graph = Digraph.edgeless(self.vertex_number)

        def edge_hook(_start, vertex):
            new_graph[_start, vertex] = 1

        vertices_left = set(range(self.vertex_number))

        while vertices_left:

            root = next(iter(vertices_left))
            vertices_left -= self.skeletal_bfs(root, edge_hook=edge_hook)

        return new_graph

    def strongly_connected_components(self) -> list[set[int]]:

        """Uses Kosaraju's algorithm to find strongly connected components in a digraph.
        It first explores the digraph fully, ranking each vertex by their finishing time.
        It then iteratively runs transposed DFS from the latest-finishing unvisited vertex,
        which creates strongly connected components."""

        remaining_vertices = set(range(self.vertex_number))

        # Rank vertices based on finishing time
        ranking = deque()

        while remaining_vertices:

            root = next(iter(remaining_vertices))

            # Every time a vertex finishes, its number is pushed to the back of the root stack.
            remaining_vertices -= self.skeletal_dfs(root,
                                            neighbor_function=lambda x: {n for n in self.outneighbors(x) if n in remaining_vertices},
                                            finishing_hook=ranking.append
                                            )

        sccs = []

        # Prevent DFS from visiting nodes already in strongly connected components
        traversed = set()

        while ranking:

            # Successively take untraversed roots from the back of the root stack.
            root = ranking.pop()
            if root in traversed:
                continue

            # Use inneighbors instead of outneighbors for the transposed DFS run.
            scc = self.skeletal_dfs(root, neighbor_function=lambda x: {n for n in self.inneighbors(x) if n not in traversed})
            sccs.append(scc)
            traversed |= scc

        return sccs

    def path(self, v1: int, v2: int) -> list[int] | None:

        """Finds a path between two vertices using DFS. In this case, the edge
        hook that runs every time a new vertex is explored will raise a TargetError
        if we have reached our target. Once a TargetError is raised and DFS execution
        halts, we store an external mapping of each of the vertices to their predecessor
        in the DFS tree, creating the path between the vertices."""

        if not self.is_vertex(v1):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(v2):
            raise ValueError("Received invalid vertex name")

        # Edge case: the two vertices are the same
        if v1 == v2:
            return [v1]

        # Store a mapping from each vertex to its predecessor / parent vertex.
        predecessors = {}

        def edge_hook(start, vertex):

            predecessors[vertex] = start
            if vertex == v2:
                raise Digraph.TargetError

        try:
            self.skeletal_dfs(v1, edge_hook=edge_hook)
        except Digraph.TargetError:
            path = [v2]

            # Create the path by successively taking predecessors.
            while True:
                predecessor = predecessors[path[-1]]
                path.append(predecessor)
                if predecessor == v1:
                    break

            return path[::-1]

    def path_exists(self, v1: int, v2: int) -> bool:

        """This function is similar to path(), but once a TargetError
        is raised, it does not store any external data. It simply
        returns True to show that v2 can be reached from v1. If a
        TargetError is never raised, False is returned."""

        if not self.is_vertex(v1):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(v2):
            raise ValueError("Received invalid vertex name")

        if v1 == v2:
            return True

        class TargetError(Exception): pass;

        def edge_hook(_, vertex):

            if vertex == v2:
                raise TargetError

        try:
            self.skeletal_dfs(v1, edge_hook=edge_hook)
        except TargetError:
            return True

        return False

    def shortest_path(self, v1: int, v2: int) -> list[int] | None:

        """This is a function that is identical to path(), except
        instead of using DFS, it uses BFS. This ensures that the shortest
        path is found."""

        if not self.is_vertex(v1):
            raise ValueError("Received invalid vertex name")
        if not self.is_vertex(v2):
            raise ValueError("Received invalid vertex name")

        if v1 == v2:
            return [v1]

        predecessors = {}

        def edge_hook(start, vertex):

            predecessors[vertex] = start
            if vertex == v2:
                raise Digraph.TargetError

        try:
            self.skeletal_bfs(v1, edge_hook=edge_hook)
        except Digraph.TargetError:
            path = [v2]

            while True:
                predecessor = predecessors[path[-1]]
                path.append(predecessor)
                if predecessor == v1:
                    break

            return path[::-1]

    def condensation(self) -> Digraph:

        """Creates the condensation of a digraph by assigning
        a number to every connected component. Then, we iterate
        over all edges and join two strongly connected components S and T
        if there is an edge from one vertex in S to another vertex in T.
        """

        sccs = self.strongly_connected_components()

        # Maps vertices to the SCC number that it is contained in. Effectively partitions the set of vertices.
        vertex_to_scc_num = {}

        scc_count = 0

        # Count the number of SCCs and populate vertex_to_scc_num.
        for scc_num, scc in enumerate(sccs):
            scc_count += 1

            for vertex in scc:
                vertex_to_scc_num[vertex] = scc_num

        cond = Digraph.edgeless(scc_count)

        for v1, v2 in self.indices():

            scc_num1, scc_num2 = vertex_to_scc_num[v1], vertex_to_scc_num[v2]

            # Draw an edge from SCCs with numbers scc_num1 and scc_num2.
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

        """The same initialization as Digraph, except it checks that the graph is undirected."""

        super().__init__(adjacency_matrix)

        # Checks that the graph is undirected
        if not self.is_undirected():
            raise ValueError("Adjacency matrix is not symmetric.")

    @property
    def edge_number(self):

        """Overwrite edge_number, as we consider every pair of two undirected edges to be an edge."""

        return super().edge_number // 2

    def is_connected(self):

        """Check if the graph is connected using DFS."""

        return len(self.skeletal_dfs(0)) == self.vertex_number

    def connected_components(self):

        """Find connected components of the graph by repeatedly running DFS
        from unvisited vertices."""

        vertices_left = set(range(self.vertex_number))

        result = []

        while vertices_left:

            root = next(iter(vertices_left))
            component = self.skeletal_dfs(root)
            result.append(component)
            vertices_left -= component

        return result

    def _bridges_on_connected_component(self, root: int) -> tuple[set[int], list[set[int]]]:

        """Locates all bridges in a specific connected component using Tarjan's bridge finding algorithm.
        The function takes in a root and runs DFS from that root. It stores two quantities for each
        vertex: its time of discovery and the vertex with the least discovery time it can reach (assuming
        that the edge from it to its parent is removed). These are stored in lists disc
        and low respectively, and the elements of low are computed recursively. From there,
        we iterate over the edges of the tree, checking if the low value of the child is less
        than or equal to the discovery time of the parent. This is true if and only if
        the edge is not a bridge (all bridges are contained within the DFS tree by necessity)."""

        disc: list[int] = [0] * self.vertex_number
        low: list[int] = [0] * self.vertex_number

        current_timestamp = 0

        # Map vertices to their parents
        child_to_parent: dict[int, int] = {}

        # Store all edges of the tree
        tree_edges: set[tuple[int, int]] = set()

        def edge_hook(_start, vertex):

            nonlocal current_timestamp

            tree_edges.add((_start, vertex))

            child_to_parent[vertex] = _start
            current_timestamp += 1
            disc[vertex] = current_timestamp

            # We initialize the low value for every vertex to be their current timestamp before any recursion happens.
            low[vertex] = current_timestamp

        def visited_hook(_start, vertex):

            # If we encounter a vertex that is already visited that isn't the parent,
            # we can reach that low into the graph.

            if _start == root or vertex != child_to_parent[_start]:
                low[_start] = min(low[_start], disc[vertex])

        def finishing_hook(child):

            """Once a child finishes, its low value is set, and the parent
            can steal that low value for itself."""

            if child != root:
                parent = child_to_parent[child]
                low[parent] = min(low[parent], low[child])

        # Populate low and disc values
        vertices_explored = self.skeletal_dfs(root, edge_hook=edge_hook, visited_hook=visited_hook, finishing_hook=finishing_hook)

        # Create a list of all edges that disconnect the connected component upon removal
        return vertices_explored, [{i, j} for i, j in tree_edges if low[j] > disc[i]]

    def bridges(self) -> list[set[int]]:

        """Find all bridges in the graph by iterating through connected components and finding all
        bridges in those components. In this sense, a bridge is defined as any edge that
        increases the number of connected components upon removal."""

        vertices_left = set(range(self.vertex_number))

        result = []

        while vertices_left:

            root = next(iter(vertices_left))

            vertices_explored, local_bridges = self._bridges_on_connected_component(root)
            vertices_left -= vertices_explored
            result.extend(local_bridges)

        return result

    def as_edge_list(self) -> list[set[int]]:

        """Create the edge list of a graph. This differs from the edge list of a digraph
        in that the edges are represented as unordered sets."""

        return [
            {i, j} for i, j in self.indices() if self[i, j]
        ]

    def as_incidence_matrix(self) -> list[list[int]]:

        """Create the incidence matrix of a graph. This differs from the incidence matrix of a digraph
        in that there is no initial and terminal edge, and both vertices the edge is incident on are
        represented as 1."""

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

        """Constructs a complete graph. There are two cases:
        - Two integers passed (K(m, n)): creates a complete undirected bipartite graph of order (m, n)
        - One integer passed (K(n)): creates a complete undirected graph of order n."""

        if not all(isinstance(size, int) and size > 0 for size in sizes):
            raise ValueError("All arguments provided must be positive integers")

        if len(sizes) == 2: # Complete bipartite graph (undirected)

            m, n = sizes

            new_graph = Graph.edgeless(m + n)
            for i in range(m):
                for j in range(m, m + n):
                    new_graph[i, j] = 1
                    new_graph[j, i] = 1

            return new_graph

        elif len(sizes) == 1: # Complete graph (undirected)

            n = sizes[0]

            # Implicitly removes loops
            return Graph([[1 for _ in range(n)] for __ in range(n)])

        else:
            raise ValueError("Number of arguments provided must be 1 or 2")

    def strong_orientation(self) -> Digraph:

        """Create a strong orientation of a graph. This works by using DFS. If vertex i discovers vertex j,
        an edge from i to j is drawn. If vertex i sees an already discovered vertex j, an edge from j to i
        is drawn. If the graph is disconnected, the strong orientation becomes the union of all strong orientations
        of the connected components. If the graph has a bridge, the graph cannot be strongly orientable
        by Robbins' theorem, and an error is raised."""

        if self.bridges():
            raise ValueError("This graph has a bridge: by Robbins' theorem, it is not strongly orientable")

        digraph = Digraph.edgeless(self.vertex_number)

        def edge_hook(_start, vertex):
            digraph[_start, vertex] = 1

        def visited_hook(_start, vertex):
            digraph[vertex, _start] = 1

        vertices_left = set(range(self.vertex_number))

        while vertices_left:

            root = next(iter(vertices_left))

            vertices_left -= self.skeletal_dfs(root, edge_hook=edge_hook, visited_hook=visited_hook)

        return digraph
