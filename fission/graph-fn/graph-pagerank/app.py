def main(input=None):
    import igraph
    import time

    start = time.time()
    size = 1000
    graph = igraph.Graph.Barabasi(size, 10)
    result = graph.pagerank()[0]
    latency_ms = (time.time() - start) * 1000
    return f"{size} size graph PageRank computed! First node rank: {result:.6f}. Latency: {latency_ms:.2f} ms"
