from flask import Flask, render_template, redirect, url_for, send_file
from database.db import db
import threading
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    data = db.load()
    return render_template('index.html', animes=data['anime_list'])

@app.route('/delete/<title>')
def delete(title):
    data = db.load()
    data['anime_list'] = [a for a in data['anime_list'] if a['title'] != title]
    db.save(data)
    return redirect(url_for('index'))

@app.route('/download')
def download():
    return send_file("../database/data.json", as_attachment=True)

def run_web():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def start_web_server():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()