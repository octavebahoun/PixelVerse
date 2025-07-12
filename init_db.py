import sqlite3

# Connexion à la base de données (elle sera créée si elle n'existe pas)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Création de la table favoris si elle n'existe pas déjà
cursor.execute("""
CREATE TABLE IF NOT EXISTS favoris (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_name TEXT NOT NULL,
    date_ajout TEXT NOT NULL
)
""")

# Commit et fermeture
conn.commit()
conn.close()

print("✅ Table 'favoris' créée avec succès (si elle n'existait pas déjà).")
