import json
from pathlib import Path

# Resolve paths relative to this file, so it works no matter the CWD
BASE_DIR = Path(__file__).resolve().parent  
INPUT_DIR = BASE_DIR / "output"
FATHER_PATH = INPUT_DIR / "parser_output_father_germanic.json"
WORD = FATHER_PATH.stem.replace("parser_output_", "").replace("_germanic", "") # Infer WORD from parser input
HIERARCHY_PATH = BASE_DIR / "languageHierarchy.json"
EXPORT_BRANCHES = {
    "germanic": "Proto-Germanic",
    "indo": "Indo-European"
}

# Load input data
with FATHER_PATH.open("r", encoding="utf-8") as f:
    words_data = json.load(f)

with HIERARCHY_PATH.open("r", encoding="utf-8") as f:
    hierarchy = json.load(f)

# Recursive tree builder
def build_tree(name):
    node = {"name": name}
    if name in words_data: # Add forms if present
        node["forms"] = words_data[name]
    node["children"] = [
        build_tree(child) for child in hierarchy[name]
    ]
    return node

for branch, root in EXPORT_BRANCHES.items():
    tree = build_tree(root)
    output_path = INPUT_DIR / f"converter_output_{WORD}_{branch}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"✅ Tree successfully built and saved to {output_path}")
