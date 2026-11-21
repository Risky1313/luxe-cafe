"""Turns drink pictures into the small square .webp files the site uses.

Usage:  python3 tools/add_photos.py <folder or files...>
Each picture must be named after its recipe id, e.g. latte.png or iced-americano.jpg
(the file names are listed in recipes/image-prompts.md). The result goes to images/<id>.webp.
Then run `node build.js` so the site picks them up.
"""
import json, pathlib, sys
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
IDS = {r["id"] for r in json.loads((ROOT / "recipes" / "recipes.json").read_text())["recipes"]}
OUT = ROOT / "images"
SIZE = 1000

def convert(src: pathlib.Path):
    rid = src.stem.lower()
    if rid not in IDS:
        print(f"skip {src.name}: no recipe with id '{rid}'"); return False
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im = ImageOps.fit(im, (SIZE, SIZE), Image.LANCZOS, centering=(0.5, 0.5))
    OUT.mkdir(exist_ok=True)
    im.save(OUT / f"{rid}.webp", "WEBP", quality=82, method=6)
    print(f"ok   {src.name} -> images/{rid}.webp"); return True

if __name__ == "__main__":
    files = []
    for a in sys.argv[1:] or ["."]:
        p = pathlib.Path(a)
        files += sorted(x for x in (p.iterdir() if p.is_dir() else [p]) if x.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    done = sum(convert(f) for f in files)
    print(f"{done} photo(s) added")
