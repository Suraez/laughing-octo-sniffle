import igraph

def graph_ops(size):
    graph = igraph.Graph.Barabasi(size, 10)
    return graph.spanning_tree(None, False)

def handle(event, context):
    size = 1000
    result = graph_ops(size)

    return {
        "statusCode": 200,
        "body": f"{size} size graph MST finished!"
    }
