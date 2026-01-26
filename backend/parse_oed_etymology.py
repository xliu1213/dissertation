import json
from bs4 import BeautifulSoup
from pathlib import Path

# Config
INPUT_HTML = "father.html"
OUTPUT_DIR = "output"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Parse the HTML 
def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    ety = soup.find("div", id="main_etymology_complete")
    if not ety:
        raise ValueError("Etymology section not found in HTML.")
    return ety

def trim_indo_html(indo_html: str) -> str:
    father_marker = '<p></p>' # father-like case: extra paragraph before Notes
    if father_marker in indo_html:
        return indo_html.split(father_marker, 1)[0]
    soup = BeautifulSoup(indo_html, "html.parser") # Most words: cut at Notes header using HTML structure
    notes_h3 = soup.find(
        "h3",
        class_="etymology-note-header",
        string=lambda s: s and s.strip() == "Notes"
    )
    if notes_h3:
        for sib in list(notes_h3.next_siblings): # Remove Notes header and everything after it in the fragment
            sib.extract()
        notes_h3.extract()
        return "".join(str(x) for x in soup.contents).strip() # Return fragment HTML without adding <html><body> wrappers
    return indo_html

# Split HTML into Germanic and Indo-European sections 
def split_and_parse(ety):
    html = str(ety)
    parts = html.split('<span class="etymology-arrow">&lt;</span>', 1)
    if len(parts) != 2:
        raise ValueError("Could not split etymology into Germanic and Indo-European blocks.")
    germanic_html, indo_html = parts
    indo_html = trim_indo_html(indo_html) # NEW: trim Indo-European block before the “probably originally…” paragraph
    germanic_soup = BeautifulSoup(germanic_html, "html.parser")
    indo_soup = BeautifulSoup(indo_html, "html.parser")
    germanic_entries = extract_language_forms(germanic_soup)
    indo_entries = extract_language_forms(indo_soup)
    return germanic_entries, indo_entries

# Extract language → forms mapping 
def extract_language_forms(etymology_div):
    result = {}
    spans = etymology_div.find_all("span", class_="language-name")
    processed_langs = set()  # track language names we've already handled
    for span in spans:
        lang = span.get_text(strip=True)
        if lang in processed_langs: # NEW: skip duplicate languages
            continue
        processed_langs.add(lang)
        forms = []
        next_tags = span.find_all_next(["span"], limit=8)
        for tag in next_tags:
            if "language-name" in tag.get("class", []):
                break
            if "foreign-form" in tag.get("class", []):
                forms.append(tag.get_text(strip=True))
        seen = set() # Remove duplicates while preserving order (forms)
        unique_forms = []
        for f in forms:
            if f not in seen:
                seen.add(f)
                unique_forms.append(f)
        result[lang] = unique_forms
    return result

# Export to JSON 
def export_json(word, entries, filename_suffix):
    out_path = Path(OUTPUT_DIR) / f"{word}_{filename_suffix}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported: {out_path}")

# Main pipeline 
def main():
    ety = parse_html(INPUT_HTML)
    germanic, indo = split_and_parse(ety)
    word = Path(INPUT_HTML).stem  # e.g. "father"
    export_json(word, germanic, "germanic")

if __name__ == "__main__":
    main()
