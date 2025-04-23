# Use a base image with Python and tk preinstalled
FROM python:3.11-slim

# Install system dependencies for GUI and pystray to work
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libgl1-mesa-glx \
    libxrandr2 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies, using the Docker-safe version
RUN pip install --no-cache-dir -r requirements-docker.txt

# Entry point
CMD ["python", "main.py"]
