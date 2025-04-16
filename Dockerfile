# Use official Python image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app code
COPY . .

# Expose port (if you're using Flask default port)
EXPOSE 5000

# Command to run the app (adjust if needed)
CMD ["python", "app.py"]
