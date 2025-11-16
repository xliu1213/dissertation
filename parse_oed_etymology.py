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

# Split HTML into Germanic and Indo-European sections 
def split_and_parse(ety):
    html = str(ety)
    parts = html.split('<span class="etymology-arrow">&lt;</span>', 1)
    if len(parts) != 2:
        raise ValueError("Could not split etymology into Germanic and Indo-European blocks.")
    germanic_html, indo_html = parts
    germanic_soup = BeautifulSoup(germanic_html, "html.parser")
    indo_soup = BeautifulSoup(indo_html, "html.parser")
    germanic_entries = extract_language_forms(germanic_soup)
    indo_entries = extract_language_forms(indo_soup)
    return germanic_entries, indo_entries

# Extract language → forms mapping 
def extract_language_forms(etymology_div):
    result = {}  # <-- dictionary instead of list
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
        seen = set() # Remove duplicates while preserving order
        unique_forms = []
        for f in forms:
            if f not in seen:
                seen.add(f)
                unique_forms.append(f)
        result[lang] = unique_forms  # <-- assign in dict
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
