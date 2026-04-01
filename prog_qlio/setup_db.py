import mysql.connector

def setup_database():
    try:
        # 1. Connexion au serveur MySQL 
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            port=3307
        )
        cursor = conn.cursor()

        # 2. Création de la Base de Données 'python_auth_db'
        cursor.execute("DROP DATABASE IF EXISTS python_auth_db") 
        cursor.execute("CREATE DATABASE python_auth_db")
        cursor.execute("USE python_auth_db")
        print("✅ Base de données 'python_auth_db' créée.")

        
        # 3. CRÉATION DES TABLES MÉTIERS 

        # Table pour la Disponibilité et Fiabilité (MTBF/MTTR)
        # Source 45: Champs clés : ResourceID, TimeStamp, Busy, ErrorL0, ErrorL1, ErrorL2, Reset
        cursor.execute("""
        CREATE TABLE tblmachinereport (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ResourceID VARCHAR(50),
            TimeStamp DATETIME,
            Busy BOOLEAN,
            ErrorL0 BOOLEAN,
            ErrorL1 BOOLEAN,
            ErrorL2 BOOLEAN,
            Reset BOOLEAN
        )""")

        # Table pour la Performance, Qualité et Cycle
        # Source 45: Champs clés : Start, End, OpNo, ResourceID, ErrorStep, ErrorRetVal
        cursor.execute("""
        CREATE TABLE tblfinstep (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ResourceID VARCHAR(50),
            OpNo VARCHAR(50),
            Start DATETIME,
            End DATETIME,
            ErrorStep INT,
            ErrorRetVal INT
        )""")

        # Table pour OTD et Lead Time
        # Source 45: Champs clés : Start, End, PlannedEnd
        cursor.execute("""
        CREATE TABLE tblfinorder (
            id INT AUTO_INCREMENT PRIMARY KEY,
            OrderID VARCHAR(50),
            Start DATETIME,
            End DATETIME,
            PlannedEnd DATETIME
        )""")

        print("✅ Tables métiers (FESTO) créées selon le cahier des charges.")

       
        # 4. CRÉATION DE LA TABLE UTILISATEURS
       
        
        cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL
        )""")

       
        # 5. CRÉATION DES COMPTES (Selon Cahier des Charges - Source 115-118)
        

        users_data = [
            # 1. ADMIN : Accès aux 3 tableaux (Ops, Qualité, Logistique) 
            ("admin@telefan.com", "admin123", "admin"),

            # 2. MANAGER OPÉRATIONNEL : Accès Ops / Qualité 
            ("ops@telefan.com", "ops123", "manager_ops"),

            # 3. MANAGER SUPPLY CHAIN : Accès Logistique / Qualité 
            ("supply@telefan.com", "supply123", "manager_supply")
        ]

        sql_insert = "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"
        cursor.executemany(sql_insert, users_data)
        conn.commit()

        print(f"✅ {cursor.rowcount} Utilisateurs créés (Admin, Ops, Supply).")

        cursor.close()
        conn.close()
        print("\n🚀 Installation terminée ! Tu peux lancer login.py")

    except mysql.connector.Error as err:
        print(f"❌ Erreur : {err}")

if __name__ == "__main__":
    setup_database()