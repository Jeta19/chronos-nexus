from generator import generate_galaxy
from graph import Graph
from prediction import predict_shortages, shortages_to_missions
from scheduler import greedy_schedule
import time

planets, routes, ships, missions, facilities = generate_galaxy(1000, 10000, 500, 100)
g = Graph(planets, routes)

proactive = shortages_to_missions(predict_shortages(planets), planets)[:200]
all_missions = missions + proactive

start = time.time()
plan, failed = greedy_schedule(g, ships, all_missions)
print("Misione gjithsej:", len(all_missions))
print("Të planifikuara:", len(plan))
print("Të dështuara (pa anije/afat):", len(failed))
print("Nyje të eksploruara:", g.nodes_explored)
print(f"Koha: {time.time() - start:.2f}s")


from scheduler import local_search, plan_score

print("\n--- Local Search ---")
score_before = plan_score(plan, all_missions)
start = time.time()
plan2, failed2, score_after, improvements = local_search(g, ships, all_missions, plan, failed)
print("Pikët para:", round(score_before, 1))
print("Pikët pas:", round(score_after, 1))
print("Përmirësime të pranuara:", improvements)
print("Të planifikuara:", len(plan2), "| Të dështuara:", len(failed2))
print(f"Koha e Local Search: {time.time() - start:.2f}s")