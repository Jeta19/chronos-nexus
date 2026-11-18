import time
import tracemalloc
from generator import generate_galaxy
from graph import Graph
from prediction import predict_shortages, shortages_to_missions
from scheduler import greedy_schedule


def run(name, planets_n, routes_n, missions_n, ships_n, max_proactive=200):
    tracemalloc.start()
    t0 = time.time()

    planets, routes, ships, missions, facilities = generate_galaxy(
        planets_n, routes_n, missions_n, ships_n)
    g = Graph(planets, routes)
    shortages = predict_shortages(planets, horizon=120)
    proactive = shortages_to_missions(shortages, planets)[:max_proactive]
    all_missions = missions + proactive

    t1 = time.time()
    plan, failed = greedy_schedule(g, ships, all_missions)
    t_sched = time.time() - t1

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    total = time.time() - t0

    print(f"{name:7s} | planetë={planets_n:5d} rrugë={routes_n:6d} | "
          f"shortages={len(shortages):4d} | "
          f"misione={len(all_missions):4d} planifikuar={len(plan):4d} "
          f"dështuar={len(failed):3d} | nyje={g.nodes_explored:9d} | "
          f"skedulim={t_sched:7.2f}s total={total:7.2f}s | "
          f"memoria={peak / 1024 / 1024:6.1f}MB")


run("small", 100, 500, 50, 20)
run("medium", 1000, 10000, 500, 100)