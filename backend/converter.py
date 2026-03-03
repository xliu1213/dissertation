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
ALWAYS_INCLUDE = {
    "germanic": {"Proto-Germanic"}
}
LANGUAGE_ALIASES = { # Language aliases / normalisation
    "Old Germanic": "Proto-Germanic"
}

def normalise_language(lang):
    return LANGUAGE_ALIASES.get(lang, lang)

def merge_entries(target, source):
    for lang, forms in source.items():
        lang = normalise_language(lang)
        if lang not in target:
            target[lang] = forms.copy()
        else:
            for f in forms:
                if f not in target[lang]:
                    target[lang].append(f)
                    
# Load Germanic forms
with GERMANIC_PATH.open("r", encoding="utf-8") as f:
    germanic_data = json.load(f)

# Load Indo-European forms
with INDO_PATH.open("r", encoding="utf-8") as f:
    indo_data = json.load(f)

# Handle EMPTY Germanic case
if germanic_data == {}:
    output_path = INPUT_DIR / f"converter_output_{WORD}_germanic.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump({}, f, indent=2, ensure_ascii=False)
    print(f"✅ Germanic input empty — blank output written to {output_path}")

words_data = {}
if germanic_data:
    merge_entries(words_data, germanic_data)
if indo_data:
    merge_entries(words_data, indo_data)

# Load hierarchy
with HIERARCHY_PATH.open("r", encoding="utf-8") as f:
    hierarchy = json.load(f)

appearance_order = list(words_data.keys())
order_index = {lang: i for i, lang in enumerate(appearance_order)}
allowed = set(words_data.keys())
def find_visible_children(name, branch):
    visible = []
    for child in hierarchy.get(name, {}).get("children", []):
        if (
            child in allowed
            or child in ALWAYS_INCLUDE.get(branch, set())
        ):
            visible.append(child)
        else:
            visible.extend(find_visible_children(child, branch))
    visible.sort(key=lambda x: order_index.get(x, float("inf")))
    return visible

def build_tree(name, branch):
    lang_meta = hierarchy.get(name, {})
    node = {
        "name": name,
        "start": lang_meta.get("start"),
        "end": lang_meta.get("end")
    }
    forms = words_data.get(name)
    if forms:
        node["forms"] = forms
    children = find_visible_children(name, branch)
    if ( # FORCE structural proto-language visibility
        name in ALWAYS_INCLUDE.get(branch, set())
        and not children
    ):
        children = []
    node["children"] = [
        build_tree(child, branch)
        for child in children
    ]
    return node

for branch, root in EXPORT_BRANCHES.items():
    if branch == "germanic" and germanic_data == {}: # Skip germanic if already handled as empty
        continue
    allowed.add(root) # ensure Proto-Germanic exists structurally
    tree = build_tree(root, branch)
    output_path = INPUT_DIR / f"converter_output_{WORD}_{branch}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"✅ Tree successfully built and saved to {output_path}")
