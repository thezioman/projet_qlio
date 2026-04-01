import os
import subprocess
import mysql.connector
import tkinter as tk
from tkinter import filedialog
import shutil
from datetime import datetime

def init_db():
    print("Initialisation de la base mcd...")
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="")
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS mcd;")
        cursor.execute("USE mcd;")
        
        chemin_schema = os.path.join(os.path.dirname(__file__), 'schema_mcd_v2.sql')
        with open(chemin_schema, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        for req in sql.split(';'):
            if req.strip():
                try:
                    cursor.execute(req.strip())
                except:
                    pass
                    
        conn.commit()
        cursor.close()
        conn.close()
        print("Base mcd prête.")
    except Exception as e:
        print("Erreur bd:", e)

if __name__ == "__main__":
    print("Démarrage du traitement SQL...")

    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True)
    
    fichier_sql = filedialog.askopenfilename(
        title="Choisir le fichier SQL Festo",
        filetypes=[("Fichiers SQL", "*.sql"), ("Tous", "*.*")]
    )
    
    if not fichier_sql:
        print("Annulé.")
        exit()
        
    print("Fichier choisi:", fichier_sql)
    
    # Historisation
    dossier_historique = os.path.join(os.path.dirname(__file__), "bases_importees")
    os.makedirs(dossier_historique, exist_ok=True)
    
    nom_fichier = os.path.basename(fichier_sql)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin_copie = os.path.join(dossier_historique, f"import_{date_str}_{nom_fichier}")
    
    shutil.copy2(fichier_sql, chemin_copie)
    print("Sauvegarde créée:", chemin_copie)

    # Lancement
    init_db()

    print("Lancement de l'ingestion...")
    chemin_courant = os.path.dirname(__file__)
    subprocess.run(["python", os.path.join(chemin_courant, "pipeline_01_ingestion.py"), chemin_copie], check=True)

    print("Calcul des KPIs...")
    subprocess.run(["python", os.path.join(chemin_courant, "pipeline_02_eclatement_kpis.py")], check=True)

    print("Terminé !")
