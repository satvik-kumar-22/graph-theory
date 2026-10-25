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
