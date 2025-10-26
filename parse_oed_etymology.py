import json
from bs4 import BeautifulSoup
from pathlib import Path

# ---------- CONFIG ----------
INPUT_HTML = "father.html"
LANG_HIERARCHY_JSON = "languageHierarchy.json"
OUTPUT_DIR = "output"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# ---------- STEP 1: Load language hierarchy ----------
def load_hierarchy():
    try:
        with open(LANG_HIERARCHY_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ languageHierarchy.json not found. Using empty hierarchy.")
        return {}

# ---------- STEP 2: Parse the HTML ----------
def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    ety = soup.find("div", id="main_etymology_complete")
    if not ety:
        raise ValueError("Etymology section not found in HTML.")
    return ety

# ---------- STEP 3: Extract language → forms mapping ----------
def extract_language_forms(etymology_div):
    pairs = []
    spans = etymology_div.find_all("span", class_="language-name")
    for span in spans:
        lang = span.get_text(strip=True)
        forms = []
        next_tags = span.find_all_next(["span"], limit=8)
        for tag in next_tags:
            if "language-name" in tag.get("class", []):
                break
            if "foreign-form" in tag.get("class", []):
                forms.append(tag.get_text(strip=True))
        # Remove duplicates while preserving order
        seen = set()
        unique_forms = []
        for f in forms:
            if f not in seen:
                seen.add(f)
                unique_forms.append(f)
        pairs.append({"language": lang, "forms": unique_forms})
    return pairs

# ---------- STEP 4: Attach parent relationships ----------
def attach_parents(entries, hierarchy):
    for e in entries:
        e["parent"] = hierarchy.get(e["language"], None)
    return entries

# ---------- STEP 5: Split HTML into Germanic and Indo-European sections ----------
def split_and_parse(ety, hierarchy):
    html = str(ety)
    parts = html.split('<span class="etymology-arrow">&lt;</span>', 1)

    if len(parts) != 2:
        raise ValueError("Could not split etymology into Germanic and Indo-European blocks.")

    germanic_html, indo_html = parts

    germanic_soup = BeautifulSoup(germanic_html, "html.parser")
    indo_soup = BeautifulSoup(indo_html, "html.parser")

    germanic_entries = extract_language_forms(germanic_soup)
    indo_entries = extract_language_forms(indo_soup)

    germanic_entries = attach_parents(germanic_entries, hierarchy)
    indo_entries = attach_parents(indo_entries, hierarchy)

    return germanic_entries, indo_entries

# ---------- STEP 6: Main pipeline ----------
def main():
    hierarchy = load_hierarchy()
    ety = parse_html(INPUT_HTML)
    germanic, indo = split_and_parse(ety, hierarchy)

    print("\n------ Germanic entries ------")
    for e in germanic:
        print(f"{e['language']}: {', '.join(e['forms'])} (parent: {e['parent']})")

if __name__ == "__main__":
    main()
