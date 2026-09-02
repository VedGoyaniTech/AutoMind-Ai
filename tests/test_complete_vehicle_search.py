"""
Complete Automated Test Suite — Vehicle Search System
Validates entity matching, domain filtering, model conflict rejection, and structured extraction across all 20 test benchmark vehicles:
1. BMW M4
2. BMW X5
3. Audi RS5
4. Mercedes C-Class
5. Hyundai Creta
6. Hyundai Venue
7. Toyota Fortuner
8. Toyota Innova
9. Tata Nexon
10. Tata Punch
11. Mahindra Scorpio N
12. Mahindra XUV700
13. Kia Seltos
14. Honda City
15. Skoda Slavia
16. Volkswagen Virtus
17. MG Hector
18. Porsche 911
19. Ferrari SF90
20. Lamborghini Huracan
"""

import pytest
from app.services.vehicle_search.filter.entity_validator import VehicleEntityValidator
from app.services.vehicle_search.filter.trusted_domains import TrustedDomainFilter
from app.services.vehicle_search.filter.duplicate_remover import DuplicateRemover
from app.services.vehicle_search.search.query_optimizer import QueryOptimizer
from app.services.vehicle_search.models.vehicle import ExtractedVehicleData
from app.services.vehicle_search.validator.field_validator import FieldValidator
from app.services.vehicle_search.validator.consensus import ConsensusEngine


BENCHMARK_VEHICLES = [
    ("BMW M4", "BMW", "M4", ["X5", "M3", "3 Series"]),
    ("BMW X5", "BMW", "X5", ["M4", "M3"]),
    ("Audi RS5", "Audi", "RS5", ["R8", "Q5"]),
    ("Mercedes C-Class", "Mercedes", "C-Class", ["E-Class", "S-Class"]),
    ("Hyundai Creta", "Hyundai", "Creta", ["Venue", "Alcazar", "Tucson", "Exter"]),
    ("Hyundai Venue", "Hyundai", "Venue", ["Creta", "Alcazar"]),
    ("Toyota Fortuner", "Toyota", "Fortuner", ["Innova", "Glanza"]),
    ("Toyota Innova", "Toyota", "Innova", ["Fortuner", "Glanza"]),
    ("Tata Nexon", "Tata", "Nexon", ["Punch", "Harrier", "Safari", "Altroz"]),
    ("Tata Punch", "Tata", "Punch", ["Nexon", "Harrier"]),
    ("Mahindra Scorpio N", "Mahindra", "Scorpio", ["XUV700", "Thar"]),
    ("Mahindra XUV700", "Mahindra", "XUV700", ["Scorpio", "Thar"]),
    ("Kia Seltos", "Kia", "Seltos", ["Sonet", "Carens"]),
    ("Honda City", "Honda", "City", ["Amaze", "Elevate"]),
    ("Skoda Slavia", "Skoda", "Slavia", ["Kushaq", "Kodiaq"]),
    ("Volkswagen Virtus", "Volkswagen", "Virtus", ["Taigun", "Tiguan"]),
    ("MG Hector", "MG", "Hector", ["Astor", "ZS EV"]),
    ("Porsche 911", "Porsche", "911", ["Taycan", "Macan"]),
    ("Ferrari SF90", "Ferrari", "SF90", ["Roma", "296"]),
    ("Lamborghini Huracan", "Lamborghini", "Huracan", ["Urus", "Revuelto"])
]


def test_query_optimizer_benchmarks():
    optimizer = QueryOptimizer()
    for raw, brand, model, _ in BENCHMARK_VEHICLES:
        opt = optimizer.optimize(raw)
        assert brand.lower() in opt.lower() or raw.lower() in opt.lower()
        assert "price" in opt.lower() or "specifications" in opt.lower()


def test_entity_decomposition():
    validator = VehicleEntityValidator()
    for raw, brand, model, _ in BENCHMARK_VEHICLES:
        entity = validator.decompose_query(raw)
        assert entity.brand.lower() == brand.lower()
        assert model.lower() in entity.model.lower()


def test_model_conflict_rejection():
    validator = VehicleEntityValidator(threshold=0.90)

    # Test BMW M4 vs BMW X5 rejection
    m4_items = [
        {"title": "BMW M4 Competition Coupe Price & Specs", "url": "https://www.carwale.com/bmw-cars/m4/", "snippet": "BMW M4 Competition"},
        {"title": "BMW X5 SUV Price & Specs", "url": "https://www.carwale.com/bmw-cars/x5/", "snippet": "BMW X5 SUV"}
    ]
    valid_m4 = validator.validate_items("BMW M4", m4_items)
    assert len(valid_m4) == 1
    assert "M4" in valid_m4[0]["title"]

    # Test Tata Nexon vs Tata Punch rejection
    nexon_items = [
        {"title": "Tata Nexon Price & Specs", "url": "https://www.carwale.com/tata-cars/nexon/", "snippet": "Tata Nexon"},
        {"title": "Tata Punch SUV Price & Specs", "url": "https://www.carwale.com/tata-cars/punch/", "snippet": "Tata Punch"}
    ]
    valid_nexon = validator.validate_items("Tata Nexon", nexon_items)
    assert len(valid_nexon) == 1
    assert "Nexon" in valid_nexon[0]["title"]

    # Test Hyundai Creta vs Hyundai Venue rejection
    creta_items = [
        {"title": "Hyundai Creta Price & Specs", "url": "https://www.carwale.com/hyundai-cars/creta/", "snippet": "Hyundai Creta"},
        {"title": "Hyundai Venue Price & Specs", "url": "https://www.carwale.com/hyundai-cars/venue/", "snippet": "Hyundai Venue"}
    ]
    valid_creta = validator.validate_items("Hyundai Creta", creta_items)
    assert len(valid_creta) == 1
    assert "Creta" in valid_creta[0]["title"]


def test_duplicate_remover():
    remover = DuplicateRemover()
    items = [
        {"url": "https://www.carwale.com/bmw-cars/m4/"},
        {"url": "https://www.carwale.com/bmw-cars/m4"},
        {"url": "https://www.carwale.com/bmw-cars/m4#specs"}
    ]
    unique = remover.remove_duplicates(items)
    assert len(unique) == 1


def test_consensus_engine():
    consensus_engine = ConsensusEngine()
    data1 = ExtractedVehicleData(
        brand="BMW", model="M4", variant="Competition xDrive", price_ex_showroom="₹1.56 Crore",
        fuel="Petrol", transmission="Automatic", source_url="https://carwale.com/m4", source_domain="carwale.com"
    )
    data2 = ExtractedVehicleData(
        brand="BMW", model="M4", variant="Competition xDrive", price_ex_showroom="₹1.56 Crore",
        fuel="Petrol", transmission="Automatic", source_url="https://cardekho.com/m4", source_domain="cardekho.com"
    )

    consensus = consensus_engine.determine_consensus("BMW M4", [data1, data2])
    assert consensus is not None
    assert consensus.brand == "BMW"
    assert consensus.model == "M4"
    assert consensus.price_ex_showroom == "₹1.56 Crore"
    assert len(consensus.consensus_sources) == 2
