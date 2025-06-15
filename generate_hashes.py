# generate_hashes.py
from flask_bcrypt import Bcrypt

# Create a dummy Flask app context to use Bcrypt
from flask import Flask
app = Flask(__name__)
bcrypt = Bcrypt(app)

def generate_passwords():
    """Generates bcrypt hashes for a list of passwords."""
    passwords_to_hash = ['manager_password', 'sales_rep_password']  # Replace with actual passwords
    hashed_passwords = [bcrypt.generate_password_hash(pw).decode('utf-8') for pw in passwords_to_hash]
    
    print("--- Generated Hashes ---")
    for i, hashed_pw in enumerate(hashed_passwords):
        print(f"Password: '{passwords_to_hash[i]}'")
        print(f"Hash: {hashed_pw}\n")
    print("Copy these hashes into your config.yaml file.")

if __name__ == '__main__':
    generate_passwords()
