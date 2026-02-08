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
    cursor = conn.cursor()
    search = f"%{query}%"

    if is_jp(query):
         orderby_clause = """
        ORDER BY
            CASE
                WHEN k.keb = ? THEN 0
                WHEN r.reb = ? THEN 0
                WHEN k.keb LIKE ? THEN 1
                WHEN r.reb LIKE ? THEN 1
                ELSE 2
            END,

            CASE 
                WHEN k.ke_pri LIKE '%nf%' THEN 
                    CAST(SUBSTR(k.ke_pri, INSTR(k.ke_pri, 'nf') + 2, 2) AS INTEGER)
                
                WHEN r.re_pri LIKE '%nf%' THEN 
                    CAST(SUBSTR(r.re_pri, INSTR(r.re_pri, 'nf') + 2, 2) AS INTEGER)
                ELSE 99
            END,
            
            
            
            
            """

         param = (search, search, search,
        query,
        query,
        search,
        search) 
    else:
        orderby_clause = """        
        ORDER BY
            CASE
                WHEN sg.gloss = ? THEN 0
                WHEN sg.gloss LIKE ? THEN 1
                ELSE 2
            END,

            CASE 
                WHEN k.ke_pri LIKE '%nf%' THEN 
                    CAST(SUBSTR(k.ke_pri, INSTR(k.ke_pri, 'nf') + 2, 2) AS INTEGER)
                
                WHEN r.re_pri LIKE '%nf%' THEN 
                    CAST(SUBSTR(r.re_pri, INSTR(r.re_pri, 'nf') + 2, 2) AS INTEGER)
                ELSE 99
            
            
            """

        param =( search, search, search, query, search)

    sql= """
                SELECT 
                    k.keb AS kanji,
 GROUP_CONCAT(DISTINCT ki.ke_inf)  AS kanji_info,
                    GROUP_CONCAT(DISTINCT kp.ke_pri)  AS kanji_priority,
                    r.reb AS reading,
                    GROUP_CONCAT(DISTINCT ri.re_inf) AS reading_info,
                    GROUP_CONCAT(DISTINCT rp.re_pri) AS reading_priority,
                    GROUP_CONCAT(DISTINCT sp.pos) AS part_of_speech,
                    GROUP_CONCAT(DISTINCT sg.gloss)  AS definitions,
                    GROUP_CONCAT(DISTINCT se.ex_text)  AS example_sentences
                    FROM k_ele k
                    JOIN entry e ON k.entry_id = e.id
                    LEFT JOIN k_ele_info ki ON k.id = ki.k_ele_id
                    LEFT JOIN k_ele_priority kp ON k.id = kp.k_ele_id
                    LEFT JOIN r_ele r ON e.id = r.entry_id
                    LEFT JOIN r_ele_info ri ON r.id = ri.r_ele_id
                    LEFT JOIN r_ele_priority rp ON r.id = rp.r_ele_id
                    LEFT JOIN sense s ON e.id = s.entry_id
                    LEFT JOIN sense_pos sp ON s.id = sp.sense_id
                    LEFT JOIN sense_gloss sg ON s.id = sg.sense_id
                    LEFT JOIN sense_example se ON s.id = se.sense_id
                    WHERE k.keb LIKE ? OR r.reb LIKE ? or sg.gloss LIKE ?
                    GROUP BY e.id

        """

    sql += orderby_clause
    sql += "\n LIMIT 7;"
    print(sql)

    results = cursor.execute(sql,param).fetchall()
    columns = [description[0] for description in cursor.description]
    formattedResults = []
    formattedResults= [dict(zip(columns, row)) for row in results]
    conn.close()
    return formattedResults
    

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
    print("First result:")
    print(results[0])
    return render_template('searchResults.html', results = results)

if __name__ == '__main__':
    app.run(debug=True)