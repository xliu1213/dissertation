import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent   # D:\Desktop\Dissertation\code\backend
INPUT_DIR = BASE_DIR / "output" # D:\Desktop\Dissertation\code\backend\output
HIERARCHY_PATH = BASE_DIR / "languageHierarchy.json" # D:\Desktop\Dissertation\code\backend\languageHierarchy.json
EXPORT_BRANCHES = {
    "germanic": "Proto-Germanic",
    "indo": "Indo-European"
}

PARSER_OUTPUT_PATH = INPUT_DIR / "parser_output.json"
GERMANIC_OUTPUT_PATH = INPUT_DIR / "converter_germanic.json"
INDO_OUTPUT_PATH = INPUT_DIR / "converter_indo.json"

with PARSER_OUTPUT_PATH.open("r", encoding="utf-8") as f: # Load all parsed forms from the single parser output
    words_data = json.load(f)

if "Old Germanic" in words_data: # Collapse the only alias we currently need
    old_germanic_forms = words_data.pop("Old Germanic")
    if "Proto-Germanic" not in words_data:
        words_data["Proto-Germanic"] = old_germanic_forms.copy()
    else:
        for form in old_germanic_forms:
            if form not in words_data["Proto-Germanic"]:
                words_data["Proto-Germanic"].append(form)

with HIERARCHY_PATH.open("r", encoding="utf-8") as f: # Load hierarchy
    hierarchy = json.load(f)

appearance_order = list(words_data.keys())
order_index = {lang: i for i, lang in enumerate(appearance_order)}
allowed = set(words_data.keys())

def find_visible_children(name): # Proto-Germanic
    visible = []
    for child in hierarchy.get(name, {}).get("children", []):
        if child in allowed:
            visible.append(child)
        else:
            visible.extend(find_visible_children(child))
    return visible

def build_tree(name): # Proto-Germanic or Indo-European
    lang_meta = hierarchy.get(name, {})
    node = {
        "name": name,
        "start": lang_meta.get("start"),
        "end": lang_meta.get("end")
    }
    forms = words_data.get(name)
    if forms:
        node["forms"] = forms
    children = find_visible_children(name)
    if name == "Indo-European" and "Proto-Germanic" in children:
        children.remove("Proto-Germanic")
        children.insert(0, "Proto-Germanic")
    node["children"] = [
        build_tree(child)
        for child in children
    ]
    return node

for branch, root in EXPORT_BRANCHES.items(): # "germanic": "Proto-Germanic",
    allowed.add(root)  # add Proto-Germanic
    tree = build_tree(root)
    has_meaningful_content = bool(tree.get("forms")) or bool(tree.get("children")) # If the Proto-Germanic / Indo-European tree has forms or children, true
    if not has_meaningful_content: # If tree has no forms and no children, we can just have it as an empty tree
        tree = {}
    output_path = GERMANIC_OUTPUT_PATH if branch == "germanic" else INDO_OUTPUT_PATH
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"✅ Tree successfully built and saved to {output_path}")
