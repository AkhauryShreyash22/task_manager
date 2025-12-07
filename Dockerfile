FROM python:3.11

WORKDIR /app

COPY tasks/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tasks/ .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
