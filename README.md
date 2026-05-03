# 🚨 CrashRespond — Road Accident Emergency Response Tool

A location-based emergency response platform that helps users quickly identify
and contact nearby trauma centres, ambulance services, police stations,
towing services, and other emergency contacts after a road accident.

---

## 📁 Project Structure

```
CrashRespond/
├── app.py                  ← Main Streamlit web application
├── database.py             ← Creates and populates the SQLite database
├── emergency_data.db       ← SQLite database (auto-generated)
├── requirements.txt        ← Python dependencies
└── README.md               ← This file
```

---

## 🗄️ Database Structure (SQLite)

| Table                  | Description                        | Rows |
|------------------------|------------------------------------|------|
| countries              | Emergency numbers per country      | 10   |
| categories             | Service type definitions           | 6    |
| services               | All emergency service providers    | 15   |
| service_tags           | Tags linked to each service        | 45   |
| service_capabilities   | Capabilities of each service       | 48   |

---

## ⚙️ How to Run

### Step 1 — Install dependencies
```bash
pip install streamlit
```

### Step 2 — Create the database (run once)
```bash
python database.py
```

### Step 3 — Launch the app
```bash
streamlit run app.py
```

Then open your browser at: `http://localhost:8501`

---

## ✅ Features

- Nearest hospitals, ambulance services, police stations
- Towing services, puncture shops, petrol pumps
- Global emergency numbers (India, USA, UK, Australia, Germany, UAE, and more)
- Search and filter by service type
- Golden Hour 60-minute countdown timer
- SOS modal with one-tap emergency calling
- SVG map with service markers
- Export data as JSON
- Offline functionality (SQLite — no internet needed)
- Service detail panel with capabilities

---

## 🌍 Countries Supported

India, USA, UK, Australia, Germany, UAE, Canada, France, Japan, Brazil

---

## 🔧 Tech Stack

- Python 3.x
- Streamlit (UI framework)
- SQLite (structured local database — built into Python)
