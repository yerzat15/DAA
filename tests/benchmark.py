import gc
import os
import pathlib
import platform
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))
sys.path.insert(0, str(ROOT / "tests"))

import algorithms
import checker
import generate

SIZES = [(1000, 2500), (10000, 25000), (100000, 250000)]
SEED = 2025
RUNS = 5


def time_once(method, request):
    gc.collect()
    start = time.perf_counter_ns()
    result = method(request)
    return (time.perf_counter_ns() - start) / 1e6, result


def cpu_name():
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as stream:
            for line in stream:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def main():
    print("Python %s, %s, CPU: %s, %d logical CPUs" % (
        platform.python_version(), platform.platform(), cpu_name(), os.cpu_count()))
    print("Graphs: generate.connected_weighted(n, m, seed=%d + n), weights in [-1e9, 1e9]" % SEED)
    print("Runs per method and size: %d timed after 1 warm-up; times in ms\n" % RUNS)
    print("| n | m | cost (both) | Kruskal runs | Kruskal median | Prim runs | Prim median | Prim/Kruskal |")
    print("|---:|---:|---:|---|---:|---|---:|---:|")
    for n, m in SIZES:
        edges = generate.connected_weighted(n, m, SEED + n)
        requests = {task: {"task": task, "n": n, "edges": edges} for task in ("kruskal", "prim")}
        expected = checker.reference(requests["kruskal"])
        times = {}
        for task, request in requests.items():
            method = getattr(algorithms, task)
            _, warm = time_once(method, request)
            problem = checker.check(request, warm, expected)
            if problem:
                raise SystemExit("%s n=%d: %s" % (task, n, problem))
            times[task] = [time_once(method, request)[0] for _ in range(RUNS)]
        k, p = statistics.median(times["kruskal"]), statistics.median(times["prim"])
        print("| %d | %d | %d | %s | %.1f | %s | %.1f | %.2f |" % (
            n, m, expected["cost"], ", ".join("%.1f" % t for t in times["kruskal"]), k,
            ", ".join("%.1f" % t for t in times["prim"]), p, p / k))


if __name__ == "__main__":
    main()
