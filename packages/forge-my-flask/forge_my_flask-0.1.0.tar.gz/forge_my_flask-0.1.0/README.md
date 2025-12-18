# Forge My Flask (FMF)

Forge My Flask (FMF) is a lightweight CLI tool that scaffolds Flask projects in seconds.  
It helps you quickly bootstrap Flask web applications or Flask API projects using a clean and practical project structure.

FMF is designed to be beginner friendly while still following patterns used in real Flask projects.

---

## Features

- Create Flask web applications with templates and static files
- Create Flask API projects using blueprints
- Clean and consistent project structure
- No configuration required
- Works on Windows, Linux, and macOS
- Simple interactive CLI

---

## Project Types

### Web App

Generates a Flask project with:
- `app.py`
- `templates/`
- `static/`
- `requirements.txt`

Best suited for traditional Flask applications that use HTML templates.

### API

Generates a Flask API project with:
- Application factory pattern
- Blueprint based routing
- Example health endpoint
- Utility helpers for JSON responses
- `requirements.txt`

Best suited for REST APIs and backend services.

---

## Installation

PyPI release coming soon.

For now, clone the repository:

```bash
git clone https://github.com/Sparkleeop/Forge-my-FLASK.git
cd forge-my-flask
````

Run the CLI:

```bash
python app.py
```

---

## Usage

When you start FMF, you will be prompted to select a project type:

```
Forge My Flask (FMF)

1. API Project
2. WebApp Project
```

Follow the prompts and enter a project name. FMF will generate the project structure automatically.

---

## Example Output

### Web App Structure

```
my_web_app/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    └── style.css
```

### API Structure

```
my_api/
├── app.py
├── config.py
├── requirements.txt
├── routes/
│   ├── __init__.py
│   └── health.py
└── utils/
    └── response.py
```

---

## Why FMF

Flask provides flexibility, but that flexibility often leads to inconsistent project layouts and repeated boilerplate.

FMF solves this by providing a simple and consistent starting point that can be extended as projects grow.

---

## Roadmap

Planned improvements include:

* Non interactive CLI commands
* Optional database setup
* Authentication templates
* Environment based configuration

---

## Contributing

Contributions are welcome.

If you find a bug or have a suggestion, feel free to open an issue or submit a pull request.

---

## License

MIT License

---

## Author

Built by Sparklee