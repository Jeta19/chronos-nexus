from models import Mission


def predict_shortages(planets, horizon=60):
    """Gjen çdo planet dhe burim që do të mbarojë brenda 'horizon' ditëve.

    Kthen listë me (dite_deri_ne_mungese, planet_id, burimi, sasia_qe_mungon),
    e renditur nga më urgjentja.
    """
    shortages = []
    for p in planets:
        for res in p.stock:
            # Kalo burimet që mungojnë në production ose consumption
            if res not in p.production or res not in p.consumption:
                continue
            net = p.production[res] - p.consumption[res]   # ndryshimi ditor
            if net >= 0:
                continue                                    # nuk po pakësohet
            days_left = p.stock[res] / (-net)
            if days_left <= horizon:
                needed = (-net) * horizon - p.stock[res]    # sa duhet për horizontin
                shortages.append((days_left, p.id, res, needed))
    shortages.sort()                                        # më urgjentet së pari
    return shortages


def shortages_to_missions(shortages, planets, next_id=10000, lead_time=10):
    """Kthen mungesat e parashikuara në misione dërgese.
    Burimi merret nga planeti më i afërt që ka teprica të këtij burimi.
    lead_time = sa ditë para mungesës duhet të mbërrijë dërgesa."""
    surplus = {}
    for p in planets:
        for res in p.production:
            if res in p.consumption and p.production[res] > p.consumption[res]:
                surplus.setdefault(res, []).append(p)

    missions = []
    for days_left, pid, res, needed in shortages:
        target = planets[pid]
        donors = surplus.get(res, [])
        if not donors:
            continue
        # donori më i afërt me vijë të drejtë
        donor = min(donors, key=lambda d: (d.x - target.x) ** 2 + (d.y - target.y) ** 2)
        missions.append(Mission(
            id=next_id, origin=donor.id, destination=pid,
            cargo_type=res, cargo_amount=min(needed, 800),
            deadline=max(20.0, (days_left - lead_time) * 10),
            priority=1 if days_left < 15 else 2,
            importance=target.importance,
        ))
        next_id += 1
    return missions