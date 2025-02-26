from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    words = Vocabulary.query.all() 
    return render_template('index.html', words=words)

@app.route('/add', methods=['GET', 'POST'])
def add_word():
    if request.method == 'POST':
        word = request.form['word']
        meaning = request.form['meaning']
        
        print(f"Received: {word} - {meaning}")  # Debugging
        
        new_word = Vocabulary(word=word, meaning=meaning)
        db.session.add(new_word)
        db.session.commit()
        print("Word added to the database!")  # Debugging
        return redirect(url_for('home'))
    return render_template('add_word.html')

@app.route('/view')
def view_words():
    words = Vocabulary.query.all()
    return str([(word.word, word.meaning) for word in words])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)