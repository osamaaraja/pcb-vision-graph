from pathlib import Path
import json, math
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw
from pcb_partgraph.detect import detect_pads

IMAGE = "../outputs/scene_v1.png"
GRAPH = "../outputs/scene_v1.graph.json"
OUT   = "../outputs/scene_v1.pads.overlay.png"
MATCH_TOL = 1.6

def load_gt_pads(graph_path):
    g = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    return [n for n in g["nodes"] if n.get("type") == "pad"]

def match_greedy(dets, gts):

    used_det = set()
    matches: List[Tuple[int,int]] = []
    for gi, gt in enumerate(gts):
        gx, gy, gr = gt["x"], gt["y"], gt.get("radius", 8)
        best, best_d = None, float("inf")
        for dj, d in enumerate(dets):
            if dj in used_det:
                continue
            dist = math.hypot(d["x"] - gx, d["y"] - gy)
            if dist < best_d:
                best, best_d = dj, dist
        if best is not None and best_d <= MATCH_TOL * gr:
            used_det.add(best)
            matches.append((gi, best))
    matched_g = {gi for gi, _ in matches}
    matched_d = {dj for _, dj in matches}
    fp_idx = [j for j in range(len(dets)) if j not in matched_d]
    fn_idx = [i for i in range(len(gts))  if i not in matched_g]
    return matches, fp_idx, fn_idx

def draw_overlay(image_path, gts, dets,
                 matches: List[Tuple[int,int]], fp_idx, fn_idx,
                 out_path):
    # colors
    BLUE  = (80, 160, 255)   # GT rings
    GREEN = (60, 220, 120)   # matched detections
    RED   = (240, 80, 80)    # false positives
    PURP  = (190, 90, 220)   # missed GT highlight

    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    for i, gt in enumerate(gts):
        r = int(gt.get("radius", 8))
        x, y = gt["x"], gt["y"]
        draw.ellipse([x-r-2, y-r-2, x+r+2, y+r+2], outline=BLUE, width=2)

    matched_d = {dj for _, dj in matches}
    for _, dj in matches:
        d = dets[dj]
        r = int(max(4, d["r"]))
        x, y = int(d["x"]), int(d["y"])
        draw.ellipse([x-r, y-r, x+r, y+r], outline=GREEN, width=2)

    for j in fp_idx:
        d = dets[j]
        r = int(max(4, d["r"]))
        x, y = int(d["x"]), int(d["y"])
        draw.ellipse([x-r, y-r, x+r, y+r], outline=RED, width=2)

    for i in fn_idx:
        gt = gts[i]
        r = int(gt.get("radius", 8))
        x, y = gt["x"], gt["y"]
        draw.ellipse([x-r-3, y-r-3, x+r+3, y+r+3], outline=PURP, width=3)
        draw.line([x-6, y, x+6, y], fill=PURP, width=2)
        draw.line([x, y-6, x, y+6], fill=PURP, width=2)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)

def main():
    dets = detect_pads(IMAGE)
    gts  = load_gt_pads(GRAPH)
    matches, fp_idx, fn_idx = match_greedy(dets, gts)

    tp = len(matches); fp = len(fp_idx); fn = len(fn_idx)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = 2*precision*recall/(precision+recall) if (precision+recall) else 0.0

    print(f"GT pads: {len(gts)}")
    print(f"Detections: {len(dets)}")
    print(f"TP: {tp}  FP: {fp}  FN: {fn}")
    print(f"Precision: {precision:.3f}  Recall: {recall:.3f}  F1: {f1:.3f}")

    draw_overlay(IMAGE, gts, dets, matches, fp_idx, fn_idx, OUT)
    print(f"Saved overlay → {Path(OUT).resolve()}")

if __name__ == "__main__":
    main()
