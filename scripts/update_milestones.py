#!/usr/bin/env python3

import os
import json
import re
from copy import deepcopy
from math import floor, log10

CROP_MAP = {
    "Melon Slice": "MELON",
}

CROP_GROUPS = [
    {"WHEAT", "PUMPKIN", "MUSHROOM", "MOONFLOWER", "SUNFLOWER"},
    {"CARROT", "POTATO"},
    {"SUGAR_CANE", "CACTUS", "WILD_ROSE"},
    {"MELON"},
    {"COCOA_BEANS", "NETHER_WART"},
]
EQUIVALENT_CROPS = {}
for group in CROP_GROUPS:
    frozen = frozenset(group)
    for item in group:
        EQUIVALENT_CROPS[item] = frozen

OVERRIDES = """
Wheat:4:350
Pumpkin:4:350
Mushroom:4:350
Moonflower:4:700
Sunflower:4:350
Sugar Cane:22:1,000,000
Cactus:22:1,000,000
Cocoa Beans:23:1,950,000
Nether Wart:23:1,950,000
Wild Rose:22:800,000
"""


def round_sig(x: int, sig: int) -> int:
    return round(x, sig - int(floor(log10(abs(x)))) - 1)


def update(data: dict[str, dict[str, int]], lines: list[str], *, equivalents: bool) -> None:
    updated = 0
    for line in lines:
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        try:
            crop_name, index, amount = line.split(":")
        except:
            print(repr(line))
            raise
        if crop_name == "Melon":
            # Old SkyHanni version, may be from main server, cannot be trusted
            continue

        crop_id = CROP_MAP.get(crop_name) or crop_name.replace(" ", "_").upper()
        index = int(index)
        amount = int(re.sub(r"[ .,]", "", amount))

        crop_ids = EQUIVALENT_CROPS[crop_id] if equivalents else {crop_id}
        for cid in crop_ids:
            ms = data["crop_milestones"][cid]
            if ms[index] != amount:
                if round_sig(ms[index], 2) == amount:
                    print(f"Warning: Ignoring milestone change within 2 significant figures for {cid}:{index} ({ms[index]} -> {amount})")
                    continue
                data["crop_milestones"][cid][index] = amount
                updated += 1
    return updated


updated = 0

with open("constants/Garden.json", "r") as fd:
    data = json.load(fd)
data_orig = deepcopy(data)

with open("milestones.txt") as fd:
    lines = [x.rstrip("\n") for x in fd.readlines()]
lines += OVERRIDES.splitlines()
# First pass: Apply updates to equivalent crops as well
update(data, lines, equivalents=True)
# Second pass: Correct for any confirmed discrepancies
update(data, lines, equivalents=False)

with open("constants/Garden.json.new", "w") as fd:
    json.dump(data, fd, indent=2)
os.replace("constants/Garden.json.new", "constants/Garden.json")

updated = 0
for crop_id, milestones in data["crop_milestones"].items():
    for index, amount in enumerate(milestones):
        if data_orig["crop_milestones"][crop_id][index] != amount:
            updated += 1
print(f"Updated {updated} milestone(s)")
