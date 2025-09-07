#!/bin/bash

# 🚀 GitHub Upload Script for AI Investment Research Assistant
# This script helps you upload your project to GitHub

set -e  # Exit on any error

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME
if [ -z "$GITHUB_USERNAME" ]; then
    print_error "GitHub username is required."
    exit 1
fi

print_status "Setting up repository for user: $GITHUB_USERNAME"

# Check if we're already in a git repository
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..."
    git init
    print_success "Git repository initialized"
else
    print_warning "Git repository already exists"
fi

# Update README with correct username
print_status "Updating README with your GitHub username..."
if [ -f "README.md" ]; then
    sed -i.bak "s/yourusername/$GITHUB_USERNAME/g" README.md
    rm README.md.bak 2>/dev/null || true
    print_success "README updated with username: $GITHUB_USERNAME"
fi

# Update other files with username
if [ -f "setup.py" ]; then
    sed -i.bak "s/yourusername/$GITHUB_USERNAME/g" setup.py
    rm setup.py.bak 2>/dev/null || true
fi

# Set up git config if not already configured
if [ -z "$(git config --global user.name)" ]; then
    read -p "Enter your full name for Git: " USER_NAME
    git config --global user.name "$USER_NAME"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Enter your email for Git: " USER_EMAIL
    git config --global user.email "$USER_EMAIL"
fi

# Create output directories
print_status "Creating output directories..."
mkdir -p charts reports presentations
print_success "Output directories created"

# Check if files are ready
print_status "Checking project files..."
required_files=("README.md" "requirements.txt" "LICENSE" "investment_advisor/cli.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done
print_success "All required files present"

# Add all files to git
print_status "Adding files to Git..."
git add .

# Check if there are any changes to commit
if git diff --cached --quiet; then
    print_warning "No changes to commit"
else
    # Commit files
    print_status "Creating initial commit..."
    git commit -m "Initial commit: AI Investment Research Assistant v1.0

🤖 Features:
- Natural language CLI interface
- Multi-source financial data integration
- Advanced technical analysis tools
- Strategy backtesting engine
- Professional report generation
- AI-powered task planning

🚀 Ready for production use!"

    print_success "Initial commit created"
fi

# Set main branch
print_status "Setting main branch..."
git branch -M main

# Add remote origin
print_status "Adding GitHub remote..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GITHUB_USERNAME/ai-investment-advisor.git"
print_success "Remote origin added"

# Push to GitHub
print_status "Pushing to GitHub..."
echo
print_warning "You may need to authenticate with GitHub (username/password or token)"
echo

if git push -u origin main; then
    print_success "Successfully pushed to GitHub!"
else
    print_error "Failed to push to GitHub. Please check:"
    echo "  1. Repository exists: https://github.com/$GITHUB_USERNAME/ai-investment-advisor"
    echo "  2. You have correct permissions"
    echo "  3. Your authentication credentials are correct"
    exit 1
fi

# Create and push tags
print_status "Creating release tag..."
git tag -a v1.0.0 -m "Release v1.0.0: Initial public release

🎉 First stable release of AI Investment Research Assistant

Features:
- Natural language investment queries
- Technical analysis and backtesting
- Multi-format report generation
- Professional charts and visualizations
- Session memory and context retention

Installation:
git clone https://github.com/$GITHUB_USERNAME/ai-investment-advisor.git
cd ai-investment-advisor
pip install -r requirements.txt
python investment_advisor/cli.py"

if git push origin v1.0.0; then
    print_success "Release tag v1.0.0 created and pushed"
else
    print_warning "Failed to push tag, but main code is uploaded"
fi

# Final instructions
echo
echo "🎉 SUCCESS! Your repository has been uploaded to GitHub!"
echo
print_success "Repository URL: https://github.com/$GITHUB_USERNAME/ai-investment-advisor"
echo
print_status "Next Steps:"
echo "  1. Visit your repository on GitHub"
echo "  2. Add repository description: 'Sophisticated AI investment research assistant with CLI interface'"
echo "  3. Add topics: python, finance, investment, ai, cli, technical-analysis, backtesting"
echo "  4. Enable Issues and Discussions in Settings"
echo "  5. Create your first GitHub Release from the v1.0.0 tag"
echo "  6. Consider adding a demo GIF or screenshots to README"
echo
print_status "Optional Enhancements:"
echo "  • Set up GitHub Actions (already configured in .github/workflows/)"
echo "  • Enable GitHub Pages for documentation"
echo "  • Add Codecov for test coverage"
echo "  • Submit to awesome-python lists"
echo "  • Share on social media and communities"
echo
print_status "🌟 NEW: Enhanced Access Methods Available!"
echo "  🔗 Gitpod: One-click development environment"
echo "  📓 Google Colab: Interactive notebook demos"
echo "  🚀 Binder: Jupyter environment in browser"
echo "  ⚡ Replit: Instant code execution"
echo "  🐳 Docker: Container-based deployment"
echo "  🔒 Security: CodeQL analysis enabled"
echo "  📊 CI/CD: Multi-platform testing pipeline"
echo
print_success "Happy coding! 🚀"