import json
from collections import defaultdict
from pathlib import Path

# Resolve paths relative to this file, so it works no matter the CWD
BASE_DIR = Path(__file__).resolve().parent      # .../visualization
ROOT_DIR = BASE_DIR.parent                      # project root
FATHER_PATH = ROOT_DIR / "output" / "father_germanic.json"
HIERARCHY_PATH = ROOT_DIR / "languageHierarchy.json"
OUTPUT_PATH = BASE_DIR / "tree_germanic.json"

# Load input data
with FATHER_PATH.open("r", encoding="utf-8") as f:
    words_data = json.load(f)

with HIERARCHY_PATH.open("r", encoding="utf-8") as f:
    hierarchy = json.load(f)

# Recursive tree builder
def build_tree(name):
    node = {"name": name}
    # Add forms if present
    if name in words_data:
        node["forms"] = words_data[name]
    node["children"] = [
        build_tree(child) for child in hierarchy[name]
    ]
    return node

# Use root to build the tree
tree = build_tree("Proto-Germanic")

# Save D3-compatible tree JSON
with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(tree, f, indent=2, ensure_ascii=False)
print(f"✅ Tree successfully built and saved to {OUTPUT_PATH}")
