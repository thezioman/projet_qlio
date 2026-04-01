-- ============================================================
-- T'EleFan MES 4.0 — Initialisation de la base d'authentification
-- Exécuté automatiquement au démarrage du conteneur MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS python_auth_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE python_auth_db;

-- Table des utilisateurs (mots de passe hachés via werkzeug/bcrypt)
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('admin', 'manager_ops', 'manager_supply') NOT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Note : les mots de passe hachés sont insérés par init/setup_users.py
-- au démarrage de l'application (via entrypoint.sh)
