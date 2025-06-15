# DONT Delete--- Generated Hashes ---
# manager
# Password: 'manager_password'
# Hash: $2b$12$OO7UV2uWWaNk//zlLon9PO6/IdM4k3pLUggw4MvwjVRrFoyMBLSwy
# salesrep
# Password: 'sales_rep_password'
# Hash: $2b$12$dy7bcgBM9oOVW.5ezzSFweXpOEt3x6qJYZXQKxmLlMFNBZBX.r8Qm

# Copy these hashes into your config.yaml file.


# app.py
import yaml
from datetime import date
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# Import our data management functions and global DataFrames
import data as db

# 1. --- App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = yaml.safe_load(open('config.yaml'))['cookie']['key']
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to /login if user is not authenticated

# 2. --- User Model & Login Management ---
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.details = db.USER_CONFIG.get(username, {})
        self.name = self.details.get('name')
        self.email = self.details.get('email')
        self.password_hash = self.details.get('password')
        self.role = self.details.get('role')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login hook to load a user from the 'database' (our config)."""
    if user_id in db.USER_CONFIG:
        return User(user_id)
    return None

# 3. --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = load_user(username)
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check username and password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'Representative':
        return redirect(url_for('assigned_leads'))
        
    # Get available leads (not yet assigned)
    assigned_ids = db.ASSIGNED_LEADS_DF['lead_id'].tolist()
    available_leads = db.LEADS_DF[~db.LEADS_DF['lead_id'].isin(assigned_ids)]

    # --- Handle Filtering (GET request) ---
    filter_col = request.args.get('filter_col')
    filter_vals = request.args.getlist('filter_val') # getlist for multiselect
    
    if filter_col and filter_vals:
        available_leads = available_leads[available_leads[filter_col].isin(filter_vals)]

    # Get filter options for the sidebar
    filter_options = {
        'columns': [col for col in db.LEADS_DF.columns if db.LEADS_DF[col].dtype == 'object' and db.LEADS_DF[col].nunique() > 1],
        'value_options': db.LEADS_DF[filter_col].unique().tolist() if filter_col else [] # Renamed 'values' to 'value_options'
    }

    # --- Handle Lead Assignment (POST request, Manager only) ---
    if request.method == 'POST' and current_user.role == 'Manager':
        assigned_to_user = request.form.get('assignee')
        selected_lead_ids = request.form.getlist('selected_leads') # Checkboxes with this name

        if not assigned_to_user:
            flash('Please select a representative to assign leads to.', 'warning')
        elif not selected_lead_ids:
            flash('Please select at least one lead to assign.', 'warning')
        else:
            # Process assignment
            selected_ids_int = [int(id) for id in selected_lead_ids]
            leads_to_move = db.LEADS_DF[db.LEADS_DF['lead_id'].isin(selected_ids_int)].copy()
            leads_to_move['selection_date'] = date.today().isoformat()
            leads_to_move['assigned_to'] = assigned_to_user
            
            # Append to our "assigned" table and handle potential duplicates
            db.ASSIGNED_LEADS_DF = pd.concat([db.ASSIGNED_LEADS_DF, leads_to_move]).drop_duplicates(subset=['lead_id'], keep='last')
            
            flash(f'{len(leads_to_move)} leads assigned to {assigned_to_user}.', 'success')
            return redirect(url_for('dashboard')) # Redirect to clear the form

    return render_template('dashboard.html', 
                           leads=available_leads.to_dict('records'), 
                           representatives=db.get_representatives(),
                           filter_options=filter_options,
                           current_filters={'col': filter_col, 'vals': filter_vals})


@app.route('/assigned-leads')
@login_required
def assigned_leads():
    assigned_df = db.ASSIGNED_LEADS_DF.copy()

    # Add assignee's full name for display
    user_names = {u['username']: u['name'] for u in db.get_all_users()}
    assigned_df['assigned_to_name'] = assigned_df['assigned_to'].map(user_names)

    if current_user.role == 'Representative':
        leads_to_show = assigned_df[assigned_df['assigned_to'] == current_user.id]
    else: # Manager view
        leads_to_show = assigned_df

    return render_template('assigned_leads.html', leads=leads_to_show.to_dict('records'))

@app.route('/clear-assigned', methods=['POST'])
@login_required
def clear_assigned():
    if current_user.role == 'Manager':
        # Re-initialize the assigned leads DataFrame
        assigned_cols = list(db.LEADS_DF.columns) + ['selection_date', 'assigned_to']
        db.ASSIGNED_LEADS_DF = pd.DataFrame(columns=assigned_cols)
        flash('All assigned leads have been cleared.', 'success')
    else:
        flash('You do not have permission to perform this action.', 'danger')
    return redirect(url_for('assigned_leads'))

@app.route('/lead/<int:lead_id>')
@login_required
def get_lead_details(lead_id):
    """API endpoint to get details for a single lead."""
    
    # Check both assigned and available leads
    lead_details = None
    if not db.ASSIGNED_LEADS_DF.empty and lead_id in db.ASSIGNED_LEADS_DF['lead_id'].values:
        lead_details = db.ASSIGNED_LEADS_DF.loc[db.ASSIGNED_LEADS_DF['lead_id'] == lead_id]
    elif not db.LEADS_DF.empty and lead_id in db.LEADS_DF['lead_id'].values:
        lead_details = db.LEADS_DF.loc[db.LEADS_DF['lead_id'] == lead_id]

    if lead_details is not None and not lead_details.empty:
        return jsonify(lead_details.to_dict('records')[0])
    else:
        return jsonify({'error': 'Lead not found'}), 404

@app.route('/lead/<int:lead_id>/update', methods=['POST'])
@login_required
def update_lead_details(lead_id):
    """API endpoint to update a lead's notes and status."""
    data = request.get_json()
    
    # We only expect reps to update leads assigned to them
    if not db.ASSIGNED_LEADS_DF.empty and lead_id in db.ASSIGNED_LEADS_DF['lead_id'].values:
        lead_index = db.ASSIGNED_LEADS_DF[db.ASSIGNED_LEADS_DF['lead_id'] == lead_id].index[0]

        # Update the DataFrame
        db.ASSIGNED_LEADS_DF.loc[lead_index, 'notes'] = data.get('notes', '')
        db.ASSIGNED_LEADS_DF.loc[lead_index, 'status'] = data.get('status', 'New')
        
        # In a real app, you would save this change to a persistent database
        
        return jsonify({'success': True, 'message': 'Lead updated successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Assigned lead not found.'}), 404

@app.route('/member-map')
@login_required
def member_map():
    if current_user.role != 'Manager':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))

    # For now, let's assume "acquired members" are those in ASSIGNED_LEADS_DF
    # with a specific status, e.g., 'Acquired'.
    # If the status isn't being updated yet, this will show all assigned leads.
    # We need 'name', 'latitude', 'longitude', and potentially 'notes' or 'branche' as details.
    
    acquired_members_df = db.ASSIGNED_LEADS_DF[db.ASSIGNED_LEADS_DF['status'] == 'Acquired']
    
    if acquired_members_df.empty:
        # If no 'Acquired' leads, pass all assigned leads for now, or an empty list
        # For demonstration, let's pass all assigned leads if no 'Acquired' ones are found.
        # In a real scenario, you might want to strictly show only 'Acquired' or message if none.
        # For this task, we will show all assigned leads if no 'Acquired' leads are found.
        # This ensures the map has data to display if the 'Acquired' status is not yet in use.
        # A better approach for production would be to ensure 'Acquired' status is correctly set.
        if db.ASSIGNED_LEADS_DF.empty:
            members_data = []
        else:
            # Select relevant columns for the map
            members_data = db.ASSIGNED_LEADS_DF[['name', 'latitude', 'longitude', 'branche', 'notes']].copy()
            members_data.rename(columns={'branche': 'details_branche', 'notes': 'details_notes'}, inplace=True) # Avoid conflict if 'details' is a direct column
            # Combine branche and notes into a 'details' field for the popup
            members_data['details'] = members_data.apply(lambda row: f"Branche: {row['details_branche']}<br>Notes: {row['details_notes']}", axis=1)
            members_data = members_data[['name', 'latitude', 'longitude', 'details']].to_dict('records')


    else:
        # Select relevant columns for the map
        members_data = acquired_members_df[['name', 'latitude', 'longitude', 'branche', 'notes']].copy()
        members_data.rename(columns={'branche': 'details_branche', 'notes': 'details_notes'}, inplace=True)
        members_data['details'] = members_data.apply(lambda row: f"Branche: {row['details_branche']}<br>Notes: {row['details_notes']}", axis=1)
        members_data = members_data[['name', 'latitude', 'longitude', 'details']].to_dict('records')
        
    return render_template('map.html', members_data=members_data)

if __name__ == '__main__':
    app.run(debug=True)
