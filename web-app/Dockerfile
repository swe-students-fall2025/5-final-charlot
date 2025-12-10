FROM python:3.13-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

EXPOSE 9000

# Run the application
CMD ["python", "-m", "app.main"]
