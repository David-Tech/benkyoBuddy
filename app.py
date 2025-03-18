from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import dbSchema
import dbLoad


def search(query):
    conn = sqlite3.connect("./instance/jisho.db")
    cursor = conn.cursor()
    search = '%' + query + '%'
    param =(search, )
    for row in cursor.execute("""
                    SELECT e.id, k.keb, g.gloss
                    FROM entry AS e
                    JOIN k_ele AS k ON e.id = k.entry_id
                    JOIN sense AS s ON k.entry_id = s.entry_id
                    JOIN sense_gloss AS g ON s.id = g.sense_id
                    WHERE k.keb LIKE ?
                    LIMIT 7;
                """,param ):

        print(row)
    return cursor.fetchall()
    


app = Flask(__name__)



# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)


class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'GET':
        query = request.args.get('search', '')
        return redirect(url_for('results'))
    
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_word():
    if request.method == 'GET':
        query = request.form['query']
        
        
        print(f"Received: {query}")  # Debugging
        
        new_word = Vocabulary(word=word, meaning=meaning)
        db.session.add(new_word)
        db.session.commit()
        print("Word added to the database!")  # Debugging
        return redirect(url_for('home'))
    return render_template('add_word.html')

@app.route('/library')
def view_words():
    words = Vocabulary.query.all()

    return render_template('myLibrary.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)