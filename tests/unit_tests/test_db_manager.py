import os
import tempfile
import shutil
import database
import pathlib

TEMP_DIR = None
DB_PATH = None

def setup_db():
    global TEMP_DIR, DB_PATH
    TEMP_DIR = tempfile.mkdtemp()
    DB_PATH = os.path.join(TEMP_DIR, "test_problems.db")

    desc_path = os.path.join(TEMP_DIR, "hello_world")
    pathlib.Path(desc_path).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(desc_path, "description.html"), "w") as f:
        f.write("<h1>Hello World Problem</h1><p>Print 'Hello World'.</p>")

    input_path = os.path.join(TEMP_DIR,"hello_world", "input")
    pathlib.Path(input_path).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(input_path, "case1.txt"), "w") as f:
        f.write("") 

    output_path = os.path.join(TEMP_DIR,"hello_world", "output")
    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(output_path, "case1.txt"), "w") as f:
        f.write("Hello World\n")

    database.init_db(DB_PATH)
    database.import_problems(DB_PATH, TEMP_DIR)

def remove_db():
    global TEMP_DIR
    if TEMP_DIR and os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        TEMP_DIR = None
