from generator import generate_galaxy
from graph import Graph, WEIGHTS
import time

planets, routes, ships, missions, facilities = generate_galaxy(1000, 10000, 500, 100)
g = Graph(planets, routes)
w = WEIGHTS["cargo"]

for name in ["dijkstra", "astar"]:
    g.nodes_explored = 0
    start = time.time()
    total = 0
    for m in missions[:100]:
        cost, path = getattr(g, name)(m.origin, m.destination, w)
        total += cost
    print(f"{name}: kosto totale={total:.1f}, "
          f"nyje të eksploruara={g.nodes_explored}, "
          f"koha={time.time() - start:.3f}s")