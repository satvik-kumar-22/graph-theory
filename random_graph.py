from graph import Digraph, Graph
from random import random, sample
from itertools import product

class GilbertDigraph(Digraph):

    """This class implements the Gilbert random digraph model
    G(n, p), which takes in a number of vertices n and a probability p.
    For each possible edge between two vertices, there is a probability p
    that it will be drawn in this model. As such, n^2 - n independent
    trials are run using random.random() to draw edges."""

    def __init__(self, n: int, p: float):

        if not isinstance(n, int):
            raise TypeError("n must be an integer")
        if n <= 0:
            raise ValueError("n must be positive")
        if not isinstance(p, float):
            raise TypeError("p must be a float.")
        if not (0.0 < p < 1.0):
            raise ValueError("p must strictly be in between 0.0 and 1.0.")

        adj = [[int(random() < p) for _ in range(n)] for __ in range(n)]

        # Automatically simplifies loops
        super().__init__(adj)

class GilbertGraph(Graph):

    """This class implements the Gilbert graph model. This is basically
    the same as the digraph model, except now, we run (n^2 - n)/2 trials,
    one for each pair of vertices."""

    def __init__(self, n: int, p: float):

        if not isinstance(n, int):
            raise TypeError("n must be an integer")
        if n <= 0:
            raise ValueError("n must be positive")
        if not isinstance(p, float):
            raise TypeError("p must be a float.")
        if not (0.0 < p < 1.0):
            raise ValueError("p must strictly be in between 0.0 and 1.0.")

        adj = [[0 for _ in range(n)] for __ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                edge = int(random() < p)
                adj[i][j] = edge
                adj[j][i] = edge

        super().__init__(adj)

class ErdosRenyiDigraph(Digraph):

    """This class implements the Erdős-Rényi random digraph model
    G(n, M), which takes in a number of vertices n and a number of edges M.
    M edges are randomly chosen from the n^2 - n possible edges to create the
    graph."""

    def __init__(self, n: int, M: int):

        if not isinstance(n, int):
            raise TypeError("n must be an integer")
        if n <= 0:
            raise ValueError("n must be positive")
        if not isinstance(M, int):
            raise TypeError("M must be an integer")
        if not (0 < M < n * (n - 1)):
            raise ValueError("M must be in between 0 and n^2 - n.")

        # Get the specific edges to be drawn
        edges = set(sample(range(n * (n - 1)), k=M))

        # Empty adjacency matrix
        adj = [[0 for _ in range(n)] for __ in range(n)]

        counter = 0

        for i, j in product(range(n), range(n)):

            # Skip over loops
            if i == j:
                continue

            # Draw edge if the counter is in the set of edges
            if counter in edges:
                adj[i][j] = 1

            counter += 1

        super().__init__(adj)

class ErdosRenyiGraph(Graph):

    """This class implements the Erdős-Rényi random graph model,
    which is basically the same as the digraph model, except
    now M is the number of undirected edges chosen among
    (n^2 - n)/2 possible edges."""

    def __init__(self, n: int, M: int):

        if not isinstance(n, int):
            raise TypeError("n must be an integer")
        if n <= 0:
            raise ValueError("n must be positive")
        if not isinstance(M, int):
            raise TypeError("M must be an integer")
        if not (0 < M < (n * (n - 1)) // 2):
            raise ValueError("M must be in between 0 and n^2 - n.")

        # Get the specific edges to be drawn
        edges = set(sample(range((n * (n - 1)) // 2), k=M))

        # Empty adjacency matrix
        adj = [[0 for _ in range(n)] for __ in range(n)]

        counter = 0

        for i in range(n):
            for j in range(i + 1, n):

                # Draw edge if the counter is in the set of edges
                if counter in edges:
                    adj[i][j] = 1

                counter += 1

        super().__init__(adj)
