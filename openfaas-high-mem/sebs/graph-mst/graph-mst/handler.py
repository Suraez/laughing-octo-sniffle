import igraph
import time  # ✅ For timing

def graph_ops(size):
    graph = igraph.Graph.Barabasi(size, 10)
    return graph.spanning_tree(None, False)

def handle(event, context):
    start = time.time()  # ✅ Start timing

    size = 1000
    result = graph_ops(size)

    latency_ms = (time.time() - start) * 1000  # ✅ Calculate latency in milliseconds

    return {
        "statusCode": 200,
        "body": f"{size} size graph MST finished! Latency: {latency_ms:.2f} ms"
    }
