# Stage 1: Build the application
FROM python:3.9 as builder

# Set the working directory in the builder stage
WORKDIR /app

# Copy only the requirements file to the builder stage
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Create the final image
FROM python:3.9-slim

# Set the working directory in the final image
WORKDIR /app

# Copy the installed Python dependencies from the builder stage
COPY --from=builder /install /usr/local

# Copy the Flask app code to the final image
COPY . .

# Expose the port your Flask app will be running on
EXPOSE 8000

# Set the environment variables for Flask and Gunicorn
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=4 --threads=2 --timeout=60"

# Start the Flask app with Gunicorn when the container is run
CMD ["gunicorn", "app:app"]
