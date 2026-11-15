"""Convert a '# %%' percent-format .py into an .ipynb (no outputs). Usage: python src/py2ipynb.py in.py out.ipynb"""
import json, sys, re
src = open(sys.argv[1]).read()
cells = []
for block in re.split(r"(?m)^# %%", src)[1:]:
    md = block.startswith(" [markdown]")
    body = block.split("\n", 1)[1] if "\n" in block else ""
    body = body.strip("\n")
    if md:
        body = "\n".join(l[2:] if l.startswith("# ") else l.lstrip("#") for l in body.split("\n"))
    lines = body.split("\n")
    cell = {"cell_type": "markdown" if md else "code", "metadata": {}, "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}
    if not md: cell.update(execution_count=None, outputs=[])
    cells.append(cell)
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
json.dump(nb, open(sys.argv[2], "w"), indent=1)
print(len(cells), "cells ->", sys.argv[2])
