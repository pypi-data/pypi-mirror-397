import time
import subprocess
from pathlib import Path

def init_api_project():
    project_name = input("Enter your main directory name/project name: ")
    project_path = Path(project_name)

    print(f"Starting base template installation... for the project {project_name}")
    time.sleep(3)

    Path(project_name).mkdir(exist_ok=True)
    print("Installing main file and boilerplate code...")
    time.sleep(1)

    # APP.PY INSTALL
    
    app_file = project_path / "app.py"

    app_file.write_text(
"""from flask import Flask
from routes.health import health_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(health_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
"""
    )

    print("app.py Installed ✔")

    ## CONFIG.PY INSTALL

    config_file = project_path / "config.py"

    config_file.write_text(
"""class Config:
    DEBUG = True
"""
    )

    print("config.py Installed ✔")

    ## HEALTH.PY INSTALL

    Path(project_path / "routes").mkdir(exist_ok=True)

    health_file = project_path / "routes" / "health.py"

    health_file.write_text(
"""from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "flask-api"
    })
""",encoding="utf-8"
    )

    print("routes/health.py Installed ✔")

    ## __INIT__.PY INSTALL

    Path(project_path / "routes").mkdir(exist_ok=True)

    init_routes_file = project_path / "routes" / "__init__.py"

    init_routes_file.write_text(
"""

""",encoding="utf-8"
    )

    print("routes/__init__.py Installed ✔")

    ## RESPONSE.PY INSTALL

    Path(project_path / "utils").mkdir(exist_ok=True)

    response_file = project_path / "utils" / "response.py"

    response_file.write_text(
"""from flask import jsonify

def success(data=None, message="success", status=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status

def error(message="error", status=400):
    return jsonify({
        "success": False,
        "message": message
    }), status
"""
    )
    print("utils/response.py Installed ✔")

    ## REQUIREMENTS.TXT INSTALL

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
