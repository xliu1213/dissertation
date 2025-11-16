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

# Build lookup tables
# Map language -> forms (from the flat father_germanic.json list)
forms_lookup = {entry["language"]: entry["forms"] for entry in words_data} 

# Map parent -> list of children (every language included as a key)
children = {lang: [] for lang in hierarchy}   # initialize all languages with empty list
for lang, parent in hierarchy.items():
    if parent is not None:                    # if it has a parent, add it as a child
        children[parent].append(lang)

# Recursive tree builder
def build_tree(name):
    node = {"name": name}
    # Attach forms 
    if name in forms_lookup:
        node["forms"] = forms_lookup[name]
    # Attach children if this language has descendants in the hierarchy
    if name in children:
        node["children"] = [build_tree(child) for child in children[name]]
    return node

# Find root and build the tree
root = None
for lang, parent in hierarchy.items():
    if parent is None:
        root = lang
        break
tree = build_tree(root)

# Save D3-compatible tree JSON
with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(tree, f, indent=2, ensure_ascii=False)

print(f"✅ Tree successfully built and saved to {OUTPUT_PATH}")
