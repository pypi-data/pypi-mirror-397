#!/bin/bash

# YouTube Transcript Curator (YTC) Setup Script
# Automates environment setup and dependency installation

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}YouTube Transcript Curator - Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check Python version
echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.12 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.10"

if [[ $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc) -eq 1 ]]; then
    echo -e "${RED}❌ Python version $PYTHON_VERSION is too old${NC}"
    echo "Required: Python $REQUIRED_VERSION or higher"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Step 2: Create virtual environment
echo -e "${YELLOW}Step 2: Creating virtual environment...${NC}"
if [ -d ".venv" ]; then
    echo -e "${YELLOW}→ Virtual environment already exists${NC}"
else
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Step 3: Activate virtual environment
echo -e "${YELLOW}Step 3: Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 4: Upgrade pip
echo -e "${YELLOW}Step 4: Upgrading pip...${NC}"
pip install --quiet --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Step 5: Install dependencies
echo -e "${YELLOW}Step 5: Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 6: Create data directories
echo -e "${YELLOW}Step 6: Creating data directories...${NC}"
mkdir -p data/input
mkdir -p data/output/metadata
mkdir -p data/output/transcripts
mkdir -p data/output/formatted
mkdir -p data/output/logs

# Create .gitkeep files
touch data/input/.gitkeep
touch data/output/metadata/.gitkeep
touch data/output/transcripts/.gitkeep
touch data/output/formatted/.gitkeep
touch data/output/logs/.gitkeep

echo -e "${GREEN}✓ Data directories created${NC}"
echo ""

# Step 7: Create .env file if it doesn't exist
echo -e "${YELLOW}Step 7: Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}→ Created .env from .env.example${NC}"
    echo -e "${YELLOW}→ Edit .env to add API keys if needed${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi
echo ""

# Step 8: Verify installation
echo -e "${YELLOW}Step 8: Verifying installation...${NC}"
echo -n "  Checking Click... "
python -c "import click; print('OK')" && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

echo -n "  Checking youtube-transcript-api... "
python -c "import youtube_transcript_api; print('OK')" && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

echo -n "  Checking yt-dlp... "
python -c "import yt_dlp; print('OK')" && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

echo -n "  Checking PyYAML... "
python -c "import yaml; print('OK')" && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

echo ""

# Step 9: Setup tab completion
echo -e "${YELLOW}Step 9: Setting up tab completion...${NC}"
if bash scripts/setup-completion.sh 2>&1 | grep -q "Tab completion setup complete"; then
    echo -e "${GREEN}✓ Tab completion configured${NC}"
else
    echo -e "${YELLOW}→ Tab completion setup skipped or failed${NC}"
fi
echo ""

# Step 10: Display next steps
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete! ✓${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. Reload your shell configuration:"
echo -e "   ${YELLOW}source ~/.zshrc${NC}  # or ~/.bash_profile for bash"
echo ""
echo "2. (Optional) Add Anthropic API key to .env:"
echo -e "   ${YELLOW}export ANTHROPIC_API_KEY=your_key_here${NC}"
echo ""
echo "3. Test the tool:"
echo -e "   ${YELLOW}ytc --help${NC}"
echo -e "   ${YELLOW}ytc <TAB>${NC}  # Try tab completion!"
echo ""
echo "4. Extract your first transcript:"
echo -e "   ${YELLOW}ytc fetch 'https://www.youtube.com/watch?v=VIDEO_ID'${NC}"
echo ""
echo -e "${BLUE}Output will be saved to:${NC}"
echo "  - data/output/metadata/"
echo "  - data/output/transcripts/"
echo ""
echo -e "${BLUE}For help:${NC}"
echo "  - See: development/prerequisites.md"
echo "  - See: README.md"
echo ""
