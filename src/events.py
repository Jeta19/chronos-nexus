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


def _ship_state(ships, plan):
    """Gjendja e anijeve pas misioneve të një plani: (koha e lirë, vendndodhja)."""
    state = {s.id: (s.available_at, s.location) for s in ships}
    for e in sorted(plan, key=lambda e: e[3]):
        state[e[1]] = (e[3], e[4][-1])
    return [replace(s, available_at=state[s.id][0], location=state[s.id][1])
            for s in ships]


def replan(graph, ships, missions, plan, failed, affected_ids):
    """Re-planning inkremental: mban misionet e pa prekura dhe riplanifikon
    vetëm ato të prekura, duke filluar nga gjendja e anijeve pas pjesës së mbajtur.

    Kthen (plani_i_ri, lista_e_dështuar_e_re).
    """
    by_id = {m.id: m for m in missions}
    keep = [e for e in plan if e[0] not in affected_ids]
    temp_ships = _ship_state(ships, keep)

    todo = [by_id[i] for i in affected_ids]
    for m in todo:
        m.status = "pending"
    new_plan, new_failed = greedy_schedule(graph, temp_ships, todo)
    return keep + new_plan, failed + new_failed


def reduce_production(planet, factor=0.4):
    """Ngjarje: prodhimi i planetit bie 60% (mbetet 40%). Ndikon te parashikimi."""
    for res in planet.production:
        planet.production[res] *= factor


def increase_risk(graph, u, v, new_risk=0.5, new_reliability=0.6):
    """Ngjarje: rruga u->v bëhet shumë më e rrezikshme. Kthen True nëse ekziston."""
    for r in graph.adj[u]:
        if r.target == v:
            r.risk = new_risk
            r.reliability = new_reliability
            return True
    return False


def schedule_new_mission(graph, ships, missions, plan, failed, new_mission):
    """Mision i ri emergjent: plani ekzistues mbahet, vetëm misioni i ri skedulohet."""
    temp_ships = _ship_state(ships, plan)
    new_plan, new_failed = greedy_schedule(graph, temp_ships, [new_mission])
    return plan + new_plan, failed + new_failed