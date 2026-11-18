import time
from generator import generate_galaxy
from infrastructure import knapsack_dp, knapsack_greedy, knapsack_branch_and_bound

planets, routes, ships, missions, facilities = generate_galaxy(100, 500, 50, 20)
budget = 5000

print(f"Objekte: {len(facilities)}, buxheti: {budget}\n")

t = time.time()
v, c, ch = knapsack_dp(facilities, budget)
print(f"DP:      vlera={v:.1f}, kosto={c:.1f}, objekte={len(ch)}, koha={time.time()-t:.4f}s")

t = time.time()
v, c, ch = knapsack_greedy(facilities, budget)
print(f"Greedy:  vlera={v:.1f}, kosto={c:.1f}, objekte={len(ch)}, koha={time.time()-t:.4f}s")

t = time.time()
v, c, ch, nodes = knapsack_branch_and_bound(facilities, budget)
print(f"B&B:     vlera={v:.1f}, kosto={c:.1f}, objekte={len(ch)}, nyje={nodes}, koha={time.time()-t:.4f}s")