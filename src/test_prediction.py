from generator import generate_galaxy
from prediction import predict_shortages, shortages_to_missions
from models import Planet

# Shembulli i profesorit: 10000 ushqim, -400 në ditë => 25 ditë
p = Planet(id=0, x=0, y=0, population=1000,
           production={"food": 300}, consumption={"food": 700},
           stock={"food": 10000}, storage_capacity=50000,
           tech_level=1, defense=1, importance=0.5)
print("Shembulli:", predict_shortages([p]))

# Galaktikë reale
planets, routes, ships, missions, facilities = generate_galaxy(1000, 10000, 500, 100)
s = predict_shortages(planets, horizon=60)
print("Mungesa të parashikuara:", len(s))
if s:
    print("Më e urgjentja:", s[0])
new_missions = shortages_to_missions(s, planets)
print("Misione proaktive të krijuara:", len(new_missions))