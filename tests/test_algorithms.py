import json
import pathlib
import random
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))
sys.path.insert(0, str(ROOT / "tests"))

import algorithms
import checker
import generate

PROGRAM = [sys.executable, str(ROOT / "src" / "Python" / "main.py")]
CASES = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
TASKS = ("dsu", "kruskal", "prim", "scc", "topo", "dag")


def run_program(requests, timeout=20):
    data = "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in requests)
    result = subprocess.run(PROGRAM, input=data, capture_output=True, text=True,
                            encoding="utf-8", timeout=timeout, check=True)
    lines = result.stdout.splitlines()
    assert len(lines) == len(requests), "one output line per request"
    return [json.loads(line) for line in lines]


def solve(request):
    return getattr(algorithms, request["task"])(request)


def random_request(task, rng, n_max=7, m_max=10):
    n = rng.randint(1 if task == "dag" else 0, n_max)
    m = rng.randint(0, m_max) if n else 0
    w = rng.choice([3, 10, 10 ** 9])
    if task == "dsu":
        return {"task": task, "n": n, "operations": [[rng.randrange(n), rng.randrange(n)] for _ in range(m)]}
    if task in ("kruskal", "prim"):
        return {"task": task, "n": n,
                "edges": [[rng.randrange(n), rng.randrange(n), rng.randint(-w, w)] for _ in range(m)]}
    if task in ("scc", "topo"):
        if task == "topo" and rng.random() < 0.5 and n:
            return {"task": task, "n": n, "edges": generate.random_dag(n, m, rng.random()) if n > 1 else []}
        return {"task": task, "n": n, "edges": [[rng.randrange(n), rng.randrange(n)] for _ in range(m)]}
    if rng.random() < 0.7 and n > 1:
        edges = generate.random_dag(n, m, rng.random(), weighted=True, low=-w, high=w)
    else:
        edges = [[rng.randrange(n), rng.randrange(n), rng.randint(-w, w)] for _ in range(m)]
    return {"task": task, "n": n, "source": rng.randrange(n), "edges": edges}


class HandwrittenCases(unittest.TestCase):
    def test_expected_answers_agree_with_independent_references(self):
        for case in CASES:
            request = case["input"]
            if request["task"] == "ping":
                continue
            with self.subTest(case=case["name"]):
                self.assertIsNone(checker.check(request, case["expected"], checker.reference(request)))

    def test_program_output_in_one_process_with_repeats(self):
        requests = [case["input"] for case in CASES]
        answers = run_program(requests + requests[::-1])
        for case, answer in zip(CASES + CASES[::-1], answers):
            with self.subTest(case=case["name"]):
                if case["input"]["task"] == "ping":
                    self.assertEqual(answer, {"status": "ready"})
                else:
                    self.assertIsNone(checker.check(case["input"], answer, case["expected"]))


class CheckerAcceptsAlternativesAndRejectsInvalidWitnesses(unittest.TestCase):

    def test_msf(self):
        request = {"task": "kruskal", "n": 3, "edges": [[0, 1, 5], [0, 1, -3], [1, 2, -3], [0, 2, -3], [2, 2, -100]]}
        expected = {"cost": -6, "components": 1}
        for ids in ([1, 2], [2, 1], [1, 3], [3, 2]):
            self.assertIsNone(checker.check(request, {"cost": -6, "components": 1, "edge_ids": ids}, expected))
        for ids, cost in (([1, 1], -6),
                          ([1, 4], -103),
                          ([0, 2], 2),
                          ([1], -3),
                          ([1, 2, 3], -9),
                          ([1, 2], -7)):
            answer = {"cost": cost, "components": 1, "edge_ids": ids}
            self.assertIsNotNone(checker.check(request, answer, expected), ids)

    def test_scc(self):
        request = {"task": "scc", "n": 5, "edges": [[0, 1], [1, 2], [2, 0], [2, 3], [1, 3], [3, 3], [4, 3]]}
        expected = {"component": [0, 0, 0, 1, 2]}
        self.assertIsNone(checker.check(request, {"component": [9, 9, 9, 4, 70],
                                                  "condensation": [[70, 4], [9, 4]]}, expected))
        for answer in ({"component": [9, 9, 9, 4, 70], "condensation": [[9, 4], [9, 4], [70, 4]]},
                       {"component": [9, 9, 9, 4, 70], "condensation": [[9, 4]]},
                       {"component": [9, 9, 9, 4, 70], "condensation": [[9, 4], [70, 4], [4, 4]]},
                       {"component": [9, 9, 4, 4, 70], "condensation": [[9, 4], [4, 9], [70, 4]]},
                       {"component": [1, 1, 1, 2, -1], "condensation": [[1, 2], [-1, 2]]}):
            self.assertIsNotNone(checker.check(request, answer, expected))

    def test_topo(self):
        request = {"task": "topo", "n": 4, "edges": [[0, 1], [0, 2], [1, 3], [2, 3]]}
        for order in ([0, 1, 2, 3], [0, 2, 1, 3]):
            self.assertIsNone(checker.check(request, {"acyclic": True, "order": order}, {"acyclic": True}))
        for answer in ({"acyclic": True, "order": [1, 0, 2, 3]},
                       {"acyclic": True, "order": [0, 1, 3]},
                       {"acyclic": True, "order": [0, 1, 1, 3]},
                       {"acyclic": False, "order": []},
                       {"acyclic": 1, "order": [0, 1, 2, 3]}):
            self.assertIsNotNone(checker.check(request, answer, {"acyclic": True}))

    def test_dag(self):
        request = {"task": "dag", "n": 4, "source": 0,
                   "edges": [[0, 1, 1], [0, 2, 2], [1, 3, 2], [2, 3, 1], [0, 3, 3], [0, 3, 3]]}
        expected = {"acyclic": True, "distance": [0, 1, 2, 3]}
        for parent in (2, 3, 4, 5):
            answer = {"acyclic": True, "distance": [0, 1, 2, 3], "parent_edge": [-1, 0, 1, parent]}
            self.assertIsNone(checker.check(request, answer, expected))
        for parents in ([-1, 0, 1, 0],
                        [-1, 0, 1, 1],
                        [0, 0, 1, 2],
                        [-1, 0, 1, -1],
                        [-1, 0, 1, 3.0]):
            answer = {"acyclic": True, "distance": [0, 1, 2, 3], "parent_edge": parents}
            self.assertIsNotNone(checker.check(request, answer, expected), parents)
        wrong = {"acyclic": True, "distance": [0, 1, 2, 4], "parent_edge": [-1, 0, 1, 2]}
        self.assertIsNotNone(checker.check(request, wrong, expected))
        minus_one = {"acyclic": True, "distance": [0, 1, 2, -1], "parent_edge": [-1, 0, 1, 2]}
        self.assertIsNotNone(checker.check(request, minus_one, expected))

    def test_dsu(self):
        request = {"task": "dsu", "n": 3, "operations": [[0, 1], [0, 1]]}
        self.assertIsNone(checker.check(request, {"states": [[2, 2], [2, 2]]}, checker.reference(request)))
        self.assertIsNotNone(checker.check(request, {"states": [[2, 2], [1, 3]]}, checker.reference(request)))


class RandomCrossCheck(unittest.TestCase):

    def test_random_small_graphs(self):
        rng = random.Random(20251025)
        for round_number in range(400):
            for task in TASKS:
                request = random_request(task, rng)
                with self.subTest(round=round_number, task=task, request=request):
                    self.assertIsNone(checker.check(request, solve(request), checker.reference(request)))

    def test_kruskal_and_prim_agree(self):
        rng = random.Random(7)
        for _ in range(200):
            request = random_request("kruskal", rng, n_max=40, m_max=80)
            a = algorithms.kruskal(request)
            b = algorithms.prim(dict(request, task="prim"))
            self.assertEqual((a["cost"], a["components"]), (b["cost"], b["components"]))

    def test_repeated_mixed_requests_in_one_process(self):
        rng = random.Random(99)
        requests = [random_request(rng.choice(TASKS), rng, n_max=30, m_max=60) for _ in range(300)]
        requests.insert(150, {"task": "ping"})
        answers = run_program(requests * 2)
        for request, answer in zip(requests * 2, answers):
            if request["task"] == "ping":
                self.assertEqual(answer, {"status": "ready"})
            else:
                self.assertIsNone(checker.check(request, answer, checker.reference(request)), request)


class RouteHelper(unittest.TestCase):
    EDGES = [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]]

    def result(self):
        return algorithms.dag({"task": "dag", "n": 5, "source": 0, "edges": self.EDGES})

    def test_reachable_target(self):
        route = algorithms.reconstruct_route(self.EDGES, self.result(), 0, 3)
        self.assertEqual(route, [0, 1, 2, 3])
        weight = sum(next(w for u, v, w in self.EDGES if (u, v) == pair) for pair in zip(route, route[1:]))
        self.assertEqual(weight, self.result()["distance"][3])

    def test_source(self):
        self.assertEqual(algorithms.reconstruct_route(self.EDGES, self.result(), 0, 0), [0])

    def test_unreachable_target(self):
        self.assertEqual(algorithms.reconstruct_route(self.EDGES, self.result(), 0, 4), [])

    def test_tied_and_parallel_edges(self):
        edges = [[0, 1, 1], [0, 2, 2], [1, 3, 2], [2, 3, 1], [0, 3, 3], [0, 3, 3]]
        result = algorithms.dag({"task": "dag", "n": 4, "source": 0, "edges": edges})
        route = algorithms.reconstruct_route(edges, result, 0, 3)
        self.assertIn(route, ([0, 1, 3], [0, 2, 3], [0, 3]))
        self.assertEqual(route[0], 0)
        self.assertEqual(route[-1], 3)
        tail, head, weight = edges[result["parent_edge"][3]]
        self.assertEqual((tail, head), (route[-2], 3))
        self.assertEqual(result["distance"][tail] + weight, 3)

    def test_cyclic_result_has_no_route(self):
        edges = [[0, 1, 1], [1, 0, 1]]
        result = algorithms.dag({"task": "dag", "n": 2, "source": 0, "edges": edges})
        self.assertEqual(algorithms.reconstruct_route(edges, result, 0, 1), [])

    def test_broken_witness_is_reported(self):
        result = {"acyclic": True, "distance": [0, 3, -4, 0, None], "parent_edge": [-1, 0, 0, 3, -1]}
        with self.assertRaises(ValueError):
            algorithms.reconstruct_route(self.EDGES, result, 0, 3)

    def test_route_on_deep_chain(self):
        n = 100000
        edges = generate.chain(n, weighted=True, weight=1)
        result = algorithms.dag({"task": "dag", "n": n, "source": 0, "edges": edges})
        self.assertEqual(algorithms.reconstruct_route(edges, result, 0, n - 1), list(range(n)))


if __name__ == "__main__":
    unittest.main()
