#!/bin/bash

# Script to make the casino-scanner repository private
# Requires GitHub CLI (gh) to be installed and authenticated

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

echo ""
print_header "🔒 Make Repository Private"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed"
    echo ""
    print_info "Install it using:"
    echo "  • Ubuntu/Debian: sudo apt install gh"
    echo "  • macOS: brew install gh"
    echo "  • Other: https://cli.github.com/manual/installation"
    echo ""
    exit 1
fi

print_status "GitHub CLI is installed"

# Check if authenticated
if ! gh auth status &> /dev/null; then
    print_warning "Not authenticated with GitHub CLI"
    print_info "Attempting to authenticate..."
    echo ""
    
    if gh auth login; then
        print_status "Authentication successful"
    else
        print_error "Authentication failed"
        echo ""
        print_info "Please run: gh auth login"
        exit 1
    fi
else
    print_status "Already authenticated with GitHub"
fi

# Get current repository info
repo_owner="dickbags21"
repo_name="casino-scanner"
full_repo="${repo_owner}/${repo_name}"

echo ""
print_info "Repository: ${full_repo}"
echo ""

# Check current visibility
current_visibility=$(gh repo view "$full_repo" --json isPrivate -q '.isPrivate')

if [ "$current_visibility" = "true" ]; then
    print_status "Repository is already private!"
    echo ""
    exit 0
fi

print_warning "Repository is currently public"
echo ""

# Confirm action
print_warning "This action will:"
echo "  • Make the repository private"
echo "  • Only you and invited collaborators can access it"
echo "  • The repository won't appear in search results"
echo "  • Any forks will be deleted"
echo ""

read -p "Do you want to continue? (yes/no): " -r confirm
echo ""

if [[ ! "$confirm" =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Operation cancelled"
    exit 0
fi

# Make repository private
print_info "Making repository private..."
echo ""

if gh repo edit "$full_repo" --visibility private; then
    echo ""
    print_status "Repository is now private! 🎉"
    echo ""
    
    # Verify
    new_visibility=$(gh repo view "$full_repo" --json isPrivate -q '.isPrivate')
    if [ "$new_visibility" = "true" ]; then
        print_status "Verified: Repository visibility is private"
    else
        print_warning "Could not verify repository visibility"
    fi
    
    echo ""
    print_header "✅ Next Steps"
    echo ""
    print_info "Your repository is now private. Consider:"
    echo "  1. Review commit history for any exposed secrets"
    echo "  2. Rotate any API keys that may have been public"
    echo "  3. Enable additional security features in GitHub settings"
    echo "  4. Invite collaborators if needed"
    echo ""
    print_info "See MAKE_PRIVATE.md for more security recommendations"
    echo ""
else
    echo ""
    print_error "Failed to make repository private"
    echo ""
    print_info "Possible reasons:"
    echo "  • Insufficient permissions (need admin access)"
    echo "  • Organization policy restrictions"
    echo "  • Network or API issues"
    echo ""
    print_info "Try using the GitHub web interface instead:"
    echo "  https://github.com/${full_repo}/settings"
    echo ""
    exit 1
fi
