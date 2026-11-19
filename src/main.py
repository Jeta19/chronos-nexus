import sys
import time
import tracemalloc
from collections import Counter

from generator import generate_galaxy, SIZES
from graph import Graph
from prediction import predict_shortages, shortages_to_missions
from meta import MetaOptimizer
from stats import plan_statistics
from events import block_route, affected_by_route, affected_by_ship, replan
from models import RESOURCES


def main(size="small"):
    p, r, m, s = SIZES[size]
    tracemalloc.start()
    t0 = time.time()

    planets, routes, ships, missions, facilities = generate_galaxy(p, r, m, s)
    g = Graph(planets, routes)
    meta = MetaOptimizer()

    # 1. Parashikimi
    shortages = predict_shortages(planets, horizon=120)
    proactive = shortages_to_missions(shortages, planets)[:200]
    all_missions = missions + proactive

    # 2. Shpërndarja e burimeve
    transport, unmet = meta.allocate(planets)
    total_need = sum(n for _, _, _, n in shortages) or 1.0

    # 3. Skedulimi
    plan, failed = meta.schedule(g, ships, all_missions)

    # 4. Infrastruktura
    infra_value, infra_cost, chosen = meta.infrastructure(facilities, 5000)

    # 5. Ngjarje dinamike
    replan_times = []
    edges = Counter()
    for e in plan:
        for a, b in zip(e[4], e[4][1:]):
            edges[(a, b)] += 1
    if edges:
        (u, v), _ = edges.most_common(1)[0]
        block_route(g, u, v)
        aff = affected_by_route(plan, u, v)
        t = time.time()
        plan, failed = replan(g, ships, all_missions, plan, failed, aff)
        replan_times.append(time.time() - t)
    if plan:
        sid = Counter(e[1] for e in plan).most_common(1)[0][0]
        ships[sid].alive = False
        aff = affected_by_ship(plan, sid)
        t = time.time()
        plan, failed = replan(g, ships, all_missions, plan, failed, aff)
        replan_times.append(time.time() - t)

    # 6. Statistikat dhe pikët
    stats = plan_statistics(g, plan, all_missions)
    _, peak = tracemalloc.get_traced_memory()
    total_time = time.time() - t0

    mission_success = 100 * len(plan) / max(1, len(all_missions))
    resource_security = 100 * (1 - min(1.0, unmet / total_need))
    economic = infra_value / 100
    score = (mission_success + resource_security + economic
             - transport / 10000 - stats["rreziku_total"] / 10)

    print(f"=== CHRONOS NEXUS ({size}) ===")
    print(f"Planetë: {p}, rrugë: {len(routes)}, misione: {len(all_missions)}, anije: {s}")
    print(f"Mungesa të parashikuara: {len(shortages)}")
    print(f"Misione të kryera: {len(plan)}, të dështuara: {len(failed)}")
    print(f"Burime të paplotësuara: {unmet:.1f}, transport: {transport:.1f}")
    print(f"Infrastruktura: {len(chosen)} objekte, vlera {infra_value:.1f}, kosto {infra_cost:.1f}")
    print(f"Distanca: {stats['distanca_totale']}, karburanti: {stats['karburanti_total']}, "
          f"rreziku: {stats['rreziku_total']}")
    print(f"Ngjarje të trajtuara: {len(replan_times)}, "
          f"koha mesatare re-planning: {sum(replan_times) / max(1, len(replan_times)):.3f}s")
    print(f"Nyje të eksploruara: {g.nodes_explored}")
    print(f"Koha totale: {total_time:.2f}s, memoria maksimale: {peak / 1024 / 1024:.1f} MB")
    print("Vendimet e Meta-Optimizer:")
    for comp, choice, reason in meta.log:
        print(f"  [{comp}] {choice} ({reason})")
    print(f"\nCIVILIZATION SCORE: {score:.1f}")
    print(f"  Mission Success={mission_success:.1f}  Resource Security={resource_security:.1f}  "
          f"Economic={economic:.1f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "small")