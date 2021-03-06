import json

from pathlib import Path

source_file = Path("contacts.json")
assert source_file.exists

with source_file.open() as f:
    source_data = json.load(f)


output_file = Path("data.json")

with output_file.open(mode="w") as f:
    json.dump(source_data, f, indent=4)