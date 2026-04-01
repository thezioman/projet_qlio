import mysql.connector
import os

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3307")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
    )

def init_kpi_db(nom_db, req_table):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {nom_db};")
    cur.execute(f"CREATE DATABASE {nom_db};")
    cur.execute(f"USE {nom_db};")
    cur.execute(req_table)
    return conn, cur

def exec_insert(cur, req, params):
    # Transformation en chaine pour regler les soucis de Decimal avec mysql-connector
    params_propres = []
    for p in params:
        params_propres.append(str(p) if p is not None else None)
    cur.execute(req, tuple(params_propres))

def kpi_dispo():
    print("Calcul Dispo...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(ETAT_MACHINE_HORODATAGE), ID_RESSOURCE, COUNT(ID_SURVEILLANCE_MACHINE), SUM(CASE WHEN ETAT_MACHINE_EN_MARCHE = 1 THEN 1 ELSE 0 END)
        FROM Surveillance_machine WHERE ETAT_MACHINE_HORODATAGE IS NOT NULL GROUP BY DATE(ETAT_MACHINE_HORODATAGE), ID_RESSOURCE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Disponibilite_Journaliere (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, Total_Releves INT, Releves_En_Marche INT, Disponibilite_Pourcent FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_disponibilite", req_table)

    for l in lignes:
        total = int(l[2]) if l[2] else 0
        en_marche = int(l[3]) if l[3] else 0
        dispo = (float(en_marche) / float(total) * 100.0) if total > 0 else 0.0
        exec_insert(cur_kpi, "INSERT INTO Disponibilite_Journaliere VALUES (NULL, %s, %s, %s, %s, %s)", (l[0], l[1], total, en_marche, dispo))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_perf():
    print("Calcul Perf...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(ETAPE_DEBUT), ID_RESSOURCE, COUNT(ID_PRODUCTION_OPERATIONS), SUM(TIMESTAMPDIFF(SECOND, ETAPE_DEBUT, ETAPE_FIN))
        FROM Production_operations WHERE ETAPE_DEBUT IS NOT NULL AND ETAPE_FIN IS NOT NULL GROUP BY DATE(ETAPE_DEBUT), ID_RESSOURCE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Performance_Journaliere (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, Pieces_Produites INT, Temps_Production_Secondes INT, Cadence_Pieces_Par_Heure FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_performance", req_table)

    for l in lignes:
        pieces = int(l[2]) if l[2] else 0
        temps = int(l[3]) if l[3] else 0
        cadence = (float(pieces) / (float(temps) / 3600.0)) if temps > 0 else 0.0
        exec_insert(cur_kpi, "INSERT INTO Performance_Journaliere VALUES (NULL, %s, %s, %s, %s, %s)", (l[0], l[1], pieces, temps, cadence))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_qualite():
    print("Calcul Qualite...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(ETAPE_DEBUT), ID_RESSOURCE, COUNT(ID_PRODUCTION_OPERATIONS), SUM(CASE WHEN ETAPE_EST_CONFORME = 1 THEN 1 ELSE 0 END)
        FROM Production_operations WHERE ETAPE_DEBUT IS NOT NULL GROUP BY DATE(ETAPE_DEBUT), ID_RESSOURCE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Qualite_Journaliere (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, Total_Pieces INT, Pieces_Conformes INT, Taux_Qualite_Pourcent FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_qualite", req_table)

    for l in lignes:
        tot = int(l[2]) if l[2] else 0
        conf = int(l[3]) if l[3] else 0
        taux = (float(conf) / float(tot) * 100.0) if tot > 0 else 0.0
        exec_insert(cur_kpi, "INSERT INTO Qualite_Journaliere VALUES (NULL, %s, %s, %s, %s, %s)", (l[0], l[1], tot, conf, taux))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_trs():
    print("Calcul TRS...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        WITH Dispo AS (
            SELECT DATE(ETAT_MACHINE_HORODATAGE) as Date_Jour, ID_RESSOURCE, (SUM(CASE WHEN ETAT_MACHINE_EN_MARCHE = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(ID_SURVEILLANCE_MACHINE) as Dispo_Pct
            FROM Surveillance_machine WHERE ETAT_MACHINE_HORODATAGE IS NOT NULL GROUP BY DATE(ETAT_MACHINE_HORODATAGE), ID_RESSOURCE
        ),
        Perf AS (
            SELECT DATE(ETAPE_DEBUT) as Date_Jour, ID_RESSOURCE, COUNT(ID_PRODUCTION_OPERATIONS) as Pieces_Produites
            FROM Production_operations WHERE ETAPE_DEBUT IS NOT NULL GROUP BY DATE(ETAPE_DEBUT), ID_RESSOURCE
        ),
        Qual AS (
            SELECT DATE(ETAPE_DEBUT) as Date_Jour, ID_RESSOURCE, (SUM(CASE WHEN ETAPE_EST_CONFORME = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(ID_PRODUCTION_OPERATIONS) as Qual_Pct
            FROM Production_operations WHERE ETAPE_DEBUT IS NOT NULL GROUP BY DATE(ETAPE_DEBUT), ID_RESSOURCE
        )
        SELECT D.Date_Jour, D.ID_RESSOURCE, D.Dispo_Pct, P.Pieces_Produites, Q.Qual_Pct
        FROM Dispo D JOIN Perf P ON D.Date_Jour = P.Date_Jour AND D.ID_RESSOURCE = P.ID_RESSOURCE JOIN Qual Q ON D.Date_Jour = Q.Date_Jour AND D.ID_RESSOURCE = Q.ID_RESSOURCE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE TRS_Journalier (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, TRS_Pourcent FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_trs", req_table)

    for l in lignes:
        dispo = float(l[2]) if l[2] else 0.0
        qual = float(l[4]) if l[4] else 0.0
        trs = (dispo / 100.0) * (qual / 100.0) * 100.0
        exec_insert(cur_kpi, "INSERT INTO TRS_Journalier VALUES (NULL, %s, %s, %s)", (l[0], l[1], trs))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_rebuts():
    print("Calcul Rebuts...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(p.ETAPE_DEBUT), p.ID_RESSOURCE, e.DESCRIPTION_ERREUR, COUNT(p.ID_PRODUCTION_OPERATIONS)
        FROM Production_operations p JOIN Erreur e ON p.ID_ERREUR = e.ID_ERREUR 
        WHERE p.ETAPE_EST_CONFORME = 0 AND p.ETAPE_DEBUT IS NOT NULL GROUP BY DATE(p.ETAPE_DEBUT), p.ID_RESSOURCE, e.DESCRIPTION_ERREUR;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Rebuts_Journaliers (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, Description_Erreur VARCHAR(255), Nb_Rebuts INT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_rebuts", req_table)

    for l in lignes:
        exec_insert(cur_kpi, "INSERT INTO Rebuts_Journaliers VALUES (NULL, %s, %s, %s, %s)", (l[0], l[1], l[2], int(l[3] if l[3] else 0)))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_lead_time():
    print("Calcul Lead Time...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(DATE_DEBUT_COMMANDE), ID_COMMANDE, TIMESTAMPDIFF(MINUTE, DATE_DEBUT_COMMANDE, DATE_FIN_COMMANDE)
        FROM Commande WHERE DATE_DEBUT_COMMANDE IS NOT NULL AND DATE_FIN_COMMANDE IS NOT NULL;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Lead_Time_Journalier (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Commande INT, Lead_Time_Minutes INT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_lead_time", req_table)

    for l in lignes:
        exec_insert(cur_kpi, "INSERT INTO Lead_Time_Journalier VALUES (NULL, %s, %s, %s)", (l[0], l[1], int(l[2] if l[2] else 0)))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_otd():
    print("Calcul OTD...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(DATE_FIN_COMMANDE), COUNT(ID_COMMANDE), SUM(CASE WHEN DATE_FIN_COMMANDE <= DATE_FIN_PLANIFIEE_COMMANDE THEN 1 ELSE 0 END)
        FROM Commande WHERE DATE_FIN_COMMANDE IS NOT NULL GROUP BY DATE(DATE_FIN_COMMANDE);
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE OTD_Journalier (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, Total_Commandes INT, Commandes_A_L_Heure INT, OTD_Pourcent FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_otd", req_table)

    for l in lignes:
        tot = int(l[1]) if l[1] else 0
        ok = int(l[2]) if l[2] else 0
        otd = (float(ok) / float(tot) * 100.0) if tot > 0 else 0.0
        exec_insert(cur_kpi, "INSERT INTO OTD_Journalier VALUES (NULL, %s, %s, %s, %s)", (l[0], tot, ok, otd))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_wip():
    print("Calcul WIP...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(ETAPE_DEBUT), ID_RESSOURCE, AVG(STOCK_POSITIONS_OCCUPEES), MAX(STOCK_CAPACITE_TOTALE)
        FROM Production_operations WHERE ETAPE_DEBUT IS NOT NULL GROUP BY DATE(ETAPE_DEBUT), ID_RESSOURCE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE WIP_Journalier (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, Moyenne_Positions_Occupees FLOAT, Capacite_Totale INT, Taux_Occupation_Pourcent FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_wip", req_table)

    for l in lignes:
        occ = float(l[2]) if l[2] else 0.0
        capa = int(l[3]) if l[3] else 0
        taux = (occ / float(capa) * 100.0) if capa > 0 else 0.0
        exec_insert(cur_kpi, "INSERT INTO WIP_Journalier VALUES (NULL, %s, %s, %s, %s, %s)", (l[0], l[1], occ, capa, taux))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_taux_charge():
    print("Calcul Taux de charge...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(ETAT_MACHINE_HORODATAGE), ID_RESSOURCE, COUNT(ID_SURVEILLANCE_MACHINE), SUM(CASE WHEN ETAT_MACHINE_EN_MARCHE = 1 THEN 1 ELSE 0 END)
        FROM Surveillance_machine WHERE ETAT_MACHINE_HORODATAGE IS NOT NULL GROUP BY DATE(ETAT_MACHINE_HORODATAGE), ID_RESSOURCE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Taux_Charge_Journalier (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, Total_Releves INT, Releves_Actifs INT, Taux_Charge_Pourcent FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_taux_charge", req_table)

    for l in lignes:
        tot = int(l[2]) if l[2] else 0
        act = int(l[3]) if l[3] else 0
        charge = (float(act) / float(tot) * 100.0) if tot > 0 else 0.0
        exec_insert(cur_kpi, "INSERT INTO Taux_Charge_Journalier VALUES (NULL, %s, %s, %s, %s, %s)", (l[0], l[1], tot, act, charge))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_cycle():
    print("Calcul Cycle moyen...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT DATE(p.ETAPE_DEBUT), p.ID_RESSOURCE, o.DESCRIPTION_OPERATION, AVG(TIMESTAMPDIFF(SECOND, p.ETAPE_DEBUT, p.ETAPE_FIN))
        FROM Production_operations p JOIN Operation o ON p.ID_OPERATION = o.ID_OPERATION 
        WHERE p.ETAPE_DEBUT IS NOT NULL AND p.ETAPE_FIN IS NOT NULL GROUP BY DATE(p.ETAPE_DEBUT), p.ID_RESSOURCE, o.DESCRIPTION_OPERATION;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Cycle_Moyen_Journalier (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, Description_Operation VARCHAR(255), Cycle_Moyen_Secondes FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_cycle_moyen", req_table)

    for l in lignes:
        exec_insert(cur_kpi, "INSERT INTO Cycle_Moyen_Journalier VALUES (NULL, %s, %s, %s, %s)", (l[0], l[1], l[2], float(l[3] if l[3] else 0)))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_fiabilite():
    print("Calcul Fiabilite...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        WITH Events AS (
            SELECT DATE(ETAT_MACHINE_HORODATAGE) as Date_Jour, ID_RESSOURCE, ETAT_MACHINE_HORODATAGE, ETAT_MACHINE_EN_ARRET, ETAT_MACHINE_RESET,
                LEAD(ETAT_MACHINE_HORODATAGE) OVER(PARTITION BY ID_RESSOURCE ORDER BY ETAT_MACHINE_HORODATAGE) AS NEXT_TIME,
                LEAD(ETAT_MACHINE_RESET) OVER(PARTITION BY ID_RESSOURCE ORDER BY ETAT_MACHINE_HORODATAGE) AS NEXT_IS_RESET,
                LEAD(ETAT_MACHINE_EN_ARRET) OVER(PARTITION BY ID_RESSOURCE ORDER BY ETAT_MACHINE_HORODATAGE) AS NEXT_IS_ARRET
            FROM Surveillance_machine WHERE ETAT_MACHINE_EN_ARRET = 1 OR ETAT_MACHINE_RESET = 1
        )
        SELECT Date_Jour, ID_RESSOURCE,
            AVG(CASE WHEN ETAT_MACHINE_EN_ARRET = 1 AND NEXT_IS_RESET = 1 THEN TIMESTAMPDIFF(SECOND, ETAT_MACHINE_HORODATAGE, NEXT_TIME) END) / 60.0 AS MTTR,
            AVG(CASE WHEN ETAT_MACHINE_RESET = 1 AND NEXT_IS_ARRET = 1 THEN TIMESTAMPDIFF(SECOND, ETAT_MACHINE_HORODATAGE, NEXT_TIME) END) / 60.0 AS MTBF
        FROM Events WHERE Date_Jour IS NOT NULL GROUP BY Date_Jour, ID_RESSOURCE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Fiabilite_Journaliere (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Date_Jour DATE, ID_Ressource INT, MTTR_Minutes FLOAT, MTBF_Minutes FLOAT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_fiabilite", req_table)

    for l in lignes:
        exec_insert(cur_kpi, "INSERT INTO Fiabilite_Journaliere VALUES (NULL, %s, %s, %s, %s)", (l[0], l[1], float(l[2] if l[2] else 0), float(l[3] if l[3] else 0)))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

def kpi_stock():
    print("Calcul Stock...")
    conn_mcd = get_conn()
    cur_mcd = conn_mcd.cursor()
    cur_mcd.execute("USE mcd;")
    cur_mcd.execute("""
        SELECT p.DESCRIPTION_PIECE, SUM(c.QUANTITE) FROM CONTENU_STOCK c JOIN Piece p ON c.ID_PIECE = p.ID_PIECE GROUP BY p.DESCRIPTION_PIECE;
    """)
    lignes = cur_mcd.fetchall()

    req_table = """
        CREATE TABLE Stock_Actuel (
            ID_ENREGISTREMENT INT AUTO_INCREMENT PRIMARY KEY, Description_Piece VARCHAR(255), Quantite_Totale INT
        );
    """
    conn_kpi, cur_kpi = init_kpi_db("kpi_stock", req_table)

    for l in lignes:
        exec_insert(cur_kpi, "INSERT INTO Stock_Actuel VALUES (NULL, %s, %s)", (l[0], int(l[1] if l[1] else 0)))

    conn_kpi.commit()
    conn_kpi.close()
    conn_mcd.close()

if __name__ == "__main__":
    print("Début du traitement des KPIs...")
    kpi_dispo()
    kpi_perf()
    kpi_qualite()
    kpi_trs()
    kpi_rebuts()
    kpi_lead_time()
    kpi_otd()
    kpi_wip()
    kpi_taux_charge()
    kpi_cycle()
    kpi_fiabilite()
    kpi_stock()
    print("Bases KPIs mises à jour avec succès.")
