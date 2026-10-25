import pathlib
import sys
import time
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from test_algorithms import checker, generate, run_program

LIMIT_SECONDS = 20


class FullLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests = generate.large_requests()

    def test_each_large_request(self):
        for name, request in self.requests:
            with self.subTest(case=name):
                start = time.perf_counter()
                [answer] = run_program([request], timeout=LIMIT_SECONDS)
                elapsed = time.perf_counter() - start
                print("  %-40s %.2f s" % (name, elapsed))
                self.assertLess(elapsed, LIMIT_SECONDS)
                self.assertIsNone(checker.check(request, answer, checker.reference(request)))

    def test_mixed_large_batch_in_one_process(self):
        picked = {}
        for name, request in self.requests:
            picked.setdefault(request["task"], request)
        batch = list(picked.values()) + [{"task": "dag", "n": 1, "source": 0, "edges": []}]
        start = time.perf_counter()
        answers = run_program(batch, timeout=LIMIT_SECONDS)
        elapsed = time.perf_counter() - start
        print("  mixed batch of %d requests: %.2f s" % (len(batch), elapsed))
        self.assertLess(elapsed, LIMIT_SECONDS)
        self.assertEqual(answers[-1], {"acyclic": True, "distance": [0], "parent_edge": [-1]})
        for request, answer in zip(batch, answers):
            self.assertIsNone(checker.check(request, answer, checker.reference(request)))


if __name__ == "__main__":
    unittest.main()
