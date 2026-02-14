#!/bin/bash
# Setup script for Crohn's Disease Population Genetics Pipeline

echo "Setting up Crohn's Disease Pipeline..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if PLINK2 is installed
if ! command -v plink2 &> /dev/null; then
    echo "PLINK2 is not installed. Please download it from:"
    echo "https://www.cog-genomics.org/plink/2.0/"
    echo "and ensure it's in your PATH."
    exit 1
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! To run the pipeline:"
echo "  source venv/bin/activate"
echo "  python crohn_pipeline.py"
