import math
from collections import deque

INF = float("inf")


class MinCostFlow:
    """Min-Cost Flow me Successive Shortest Path (SPFA).
    Kompleksiteti: O(F * V * E) në rastin më të keq, ku F = numri i augmentimeve."""

    def __init__(self, n):
        self.n = n
        self.g = [[] for _ in range(n)]

    def add_edge(self, u, v, cap, cost):
        """Kthen indeksin e skajit në g[u]."""
        self.g[u].append([v, cap, cost, len(self.g[v])])
        self.g[v].append([u, 0.0, -cost, len(self.g[u]) - 1])
        return len(self.g[u]) - 1

    def solve(self, s, t, max_flow=INF):
        flow = cost = 0.0
        augmentations = 0
        while flow < max_flow - 1e-9:
            dist = [INF] * self.n
            dist[s] = 0.0
            inq = [False] * self.n
            prev = [None] * self.n
            dq = deque([s])
            while dq:
                u = dq.popleft()
                inq[u] = False
                for i, (v, cap, c, _) in enumerate(self.g[u]):
                    if cap > 1e-9 and dist[u] + c < dist[v] - 1e-12:
                        dist[v] = dist[u] + c
                        prev[v] = (u, i)
                        if not inq[v]:
                            inq[v] = True
                            dq.append(v)
            if dist[t] == INF:
                break
            # pengesa më e ngushtë në rrugën e gjetur
            f = max_flow - flow
            v = t
            while v != s:
                u, i = prev[v]
                f = min(f, self.g[u][i][1])
                v = u
            v = t
            while v != s:
                u, i = prev[v]
                e = self.g[u][i]
                e[1] -= f
                self.g[v][e[3]][1] += f
                v = u
            flow += f
            cost += f * dist[t]
            augmentations += 1
        return flow, cost, augmentations


def _collect(planets, res, horizon):
    donors, receivers = [], []
    for p in planets:
        if res not in p.production or res not in p.consumption:
            continue
        net = p.production[res] - p.consumption[res]
        if net > 0:
            donors.append((p, net * horizon))
        elif net < 0 and p.stock[res] / (-net) <= horizon:
            need = -net * horizon - p.stock[res]
            if need > 0:
                receivers.append((p, need))
    return donors, receivers


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def allocate_mcf(planets, res, horizon=120, k=5, unit_cost=0.1, penalty=500.0):
    """Shpërndarja optimale e një burimi me Min-Cost Flow.
    k = numri i dhuruesve më të afërt për çdo marrës (None = të gjithë).
    Kthen (dërgesat, kosto_transporti, mungesa_e_paplotësuar, augmentime)."""
    donors, receivers = _collect(planets, res, horizon)
    if not donors or not receivers:
        return [], 0.0, sum(n for _, n in receivers), 0

    S, T = 0, 1
    d_off = 2
    r_off = 2 + len(donors)
    net = MinCostFlow(2 + len(donors) + len(receivers))

    for i, (_, avail) in enumerate(donors):
        net.add_edge(S, d_off + i, avail, 0.0)

    ship_edges = []          # (u, indeksi, donor, marrës)
    pen_edges = []
    total_need = 0.0
    for j, (rp, need) in enumerate(receivers):
        total_need += need
        # pruning: vetëm k dhuruesit më të afërt
        near = sorted(range(len(donors)), key=lambda i: _dist(donors[i][0], rp))
        if k is not None:
            near = near[:k]
        for i in near:
            idx = net.add_edge(d_off + i, r_off + j, need,
                               _dist(donors[i][0], rp) * unit_cost)
            ship_edges.append((d_off + i, idx, donors[i][0].id, rp.id))
        net.add_edge(r_off + j, T, need, 0.0)
        pen_edges.append((net.add_edge(S, r_off + j, need, penalty), j))

    flow, cost, aug = net.solve(S, T, total_need)

    shipments = []
    transport = 0.0
    for u, idx, did, rid in ship_edges:
        e = net.g[u][idx]
        sent = net.g[e[0]][e[3]][1]          # kapaciteti i skajit të kundërt = fluksi
        if sent > 1e-6:
            shipments.append((did, rid, sent))
            transport += sent * e[2]
    unmet = 0.0
    for idx, j in pen_edges:
        used = receivers[j][1] - net.g[S][idx][1]
        unmet += max(0.0, used)
    return shipments, transport, unmet, aug


def allocate_greedy(planets, res, horizon=120, unit_cost=0.1, penalty=500.0):
    """Baza e krahasimit: çdo marrës (më urgjenti i pari) merr nga dhuruesi më i afërt."""
    donors, receivers = _collect(planets, res, horizon)
    avail = {p.id: a for p, a in donors}
    dmap = {p.id: p for p, _ in donors}
    shipments, transport, unmet = [], 0.0, 0.0
    receivers.sort(key=lambda x: x[0].stock[res]
                   / max(1e-9, x[0].consumption[res] - x[0].production[res]))
    for rp, need in receivers:
        for did in sorted(avail, key=lambda i: _dist(dmap[i], rp)):
            if need <= 1e-9:
                break
            take = min(need, avail[did])
            if take <= 1e-9:
                continue
            avail[did] -= take
            need -= take
            shipments.append((did, rp.id, take))
            transport += take * _dist(dmap[did], rp) * unit_cost
        unmet += need
    return shipments, transport, unmet