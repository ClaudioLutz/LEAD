# data.py

import pandas as pd
import yaml

# --- Load User Config ---
with open('config.yaml') as file:
    config = yaml.safe_load(file)
    USER_CONFIG = config['credentials']['usernames']

# --- Mock Database ---
LEADS_DF = None
ASSIGNED_LEADS_DF = None

def get_all_users():
    """Returns a list of all user objects from the config."""
    return [
        {'username': u, 'name': d['name'], 'role': d['role']} 
        for u, d in USER_CONFIG.items()
    ]

def get_representatives():
    """Returns a list of users with the 'Representative' role."""
    return [u for u in get_all_users() if u['role'] == 'Representative']

def initialize_data():
    """Loads the initial lead data and initializes the assigned leads DataFrame."""
    global LEADS_DF, ASSIGNED_LEADS_DF
    
    # 1. Load Main Leads with new 'notes', 'status', 'latitude', and 'longitude' fields
    # Sample coordinates for Swiss cities
    locations = {
        "Zurich": (47.3769, 8.5417),
        "Geneva": (46.2044, 6.1432),
        "Bern": (46.9480, 7.4474),
        "Lausanne": (46.5197, 6.6323),
        "Lucerne": (47.0502, 8.3093)
    }
    city_names = list(locations.keys())

    leads_data = []
    for i in range(10):
        city_name = city_names[i % len(city_names)] # Cycle through cities
        lat, lon = locations[city_name]
        leads_data.append({
            'lead_id': i, 
            'name': f'Lead Company {i}', 
            'branche': 'Tech' if i % 2 == 0 else 'Finance', 
            'size_kategorie': '1-10' if i < 5 else '11-50', 
            'number': f'555-010{i}', 
            'email': f'contact@lead{i}.com', 
            'ort': city_name,
            'latitude': lat + (i * 0.001 - 0.005), # Add slight variation for distinct points
            'longitude': lon + (i * 0.001 - 0.005), # Add slight variation for distinct points
            'notes': '', 
            'status': 'New' # Initial status
        })
    LEADS_DF = pd.DataFrame(leads_data)

    # 2. Initialize an empty DataFrame for assigned leads, ensuring all columns from LEADS_DF are included
    # plus 'selection_date' and 'assigned_to'
    assigned_cols = list(LEADS_DF.columns) + ['selection_date', 'assigned_to']
    ASSIGNED_LEADS_DF = pd.DataFrame(columns=assigned_cols)
    # Ensure correct dtypes for empty DataFrame to avoid issues later, especially for numeric/object
    for col in LEADS_DF.columns:
        ASSIGNED_LEADS_DF[col] = ASSIGNED_LEADS_DF[col].astype(LEADS_DF[col].dtype)
    ASSIGNED_LEADS_DF['selection_date'] = pd.to_datetime(ASSIGNED_LEADS_DF['selection_date'])
    ASSIGNED_LEADS_DF['assigned_to'] = ASSIGNED_LEADS_DF['assigned_to'].astype(object)

# Run initialization on import
initialize_data()
