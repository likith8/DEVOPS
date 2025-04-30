# Use a lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all files
COPY . . 

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file into the container
COPY new_to/.env /app/.env


# Install python-dotenv
RUN pip install python-dotenv

# Expose the port Flask runs on
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
