# Assignment 3 Analysis - Graph Algorithms

Language is **Python** (`submission.json` has `{"language": "Python"}`), I tested with Python 3.12.3
All my code is in `src/Python/algorithms.py`, the given `main.py` adapter is not changed

## 1. How to build, run and test

Python has no build step
Run everything from the root of the repository

| What | Command |
|---|---|
| Launch check (ping) | `python tools/run.py --setup` |
| 36 public cases and state reset with two batches | `python tools/run.py --check` |
| My own requests, prints actual results | `python tools/run.py --input tests/my_cases.jsonl` |
| All my tests (correctness, witnesses, route helper, full limits) | `python -m unittest discover -s tests -v` |
| Tests of template tools | `python -m unittest discover -s tools -p "test_*.py"` |
| Kruskal vs Prim benchmark | `python tests/benchmark.py` |
| Route helper demo | `python tests/route_demo.py` |

On Windows you can write `py -3` instead of `python`
Outputs of these commands are saved in `tests/results/`

## 2. Methods

`n` is number of vertices, `m` number of edges, `q` number of union operations and `α` is inverse Ackermann function

### 2.1 `dsu` - disjoint set union

**Steps** `DisjointSet(n)` makes `parent[v] = v`, `size[v] = 1`, `components = n` and `largest = 1` (or 0 if `n = 0`)
For every operation `[u, v]` we call `union(u, v)` and add `[components, largest]` to states
`find` first goes up to the root and after that goes the same way again and points every vertex directly to the root, this is full path compression
`union` puts root of smaller set under root of bigger set (union by size)
So `size` is used for balancing and also it is the real size we print, no rank needed

**Invariant** `parent[r] == r` only for roots
`size[r]` is number of vertices in tree of root `r`
`components` = number of roots, `largest` = max of `size[r]`

**Correctness** Path compression changes only which ancestor vertex points to, root stays the same, so sets do not change
Union of two different roots merges exactly two sets, components goes down by 1 and new size is sum of two sizes
Sets never split so `largest` can only grow, comparing it with merged size keeps it correct

**Boundary cases** Self union (`u == v`) and repeated union find the same root and change nothing, but state is still added, so `len(states) == q`
For `n = 0` result is `states = []`

**Complexity** Time `O(n + q α(n))` amortized because of union by size + path compression
Memory `O(n + q)` with the `q` states in output

### 2.2 `kruskal` - minimum spanning forest

**Steps** Sort edge *indices* `0..m-1` by weight, this way original IDs stay
Go through them and take edge `(u, v, w)` only when `union(u, v)` works, it means `find(u) != find(v)`
We stop early when `n - 1` edges are taken
Answer `components = n - |chosen|`

**Invariant** Taken edges are a forest and this forest is inside some minimum spanning forest
DSU sets = trees of this forest

**Correctness** Cut property
When edge `e` joins two different trees `A` and `B`, all lighter edges were already checked, they joined trees or made cycle
So `e` is a lightest edge crossing cut `(A, rest)` and some MSF has it
Rejected edge closes cycle where other edges are not heavier, so we never need it
In the end each connected component is one tree, so `n - |chosen|` is number of components and isolated vertices are counted too

**Boundary cases**
- loop has `find(u) == find(v)` so it is never taken
- parallel edges - lightest goes first, others are rejected
- negative and equal weights need nothing special, sort is stable and any choice in tie is optimal
- total is Python int, no overflow
- for `n = 0` answer is `cost 0, [], 0`

**Complexity** Time `O(n + m log(m+1))` for sort and `O(m α(n))` for DSU
Memory `O(n + m)`

### 2.3 `prim` - minimum spanning forest with restarts

**Steps** Make adjacency lists with `(weight, edge_id, other_end)`, loops are skipped
For each `start` vertex that is not visited yet we add 1 to `components` (this is the restart), mark it and grow the tree with lazy binary heap (`heapq`)
Every step pushes edges from new vertex to unvisited vertices, throws away heap entries where far end is already visited, pops lightest edge going out of the tree, marks its far end and adds weight and original ID
Edge to `v` is pushed only if it is lighter than best edge already in heap for `v` (`best[v]`)
Heavier or equal edge can not be popped first anyway, so this only makes heap smaller

**Invariant** Visited vertices of current start are one tree, and this tree is part of some MSF
For every unvisited neighbour `v` heap has the lightest edge seen so far from tree to `v`

**Correctness** Again cut property - popped edge is lightest edge crossing cut (current tree, everything else)
Order `(weight, edge_id)` is total because IDs are unique
When heap is empty no edge goes out of the tree, component is finished and outer loop starts again at next unvisited vertex
So each restart is exactly one connected component

**Boundary cases** Loops are not in adjacency
Parallel edges are different heap entries with different IDs, so ID is chosen max once and only the lightest can win
Isolated vertex is a restart with empty heap
For `n = 0` loop does not run

**Complexity** Lazy heap gives time `O(n + m log(m+1))`, every edge is pushed max 2 times and push/pop is `O(log m)`
Memory `O(n + m)` for adjacency, heap and `best`

### 2.4 `scc` - Kosaraju

**Steps**
1. Build `successors` (G) and `predecessors` (transpose Gᵀ) in one pass over edges
2. **First DFS** on G over all vertices, without recursion
   `position[u]` keeps how far list of neighbours of u was scanned, so stopped vertex continues from the same place
   When all neighbours are done u goes to `finished`
3. **Second DFS** on Gᵀ, roots are taken in *decreasing* finish time (`reversed(finished)`)
   Every reached vertex without label gets current label (`0, 1, 2, ...`)
4. Condensation - for every edge where labels of ends are different, put `(label_u, label_v)` in hash set, so each pair is only once

**Invariant** In second pass when new root `r` is taken, all SCCs with bigger max finish time already have labels
Search from `r` in Gᵀ can reach only SCC of `r` and already labelled SCCs, and labelled vertices are not entered

**Correctness** Kosaraju lemma - if in G there is edge from SCC C to SCC C′ then `max_finish(C) > max_finish(C′)`
In Gᵀ the edge goes C′ → C
Root with biggest remaining finish time is in SCC C, and all G-edges coming into C are from SCCs that already have labels
So search in Gᵀ from it covers exactly C, and same label = exactly one SCC

**Boundary cases** Loop or duplicate edge stays inside one SCC or gives repeated pair which set removes
Isolated vertex gets own label
`n = 0` gives two empty arrays
Deep chains work because both passes use explicit stack

**Complexity** Time `O(n + m)` expected (set operations are expected `O(1)`)
Memory `O(n + m)` for two adjacency lists, finish list, labels and set with max `m` pairs

### 2.5 `topo` - three state DFS

**Steps** `state` can be `UNVISITED`, `ACTIVE` or `DONE`
For each unvisited start we run DFS with explicit stack, stack has exactly the `ACTIVE` vertices
Vertex on top continues scan from `position[u]`
- `UNVISITED` neighbour becomes `ACTIVE` and goes on stack (scan position is saved before)
- `ACTIVE` neighbour is back edge, we return `acyclic=false, order=[]` right away
- `DONE` neighbour is forward or cross edge, ignore it

When scan is finished vertex becomes `DONE` and goes to finish list
Answer is reversed finish list

**Invariant** `ACTIVE` vertices are exactly current DFS path from root to top of stack
Every `DONE` vertex has all its descendants `DONE`

**Correctness** Edge `u → v` with `v` `ACTIVE` means `v` is ancestor of `u`, so `v ⇝ u → v` is directed cycle
Other way - when DFS first enters a cycle, it reaches the last edge of cycle while first vertex is still `ACTIVE`, so every cycle is found
If there is no cycle, for every edge `u → v` the vertex `v` finishes before `u` (tree or forward edge finishes inside u, cross edge goes to already `DONE` vertex)
So reversed finish order puts u before v for every edge

**Boundary cases** Loop `v → v` sees v `ACTIVE` → cycle
Cycle in later component is still found because outer loop goes over all vertices
Parallel edges dont matter
`n = 0` gives `true, []`

**Complexity** Time `O(n + m)`, with saved `position` every neighbour list is scanned once
Memory `O(n + m)`

### 2.6 `dag` - shortest paths in DAG

**Steps** Build `successors` and lists of outgoing edge IDs `outgoing`
Run the same three state DFS on the **whole** graph
If there is cycle, return `acyclic=false, distance=[], parent_edge=[]`
Else `distance[source] = 0`, other distances are `None` (it is JSON `null`), all `parent_edge` are `-1`
Go through vertices in topological order and skip vertex if its distance is still `None` (unreachable)
For every outgoing edge `(u, v, w)` with ID `e`, if `distance[v]` is `None` or `distance[u] + w < distance[v]`, save new distance and `parent_edge[v] = e`

**Invariant** When we process vertex u, all its predecessors were processed before, so `distance[u]` is final - it is shortest distance from source or `None` if u is unreachable
For every reachable `v ≠ source`, `parent_edge[v]` is edge that ends in `v` with `distance[tail] + w = distance[v]`

**Correctness** Induction by topological order
Shortest path to v ends with some edge `u → v`, u is earlier and already final, and this edge was relaxed when u was processed
Vertices before source in the order are not reachable, and source has no reachable incoming edge (it would be cycle), so source keeps `0` and `-1`
Strict `<` keeps the first tight edge, so every parent edge is tight and going by parents topological position always goes down until source

**Boundary cases**
- unreachable vertex is `null`, not `-1`, because `-1` can be real distance (there is test for this)
- cycle which source can not reach still gives `acyclic=false`, because check is on whole graph
- loop is cycle
- negative weights are fine since there are no cycles
- tied paths and parallel edges - any tight parent is ok
- sums bigger than 32 bit - Python int has no limit and `250000·10⁹` fits in 64 bit anyway

**Complexity** Time `O(n + m)`, memory `O(n + m)` together with output arrays

### 2.7 Route helper `reconstruct_route(edges, result, source, target)`

Starts at `target`, takes `edges[parent_edge[v]]`, checks that edge ends in `v`, goes to its tail and repeats until `source`
Then list is reversed
My choice: unreachable target (or cyclic result) gives **empty list `[]`**, source gives `[source]`
If witness is broken (parent edge does not end in the vertex or chain does not come to source) it raises `ValueError`
Time and memory `O(L)` for route with `L` vertices

Real calls (`python tests/route_demo.py`, also in `tests/results/route_demo.txt`):

```
## Published example (reachable target, source, unreachable target)
edges = [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]]
dag result = {"acyclic":true,"distance":[0,3,-4,0,null],"parent_edge":[-1,0,2,3,-1]}
reconstruct_route(edges, result, 0, 3) -> [0, 1, 2, 3]   edge IDs [0, 2, 3], total weight 0, distance 0
reconstruct_route(edges, result, 0, 0) -> [0]   edge IDs [], total weight 0, distance 0
reconstruct_route(edges, result, 0, 4) -> []   edge IDs [], total weight -, distance null

## Tied paths and parallel edges
edges = [[0, 1, 1], [0, 2, 2], [1, 3, 2], [2, 3, 1], [0, 3, 3], [0, 3, 3]]
dag result = {"acyclic":true,"distance":[0,1,2,3],"parent_edge":[-1,0,1,4]}
reconstruct_route(edges, result, 0, 3) -> [0, 3]   edge IDs [4], total weight 3, distance 3
reconstruct_route(edges, result, 0, 1) -> [0, 1]   edge IDs [0], total weight 1, distance 1

## Source that is not vertex 0
edges = [[0, 1, 1], [1, 2, 1], [2, 3, 4]]
dag result = {"acyclic":true,"distance":[null,null,0,4],"parent_edge":[-1,-1,-1,2]}
reconstruct_route(edges, result, 2, 3) -> [2, 3]   edge IDs [2], total weight 4, distance 4
reconstruct_route(edges, result, 2, 2) -> [2]   edge IDs [], total weight 0, distance 0
reconstruct_route(edges, result, 2, 0) -> []   edge IDs [], total weight -, distance null
```

Every route starts at source and ends at target, uses exactly the chosen `parent_edge` IDs and total weight = `distance[target]`
In the tied case vertex 3 has four optimal parents (edges 2, 3, 4, 5)
DFS order relaxed direct parallel edge 4 first and later edges with the same cost did not replace it because comparison is strict
Any of four is accepted, `tests/test_algorithms.py` checks that checker accepts all of them

## 3. State reset and deep DFS

**State reset** Every public function builds its arrays, DSU and heaps from its own request and returns new dict
There are no module level variables that change, so many requests in one process work same as separate runs
This is tested by
- `tools/run.py --check` (36 cases two times in one process)
- my 33 cases forward and then reversed in one process
- 300 random mixed requests with `ping` in the middle, sent two times in one process
- batch with one full size request of every task and a tiny `dag` after it

**Deep DFS** Recursion limit in CPython is about 1000 frames, recursive DFS would crash already on 2000 vertex chain from public tests
So all DFS passes (Kosaraju pass 1 and 2, cycle check for topo and dag) use Python list as explicit stack
The ones that can stop keep `position[u]`, so stopped vertex continues scan and never starts from beginning again
Tests have chains of 100000 vertices for `scc`, `topo`, `dag` and route helper, also ring of 100000 vertices and chain closed into cycle

## 4. My tests (`tests/`)

| File | What is inside |
|---|---|
| `cases.json` | 33 hand made cases: input, expected answer and `why` (explanation) |
| `my_cases.jsonl` | same inputs as JSON Lines for `python tools/run.py --input tests/my_cases.jsonl` |
| `results/my_cases_actual.jsonl` | actual output of this command |
| `checker.py` | my checker and reference solutions, it does not import the solution |
| `test_algorithms.py` | hand made cases, checker tests, random cross checks, mixed repeated requests, route helper |
| `test_scale.py` | full limits (n = 100000, m or q = 250000), each must be under 20 s batch limit |
| `generate.py` | generators with seed, large inputs are made again from seed and not stored |
| `results/*.txt`, `results/benchmark.md` | saved outputs of all commands |

**How answers are checked** Unique parts are compared exactly - DSU states, MSF cost and number of components, SCC partition (labels can be renamed), `acyclic`, DAG distances
Parts that are not unique are checked by validity:
- forest has distinct IDs, no loops, no cycle, exactly `n − c` edges and weights sum = `cost`
- condensation has every different cross SCC pair, each only once
- every edge goes forward in topological order
- every parent edge ends in its vertex and is tight, parent chains come to source

Reference answers use **other** algorithms than my solution:
- DSU - relabel of member lists
- MSF cost - brute force over all edge subsets (m ≤ 12) or Borůvka, components by BFS
- SCC - Tarjan
- cycles - Kahn queue
- DAG distances - Bellman-Ford, for big graphs relaxation in Kahn order

My hand made expected answers are also checked against these references (`HandwrittenCases.test_expected_answers_agree_with_independent_references`)

**Alternative answer and invalid witness** `CheckerAcceptsAlternativesAndRejectsInvalidWitnesses` shows that checker accepts:
- four different optimal forests of tied triangle
- renamed SCC labels
- both orders of diamond
- all four tight parents of tied vertex

and rejects:
- MSF answers with repeated ID, loop, not minimal tree, too few edges, cycle, or cost that does not match edges
- condensation with repeated, missing or internal pair, wrong partition or negative label
- topo order that goes backwards, is not complete or has duplicates, and integer instead of bool
- DAG parent edge which does not end in vertex, parent for source, missing parent, float parent, wrong distance and `-1` used for unreachable

**Covered boundaries** Empty graphs, `n = 1`, isolated vertices, disconnected graphs, self unions and repeated unions, union by rank vs size, loops, parallel edges, equal weights and tied optima, negative weights, sums above and below 32 bit range, forward and cross edges that are not cycles, cycle in later component, source that is not vertex 0 with unreachable vertices before it, distance `-1` as real value, cycle unreachable from source
Also 400 random rounds of every task against references, and Kruskal = Prim on 200 random graphs

**Mutation check** I broke the solution on purpose and test suite failed every time
What I broke:
- ignore `ACTIVE` neighbours in topo
- vertex instead of edge ID in `parent_edge`
- stop Kruskal one edge earlier
- increasing finish order in Kosaraju instead of decreasing
- keep internal pairs in condensation

**Full limit timings** (`tests/results/unittest.txt`, each request in its own process, start-up + JSON parse + output are included)

| Request | Time |
|---|---:|
| dsu random q=250000 | 1.23 s |
| dsu chain then repeats | 0.96 s |
| kruskal random / connected | 0.93 / 0.82 s |
| prim random / connected | 1.77 / 1.61 s |
| scc random / deep chain / giant cycle | 0.67 / 0.36 / 0.58 s |
| topo DAG / deep chain / chain closed into cycle | 0.48 / 0.13 / 0.12 s |
| dag full / deep chain / chain + unreachable cycle | 0.65 / 0.26 / 0.26 s |
| one full size request of every task in one process | 5.53 s |

## 5. Kruskal vs Prim benchmark

**Inputs** `generate.connected_weighted(n, m, seed = 2025 + n)` - random spanning tree plus random extra edges until `m`, weights are random integers in `[-10⁹, 10⁹]`
Both methods get the **same edge list** at three sizes, `m = 2.5 n`
Before timing, both answers are checked - valid forests with same minimum cost as Borůvka reference

**Command** `python tests/benchmark.py`, output is in `tests/results/benchmark.md`

**Environment** Python 3.12.3 (CPython), Linux 6.18 x86-64 (glibc 2.39), Intel Xeon @ 2.10 GHz, 4 logical CPUs, shared cloud container, background load was not controlled

**Timer and what is measured**
- timer is `time.perf_counter_ns`
- one call of `algorithms.kruskal(request)` or `algorithms.prim(request)` on request which is already parsed
- included: everything method builds by itself (for Kruskal sorted ID list and DSU, for Prim adjacency lists, heap and `best`)
- not included: JSON parsing, output and process start-up
- Python has no compilation so nothing to exclude there
- warm-up: 1 run per method and size which is not timed, `gc.collect()` before each call
- 5 timed runs per method per size, median in table

| n | m | cost (both) | Kruskal runs (ms) | Kruskal median | Prim runs (ms) | Prim median | Prim / Kruskal |
|---:|---:|---:|---|---:|---|---:|---:|
| 1000 | 2500 | -538220789268 | 1.3, 1.1, 1.2, 1.1, 1.1 | 1.1 | 1.6, 1.5, 1.5, 1.5, 1.5 | 1.5 | 1.34 |
| 10000 | 25000 | -5292000852570 | 30.3, 27.9, 23.0, 23.0, 22.8 | 23.0 | 35.8, 35.2, 36.1, 38.5, 36.7 | 36.1 | 1.57 |
| 100000 | 250000 | -53264499032450 | 709.0, 627.7, 626.1, 624.5, 671.7 | 627.7 | 1293.7, 1506.4, 1253.0, 1245.1, 1200.2 | 1253.0 | 2.00 |

**What I see**
- both give same minimum cost on every size, like cut property says
  Edge sets can be different only between edges with equal weight
- Kruskal is around 1.3-2 times faster here
  In CPython the main work of Kruskal is one call of built-in `sorted`, and it runs in C
  Prim does about `m` calls of `heappush`/`heappop` with tuple comparison and before that builds `2m` adjacency tuples
- from n = 10⁴ to 10⁵ (input 10× bigger) both become about 27-35× slower, it is more than `log m` alone
  I think reason is worse cache locality on big lists and garbage collector going over many new tuples

**Asymptotic** On these sparse graphs both are `O(n + m log m)` time and `O(n + m)` memory
Prim with indexed heap and decrease-key would be `O((n + m) log n)`, it helps on dense graphs where `m ≫ n`, but Python standard library has no such heap so I used lazy version with `best[v]` filter

**Limitations** Only one graph family (random connected, m = 2.5 n) and one machine
Dense graphs and graphs with many small components were not measured
Background load of cloud container was not controlled, so some runs are outliers (for example 1506.4 ms in Prim at biggest size), median makes it smaller problem
Numbers also depend on interpreter version

## 6. Sources and AI assistance

- algorithms are from standard textbook: Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms* (3rd ed.), chapters 21 (disjoint sets), 22 (DFS, topological sort, SCC), 23 (Kruskal, Prim) and 24.2 (shortest paths in DAG), also course lectures
- Python documentation for `heapq`
- **AI assistance:** I used Claude (Anthropic), AI assistant, to help with implementation, tests, benchmark script and this analysis
  I checked the code and run all commands from section 1 myself, outputs in `tests/results/` are from these runs
  I am responsible for correctness and originality of this work
