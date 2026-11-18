def knapsack_dp(facilities, budget, unit=10):
    """0/1 Knapsack me Dynamic Programming.

    Kostot rrumbullakohen te 'unit' për ta mbajtur tabelën të vogël.
    Kompleksiteti: O(n * B/unit) kohë, O(n * B/unit) memorie (për rindërtim).
    Kthen (vlera_totale, kosto_totale, lista_e_zgjedhur).
    """
    n = len(facilities)
    cap = int(budget // unit)
    costs = [max(1, int(round(f.cost / unit))) for f in facilities]

    # dp[i][c] = vlera më e mirë me objektet e para i dhe buxhet c
    dp = [[0.0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        f, w = facilities[i - 1], costs[i - 1]
        for c in range(cap + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c:
                alt = dp[i - 1][c - w] + f.value
                if alt > dp[i][c]:
                    dp[i][c] = alt

    # rindërtimi i zgjedhjes
    chosen = []
    c = cap
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(facilities[i - 1])
            c -= costs[i - 1]
    chosen.reverse()
    return dp[n][cap], sum(f.cost for f in chosen), chosen


def knapsack_greedy(facilities, budget):
    """Greedy: zgjedh sipas raportit vlerë/kosto. I shpejtë, por jo gjithmonë optimal."""
    ordered = sorted(facilities, key=lambda f: f.value / f.cost, reverse=True)
    chosen, spent, total = [], 0.0, 0.0
    for f in ordered:
        if spent + f.cost <= budget:
            chosen.append(f)
            spent += f.cost
            total += f.value
    return total, spent, chosen


def knapsack_branch_and_bound(facilities, budget, max_nodes=200000):
    """Branch and Bound me kufi të sipërm nga relaksimi fraksional.
    Prerja: nëse kufiri i sipërm <= zgjidhja më e mirë e njohur, dega hidhet.
    Kthen (vlera, kosto, lista, nyje_te_eksploruara)."""
    items = sorted(facilities, key=lambda f: f.value / f.cost, reverse=True)
    n = len(items)
    best = {"value": 0.0, "set": [], "cost": 0.0}
    nodes = [0]

    def bound(i, cost, value):
        # kufiri i sipërm: mbushim fraksionalisht me objektet e mbetura
        remaining = budget - cost
        b = value
        while i < n and items[i].cost <= remaining:
            remaining -= items[i].cost
            b += items[i].value
            i += 1
        if i < n:
            b += items[i].value * remaining / items[i].cost
        return b

    def search(i, cost, value, chosen):
        nodes[0] += 1
        if nodes[0] > max_nodes:
            return
        if value > best["value"]:
            best["value"], best["cost"], best["set"] = value, cost, list(chosen)
        if i == n:
            return
        if bound(i, cost, value) <= best["value"]:
            return                                  # pruning
        if cost + items[i].cost <= budget:          # merr objektin
            chosen.append(items[i])
            search(i + 1, cost + items[i].cost, value + items[i].value, chosen)
            chosen.pop()
        search(i + 1, cost, value, chosen)          # nuk e merr

    search(0, 0.0, 0.0, [])
    return best["value"], best["cost"], best["set"], nodes[0]