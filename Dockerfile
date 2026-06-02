FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn httpx pandas plotly streamlit
COPY app.py /app/
# 使用 8000 port
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "6"]