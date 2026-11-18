import time
from collections import Counter
from generator import generate_galaxy
from graph import Graph
from prediction import predict_shortages, shortages_to_missions
from scheduler import greedy_schedule
from events import block_route, affected_by_route, affected_by_ship, replan

planets, routes, ships, missions, facilities = generate_galaxy(100, 500, 50, 20)
g = Graph(planets, routes)
proactive = shortages_to_missions(predict_shortages(planets), planets)[:200]
all_missions = missions + proactive

plan, failed = greedy_schedule(g, ships, all_missions)
print(f"Plani fillestar: {len(plan)} të planifikuara, {len(failed)} të dështuara\n")


def compare(title, affected, plan_before, failed_before):
    n0 = g.nodes_explored
    t = time.time()
    plan_inc, failed_inc = replan(g, ships, all_missions, plan_before,
                                  failed_before, affected)
    t_inc = time.time() - t
    n_inc = g.nodes_explored - n0

    for m in all_missions:
        m.status = "pending"
    n0 = g.nodes_explored
    t = time.time()
    plan_full, failed_full = greedy_schedule(g, ships, all_missions)
    t_full = time.time() - t
    n_full = g.nodes_explored - n0

    print(title)
    print(f"  misione të prekura: {len(affected)} nga {len(all_missions)}")
    print(f"  inkremental: {len(plan_inc)} plan, {len(failed_inc)} dështuar, "
          f"{n_inc} nyje, {t_inc:.3f}s")
    print(f"  i plotë:     {len(plan_full)} plan, {len(failed_full)} dështuar, "
          f"{n_full} nyje, {t_full:.3f}s")
    if t_inc > 0:
        print(f"  shpejtësia: {t_full / t_inc:.1f}x më shpejt")
    print()
    return plan_inc, failed_inc


# Ngjarja 1: rruga më e përdorur bllokohet
edges = Counter()
for e in plan:
    for a, b in zip(e[4], e[4][1:]):
        edges[(a, b)] += 1
(u, v), uses = edges.most_common(1)[0]
print(f"Ngjarja 1: rruga {u}->{v} bllokohet (përdorej nga {uses} misione)")
block_route(g, u, v)
affected = affected_by_route(plan, u, v)
plan, failed = compare("Rezultati:", affected, plan, failed)
still_using = len(affected_by_route(plan, u, v))
print(f"Kontroll: misione që ende e përdorin rrugën e bllokuar = {still_using}\n")

# Ngjarja 2: anija me më shumë misione shkatërrohet
counts = Counter(e[1] for e in plan)
sid, k = counts.most_common(1)[0]
print(f"Ngjarja 2: anija {sid} shkatërrohet (kishte {k} misione)")
ships[sid].alive = False
affected = affected_by_ship(plan, sid)
plan, failed = compare("Rezultati:", affected, plan, failed)
print(f"Kontroll: misione të planit që e përdorin anijen e shkatërruar = "
      f"{len(affected_by_ship(plan, sid))}")