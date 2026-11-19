import time
from generator import generate_galaxy
from models import RESOURCES
from flow import allocate_mcf, allocate_greedy

PENALTY = 500.0

for name, (p, r, m, s) in [("small", (100, 500, 50, 20)), ("medium", (1000, 10000, 500, 100))]:
    planets, routes, ships, missions, facilities = generate_galaxy(p, r, m, s)
    print(f"\n{name}: {p} planetë")

    t = time.time()
    tr_gr = unmet_gr = 0.0
    for res in RESOURCES:
        sh, tr, un = allocate_greedy(planets, res)
        tr_gr += tr
        unmet_gr += un
    print(f"  Greedy      : transport={tr_gr:10.1f} paplotësuar={unmet_gr:8.1f} "
          f"TOTAL={tr_gr + PENALTY * unmet_gr:11.1f} koha={time.time() - t:.3f}s")

    for k in [5, 10, 20, None]:
        t = time.time()
        tr_m = unmet_m = 0.0
        aug = 0
        for res in RESOURCES:
            sh, tr, un, a = allocate_mcf(planets, res, k=k)
            tr_m += tr
            unmet_m += un
            aug += a
        label = f"MCF k={k}".ljust(12)
        print(f"  {label}: transport={tr_m:10.1f} paplotësuar={unmet_m:8.1f} "
              f"TOTAL={tr_m + PENALTY * unmet_m:11.1f} augmentime={aug} "
              f"koha={time.time() - t:.3f}s")