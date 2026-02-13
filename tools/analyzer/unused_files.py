from pathlib import Path

CORE_HINTS = {"core", "application", "ui"}

def classify(file: str, reverse_graph: dict[str, set[str]]) -> str:
    if file in reverse_graph:
        return "dangerous"

    if any(h in file for h in CORE_HINTS):
        return "review"

    return "safe"
