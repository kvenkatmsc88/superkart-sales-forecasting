#!/bin/bash
# Builds and runs the SuperKart backend (Flask) and frontend (Streamlit) as separate containers
# connected through a user-defined Docker network. Run from the repository root: bash start_app.sh
set -e

NETWORK=superkart-net

# Create the Docker network (ignore the error if it already exists)
docker network create $NETWORK 2>/dev/null || true

# Remove old containers if they exist
docker rm -f superkart-backend superkart-frontend 2>/dev/null || true

# Build and run the backend container (Flask API on port 7860)
docker build -t superkart-backend ./backend_files
docker run -d --name superkart-backend --network $NETWORK -p 7860:7860 superkart-backend

# Build and run the frontend container (Streamlit UI on port 8501)
docker build -t superkart-frontend ./frontend_files
docker run -d --name superkart-frontend --network $NETWORK -p 8501:8501 \
    -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

# Check that the frontend can reach the backend through the Docker network.
# In some GitHub Codespaces, traffic between containers on a user-defined network is blocked
# (requests time out). In that case, run the frontend on the host network and reach the
# backend through its published port 7860 instead.
sleep 5
if ! docker exec superkart-frontend python -c "import requests; requests.get('http://superkart-backend:7860', timeout=5)" 2>/dev/null; then
    echo "Backend not reachable over $NETWORK - restarting the frontend on the host network"
    docker rm -f superkart-frontend
    docker run -d --name superkart-frontend --network host \
        -e BACKEND_URL=http://localhost:7860 superkart-frontend
fi

docker ps
echo "Backend  -> port 7860 | Frontend -> port 8501 (see the Ports tab of the Codespace)"
