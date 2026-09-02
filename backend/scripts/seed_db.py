import sys
import os

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine, Base
from app.models.user import User, UserPreference
from app.models.source import Source
from app.models.car import Manufacturer, CarModel, CarVariant
from app.core.security import get_password_hash
from app.services.ai.embedding_service import embedding_service
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.core.config import settings

def seed():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Sources
        print("Seeding Automotive Sources...")
        sources_data = [
            {"name": "CarWale Official", "domain": "carwale.com", "base_url": "https://www.carwale.com", "score": 0.98},
            {"name": "ZigWheels India", "domain": "zigwheels.com", "base_url": "https://www.zigwheels.com", "score": 0.96},
            {"name": "Cardekho Intelligence", "domain": "cardekho.com", "base_url": "https://www.cardekho.com", "score": 0.97},
            {"name": "Autocar India", "domain": "autocarindia.com", "base_url": "https://www.autocarindia.com", "score": 0.99},
            {"name": "EV India Portal", "domain": "evindia.online", "base_url": "https://www.evindia.online", "score": 0.95}
        ]

        source_objs = []
        for s in sources_data:
            existing = db.query(Source).filter(Source.domain == s["domain"]).first()
            if not existing:
                existing = Source(
                    name=s["name"],
                    domain=s["domain"],
                    base_url=s["base_url"],
                    source_type="Official Review",
                    reliability_score=s["score"]
                )
                db.add(existing)
                db.commit()
                db.refresh(existing)
            source_objs.append(existing)

        # 2. Seed / Synchronize Demo User
        print("Seeding/Ensuring Demo User (demo@automind.ai / password123)...")
        demo_user = db.query(User).filter(User.email == "demo@automind.ai").first()
        if not demo_user:
            demo_user = User(
                full_name="Alex Vance",
                email="demo@automind.ai",
                hashed_password=get_password_hash("password123"),
                is_admin=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            pref = UserPreference(user_id=demo_user.id, answer_detail="Balanced", units="Metric", currency="INR")
            db.add(pref)
            db.commit()
        else:
            # Synchronize password hash to guarantee password123 works
            demo_user.hashed_password = get_password_hash("password123")
            demo_user.is_admin = True
            db.commit()

        # 3. Seed Vehicles
        print("Seeding Sample Vehicles & Specifications...")
        vehicles_dataset = [
            {
                "manufacturer": "Tata",
                "model": "Nexon",
                "body_type": "SUV",
                "variant": "Creative Plus 1.2 Petrol MT",
                "price": 1150000,
                "on_road": 1320000,
                "fuel": "Petrol",
                "transmission": "Manual",
                "engine_cc": 1199,
                "hp": 118.2,
                "torque": 170.0,
                "mileage": 17.4,
                "airbags": 6,
                "safety": 5.0,
                "seats": 5,
                "boot": 382,
                "clearance": 208,
                "desc": "The Tata Nexon Creative Plus features a 5-star GNCAP safety rating, 6 airbags, 360-degree camera, and sequential LED DRLs.",
                "source_idx": 0
            },
            {
                "manufacturer": "Tata",
                "model": "Nexon EV",
                "body_type": "EV",
                "variant": "Empowered Plus Long Range",
                "price": 1699000,
                "on_road": 1790000,
                "fuel": "EV",
                "transmission": "Automatic",
                "battery": 40.5,
                "range": 465.0,
                "hp": 142.7,
                "torque": 215.0,
                "airbags": 6,
                "safety": 5.0,
                "seats": 5,
                "boot": 350,
                "clearance": 190,
                "desc": "Best selling electric SUV in India with V2L charging capability, 12.3-inch touchscreen, and 465 km ARAI certified range.",
                "source_idx": 4
            },
            {
                "manufacturer": "Hyundai",
                "model": "Creta",
                "body_type": "SUV",
                "variant": "SX (O) 1.5 Turbo DCT",
                "price": 2000000,
                "on_road": 2340000,
                "fuel": "Petrol",
                "transmission": "DCT",
                "engine_cc": 1482,
                "hp": 157.8,
                "torque": 253.0,
                "mileage": 18.4,
                "airbags": 6,
                "safety": 4.5,
                "seats": 5,
                "boot": 433,
                "clearance": 190,
                "desc": "Segment leading compact SUV with Level 2 ADAS suite, dual-zone climate control, and panoramic sunroof.",
                "source_idx": 1
            },
            {
                "manufacturer": "Kia",
                "model": "Seltos",
                "body_type": "SUV",
                "variant": "GTX Plus 1.5 Diesel AT",
                "price": 1980000,
                "on_road": 2310000,
                "fuel": "Diesel",
                "transmission": "Automatic",
                "engine_cc": 1493,
                "hp": 114.4,
                "torque": 250.0,
                "mileage": 19.1,
                "airbags": 6,
                "safety": 4.0,
                "seats": 5,
                "boot": 433,
                "clearance": 190,
                "desc": "Feature loaded SUV offering dual screen curved display, ventilated seats, and 17 autonomous ADAS safety features.",
                "source_idx": 2
            },
            {
                "manufacturer": "Mahindra",
                "model": "XUV400 EV",
                "body_type": "EV",
                "variant": "EL Pro 39.4 kWh",
                "price": 1749000,
                "on_road": 1850000,
                "fuel": "EV",
                "transmission": "Automatic",
                "battery": 39.4,
                "range": 456.0,
                "hp": 147.5,
                "torque": 310.0,
                "airbags": 6,
                "safety": 5.0,
                "seats": 5,
                "boot": 378,
                "clearance": 200,
                "desc": "Spacious electric SUV boasting 310 Nm instant torque, 0-100 km/h in 8.3 seconds, and dual 10.25-inch screens.",
                "source_idx": 4
            },
            {
                "manufacturer": "BMW",
                "model": "X5",
                "body_type": "SUV",
                "variant": "xDrive40i M Sport",
                "price": 9600000,
                "on_road": 11100000,
                "fuel": "Petrol",
                "transmission": "Automatic",
                "engine_cc": 2998,
                "hp": 375.0,
                "torque": 520.0,
                "mileage": 12.0,
                "airbags": 8,
                "safety": 5.0,
                "seats": 5,
                "boot": 650,
                "clearance": 214,
                "desc": "Luxury mid-size SUV featuring twin-turbo inline-6 mild-hybrid powertrain, BMW Curved Display, and adaptive air suspension.",
                "source_idx": 3
            },
            {
                "manufacturer": "Toyota",
                "model": "Fortuner",
                "body_type": "SUV",
                "variant": "2.8 Diesel 4x4 AT",
                "price": 3950000,
                "on_road": 4680000,
                "fuel": "Diesel",
                "transmission": "Automatic",
                "engine_cc": 2755,
                "hp": 201.1,
                "torque": 500.0,
                "mileage": 14.2,
                "airbags": 7,
                "safety": 5.0,
                "seats": 7,
                "boot": 296,
                "clearance": 225,
                "desc": "Iconic rugged 7-seater body-on-frame SUV with high resale value, active traction control, and 500 Nm pulling power.",
                "source_idx": 0
            },
            {
                "manufacturer": "Maruti",
                "model": "Brezza",
                "body_type": "SUV",
                "variant": "ZXi Plus 1.5 Smart Hybrid MT",
                "price": 1250000,
                "on_road": 1430000,
                "fuel": "Petrol",
                "transmission": "Manual",
                "engine_cc": 1462,
                "hp": 101.6,
                "torque": 136.8,
                "mileage": 19.8,
                "airbags": 6,
                "safety": 4.0,
                "seats": 5,
                "boot": 328,
                "clearance": 198,
                "desc": "Reliable city SUV with mild hybrid technology, head-up display, electric sunroof, and 19.8 km/l fuel efficiency.",
                "source_idx": 2
            }
        ]

        docs_for_vector = []
        texts_for_embed = []

        for item in vehicles_dataset:
            m_name = item["manufacturer"]
            m_obj = db.query(Manufacturer).filter(Manufacturer.name == m_name).first()
            if not m_obj:
                m_obj = Manufacturer(name=m_name, country="Global")
                db.add(m_obj)
                db.commit()
                db.refresh(m_obj)

            model_name = item["model"]
            c_model = db.query(CarModel).filter(CarModel.manufacturer_id == m_obj.id, CarModel.name == model_name).first()
            if not c_model:
                c_model = CarModel(manufacturer_id=m_obj.id, name=model_name, body_type=item["body_type"])
                db.add(c_model)
                db.commit()
                db.refresh(c_model)

            var_name = item["variant"]
            v_obj = db.query(CarVariant).filter(CarVariant.model_id == c_model.id, CarVariant.variant_name == var_name).first()
            if not v_obj:
                src = source_objs[item["source_idx"]]
                v_obj = CarVariant(
                    model_id=c_model.id,
                    source_id=src.id,
                    variant_name=var_name,
                    model_year=2024,
                    ex_showroom_price=item["price"],
                    estimated_on_road_price=item["on_road"],
                    fuel_type=item["fuel"],
                    transmission=item["transmission"],
                    engine_cc=item.get("engine_cc"),
                    horsepower=item.get("hp"),
                    torque_nm=item.get("torque"),
                    combined_mileage=item.get("mileage"),
                    battery_capacity=item.get("battery"),
                    electric_range=item.get("range"),
                    seating_capacity=item["seats"],
                    airbags=item["airbags"],
                    safety_rating=item.get("safety"),
                    boot_space=item.get("boot"),
                    ground_clearance=item.get("clearance"),
                    description=item["desc"],
                    source_url=f"{src.base_url}/cars/{m_name.lower()}-{model_name.lower()}"
                )
                db.add(v_obj)
                db.commit()
                db.refresh(v_obj)

            summary_text = f"{m_name} {model_name} {var_name} {item['body_type']} {item['fuel']} {item['transmission']} Price: ₹{item['price']} Airbags: {item['airbags']} Mileage: {item.get('mileage')} Range: {item.get('range')} Safety: {item.get('safety')} Stars. {item['desc']}"
            
            doc_meta = {
                "car_variant_id": v_obj.id,
                "manufacturer": m_name,
                "model": model_name,
                "variant": var_name,
                "body_type": item["body_type"],
                "fuel_type": item["fuel"],
                "ex_showroom_price": item["price"],
                "source_info": {
                    "id": v_obj.source.id,
                    "name": v_obj.source.name,
                    "domain": v_obj.source.domain,
                    "base_url": v_obj.source.base_url,
                    "reliability_score": v_obj.source.reliability_score
                } if v_obj.source else None
            }

            docs_for_vector.append(doc_meta)
            texts_for_embed.append(summary_text)

        # Build initial vector index
        print("Building Vector Index for Seed Data...")
        vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
        embeddings = embedding_service.encode(texts_for_embed)
        vector_store.add_documents(docs_for_vector, embeddings)
        print("Database & Vector Store successfully seeded!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
