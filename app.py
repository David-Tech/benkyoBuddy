from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import dbSchema
import dbLoad
import re

KANJI_RE = re.compile(r'[\u4E00-\u9FFF]')
KANA_RE = re.compile(r'[\u3040-\u30FF]')
def is_jp(text):
    return bool(KANJI_RE.search(text) or KANA_RE.search(text))


def search(query):
    conn = sqlite3.connect("./instance/jisho.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    fts_sql = """
        SELECT entry_id, 
               (rank * 10) + (
                   CASE 
                       WHEN priorities LIKE '%nf%' THEN 
                           CAST(SUBSTR(priorities, INSTR(priorities, 'nf') + 2, 2) AS INTEGER)
                       ELSE 99 
                   END
               ) as hybrid_score
        FROM jisho_fts 
        WHERE jisho_fts MATCH ? 
        ORDER BY hybrid_score ASC 
        LIMIT 20
        """
    
    fts_param =f'"{query}"*'
    fts_results = cursor.execute(fts_sql, (fts_param,)).fetchall()
    entry_ids = [row['entry_id'] for row in fts_results]

    if not entry_ids:
        conn.close()
        return[]

    placeholders = ', '.join(['?'] * len(entry_ids))

    sql = f"""
    SELECT 
            k.keb AS kanji,
            GROUP_CONCAT(DISTINCT ki.ke_inf) AS kanji_info,
            GROUP_CONCAT(DISTINCT kp.ke_pri) AS kanji_priority,
            r.reb AS reading,
            GROUP_CONCAT(DISTINCT ri.re_inf) AS reading_info,
            GROUP_CONCAT(DISTINCT rp.re_pri) AS reading_priority,
            GROUP_CONCAT(DISTINCT sp.pos) AS part_of_speech,
            GROUP_CONCAT(DISTINCT sg.gloss) AS definitions,
            GROUP_CONCAT(DISTINCT se.ex_text) AS example_sentences
        FROM entry e
        LEFT JOIN k_ele k ON e.id = k.entry_id
        LEFT JOIN k_ele_info ki ON k.id = ki.k_ele_id
        LEFT JOIN k_ele_priority kp ON k.id = kp.k_ele_id
        LEFT JOIN r_ele r ON e.id = r.entry_id
        LEFT JOIN r_ele_info ri ON r.id = ri.r_ele_id
        LEFT JOIN r_ele_priority rp ON r.id = rp.r_ele_id
        LEFT JOIN sense s ON e.id = s.entry_id
        LEFT JOIN sense_pos sp ON s.id = sp.sense_id
        LEFT JOIN sense_gloss sg ON s.id = sg.sense_id
        LEFT JOIN sense_example se ON s.id = se.sense_id
        WHERE e.id IN ({placeholders})
        GROUP BY e.id
        ORDER BY CASE e.id
    """

    for i, entry_id in enumerate(entry_ids):
        sql += f" WHEN {entry_id} THEN {i}"

    sql += " END;"

    results = cursor.execute(sql, entry_ids).fetchall()


    formattedResults= [dict(row) for row in results]
    conn.close()
    return formattedResults
    

app = Flask(__name__)


@app.route('/')
def home():
    query = request.args.get('search', '').strip()

    if query: 
        return redirect(url_for('results_page', query=query))
    return render_template('index.html')


@app.route('/results')
def results_page():
    query = request.args.get('query', '').strip()
    
    if not query:
        return redirect(url_for('home'))
    

    results = search(query)

    if results:
        print(f"Found {len(results)} results. First: {results[0]['kanji'] or results[0]['reading']}")
    else: print("NO results found.")


    return render_template('searchResults.html', results = results, query=query)

if __name__ == '__main__':
    app.run(debug=True)