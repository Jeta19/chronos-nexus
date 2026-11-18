import time
import tracemalloc
from generator import generate_galaxy
from graph import Graph
from prediction import predict_shortages, shortages_to_missions
from scheduler import greedy_schedule
from stats import plan_statistics

tracemalloc.start()
t0 = time.time()

planets, routes, ships, missions, facilities = generate_galaxy(100, 500, 50, 20)
g = Graph(planets, routes)
shortages = predict_shortages(planets, horizon=120)
proactive = shortages_to_missions(shortages, planets)[:200]
all_missions = missions + proactive

plan, failed = greedy_schedule(g, ships, all_missions)
stats = plan_statistics(g, plan, all_missions)

current, peak = tracemalloc.get_traced_memory()
total = time.time() - t0

print("=== STATISTIKAT ===")
print("Mungesa të parashikuara:", len(shortages))
print("Misione gjithsej:", len(all_missions))
print("Misione të kryera:", stats["misione_te_kryera"])
print("Misione të dështuara:", len(failed))
print("Distanca totale:", stats["distanca_totale"])
print("Karburanti total:", stats["karburanti_total"])
print("Rreziku total:", stats["rreziku_total"])
print("Burime të dorëzuara:", stats["burime_te_dorezuara"])
print("Nyje të eksploruara:", g.nodes_explored)
print(f"Koha totale: {total:.2f}s")
print(f"Memoria maksimale: {peak / 1024 / 1024:.1f} MB")