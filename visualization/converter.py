import json
from collections import defaultdict

# Load data
with open("../output/father_germanic.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Build lookup
children = defaultdict(list)
nodes = {}
for d in data:
    nodes[d["language"]] = d
    children[d["parent"]].append(d["language"])

def build_tree(name):
    node = {"name": name}
    if name in nodes:
        node["forms"] = nodes[name]["forms"]
    if name in children:
        node["children"] = [build_tree(c) for c in children[name]]
    return node

tree = build_tree("Germanic")

with open("tree_germanic.json", "w", encoding="utf-8") as f:
    json.dump(tree, f, indent=2, ensure_ascii=False)
    