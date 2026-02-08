import sqlite3
import xml.etree.ElementTree as ET

# Connect to SQLite
conn = sqlite3.connect("./instance/jisho.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM entry")
count = cursor.fetchone()[0]

if count > 0:
    print("Data already uploaded")
    conn.close()

else:

    # Load XML File
    tree = ET.parse("JMdict_e.xml")  # Replace with your actual XML file path
    root = tree.getroot()

    # Iterate over each entry in the XML
    for entry in root.findall("entry"):
        ent_seq = entry.find("ent_seq").text

        # Insert into entry table
        cursor.execute("INSERT INTO entry (ent_seq) VALUES (?)", (ent_seq,))
        entry_id = cursor.lastrowid  # Get last inserted ID

        # Process k_ele elements
        for k_ele in entry.findall("k_ele"):
            keb = k_ele.find("keb").text
            cursor.execute("INSERT INTO k_ele (entry_id, keb) VALUES (?, ?)", (entry_id, keb))
            k_ele_id = cursor.lastrowid

            for ke_inf in k_ele.findall("ke_inf"):
                cursor.execute("INSERT INTO k_ele_info (k_ele_id, ke_inf) VALUES (?, ?)", (k_ele_id, ke_inf.text))

            for ke_pri in k_ele.findall("ke_pri"):
                cursor.execute("INSERT INTO k_ele_priority (k_ele_id, ke_pri) VALUES (?, ?)", (k_ele_id, ke_pri.text))

        # Process r_ele elements
        for r_ele in entry.findall("r_ele"):
            reb = r_ele.find("reb").text
            re_nokanji = 1 if r_ele.find("re_nokanji") is not None else 0  # Convert boolean flag
            cursor.execute("INSERT INTO r_ele (entry_id, reb, re_nokanji) VALUES (?, ?, ?)", (entry_id, reb, re_nokanji))
            r_ele_id = cursor.lastrowid

            for re_restr in r_ele.findall("re_restr"):
                cursor.execute("INSERT INTO r_ele_restriction (r_ele_id, re_restr) VALUES (?, ?)", (r_ele_id, re_restr.text))

            for re_inf in r_ele.findall("re_inf"):
                cursor.execute("INSERT INTO r_ele_info (r_ele_id, re_inf) VALUES (?, ?)", (r_ele_id, re_inf.text))

            for re_pri in r_ele.findall("re_pri"):
                cursor.execute("INSERT INTO r_ele_priority (r_ele_id, re_pri) VALUES (?, ?)", (r_ele_id, re_pri.text))

        # Process sense elements
        for sense in entry.findall("sense"):
            cursor.execute("INSERT INTO sense (entry_id) VALUES (?)", (entry_id,))
            sense_id = cursor.lastrowid

            for stagk in sense.findall("stagk"):
                cursor.execute("INSERT INTO sense_stagk (sense_id, stagk) VALUES (?, ?)", (sense_id, stagk.text))

            for stagr in sense.findall("stagr"):
                cursor.execute("INSERT INTO sense_stagr (sense_id, stagr) VALUES (?, ?)", (sense_id, stagr.text))

            for pos in sense.findall("pos"):
                cursor.execute("INSERT INTO sense_pos (sense_id, pos) VALUES (?, ?)", (sense_id, pos.text))

            for xref in sense.findall("xref"):
                cursor.execute("INSERT INTO sense_xref (sense_id, xref) VALUES (?, ?)", (sense_id, xref.text))

            for ant in sense.findall("ant"):
                cursor.execute("INSERT INTO sense_ant (sense_id, ant) VALUES (?, ?)", (sense_id, ant.text))

            for field in sense.findall("field"):
                cursor.execute("INSERT INTO sense_field (sense_id, field) VALUES (?, ?)", (sense_id, field.text))

            for misc in sense.findall("misc"):
                cursor.execute("INSERT INTO sense_misc (sense_id, misc) VALUES (?, ?)", (sense_id, misc.text))

            for s_inf in sense.findall("s_inf"):
                cursor.execute("INSERT INTO sense_s_inf (sense_id, s_inf) VALUES (?, ?)", (sense_id, s_inf.text))

            for lsource in sense.findall("lsource"):
                if lsource.text:  # Only insert if lsource has text
                    xml_lang = lsource.get("xml:lang", "eng")  # Default "eng"
                    ls_type = lsource.get("ls_type", None)
                    ls_wasei = 1 if lsource.get("ls_wasei") is not None else 0  # Convert boolean flag

                    cursor.execute("INSERT INTO sense_lsource (sense_id, lsource, xml_lang, ls_type, ls_wasei) VALUES (?, ?, ?, ?, ?)",
                                (sense_id, lsource.text, xml_lang, ls_type, ls_wasei))

            for dial in sense.findall("dial"):
                cursor.execute("INSERT INTO sense_dial (sense_id, dial) VALUES (?, ?)", (sense_id, dial.text))

            for gloss in sense.findall("gloss"):
                gloss_text = gloss.text if gloss.text else None  # Allow NULL gloss
                xml_lang = gloss.get("xml:lang", "eng")  # Default "eng"
                g_gend = gloss.get("g_gend", None)
                g_type = gloss.get("g_type", None)

                cursor.execute("INSERT INTO sense_gloss (sense_id, gloss, xml_lang, g_gend, g_type) VALUES (?, ?, ?, ?, ?)",
                            (sense_id, gloss_text, xml_lang, g_gend, g_type))
                gloss_id = cursor.lastrowid

                for pri in gloss.findall("pri"):
                    cursor.execute("INSERT INTO sense_gloss_priority (gloss_id, pri) VALUES (?, ?)", (gloss_id, pri.text))

            # Insert example sentences
            for example in sense.findall("example"):
                ex_srce = example.find("ex_srce").text if example.find("ex_srce") is not None else None
                ex_text = example.find("ex_text").text if example.find("ex_text") is not None else None
                cursor.execute("INSERT INTO sense_example (sense_id, ex_srce, ex_text) VALUES (?, ?, ?)", (sense_id, ex_srce, ex_text))
                example_id = cursor.lastrowid

                for ex_sent in example.findall("ex_sent"):
                    cursor.execute("INSERT INTO sense_example_sent (example_id, ex_sent) VALUES (?, ?)", (example_id, ex_sent.text))

    # Commit and close
    print("Building FTS")
    cursor.execute("DELETE FROM jisho_fts;")
    cursor.execute("""

    INSERT INTO jisho_fts(entry_id, kanji, reading, definitions, priorities)
        SELECT e.id,
            (SELECT GROUP_CONCAT(keb, ' ') FROM k_ele WHERE entry_id = e.id),
            (SELECT GROUP_CONCAT(reb, ' ') FROM r_ele WHERE entry_id = e.id),
            (SELECT GROUP_CONCAT(gloss, ' ') FROM sense_gloss sg 
                JOIN sense s ON sg.sense_id = s.id WHERE s.entry_id = e.id),
            (SELECT GROUP_CONCAT(ke_pri, ' ') FROM k_ele_priority kp 
                JOIN k_ele k ON kp.k_ele_id = k.id WHERE k.entry_id = e.id)
        FROM entry e;
                   
    """)
    
    conn.commit()
    cursor.execute("VACUUM;")
    conn.close()

    print("XML data & FTS successfully inserted into SQLite!")


