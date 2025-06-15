# Lead Management System

A simple web-based application for managing and assigning sales leads.

## Overview

This project is a Flask-based Lead Management System. It allows:
*   User authentication (Manager and Sales Representative roles).
*   Managers to view available leads.
*   Managers to assign leads to Sales Representatives.
*   Sales Representatives to view their assigned leads.
*   Filtering of leads.

The application currently uses in-memory Pandas DataFrames for data storage as a mock database.

For detailed technical documentation, please see [documentation.md](documentation.md).

## Features

*   **User Roles**: Manager and Representative roles with different permissions.
*   **Lead Dashboard**: View unassigned leads with filtering capabilities.
*   **Lead Assignment**: Managers can assign leads to representatives.
*   **Assigned Leads View**: Representatives see their leads; Managers see all assigned leads.
*   **Password Management**: Includes a script to generate hashed passwords.

## Setup and Installation

1.  **Prerequisites**:
    *   Python 3.7+
    *   pip (Python package installer)

2.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` file includes:
    *   Flask
    *   Flask-Login
    *   Flask-Bcrypt
    *   PyYAML
    *   Pandas

5.  **Configure User Credentials:**
    *   The application uses a `config.yaml` file for user credentials and other settings. A sample structure is provided in the repository.
    *   To add or change users, you'll need to generate bcrypt password hashes.
    *   Run the `generate_hashes.py` script:
        ```bash
        python generate_hashes.py
        ```
    *   This script will output password hashes for predefined passwords (e.g., 'manager_password', 'sales_rep_password').
    *   Copy these generated hashes into your `config.yaml` file under the `credentials.usernames.<username>.password` section for the respective users.
    *   **Example `config.yaml` structure:**
        ```yaml
        cookie:
          key: 'a_very_secret_key_please_change_me'
          # ... other cookie settings

        credentials:
          usernames:
            manager:
              email: 'manager@example.com'
              name: 'Manager User'
              password: '$2b$12$....your_generated_hash_here....' # Replace with generated hash
              role: 'Manager'
            salesrep:
              email: 'salesrep@example.com'
              name: 'Sales Representative'
              password: '$2b$12$....your_generated_hash_here....' # Replace with generated hash
              role: 'Representative'
        # ...
        ```
    *   **Important**: Change the `cookie.key` in `config.yaml` to a unique, strong secret key.

6.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

## Usage

1.  Navigate to the application URL in your web browser.
2.  Log in using the credentials defined in `config.yaml`.
    *   Default usernames (if using provided hashes): `manager`, `salesrep`
    *   Passwords (plain text, before hashing): `manager_password`, `sales_rep_password`
3.  **Managers**:
    *   Can see unassigned leads on the dashboard.
    *   Can filter leads.
    *   Can select leads and assign them to a sales representative.
    *   Can view all assigned leads under "Assigned Leads".
    *   Can clear all assigned leads (for demo purposes).
4.  **Sales Representatives**:
    *   Will be directed to the dashboard (may show no unassigned leads if filters are restrictive or all leads are assigned).
    *   Can view leads specifically assigned to them under "Assigned Leads".

## Project Structure

*   `app.py`: Main Flask application, routes, and logic.
*   `data.py`: Handles data (currently mock data using Pandas).
*   `generate_hashes.py`: Utility to create password hashes for `config.yaml`.
*   `config.yaml`: Configuration file for credentials, secret keys, etc.
*   `requirements.txt`: Python dependencies.
*   `templates/`: HTML templates.
*   `static/`: CSS and other static files.
*   `documentation.md`: Detailed technical documentation.
*   `brainstorming.md`: Ideas for future enhancements.

## Future Development

Refer to `brainstorming.md` and `documentation.md` for potential future enhancements, such as database integration, advanced lead historization, and PLZ-based segmentation.
