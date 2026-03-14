# OED Etymology Visualisation

Pipeline:

1. parser.py
   Extracts languages and forms from OED HTML.

2. converter.py
   Merges parsed data with languageHierarchy.json and builds a tree.

3. languageHierarchy.json
   Defines genealogical relationships and time ranges.

4. tree.html + D3
   Interactive visualisation of language evolution.

Running the system:

cd backend
python parser.py
python converter.py

Open frontend/tree.html
