"""
Script de chargement de données de catégories dans une base SQLite.

Ce script :
1. Crée (ou recrée) une base de données SQLite.
2. Supprime et reconstruit la table `categories`.
3. Lit les données depuis un fichier CSV.
4. Insère les données dans la base.
"""

import sqlite3
import csv
import os

# Chemin du fichier SQLite
DB_PATH = 'gammvert.db'

# Chemin du fichier CSV contenant les catégories
CSV_PATH = 'categories.csv'

# Connexion à la base de données SQLite.
# Le fichier est créé s'il n'existe pas.
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Suppression de la table 'categories' si elle existe,
# puis création d'une nouvelle table avec les colonnes définies.
cur.execute("DROP TABLE IF EXISTS categories;")
cur.execute("""
    CREATE TABLE categories (
        category_id   TEXT PRIMARY KEY,  -- Identifiant unique de la catégorie
        parent_id     TEXT,              -- ID de la catégorie parente, si elle existe
        name          TEXT,              -- Nom de la catégorie
        url           TEXT,              -- URL associée
        is_pagelist   INTEGER            -- Indique si la catégorie correspond à une liste paginée (1 ou 0)
    )
""")

# Lecture du fichier CSV en tant que dictionnaire.
# Chaque ligne est transformée en tuple correspondant aux colonnes de la table.
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    to_db = [
        (
            row['category_id'],
            row.get('parent_id', '') or None,  # Convertir les valeurs vides en NULL
            row['name'],
            row['url'],
            int(row['is_pagelist'])            # Conversion explicite en entier
        )
        for row in reader
    ]

# Insertion des données dans la base de données via executemany (batch insert).
cur.executemany(
    "INSERT INTO categories (category_id, parent_id, name, url, is_pagelist) VALUES (?, ?, ?, ?, ?);",
    to_db
)

# Commit des changements et fermeture de la connexion.
conn.commit()
conn.close()

# Affichage du nombre de lignes importées.
print(f"Importé {len(to_db)} catégories dans {DB_PATH}")
