#!/usr/bin/python3

REQUIRED_SECTIONS = [
    "Topic",
    "Simple Explanation",
    "Key Concepts",
    "Example",
    "Practice Exercise",
    "Common Mistakes",
    "Review Comments",
    "Final Summary",
]

def validate_required_sections(content):
    missing = []
    for sects in REQUIRED_SECTIONS:
        if sects not in content:
            missing.append(sects)

    result = {
        "passed": not missing,
        "missing": missing,
    }
    return result