# Project Documentation

## 1. Overview

This project is a web-based Lead Management System designed to help sales teams manage and assign leads effectively. It allows managers to import leads, assign them to sales representatives, and track their status. Sales representatives can view their assigned leads and work on them.

The application is built using Python with the Flask framework for the web interface and Pandas for data manipulation. User authentication is handled using Flask-Login and password hashing with Flask-Bcrypt.

## 2. Architecture

The system follows a typical Flask web application structure:

*   **`app.py`**: The main application file containing Flask routes, view functions, and business logic.
*   **`data.py`**: Handles data loading and management. Currently, it uses in-memory Pandas DataFrames as a mock database.
*   **`config.yaml`**: Stores application configuration, including user credentials and secret keys.
*   **`templates/`**: Contains HTML templates for rendering web pages.
*   **`static/`**: Stores static assets like CSS and JavaScript files.
*   **`generate_hashes.py`**: A utility script to generate hashed passwords for user credentials.

## 3. Modules and Components

### 3.1. `app.py` - Main Application

*   **Initialization**: Sets up the Flask app, Flask-Login, and Flask-Bcrypt.
*   **User Model (`User(UserMixin)`)**: Defines the user object used by Flask-Login, including methods for password checking.
*   **Login Management (`@login_manager.user_loader`)**: Loads a user object based on their ID.
*   **Routes**:
    *   `/login` (GET, POST): Handles user login. Authenticated users are redirected to the dashboard.
    *   `/logout` (GET): Logs out the current user.
    *   `/` or `/dashboard` (GET, POST):
        *   Displays available (unassigned) leads.
        *   Allows filtering of available leads based on lead attributes.
        *   Allows managers to assign selected leads to sales representatives (POST request).
    *   `/assigned-leads` (GET):
        *   Displays leads assigned to the currently logged-in representative.
        *   Managers can view all assigned leads.
    *   `/clear-assigned` (POST):
        *   Allows managers to clear all currently assigned leads (for demonstration/reset purposes).
*   **Authentication**: Uses Flask-Login for session management and `@login_required` decorator to protect routes. Passwords are checked using bcrypt.

### 3.2. `data.py` - Data Management

*   **`USER_CONFIG`**: Loads user credentials from `config.yaml`.
*   **`LEADS_DF`**: A Pandas DataFrame holding all lead information (mock data).
*   **`ASSIGNED_LEADS_DF`**: A Pandas DataFrame tracking leads that have been assigned to representatives.
*   **`get_all_users()`**: Returns a list of all user details.
*   **`get_representatives()`**: Returns a list of users with the 'Representative' role.
*   **`initialize_data()`**: Loads initial lead data into `LEADS_DF` and sets up an empty `ASSIGNED_LEADS_DF` with the correct columns. This function is called when the module is imported.

### 3.3. `generate_hashes.py` - Password Hashing Utility

*   This is a command-line script.
*   It takes a list of plain-text passwords and generates bcrypt hashes for them.
*   The generated hashes are intended to be manually copied into the `config.yaml` file for the respective user accounts.
*   This script is run separately and is not part of the main web application flow.

### 3.4. `config.yaml` - Configuration File

*   Stores application-level configurations.
*   **`cookie`**:
    *   `key`: Secret key for session management (CSRF protection, etc.). **Important: This should be changed to a unique, random string in a production environment.**
    *   `name`: Name of the session cookie.
    *   `expiry_days`: Session cookie lifetime.
*   **`credentials`**:
    *   `usernames`: A dictionary where each key is a username.
        *   `email`: User's email address.
        *   `name`: User's full name.
        *   `password`: The bcrypt-hashed password for the user.
        *   `role`: User's role (e.g., 'Manager', 'Representative'). This controls access to certain features.
*   **`preauthorized`**:
    *   `emails`: A list of email addresses that might be used for other authorization purposes (currently not heavily used in the provided code but could be for future features like self-registration with whitelisting).

### 3.5. HTML Templates (`templates/`)

*   **`base.html`**: Base template providing the overall page structure (e.g., navigation bar, common CSS includes). Other templates extend this.
*   **`login.html`**: Login page form.
*   **`dashboard.html`**: Main dashboard view. Displays available leads, filtering options, and lead assignment controls for managers.
*   **`assigned_leads.html`**: Displays leads that have been assigned. Content varies based on user role (Manager sees all, Representative sees their own).

### 3.6. Static Files (`static/`)

*   **`static/css/style.css`**: Contains custom CSS styles for the application.

## 4. Data Flow

1.  **Initialization**: When `app.py` starts, `data.py` is imported, which initializes `LEADS_DF` with sample data and `ASSIGNED_LEADS_DF` as an empty DataFrame. User configurations are loaded from `config.yaml`.
2.  **Login**: A user enters credentials on the `/login` page. `app.py` verifies these against the hashed passwords in `USER_CONFIG`.
3.  **Dashboard View**:
    *   Available leads are fetched by taking `LEADS_DF` and filtering out any lead IDs present in `ASSIGNED_LEADS_DF`.
    *   Users can apply filters, which dynamically subset the `available_leads` DataFrame.
4.  **Lead Assignment (Manager)**:
    *   A manager selects leads from the dashboard and an assignee.
    *   The selected leads are copied from `LEADS_DF`, augmented with `selection_date` and `assigned_to` information.
    *   These augmented lead records are appended to the `ASSIGNED_LEADS_DF`.
    *   Duplicates (based on `lead_id`) are dropped to ensure a lead is only assigned once (or its latest assignment is kept).
5.  **Assigned Leads View**:
    *   The `ASSIGNED_LEADS_DF` is displayed.
    *   If the user is a 'Representative', the view is filtered to show only leads assigned to them.
    *   If the user is a 'Manager', all assigned leads are shown.

## 5. Future Scope (from `brainstorming.md`)

The `brainstorming.md` file outlines several potential enhancements for this system, including but not limited to:

*   **Lead Historization & Deduplication**: Tracking lead assignment history and preventing re-contact.
*   **PLZ-Based Lead Segmentation**: Separating lead access for different offices based on postal codes.
*   **Lead Selection Optimization**: Implementing lead scoring and prioritization.
*   **Role-Specific Features**: Expanding functionalities for Manager and Representative roles.
*   **Data Handling and System Architecture**: Migrating from in-memory data to a robust database like SQL Server.

This documentation provides a snapshot of the current system. For planned features and future development ideas, please refer to `brainstorming.md`.
