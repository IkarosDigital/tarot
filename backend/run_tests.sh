#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

echo -e "${BLUE}Setting up test environment...${NC}"

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo -e "${BLUE}Installing test requirements...${NC}"
pip install -r requirements-test.txt

# Run tests with coverage
echo -e "${BLUE}Running tests...${NC}"
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Check the exit status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    echo -e "${BLUE}Coverage report has been generated in htmlcov/index.html${NC}"
else
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
fi

# Deactivate virtual environment
deactivate
