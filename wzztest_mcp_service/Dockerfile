FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY server.py /app/server.py

ENV HOST=0.0.0.0
ENV PORT=8000
ENV MCP_PATH=/mcp

EXPOSE 8000

CMD ["python", "/app/server.py"]
