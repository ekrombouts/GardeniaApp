FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 8501

ENV PYTHONPATH=/app
CMD ["streamlit", "run", "frontend/app.py"]