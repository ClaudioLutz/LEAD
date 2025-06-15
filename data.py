# data.py
import pandas as pd
import yaml

# --- Load User Config ---
with open('config.yaml') as file:
    config = yaml.safe_load(file)
    USER_CONFIG = config['credentials']['usernames']

# --- Mock Database ---
# This is our in-memory data store. In a real app, this would be a database.
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
    
    # 1. Load Main Leads (Hardcoded placeholder)
    leads_data = [
        {'lead_id': i, 'name': f'Lead Company {i}', 'branche': 'Tech' if i % 2 == 0 else 'Finance', 'size_kategorie': '1-10' if i < 5 else '11-50', 'number': f'555-010{i}', 'email': f'contact@lead{i}.com', 'ort': 'Zurich'}
        for i in range(10)
    ]
    LEADS_DF = pd.DataFrame(leads_data)

    # 2. Initialize an empty DataFrame for assigned leads
    # It must have the same columns as LEADS_DF plus the assignment columns
    assigned_cols = list(LEADS_DF.columns) + ['selection_date', 'assigned_to']
    ASSIGNED_LEADS_DF = pd.DataFrame(columns=assigned_cols)

# Run initialization on import
initialize_data()
