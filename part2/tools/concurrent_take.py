"""Fill an empty test queue, then consume it with 200 concurrent requests."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000")
    args = parser.parse_args()
    base = args.url.rstrip("/")

    def post(route, payload=None):
        data = b"" if payload is None else json.dumps(payload).encode()
        request = Request(base + route, data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=60) as response:
                return response.status, response.read().decode()
        except HTTPError as error:
            return error.code, error.read().decode()

    assert post("/next") == (404, "empty"), "Use a separate empty queue"
    names = [f"take-{i:03d}" for i in range(200)]
    for i, name in enumerate(names, 1):
        assert post("/join", {"name": name}) == (200, str(i))
    start = threading.Event()

    def take(_):
        start.wait()
        return post("/next")

    with ThreadPoolExecutor(max_workers=200) as pool:
        futures = [pool.submit(take, i) for i in range(200)]
        start.set()
        results = [future.result() for future in futures]
    actual = Counter(body for status, body in results if status == 200)
    final = post("/next")
    passed = actual == Counter(names) and final == (404, "empty")
    print(json.dumps({"sent": 200, "successful": sum(s == 200 for s, _ in results),
                      "unique_names": len(actual), "missing": list((Counter(names)-actual).elements()),
                      "extra": list((actual-Counter(names)).elements()),
                      "final_next": final, "passed": passed}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
