from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import dbSchema
import dbLoad



def search(query):
    conn = sqlite3.connect("./instance/jisho.db")
    cursor = conn.cursor()
    search = '%' + query + '%'
    param =(search, )
    for row in cursor.execute("""
                    SELECT *,
                              GROUP_CONCAT(DISTINCT k.keb ORDER BY k.keb),
                              GROUP_CONCAT(DISTINCT s.id ORDER BY s.id),
                              GROUP_CONCAT(DISTINCT g.gloss ORDER BY g.gloss)
                    FROM entry AS e
                    JOIN k_ele AS k ON e.id = k.entry_id
                    JOIN sense AS s ON k.entry_id = s.entry_id
                    JOIN sense_gloss AS g ON s.id = g.sense_id
                    WHERE k.keb LIKE ?
                    GROUP BY e.id
                    LIMIT 7;
                """,param ):

        print(row)
    return cursor.fetchall()
    

app = Flask(__name__)


@app.route('/')
def home():
    query = request.args.get('search', '')

    if query: 
        print(query)
        return redirect(url_for('results_page', query=query))
    return render_template('index.html')


@app.route('/results')
def results_page():
    query = request.args.get('query', '')
    
    results = search(query)
    print(results)
    return render_template('searchResults.html', results = results)

if __name__ == '__main__':
    app.run(debug=True)