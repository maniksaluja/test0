#!/bin/bash

# Update and upgrade system
echo "Updating and upgrading system..."
sudo apt update -y
sudo apt upgrade -y

# Install Git
echo "Installing Git..."
sudo apt install git -y

# Install Python and pip
echo "Installing Python and pip..."
sudo apt install python3 -y
sudo apt install python3-pip -y

# Install virtualenv
echo "Installing virtualenv..."
sudo pip3 install virtualenv

# Install Node.js and npm (if needed)
echo "Installing Node.js and npm..."
sudo apt install nodejs -y
sudo apt install npm -y

# Add any other required installations below

# Cleanup
echo "Cleaning up..."
sudo apt autoremove -y
sudo apt clean

echo "System update and essential tools installation completed!"
