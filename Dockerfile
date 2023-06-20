# Use a base image with Python and necessary dependencies
FROM python:3.9

# Install the required Linux libraries
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code to the container
COPY . .

# Expose the port your Flask app will be running on
EXPOSE 8000

# Set the environment variables for Flask and Gunicorn
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=4 --threads=2 --timeout=60"

# Start the Flask app with Gunicorn when the container is run
CMD ["gunicorn", "app:app"]
