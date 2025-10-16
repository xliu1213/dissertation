import json
import re
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

# ---------- STEP 2: Parse HTML ----------
def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    ety = soup.find("div", id="main_etymology_complete")
    if not ety:
        raise ValueError("Etymology section not found in HTML.")
    return ety

# ---------- STEP 3: Segment paragraphs ----------
def segment_paragraphs(etymology_div):
    text = etymology_div.get_text(" ", strip=True)
    # Split by the Indo-European paragraph marker
    split_match = re.split(
        r"< the same Indo-European base as", text, flags=re.IGNORECASE
    )
    if len(split_match) == 2:
        germanic_text, indo_euro_text = split_match
    else:
        germanic_text, indo_euro_text = text, ""
    return germanic_text.strip(), indo_euro_text.strip()

# ---------- STEP 4: Extract language entries ----------
def extract_language_forms(etymology_div):
    pairs = []
    spans = etymology_div.find_all("span", class_="language-name")
    for span in spans:
        lang = span.get_text(strip=True)
        # Get nearby foreign-form spans (up to 3 after each language)
        forms = []
        next_tags = span.find_all_next(["span"], limit=8)
        for tag in next_tags:
            if "language-name" in tag.get("class", []):
                break
            if "foreign-form" in tag.get("class", []):
                forms.append(tag.get_text(strip=True))
        pairs.append({"language": lang, "forms": list(set(forms))})
    return pairs

# ---------- STEP 5: Attach parents from hierarchy ----------
def attach_parents(entries, hierarchy):
    for e in entries:
        e["parent"] = hierarchy.get(e["language"], None)
    return entries

# ---------- STEP 6: Split into Germanic vs Indo-European ----------
def classify_entries(entries):
    germanic_keywords = [
        "Old Frisian",
        "West Frisian",
        "Old Dutch",
        "Middle Dutch",
        "Dutch",
        "Old Saxon",
        "Middle Low German",
        "Old High German",
        "Middle High German",
        "German",
        "Old Icelandic",
        "Old Swedish",
        "Swedish",
        "Old Danish",
        "Danish",
        "Gothic",
    ]
    indo_euro_keywords = [
        "Sanskrit",
        "Greek",
        "Latin",
        "Old French",
        "Middle French",
        "French",
        "Old Occitan",
        "Occitan",
        "Catalan",
        "Spanish",
        "Portuguese",
        "Italian",
        "Gaulish",
        "Armenian",
        "Tocharian",
        "Early Irish",
        "Oscan",
        "Avestan",
    ]

    germanic, indo_euro = [], []
    for e in entries:
        if any(k in e["language"] for k in germanic_keywords):
            germanic.append(e)
        elif any(k in e["language"] for k in indo_euro_keywords):
            indo_euro.append(e)
    return germanic, indo_euro

# ---------- STEP 7: Export ----------
def export_json(word, germanic, indo_euro):
    g_path = Path(OUTPUT_DIR) / f"{word}_germanic.json"
    i_path = Path(OUTPUT_DIR) / f"{word}_indoEuropean.json"
    with open(g_path, "w", encoding="utf-8") as g:
        json.dump(germanic, g, ensure_ascii=False, indent=2)
    with open(i_path, "w", encoding="utf-8") as i:
        json.dump(indo_euro, i, ensure_ascii=False, indent=2)
    print(f"✅ Exported: {g_path}, {i_path}")

# ---------- MAIN PIPELINE ----------
def main():
    hierarchy = load_hierarchy()
    ety = parse_html(INPUT_HTML)
    germanic_text, indo_text = segment_paragraphs(ety)
    entries = extract_language_forms(ety)
    entries = attach_parents(entries, hierarchy)
    germanic, indo = classify_entries(entries)

    word = Path(INPUT_HTML).stem
    export_json(word, germanic, indo)
    print(
        f"Parsed {len(entries)} entries → Germanic: {len(germanic)}, Indo-European: {len(indo)}"
    )

if __name__ == "__main__":
    main()
    