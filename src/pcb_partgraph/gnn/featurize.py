from pathlib import Path
import json
import numpy as np
from typing import Dict, Any, List, Tuple

# map string types to indices for one-hot encodings
NODE_TYPES = {"component": 0, "pad": 1}
EDGE_TYPES = {"belongs_to": 0, "trace": 1}

def load_graph(graph_path):
    return json.loads(Path(graph_path).read_text(encoding="utf-8"))

def featurize_graph(g):
    W, H = g["image"]["width"], g["image"]["height"]
    nodes = g["nodes"]; edges = g["edges"]

    # index nodes
    id2idx = {n["id"]: i for i, n in enumerate(nodes)}
    N = len(nodes)

    degree = np.zeros((N,), dtype=np.float32)

    # edge_index (directed both ways) and edge_attr (one-hot)
    ei_src: List[int] = []
    ei_dst: List[int] = []
    ea: List[List[float]] = []

    for e in edges:
        t = EDGE_TYPES.get(e["type"], 0)
        s = id2idx[e["source"]]; d = id2idx[e["target"]]
        ei_src += [s, d]; ei_dst += [d, s]
        ea += [[1.0 if t == 0 else 0.0, 1.0 if t == 1 else 0.0]] * 2
        degree[s] += 1; degree[d] += 1

    edge_index = np.asarray([ei_src, ei_dst], dtype=np.int64)
    edge_attr  = np.asarray(ea, dtype=np.float32)

    X = np.zeros((N, 2 + 2 + 2 + 1), dtype=np.float32)
    for i, n in enumerate(nodes):
        # type one-hot
        t_idx = NODE_TYPES.get(n["type"], 0)
        X[i, t_idx] = 1.0

        # position normalized
        X[i, 2] = float(n["x"]) / float(W)
        X[i, 3] = float(n["y"]) / float(H)

        # size features
        if n["type"] == "pad":
            r = float(n.get("radius", 0.0))
            X[i, 4] = r / max(W, H)  # size1
            X[i, 5] = 0.0            # size2 unused for pads
        else:  # component
            x0, y0, x1, y1 = n["bbox"]
            w = (x1 - x0) / W
            h = (y1 - y0) / H
            X[i, 4] = w             # size1
            X[i, 5] = h             # size2

        # degree normalized
        X[i, 6] = degree[i] / max(1.0, float(N - 1))

    return {
        "node_ids": [n["id"] for n in nodes],
        "edge_types": [e["type"] for e in edges],
        "x": X,                     # (N, 7) node features
        "edge_index": edge_index,   # (2, E*2) directed both ways
        "edge_attr": edge_attr,     # (E*2, 2) one-hot for edge type
    }
