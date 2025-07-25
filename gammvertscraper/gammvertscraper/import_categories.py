import sqlite3
import csv
import os

DB_PATH = 'gammvert.db'
CSV_PATH = 'categories.csv'

#Connexion (le fichier est créé s'il n'existe pas)
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

#Supprimer et recréer la table
cur.execute("DROP TABLE IF EXISTS categories;")
cur.execute("""
    CREATE TABLE categories (
        category_id   TEXT PRIMARY KEY,
        parent_id     TEXT,
        name          TEXT,
        url           TEXT,
        is_pagelist   INTEGER
    )
""")

#Charger le CSV
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    to_db = [
        (
            row['category_id'],
            row.get('parent_id', '') or None,
            row['name'],
            row['url'],
            int(row['is_pagelist'])
        )
        for row in reader
    ]

#Insérer les data
cur.executemany(
    "INSERT INTO categories (category_id, parent_id, name, url, is_pagelist) VALUES (?, ?, ?, ?, ?);",
    to_db
)

#Valider et fermer
conn.commit()
conn.close()

print(f"Importé {len(to_db)} catégories dans {DB_PATH}")
