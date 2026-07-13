from __future__ import annotations

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from _bootstrap import bootstrap_src_path

bootstrap_src_path()
from clinical_inference_workstation.config import ROOT_DIR


def main() -> None:
    web_dir = ROOT_DIR / "web"
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=str(web_dir), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 4173), handler)
    print("WORKSTATION_STATIC_SERVER http://127.0.0.1:4173/index.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
