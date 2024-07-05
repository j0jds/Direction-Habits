from flask import Flask, render_template

app = Flask(__name__, template_folder='templates', static_url_path='/static')

@app.route("/") 
def home():
    
    return render_template("home.html")

@app.route("/cadastro")
def cadastro():
    
    return render_template("cadastro.html")

@app.route("/login")
def login():
    
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