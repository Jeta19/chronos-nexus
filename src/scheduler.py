from graph import WEIGHTS


def mission_weights(m):
    """Zgjedh peshat e rrugës sipas llojit të misionit."""
    if m.priority == 1:
        return WEIGHTS["emergency"]
    if m.cargo_type in ("fuel", "minerals", "materials"):
        return WEIGHTS["cargo"]
    return WEIGHTS["balanced"]


def urgency(m):
    """Sa më e vogël vlera, aq më urgjent misioni."""
    return (m.priority, m.deadline, -m.importance)


def greedy_schedule(graph, ships, missions, max_missions=None, top_k=10, order=None):
    """Greedy me pruning: çdo mision provon vetëm top_k anijet më të afërta.

    Nëse jepet 'order' (dict mission_id -> pozicioni), përdoret ai rend,
    përndryshe misionet rendisen sipas urgjencës.

    Kthen (plani, lista e dështuara). Plani është listë me
    (mission_id, ship_id, nisja, mberritja, rruga, kostoja).
    """
    plan = []
    failed = []
    free_at = {s.id: s.available_at for s in ships if s.alive}
    loc = {s.id: s.location for s in ships if s.alive}
    cache = {}                                   # memoizim i rrugëve

    def path_cost(a, b, w):
        key = (a, b, w)
        if key not in cache:
            cache[key] = graph.astar(a, b, w)
        return cache[key]

    if order is not None:
        todo = sorted(missions, key=lambda m: order[m.id])
    else:
        todo = sorted(missions, key=urgency)
    if max_missions:
        todo = todo[:max_missions]

    for m in todo:
        w = mission_weights(m)
        best = None

        # Pruning: vetëm top_k anijet më të afërta (me vijë të drejtë)
        ox = graph.planets[m.origin].x
        oy = graph.planets[m.origin].y
        candidates = sorted(
            (s for s in ships if s.alive and s.cargo_capacity >= m.cargo_amount),
            key=lambda s: (graph.planets[loc[s.id]].x - ox) ** 2
                          + (graph.planets[loc[s.id]].y - oy) ** 2,
        )[:top_k]

        for s in candidates:
            c1, p1 = path_cost(loc[s.id], m.origin, w)
            if not p1 and loc[s.id] != m.origin:
                continue
            c2, p2 = path_cost(m.origin, m.destination, w)
            if not p2:
                continue
            travel = (c1 + c2) / 10.0            # kohë e përafërt
            start = free_at[s.id]
            arrive = start + travel
            if arrive > m.deadline * 10:         # afati i kaluar
                continue
            if best is None or arrive < best[0]:
                best = (arrive, s, start, p1, p2, c1 + c2)

        if best is None:
            failed.append(m.id)
            m.status = "failed"
            continue

        arrive, s, start, p1, p2, cost = best
        free_at[s.id] = arrive
        loc[s.id] = m.destination
        m.status = "assigned"
        plan.append((m.id, s.id, start, arrive, p1[:-1] + p2, cost))

    return plan, failed


def plan_score(plan, missions):
    """Pikët e planit: rëndësia e misioneve të kryera, minus kostoja e vogël."""
    by_id = {m.id: m for m in missions}
    score = 0.0
    for mid, sid, start, arrive, path, cost in plan:
        m = by_id[mid]
        score += m.importance * (6 - m.priority) * 100   # prioriteti 1 vlen më shumë
        score -= cost * 0.01                             # kosto e vogël ndëshkuese
    return score


def local_search(graph, ships, missions, plan, failed, rounds=3):
    """Local Search: provon ta rindërtojë planin duke i dhënë përparësi
    misioneve të dështuara me rëndësi të lartë.

    Çdo raund: misionet e dështuara me vlerë të lartë vendosen para
    misioneve të planifikuara me vlerë më të vogël. Ndryshimi ruhet
    vetëm nëse pikët e planit rriten.
    """
    by_id = {m.id: m for m in missions}
    best_plan, best_failed = plan, failed
    best_score = plan_score(plan, missions)
    improvements = 0

    def value(m):
        return m.importance * (6 - m.priority)

    for _ in range(rounds):
        rescue = sorted((by_id[i] for i in best_failed),
                        key=lambda m: -value(m))[:20]
        if not rescue:
            break
        weak = sorted((by_id[p[0]] for p in best_plan), key=value)[:20]

        rescue_ids = {m.id for m in rescue}
        weak_ids = {m.id for m in weak}

        # rendi i ri: shpëtimi, pastaj të tjerat sipas urgjencës, në fund të dobëtit
        middle = sorted((m for m in missions
                         if m.id not in rescue_ids and m.id not in weak_ids),
                        key=urgency)
        reordered = rescue + middle + weak
        order = {m.id: i for i, m in enumerate(reordered)}

        for m in missions:
            m.status = "pending"
        new_plan, new_failed = greedy_schedule(graph, ships, missions, order=order)
        new_score = plan_score(new_plan, missions)

        if new_score > best_score:
            best_plan, best_failed, best_score = new_plan, new_failed, new_score
            improvements += 1
        else:
            break

    return best_plan, best_failed, best_score, improvements