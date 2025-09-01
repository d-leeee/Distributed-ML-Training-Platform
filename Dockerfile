# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose Redis default port (optional, if you run Redis in the container)
# EXPOSE 6379

# Run your main script
CMD ["python", "src/main.py"]