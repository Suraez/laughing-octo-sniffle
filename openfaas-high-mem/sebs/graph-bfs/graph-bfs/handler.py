import igraph
import time  # ✅ For timing execution

def graph_ops(size):
    graph = igraph.Graph.Barabasi(size, 10)
    return graph.bfs(0)

def handle(event, context):
    start = time.time()  # ✅ Start measuring latency

    size = 1000
    result = graph_ops(size)

    latency_ms = (time.time() - start) * 1000  # ✅ Calculate elapsed time in ms

    return {
        "statusCode": 200,
        "body": f"{size} size graph BFS finished! Latency: {latency_ms:.2f} ms"
    }
