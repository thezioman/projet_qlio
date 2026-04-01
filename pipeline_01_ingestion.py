import mysql.connector
import os
import sys

def _get_conn_config():
    return {
        "host":     os.getenv("MYSQL_HOST", "localhost"),
        "port":     int(os.getenv("MYSQL_PORT", "3307")),
        "user":     os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "root"),
    }

def run_sql_file(chemin_fichier, curseur):
    print("Lecture de", chemin_fichier)
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Nettoyage de base pour eviter de tout casser
    contenu = contenu.replace("DROP TABLE", "-- DROP TABLE")
    contenu = contenu.replace("DROP DATABASE", "-- DROP DATABASE")
    contenu = contenu.replace("CREATE DATABASE", "-- CREATE DATABASE")
    contenu = contenu.replace("USE ", "-- USE ")
    contenu = contenu.replace("INSERT INTO", "INSERT IGNORE INTO")

    # On se met dans la base temporaire
    curseur.execute("USE zone_upload_temp;")

    # Decoupage par point-virgule et saut de ligne
    for req in [r.strip() for r in contenu.split(';\n')]:
        if req:
            try:
                curseur.execute(req)
            except:
                pass

def importer_donnees(chemin_upload):
    print("Début de l'ingestion...")

    conn = mysql.connector.connect(**_get_conn_config())
    cur = conn.cursor()

    # Creation du sas
    cur.execute("CREATE DATABASE IF NOT EXISTS zone_upload_temp;")
    cur.execute("USE zone_upload_temp;")

    if os.path.exists(chemin_upload):
        run_sql_file(chemin_upload, cur)
    else:
        print("Fichier introuvable.")
        return

    print("Transfert vers mcd...")

    # Vider les tables mcd pour permettre le remplacement des donnees
    tables_mcd = [
        "CONTENU_STOCK", "Production_operations", "Surveillance_machine",
        "Buffer", "Commande", "Erreur", "Operation", "Piece", "Ressource",
    ]
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for t in tables_mcd:
        try:
            cur.execute(f"TRUNCATE TABLE mcd.{t};")
        except:
            pass
    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
    print("Tables mcd videes, reimport en cours...")

    # Requetes de transfert
    reqs_transfert = [
        "INSERT IGNORE INTO mcd.Ressource SELECT DISTINCT ResourceID, ResourceName FROM zone_upload_temp.tblresource;",
        "INSERT IGNORE INTO mcd.Piece SELECT DISTINCT PNo, Description FROM zone_upload_temp.tblparts;",
        "INSERT IGNORE INTO mcd.Operation SELECT DISTINCT OpNo, Description FROM zone_upload_temp.tbloperation;",
        "INSERT IGNORE INTO mcd.Erreur SELECT DISTINCT ErrorId, Description FROM zone_upload_temp.tblerrorcodes;",
        "INSERT IGNORE INTO mcd.Commande SELECT DISTINCT ONo, Start, End, PlannedEnd FROM zone_upload_temp.tblfinorder;",
        "INSERT IGNORE INTO mcd.Buffer SELECT ResourceID, BufNo, (Sides * `Rows` * `Columns`) FROM zone_upload_temp.tblbuffer;",
        """
        INSERT IGNORE INTO mcd.Surveillance_machine (ID_RESSOURCE, ETAT_MACHINE_HORODATAGE, ETAT_MACHINE_EN_MARCHE, ETAT_MACHINE_EN_ARRET, ETAT_MACHINE_RESET)
        SELECT ResourceID, TimeStamp,
               CASE WHEN Busy=1 AND ErrorL0=0 AND ErrorL1=0 AND ErrorL2=0 THEN 1 ELSE 0 END,
               CASE WHEN ErrorL0 > 0 OR ErrorL1 > 0 OR ErrorL2 > 0 THEN 1 ELSE 0 END,
               Reset
        FROM zone_upload_temp.tblmachinereport;
        """,
        """
        INSERT IGNORE INTO mcd.Production_operations (
            ID_COMMANDE, ID_PIECE, ID_RESSOURCE, ID_OPERATION, ETAPE_DEBUT, ETAPE_FIN, 
            ETAPE_EST_CONFORME, STOCK_CAPACITE_TOTALE, STOCK_POSITIONS_OCCUPEES, STOCK_QUANTITE_STOCK, ID_ERREUR
        )
        SELECT
            s.ONo, p.PNo, s.ResourceID, s.OpNo, s.Start, s.End, 
            CASE WHEN s.ErrorStep = 0 AND s.ErrorRetVal = 0 THEN 1 ELSE 0 END, 
            IFNULL(b.CapaciteTotale, 0), IFNULL(bp.PositionsOccupees, 0), IFNULL(bp.QuantiteStock, 0), s.ErrorRetVal
        FROM zone_upload_temp.tblfinstep s
        JOIN zone_upload_temp.tblfinorderpos p ON s.ONo = p.ONo AND s.OPos = p.OPos
        LEFT JOIN (
            SELECT ResourceID, SUM(Sides * `Rows` * `Columns`) as CapaciteTotale
            FROM zone_upload_temp.tblbuffer GROUP BY ResourceID
        ) b ON s.ResourceID = b.ResourceID
        LEFT JOIN (
            SELECT ResourceId, COUNT(BufPos) as PositionsOccupees, SUM(Quantity) as QuantiteStock
            FROM zone_upload_temp.tblbufferpos GROUP BY ResourceId
        ) bp ON s.ResourceID = bp.ResourceId;
        """,
        "INSERT IGNORE INTO mcd.CONTENU_STOCK (ID_RESSOURCE, ID_BUFFER, ID_PIECE, QUANTITE, NUM_EMPLACEMENT) SELECT ResourceId, BufNo, PNo, Quantity, BufPos FROM zone_upload_temp.tblbufferpos;"
    ]

    for req in reqs_transfert:
        try:
            cur.execute(req)
        except:
            pass

    conn.commit()

    # Nettoyage
    cur.execute("DROP DATABASE IF EXISTS zone_upload_temp;")
    cur.close()
    conn.close()
    print("Ingestion terminée.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fichier = sys.argv[1]
    else:
        fichier = os.path.join(os.path.dirname(__file__), "chemin_vers_nouveau_fichier_upload.sql")
        
    importer_donnees(fichier)
