FROM quay.io/biocontainers/plink2:2.0.0--h9f5acd7_0

# Install Python and pip via conda (if not already present)
RUN conda install python=3.10 pip -y

# Install Python dependencies
RUN pip install --no-cache-dir requests pandas matplotlib pytest

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Ensure script is executable
RUN chmod +x crohn_pipeline.py

# Default command
CMD ["python", "crohn_pipeline.py"]
