import sqlite3
import os
import tempfile
import shutil

TEMP_DIR = None
DB_PATH = None

def init_db(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            difficulty INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER,
            input TEXT,
            output TEXT,
            hidden BOOLEAN,
            FOREIGN KEY (id) REFERENCES descriptions(id)
        )
    """)

    conn.commit()

def create_test_problem(conn, temp_dir):
    cursor = conn.cursor()

    desc_path = os.path.join(temp_dir, "description.html")
    with open(desc_path, "w") as f:
        f.write("<h1>Hello World Problem</h1><p>Print 'Hello World'.</p>")

    input_path = os.path.join(temp_dir, "input.txt")
    with open(input_path, "w") as f:
        f.write("") 

    output_path = os.path.join(temp_dir, "output.txt")
    with open(output_path, "w") as f:
        f.write("Hello World\n")

    cursor.execute(
        "INSERT INTO descriptions (name, description, difficulty) VALUES (?, ?, ?)",
        ("Hello World", desc_path, 1)
    )
    problem_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO test_cases (id, input, output, hidden) VALUES (?, ?, ?, ?)",
        (problem_id, input_path, output_path, False)
    )

    conn.commit()


def setup_db():
    global TEMP_DIR, DB_PATH
    TEMP_DIR = tempfile.mkdtemp()
    DB_PATH = os.path.join(TEMP_DIR, "test_problems.db")

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    create_test_problem(conn, TEMP_DIR)
    conn.close()

def remove_db():
    global TEMP_DIR
    if TEMP_DIR and os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        TEMP_DIR = None
