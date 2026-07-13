from __future__ import annotations

import uvicorn

from _bootstrap import bootstrap_src_path

bootstrap_src_path()

def main() -> None:
    uvicorn.run(
        "clinical_inference_workstation.api.app:create_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
