# Running the project

## 1. Get the OED etymology HTML
<img width="1919" height="1032" alt="Screenshot 2026-03-26 231507" src="https://github.com/user-attachments/assets/24f154d5-0d63-49ee-89c0-c27b3fd5209d" />

1. Open the word in the Oxford English Dictionary and go to the **Etymology** tab.
2. Right click the page and choose **Inspect**.
3. In the developer tools, choose **Select an element** and click the block of text as in image above.
4. That will highlight the `div` with id `main_etymology_complete` in the **Elements** panel.
5. Right click that element and choose **Copy -> Copy element**.
6. Paste the copied HTML into a new file with a `.html` extension.
7. Save that file in `backend/input/`.

## 2. Run the parser and converter
From the project root, run:
```bash
cd backend
py parser.py <filename>.html
py converter.py
```

## 3. Start a local server in the project root
```bash
cd ..
py -m http.server 8080 --bind 127.0.0.1
```

## 4. Open the visualisation
Open this in your browser: http://127.0.0.1:8080/frontend/tree.html
