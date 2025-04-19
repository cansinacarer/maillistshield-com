import re

# Read coverage percentage from coverage.txt
with open("../coverage.txt", "r") as file:
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
color = "red"
if coverage >= 90:
    color = "brightgreen"
if coverage >= 75:
    color = "yellowgreen"
if coverage >= 50:
    color = "yellow"

# Generate the SVG badge
badge = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="130" height="20">
  <rect width="90" height="20" fill="#555"/>
  <rect x="90" width="40" height="20" fill="{color}"/>
  <text x="45" y="14" fill="#fff" font-family="Verdana" font-size="11" text-anchor="middle">Test Coverage</text>
  <text x="110" y="14" fill="#fff" font-family="Verdana" font-size="11" text-anchor="middle">{coverage}%</text>
</svg>
"""

# Write the badge to a file
with open("coverage-badge.svg", "w") as f:
    f.write(badge)
