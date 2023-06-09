export ENVIRONMENT=dev
uvicorn application.app:app --host 0.0.0.0 --port 6500 --reload