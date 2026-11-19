import time
from collections import Counter
from generator import generate_galaxy
from graph import Graph
from models import Mission
from prediction import predict_shortages, shortages_to_missions
from scheduler import greedy_schedule
from events import (reduce_production, increase_risk, affected_by_route,
                    replan, schedule_new_mission)

planets, routes, ships, missions, facilities = generate_galaxy(100, 500, 50, 20)
g = Graph(planets, routes)
all_missions = missions + shortages_to_missions(
    predict_shortages(planets, horizon=120), planets)[:200]
plan, failed = greedy_schedule(g, ships, all_missions)
print(f"Plani fillestar: {len(plan)} planifikuar, {len(failed)} dështuar\n")

# Ngjarja 3: prodhimi i një planeti bie 60%
before = len(predict_shortages(planets, horizon=120))
reduce_production(planets[10])
after = len(predict_shortages(planets, horizon=120))
print(f"Ngjarja 3: prodhimi i planetit 10 bie 60%: mungesa {before} -> {after}\n")

# Ngjarja 4: rruga më e përdorur bëhet shumë e rrezikshme
edges = Counter()
for e in plan:
    for a, b in zip(e[4], e[4][1:]):
        edges[(a, b)] += 1
(u, v), uses = edges.most_common(1)[0]
increase_risk(g, u, v)
affected = affected_by_route(plan, u, v)
t = time.time()
plan, failed = replan(g, ships, all_missions, plan, failed, affected)
print(f"Ngjarja 4: rruga {u}->{v} bëhet e rrezikshme (përdorej nga {uses} misione)")
print(f"  riplanifikuar {len(affected)} misione në {time.time() - t:.3f}s, "
      f"plan {len(plan)}, dështuar {len(failed)}\n")

# Ngjarja 5: mision i ri emergjent
new = Mission(id=99999, origin=3, destination=77, cargo_type="medicine",
              cargo_amount=100, deadline=400, priority=1, importance=1.0)
all_missions.append(new)
n0 = g.nodes_explored
t = time.time()
plan, failed = schedule_new_mission(g, ships, all_missions, plan, failed, new)
done = any(e[0] == 99999 for e in plan)
print("Ngjarja 5: mision i ri emergjent")
print(f"  skeduluar: {done}, nyje: {g.nodes_explored - n0}, {time.time() - t:.3f}s")
print(f"  plani tani: {len(plan)} planifikuar, {len(failed)} dështuar")