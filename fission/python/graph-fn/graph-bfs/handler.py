import igraph
import time

def graph_ops(size):
    graph = igraph.Graph.Barabasi(size, 10)
    return graph.bfs(0)

def main(input=None):

    start = time.time()
    size = 1000
    result = graph_ops(size)

    latency_ms = (time.time() - start) * 1000
    return f"{size} size graph BFS finished! Latency: {latency_ms:.2f} ms"
