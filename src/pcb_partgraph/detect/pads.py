
from typing import List, Dict, Tuple
import math
import numpy as np
from PIL import Image

PAD_COLOR = np.array([230, 200, 80], dtype=np.int16)
COLOR_TOL = 25      # per-channel tolerance
MIN_AREA  = 40      # min pixels in a blob to count

def _pad_mask(image_path: str) -> np.ndarray:

    arr = np.asarray(Image.open(image_path).convert("RGB")).astype(np.int16)  # (H,W,3)
    diff = np.abs(arr - PAD_COLOR)                                            # (H,W,3)
    return (diff.max(axis=2) <= COLOR_TOL)                                    # (H,W)

def _components(mask: np.ndarray) -> List[List[Tuple[int,int]]]:
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    comps: List[List[Tuple[int,int]]] = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                stack = [(x, y)]
                seen[y, x] = True
                pixels: List[Tuple[int,int]] = []
                while stack:
                    cx, cy = stack.pop()
                    pixels.append((cx, cy))
                    for ny in (cy-1, cy, cy+1):
                        for nx in (cx-1, cx, cx+1):
                            if nx == cx and ny == cy:
                                continue
                            if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                stack.append((nx, ny))
                if len(pixels) >= MIN_AREA:
                    comps.append(pixels)
    return comps

def _centroid_and_radius(pixels: List[Tuple[int,int]]) -> Dict[str, float]:
    xs = np.fromiter((p[0] for p in pixels), dtype=np.float32)
    ys = np.fromiter((p[1] for p in pixels), dtype=np.float32)
    cx, cy = float(xs.mean()), float(ys.mean())
    r = float(math.sqrt(len(pixels) / math.pi))
    return {"x": cx, "y": cy, "r": r}

def detect_pads(image_path: str) -> List[Dict[str, float]]:
    mask = _pad_mask(image_path)
    return [_centroid_and_radius(pix) for pix in _components(mask)]
