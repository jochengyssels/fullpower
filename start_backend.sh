#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Path to your virtual environment and project
VENV_PATH="$HOME/fullpower/venv"
PROJECT_PATH="$HOME/fullpower"

# Function to open browser after a delay
open_browser() {
    sleep 3 # Wait for the server to start
    xdg-open http://localhost:8000/docs
    echo -e "${BLUE}Swagger UI opened in your browser${NC}"
}

# Change to project directory
cd "$PROJECT_PATH"
echo -e "${GREEN}Changed to project directory: $PROJECT_PATH${NC}"

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Check if virtual environment was activated successfully
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}Virtual environment activated: $VIRTUAL_ENV${NC}"
else
    echo -e "\033[0;31mFailed to activate virtual environment at $VENV_PATH\033[0m"
    exit 1
fi

# Open browser in the background
echo -e "${GREEN}Starting browser in 3 seconds...${NC}"
open_browser &

# Start the FastAPI application
echo -e "${GREEN}Starting FastAPI application...${NC}"
echo -e "${BLUE}API documentation will be available at: http://localhost:8000/docs${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
python main.py

# This will execute when the user presses Ctrl+C
echo -e "${GREEN}Shutting down...${NC}"