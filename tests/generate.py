import random

N_MAX = 100000
M_MAX = 250000
W_MAX = 10 ** 9


def random_weighted(n, m, seed, low=-W_MAX, high=W_MAX):
    rng = random.Random(seed)
    return [[rng.randrange(n), rng.randrange(n), rng.randint(low, high)] for _ in range(m)]


def connected_weighted(n, m, seed, low=-W_MAX, high=W_MAX):
    rng = random.Random(seed)
    edges = [[rng.randrange(v), v, rng.randint(low, high)] for v in range(1, n)]
    edges += [[rng.randrange(n), rng.randrange(n), rng.randint(low, high)] for _ in range(m - len(edges))]
    rng.shuffle(edges)
    return edges


def random_dag(n, m, seed, weighted=False, low=-W_MAX, high=W_MAX):
    rng = random.Random(seed)
    label = list(range(n))
    rng.shuffle(label)
    edges = []
    for _ in range(m):
        a, b = rng.randrange(n), rng.randrange(n)
        while a == b:
            a, b = rng.randrange(n), rng.randrange(n)
        if a > b:
            a, b = b, a
        edge = [label[a], label[b]]
        if weighted:
            edge.append(rng.randint(low, high))
        edges.append(edge)
    return edges


def random_directed(n, m, seed):
    rng = random.Random(seed)
    return [[rng.randrange(n), rng.randrange(n)] for _ in range(m)]


def chain(n, weighted=False, weight=-W_MAX):
    return [[v, v + 1, weight] if weighted else [v, v + 1] for v in range(n - 1)]


def large_requests():
    n, m = N_MAX, M_MAX
    rng = random.Random(2025)
    operations = [[rng.randrange(n), rng.randrange(n)] for _ in range(m)]
    ring = [[v, (v + 1) % n] for v in range(n)]
    big_cycle = random_directed(n, m - n, 7) + ring
    return [
        ("dsu random q=250000", {"task": "dsu", "n": n, "operations": operations}),
        ("dsu chain then repeats", {"task": "dsu", "n": n,
                                     "operations": [[v, v + 1] for v in range(n - 1)] + operations[:m - n + 1]}),
        ("kruskal random full", {"task": "kruskal", "n": n, "edges": random_weighted(n, m, 11)}),
        ("prim random full", {"task": "prim", "n": n, "edges": random_weighted(n, m, 11)}),
        ("kruskal connected full", {"task": "kruskal", "n": n, "edges": connected_weighted(n, m, 12)}),
        ("prim connected full", {"task": "prim", "n": n, "edges": connected_weighted(n, m, 12)}),
        ("scc random full", {"task": "scc", "n": n, "edges": random_directed(n, m, 13)}),
        ("scc deep chain n=100000", {"task": "scc", "n": n, "edges": chain(n)}),
        ("scc one giant cycle", {"task": "scc", "n": n, "edges": big_cycle}),
        ("topo dag full", {"task": "topo", "n": n, "edges": random_dag(n, m, 14)}),
        ("topo deep chain n=100000", {"task": "topo", "n": n, "edges": chain(n)}),
        ("topo chain closed into a cycle", {"task": "topo", "n": n, "edges": chain(n) + [[n - 1, 0]]}),
        ("dag full", {"task": "dag", "n": n, "source": 0, "edges": random_dag(n, m, 15, weighted=True)}),
        ("dag deep chain n=100000", {"task": "dag", "n": n, "source": 0, "edges": chain(n, weighted=True)}),
        ("dag chain with far unreachable cycle", {"task": "dag", "n": n, "source": 0,
                                                  "edges": chain(n - 2, weighted=True) + [[n - 2, n - 1, 1], [n - 1, n - 2, 1]]}),
    ]
