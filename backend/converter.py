import json
from pathlib import Path

# Resolve paths relative to this file, so it works no matter the CWD
BASE_DIR = Path(__file__).resolve().parent  
INPUT_DIR = BASE_DIR / "output"
GERMANIC_PATH = INPUT_DIR / "parser_output_baptize_germanic.json"
INDO_PATH = INPUT_DIR / "parser_output_baptize_indo.json"
WORD = GERMANIC_PATH.stem.replace("parser_output_", "").replace("_germanic", "") # Infer WORD from parser input
HIERARCHY_PATH = BASE_DIR / "languageHierarchy.json"
EXPORT_BRANCHES = {
    "germanic": "Proto-Germanic",
    "indo": "Indo-European"
}

def merge_entries(target, source):
    for lang, forms in source.items():
        if lang not in target:
            target[lang] = forms.copy()
        else:
            for f in forms:
                if f not in target[lang]:
                    target[lang].append(f)
                    
# Load input data
words_data = {}
# Load Germanic forms
with GERMANIC_PATH.open("r", encoding="utf-8") as f:
    germanic_data = json.load(f)
    merge_entries(words_data, germanic_data)

# Load Indo-European forms
with INDO_PATH.open("r", encoding="utf-8") as f:
    indo_data = json.load(f)
    merge_entries(words_data, indo_data)

# Load hierarchy
with HIERARCHY_PATH.open("r", encoding="utf-8") as f:
    hierarchy = json.load(f)

appearance_order = list(words_data.keys())
order_index = {lang: i for i, lang in enumerate(appearance_order)}
allowed = set(words_data.keys())
def find_visible_children(name):
    visible = []
    for child in hierarchy.get(name, []):
        if child in allowed:
            visible.append(child)
        else:
            visible.extend(find_visible_children(child))
    visible.sort(key=lambda x: order_index.get(x, float("inf"))) # Preserve OED appearance order
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
