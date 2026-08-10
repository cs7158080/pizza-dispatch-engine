# pizza-dispatch-engine
Event-driven pizza order and delivery dispatch system built with REST API, message broker, worker service, and database.

## Local development

The system runs under Docker Compose; this section is only for working on the source.
Requires Python 3.12.

```
uv venv --python 3.12
.venv\Scripts\Activate.ps1          # PowerShell; source .venv/bin/activate elsewhere
uv pip install -e ".[dev]"
python -c "import pizza"
```

The package is installed rather than imported from the working directory, so `import pizza`
failing means the install did not happen.
