from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime 

app = Flask(__name__, template_folder='templates', static_url_path='/static')

app.config['DATABASE'] = 'backend/database.db'
app.config['SECRET_KEY'] = 'cookiesecreto'

login_manager = LoginManager()
login_manager.init_app(app)

class Usuario(UserMixin):
    def __init__(self, id, nome, email, senha):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha

    @staticmethod
    def buscar_por_id(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM membros WHERE id = ?', (id,))
        usuario_data = cursor.fetchone()
        cursor.close()

        if not usuario_data:
            return None

        id, nome, email, senha = usuario_data
        return Usuario(id=id, nome=nome, email=email, senha=senha)

    @staticmethod
    def buscar_por_email(email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM membros WHERE email = ?', (email,))
        usuario_data = cursor.fetchone()
        cursor.close()

        if not usuario_data:
            return None

        id, nome, email, senha = usuario_data
        return Usuario(id=id, nome=nome, email=email, senha=senha)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.buscar_por_id(user_id)

@login_manager.request_loader
def load_user_from_request(request):
    email = request.form.get('email')
    if email:
        usuario = Usuario.buscar_por_email(email)
        if usuario:
            return usuario
    return None

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
    return render_template("index.html")

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT * FROM membros WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Email já cadastrado. Por favor, tente outro email.', 'cadastro_error')
            return redirect(url_for('cadastro'))
        
        else:
            cursor.execute('INSERT INTO membros (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))  
            db.commit()
            cursor.close()
            
            cursor = db.cursor()
            cursor.execute('SELECT * FROM membros WHERE email = ?', (email,))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                usuario = Usuario(user[0], nome, email, senha)
                login_user(usuario)
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
            usuario = Usuario(user[0], user[1], user[2], user[3])
            login_user(usuario)
            flash('Login realizado com sucesso!', 'login_success')
            return redirect(url_for('usuarioentrou'))
        else:
            flash('Email ou senha incorretos. Por favor, tente novamente.', 'login_error')
        
        cursor.close()
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/usuarioentrou")
@login_required
def usuarioentrou():
    return render_template("usuarioentrou.html", nome=current_user.nome)

@app.route("/novatarefa", methods=['GET', 'POST'])
@login_required
def novatarefa():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        
        usuario_id = current_user.id
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT id FROM tarefa WHERE nome = ? AND usuario_id = ?', (nome, usuario_id))
        existing_task = cursor.fetchone()
        
        if existing_task:
            flash('Nome de tarefa já usado', 'tarefa_error')
            return redirect(url_for('novatarefa'))
        
        cursor.execute('INSERT INTO tarefa (nome, descricao, prioridade, usuario_id) VALUES (?, ?, ?, ?)', (nome, descricao, prioridade, usuario_id))
        db.commit()
        cursor.close()
        
        return redirect(url_for('minhastarefas'))  
    
    return render_template("novatarefa.html")


@app.route("/minhastarefas")
@login_required
def minhastarefas():
    usuario_id = current_user.id
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, nome, descricao, prioridade, DATE(data_criacao) FROM tarefa WHERE usuario_id = ?', (usuario_id,))
    tarefas = cursor.fetchall()
    cursor.close()

    return render_template("minhastarefas.html", tarefas=tarefas)


@app.route("/calendario")
@login_required
def calendario():
    return render_template("calendario.html")


@app.route("/excluir_tarefa/<int:tarefa_id>", methods=['POST'])
@login_required
def excluir_tarefa(tarefa_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM tarefa WHERE id = ?', (tarefa_id,))
    db.commit()
    cursor.close()
    flash('Tarefa excluída com sucesso!', 'tarefa_excluida')
    return redirect(url_for('minhastarefas'))

@app.route("/editartarefas/<int:tarefa_id>", methods=['GET', 'POST'])
@login_required
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
        
        flash('Tarefa atualizada com sucesso!', 'tarefa_editada')
        return redirect(url_for('minhastarefas'))

    return render_template('editartarefas.html', tarefa=tarefa)

@app.route("/excluirusuario", methods=['GET', 'POST'])
@login_required
def excluirusuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT * FROM membros WHERE nome = ? AND email = ? AND senha = ?', (nome, email, senha))
        user = cursor.fetchone()
        
        if user:
            cursor.execute('DELETE FROM membros WHERE id = ?', (user[0],))
            db.commit()
            cursor.close()
            logout_user()
            flash('Conta excluída com sucesso!', 'excluirusuario_success')
            return redirect(url_for('home'))
        else:
            flash('Informações incorretas. Por favor, tente novamente.', 'excluirusuario_error')
            cursor.close()
    
    return render_template("excluirusuario.html")

if __name__ == "__main__":
    app.run()
