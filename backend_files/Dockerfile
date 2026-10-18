# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install the dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code and the serialized model
COPY . .

# Expose the port on which the Flask API runs
EXPOSE 7860

# Start the Flask app with gunicorn: 4 workers, bound to port 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
