# graph.py
A lightweight Python module for working with directed and undirected graphs using adjacency matrices.
The project provides mutable graph data structures with common graph algorithms and methods.

## Features

### Directed Graphs

The `Digraph` class represents a simple directed graph using an adjacency matrix.

Supported functionality includes:

- Create directed graphs from adjacency matrices
- Automatically simplify loops and multiple edges
- Add and remove vertices
- Read and update edges with `graph[i, j]` syntax
- Compute vertex and edge counts
- Get indegrees and outdegrees
- Find neighbors, inneighbors, and outneighbors
- Generate induced subdigraphs
- Convert to:
  - adjacency lists
  - edge lists
  - incidence matrices
- Run depth-first search and breadth-first search
- Build DFS and BFS trees or forests
- Check whether a path exists between two vertices
- Find paths and shortest paths
- Count paths of a fixed length between two vertices
- Find strongly connected components using Kosaraju's algorithm
- Build the condensation graph

### Undirected Graphs

The `Graph` class is a subclass of the `Digraph` class for undirected graphs.

Supported functionality includes:

- Validate symmetric adjacency matrices
- Check graph connectivity
- Find connected components
- Find bridges using Tarjan's algorithm
- Generate complete graphs using `Graph.K(n)` and complete bipartite graphs using `Graph.K(m, n)`
- Compute strong orientations when possible

## Requirements

- Python 3.14+
- No third-party runtime dependencies

## Usage

Import graph at the top of your Python file:

```
import graph
```

### Creating a Directed Graph

You can pass in an adjacency matrix. For example:
```
g = Digraph([
    [0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 0, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 0, 0, 0]
])
    
print(g.vertex_number) # 5
print(g.edge_number) # 10
```

Loops are automatically removed when passed to the constructor (diagonal elements
are zeroed out). Also, multiple edges are removed (every entry is 0 or 1). This
makes the graph simple.

### Checking Edges

In the above graph:

```
print(g[0, 4]) # 0
print(g[2, 3]) # 1
``` 

### Updating Edges

We can set edges within a graph in the following way:

```
g[0, 4] = 1
g[2, 3] = 0
```

### Finding Neighbors
```
print(g.outneighbors(0)) # {2, 3}
print(g.inneighbors(0)) # {0, 4} 
print(g.neighbors(0)) # {0, 2, 3, 4}
``` 

### Paths

```
print(g.path_exists(0, 2)) # True
print(g.path(0, 2)) # [0, 1, 2]
print(g.shortest_path(0, 2)) # [0, 2]
```

### Strongly Connected Components

In this case, our graph `g` is strongly connected.

```
print(g.strongly_connected_components()) # [{0, 1, 2, 3, 4}]
```

### Condensation Graph
```
python condensation = g.condensation()
print(condensation) # You can probably guess what this would look like
```

### Creating an Undirected Graph

This is an example of a 6 x 6 graph. In order for an undirected graph
to be constructed, the adjacency matrix must be symmetric.

```
import graph

h = graph.Graph([
    [0, 1, 1, 0, 0, 0],
    [1, 0, 1, 0, 0, 0],
    [1, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1],
    [0, 0, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 0]
])

print(h.is_connected()) # True
print(h.connected_components()) # [{0, 1, 2, 3, 4, 5}]
print(h.bridges()) # [{2, 3}]
``` 

### Complete Graphs

Create a complete undirected graph with `n` vertices:

```
n = 4
i = Graph.K(n)
print(i)

# 0 1 1 1
# 1 0 1 1
# 1 1 0 1
# 1 1 1 0
```

Create a complete undirected bipartite graph of order `m, n`:
```
m = 2
n = 3

j = Graph.K(m, n)
print(j)

# 0 0 1 1 1
# 0 0 1 1 1
# 1 1 0 0 0
# 1 1 0 0 0
# 1 1 0 0 0
```

Create a complete directed bipartite graph of order `m, n`:
```
m = 2
n = 3

k = Digraph.K(m, n)
print(k)

# 0 0 1 1 1
# 0 0 1 1 1
# 0 0 0 0 0
# 0 0 0 0 0
# 0 0 0 0 0
```

### Conversions

Use the following syntax to convert graphs into:

- Adjacency Matrices

```
adjacency_list = g.as_adjacency_list()
print(adjacency_list)
``` 

- Edge List

```
edge_list = g.as_edge_list()
print(edge_list)
```

- Incidence Matrix

```
incidence_matrix = g.as_incidence_matrix()
print(incidence_matrix)
``` 

## Development

This project only uses the Python standard library.

## Notes

- Vertices are represented by integer indices.
- Vertex numbering starts at `0`.
- Graphs are represented internally with adjacency matrices.
- All graphs are simplified on creation:
  - loops are removed
  - multiple edges are collapsed to a single edge
- The null graph is not supported.

## Roadmap

Possible future additions include:

- Random graph generation
- Topological sorting
- Reachability matrices
- Bipartite graph checks
- Graph isomorphism checks
- Cycle detection
- Articulation point detection
- Minimum spanning trees
- Planarity checks
- Graph coloring
- Eulerian and Hamiltonian path utilities
