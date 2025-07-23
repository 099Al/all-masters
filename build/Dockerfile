FROM python:3.11-slim

WORKDIR /app

# Copy code and requirements
COPY src /app/src
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add src to PYTHONPATH
ENV PYTHONPATH=/app/src

# Run your app (adjust as needed)
CMD ["python", "src/main.py"]
