from collections import deque
from itertools import combinations

INT64 = range(-(1 << 63), 1 << 63)


def is_int(value):
    return type(value) is int and value in INT64


def int_list(value):
    return isinstance(value, list) and all(is_int(item) for item in value)


def reference_dsu(request):
    n = request["n"]
    owner = list(range(n))
    members = [[v] for v in range(n)]
    components, largest, states = n, (1 if n else 0), []
    for u, v in request["operations"]:
        a, b = owner[u], owner[v]
        if a != b:
            if len(members[a]) < len(members[b]):
                a, b = b, a
            for vertex in members[b]:
                owner[vertex] = a
            members[a] += members[b]
            members[b] = []
            components -= 1
            largest = max(largest, len(members[a]))
        states.append([components, largest])
    return {"states": states}


def count_components(n, edges):
    adjacency = [[] for _ in range(n)]
    for edge in edges:
        adjacency[edge[0]].append(edge[1])
        adjacency[edge[1]].append(edge[0])
    seen, components = [False] * n, 0
    for start in range(n):
        if seen[start]:
            continue
        components += 1
        seen[start] = True
        queue = deque([start])
        while queue:
            for v in adjacency[queue.popleft()]:
                if not seen[v]:
                    seen[v] = True
                    queue.append(v)
    return components


def _acyclic_forest(n, edges, ids):
    parent = list(range(n))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for edge_id in ids:
        a, b = root(edges[edge_id][0]), root(edges[edge_id][1])
        if a == b:
            return False
        parent[a] = b
    return True


def brute_force_msf_cost(n, edges):
    c = count_components(n, edges)
    best = None
    for ids in combinations(range(len(edges)), n - c):
        if _acyclic_forest(n, edges, ids):
            cost = sum(edges[i][2] for i in ids)
            best = cost if best is None else min(best, cost)
    return best if best is not None else 0


def boruvka_msf_cost(n, edges):
    parent = list(range(n))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    cost, merged = 0, True
    while merged:
        merged = False
        cheapest = {}
        for edge_id, (u, v, w) in enumerate(edges):
            a, b = root(u), root(v)
            if a == b:
                continue
            key = (w, edge_id)
            for r in (a, b):
                if r not in cheapest or key < cheapest[r]:
                    cheapest[r] = key
        for w, edge_id in set(cheapest.values()):
            u, v, _ = edges[edge_id]
            a, b = root(u), root(v)
            if a != b:
                parent[a] = b
                cost += w
                merged = True
    return cost


def reference_msf(request):
    n, edges = request["n"], request["edges"]
    cost = brute_force_msf_cost(n, edges) if len(edges) <= 12 else boruvka_msf_cost(n, edges)
    return {"cost": cost, "components": count_components(n, edges)}


def tarjan_components(n, edges):
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
    index, low, on_stack = [-1] * n, [0] * n, [False] * n
    label, stack, counter, next_label = [-1] * n, [], 0, 0
    for start in range(n):
        if index[start] != -1:
            continue
        work = [(start, 0)]
        while work:
            u, i = work.pop()
            if i == 0:
                index[u] = low[u] = counter
                counter += 1
                stack.append(u)
                on_stack[u] = True
            else:
                child = adjacency[u][i - 1]
                low[u] = min(low[u], low[child])
            while i < len(adjacency[u]):
                v = adjacency[u][i]
                i += 1
                if index[v] == -1:
                    work.append((u, i))
                    work.append((v, 0))
                    break
                if on_stack[v]:
                    low[u] = min(low[u], index[v])
            else:
                if low[u] == index[u]:
                    while True:
                        v = stack.pop()
                        on_stack[v] = False
                        label[v] = next_label
                        if v == u:
                            break
                    next_label += 1
    return label


def kahn_order(n, edges):
    indegree = [0] * n
    adjacency = [[] for _ in range(n)]
    for edge in edges:
        adjacency[edge[0]].append(edge[1])
        indegree[edge[1]] += 1
    queue = deque(v for v in range(n) if indegree[v] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adjacency[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    return order if len(order) == n else None


def bellman_ford(n, edges, source):
    distance = [None] * n
    distance[source] = 0
    for _ in range(max(n - 1, 0)):
        changed = False
        for u, v, w in edges:
            if distance[u] is not None and (distance[v] is None or distance[u] + w < distance[v]):
                distance[v] = distance[u] + w
                changed = True
        if not changed:
            break
    return distance


def reference_dag(request):
    n, edges, source = request["n"], request["edges"], request["source"]
    order = kahn_order(n, edges)
    if order is None:
        return {"acyclic": False, "distance": [], "parent_edge": []}
    if len(edges) <= 2000:
        return {"acyclic": True, "distance": bellman_ford(n, edges, source)}
    outgoing = [[] for _ in range(n)]
    for u, v, w in edges:
        outgoing[u].append((v, w))
    distance = [None] * n
    distance[source] = 0
    for u in order:
        if distance[u] is not None:
            for v, w in outgoing[u]:
                if distance[v] is None or distance[u] + w < distance[v]:
                    distance[v] = distance[u] + w
    return {"acyclic": True, "distance": distance}


def reference(request):
    task = request["task"]
    if task == "dsu":
        return reference_dsu(request)
    if task in ("kruskal", "prim"):
        return reference_msf(request)
    if task == "scc":
        return {"component": tarjan_components(request["n"], request["edges"])}
    if task == "topo":
        return {"acyclic": kahn_order(request["n"], request["edges"]) is not None}
    if task == "dag":
        return reference_dag(request)
    raise ValueError(task)


def same_partition(labels, other):
    forward, backward = {}, {}
    for a, b in zip(labels, other):
        if forward.setdefault(a, b) != b or backward.setdefault(b, a) != a:
            return False
    return len(labels) == len(other)


def check(request, answer, expected):
    try:
        return _check(request, answer, expected)
    except (KeyError, TypeError, IndexError, ValueError) as error:
        return "malformed answer: %r" % (error,)


def _check(x, y, e):
    task, n = x["task"], x.get("n")
    if task == "dsu":
        if y["states"] != e["states"] or not all(int_list(s) and len(s) == 2 for s in y["states"]):
            return "states differ from expected"
        return None

    if task in ("kruskal", "prim"):
        edges, ids = x["edges"], y["edge_ids"]
        if not (is_int(y["cost"]) and is_int(y["components"]) and int_list(ids)):
            return "cost, components and edge_ids must be 64-bit integers"
        if y["components"] != e["components"]:
            return "components %d, expected %d" % (y["components"], e["components"])
        if y["cost"] != e["cost"]:
            return "cost %d is not the minimum %d" % (y["cost"], e["cost"])
        if len(set(ids)) != len(ids) or len(ids) != n - y["components"]:
            return "a spanning forest needs n - c distinct edge IDs"
        if any(not 0 <= i < len(edges) for i in ids):
            return "edge ID out of range"
        if any(edges[i][0] == edges[i][1] for i in ids):
            return "a loop was chosen"
        if not _acyclic_forest(n, edges, ids):
            return "chosen edges contain a cycle"
        if sum(edges[i][2] for i in ids) != y["cost"]:
            return "cost is not the sum of the chosen edge weights"
        return None

    if task == "scc":
        labels, pairs = y["component"], y["condensation"]
        if not int_list(labels) or len(labels) != n or any(label < 0 for label in labels):
            return "component must hold one non-negative label per vertex"
        if not same_partition(labels, e["component"]):
            return "SCC partition differs from expected"
        if not all(int_list(p) and len(p) == 2 for p in pairs):
            return "condensation must hold [from,to] pairs"
        given = [tuple(p) for p in pairs]
        wanted = {(labels[u], labels[v]) for u, v in x["edges"] if labels[u] != labels[v]}
        if len(set(given)) != len(given):
            return "condensation repeats a pair"
        if set(given) != wanted:
            return "condensation pairs are missing or invented"
        return None

    if task == "topo":
        if type(y["acyclic"]) is not bool or y["acyclic"] != e["acyclic"]:
            return "acyclic flag is wrong"
        order = y["order"]
        if not y["acyclic"]:
            return None if order == [] else "a cyclic graph must return an empty order"
        if not int_list(order) or sorted(order) != list(range(n)):
            return "order must contain every vertex exactly once"
        position = [0] * n
        for index, vertex in enumerate(order):
            position[vertex] = index
        if any(position[u] >= position[v] for u, v in x["edges"]):
            return "some edge points backwards in the order"
        return None

    if task == "dag":
        if type(y["acyclic"]) is not bool or y["acyclic"] != e["acyclic"]:
            return "acyclic flag is wrong"
        distance, parents = y["distance"], y["parent_edge"]
        if not y["acyclic"]:
            return None if distance == [] and parents == [] else "cyclic graph needs two empty arrays"
        source, edges = x["source"], x["edges"]
        if distance != e["distance"] or any(d is not None and not is_int(d) for d in distance):
            return "distances differ from expected"
        if not int_list(parents) or len(parents) != n:
            return "parent_edge must hold one integer per vertex"
        for v in range(n):
            if v == source or distance[v] is None:
                if parents[v] != -1:
                    return "source and unreachable vertices need parent_edge -1"
                continue
            p = parents[v]
            if not 0 <= p < len(edges):
                return "parent edge ID out of range"
            a, b, w = edges[p]
            if b != v:
                return "parent edge %d does not end at %d" % (p, v)
            if distance[a] is None or distance[a] + w != distance[v]:
                return "parent edge %d is not tight" % p
        done = [False] * n
        done[source] = True
        for v in range(n):
            chain = []
            while distance[v] is not None and not done[v]:
                if len(chain) > n:
                    return "parent chain loops"
                chain.append(v)
                v = edges[parents[v]][0]
            for u in chain:
                done[u] = True
        return None
    return "unknown task"
