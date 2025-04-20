import re

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
    <g>
        <g>
            <path d="M0,3 C0,1.3431 1.3552,0 3.02702703,0 L91,0 L91,20 L3.02702703,20 C1.3552,20 0,18.6569 0,17 L0,3 Z" fill="#555"/>
            <text x="45" y="14" fill="#fff" font-family="Verdana" font-size="11" text-anchor="middle">Test Coverage</text>
            </g>
            <g xmlns="http://www.w3.org/2000/svg" transform="translate(90)">
                <path xmlns="http://www.w3.org/2000/svg" d="M0 0h37C40 0 40 1.343 40 3v14c0 1.657-1.37 3-3.061 3H0V0z" fill="{color}"/>
                <text xmlns="http://www.w3.org/2000/svg" fill="#FFFFFF" font-family="Verdana" font-size="11">
                    <tspan x="4" y="14">{coverage}%</tspan>
                </text>
        </g>
    </g>    
</svg>
"""

# Write the badge to a file
with open("coverage-badge.svg", "w") as f:
    f.write(badge)
