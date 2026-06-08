import pandas as pd
import random
from faker import Faker

fake = Faker()

divisions = {
    "Oklahoma City": {"state": "OK", "lat": 35.4676, "lon": -97.5164},
    "Tulsa": {"state": "OK", "lat": 36.1540, "lon": -95.9928},
    "Dallas": {"state": "TX", "lat": 32.7767, "lon": -96.7970},
    "Denver": {"state": "CO", "lat": 39.7392, "lon": -104.9903},
    "Las Vegas": {"state": "NV", "lat": 36.1699, "lon": -115.1398},
    "Austin": {"state": "TX", "lat": 30.2672, "lon": -97.7431},
    "Houston": {"state": "TX", "lat": 29.7604, "lon": -95.3698},
    "Phoenix": {"state": "AZ", "lat": 33.4484, "lon": -112.0740},
    "Washington DC": {"state": "DC", "lat": 38.9072, "lon": -77.0369},
    "Salt Lake City": {"state": "UT", "lat": 40.7608, "lon": -111.8910},
    "San Antonio": {"state": "TX", "lat": 29.4241, "lon": -98.4936},
}

items = ["Wire", "Cables", "Speakers", "Displays", "Screws & Bolts"]
statuses = ["Delivered", "In Transit", "Delayed"]

def generate_freight_number():
    return f"FR-{random.randint(10000, 99999)}"

def generate_ups_tracking():
    return "1Z" + fake.bothify(text="??? ??? ?? ???? ???? ?").replace(" ", "").upper()

def generate_data(num_records=100):
    records = []
    division_names = list(divisions.keys())

    for _ in range(num_records):
        origin = random.choice(division_names)
        destination = random.choice([d for d in division_names if d != origin])
        item = random.choice(items)
        quantity = random.randint(1, 50)
        cost = round(random.uniform(50, 2500), 2)
        ship_date = fake.date_between(start_date="-90d", end_date="today")
        est_delivery = fake.date_between(start_date=ship_date, end_date="+14d")
        status = random.choice(statuses)

        records.append({
            "Freight_Number": generate_freight_number(),
            "Origin": origin,
            "Origin_State": divisions[origin]["state"],
            "Origin_Lat": divisions[origin]["lat"],
            "Origin_Lon": divisions[origin]["lon"],
            "Destination": destination,
            "Destination_State": divisions[destination]["state"],
            "Destination_Lat": divisions[destination]["lat"],
            "Destination_Lon": divisions[destination]["lon"],
            "Item": item,
            "Quantity": quantity,
            "Cost": cost,
            "Ship_Date": ship_date,
            "Est_Delivery": est_delivery,
            "Status": status,
            "UPS_Tracking": generate_ups_tracking(),
        })

    return pd.DataFrame(records)

if __name__ == "__main__":
    df = generate_data(100)
    df.to_csv("shipping_data.csv", index=False)
    print(f"Generated {len(df)} records")
    print(df.head())