from collections import defaultdict

def invert_graph(graph):
    inv = defaultdict(set)
    for src, deps in graph.items():
        for d in deps:
            inv[d].add(src)
    return inv
