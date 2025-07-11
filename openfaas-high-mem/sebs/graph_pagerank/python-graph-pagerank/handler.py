import igraph
import time  # ✅ Import time for measuring latency

def graph_ops(size):
    graph = igraph.Graph.Barabasi(size, 10)
    return graph.pagerank()[0]

def handle(event, context):
    start = time.time()  # ✅ Start timing

    size = 1000
    result = graph_ops(size)

    latency_ms = (time.time() - start) * 1000  # ✅ Calculate latency in milliseconds

    return {
        "statusCode": 200,
        "body": f"{size} size graph PageRank computed! First node rank: {result:.6f}. Latency: {latency_ms:.2f} ms"
    }
