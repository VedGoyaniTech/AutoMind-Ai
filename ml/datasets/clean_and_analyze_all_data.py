import os
import json
import hashlib
import re
from collections import Counter
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VEC_DIR = os.path.join(BASE_DIR, "backend", "vector_index")
DOCS_FILE = os.path.join(VEC_DIR, "documents.json")
EMB_FILE = os.path.join(VEC_DIR, "embeddings.npy")
DATASETS_DIR = os.path.join(BASE_DIR, "ml", "datasets")

def main():
    print("=" * 80)
    print(" AUTOMIND AI — COMPLETE DATA ANALYSIS, CLEANING & VECTOR INDEX REBUILD ")
    print("=" * 80)

    # 1. Load original documents
    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        orig_docs = json.load(f)

    total_orig = len(orig_docs)
    print(f"[*] Total Raw Documents Before Cleaning: {total_orig}")

    MASTER_CARS = [
        # SUVs
        {"manufacturer": "Tata", "model": "Nexon", "variant": "Creative Plus 1.2 Petrol MT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 1150000, "safety_rating": "5.0", "airbags": 6, "mileage": 17.4, "seats": 5},
        {"manufacturer": "Tata", "model": "Punch", "variant": "Creative 1.2 MT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 885000, "safety_rating": "5.0", "airbags": 6, "mileage": 20.09, "seats": 5},
        {"manufacturer": "Tata", "model": "Harrier", "variant": "Fearless Plus Dark 2.0 AT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 2449000, "safety_rating": "5.0", "airbags": 7, "mileage": 16.8, "seats": 5},
        {"manufacturer": "Tata", "model": "Safari", "variant": "Accomplished Plus 6S AT", "body_type": "MUV / 7-Seater", "fuel_type": "Diesel", "ex_showroom_price": 2734000, "safety_rating": "5.0", "airbags": 7, "mileage": 16.3, "seats": 7},
        {"manufacturer": "Tata", "model": "Curvv", "variant": "Accomplished Plus 1.5 Kryojet", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 1749000, "safety_rating": "5.0", "airbags": 6, "mileage": 20.8, "seats": 5},
        {"manufacturer": "Mahindra", "model": "XUV700", "variant": "AX7 L AWD Diesel AT", "body_type": "MUV / 7-Seater", "fuel_type": "Diesel", "ex_showroom_price": 2604000, "safety_rating": "5.0", "airbags": 7, "mileage": 16.5, "seats": 7},
        {"manufacturer": "Mahindra", "model": "Scorpio-N", "variant": "Z8 L 4x4 Diesel AT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 2454000, "safety_rating": "5.0", "airbags": 6, "mileage": 15.2, "seats": 7},
        {"manufacturer": "Mahindra", "model": "Thar", "variant": "LX 4x4 Hard Top Diesel MT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 1675000, "safety_rating": "4.0", "airbags": 4, "mileage": 15.2, "seats": 4},
        {"manufacturer": "Mahindra", "model": "Thar Roxx", "variant": "AX7 L 4x4 Diesel AT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 2249000, "safety_rating": "5.0", "airbags": 6, "mileage": 15.2, "seats": 5},
        {"manufacturer": "Hyundai", "model": "Creta", "variant": "SX (O) 1.5 Turbo DCT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 2000000, "safety_rating": "4.5", "airbags": 6, "mileage": 18.4, "seats": 5},
        {"manufacturer": "Hyundai", "model": "Venue", "variant": "SX (O) 1.0 Turbo DCT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 1338000, "safety_rating": "4.0", "airbags": 6, "mileage": 18.3, "seats": 5},
        {"manufacturer": "Hyundai", "model": "Alcazar", "variant": "Signature 1.5 Turbo 6S DCT", "body_type": "MUV / 7-Seater", "fuel_type": "Petrol", "ex_showroom_price": 2155000, "safety_rating": "4.5", "airbags": 6, "mileage": 17.5, "seats": 6},
        {"manufacturer": "Kia", "model": "Seltos", "variant": "GTX Plus 1.5 Diesel AT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 1980000, "safety_rating": "4.0", "airbags": 6, "mileage": 19.1, "seats": 5},
        {"manufacturer": "Kia", "model": "Sonet", "variant": "GTX Plus 1.5 Diesel AT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 1575000, "safety_rating": "4.0", "airbags": 6, "mileage": 19.0, "seats": 5},
        {"manufacturer": "Kia", "model": "Carens", "variant": "Luxury Plus 1.5 Turbo 7DCT", "body_type": "MUV / 7-Seater", "fuel_type": "Petrol", "ex_showroom_price": 1967000, "safety_rating": "4.0", "airbags": 6, "mileage": 16.5, "seats": 7},
        {"manufacturer": "Toyota", "model": "Fortuner", "variant": "GR-S 4x4 Diesel AT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 5144000, "safety_rating": "5.0", "airbags": 7, "mileage": 14.4, "seats": 7},
        {"manufacturer": "Toyota", "model": "Innova Hycross", "variant": "ZX (O) Strong Hybrid e-CVT", "body_type": "MUV / 7-Seater", "fuel_type": "Hybrid", "ex_showroom_price": 3098000, "safety_rating": "5.0", "airbags": 6, "mileage": 23.24, "seats": 7},
        {"manufacturer": "Toyota", "model": "Innova Crysta", "variant": "ZX 2.4 Diesel 7S MT", "body_type": "MUV / 7-Seater", "fuel_type": "Diesel", "ex_showroom_price": 2630000, "safety_rating": "5.0", "airbags": 7, "mileage": 15.1, "seats": 7},
        {"manufacturer": "Toyota", "model": "Urban Cruiser Hyryder", "variant": "V Strong Hybrid e-CVT", "body_type": "SUV", "fuel_type": "Hybrid", "ex_showroom_price": 1999000, "safety_rating": "4.5", "airbags": 6, "mileage": 27.97, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Brezza", "variant": "ZXi Plus AT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 1398000, "safety_rating": "4.0", "airbags": 6, "mileage": 19.8, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Grand Vitara", "variant": "Alpha Plus Strong Hybrid", "body_type": "SUV", "fuel_type": "Hybrid", "ex_showroom_price": 1993000, "safety_rating": "4.5", "airbags": 6, "mileage": 27.97, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Fronx", "variant": "Alpha 1.0 Turbo 6AT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 1288000, "safety_rating": "4.0", "airbags": 6, "mileage": 20.01, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Jimny", "variant": "Alpha 4x4 1.5 AT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 1479000, "safety_rating": "3.5", "airbags": 6, "mileage": 16.39, "seats": 4},
        {"manufacturer": "Maruti Suzuki", "model": "Ertiga", "variant": "ZXi Plus AT", "body_type": "MUV / 7-Seater", "fuel_type": "Petrol", "ex_showroom_price": 1303000, "safety_rating": "3.5", "airbags": 4, "mileage": 20.3, "seats": 7},
        {"manufacturer": "Maruti Suzuki", "model": "XL6", "variant": "Alpha Plus AT", "body_type": "MUV / 7-Seater", "fuel_type": "Petrol", "ex_showroom_price": 1451000, "safety_rating": "3.5", "airbags": 4, "mileage": 20.27, "seats": 6},
        {"manufacturer": "MG", "model": "Hector", "variant": "Savvy Pro 1.5 Turbo CVT", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 2225000, "safety_rating": "4.0", "airbags": 6, "mileage": 13.96, "seats": 5},
        {"manufacturer": "MG", "model": "Hector Plus", "variant": "Savvy Pro 1.5 Turbo 6S CVT", "body_type": "MUV / 7-Seater", "fuel_type": "Petrol", "ex_showroom_price": 2320000, "safety_rating": "4.0", "airbags": 6, "mileage": 13.5, "seats": 6},
        {"manufacturer": "MG", "model": "Gloster", "variant": "Blackstorm 4x4 6S Diesel AT", "body_type": "SUV", "fuel_type": "Diesel", "ex_showroom_price": 4387000, "safety_rating": "5.0", "airbags": 6, "mileage": 12.04, "seats": 6},
        {"manufacturer": "Skoda", "model": "Kushaq", "variant": "Monte Carlo 1.5 TSI DSG", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 2049000, "safety_rating": "5.0", "airbags": 6, "mileage": 17.83, "seats": 5},
        {"manufacturer": "Skoda", "model": "Kodiaq", "variant": "L&K 2.0 TSI 4x4 DSG", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 3999000, "safety_rating": "5.0", "airbags": 9, "mileage": 13.32, "seats": 7},
        {"manufacturer": "Volkswagen", "model": "Taigun", "variant": "GT Plus Edge 1.5 TSI DSG", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 1999000, "safety_rating": "5.0", "airbags": 6, "mileage": 17.88, "seats": 5},
        {"manufacturer": "Volkswagen", "model": "Tiguan", "variant": "Elegance 2.0 TSI 4Motion", "body_type": "SUV", "fuel_type": "Petrol", "ex_showroom_price": 3517000, "safety_rating": "5.0", "airbags": 6, "mileage": 12.65, "seats": 5},

        # Electric Vehicles (EV)
        {"manufacturer": "Tata", "model": "Nexon EV", "variant": "Empowered Plus Long Range 45 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 1699000, "safety_rating": "5.0", "airbags": 6, "electric_range": 489, "seats": 5},
        {"manufacturer": "Tata", "model": "Punch EV", "variant": "Empowered Plus S Long Range", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 1429000, "safety_rating": "5.0", "airbags": 6, "electric_range": 421, "seats": 5},
        {"manufacturer": "Tata", "model": "Tiago EV", "variant": "XZ Plus Tech LUX Long Range", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 1189000, "safety_rating": "4.0", "airbags": 2, "electric_range": 315, "seats": 5},
        {"manufacturer": "Tata", "model": "Curvv EV", "variant": "Empowered Plus 55 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 2199000, "safety_rating": "5.0", "airbags": 6, "electric_range": 585, "seats": 5},
        {"manufacturer": "Mahindra", "model": "XUV400 EV", "variant": "EL Pro 39.4 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 1749000, "safety_rating": "5.0", "airbags": 6, "electric_range": 456, "seats": 5},
        {"manufacturer": "MG", "model": "ZS EV", "variant": "Exclusive Pro 50.3 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 2544000, "safety_rating": "5.0", "airbags": 6, "electric_range": 461, "seats": 5},
        {"manufacturer": "MG", "model": "Comet EV", "variant": "Exclusive 17.3 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 858000, "safety_rating": "3.5", "airbags": 2, "electric_range": 230, "seats": 4},
        {"manufacturer": "MG", "model": "Windsor EV", "variant": "Essence 38 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 1550000, "safety_rating": "5.0", "airbags": 6, "electric_range": 331, "seats": 5},
        {"manufacturer": "BYD", "model": "Atto 3", "variant": "Superior Extended Range 60.48 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 3399000, "safety_rating": "5.0", "airbags": 7, "electric_range": 521, "seats": 5},
        {"manufacturer": "BYD", "model": "Seal", "variant": "Performance AWD 82.56 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 5300000, "safety_rating": "5.0", "airbags": 9, "electric_range": 580, "seats": 5},
        {"manufacturer": "Hyundai", "model": "Ioniq 5", "variant": "Long Range RWD 72.6 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 4605000, "safety_rating": "5.0", "airbags": 6, "electric_range": 631, "seats": 5},
        {"manufacturer": "Kia", "model": "EV6", "variant": "GT Line AWD 77.4 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 6597000, "safety_rating": "5.0", "airbags": 8, "electric_range": 708, "seats": 5},
        {"manufacturer": "BMW", "model": "i4", "variant": "eDrive40 83.9 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 7250000, "safety_rating": "5.0", "airbags": 8, "electric_range": 590, "seats": 5},
        {"manufacturer": "BMW", "model": "iX", "variant": "xDrive50 111.5 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 13950000, "safety_rating": "5.0", "airbags": 8, "electric_range": 635, "seats": 5},
        {"manufacturer": "Mercedes-Benz", "model": "EQE SUV", "variant": "500 4MATIC 90.6 kWh", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 13900000, "safety_rating": "5.0", "airbags": 9, "electric_range": 550, "seats": 5},

        # Sedans
        {"manufacturer": "Honda", "model": "City", "variant": "ZX 1.5 i-VTEC CVT", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 1630000, "safety_rating": "5.0", "airbags": 6, "mileage": 18.4, "seats": 5},
        {"manufacturer": "Honda", "model": "City e:HEV", "variant": "ZX Strong Hybrid e-CVT", "body_type": "Sedan", "fuel_type": "Hybrid", "ex_showroom_price": 2055000, "safety_rating": "5.0", "airbags": 6, "mileage": 27.13, "seats": 5},
        {"manufacturer": "Honda", "model": "Amaze", "variant": "VX 1.2 Petrol CVT", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 996000, "safety_rating": "4.0", "airbags": 4, "mileage": 18.6, "seats": 5},
        {"manufacturer": "Hyundai", "model": "Verna", "variant": "SX (O) 1.5 Turbo DCT", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 1744000, "safety_rating": "5.0", "airbags": 6, "mileage": 20.6, "seats": 5},
        {"manufacturer": "Hyundai", "model": "Aura", "variant": "SX Plus 1.2 AMT", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 890000, "safety_rating": "3.5", "airbags": 6, "mileage": 20.5, "seats": 5},
        {"manufacturer": "Skoda", "model": "Slavia", "variant": "Monte Carlo 1.5 TSI DSG", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 1969000, "safety_rating": "5.0", "airbags": 6, "mileage": 18.73, "seats": 5},
        {"manufacturer": "Volkswagen", "model": "Virtus", "variant": "GT Plus Edge 1.5 TSI DSG", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 1941000, "safety_rating": "5.0", "airbags": 6, "mileage": 18.67, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Dzire", "variant": "ZXi Plus AGS (2024)", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 1014000, "safety_rating": "5.0", "airbags": 6, "mileage": 25.71, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Ciaz", "variant": "Alpha 1.5 AT", "body_type": "Sedan", "fuel_type": "Petrol", "ex_showroom_price": 1234000, "safety_rating": "4.0", "airbags": 2, "mileage": 20.04, "seats": 5},
        {"manufacturer": "Toyota", "model": "Camry", "variant": "Hybrid 2.5 e-CVT", "body_type": "Sedan", "fuel_type": "Hybrid", "ex_showroom_price": 4617000, "safety_rating": "5.0", "airbags": 9, "mileage": 19.1, "seats": 5},

        # Hatchbacks
        {"manufacturer": "Tata", "model": "Altroz", "variant": "XZ Plus (S) 1.2 DCA Petrol", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 1055000, "safety_rating": "5.0", "airbags": 6, "mileage": 18.5, "seats": 5},
        {"manufacturer": "Tata", "model": "Tiago", "variant": "XZ Plus 1.2 AMT", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 780000, "safety_rating": "4.0", "airbags": 2, "mileage": 19.0, "seats": 5},
        {"manufacturer": "Tata", "model": "Nano", "variant": "GenX Easy Shift AMT", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 335000, "safety_rating": "3.0", "airbags": 0, "mileage": 21.9, "seats": 4},
        {"manufacturer": "Maruti Suzuki", "model": "Swift", "variant": "ZXi Plus AGS (2024)", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 964000, "safety_rating": "3.5", "airbags": 6, "mileage": 25.75, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Baleno", "variant": "Alpha 1.2 AMT", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 988000, "safety_rating": "3.5", "airbags": 6, "mileage": 22.94, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Wagon R", "variant": "ZXi Plus 1.2 AGS", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 737000, "safety_rating": "3.0", "airbags": 2, "mileage": 24.43, "seats": 5},
        {"manufacturer": "Maruti Suzuki", "model": "Alto K10", "variant": "VXi Plus AGS", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 585000, "safety_rating": "3.0", "airbags": 2, "mileage": 24.9, "seats": 5},
        {"manufacturer": "Hyundai", "model": "i20", "variant": "Asta (O) 1.2 IVT", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 1121000, "safety_rating": "4.0", "airbags": 6, "mileage": 19.65, "seats": 5},
        {"manufacturer": "Hyundai", "model": "Grand i10 Nios", "variant": "Asta 1.2 AMT", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 856000, "safety_rating": "3.5", "airbags": 6, "mileage": 20.1, "seats": 5},
        {"manufacturer": "Toyota", "model": "Glanza", "variant": "V 1.2 AMT", "body_type": "Hatchback", "fuel_type": "Petrol", "ex_showroom_price": 999000, "safety_rating": "3.5", "airbags": 6, "mileage": 22.94, "seats": 5},

        # Luxury & Executive Cars
        {"manufacturer": "BMW", "model": "3 Series Gran Limousine", "variant": "330Li M Sport", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 6060000, "safety_rating": "5.0", "airbags": 8, "mileage": 15.39, "seats": 5},
        {"manufacturer": "BMW", "model": "5 Series", "variant": "530Li M Sport (LWB)", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 7290000, "safety_rating": "5.0", "airbags": 8, "mileage": 15.7, "seats": 5},
        {"manufacturer": "BMW", "model": "7 Series", "variant": "740i M Sport", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 18150000, "safety_rating": "5.0", "airbags": 10, "mileage": 12.6, "seats": 5},
        {"manufacturer": "BMW", "model": "X5", "variant": "xDrive40i M Sport", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 10990000, "safety_rating": "5.0", "airbags": 8, "mileage": 12.0, "seats": 5},
        {"manufacturer": "BMW", "model": "M5", "variant": "Competition 4.4L V8 Twin-Turbo", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 19990000, "safety_rating": "5.0", "airbags": 8, "mileage": 9.1, "seats": 5},
        {"manufacturer": "Mercedes-Benz", "model": "C-Class", "variant": "C 200 Avantgarde", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 6185000, "safety_rating": "5.0", "airbags": 7, "mileage": 16.9, "seats": 5},
        {"manufacturer": "Mercedes-Benz", "model": "E-Class", "variant": "E 200 LWB Exclusive", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 7850000, "safety_rating": "5.0", "airbags": 8, "mileage": 15.0, "seats": 5},
        {"manufacturer": "Mercedes-Benz", "model": "S-Class", "variant": "S 350d 4MATIC", "body_type": "Luxury", "fuel_type": "Diesel", "ex_showroom_price": 17700000, "safety_rating": "5.0", "airbags": 10, "mileage": 12.8, "seats": 5},
        {"manufacturer": "Mercedes-Benz", "model": "GLE", "variant": "450 4MATIC LWB", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 11000000, "safety_rating": "5.0", "airbags": 9, "mileage": 10.5, "seats": 5},
        {"manufacturer": "Mercedes-Benz", "model": "G-Class", "variant": "G 63 AMG 4.0 V8 Biturbo", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 36000000, "safety_rating": "5.0", "airbags": 9, "mileage": 6.1, "seats": 5},
        {"manufacturer": "Audi", "model": "A4", "variant": "Technology 40 TFSI", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 5458000, "safety_rating": "5.0", "airbags": 8, "mileage": 17.4, "seats": 5},
        {"manufacturer": "Audi", "model": "A6", "variant": "Technology 45 TFSI", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 7062000, "safety_rating": "5.0", "airbags": 8, "mileage": 14.1, "seats": 5},
        {"manufacturer": "Audi", "model": "Q7", "variant": "Technology 55 TFSI Quattro", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 9784000, "safety_rating": "5.0", "airbags": 8, "mileage": 11.2, "seats": 7},
        {"manufacturer": "Volvo", "model": "XC90", "variant": "B6 Ultimate 7S MHEV", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 10100000, "safety_rating": "5.0", "airbags": 8, "mileage": 11.04, "seats": 7},
        {"manufacturer": "Porsche", "model": "911", "variant": "Carrera S 3.0 Twin-Turbo", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 19900000, "safety_rating": "5.0", "airbags": 6, "mileage": 9.2, "seats": 4},
        {"manufacturer": "Porsche", "model": "Cayenne", "variant": "Base 3.0 V6 Turbo", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 13600000, "safety_rating": "5.0", "airbags": 8, "mileage": 10.8, "seats": 5},
        {"manufacturer": "Rolls-Royce", "model": "Phantom", "variant": "Series II 6.75L V12 Twin-Turbo", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 95000000, "safety_rating": "5.0", "airbags": 8, "mileage": 6.7, "seats": 5},
        {"manufacturer": "Rolls-Royce", "model": "Ghost", "variant": "Extended 6.75L V12", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 79500000, "safety_rating": "5.0", "airbags": 8, "mileage": 7.1, "seats": 5},
        {"manufacturer": "Rolls-Royce", "model": "Cullinan", "variant": "Black Badge 6.75L V12 4WD", "body_type": "Luxury", "fuel_type": "Petrol", "ex_showroom_price": 82000000, "safety_rating": "5.0", "airbags": 8, "mileage": 6.6, "seats": 5},
        {"manufacturer": "Rolls-Royce", "model": "Spectre", "variant": "EV Dual Electric 577 HP", "body_type": "EV / Electric", "fuel_type": "Electric", "ex_showroom_price": 75000000, "safety_rating": "5.0", "airbags": 8, "electric_range": 530, "seats": 4},

        # Supercars & Hypercars
        {"manufacturer": "Ferrari", "model": "296 GTB", "variant": "3.0L V6 Twin-Turbo Hybrid (819 HP)", "body_type": "Supercar", "fuel_type": "Hybrid", "ex_showroom_price": 54000000, "safety_rating": "5.0", "airbags": 6, "mileage": 14.0, "seats": 2},
        {"manufacturer": "Ferrari", "model": "SF90 Stradale", "variant": "4.0L V8 PHEV AWD (986 HP)", "body_type": "Supercar", "fuel_type": "Hybrid", "ex_showroom_price": 75000000, "safety_rating": "5.0", "airbags": 6, "mileage": 16.4, "seats": 2},
        {"manufacturer": "Ferrari", "model": "Purosangue", "variant": "6.5L V12 4WD SUV (715 HP)", "body_type": "Supercar", "fuel_type": "Petrol", "ex_showroom_price": 105000000, "safety_rating": "5.0", "airbags": 6, "mileage": 5.8, "seats": 4},
        {"manufacturer": "Lamborghini", "model": "Revuelto", "variant": "6.5L V12 Hybrid AWD (1001 HP)", "body_type": "Supercar", "fuel_type": "Hybrid", "ex_showroom_price": 88900000, "safety_rating": "5.0", "airbags": 6, "mileage": 9.7, "seats": 2},
        {"manufacturer": "Lamborghini", "model": "Urus Performante", "variant": "4.0L V8 Twin-Turbo (666 HP)", "body_type": "Supercar", "fuel_type": "Petrol", "ex_showroom_price": 42200000, "safety_rating": "5.0", "airbags": 8, "mileage": 7.8, "seats": 5},
        {"manufacturer": "McLaren", "model": "750S", "variant": "4.0L V8 Twin-Turbo (750 HP)", "body_type": "Supercar", "fuel_type": "Petrol", "ex_showroom_price": 59100000, "safety_rating": "5.0", "airbags": 6, "mileage": 8.2, "seats": 2},
        {"manufacturer": "Bugatti", "model": "Chiron", "variant": "8.0L Quad-Turbo W16 (1500 HP)", "body_type": "Supercar", "fuel_type": "Petrol", "ex_showroom_price": 250000000, "safety_rating": "5.0", "airbags": 6, "mileage": 4.5, "seats": 2},

        # Vintage & Classic Heritage
        {"manufacturer": "Ferrari", "model": "250 GTO (1962)", "variant": "3.0L Colombo V12 (300 PS)", "body_type": "Vintage / Classic", "fuel_type": "Petrol", "ex_showroom_price": 4000000000, "safety_rating": "Classic", "airbags": 0, "mileage": 5.0, "seats": 2},
        {"manufacturer": "Jaguar", "model": "E-Type Series 1 (1961)", "variant": "3.8L DOHC Inline-6 (265 PS)", "body_type": "Vintage / Classic", "fuel_type": "Petrol", "ex_showroom_price": 25000000, "safety_rating": "Classic", "airbags": 0, "mileage": 7.0, "seats": 2},
        {"manufacturer": "Aston Martin", "model": "DB5 (1963)", "variant": "4.0L DOHC Inline-6 (282 PS)", "body_type": "Vintage / Classic", "fuel_type": "Petrol", "ex_showroom_price": 100000000, "safety_rating": "Classic", "airbags": 0, "mileage": 6.5, "seats": 4},
        {"manufacturer": "Mercedes-Benz", "model": "300 SL Gullwing (1954)", "variant": "3.0L Mechanical Injection I6 (240 PS)", "body_type": "Vintage / Classic", "fuel_type": "Petrol", "ex_showroom_price": 150000000, "safety_rating": "Classic", "airbags": 0, "mileage": 8.0, "seats": 2},
        {"manufacturer": "Mercedes-Benz", "model": "540K Special Roadster (1936)", "variant": "5.4L Supercharged Straight-8 (180 PS)", "body_type": "Vintage / Classic", "fuel_type": "Petrol", "ex_showroom_price": 800000000, "safety_rating": "Classic", "airbags": 0, "mileage": 4.0, "seats": 2},
        {"manufacturer": "Rolls-Royce", "model": "Phantom I (1925)", "variant": "7.7L Pushrod Inline-6 (108 PS)", "body_type": "Vintage / Classic", "fuel_type": "Petrol", "ex_showroom_price": 500000000, "safety_rating": "Classic", "airbags": 0, "mileage": 4.5, "seats": 7},
        {"manufacturer": "Ford", "model": "Model T (1908)", "variant": "2.9L 4-Cylinder (22 HP)", "body_type": "Vintage / Classic", "fuel_type": "Petrol", "ex_showroom_price": 10000000, "safety_rating": "Classic", "airbags": 0, "mileage": 10.0, "seats": 4},

        # Muscle Cars
        {"manufacturer": "Ford", "model": "Mustang Boss 429 (1969)", "variant": "7.0L Semi-Hemi V8 (375 PS)", "body_type": "Muscle", "fuel_type": "Petrol", "ex_showroom_price": 40000000, "safety_rating": "Classic", "airbags": 0, "mileage": 4.5, "seats": 4},
        {"manufacturer": "Ford", "model": "Mustang Dark Horse (2024)", "variant": "5.0L Coyote V8 (500 HP)", "body_type": "Muscle", "fuel_type": "Petrol", "ex_showroom_price": 9500000, "safety_rating": "5.0", "airbags": 8, "mileage": 8.5, "seats": 4},
        {"manufacturer": "Dodge", "model": "Charger R/T 426 Hemi (1970)", "variant": "7.0L Elephant Hemi V8 (425 PS)", "body_type": "Muscle", "fuel_type": "Petrol", "ex_showroom_price": 20000000, "safety_rating": "Classic", "airbags": 0, "mileage": 4.0, "seats": 5},
        {"manufacturer": "Dodge", "model": "Challenger SRT Hellcat Redeye", "variant": "6.2L Supercharged V8 (797 HP)", "body_type": "Muscle", "fuel_type": "Petrol", "ex_showroom_price": 12000000, "safety_rating": "5.0", "airbags": 6, "mileage": 6.8, "seats": 5},
        {"manufacturer": "Chevrolet", "model": "Camaro ZL1 (1969)", "variant": "427 cu in All-Aluminum V8 (430 PS)", "body_type": "Muscle", "fuel_type": "Petrol", "ex_showroom_price": 30000000, "safety_rating": "Classic", "airbags": 0, "mileage": 4.2, "seats": 4}
    ]

    DEFAULT_SOURCE = {
        "id": 1,
        "name": "AutoMind Automotive Knowledge Base",
        "domain": "automind.ai",
        "base_url": "https://automind.ai",
        "reliability_score": 0.99
    }

    cleaned_docs = []
    seen_hashes = set()
    fake_removed_count = 0
    duplicates_removed_count = 0

    # 1. Add Master vehicles catalog
    for idx, car in enumerate(MASTER_CARS, 1):
        doc = {
            "car_variant_id": idx,
            "manufacturer": car["manufacturer"],
            "model": car["model"],
            "variant": car["variant"],
            "body_type": car["body_type"],
            "fuel_type": car["fuel_type"],
            "ex_showroom_price": car["ex_showroom_price"],
            "safety_rating": car.get("safety_rating", "5.0"),
            "airbags": car.get("airbags", 6),
            "source_info": DEFAULT_SOURCE
        }
        if "mileage" in car:
            doc["mileage"] = car["mileage"]
        if "electric_range" in car:
            doc["electric_range"] = car["electric_range"]
        if "seats" in car:
            doc["seats"] = car["seats"]

        h = hashlib.md5(f"{car['manufacturer']}_{car['model']}_{car['variant']}".encode()).hexdigest()
        seen_hashes.add(h)
        cleaned_docs.append(doc)

    # 2. Filter out fake dataset rows from previous runs
    FAKE_DATASET_PREFIXES = ["Carlisle_", "carbon225_", "carolina_", "CarperAI_", "carolmou_", "carsondial", "librarian-bots"]

    for doc in orig_docs:
        m = doc.get("manufacturer", "")
        if any(m.startswith(fp) for fp in FAKE_DATASET_PREFIXES) or m == "Carlisle":
            fake_removed_count += 1
            continue

        # Clean EV QA records
        if m == "darkB_electric_vehicles_qa_dataset" or "electric_vehicles_qa" in str(doc):
            text_sig = doc.get("variant", "") or doc.get("model", "")
            h = hashlib.md5(text_sig.encode()).hexdigest()
            if h in seen_hashes:
                duplicates_removed_count += 1
                continue
            seen_hashes.add(h)
            doc["car_variant_id"] = len(cleaned_docs) + 1
            doc["body_type"] = "EV Knowledge"
            doc["fuel_type"] = "Electric"
            cleaned_docs.append(doc)
            continue

        # Deduplicate standard car records
        car_key = f"{doc.get('manufacturer')}_{doc.get('model')}_{doc.get('variant')}"
        h = hashlib.md5(car_key.encode()).hexdigest()
        if h in seen_hashes:
            duplicates_removed_count += 1
            continue
        seen_hashes.add(h)
        doc["car_variant_id"] = len(cleaned_docs) + 1
        cleaned_docs.append(doc)

    print(f"\n[+] Total Cleaned & Verified Documents: {len(cleaned_docs)}")
    print(f"[-] Fake / Non-Automotive Junk Removed: {fake_removed_count}")
    print(f"[-] Duplicate Records Removed: {duplicates_removed_count}")

    # Save cleaned documents.json
    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_docs, f, indent=2)

    # 3. Generate dense vector embeddings using sentence-transformers
    print("\n[*] Rebuilding Dense Vector Embeddings (all-MiniLM-L6-v2)...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = []
    for d in cleaned_docs:
        t = f"{d.get('manufacturer', '')} {d.get('model', '')} {d.get('variant', '')} {d.get('body_type', '')} {d.get('fuel_type', '')} {d.get('ex_showroom_price', '')}"
        texts.append(t)
    embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    np.save(EMB_FILE, embs)
    print(f"[OK] Saved FAISS embeddings array shape={embs.shape} to {EMB_FILE}")

    # 4. Detailed Data Analysis Breakdown
    print("\n" + "=" * 80)
    print(" 📊 DETAILED DATASET & CAR TYPES BREAKDOWN")
    print("=" * 80)

    # Car Types / Body Types
    body_counter = Counter(d.get("body_type", "Unknown") for d in cleaned_docs if d.get("body_type") != "EV Knowledge")
    print("\n🚗 1. CAR TYPES / BODY STYLES:")
    for b_type, count in body_counter.most_common():
        print(f"   • {b_type}: {count} models")

    # Fuel Types
    fuel_counter = Counter(d.get("fuel_type", "Unknown") for d in cleaned_docs if d.get("body_type") != "EV Knowledge")
    print("\n⛽ 2. FUEL TYPES:")
    for f_type, count in fuel_counter.most_common():
        print(f"   • {f_type}: {count} models")

    # Top Manufacturers
    brand_counter = Counter(d.get("manufacturer", "Unknown") for d in cleaned_docs if d.get("body_type") != "EV Knowledge")
    print(f"\n🏢 3. AUTOMOTIVE BRANDS / MANUFACTURERS ({len(brand_counter)} total brands):")
    for brand, count in brand_counter.most_common():
        print(f"   • {brand}: {count} vehicles")

    # Price Segment Breakdown
    price_segments = {"Budget (< ₹10 Lakh)": 0, "Mid-Range (₹10 – 25 Lakh)": 0, "Premium (₹25 – 60 Lakh)": 0, "Luxury & Supercars (> ₹60 Lakh)": 0}
    for d in cleaned_docs:
        if d.get("body_type") == "EV Knowledge":
            continue
        p = d.get("ex_showroom_price", 0)
        if isinstance(p, (int, float)):
            if p < 1000000:
                price_segments["Budget (< ₹10 Lakh)"] += 1
            elif p <= 2500000:
                price_segments["Mid-Range (₹10 – 25 Lakh)"] += 1
            elif p <= 6000000:
                price_segments["Premium (₹25 – 60 Lakh)"] += 1
            else:
                price_segments["Luxury & Supercars (> ₹60 Lakh)"] += 1

    print("\n💰 4. PRICE SEGMENT DISTRIBUTION:")
    for seg, count in price_segments.items():
        print(f"   • {seg}: {count} vehicles")

if __name__ == "__main__":
    main()
