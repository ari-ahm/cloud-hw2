"""Inspect each saved layer separately, including files hidden by whiteouts."""

import gzip
import io
import json
import sys
import tarfile

MARKER = b"cloud-hw2-demo-secret-DO-NOT-USE"


def inspect(filename):
    hits = 0
    whiteouts = 0
    layers = 0
    with tarfile.open(filename) as archive:
        members = {member.name: member for member in archive if member.isfile()}
        if "manifest.json" in members:
            manifest = json.load(archive.extractfile(members["manifest.json"]))
            layer_names = {layer for item in manifest for layer in item["Layers"]}
            config_names = {item["Config"] for item in manifest}
        else:
            raise ValueError("Saved image has no Docker-compatible manifest.json")
        print("manifest.json:", json.dumps(manifest))
        for name in sorted(config_names | layer_names):
            data = archive.extractfile(members[name]).read()
            if data.startswith(b"\x1f\x8b"):
                data = gzip.decompress(data)
            if name in config_names:
                if MARKER in data:
                    print("SECRET IN CONFIG:", name)
                    hits += 1
                continue
            layers += 1
            with tarfile.open(fileobj=io.BytesIO(data)) as layer:
                for entry in layer:
                    if "/.wh." in entry.name or entry.name.startswith(".wh."):
                        print("WHITEOUT:", name, entry.name)
                        whiteouts += 1
                    if entry.isfile() and MARKER in layer.extractfile(entry).read():
                        print("SECRET IN LAYER:", name, entry.name)
                        hits += 1
    print(json.dumps({"archive": filename, "layers": layers,
                      "secret_hits": hits, "whiteouts": whiteouts}))
    return hits


if __name__ == "__main__":
    inspect(sys.argv[1])
