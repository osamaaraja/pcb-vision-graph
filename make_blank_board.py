from pathlib import Path
from PIL import Image

def main(out_path: str):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (1024, 768), (24, 80, 45))
    img.save(out_path)

    print(f"Saved - {out_path}")


if __name__ == "__main__":
    main("outputs/board.png")

