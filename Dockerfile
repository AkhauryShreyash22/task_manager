FROM python:3.11

WORKDIR /app

COPY tasks/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tasks/ .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
