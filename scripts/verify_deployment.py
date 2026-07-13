from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


def _request(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: bytes | None = None) -> tuple[int, dict[str, object]]:
    request = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    with urllib.request.urlopen(request, timeout=15) as response:  # nosec B310
        payload = response.read().decode("utf-8")
        return response.status, json.loads(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--bearer-token", default="")
    parser.add_argument("--inference-id", type=int, default=1)
    args = parser.parse_args()

    health_status, health_payload = _request(f"{args.base_url.rstrip('/')}/health")
    print(f"HEALTH_STATUS {health_status}")
    print(f"HEALTH_PAYLOAD {health_payload}")

    if args.bearer_token:
        headers = {"Authorization": f"Bearer {args.bearer_token}"}
        try:
            record_status, record_payload = _request(
                f"{args.base_url.rstrip('/')}/v1/inferences/{args.inference_id}",
                headers=headers,
            )
            print(f"INFERENCE_STATUS {record_status}")
            print(f"INFERENCE_RECORD_KEYS {sorted(record_payload.keys())}")
        except urllib.error.HTTPError as exc:
            print(f"INFERENCE_STATUS {exc.code}")
            print("INFERENCE_RECORD_KEYS []")
            raise


if __name__ == "__main__":
    main()
