from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple
import networkx as nx


PathT = Tuple[str, ...]


def _extend_simple_paths(g: nx.DiGraph) -> list[PathT]:
    """
    Enumerate *maximal simple paths* using a DFS extension strategy:
    - Simple path: no repeated nodes, except we allow a cycle closure to the start node.
    - We extend a path until it cannot be extended without breaking simplicity.
    Return the set of maximal simple paths, which includes candidate prime paths.
    """
    nodes = list(g.nodes())
    maximal: set[PathT] = set()

    for start in nodes:
        stack: list[Tuple[PathT, set[str]]] = [((start,), {start})]

        while stack:
            path, visited = stack.pop()
            last = path[-1]

            extended = False
            for succ in g.successors(last):
                # allow closing a cycle back to the start
                if succ == path[0] and len(path) > 1:
                    maximal.add(path + (succ,))
                    extended = True
                    continue

                if succ in visited:
                    continue

                extended = True
                npath = path + (succ,)
                nvisited = set(visited)
                nvisited.add(succ)
                stack.append((npath, nvisited))

            if not extended:
                maximal.add(path)

    return list(maximal)


def _is_proper_subpath(a: PathT, b: PathT) -> bool:
    """
    True if a appears in b as a contiguous subsequence and len(a) < len(b).
    """
    if len(a) >= len(b):
        return False
    for i in range(0, len(b) - len(a) + 1):
        if b[i : i + len(a)] == a:
            return True
    return False


def prime_paths(g: nx.DiGraph) -> list[PathT]:
    """
    Compute prime paths:
    1) Generate maximal simple paths via extension.
    2) Filter out any path that is a proper subpath of another.

    Returns a sorted list (by length desc, then lexicographic) for stable output.
    """
    candidates = _extend_simple_paths(g)

    # Remove duplicates and trivial empties (shouldn't exist)
    candidates = [p for p in set(candidates) if len(p) >= 1]

    primes: list[PathT] = []
    for p in candidates:
        if any(_is_proper_subpath(p, q) for q in candidates if q != p):
            continue
        primes.append(p)

    primes.sort(key=lambda x: (-len(x), x))
    return primes