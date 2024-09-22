# Step 1: Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port that the app will run on
EXPOSE 8000

# Set environment variables from .env file
ENV DEV_FRONTEND_URL=http://127.0.0.1:8000
ENV SQLALCHEMY_DATABASE_URL="sqlite:///./myapi.db"
ENV ACCESS_TOKEN_EXPIRE_MINUTES=60
ENV SMTP_HOST="smtp.gmail.com"
ENV SMTP_PORT=587
ENV SMTP_USERNAME="YOUR_EMAIL@gmail.com"
ENV SMTP_PASSWORD="YOUR_SMTP_PASSWORD"

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
