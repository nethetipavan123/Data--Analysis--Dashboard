"""
database.py — Run this file ONCE to create and populate the SQLite database.
Command: python database.py
"""

import sqlite3
import os

DB_FILE = "emergency_data.db"

def create_database():
    # Delete old DB if exists (fresh start)
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("Old database removed.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ── TABLE 1: countries ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE countries (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            flag      TEXT,
            region    TEXT,
            emergency TEXT,
            ambulance TEXT,
            police    TEXT,
            fire      TEXT
        )
    """)

    countries_data = [
        ("India",     "🇮🇳", "South Asia",     "112", "108", "100", "101"),
        ("USA",       "🇺🇸", "North America",  "911", "911", "911", "911"),
        ("UK",        "🇬🇧", "Europe",         "999", "999", "999", "999"),
        ("Australia", "🇦🇺", "Oceania",        "000", "000", "000", "000"),
        ("Germany",   "🇩🇪", "Europe",         "112", "112", "110", "112"),
        ("UAE",       "🇦🇪", "Middle East",    "999", "998", "999", "997"),
        ("Canada",    "🇨🇦", "North America",  "911", "911", "911", "911"),
        ("France",    "🇫🇷", "Europe",         "112", "15",  "17",  "18" ),
        ("Japan",     "🇯🇵", "East Asia",      "110", "119", "110", "119"),
        ("Brazil",    "🇧🇷", "South America",  "192", "192", "190", "193"),
    ]

    cursor.executemany("""
        INSERT INTO countries (name, flag, region, emergency, ambulance, police, fire)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, countries_data)

    print(f"✅ Countries table created — {len(countries_data)} countries inserted.")

    # ── TABLE 2: categories ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE categories (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            code  TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL,
            icon  TEXT
        )
    """)

    categories_data = [
        ("hospital",  "Hospital",  "🏥"),
        ("ambulance", "Ambulance", "🚑"),
        ("police",    "Police",    "🚔"),
        ("towing",    "Towing",    "🚗"),
        ("puncture",  "Puncture",  "🔧"),
        ("petrol",    "Petrol",    "⛽"),
    ]

    cursor.executemany("""
        INSERT INTO categories (code, label, icon) VALUES (?, ?, ?)
    """, categories_data)

    print(f"✅ Categories table created — {len(categories_data)} categories inserted.")

    # ── TABLE 3: services ─────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE services (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            type      TEXT NOT NULL,
            name      TEXT NOT NULL,
            dist      REAL,
            phone     TEXT,
            eta       TEXT,
            rating    REAL,
            avail     TEXT,
            priority  TEXT,
            map_x     INTEGER,
            map_y     INTEGER
        )
    """)

    services_data = [
        (1,  "hospital",  "City Trauma Care Centre",       0.8, "108",            "4 min",  4.8, "24h", "critical", 330, 200),
        (2,  "ambulance", "GVK EMRI Ambulance",            1.2, "108",            "5 min",  4.9, "24h", "critical", 390, 150),
        (3,  "police",    "Traffic Police Post — NH48",    1.5, "100",            "6 min",  4.5, "24h", "warning",  270, 260),
        (4,  "hospital",  "Apollo Hospitals",              2.1, "1860-500-1066",  "8 min",  4.7, "24h", "warning",  450, 300),
        (5,  "towing",    "Highway Rescue & Towing",       2.4, "1800-123-456",   "10 min", 4.3, "24h", "warning",  200, 180),
        (6,  "ambulance", "Red Cross Ambulance Hub",       3.0, "102",            "12 min", 4.6, "24h", "safe",     500, 200),
        (7,  "puncture",  "National Highway Tyre Shop",    0.6, "9876543210",     "3 min",  4.1, "24h", "safe",     360, 320),
        (8,  "police",    "District Police Station",       3.2, "100",            "13 min", 4.4, "24h", "safe",     170, 350),
        (9,  "petrol",    "HP Petrol Pump — Highway",      1.1, "1800-233-3555",  "4 min",  4.0, "24h", "safe",     480, 360),
        (10, "hospital",  "PHC Community Health Centre",   4.1, "104",            "16 min", 4.2, "day", "safe",     130, 200),
        (11, "hospital",  "St. John's Medical College",    3.5, "080-22065000",   "14 min", 4.6, "24h", "warning",  560, 140),
        (12, "ambulance", "Ziqitza Ambulance Service",     2.8, "1800-419-1911",  "11 min", 4.7, "24h", "safe",     240, 320),
        (13, "towing",    "QuickTow Highway Service",      1.8, "9988776655",     "8 min",  4.2, "24h", "warning",  420, 240),
        (14, "police",    "Highway Patrol Unit",           0.9, "100",            "4 min",  4.6, "24h", "critical", 310, 280),
        (15, "petrol",    "BPCL Fuel Station",             1.4, "1800-224-344",   "6 min",  3.9, "24h", "safe",     530, 310),
    ]

    cursor.executemany("""
        INSERT INTO services (id, type, name, dist, phone, eta, rating, avail, priority, map_x, map_y)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, services_data)

    print(f"✅ Services table created — {len(services_data)} services inserted.")

    # ── TABLE 4: service_tags ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE service_tags (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            tag        TEXT NOT NULL,
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    """)

    tags_data = [
        (1,  "ICU"),       (1,  "Trauma"),       (1,  "Blood Bank"),
        (2,  "ALS"),       (2,  "BLS"),           (2,  "PICU"),
        (3,  "Traffic"),   (3,  "Rescue"),        (3,  "FIR"),
        (4,  "Multi-specialty"), (4, "Helipad"),  (4,  "Blood Bank"),
        (5,  "Heavy Tow"), (5,  "Car Recovery"),  (5,  "Accident Rescue"),
        (6,  "BLS"),       (6,  "Maternity"),     (6,  "Paediatric"),
        (7,  "Puncture"),  (7,  "Tyre Change"),   (7,  "Air"),
        (8,  "FIR"),       (8,  "Legal Aid"),     (8,  "Ambulance Escort"),
        (9,  "Fuel"),      (9,  "First Aid"),     (9,  "Restroom"),
        (10, "Primary Care"), (10, "X-Ray"),      (10, "Minor Surgery"),
        (11, "Neurology"), (11, "ICU"),           (11, "Trauma"),
        (12, "ALS"),       (12, "BLS"),           (12, "Ventilator"),
        (13, "Heavy Tow"), (13, "All Vehicles"),  (13, "Insurance Assist"),
        (14, "Traffic"),   (14, "Rescue"),        (14, "Patrol"),
        (15, "Fuel"),      (15, "Air Pump"),      (15, "Restroom"),
    ]

    cursor.executemany("""
        INSERT INTO service_tags (service_id, tag) VALUES (?, ?)
    """, tags_data)

    print(f"✅ Service tags table created — {len(tags_data)} tags inserted.")

    # ── TABLE 5: service_capabilities ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE service_capabilities (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            capability TEXT NOT NULL,
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    """)

    caps_data = [
        (1,  "Neurosurgery"),         (1,  "Ortho"),           (1,  "Burns"),       (1,  "ICU Beds: 40"),
        (2,  "Advanced Life Support"),(2,  "Ventilator"),      (2,  "Defibrillator"),
        (3,  "Hydraulic Cutter"),     (3,  "First Aid"),       (3,  "FIR Registration"),
        (4,  "Cardiac Cath Lab"),     (4,  "CT Scanner"),      (4,  "MRI"),          (4,  "ICU"),
        (5,  "Hydraulic Tools"),      (5,  "All Vehicle Types"),(5, "Insurance Assist"),
        (6,  "Basic Life Support"),   (6,  "O2 Cylinder"),     (6,  "Stretcher"),
        (7,  "All tyre types"),       (7,  "Emergency fitting"),(7, "Roadside assist"),
        (8,  "24h Control Room"),     (8,  "FIR Filing"),      (8,  "Witness Statement"),
        (9,  "Air pump"),             (9,  "Basic first aid kit"),(9,"Highway patrol contact"),
        (10, "X-Ray"),                (10, "Dressing"),        (10, "Minor Surgery"), (10, "Referral"),
        (11, "Neurology ICU"),        (11, "CT Scanner"),      (11, "Blood Bank"),
        (12, "Advanced Life Support"),(12, "Ventilator"),      (12, "O2 Cylinder"),
        (13, "Hydraulic Tools"),      (13, "All Vehicle Types"),(13,"GPS Tracking"),
        (14, "24h Patrol"),           (14, "First Aid"),       (14, "FIR Registration"),
        (15, "Air pump"),             (15, "First aid kit"),   (15, "Towing contact"),
    ]

    cursor.executemany("""
        INSERT INTO service_capabilities (service_id, capability) VALUES (?, ?)
    """, caps_data)

    print(f"✅ Capabilities table created — {len(caps_data)} capabilities inserted.")

    conn.commit()
    conn.close()

    print("\n" + "="*50)
    print(f"✅ DATABASE READY: {DB_FILE}")
    print("="*50)
    print("Tables created:")
    print("  • countries            (10 rows)")
    print("  • categories           (6 rows)")
    print("  • services             (15 rows)")
    print("  • service_tags         (45 rows)")
    print("  • service_capabilities (45 rows)")
    print("\nNow run: streamlit run app.py")

if __name__ == "__main__":
    create_database()
