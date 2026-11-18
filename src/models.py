from dataclasses import dataclass, field
from typing import Dict, List

# Llojet e burimeve
RESOURCES = ["food", "water", "energy", "fuel", "medicine", "minerals", "materials"]


@dataclass
class Planet:
    id: int
    x: float
    y: float
    population: int
    production: Dict[str, float]
    consumption: Dict[str, float]
    stock: Dict[str, float]
    storage_capacity: float
    tech_level: int
    defense: int
    importance: float


@dataclass
class Route:
    source: int
    target: int
    distance: float
    travel_time: float
    fuel_cost: float
    risk: float
    capacity: float
    reliability: float
    available: bool = True


@dataclass
class Spacecraft:
    id: int
    location: int
    cargo_capacity: float
    fuel_capacity: float
    fuel: float
    speed: float
    reliability: float
    operating_cost: float
    available_at: float = 0.0
    alive: bool = True


@dataclass
class Mission:
    id: int
    origin: int
    destination: int
    cargo_type: str
    cargo_amount: float
    deadline: float
    priority: int
    importance: float
    status: str = "pending"


@dataclass
class Facility:
    id: int
    name: str
    cost: float
    build_time: float
    value: float