from generator import generate_galaxy
from graph import Graph
from prediction import predict_shortages, shortages_to_missions
from scheduler import greedy_schedule, mission_weights

planets, routes, ships, missions, facilities = generate_galaxy(1000, 10000, 500, 100)
g = Graph(planets, routes)
proactive = shortages_to_missions(predict_shortages(planets), planets)[:200]
all_missions = missions + proactive

plan, failed = greedy_schedule(g, ships, all_missions)
by_id = {m.id: m for m in all_missions}

too_big = 0
impossible_deadline = 0
for mid in failed[:100]:
    m = by_id[mid]
    if all(s.cargo_capacity < m.cargo_amount for s in ships):
        too_big += 1
        continue
    cost, path = g.astar(m.origin, m.destination, mission_weights(m))
    if cost / 10.0 > m.deadline * 10:
        impossible_deadline += 1

print("Nga 100 të dështuara:")
print("  ngarkesa më e madhe se çdo anije:", too_big)
print("  afati i pamundur edhe pa pritje:", impossible_deadline)
print("  të tjera (anijet të zëna):", 100 - too_big - impossible_deadline)