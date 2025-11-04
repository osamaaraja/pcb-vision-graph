from pathlib import Path
import json
from PIL import Image, ImageDraw

BOARD_W, BOARD_H = 1024, 768
BOARD_COLOR = (24, 80, 45)
COMP_COLOR = (30, 30, 30)
SILK = (230, 230, 230)
PAD_COLOR   = (230, 200, 80)

TRACE_COLOR = (200, 200, 60)


def rect_from_center(cx, cy, w, h):
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2
    return x0, y0, x1, y1

def main():
    out_img = Path("../outputs/scene_v1.png")
    out_graph = Path("../outputs/scene_v1.graph.json")
    out_img.parent.mkdir(exist_ok=True, parents=True)

    img = Image.new("RGB", (BOARD_W, BOARD_H), BOARD_COLOR)
    draw = ImageDraw.Draw(img)

    nodes = []
    edges = []

    # defining the component with two pads
    u1_cx, u1_cy = 512, 300
    u1_w, u1_h = 240, 120
    u1_x0, u1_y0, u1_x1, u1_y1 = rect_from_center(u1_cx, u1_cy, u1_w, u1_h)
    u1_x1, u1_y1 = u1_cx+u1_w//2, u1_cy+u1_h//2
    draw.rectangle([u1_x0, u1_y0, u1_x1, u1_y1], fill=COMP_COLOR)
    draw.text((u1_cx + 10, u1_cy - 10), "U1", fill=SILK)
    nodes.append({"id": "U1", "type": "component", "label": "U1",
                  "x": u1_cx, "y": u1_cy, "bbox": [u1_x0, u1_y0, u1_x1, u1_y1]})

    # placing pad - U1
    pad_r = 8
    u1_1_x, u1_1_y = u1_x0 - 10, u1_cy
    u1_2_x, u1_2_y = u1_x1 + 10, u1_cy
    draw.ellipse([u1_1_x - pad_r, u1_1_y - pad_r, u1_1_x + pad_r, u1_1_y + pad_r], fill=PAD_COLOR)
    draw.ellipse([u1_2_x - pad_r, u1_2_y - pad_r, u1_2_x + pad_r, u1_2_y + pad_r], fill=PAD_COLOR)

    nodes += [
        {"id": "U1_1", "type": "pad", "label": "U1.1", "x": u1_1_x, "y": u1_1_y, "radius": pad_r},
        {"id": "U1_2", "type": "pad", "label": "U1.2", "x": u1_2_x, "y": u1_2_y, "radius": pad_r},
    ]
    edges += [
        {"source": "U1", "target": "U1_1", "type": "belongs_to"},
        {"source": "U1", "target": "U1_2", "type": "belongs_to"},
    ]

    # resistor
    r1_cx, r1_cy = 360, 520
    r1_w, r1_h = 140, 60
    r1_x0, r1_y0, r1_x1, r1_y1 = rect_from_center(r1_cx, r1_cy, r1_w, r1_h)
    draw.rectangle([r1_x0, r1_y0, r1_x1, r1_y1], fill=COMP_COLOR)
    draw.text((r1_cx + 10, r1_cy - 10), "R1", fill=SILK)
    nodes.append({"id": "R1", "type": "component", "label": "R1",
                  "x": r1_cx, "y": r1_cy, "bbox": [r1_x0, r1_y0, r1_x1, r1_y1]})

    r1_1_x, r1_1_y = r1_x1 + 10, r1_cy
    draw.ellipse([r1_1_x - pad_r, r1_1_y - pad_r, r1_1_x + pad_r, r1_1_y + pad_r], fill=PAD_COLOR)
    nodes.append({"id": "R1_1", "type": "pad", "label": "R1.1", "x": r1_1_x, "y": r1_1_y, "radius": pad_r})
    edges.append({"source": "R1", "target": "R1_1", "type": "belongs_to"})


    # trace from U1_1 to the resistor
    polyline = [(u1_1_x, u1_1_y), (u1_1_x, r1_1_y), (r1_1_x, r1_1_y)]
    draw.line(polyline, fill=TRACE_COLOR, width=6)
    edges.append({"source": "U1_1", "target": "R1_1", "type": "trace",
                  "polyline": polyline})

    img.save(out_img)

    # graph node
    graph = {
        "image": {"path": str(out_img).replace("\\", "/"), "width": BOARD_W, "height": BOARD_H},
        "nodes": nodes,
        "edges": edges,
    }

    out_graph.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Wrote {out_img} and {out_graph}")

if __name__ == "__main__":
    main()