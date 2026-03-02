import json
from bs4 import BeautifulSoup
from pathlib import Path

# Config
BASE_DIR = Path(__file__).resolve().parent        # D:\Desktop\Dissertation\code\backend
ROOT_DIR = BASE_DIR.parent                        # D:\Desktop\Dissertation\code
INPUT_HTML = BASE_DIR / "input" / "father.html"   # D:\Desktop\Dissertation\code\backend\input\father.html
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Parse the HTML 
def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    ety = soup.find("div", id="main_etymology_complete")
    if not ety:
        raise ValueError("Etymology section not found in HTML.")
    return ety

def trim_indo_html(html: str) -> str:
    father_marker = '<p></p>' # father-like case: extra paragraph before Notes
    if father_marker in html:
        html = html.split(father_marker, 1)[0]
    soup = BeautifulSoup(html, "html.parser")
    notes_h3 = soup.find( # Remove Notes section if present
        "h3",
        class_="etymology-note-header",
        string=lambda s: s and s.strip() == "Notes"
    )
    if notes_h3:
        for sib in list(notes_h3.next_siblings):
            sib.extract()
        notes_h3.extract()
    return "".join(str(x) for x in soup.contents).strip()

# Split HTML into Germanic and Indo-European sections 
def split_and_parse(ety):
    html = str(ety)
    parts = html.split('<span class="etymology-arrow">&lt;</span>', 1)
    if len(parts) != 2: # Case where we cannot split → treat everything as Germanic
        print("⚠️ Could not split etymology — treating as Germanic only")
        html = trim_indo_html(html)
        germanic_soup = BeautifulSoup(html, "html.parser")
        germanic_entries = extract_language_forms(germanic_soup)
        indo_entries = {}   # <-- REQUIRED CHANGE
        return germanic_entries, indo_entries
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
    for span in spans:
        lang = span.get_text(strip=True)
        forms = []
        next_tags = span.find_all_next(["span"], limit=8)
        for tag in next_tags:
            if "language-name" in tag.get("class", []):
                break
            if "foreign-form" in tag.get("class", []):
                forms.append(tag.get_text(strip=True))
        if lang not in result: # Ensure language exists
            result[lang] = []
        for f in forms: # Append while preserving uniqueness
            if f not in result[lang]:
                result[lang].append(f)
    return result

# Export to JSON 
def export_json(word, entries, filename_suffix):
    out_path = OUTPUT_DIR / f"parser_output_{word}_{filename_suffix}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported: {out_path}")

# Main pipeline 
def main():
    ety = parse_html(INPUT_HTML)
    germanic, indo = split_and_parse(ety)
    word = INPUT_HTML.stem  # "father" if INPUT_HTML is father.html
    export_json(word, germanic, "germanic")
    export_json(word, indo, "indo")

if __name__ == "__main__":
    main()
