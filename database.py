import os
import sqlite3

if sqlite3.threadsafety == 0:
    print("No thread safety!! This will probably cause issues.")

def init_db(filename):
    conn = sqlite3.connect(filename)
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
    conn.close()

# Gets a random problem, given a connection. Returns:
# ((name, description, difficulty), [(input, output, hidden), ...])
# name: str
# description: str, formatted as an html snippet
# difficulty: int
# input: bytes
# output: bytes
# hidden: bool
def get_random(filename):
    conn = sqlite3.connect(f"file:{filename}?mode=ro", uri=True)
    cur = conn.cursor()
    res = cur.execute("""
        SELECT id, name, description, difficulty
        FROM descriptions
        ORDER BY RANDOM()
        LIMIT 1
    """)
    problem = res.fetchone()
    problem_id = problem[0]
    problem_desc = problem[1:]
    res = cur.execute("SELECT input, output, hidden FROM test_cases WHERE id=?", (problem_id,))
    test_cases = res.fetchall()
    conn.close()
    test_cases = [(i.encode(), o.encode(), h) for i,o,h in test_cases]
    return (problem_desc, test_cases)

def import_problems(filename, base_dir):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    for problem_name in os.listdir(base_dir):
        problem_dir = os.path.join(base_dir, problem_name)
        if not os.path.isdir(problem_dir):
            print(f"Problem is not a folder: \"{problem_dir}\"")
            continue

        # Read file and make sure it's not empty / the read worked
        description = ""
        with open(os.path.join(problem_dir, "description.html"), "r") as f:
            description = f.read()
        if description == "":
            print("Empty problem description: \"{problem_path}\"")
            continue

        # Insert problem record
        cursor.execute(
            "INSERT INTO descriptions (name, description, difficulty) VALUES (?, ?, ?)",
            (problem_name, description, 1), # TODO set difficulty...?
        )
        problem_id = cursor.lastrowid

        # Import test cases (both visible and hidden)
        for hidden_flag, input_folder, output_folder in (
            (False, "input", "output"),
            (True, "input_hidden", "output_hidden"),
        ):
            in_dir = os.path.join(problem_dir, input_folder)
            out_dir = os.path.join(problem_dir, output_folder)
            if not os.path.exists(in_dir):
                print(f"Directory not found: \"{in_dir}\"")
                continue

            for filename in os.listdir(in_dir):
                in_path = os.path.join(in_dir, filename)
                out_path = os.path.join(out_dir, filename)

                if not os.path.exists(out_path):
                    print(f"File not found: \"{out_path}\"")
                    continue

                in_text = ""
                with open(in_path, "r") as f:
                    in_text = f.read()
                out_text = ""
                with open(out_path, "r") as f:
                    out_text = f.read()

                cursor.execute(
                    "INSERT INTO test_cases (id, input, output, hidden) VALUES (?, ?, ?, ?)",
                    (problem_id, in_text, out_text, hidden_flag),
                )

        conn.commit()
        print(f"Imported {problem_name}")
    conn.close()

