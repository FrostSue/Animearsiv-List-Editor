from flask import Flask, render_template, redirect, url_for, send_file, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database.db import db
import threading
import logging
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    data = db.load()
    if user_id in data.get("web_admins", {}):
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if db.check_web_login(username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    data = db.load()
    anime_list = data.get('anime_list', [])
    stats = {
        "total": len(anime_list),
        "last_update": anime_list[-1]['date_added'] if anime_list else "Yok"
    }
    return render_template('index.html', animes=anime_list, stats=stats)

@app.route('/edit/<path:title>', methods=['GET', 'POST'])
@login_required
def edit(title):
    data = db.load()
    anime = next((a for a in data['anime_list'] if a['title'] == title), None)
    
    if not anime:
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_title = request.form['title']
        new_url = request.form['url']
        db.update_anime(title, new_title, new_url)
        return redirect(url_for('index'))

    return render_template('edit.html', anime=anime)

@app.route('/delete/<path:title>')
@login_required
def delete(title):
    db.delete_anime(title)
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.add_web_admin(username, password):
            flash(f'✅ Admin {username} eklendi.')
        else:
            flash('❌ Bu kullanıcı adı zaten var.')
    
    data = db.load()
    admins = list(data.get("web_admins", {}).keys())
    return render_template('settings.html', admins=admins)

@app.route('/download')
@login_required
def download():
    db_path = os.path.abspath("database/data.json")
    return send_file(db_path, as_attachment=True)

def run_web():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def start_web_server():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()