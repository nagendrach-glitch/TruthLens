"""
show_tools.py
Developer utility — prints all tools registered on the TruthLens crew.

Run from the fact_checker/ directory:
    python src/fact_checker/show_tools.py
"""

import sys
import os

# Ensure the package root (src/) is on the path
_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from fact_checker.crew import FactChecker

fc = FactChecker()
crew = fc.crew()

print("🔧 Tools registered on the TruthLens crew:\n")

seen = set()
for agent in crew.agents:
    for tool in agent.tools:
        name = tool.__class__.__name__
        desc = getattr(tool, "description", "No description")
        if name not in seen:
            print(f"  ✅  {name}")
            print(f"       {desc}\n")
            seen.add(name)

print(f"Total unique tools: {len(seen)}")
