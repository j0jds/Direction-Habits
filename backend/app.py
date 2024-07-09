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
            flash('Email já cadastrado. Por favor, tente outro email.', 'error')
            return redirect(url_for('cadastro'))
        
        else:
            cursor.execute('INSERT INTO membros (email, senha) VALUES (?, ?)', (email, senha))
            db.commit()
            cursor.close()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('usuarioentrou')) 
    
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
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('usuarioentrou'))
        else:
            flash('Email ou senha incorretos. Por favor, tente novamente.', 'error')
        
        cursor.close()
    
    return render_template("login.html")

@app.route("/usuarioentrou")
def usuarioentrou():
    return render_template("usuarioentrou.html")

@app.route("/novatarefa", methods=['GET', 'POST'])
def novatarefa():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('INSERT INTO tarefa (nome, descricao, prioridade) VALUES (?, ?, ?)', (nome, descricao, prioridade))
        db.commit()
        cursor.close()
        
        return redirect(url_for('minhastarefas'))  
    
    return render_template("novatarefa.html")

@app.route("/minhastarefas")
def minhastarefas():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tarefa')
    tarefas = cursor.fetchall()
    cursor.close()
    
    return render_template("minhastarefas.html", tarefas=tarefas)

@app.route("/excluir_tarefa/<int:tarefa_id>", methods=['POST'])
def excluir_tarefa(tarefa_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM tarefa WHERE id = ?', (tarefa_id,))
    db.commit()
    cursor.close()
    flash('Tarefa excluída com sucesso!', 'success')
    return redirect(url_for('minhastarefas'))

@app.route("/editartarefas/<int:tarefa_id>", methods=['GET', 'POST'])
def editartarefas(tarefa_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tarefa WHERE id = ?', (tarefa_id,))
    tarefa = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']

        cursor = db.cursor()
        cursor.execute('UPDATE tarefa SET nome = ?, descricao = ?, prioridade = ? WHERE id = ?', (nome, descricao, prioridade, tarefa_id))
        db.commit()
        cursor.close()
        
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('minhastarefas'))

    return render_template('editartarefas.html', tarefa=tarefa)

if __name__ == "__main__":
    app.run(debug=True)
