import anybadge
import re
import os

# Read coverage percentage from coverage.txt
with open("../../coverage.txt", "r") as file:
    for line in file:
        if line.startswith("TOTAL"):
            match = re.search(r"(\d+)%$", line)
            if match:
                coverage = int(match.group(1))
                print(f"Coverage: {coverage}%")
                break
    else:
        raise ValueError("Could not find coverage percentage in coverage.txt")

# Determine badge color based on coverage percentage
thresholds = {20: "red", 50: "yellow", 75: "yellowgreen", 90: "brightgreen"}

# Create the badge
badge = anybadge.Badge("Test Coverage", coverage, thresholds=thresholds)

# Delete coverage-badge.svg if it exists
os.remove("coverage-badge.svg") if os.path.exists("coverage-badge.svg") else None

# Write the badge to a file
badge.write_badge("coverage-badge.svg")
