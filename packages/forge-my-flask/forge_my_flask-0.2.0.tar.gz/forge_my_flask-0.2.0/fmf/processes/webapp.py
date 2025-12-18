import time
import subprocess
from pathlib import Path

def init_webapp_project(project_name=None):
    
    if project_name == None:
        project_name = input("Enter project name: ")
    project_path = Path(project_name)

    print(f"Starting base template installation... for the project {project_name}")
    time.sleep(3)

    Path(project_name).mkdir(exist_ok=True)
    print("Installing main file and boilerplate code...")
    time.sleep(1)
    
    app_file = project_path / "app.py"

    app_file.write_text(
"""from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

"""
    )

    print("app.py Installed ✔")

    Path(project_path / "templates").mkdir(exist_ok=True)

    index_file = project_path / "templates" / "index.html"

    index_file.write_text(
"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flask App</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Flask is running 🚀</h1>
    <p>Edit this file to get started.</p>
</body>
</html>
""",encoding="utf-8"
    )

    print("templates/index.html Installed ✔")

    Path(project_path / "static").mkdir(exist_ok=True)

    style_file = project_path / "static" / "style.css"

    style_file.write_text(
"""body {
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: white;
    text-align: center;
    padding-top: 50px;
}
"""
    )
    print("static/style.css Installed ✔")

    Path(project_path).mkdir(exist_ok=True)
    requirements_file = project_path / "requirements.txt"
    requirements_file.write_text(
"""flask
"""
    )
    print("requirements.txt Initialized ✔")
    time.sleep(2)

    subprocess.run(
        ["pip", "install", "-r", "requirements.txt"],
        cwd=project_path
    )

    time.sleep(2)

    print("Boilerplate Installed ✔")
    print("Done!")
