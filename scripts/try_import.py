import pcb_partgraph
print(pcb_partgraph.ping())
from pcb_partgraph.detect import detect_pads
pads = detect_pads("../outputs/scene_v1.png")  # or your latest image path
print("pads found:", len(pads))
print(pads)
