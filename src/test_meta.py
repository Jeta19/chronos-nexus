import time
from generator import generate_galaxy
from graph import Graph
from prediction import predict_shortages, shortages_to_missions
from meta import MetaOptimizer

for name, (p, r, m, s) in [("small", (100, 500, 50, 20)),
                           ("medium", (1000, 10000, 500, 100))]:
    planets, routes, ships, missions, facilities = generate_galaxy(p, r, m, s)
    g = Graph(planets, routes)
    proactive = shortages_to_missions(predict_shortages(planets, horizon=120), planets)[:200]
    all_missions = missions + proactive

    meta = MetaOptimizer()
    t = time.time()
    plan, failed = meta.schedule(g, ships, all_missions)
    t_sched = time.time() - t
    v, c, ch = meta.infrastructure(facilities, 5000)
    tr, un = meta.allocate(planets)

    print(f"\n{name}: skedulim {len(plan)} planifikuar, {len(failed)} dështuar, "
          f"{g.nodes_explored} nyje, {t_sched:.2f}s")
    print(f"  infrastruktura: vlera={v:.1f}, kosto={c:.1f}")
    print(f"  shpërndarja: transport={tr:.1f}, paplotësuar={un:.1f}")
    for comp, choice, reason in meta.log:
        print(f"  [{comp}] {choice} ({reason})")