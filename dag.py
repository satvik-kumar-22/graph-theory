from graph import Digraph

class Dag(Digraph):

    """A subclass of Digraph that necessarily has no cycles, creating a directed acyclic graph (DAG).
    This allows us to implement various algorithms and methods regarding DAGs, including:

    - topological sorting (Kahn's algorithm)
    """

    def __init__(self, adjacency_matrix: list[list[int]]) -> None:

        super().__init__(adjacency_matrix)

        if not self.is_acyclic():
            raise ValueError("Directed graph provided has cycles in it.")

        self._parents = {i: set() for i in range(self.vertex_number)}
        self._children = {i: set() for i in range(self.vertex_number)}

        for i, j in self.indices():
            if self[i, j]:
                self._children[i].add(j)
                self._parents[j].add(i)

    def indegree(self, vertex: int) -> int:

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return len(self._parents[vertex])

    def outdegree(self, vertex: int) -> int:

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return len(self._children[vertex])

    def parents(self, vertex: int) -> set[int]:

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return self._parents[vertex]

    def children(self, vertex: int) -> set[int]:

        if not self.is_vertex(vertex):
            raise ValueError("Received invalid vertex name")

        return self._children[vertex]

    def sources(self):

        return {v for v in range(self.vertex_number) if not self.indegree(v)}

    def sinks(self):

        return {v for v in range(self.vertex_number) if not self.outdegree(v)}

    def topological_sort(self) -> list[int]:

        indegs = [self.indegree(v) for v in range(self.vertex_number)]

        sort = []

        sources = {v for v in range(self.vertex_number) if indegs[v] == 0}
        print(sources)

        while sources:

            new_sources = set()

            for source in sources:

                sort.append(source)

                for i in self.children(source):
                    if indegs[i] == 1:
                        new_sources.add(i)
                    indegs[i] -= 1

            sources = new_sources

        return sort
