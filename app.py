from flask import Flask, redirect, render_template, request, session, url_for
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import os

app = Flask(__name__)
app.secret_key = "chave_segura_123_aula23" 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect("DB_PATH")
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login20"))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    db = sqlite3.connect("database.db")
    # Cria a tabela de utilizadores (Aula 23)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
 
    db.execute("""
        CREATE TABLE IF NOT EXISTS recursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT
        )
    """)
    

    db.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recurso_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            observacoes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (recurso_id) REFERENCES recursos (id)
        )
    """)
    
 
    if not db.execute("SELECT * FROM recursos").fetchone():
        db.execute("INSERT INTO recursos (nome) VALUES ('Sala de Reuniões'), ('Auditório'), ('Portátil A')")
    db.commit()
    db.close()


init_db()

# ==============================
# AREA DAS ROTAS
# ==============================
#=============================
# Aula 11
@app.route("/")
def home():
    return "Olá, Flask! <br><a href='/login20'>Ir para Login Aula 20</a>"

@app.route("/sobre_nos")
def sobre_nos():
    return "<h1>Sobre nós</h1><p>Esta é a página sobre.</p>"

@app.route("/contacto_texto")
def contacto_texto():
    return "<h1>Contacto</h1><p>Esta é a página de contacto.</p>"

@app.route("/hello/<nome>")
def hello(nome):
    return f"<h1>Bem-vindo(a), {nome}!</h1>"

#==============================
# Aula 12
@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        return f"<h2>Dados Recebidos:</h2><p>Nome: {nome}</p><p>Email: {email}</p><a href='/form'>Voltar</a>"
    return render_template("form12.html")

#==============================
# Aula 13
@app.route("/perfil/<nome>")
def perfil(nome):
    idade = 20
    hobbies = ["Surf", "Dança", "Música"]
    return render_template("perfil.html", nome=nome, idade=idade, hobbies=hobbies)

#==============================
# Aula 14 e 15 (Rotas de Navegação)
@app.route("/aula14")
def index(): return render_template("index.html")

@app.route("/sobre")
def sobre(): return render_template("sobre.html")

@app.route("/contactos")
def contactos(): return render_template("contactos.html")

#==============================
# Aula 16 e 17 (Formulários e Validação)
@app.route("/contacto17", methods=["GET", "POST"])
def contacto_aula17():
    
    return render_template("contacto17.html")

#==============================
# Aula 18 
@app.route("/login18", methods=["GET", "POST"])
def login18():
    if request.method == "POST":
        session["user"] = request.form.get("utilizador")
        return redirect(url_for("perfil18"))
    return render_template("login18.html")

@app.route("/perfil18")
def perfil18():
    if "user" in session:
        return render_template("perfil18.html", nome=session["user"])
    return redirect(url_for("login18"))

#==============================
# Aula 19 (Login com DB)
@app.route("/login19", methods=["GET", "POST"])
def login19():
    if request.method == "POST":
        username = request.form.get("utilizador") 
        password = request.form.get("password")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user and user["password"] == password:
            session["username"] = user["username"] 
            return redirect("/area_privada19")
        return render_template("login19.html", erro="Incorreto.")
    return render_template("login19.html")

#==============================
# Aula 20 (Login Seguro com Hash e ID)
@app.route("/registar20", methods=["GET", "POST"])
def registar20():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = generate_password_hash(request.form.get("password").strip())
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            db.commit()
            return redirect(url_for("login20"))
        except:
            return render_template("registar20.html", erro="Erro ao registar.")
    return render_template("registar20.html")

@app.route("/login20", methods=["GET", "POST"])
def login20():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"] 
            session["username"] = user["username"]
            return redirect(url_for("dashboard21"))
        
        return render_template("login20.html", erro="Credenciais inválidas.")
    return render_template("login20.html")

#==============================
# Aula 21, 22 e 23 (CRUD e Dashboard)
@app.route("/dashboard21")
@login_required
def dashboard21():
    return render_template("dashboard21.html")

@app.route("/users23")
@login_required
def users23():
    db = get_db()
    utilizadores = db.execute("SELECT id, username, email FROM users").fetchall()
    
    return render_template("users23.html", users=utilizadores)

@app.route("/edit23/<int:id>", methods=["GET", "POST"])
@login_required
def edit23(id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (id,)).fetchone()
    if request.method == "POST":
        db.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", 
                   (request.form.get("username"), request.form.get("email"), id))
        db.commit()
        return redirect(url_for("users23"))
    return render_template("edit23.html", user=user)

@app.route("/delete23/<int:id>")
@login_required
def delete23(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("users23"))

@app.route("/logout20")
def logout20():
    session.clear()
    return redirect(url_for("login20"))

#==============================
#Aula 24, 25, 26, 27

@app.route("/reservas")
@login_required
def listar_reservas():
    db = get_db()
    
    
    filtro_recurso = request.args.get("recurso_id")
    filtro_data = request.args.get("data")
    
     
    query = """
        SELECT reservas.*, recursos.nome AS recurso_nome 
        FROM reservas 
        JOIN recursos ON reservas.recurso_id = recursos.id 
        WHERE reservas.user_id = ?
    """
    parametros = [session["user_id"]]

    
    if filtro_recurso:
        query += " AND reservas.recurso_id = ?"
        parametros.append(filtro_recurso)
    
    if filtro_data:
        query += " AND reservas.data = ?"
        parametros.append(filtro_data)

    query += " ORDER BY data ASC, hora ASC"
    
    reservas = db.execute(query, parametros).fetchall()
    recursos = db.execute("SELECT * FROM recursos").fetchall()
    
    return render_template("reservas24.html", reservas=reservas, recursos=recursos)

@app.route("/criar_reserva", methods=["GET", "POST"])
@login_required
def criar_reserva():
    db = get_db()
    
    if request.method == "POST":
        recurso_id = request.form.get("recurso_id")
        data = request.form.get("data")
        hora = request.form.get("hora")
        
       
        conflito = db.execute("SELECT * FROM reservas WHERE recurso_id = ? AND data = ? AND hora = ?", 
                             (recurso_id, data, hora)).fetchone()
        
        if conflito:
            recursos = db.execute("SELECT * FROM recursos").fetchall()
            return render_template("criar_reserva24.html", recursos=recursos, erro="Horário ocupado!")

        db.execute("INSERT INTO reservas (user_id, recurso_id, data, hora) VALUES (?, ?, ?, ?)",
                   (session["user_id"], recurso_id, data, hora))
        db.commit()
        return redirect(url_for("listar_reservas"))

   
    recursos = db.execute("SELECT * FROM recursos").fetchall()
    return render_template("criar_reserva24.html", recursos=recursos)

#==============================
#Aula 28
@app.route("/relatorio/recurso/<int:recurso_id>")
@login_required
def relatorio_recurso(recurso_id):
    db = get_db()
    # Busca o nome do recurso
    recurso = db.execute("SELECT nome FROM recursos WHERE id = ?", (recurso_id,)).fetchone()
    
    # Busca todas as reservas desse recurso (ordenadas por data)
    reservas = db.execute("""
        SELECT reservas.*, users.username 
        FROM reservas 
        JOIN users ON reservas.user_id = users.id 
        WHERE recurso_id = ? 
        ORDER BY data DESC
    """, (recurso_id,)).fetchall()
    
    return render_template("relatorio.html", reservas=reservas, recurso=recurso)

@app.route("/delete_reserva/<int:id>")
@login_required
def delete_reserva(id):
    db = get_db()
    db.execute("DELETE FROM reservas WHERE id = ? AND user_id = ?", (id, session["user_id"]))
    db.commit()

    return redirect(url_for('listar_reservas', msg="Reserva cancelada com sucesso!"))
#==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
