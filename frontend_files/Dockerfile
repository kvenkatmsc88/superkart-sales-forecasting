# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the Streamlit app
COPY . .

# URL of the backend container on the shared Docker network (can be overridden at runtime)
ENV BACKEND_URL=http://superkart-backend:7860

# Expose the Streamlit port
EXPOSE 8501

# Run Streamlit. CORS/XSRF protection is disabled so file uploads work behind the Codespaces port-forwarding proxy
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false", "--server.enableCORS=false"]
