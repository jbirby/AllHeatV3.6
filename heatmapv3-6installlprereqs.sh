#!/bin/bash

# This bash script will install the necessary libraries required to run the given Python script.

# Update package lists and upgrade the system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python3 and pip3
sudo apt-get install -y python3 python3-pip

# Install required Python libraries
pip3 install pandas folium datetime mgrs folium-plugin-heatmap-withtime python-tk

echo "All required libraries have been installed successfully."

