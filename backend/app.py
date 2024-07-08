from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3

app = Flask(__name__, template_folder='templates', static_url_path='/static')

app.config['DATABASE'] = 'backend/database.db'
app.config['SECRET_KEY'] = 'cookiesecreto'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/") 
def home():

    return render_template("home.html")

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT * FROM membros WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Email já cadastrado. Por favor, tente outro email.')
            return redirect(url_for('cadastro'))
        
        else:
            cursor.execute('INSERT INTO membros (email, senha) VALUES (?, ?)', (email, senha))
        db.commit()
        cursor.close()
        
        return redirect(url_for('novatarefa')) 
    
    return render_template("cadastro.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT * FROM membros WHERE email = ? AND senha = ?', (email, senha))
        user = cursor.fetchone()
        
        if user:
            return redirect(url_for('novatarefa'))
        else:
            flash('Email ou senha incorretos. Por favor, tente novamente.', 'error')
        
        cursor.close()
    
    return render_template("login.html")

@app.route("/tarefas")
def tarefas():

    return render_template("tarefas.html")

@app.route("/novatarefa")
def novatarefa():

    return render_template("novatarefa.html")

@app.route("/minhastarefas")
def minhastarefas():

    return render_template("minhastarefas.html")

if __name__ == "__main__":
    app.run(debug=True)