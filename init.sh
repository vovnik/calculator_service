python makemigration.py
python calculator_run.py &
gunicorn wsgi:app
