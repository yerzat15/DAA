import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src" / "Python"))
import algorithms


def show(title, n, source, edges, targets):
    result = algorithms.dag({"task": "dag", "n": n, "source": source, "edges": edges})
    print("## %s" % title)
    print("edges =", json.dumps(edges))
    print("dag result =", json.dumps(result, separators=(",", ":")))
    for target in targets:
        route = algorithms.reconstruct_route(edges, result, source, target)
        used = [result["parent_edge"][v] for v in route[1:]]
        weight = sum(edges[i][2] for i in used)
        print("reconstruct_route(edges, result, %d, %d) -> %s   edge IDs %s, total weight %s, distance %s"
              % (source, target, route, used, weight if route else "-", json.dumps(result["distance"][target])))
    print()


show("Published example (reachable target, source, unreachable target)", 5, 0,
     [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]], [3, 0, 4])
show("Tied paths and parallel edges", 4, 0,
     [[0, 1, 1], [0, 2, 2], [1, 3, 2], [2, 3, 1], [0, 3, 3], [0, 3, 3]], [3, 1])
show("Source that is not vertex 0", 4, 2, [[0, 1, 1], [1, 2, 1], [2, 3, 4]], [3, 2, 0])
