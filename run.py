import os, sys, webbrowser, subprocess
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
HOST = "127.0.0.1"
PORT = 8080

def run_backend_pipeline(filename: str) -> None:
    subprocess.run(
        [sys.executable, "parser.py", filename],
        cwd=BACKEND,
        check=True
    )
    subprocess.run(
        [sys.executable, "converter.py"],
        cwd=BACKEND,
        check=True
    )

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python run.py <filename>.html")
        sys.exit(1)
    filename = sys.argv[1]
    input_file = BACKEND / "input" / filename
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        sys.exit(1)
    try:
        run_backend_pipeline(filename)
    except subprocess.CalledProcessError as e:
        print(f"Error while running backend pipeline: {e}")
        sys.exit(e.returncode)
    os.chdir(ROOT)
    url = f"http://{HOST}:{PORT}/frontend/tree.html"
    print(f"Opening {url}")
    print("Press Ctrl+C to stop the server.")
    webbrowser.open(url)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return  # suppress all request logs
    server = ThreadingHTTPServer((HOST, PORT), QuietHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()