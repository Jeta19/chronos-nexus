from dataclasses import replace
from scheduler import greedy_schedule


def block_route(graph, u, v):
    """Ngjarje: rruga u->v bllokohet. Kthen True nëse rruga ekziston."""
    for r in graph.adj[u]:
        if r.target == v:
            r.available = False
            return True
    return False


def affected_by_route(plan, u, v):
    """Gjen misionet e planit që e përdorin rrugën u->v."""
    bad = set()
    for entry in plan:
        path = entry[4]
        for a, b in zip(path, path[1:]):
            if a == u and b == v:
                bad.add(entry[0])
                break
    return bad


def affected_by_ship(plan, ship_id):
    """Gjen misionet e planit që i kryen një anije e caktuar."""
    return {entry[0] for entry in plan if entry[1] == ship_id}


def replan(graph, ships, missions, plan, failed, affected_ids):
    """Re-planning inkremental: mban misionet e pa prekura dhe riplanifikon
    vetëm ato të prekura, duke filluar nga gjendja e anijeve pas pjesës së mbajtur.

    Kthen (plani_i_ri, lista_e_dështuar_e_re).
    """
    by_id = {m.id: m for m in missions}
    keep = [e for e in plan if e[0] not in affected_ids]

    # Gjendja e çdo anijeje pas misioneve të mbajtura: (koha e lirë, vendndodhja)
    state = {s.id: (s.available_at, s.location) for s in ships}
    for e in sorted(keep, key=lambda e: e[3]):
        state[e[1]] = (e[3], e[4][-1])
    temp_ships = [replace(s, available_at=state[s.id][0], location=state[s.id][1])
                  for s in ships]

    todo = [by_id[i] for i in affected_ids]
    for m in todo:
        m.status = "pending"
    new_plan, new_failed = greedy_schedule(graph, temp_ships, todo)
    return keep + new_plan, failed + new_failed