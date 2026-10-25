import heapq


class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
        self.largest = 1 if n > 0 else 0

    def find(self, x):
        parent = self.parent
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def union(self, u, v):
        a, b = self.find(u), self.find(v)
        if a == b:
            return False
        size = self.size
        if size[a] < size[b]:
            a, b = b, a
        self.parent[b] = a
        size[a] += size[b]
        self.components -= 1
        if size[a] > self.largest:
            self.largest = size[a]
        return True


def dsu(request):
    """DSU with path compression and union by size, gives states after every union"""
    n = request["n"]
    operations = request["operations"]

    sets = DisjointSet(n)
    states = []
    for u, v in operations:
        sets.union(u, v)
        states.append([sets.components, sets.largest])
    return {"states": states}


def kruskal(request):
    """Kruskal, returns cost, edge_ids and components"""
    n = request["n"]
    edges = request["edges"]

    order = sorted(range(len(edges)), key=lambda edge_id: edges[edge_id][2])
    sets = DisjointSet(n)
    cost = 0
    edge_ids = []
    for edge_id in order:
        u, v, weight = edges[edge_id]
        if sets.union(u, v):
            cost += weight
            edge_ids.append(edge_id)
            if len(edge_ids) == n - 1:
                break
    return {"cost": cost, "edge_ids": edge_ids, "components": n - len(edge_ids)}


def prim(request):
    """Prim with lazy heap, starts again from every unvisited vertex"""
    n = request["n"]
    edges = request["edges"]

    adjacency = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        if u != v:
            adjacency[u].append((weight, edge_id, v))
            adjacency[v].append((weight, edge_id, u))

    visited = [False] * n
    best = [None] * n
    push, pop = heapq.heappush, heapq.heappop
    cost = 0
    edge_ids = []
    components = 0
    for start in range(n):
        if visited[start]:
            continue
        components += 1
        visited[start] = True
        heap = []
        vertex = start
        while True:
            for entry in adjacency[vertex]:
                v = entry[2]
                if not visited[v] and (best[v] is None or entry[0] < best[v]):
                    best[v] = entry[0]
                    push(heap, entry)
            while heap and visited[heap[0][2]]:
                pop(heap)
            if not heap:
                break
            weight, edge_id, vertex = pop(heap)
            visited[vertex] = True
            cost += weight
            edge_ids.append(edge_id)
    return {"cost": cost, "edge_ids": edge_ids, "components": components}


def _finish_order(n, successors):
    visited = [False] * n
    position = [0] * n
    finished = []
    for start in range(n):
        if visited[start]:
            continue
        visited[start] = True
        stack = [start]
        while stack:
            u = stack[-1]
            neighbours = successors[u]
            i = position[u]
            while i < len(neighbours) and visited[neighbours[i]]:
                i += 1
            if i < len(neighbours):
                v = neighbours[i]
                position[u] = i + 1
                visited[v] = True
                stack.append(v)
            else:
                position[u] = i
                stack.pop()
                finished.append(u)
    return finished


def scc(request):
    """Kosaraju with two DFS passes and transposed graph, returns component and condensation"""
    n = request["n"]
    edges = request["edges"]

    successors = [[] for _ in range(n)]
    predecessors = [[] for _ in range(n)]
    for u, v in edges:
        successors[u].append(v)
        predecessors[v].append(u)

    finished = _finish_order(n, successors)

    component = [-1] * n
    label = 0
    for root in reversed(finished):
        if component[root] != -1:
            continue
        component[root] = label
        stack = [root]
        while stack:
            u = stack.pop()
            for v in predecessors[u]:
                if component[v] == -1:
                    component[v] = label
                    stack.append(v)
        label += 1

    pairs = set()
    for u, v in edges:
        a, b = component[u], component[v]
        if a != b:
            pairs.add((a, b))
    condensation = [[a, b] for a, b in pairs]
    return {"component": component, "condensation": condensation}


def _topological_order(n, successors):
    UNVISITED, ACTIVE, DONE = 0, 1, 2
    state = [UNVISITED] * n
    position = [0] * n
    finished = []
    for start in range(n):
        if state[start] != UNVISITED:
            continue
        state[start] = ACTIVE
        stack = [start]
        while stack:
            u = stack[-1]
            neighbours = successors[u]
            i = position[u]
            descended = False
            while i < len(neighbours):
                v = neighbours[i]
                i += 1
                if state[v] == UNVISITED:
                    position[u] = i
                    state[v] = ACTIVE
                    stack.append(v)
                    descended = True
                    break
                if state[v] == ACTIVE:
                    return None
            if not descended:
                position[u] = i
                state[u] = DONE
                stack.pop()
                finished.append(u)
    finished.reverse()
    return finished


def topo(request):
    """Three state DFS, order is reversed finish order"""
    n = request["n"]
    edges = request["edges"]

    successors = [[] for _ in range(n)]
    for u, v in edges:
        successors[u].append(v)
    order = _topological_order(n, successors)
    if order is None:
        return {"acyclic": False, "order": []}
    return {"acyclic": True, "order": order}


def dag(request):
    """Cycle check on whole graph, then relaxation in topological order"""
    n = request["n"]
    source = request["source"]
    edges = request["edges"]

    successors = [[] for _ in range(n)]
    outgoing = [[] for _ in range(n)]
    for edge_id, (u, v, _) in enumerate(edges):
        successors[u].append(v)
        outgoing[u].append(edge_id)

    order = _topological_order(n, successors)
    if order is None:
        return {"acyclic": False, "distance": [], "parent_edge": []}

    distance = [None] * n
    parent_edge = [-1] * n
    distance[source] = 0
    for u in order:
        du = distance[u]
        if du is None:
            continue
        for edge_id in outgoing[u]:
            _, v, weight = edges[edge_id]
            candidate = du + weight
            dv = distance[v]
            if dv is None or candidate < dv:
                distance[v] = candidate
                parent_edge[v] = edge_id
    return {"acyclic": True, "distance": distance, "parent_edge": parent_edge}


def reconstruct_route(edges, result, source, target):
    """Route from source to target by parent_edge, empty list if target is unreachable"""
    distance = result["distance"]
    parent_edge = result["parent_edge"]
    if not result["acyclic"] or distance[target] is None:
        return []
    route = [target]
    vertex = target
    while vertex != source:
        edge_id = parent_edge[vertex]
        if edge_id < 0 or len(route) > len(distance):
            raise ValueError("parent_edge does not lead back to the source")
        tail, head, _ = edges[edge_id]
        if head != vertex:
            raise ValueError("parent edge %d does not end at vertex %d" % (edge_id, vertex))
        route.append(tail)
        vertex = tail
    route.reverse()
    return route
