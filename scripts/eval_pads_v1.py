
from pathlib import Path
import json, math
from pcb_partgraph.detect import detect_pads

IMAGE = "../outputs/scene_v1.png"
GRAPH = "../outputs/scene_v1.graph.json"
MATCH_TOL = 1.6 

def load_gt_pads(graph_path):
    g = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    return [n for n in g["nodes"] if n.get("type") == "pad"]

def match_greedy(dets, gts):
    used_det = set()
    tp = 0
    for gt in gts:
        gx, gy, gr = gt["x"], gt["y"], gt.get("radius", 8)
        # find nearest unused detection
        best = None
        best_d = float("inf")
        for j, d in enumerate(dets):
            if j in used_det:
                continue
            dist = math.hypot(d["x"] - gx, d["y"] - gy)
            if dist < best_d:
                best_d, best = dist, j
        if best is not None and best_d <= MATCH_TOL * gr:
            used_det.add(best)
            tp += 1
    fp = len(dets) - len(used_det)
    fn = len(gts) - tp
    return tp, fp, fn

def main():
    dets = detect_pads(IMAGE)
    gts  = load_gt_pads(GRAPH)
    tp, fp, fn = match_greedy(dets, gts)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = 2*precision*recall/(precision+recall) if (precision+recall) else 0.0

    print(f"GT pads: {len(gts)}")
    print(f"Detections: {len(dets)}")
    print(f"TP: {tp}  FP: {fp}  FN: {fn}")
    print(f"Precision: {precision:.3f}  Recall: {recall:.3f}  F1: {f1:.3f}")

if __name__ == "__main__":
    main()
