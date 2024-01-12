# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Gunicorn will run on
EXPOSE 5000

# Define environment variable for Flask to run in production mode
ENV FLASK_ENV=production

# Run init_db() to initialize the database
RUN python -c 'from app import init_db; init_db()'

# Use Gunicorn to run the Flask app
CMD ["gunicorn", "-w", "4", "app:app", "-b", "0.0.0.0:5000"]
