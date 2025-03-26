#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Installing WebScraper...${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}Installing pip...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-pip
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm python-pip
    else
        echo -e "${RED}Could not install pip. Please install pip manually.${NC}"
        exit 1
    fi
fi

# Create virtual environment (optional)
echo -e "${YELLOW}Do you want to install in a virtual environment? [y/N]${NC}"
read -r use_venv

if [[ $use_venv =~ ^[Yy]$ ]]; then
    # Check for venv module
    python3 -m venv --help &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Installing venv module...${NC}"
        if command -v apt &> /dev/null; then
            sudo apt install -y python3-venv
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-venv
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm python-virtualenv
        fi
    fi

    # Create and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies and package
echo -e "${YELLOW}Installing dependencies...${NC}"
pip3 install requests beautifulsoup4

echo -e "${YELLOW}Installing WebScraper...${NC}"
pip3 install -e .

# Make the script executable
chmod +x src/scraper.py

# Create symbolic link
if [[ $use_venv =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Creating symbolic link in virtual environment...${NC}"
    ln -sf "$(pwd)/src/scraper.py" venv/bin/webscraper
else
    echo -e "${YELLOW}Creating symbolic link in /usr/local/bin...${NC}"
    sudo ln -sf "$(pwd)/src/scraper.py" /usr/local/bin/webscraper
fi

echo -e "${GREEN}Installation complete!${NC}"
echo -e "You can now use the webscraper by running: ${YELLOW}webscraper <url>${NC}"

if [[ $use_venv =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Note: The virtual environment must be activated to use webscraper:${NC}"
    echo -e "source $(pwd)/venv/bin/activate"
fi 