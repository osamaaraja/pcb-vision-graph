from pcb_partgraph.gnn.featurize import load_graph, featurize_graph

GRAPH = "../outputs/scene_v1.graph.json"

def main():
    g = load_graph(GRAPH)
    data = featurize_graph(g)
    x = data["x"]; ei = data["edge_index"]; ea = data["edge_attr"]
    print("nodes:", len(data["node_ids"]))
    print("x.shape:", x.shape)            # (N, 7)
    print("edge_index.shape:", ei.shape)  # (2, 2E)
    print("edge_attr.shape:", ea.shape)   # (2E, 2)

if __name__ == "__main__":
    main()
