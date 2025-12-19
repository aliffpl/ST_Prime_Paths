from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import networkx as nx
try:
    from staticfg import CFGBuilder  # type: ignore
except Exception:
    CFGBuilder = None  # type: ignore


@dataclass(frozen=True)
class CFGArtifact:
    file: Path
    function: str  # "module" or function name
    graph: nx.DiGraph


def _cfg_to_networkx(cfg) -> nx.DiGraph:
    """
    Convert staticfg CFG to a NetworkX DiGraph.
    Nodes in staticfg are basic blocks; we use their IDs (or repr) as node keys.
    """
    g = nx.DiGraph()

    # staticfg CFG has .entryblock and blocks reachable via ._blocks or iter
    # We'll traverse from entry to be robust.
    entry = cfg.entryblock
    stack = [entry]
    seen = set()

    def node_id(block) -> str:
        # block.id exists in staticfg basic blocks
        return str(getattr(block, "id", repr(block)))

    while stack:
        b = stack.pop()
        bid = node_id(b)
        if bid in seen:
            continue
        seen.add(bid)
        g.add_node(bid, label=str(bid))

        for nxt in getattr(b, "next", []) or []:
            nid = node_id(nxt)
            g.add_edge(bid, nid)
            if nid not in seen:
                stack.append(nxt)

        # some versions use .exits (list of (exitcase, block))
        for ex in getattr(b, "exits", []) or []:
            if isinstance(ex, tuple) and len(ex) == 2:
                _, blk = ex
                nid = node_id(blk)
                g.add_edge(bid, nid)
                if nid not in seen:
                    stack.append(blk)

    return g


def extract_cfgs_from_file(py_file: Path) -> list[CFGArtifact]:
    """
    Extract:
      - module-level CFG
      - per-function CFGs (where possible)
    """
    src = py_file.read_text(encoding="utf-8", errors="ignore")
    artifacts: list[CFGArtifact] = []

    # module CFG: prefer staticfg when available, otherwise use an AST-based fallback
    if CFGBuilder is not None:
        try:
            cfg_mod = CFGBuilder().build_from_src(str(py_file), src)
            artifacts.append(CFGArtifact(file=py_file, function="module", graph=_cfg_to_networkx(cfg_mod)))
        except Exception:
            # fall through to AST fallback
            pass

    if not artifacts:
        # simple AST-based CFG fallback (best-effort): sequential statements + basic branching
        try:
            import ast

            def _ast_to_simple_cfg(source: str) -> nx.DiGraph:
                tree = ast.parse(source)
                g = nx.DiGraph()
                # nodes will be numbered strings
                counter = 0

                def new_node(label: str) -> str:
                    nonlocal counter
                    counter += 1
                    nid = f"n{counter}"
                    g.add_node(nid, label=label)
                    return nid

                start = new_node("start")
                last = start

                # For module-level, walk top-level statements sequentially
                for node in tree.body:
                    if isinstance(node, ast.If):
                        cond = new_node("if")
                        g.add_edge(last, cond)

                        # then branch
                        then_node = new_node("then")
                        g.add_edge(cond, then_node)
                        g.add_edge(then_node, cond)

                        # else branch (if present)
                        if node.orelse:
                            else_node = new_node("else")
                            g.add_edge(cond, else_node)
                            g.add_edge(else_node, cond)
                        last = cond
                    elif isinstance(node, ast.While):
                        w = new_node("while")
                        g.add_edge(last, w)
                        body_node = new_node("while_body")
                        g.add_edge(w, body_node)
                        g.add_edge(body_node, w)
                        last = w
                    else:
                        s = new_node(type(node).__name__)
                        g.add_edge(last, s)
                        last = s

                end = new_node("end")
                g.add_edge(last, end)
                return g

            g = _ast_to_simple_cfg(src)
            artifacts.append(CFGArtifact(file=py_file, function="module", graph=g))
        except Exception:
            pass

    return artifacts