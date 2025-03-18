import sqlite3

# Connect to SQLite database (or create if not exists)
conn = sqlite3.connect("./instance/jisho.db")
cursor = conn.cursor()

# Create tables (same schema as discussed earlier)
cursor.executescript("""
 CREATE TABLE IF NOT EXISTS entry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ent_seq INTEGER UNIQUE NOT NULL
    );

        CREATE TABLE IF NOT EXISTS k_ele (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            keb TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entry(id) ON DELETE CASCADE
        );

            CREATE TABLE IF NOT EXISTS k_ele_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                k_ele_id INTEGER NOT NULL,
                ke_inf TEXT,
                FOREIGN KEY (k_ele_id) REFERENCES k_ele(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS k_ele_priority (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                k_ele_id INTEGER NOT NULL,
                ke_pri TEXT,
                FOREIGN KEY (k_ele_id) REFERENCES k_ele(id) ON DELETE CASCADE
            );

        CREATE TABLE IF NOT EXISTS r_ele (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            reb TEXT NOT NULL,
            re_nokanji INTEGER DEFAULT 0 CHECK (re_nokanji IN (0,1)),
            FOREIGN KEY (entry_id) REFERENCES entry(id) ON DELETE CASCADE
        );

            CREATE TABLE IF NOT EXISTS r_ele_restriction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                r_ele_id INTEGER NOT NULL,
                re_restr TEXT,
                FOREIGN KEY (r_ele_id) REFERENCES r_ele(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS r_ele_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                r_ele_id INTEGER NOT NULL,
                re_inf TEXT,
                FOREIGN KEY (r_ele_id) REFERENCES r_ele(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS r_ele_priority (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                r_ele_id INTEGER NOT NULL,
                re_pri TEXT,
                FOREIGN KEY (r_ele_id) REFERENCES r_ele(id) ON DELETE CASCADE
            );

        CREATE TABLE IF NOT EXISTS sense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entry(id) ON DELETE CASCADE
        );

            CREATE TABLE IF NOT EXISTS sense_stagk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                stagk TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_stagr (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                stagr TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_pos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                pos TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_xref (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                xref TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_ant (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                ant TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_field (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                field TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_misc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                misc TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_s_inf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                s_inf TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_lsource (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                lsource TEXT DEFAULT NULL,
                xml_lang TEXT DEFAULT 'eng',
                ls_type TEXT DEFAULT NULL,
                ls_wasei INTEGER DEFAULT 0 CHECK (ls_wasei IN (0,1)),
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_dial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                dial TEXT,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_gloss (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                gloss TEXT DEFAULT NULL,
                xml_lang TEXT DEFAULT 'eng',
                g_gend TEXT DEFAULT NULL,
                g_type TEXT DEFAULT NULL,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_example (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sense_id INTEGER NOT NULL,
                ex_srce TEXT DEFAULT NULL,
                ex_text TEXT DEFAULT NULL,
                FOREIGN KEY (sense_id) REFERENCES sense(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sense_example_sent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                example_id INTEGER NOT NULL,
                ex_sent TEXT,
                FOREIGN KEY (example_id) REFERENCES sense_example(id) ON DELETE CASCADE
        );
"""
)

# Commit and close connection
conn.commit()
conn.close()

print("Database tables created successfully!")



