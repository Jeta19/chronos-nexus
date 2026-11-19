import time
from scheduler import greedy_schedule
from infrastructure import knapsack_dp, knapsack_branch_and_bound
from flow import allocate_mcf
from models import RESOURCES


class MetaOptimizer:
    """Zgjedh algoritmin sipas madhësisë së problemit.
    Çdo vendim ruhet në self.log për raport."""

    def __init__(self):
        self.log = []

    def _note(self, component, choice, reason):
        self.log.append((component, choice, reason))

    def choose_top_k(self, n_missions):
        if n_missions <= 100:
            return 20
        if n_missions <= 1000:
            return 10
        return 5

    def schedule(self, graph, ships, missions):
        k = self.choose_top_k(len(missions))
        self._note("skedulimi", f"Greedy me top_k={k}",
                   f"{len(missions)} misione")
        return greedy_schedule(graph, ships, missions, top_k=k)

    def infrastructure(self, facilities, budget):
        if len(facilities) <= 25:
            self._note("infrastruktura", "Branch and Bound",
                       f"{len(facilities)} objekte, zgjidhje e saktë e lirë")
            v, c, ch, _ = knapsack_branch_and_bound(facilities, budget)
        else:
            self._note("infrastruktura", "Dynamic Programming",
                       f"{len(facilities)} objekte, kosto pseudo-polinomiale")
            v, c, ch = knapsack_dp(facilities, budget)
        return v, c, ch

    def allocate(self, planets, horizon=120):
        k = None if len(planets) <= 300 else 10
        self._note("shpërndarja", f"Min-Cost Flow me k={k}",
                   f"{len(planets)} planetë")
        total_tr = total_un = 0.0
        for res in RESOURCES:
            _, tr, un, _ = allocate_mcf(planets, res, horizon=horizon, k=k)
            total_tr += tr
            total_un += un
        return total_tr, total_un