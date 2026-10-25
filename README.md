# DAA Assignment 3 - Graph Algorithms

This is my solution for Assignment 3 in Design and Analysis of Algorithms
The story of the task is a campus festival - cables between places, order of preparation work and delivery routes, and every one of them is a graph problem

Language is Python (3.12 or newer), no extra libraries needed

## What is inside

Six methods in `src/Python/algorithms.py`

| Task | What it does | How |
|---|---|---|
| `dsu` | adds cables one by one and after each one says how many components and how big the largest is | union-find with path compression and union by size |
| `kruskal` | cheapest cable network (minimum spanning forest) | sort edges + DSU |
| `prim` | same thing but other way | heap, starts again in every component |
| `scc` | finds groups of tasks that depend on each other in a circle | Kosaraju, two DFS and transposed graph |
| `topo` | order of preparation work, or says it is impossible if there is a cycle | DFS with three states |
| `dag` | shortest delivery routes from one place, negative weights are ok | topological order + relaxation |

Also there is `reconstruct_route` which builds the actual route (list of vertices) from the `dag` answer

All DFS are written with own stack and without recursion, so even chain of 100000 vertices works fine

## Folders

- `src/Python/` - my code (`algorithms.py`) and the given `main.py` which reads JSON lines and calls my functions
- `tests/` - my tests, test cases with explanations, benchmark and saved results in `tests/results/`
- `tools/` - checker from the teacher with 36 public tests
- `ANALYSIS.md` - full report: how each algorithm works, why it is correct, complexity, tests and Kruskal vs Prim comparison
- `submission.json` - says which language is used

## How to run

From the root folder

```sh
python tools/run.py --setup                        # check that program starts
python tools/run.py --check                        # 36 public tests
python -m unittest discover -s tests -v            # my tests, takes about 1 minute
python tests/benchmark.py                          # Kruskal vs Prim timing
python tests/route_demo.py                         # examples of route helper
```

On Windows `py -3` can be used instead of `python`

Program works with JSON Lines - one request per line in, one answer per line out, for example

```
{"task":"dsu","n":4,"operations":[[0,1],[1,2],[0,2],[3,3]]}
```

gives

```
{"states":[[3,2],[2,3],[2,3],[2,3]]}
```

## Results

All 36 public tests pass, also my own tests (hand made cases, random graphs compared with other algorithms, full limits n = 100000 and m = 250000)
Biggest requests take around 0.1-2 seconds each, limit is 20 seconds
More details are in `ANALYSIS.md`
