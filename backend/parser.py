import json
from bs4 import BeautifulSoup
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent        # D:\Desktop\Dissertation\code\backend
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def resolve_input_html(): # Checks whether the user supplied a filename on the command line
    if len(sys.argv) < 2:
        raise SystemExit("Please enter the html file in the format: py parser.py <filename>.html")
    filename = sys.argv[1]
    input_html = BASE_DIR / "input" / filename
    if not input_html.exists():
        raise SystemExit(f"Input file not found: {input_html}")
    return input_html # D:\Desktop\Dissertation\code\backend\input\father.html

def parse_html(file_path): # Opens the HTML file and extracts the main etymology section 
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    ety = soup.find("div", id="main_etymology_complete")
    if not ety:
        raise ValueError("Etymology section not found in HTML.")
    return ety # <div class="etymology" id="main_etymology_complete">Cognate...

def trim_etymology_html(html: str) -> str: # Chops off everything including and after Notes
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

def trim_after_discussion_start(html: str) -> str:
    stop_phrases = [
        "The place and time of borrowing"
    ]
    lower_html = html.lower()
    cut_positions = []
    for phrase in stop_phrases:
        pos = lower_html.find(phrase.lower())
        if pos != -1:
            cut_positions.append(pos)
    if cut_positions:
        html = html[:min(cut_positions)]
    return html.strip()

def extract_language_forms(etymology_div):
    result = {}
    current_language = None
    skip_example_forms = False
    for node in etymology_div.descendants:
        node_name = getattr(node, "name", None)
        if node_name == "p": # Stop carrying a language across paragraph boundaries
            current_language = None
            skip_example_forms = False
            continue
        if node_name is None: # Look at plain text nodes as well as tags
            text = str(node).strip().lower()
            if text == "as" or ", as " in f" {text} " or text.endswith(" as"): # Skip example forms introduced by "... as X"
                skip_example_forms = True
            continue
        if node_name != "span": # Only span tags matter for extraction
            continue
        classes = node.get("class", [])
        if "language-name" in classes:
            current_language = node.get_text(strip=True)
            skip_example_forms = False
            if current_language not in result:
                result[current_language] = []
        elif "foreign-form" in classes and current_language is not None and not skip_example_forms:
            form = node.get_text(strip=True)
            if form not in result[current_language]:
                result[current_language].append(form)
    return result

def export_json(entries, filename_suffix):
    out_path = OUTPUT_DIR / f"parser_{filename_suffix}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported: {out_path}")

input_html = resolve_input_html()
ety = parse_html(input_html)
html = str(ety)
trimmed_html = trim_etymology_html(html)
trimmed_html = trim_after_discussion_start(trimmed_html)
ety_soup = BeautifulSoup(trimmed_html, "html.parser")
entries = extract_language_forms(ety_soup)
export_json(entries, "output")