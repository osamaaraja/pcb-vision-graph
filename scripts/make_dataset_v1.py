from pathlib import Path
import json, random
from typing import List, Tuple
from PIL import Image, ImageDraw


BOARD_W, BOARD_H = 1024, 768
BOARD_COLOR = (24, 80, 45)
COMP_COLOR  = (30, 30, 30)
PAD_COLOR   = (230, 200, 80)
TRACE_COLOR = (200, 200, 60)
SILK        = (230, 230, 230)


def rect_from_center(cx, cy, w, h):
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2
    return x0, y0, x1, y1

def draw_component(draw: ImageDraw.ImageDraw, label, cx, cy, w, h):
    x0, y0, x1, y1 = rect_from_center(cx, cy, w, h)
    draw.rectangle([x0, y0, x1, y1], fill=COMP_COLOR)
    draw.text((cx + 10, cy - 10), label, fill=SILK)
    node = {"id": label, "type": "component", "label": label, "x": cx, "y": cy, "bbox": [x0, y0, x1, y1]}
    return node, (x0, y0, x1, y1)

def draw_pad(draw: ImageDraw.ImageDraw, parent_label, idx, x, y, r = 8):
    draw.ellipse([x - r, y - r, x + r, y + r], fill=PAD_COLOR)
    pid = f"{parent_label}_{idx}"
    node = {"id": pid, "type": "pad", "label": f"{parent_label}.{idx}", "x": x, "y": y, "radius": r}
    edge = {"source": parent_label, "target": pid, "type": "belongs_to"}
    return node, edge

def draw_trace(draw: ImageDraw.ImageDraw, src_xy, dst_xy):
    (sx, sy), (dx, dy) = src_xy, dst_xy
    polyline = [(sx, sy), (sx, dy), (dx, dy)]  # simple L-shape
    draw.line(polyline, fill=TRACE_COLOR, width=6)
    return polyline

def ensure_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def validate_graph(g):
    ids = [n["id"] for n in g["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate node ids"
    node_ids = set(ids)
    for e in g["edges"]:
        assert e["source"] in node_ids and e["target"] in node_ids, "edge references unknown node"

def make_one_sample(out_img: Path, out_graph: Path, rng: random.Random):
    img = Image.new("RGB", (BOARD_W, BOARD_H), BOARD_COLOR)
    draw = ImageDraw.Draw(img)

    nodes, edges = [], []

    # U1 near top-middle, R1 lower-left with jitter
    u1_cx = 480 + rng.randint(-40, 40)
    u1_cy = 260 + rng.randint(-25, 25)
    u1_w, u1_h = 240, 120

    r1_cx = 340 + rng.randint(-30, 30)
    r1_cy = 520 + rng.randint(-30, 30)
    r1_w, r1_h = 140, 60

    # draw components
    u1_node, (u1_x0, _, u1_x1, _) = draw_component(draw, "U1", u1_cx, u1_cy, u1_w, u1_h)
    r1_node, (r1_x0, r1_y0, r1_x1, r1_y1) = draw_component(draw, "R1", r1_cx, r1_cy, r1_w, r1_h)
    nodes += [u1_node, r1_node]

    # pads
    pad_r = 8
    u1_1_x, u1_1_y = u1_x0 - 10, u1_cy
    u1_2_x, u1_2_y = u1_x1 + 10, u1_cy
    n_u1_1, e_u1_1 = draw_pad(draw, "U1", 1, u1_1_x, u1_1_y, pad_r)
    n_u1_2, e_u1_2 = draw_pad(draw, "U1", 2, u1_2_x, u1_2_y, pad_r)
    nodes += [n_u1_1, n_u1_2]; edges += [e_u1_1, e_u1_2]

    r1_1_x, r1_1_y = r1_x1 + 10, r1_cy
    n_r1_1, e_r1_1 = draw_pad(draw, "R1", 1, r1_1_x, r1_1_y, pad_r)
    nodes.append(n_r1_1); edges.append(e_r1_1)

    # one trace U1_1 to R1_1
    poly = draw_trace(draw, (u1_1_x, u1_1_y), (r1_1_x, r1_1_y))
    edges.append({"source": "U1_1", "target": "R1_1", "type": "trace", "polyline": poly})

    ensure_dir(out_img); img.save(out_img)
    graph = {"image": {"path": out_img.as_posix(), "width": BOARD_W, "height": BOARD_H},
             "nodes": nodes, "edges": edges}
    out_graph.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    validate_graph(graph)

def main(n: int = 5, seed: int = 0, out_dir: str = "../data/ds_v1"):
    rng = random.Random(seed)
    root = Path(out_dir)
    for i in range(1, n + 1):
        sample_dir = root / f"sample_{i:04d}"
        img_path   = sample_dir / "pcb.png"
        graph_path = sample_dir / "graph.json"
        make_one_sample(img_path, graph_path, rng)
    print(f"Wrote {n} samples under {root}")

if __name__ == "__main__":
    main()
