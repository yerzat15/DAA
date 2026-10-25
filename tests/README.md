# My tests

Run all commands from repository root
Explanation of every case and of the checker is in `ANALYSIS.md`, section 4

```sh
python tools/run.py --check                          # 36 public cases + state reset
python tools/run.py --input tests/my_cases.jsonl     # my inputs -> actual outputs
python -m unittest discover -s tests -v              # all my tests (about 1 minute)
python tests/benchmark.py                            # Kruskal vs Prim timings
python tests/route_demo.py                           # route helper calls
```

| File | What it is |
|---|---|
| `cases.json` | 33 hand made cases with `input`, expected answer and `why` |
| `my_cases.jsonl` | same inputs as JSON Lines |
| `checker.py` | checker and reference solutions, does not import the solution |
| `test_algorithms.py` | hand made cases, checker tests, random cross checks, mixed repeated requests, route helper |
| `test_scale.py` | full limits (n = 100000, m or q = 250000), deep chains, 20 s batch limit |
| `generate.py` | graph generators with seed |
| `benchmark.py`, `route_demo.py` | benchmark and route helper demo |
| `results/` | saved outputs - `public_check.txt`, `my_cases_actual.jsonl`, `unittest.txt`, `benchmark.md`, `route_demo.txt` |

Answers that are not unique (forests, SCC labels, orders, parent edges) are checked by validity, so other correct answer passes and wrong witness fails
