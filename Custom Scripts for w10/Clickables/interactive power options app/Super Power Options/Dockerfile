FROM python:3.11-slim

# Install system dependencies for Tkinter and pystray GUI libs
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-dev \
    libgtk-3-0 \
    libx11-6 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libatk-bridge2.0-0 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libxrender1 \
    libxcb1 \
    libx11-xcb1 \
    libxss1 \
    libxcomposite1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy only the Docker-friendly requirements file and install it
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy remaining app code
COPY . .

# Set display env variable (for GUI forwarding, if any)
ENV DISPLAY=:0

# Run the main Python script
CMD ["python", "main.py"]
