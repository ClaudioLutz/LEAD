# --- Generated Hashes ---
# Password: 'manager_password'
# Hash: $2b$12$OO7UV2uWWaNk//zlLon9PO6/IdM4k3pLUggw4MvwjVRrFoyMBLSwy

# Password: 'sales_rep_password'
# Hash: $2b$12$dy7bcgBM9oOVW.5ezzSFweXpOEt3x6qJYZXQKxmLlMFNBZBX.r8Qm

# Copy these hashes into your config.yaml file.


# app.py
import yaml
from datetime import date
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
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


if __name__ == '__main__':
    app.run(debug=True)
