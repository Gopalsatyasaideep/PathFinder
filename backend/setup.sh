#!/bin/bash
# Setup script for PathFinder AI Backend

echo "Setting up PathFinder AI Backend..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

echo "Setup complete!"
echo "Run the server with: python main.py"
