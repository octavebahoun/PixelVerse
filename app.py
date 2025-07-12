from flask import Flask, render_template, request, url_for, session, redirect, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "galerie.db") 

# === CONFIGURATION FLASK === 
app = Flask(__name__)
app.secret_key = "645231977ghtffyudgsyuguilbqcyuigunnnnnnnnabvycuhgs462w"


# === FONCTION DE CONNEXION BDD ===
def get_db_conn(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  
    return conn

# === INITIALISATION BDD GALERIE ===
def init_galerie_db():
    with get_db_conn("galerie.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                image_name TEXT PRIMARY KEY,
                like_count INTEGER DEFAULT 0
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS favoris (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                image_name TEXT,
                UNIQUE(user_id, image_name)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS likes_users (
                user_id INTEGER,
                image_name TEXT,
                PRIMARY KEY (user_id, image_name)
            )
        """)
        conn.commit()

# === INITIALISATION BDD UTILISATEURS ===
def init_utilisateurs_db():
    with get_db_conn("utilisateurs.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                motdepasse TEXT NOT NULL,
                date_inscription TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                page TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_galerie_db()
init_utilisateurs_db()

# === DÉCORATEUR PROTECTION ===
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('connexion'))
        return f(*args, **kwargs)
    return decorated_function

# === LOG ACTIVITÉ UTILISATEUR ===
def log_user_activity(page):
    if 'user_id' in session:
        with get_db_conn("utilisateurs.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO stats (user_id, page) VALUES (?, ?)", (session['user_id'], page))
            conn.commit()

# === ROUTES ===

@app.route("/")
def accueil():
    if 'user_id' in session:
        log_user_activity("accueil")
    return render_template("accueil.html")

# === ROUTE INSCRIPTION ===
@app.route("/formulaire", methods=["GET", "POST"])
def formulaire():
    if request.method == "POST":
        nom = request.form.get("Nom", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        if not nom or not email or not password:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for("formulaire"))

        with get_db_conn("utilisateurs.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM utilisateurs WHERE nom = ? OR email = ?", (nom, email))
            if cur.fetchone():
                flash("Nom ou email déjà utilisé.", "error")
                return redirect(url_for("formulaire"))

            password_hash = generate_password_hash(password)
            date_inscription = datetime.now().strftime('%Y-%m-%d')
            cur.execute(
                "INSERT INTO utilisateurs (nom, email, motdepasse, date_inscription) VALUES (?, ?, ?, ?)",
                (nom, email, password_hash, date_inscription)
            )
            conn.commit()

        flash(f"Inscription de {nom} réussie.", "success")
        return redirect(url_for("connexion"))

    return render_template("formulaire.html")


# === ROUTE CONNEXION ===
@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if 'user_id' in session:
        return redirect(url_for('dashboard' if session.get('role') == 'admin' else 'galerie'))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        with get_db_conn("utilisateurs.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM utilisateurs WHERE email = ?", (email,))
            utilisateur = cur.fetchone()

        if utilisateur:
            if check_password_hash(utilisateur['motdepasse'], password):
                session['user_id'] = utilisateur['id']
                session['user_nom'] = utilisateur['nom']
                session['role'] = utilisateur['role']
                session.modified = True

                flash("Connexion réussie.", "success")
                return redirect(url_for('dashboard' if utilisateur['role'] == 'admin' else 'galerie'))
            else:
                flash("Mot de passe incorrect.", "error")
        else:
            flash("Email inconnu.", "error")

        return redirect(url_for("connexion"))

    return render_template("connexion.html")


# === ROUTE DECONNEXION ===
@app.route("/deconnexion")
def deconnexion():
    session.clear()
    flash("Déconnexion effectuée.", "success")
    return redirect(url_for("connexion"))


# === ROUTE GALERIE ===
@app.route("/galerie")
def galerie():
    if 'user_id' in session:
        log_user_activity("galerie")

    images = [img for img in os.listdir("static/images") if img.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]
    likes = {}
    liked_images = []

    with get_db_conn("galerie.db") as conn:
        cur = conn.cursor()
        for image in images:
            cur.execute("SELECT like_count FROM likes WHERE image_name = ?", (image,))
            row = cur.fetchone()
            likes[image] = row['like_count'] if row else 0

        if 'user_id' in session:
            user_id = session['user_id']
            cur.execute("SELECT image_name FROM likes_users WHERE user_id = ?", (user_id,))
            liked_images = [row['image_name'] for row in cur.fetchall()]

    return render_template("galerie.html", images=images, likes=likes, liked_images=liked_images)


# === ROUTE LIKE ===
@app.route("/like", methods=["POST"])
@login_required
def like():
    data = request.get_json()
    image_name = data.get("image_name")
    action = data.get("action")
    user_id = session['user_id']

    if not image_name or action not in ("like", "unlike"):
        return jsonify({"success": False, "message": "Données invalides."}), 400

    if not os.path.isfile(os.path.join("static/images", image_name)):
        return jsonify({"success": False, "message": "Image introuvable."}), 404

    with get_db_conn("galerie.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT like_count FROM likes WHERE image_name = ?", (image_name,))
        row = cur.fetchone()
        like_count = row['like_count'] if row else 0

        if action == "like":
            cur.execute("SELECT 1 FROM likes_users WHERE user_id = ? AND image_name = ?", (user_id, image_name))
            if cur.fetchone():
                return jsonify({"success": False, "message": "Déjà liké."}), 400

            cur.execute("INSERT INTO likes_users (user_id, image_name) VALUES (?, ?)", (user_id, image_name))
            if row is None:
                cur.execute("INSERT INTO likes (image_name, like_count) VALUES (?, 1)", (image_name,))
                like_count = 1
            else:
                cur.execute("UPDATE likes SET like_count = like_count + 1 WHERE image_name = ?", (image_name,))
                like_count += 1

        elif action == "unlike":
            cur.execute("SELECT 1 FROM likes_users WHERE user_id = ? AND image_name = ?", (user_id, image_name))
            if not cur.fetchone():
                return jsonify({"success": False, "message": "Pas liké."}), 400

            cur.execute("DELETE FROM likes_users WHERE user_id = ? AND image_name = ?", (user_id, image_name))
            like_count = max(0, like_count - 1)
            cur.execute("UPDATE likes SET like_count = ? WHERE image_name = ?", (like_count, image_name))

        conn.commit()

    return jsonify({"success": True, "like_count": like_count})

@app.route("/favoris")
@login_required
def favoris():
    user_id = session['user_id']
    with get_db_conn("galerie.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT image_name FROM likes_users WHERE user_id = ?", (user_id,))
        favoris_images = [row['image_name'] for row in cur.fetchall()]
    return render_template("favoris.html", favoris=favoris_images)


@app.route("/supprimer_favoris", methods=["POST"])
def supprimer_favoris():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Non autorisé"})

    image_name = request.form.get("image_name")
    if not image_name:
        return jsonify({"success": False, "message": "Image manquante"})

    with get_db_conn("galerie.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM likes_users WHERE user_id = ? AND image_name = ?", (session['user_id'], image_name))
        conn.commit()

    return jsonify({"success": True, "message": "Favori supprimé avec succès"})



@app.route("/populaires")
def populaires():
    with get_db_conn("galerie.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT image_name, COUNT(*) as like_count
            FROM likes_users
            GROUP BY image_name
            HAVING like_count > 10
            ORDER BY like_count DESC
        """)
        images_populaires = cur.fetchall()

    print("📊 Images populaires (>10 likes) trouvées :", images_populaires)

    return render_template("populaires.html", images=images_populaires)





@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'Aucun fichier sélectionné'
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return 'Fichier invalide'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('galerie'))
    return render_template('upload.html')






# === ROUTE PROFIL ===
@app.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    user_id = session['user_id']

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        if not nom or not email:
            flash("Champs requis.", "error")
            return redirect(url_for("profil"))

        with get_db_conn("utilisateurs.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM utilisateurs WHERE email = ? AND id != ?", (email, user_id))
            if cur.fetchone():
                flash("Email utilisé.", "error")
                return redirect(url_for("profil"))

            cur.execute("UPDATE utilisateurs SET nom = ?, email = ? WHERE id = ?", (nom, email, user_id))
            conn.commit()

        session['user_nom'] = nom
        flash("Profil mis à jour.", "success")
        return redirect(url_for("profil"))

    with get_db_conn("utilisateurs.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT nom, email FROM utilisateurs WHERE id = ?", (user_id,))
        user = cur.fetchone()

    if not user:
        return redirect(url_for("deconnexion"))

    return render_template("profil.html", nom=user['nom'], email=user['email'])


# === ROUTE DASHBOARD ===
@app.route("/dashboard")
@login_required
def dashboard():
    today = datetime.now().strftime('%Y-%m-%d')

    with get_db_conn("utilisateurs.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM utilisateurs")
        total_users = cur.fetchone()['total']

        cur.execute("SELECT COUNT(*) AS today_count FROM utilisateurs WHERE date(date_inscription) = ?", (today,))
        inscriptions_today = cur.fetchone()['today_count']

        cur.execute("""
            SELECT utilisateurs.nom, COUNT(stats.id) AS total_views
            FROM stats
            JOIN utilisateurs ON stats.user_id = utilisateurs.id
            GROUP BY stats.user_id
            ORDER BY total_views DESC
            LIMIT 5
        """)
        top_users = cur.fetchall()

    with get_db_conn("galerie.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT SUM(like_count) AS total_likes FROM likes")
        total_likes = cur.fetchone()['total_likes'] or 0

        cur.execute("SELECT COUNT(*) AS total_fav FROM favoris")
        total_favoris = cur.fetchone()['total_fav']

        cur.execute("SELECT image_name, like_count FROM likes ORDER BY like_count DESC LIMIT 5")
        top_images = cur.fetchall()

        images_count = len([img for img in os.listdir("static/images") if img.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))])

    return render_template(
        "dashboard.html",
        total_users=total_users,
        inscriptions_today=inscriptions_today,
        images_count=images_count,
        total_likes=total_likes,
        total_favoris=total_favoris,
        top_users=top_users,
        top_images=top_images
    )



# === ROUTE STATISTIQUES ===
@app.route("/stats")
@login_required
def stats():
    with get_db_conn("utilisateurs.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT utilisateurs.nom, stats.page, stats.timestamp
            FROM stats
            JOIN utilisateurs ON stats.user_id = utilisateurs.id
            ORDER BY stats.timestamp DESC
        """)
        stats_data = cur.fetchall()

    return render_template("stats.html", stats=stats_data)


# === ROUTE SUPPRESSION DE COMPTE ===
@app.route("/supprimer_compte", methods=["POST"])
@login_required
def supprimer_compte():
    user_id = session['user_id']
    with get_db_conn("utilisateurs.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
        conn.commit()

    session.clear()
    flash("Compte supprimé.", "success")
    return redirect(url_for("formulaire"))



@app.route("/modifier_profil")
def modifier_profil():
    if 'user_id' in session:
        log_user_activity("modifier_profil")
    return render_template("modifier_profil.html")



# === CONFIGURATION UPLOAD ===
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Types de fichiers autorisés
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Fonction pour vérifier l'extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/gestion_utilisateurs")
@login_required
def gestion_utilisateurs():
    if session.get("role") != "admin":
        return redirect(url_for("accueil"))

    with get_db_conn("utilisateurs.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nom, email FROM utilisateurs")
        utilisateurs = cur.fetchall()

    return render_template("gestion_utilisateurs.html", utilisateurs=utilisateurs)


@app.route("/supprimer_utilisateur/<int:user_id>", methods=["POST"])
@login_required
def supprimer_utilisateur(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("accueil"))

    with get_db_conn("utilisateurs.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
        conn.commit()

    flash("Utilisateur supprimé.", "success")
    return redirect(url_for("gestion_utilisateurs"))

# === LANCEMENT DU SERVEUR ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

