from generator import generate_galaxy
from graph import Graph, WEIGHTS

planets, routes, ships, missions, facilities = generate_galaxy(1000, 10000, 500, 100)
g = Graph(planets, routes)
w = WEIGHTS["balanced"]
by_rel = {(r.source, r.target): r.reliability for u in range(g.n) for r in g.adj[u]}


def path_stats(path):
    surv = 1.0
    for a, b in zip(path, path[1:]):
        surv *= by_rel[(a, b)]
    return surv


for label, flag in [("pa pasiguri", False), ("me pasiguri", True)]:
    g.uncertainty = flag
    surv_sum = hops = 0.0
    n = 0
    for m in missions[:100]:
        cost, path = g.astar(m.origin, m.destination, w)
        if path:
            surv_sum += path_stats(path)
            hops += len(path) - 1
            n += 1
    print(f"{label:12s}: probabiliteti mesatar i sukseshit të rrugës={surv_sum / n:.4f}, "
          f"hop mesatar={hops / n:.2f}")