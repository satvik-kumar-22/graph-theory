from graph import Graph

class Tree(Graph):

    """A subclass of Graph that represents a connected acyclic graph (also known as a tree).
    This allows us to implement various algorithms and methods regarding trees."""

    def __init__(self, adjacency_matrix: list[list[int]]) -> None:

        super().__init__(adjacency_matrix)

        if not self.is_acyclic():
            raise ValueError("Graph provided has cycles in it.")

        if not self.is_connected():
            raise ValueError("Graph provided is not connected.")
