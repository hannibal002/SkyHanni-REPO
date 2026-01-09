#!/usr/bin/env python3

import os
import json
import re

CROP_MAP = {
    "Melon Slice": "MELON",
}

updated = 0

with open("constants/Garden.json", "r") as fd:
    data = json.load(fd)

with open("milestones.txt") as fd:
    for line in fd:
        line = line.rstrip("\n")
        crop, index, amount = line.split(":")

        crop_id = CROP_MAP.get(crop) or crop.replace(" ", "_").upper()
        index = int(index)
        amount = int(re.sub(r"[ .,]", "", amount))

        data["crop_milestones"][crop_id][index] = amount
        updated += 1

with open("constants/Garden.json.new", "w") as fd:
    json.dump(data, fd, indent=2)
os.replace("constants/Garden.json.new", "constants/Garden.json")

print(f"Updated {updated} milestone(s)")
