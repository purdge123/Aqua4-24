# Use a Python base image with Debian Buster
FROM python:3.8-buster

# Update and upgrade packages
RUN apt-get update && \
    apt-get upgrade -y

# Install system dependencies
RUN apt-get install -y \
    build-essential \
    git \
    unzip \
    openjdk-11-jdk \
    wget \
    zlib1g-dev \
    libncurses5-dev \
    libbz2-dev \
    liblzma-dev \
    libffi-dev \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Buildozer
RUN pip install buildozer

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python packages
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the rest of your application code to the container
COPY . /app/

# Specify the command to build the APK
CMD ["buildozer", "android", "debug"]
