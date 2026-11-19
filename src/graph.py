import heapq
import math
from models import Route


# Peshat për lloje të ndryshme misionesh: (distancë, karburant, kohë, rrezik)
WEIGHTS = {
    "cargo":     (0.2, 0.6, 0.1, 0.1),   # kursen karburant
    "emergency": (0.0, 0.1, 0.5, 0.4),   # shpejt dhe i sigurt
    "balanced":  (0.25, 0.25, 0.25, 0.25),
}


class Graph:
    def __init__(self, planets, routes):
        self.planets = planets
        self.n = len(planets)
        # Lista e fqinjësisë: adj[u] = lista e rrugëve që nisin nga u
        self.adj = [[] for _ in range(self.n)]
        for r in routes:
            self.adj[r.source].append(r)
        self.nodes_explored = 0   # statistikë për profesorin
        self.uncertainty = True   # kosto e pritshme me besueshmëri

    def edge_cost(self, r: Route, w):
        """Kostoja e një rruge sipas peshave. Rreziku shumëzohet me 100
        që të jetë në të njëjtën shkallë me distancën.
        Me pasiguri: kostoja pritet = kosto bazë / besueshmëria
        (rruga që dështon riprovohet, shpërndarje gjeometrike)."""
        base = (w[0] * r.distance + w[1] * r.fuel_cost
                + w[2] * r.travel_time + w[3] * r.risk * 100)
        if self.uncertainty:
            return base + (1 - r.reliability) * 1000
        return base

    def heuristic(self, a, b, w):
        """Vlerësim i poshtëm për A*: w1 * distanca e drejtë.
        Mbetet i pranueshëm edhe me pasiguri, sepse
        base / reliability >= base >= w1 * distanca e drejtë."""
        pa, pb = self.planets[a], self.planets[b]
        straight = math.hypot(pa.x - pb.x, pa.y - pb.y)
        return w[0] * straight

    def dijkstra(self, start, goal, w):
        return self._search(start, goal, w, use_astar=False)

    def astar(self, start, goal, w):
        return self._search(start, goal, w, use_astar=True)

    def _search(self, start, goal, w, use_astar):
        """Kthen (kostoja, rruga si listë planetësh) ose (inf, [])."""
        dist = {start: 0.0}
        prev = {}
        h0 = self.heuristic(start, goal, w) if use_astar else 0.0
        heap = [(h0, start)]
        done = set()
        explored = 0

        while heap:
            _, u = heapq.heappop(heap)
            if u in done:
                continue
            done.add(u)
            explored += 1
            if u == goal:
                break
            for r in self.adj[u]:
                if not r.available:
                    continue
                v = r.target
                nd = dist[u] + self.edge_cost(r, w)
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = u
                    h = self.heuristic(v, goal, w) if use_astar else 0.0
                    heapq.heappush(heap, (nd + h, v))

        self.nodes_explored += explored
        if goal not in dist:
            return math.inf, []
        path = [goal]
        while path[-1] != start:
            path.append(prev[path[-1]])
        path.reverse()
        return dist[goal], path