from flask import Flask, render_template, redirect, url_for, send_file
from database.db import db
import threading
import logging
import os

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    data = db.load()
    anime_list = data.get('anime_list', [])
    stats = {
        "total": len(anime_list),
        "last_update": anime_list[-1]['date_added'] if anime_list else "Yok"
    }
    return render_template('index.html', animes=anime_list, stats=stats)

@app.route('/delete/<title>')
def delete(title):
    data = db.load()
    data['anime_list'] = [a for a in data['anime_list'] if a['title'] != title]
    db.save(data)
    return redirect(url_for('index'))

@app.route('/download')
def download():
    db_path = os.path.abspath("database/data.json")
    return send_file(db_path, as_attachment=True)

def run_web():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def start_web_server():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()