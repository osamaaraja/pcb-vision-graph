from pathlib import Path
import json
from PIL import Image, ImageDraw

BOARD_W, BOARD_H = 1024, 768
BOARD_COLOR = (24, 80, 45)
COMP_COLOR = (30, 30, 30)
SILK = (230, 230, 230)

def main():
    out_img = Path("../outputs/component_v1.png")
    out_graph = Path("../outputs/component_v1.graph.json")
    out_img.parent.mkdir(exist_ok=True, parents=True)

    img = Image.new("RGB", (BOARD_W, BOARD_H), BOARD_COLOR)
    draw = ImageDraw.Draw(img)

    # defining the component
    cx, cy = 512, 300
    w, h = 240, 120
    x0, y0 = cx-w//2, cy-h//2
    x1, y1 = cx+w//2, cy+h//2

    draw.rectangle((x0, y0, x1, y1), fill=COMP_COLOR)
    draw.text((cx+10, cy-10), "U1", fill=SILK)

    img.save(out_img)

    # graph node
    graph = {
        "image": {"path": str(out_graph).replace("\\", "/"), "width": BOARD_W, "height": BOARD_H},
        "nodes": [{"id":"U1", "type":"component", "label":"U1", "x":cx, "y":cy, "bbox":[x0, y0, x1, y1]}],
        "edges": [],
    }

    out_graph.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Wrote {out_img} and {out_graph}")

if __name__ == "__main__":
    main()