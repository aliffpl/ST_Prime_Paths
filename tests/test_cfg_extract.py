import sys
import os
import tempfile
from pathlib import Path

# Ensure project root is importable when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import networkx as nx
from primepaths.cfg_extract import extract_cfgs_from_file
import importlib
import primepaths.prime_paths as _pp_mod
importlib.reload(_pp_mod)
from primepaths.prime_paths import prime_paths


def test_cfg_extract_and_prime_paths_fallback():
    src = """
def foo(x):
    if x > 0:
        y = 1
    else:
        y = -1
    i = 0
    while i < 2:
        i += 1
    return y
"""

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "mod.py"
        p.write_text(src, encoding="utf-8")

        arts = extract_cfgs_from_file(p)
        assert len(arts) >= 1
        g = arts[0].graph
        assert isinstance(g, nx.DiGraph)
        assert g.number_of_nodes() > 0

        pp = prime_paths(g)
        # should produce some prime paths
        assert isinstance(pp, list)
        assert len(pp) >= 1
