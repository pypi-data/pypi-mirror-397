FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY test_project ./test_project

# Install dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Default command
CMD ["test-app", "serve", "--port", "8000", "--host", "0.0.0.0"]

