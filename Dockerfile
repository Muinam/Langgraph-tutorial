# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if any are needed (none standard needed here, but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies, including JupyterLab to run the notebooks
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir jupyterlab

# Copy the rest of the project files into the container
COPY . .

# Expose port 8888 for Jupyter Lab
EXPOSE 8888

# Command to run Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
