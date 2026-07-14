#!/usr/bin/python3
from pathlib import Path


def save_markdown_file(file_path: str, content: str ):
    path = Path(file_path)
    if path is None:
        raise ValueError("File path doesnt exist")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return "The file has been written"