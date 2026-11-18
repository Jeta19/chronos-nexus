import math
import random
from models import Planet, Route, Spacecraft, Mission, Facility, RESOURCES

# Sa konsumon 1000 banorë në ditë (vlera realiste sipas llojit të burimit)
PER_CAPITA = {
    "food": 0.5, "water": 1.0, "energy": 0.8, "fuel": 0.2,
    "medicine": 0.05, "minerals": 0.1, "materials": 0.15,
}

# Llojet e anijeve: (emri, kapaciteti, karburanti, shpejtësia, kosto operimi)
SHIP_TYPES = [
    ("scout",  (200, 350),  (500, 900),   (12, 15), (1, 3)),
    ("cargo",  (400, 700),  (900, 1500),  (8, 12),  (3, 6)),
    ("heavy",  (700, 1000), (1500, 2500), (5, 8),   (6, 10)),
]

FACILITY_TYPES = [
    # (emri, kosto, koha e ndërtimit, vlera strategjike)
    ("Farm",             (150, 300),  (10, 20), (80, 200)),
    ("Hospital",         (300, 600),  (20, 35), (150, 350)),
    ("Factory",          (400, 800),  (25, 45), (200, 400)),
    ("Energy Plant",     (500, 900),  (30, 50), (250, 450)),
    ("Defense System",   (600, 1000), (30, 50), (150, 500)),
    ("Research Station", (350, 700),  (25, 40), (120, 380)),
    ("Spaceport",        (700, 1000), (40, 60), (300, 500)),
    ("Mining Facility",  (250, 500),  (15, 30), (100, 250)),
]


def generate_galaxy(num_planets, num_routes, num_missions, num_ships, seed=42):
    """Krijon një galaktikë realiste. Me të njëjtin seed del gjithmonë e njëjta."""
    rng = random.Random(seed)

    # 1. Planetët: popullsia log-uniforme (shumë koloni të vogla, pak qendra të mëdha)
    planets = []
    for i in range(num_planets):
        pop = int(math.exp(rng.uniform(math.log(1000), math.log(1_000_000))))
        consumption = {r: pop / 1000 * PER_CAPITA[r] * rng.uniform(0.8, 1.2)
                       for r in RESOURCES}
        # Çdo planet ka 2 burime ku specializohet (prodhon teprica)
        specialties = rng.sample(RESOURCES, 2)
        production = {}
        for r in RESOURCES:
            if r in specialties:
                production[r] = consumption[r] * rng.uniform(1.5, 3.0)
            else:
                production[r] = consumption[r] * rng.uniform(0.6, 1.1)

        # 15% e planetëve kanë deficit real në një burim (që të provohet parashikimi)
        if rng.random() < 0.15:
            r = rng.choice(RESOURCES)
            production[r] = consumption[r] * rng.uniform(0.3, 0.7)

        # Rezerva për 20 deri 120 ditë konsum
        stock = {r: consumption[r] * rng.uniform(20, 120) for r in RESOURCES}
        planets.append(Planet(
            id=i,
            x=rng.uniform(0, 1000),
            y=rng.uniform(0, 1000),
            population=pop,
            production=production,
            consumption=consumption,
            stock=stock,
            storage_capacity=max(stock.values()) * 1.5,
            tech_level=rng.randint(1, 10),
            defense=rng.randint(1, 10),
            importance=min(1.0, 0.1 + pop / 1_000_000 * 0.6 + rng.uniform(0, 0.3)),
        ))

    # 2. Rrugët (zinxhir që e bën grafin të lidhur, pastaj rrugë të rastësishme)
    routes = []
    seen = set()

    def add_route(a, b):
        if a == b or (a, b) in seen:
            return
        seen.add((a, b))
        pa, pb = planets[a], planets[b]
        dist = math.hypot(pa.x - pb.x, pa.y - pb.y)
        routes.append(Route(
            source=a, target=b,
            distance=dist,
            travel_time=dist / rng.uniform(8, 14),
            fuel_cost=dist * rng.uniform(0.5, 1.5),
            risk=min(0.5, 0.02 + dist / 5000 + rng.uniform(0, 0.1)),
            capacity=rng.uniform(200, 1000),
            reliability=rng.uniform(0.90, 0.999),
        ))

    for i in range(num_planets - 1):
        add_route(i, i + 1)
        add_route(i + 1, i)
    while len(routes) < num_routes:
        add_route(rng.randrange(num_planets), rng.randrange(num_planets))

    # 3. Anijet (3 lloje)
    ships = []
    for i in range(num_ships):
        _, cap, fuel, speed, cost = rng.choice(SHIP_TYPES)
        fuel_cap = rng.uniform(*fuel)
        ships.append(Spacecraft(
            id=i,
            location=rng.randrange(num_planets),
            cargo_capacity=rng.uniform(*cap),
            fuel_capacity=fuel_cap,
            fuel=fuel_cap,
            speed=rng.uniform(*speed),
            reliability=rng.uniform(0.92, 0.999),
            operating_cost=rng.uniform(*cost),
        ))

    # 4. Misionet: afati varet nga largësia (realist, jo i rastësishëm)
    missions = []
    for i in range(num_missions):
        a = rng.randrange(num_planets)
        b = rng.randrange(num_planets)
        while b == a:
            b = rng.randrange(num_planets)
        pa, pb = planets[a], planets[b]
        dist = math.hypot(pa.x - pb.x, pa.y - pb.y)
        # Prioriteti 1 (emergjencë) është i rrallë, prioriteti 3-4 më i shpeshti
        priority = rng.choices([1, 2, 3, 4, 5], weights=[5, 15, 30, 30, 20])[0]
        cargo = "medicine" if priority == 1 and rng.random() < 0.6 else rng.choice(RESOURCES)
        # Emergjencat kanë afat më të ngushtë, misionet e zakonshme më të gjerë
        slack = rng.uniform(2, 4) if priority == 1 else rng.uniform(4, 12)
        missions.append(Mission(
            id=i, origin=a, destination=b,
            cargo_type=cargo,
            cargo_amount=rng.uniform(50, 600) if priority > 1 else rng.uniform(50, 300),
            deadline=(dist / 10 + 20) * slack,
            priority=priority,
            importance=min(1.0, rng.uniform(0.1, 0.7) + (6 - priority) * 0.06),
        ))

    # 5. Infrastruktura (8 lloje x 5 variante)
    facilities = []
    fid = 0
    for _ in range(5):
        for name, cost, btime, value in FACILITY_TYPES:
            facilities.append(Facility(
                id=fid, name=name,
                cost=rng.uniform(*cost),
                build_time=rng.uniform(*btime),
                value=rng.uniform(*value),
            ))
            fid += 1

    return planets, routes, ships, missions, facilities


# Madhësitë e kërkuara nga profesori
SIZES = {
    "small":  (100, 500, 50, 20),
    "medium": (1000, 10000, 500, 100),
    "large":  (10000, 100000, 5000, 500),
}