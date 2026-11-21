"""Builds the ChatGPT image prompts (one per drink) from recipes.json + looks.py.
Run: python3 build_prompts.py  ->  writes image-prompts.md and prompts.json next to this file
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from looks import LOOKS

STYLE = ("Setting: a pale, warm stone-gray countertop, a plain softly blurred stone-colored background, "
         "and soft warm golden window light from the side.")
RULES = ("Show only what is described: no extra garnishes, straws, napkins, text, logos, labels, people or hands.")

def angle(look):
    cup = re.split(r"[,:]", look)[0].lower()  # just the vessel part
    if "clear" in cup or " glass" in cup:
        return ("Camera: low three-quarter view from just above eye level, so the layers through the glass "
                "and the top of the drink are both visible, shallow depth of field, drink centered and sharp.")
    return ("Camera: about 45 degrees above the cup so the surface of the drink is clearly visible, "
            "shallow depth of field, drink centered and sharp.")

def prompt(rid):
    look, props = LOOKS[rid]
    extra = ("Nothing else in the frame besides the drink." if props.strip().lower() == "nothing else"
             else f"Also in frame: {props}.")
    return (f"Photorealistic editorial drink photo, square 1:1 format. Subject: {look}. {extra} "
            f"{STYLE} {angle(look)} {RULES}")

def main():
    data = json.load(open(os.path.join(HERE, "recipes.json")))
    cats = {c["id"]: c["name"] for c in data["categories"]}
    out, md = [], ["# ChatGPT image prompts, Luxe Café Pro recipes", "",
                   "One prompt per drink. Save each picture with the file name shown, e.g. `latte.png`.", ""]
    for cid in cats:
        md += [f"## {cats[cid]}", ""]
        for r in [r for r in data["recipes"] if r["category"] == cid]:
            p = prompt(r["id"])
            out.append({"id": r["id"], "name": r["name"], "cat": cid, "catName": cats[cid],
                        "ninja": r["source"]["kind"] == "ninja", "file": r["id"] + ".png", "prompt": p})
            md += [f"### {r['name']}", f"Save as: `{r['id']}.png`", "", "```", p, "```", ""]
    missing = [r["id"] for r in data["recipes"] if r["id"] not in LOOKS]
    assert not missing, missing
    json.dump(out, open(os.path.join(HERE, "prompts.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(HERE, "image-prompts.md"), "w").write("\n".join(md))
    print(len(out), "prompts written")

if __name__ == "__main__":
    main()
