"""
Insère les utilisateurs de démonstration dans la base python_auth_db.
Ce script est exécuté automatiquement par entrypoint.sh au démarrage du conteneur.
"""
import os
import sys
import time
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

DEMO_USERS = [
    ("admin@telefan.com",  "Admin2024!",  "admin"),
    ("ops@telefan.com",    "Ops2024!",    "manager_ops"),
    ("supply@telefan.com", "Supply2024!", "manager_supply"),
]

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST",     "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", "3306")),
    "user":     os.getenv("MYSQL_USER",     "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": "python_auth_db",
}


def wait_for_mysql(max_retries: int = 30, delay: float = 2.0) -> None:
    """Attend que MySQL soit prêt avant d'insérer les données."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            conn.close()
            print(f"[setup_users] MySQL prêt après {attempt} tentative(s).")
            return
        except Error as e:
            print(f"[setup_users] Tentative {attempt}/{max_retries} — MySQL pas encore prêt : {e}")
            time.sleep(delay)
    print("[setup_users] ERREUR : MySQL inaccessible après tous les essais.", file=sys.stderr)
    sys.exit(1)


def insert_users() -> None:
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for email, password, role in DEMO_USERS:
            # Vérifie si l'utilisateur existe déjà
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                print(f"[setup_users] Utilisateur déjà présent : {email}")
                continue

            hashed = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                (email, hashed, role),
            )
            print(f"[setup_users] Utilisateur créé : {email} ({role})")

        conn.commit()
        cursor.close()
        conn.close()
        print("[setup_users] Initialisation des utilisateurs terminée.")

    except Error as e:
        print(f"[setup_users] ERREUR lors de l'insertion : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    wait_for_mysql()
    insert_users()
