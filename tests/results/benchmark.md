$ python tests/benchmark.py
Python 3.12.3, Linux-6.18.44-fc-v153-x86_64-with-glibc2.39, CPU: Intel(R) Xeon(R) Processor @ 2.10GHz, 4 logical CPUs
Graphs: generate.connected_weighted(n, m, seed=2025 + n), weights in [-1e9, 1e9]
Runs per method and size: 5 timed after 1 warm-up; times in ms

| n | m | cost (both) | Kruskal runs | Kruskal median | Prim runs | Prim median | Prim/Kruskal |
|---:|---:|---:|---|---:|---|---:|---:|
| 1000 | 2500 | -538220789268 | 1.3, 1.1, 1.2, 1.1, 1.1 | 1.1 | 1.6, 1.5, 1.5, 1.5, 1.5 | 1.5 | 1.34 |
| 10000 | 25000 | -5292000852570 | 30.3, 27.9, 23.0, 23.0, 22.8 | 23.0 | 35.8, 35.2, 36.1, 38.5, 36.7 | 36.1 | 1.57 |
| 100000 | 250000 | -53264499032450 | 709.0, 627.7, 626.1, 624.5, 671.7 | 627.7 | 1293.7, 1506.4, 1253.0, 1245.1, 1200.2 | 1253.0 | 2.00 |
