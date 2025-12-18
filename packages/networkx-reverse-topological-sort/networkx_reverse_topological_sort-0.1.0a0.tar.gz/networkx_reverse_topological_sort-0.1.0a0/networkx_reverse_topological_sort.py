import networkx as nx


def reverse_topological_generations(G):
    """
    Stratifies a DAG into generations in reverse topological order.
    That is, first generation are leaves (no outgoing edges), etc.
    """
    if not G.is_directed():
        raise nx.NetworkXError("Topological sort not defined on undirected graphs.")

    multigraph = G.is_multigraph()
    # outdegree_map: only nodes with any outgoing edge
    outdegree_map = {v: d for v, d in G.out_degree() if d > 0}
    zero_outdegree = [v for v, d in G.out_degree() if d == 0]

    while zero_outdegree:
        this_generation = zero_outdegree
        zero_outdegree = []
        for node in this_generation:
            if node not in G:
                raise RuntimeError("Graph changed during iteration")
            for parent in G.predecessors(node):
                try:
                    outdegree_map[parent] -= len(G[parent][node]) if multigraph else 1
                except KeyError:
                    raise RuntimeError("Graph changed during iteration")
                if outdegree_map[parent] == 0:
                    zero_outdegree.append(parent)
                    del outdegree_map[parent]
        yield this_generation

    if outdegree_map:
        raise nx.NetworkXUnfeasible(
            "Graph contains a cycle or graph changed during iteration"
        )


def reverse_topological_sort(G):
    """
    Yields the nodes of G in reverse topological order (from leaves to roots).
    """
    for generation in reverse_topological_generations(G):
        for node in generation:
        	yield node