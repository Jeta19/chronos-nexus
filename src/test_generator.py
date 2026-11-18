from generator import generate_galaxy, SIZES
import time

for name, (p, r, m, s) in SIZES.items():
    start = time.time()
    planets, routes, ships, missions, facilities = generate_galaxy(p, r, m, s)
    print(f"{name}: {len(planets)} planetë, {len(routes)} rrugë, "
          f"{len(missions)} misione, {len(ships)} anije "
          f"({time.time() - start:.2f} sekonda)")