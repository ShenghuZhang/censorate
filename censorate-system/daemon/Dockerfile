FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy skill manager
COPY skill_manager.py .

# Default command - runs in server mode (webhook-driven)
CMD ["python", "skill_manager.py", "--server"]
