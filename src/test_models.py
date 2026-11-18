from models import Planet, Route

p = Planet(
    id=0, x=1.0, y=2.0, population=1000,
    production={"food": 300}, consumption={"food": 700},
    stock={"food": 10000}, storage_capacity=50000,
    tech_level=3, defense=2, importance=0.8,
)
r = Route(source=0, target=1, distance=15, travel_time=10,
          fuel_cost=25, risk=0.10, capacity=500, reliability=0.97)

print(p)
print(r)