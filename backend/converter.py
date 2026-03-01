import json
from pathlib import Path

# Resolve paths relative to this file, so it works no matter the CWD
BASE_DIR = Path(__file__).resolve().parent  
INPUT_DIR = BASE_DIR / "output"
GERMANIC_PATH = INPUT_DIR / "parser_output_father_germanic.json"
INDO_PATH = INPUT_DIR / "parser_output_father_indo.json"
WORD = GERMANIC_PATH.stem.replace("parser_output_", "").replace("_germanic", "") # Infer WORD from parser input
HIERARCHY_PATH = BASE_DIR / "languageHierarchy.json"
EXPORT_BRANCHES = {
    "germanic": "Proto-Germanic",
    "indo": "Indo-European"
}

# Load input data
words_data = {}

# Load Germanic forms
with GERMANIC_PATH.open("r", encoding="utf-8") as f:
    germanic_data = json.load(f)
    words_data.update(germanic_data)

# Load Indo-European forms
with INDO_PATH.open("r", encoding="utf-8") as f:
    indo_data = json.load(f)
    words_data.update(indo_data)

# Load hierarchy
with HIERARCHY_PATH.open("r", encoding="utf-8") as f:
    hierarchy = json.load(f)

allowed = set(words_data.keys())
def find_visible_children(name):
    visible = []
    for child in hierarchy.get(name, []):
        if child in allowed:
            visible.append(child)
        else:
            visible.extend(find_visible_children(child)) # skip this node but keep searching below it
    return visible

def build_tree(name):
    node = {"name": name}
    forms = words_data.get(name)
    if forms:
        node["forms"] = forms
    node["children"] = [
        build_tree(child)
        for child in find_visible_children(name)
    ]
    return node

for branch, root in EXPORT_BRANCHES.items():
    tree = build_tree(root)
    output_path = INPUT_DIR / f"converter_output_{WORD}_{branch}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"✅ Tree successfully built and saved to {output_path}")
