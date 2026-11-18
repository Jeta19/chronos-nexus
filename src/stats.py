def plan_statistics(graph, plan, missions):
    """Llogarit statistikat e planit duke ndjekur çdo rrugë të zgjedhur."""
    by_id = {m.id: m for m in missions}
    edge = {}
    for u in range(graph.n):
        for r in graph.adj[u]:
            edge[(r.source, r.target)] = r

    distance = fuel = time_total = 0.0
    survive = 1.0                    # probabiliteti që të gjitha rrugët të mos dështojnë
    risk_sum = 0.0
    delivered = {}
    for mid, sid, start, arrive, path, cost in plan:
        m = by_id[mid]
        delivered[m.cargo_type] = delivered.get(m.cargo_type, 0.0) + m.cargo_amount
        for a, b in zip(path, path[1:]):
            r = edge[(a, b)]
            distance += r.distance
            fuel += r.fuel_cost
            time_total += r.travel_time
            risk_sum += r.risk
            survive *= r.reliability
    return {
        "misione_te_kryera": len(plan),
        "distanca_totale": round(distance, 1),
        "karburanti_total": round(fuel, 1),
        "koha_totale_udhetimit": round(time_total, 1),
        "rreziku_total": round(risk_sum, 2),
        "burime_te_dorezuara": {k: round(v, 1) for k, v in delivered.items()},
    }