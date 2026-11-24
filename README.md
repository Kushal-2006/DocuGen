# P34 – DocuGen: Technical Documentation Portal

A Flask and SQLite academic project for managing technical documents, generating function documentation and code-change summaries, and restoring previous revisions.

## Run locally

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 and register an account. Create a project and document, edit and save revisions, and use Generate to produce documentation. Copy generated output into your document editor.

## Optional AI
Set OPENAI_API_KEY and optionally OPENAI_MODEL in your shell environment before starting. Without a key, local Python AST analysis and unified diffs are available; these are not LLM outputs. Do not submit confidential code to external APIs without authorization. Set a persistent SECRET_KEY for deployment.

## Testing
Run `python -m pytest --cov=app --cov=services`. GitHub Actions runs tests and builds the Docker image on pushes and pull requests. Deployment, Selenium, SonarQube and Grafana are not configured in this starter. Capture actual screenshots after running the application and CI; illustrative mockups are not evidence of execution.

## Architecture
Browser / Jinja templates → Flask routes → SQLite database; optional OpenAI service. This implementation uses server-rendered HTML rather than React.

## GitHub
Create an empty repository named docugen, then run:
```sh
git init
git add .
git commit -m "Initial DocuGen project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/docugen.git
git push -u origin main
```
