#!/bin/bash
# ============================================================================
# VS Code Extensions Auto-Installer (Bash)
# ============================================================================
# Purpose: Automatically install all recommended extensions from .vscode/extensions.json
# Usage: bash scripts/install-vscode-extensions.sh [--code-insiders] [--verbose]
# Platform: Linux/macOS/WSL
# ============================================================================

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

EXTENSIONS_JSON=".vscode/extensions.json"
CODE_COMMAND="code"
VERBOSE=false
INSTALL_LOG="install-extensions-$(date +%Y%m%d-%H%M%S).log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_title() {
    echo -e "${CYAN}$1${NC}"
}

log_section() {
    echo -e "\n${YELLOW}[$1]${NC}"
}

check_code_installed() {
    if ! command -v "$CODE_COMMAND" &> /dev/null; then
        log_error "$CODE_COMMAND not found in PATH"
        echo "Please install VS Code or VS Code Insiders first"
        return 1
    fi

    local version=$($CODE_COMMAND --version 2>/dev/null | head -n1)
    log_info "Found $CODE_COMMAND (v$version)"
    return 0
}

check_extensions_json() {
    if [ ! -f "$EXTENSIONS_JSON" ]; then
        log_error "extensions.json not found at: $EXTENSIONS_JSON"
        return 1
    fi

    log_info "Found extensions.json"
    return 0
}

parse_extensions() {
    # Extract recommendations array from JSON
    grep -oP '"recommendations":\s*\[\s*\K[^\]]*' "$EXTENSIONS_JSON" \
        | grep -oP '"[^"]+"' \
        | sed 's/"//g' \
        | sort
}

install_extension() {
    local ext_id="$1"
    local output

    echo -n "   Installing: $ext_id ... "

    if output=$($CODE_COMMAND --install-extension "$ext_id" --force 2>&1); then
        echo -e "${GREEN}✅${NC}"
        [ "$VERBOSE" = true ] && echo "     $output" | head -n1
        return 0
    else
        echo -e "${YELLOW}⚠️ ${NC}"
        log_warn "Extension $ext_id may have failed"
        echo "     $output" | head -n1 >> "$INSTALL_LOG"
        return 1
    fi
}

count_extensions() {
    parse_extensions | wc -l
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --code-insiders)
            CODE_COMMAND="code-insiders"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--code-insiders] [--verbose]"
            exit 1
            ;;
    esac
done

# ============================================================================
# MAIN
# ============================================================================

clear

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    VS Code Extensions Auto-Installer (Bash)                 ║${NC}"
echo -e "${CYAN}║    Project: Helios (HaaS)                                  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}\n"

# Check prerequisites
if ! check_code_installed; then
    exit 1
fi

if ! check_extensions_json; then
    exit 1
fi

# Count extensions
total=$(count_extensions)
if [ "$total" -eq 0 ]; then
    log_error "No extensions found in extensions.json"
    exit 1
fi

log_info "Found $total extensions to install\n"

# Initialize counters
installed=0
failed=0
extensions=($(parse_extensions))

# Install extensions
log_section "INSTALLING EXTENSIONS"

for ext in "${extensions[@]}"; do
    if install_extension "$ext"; then
        ((installed++))
    else
        ((failed++))
    fi
done

# Summary
echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                      Installation Summary                    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"

echo -e "   Total: $total"
echo -e "   ${GREEN}✅ Installed: $installed${NC}"
echo -e "   ${RED}❌ Failed: $failed${NC}"
echo -e "   ${YELLOW}📝 Log: $INSTALL_LOG${NC}\n"

if [ "$failed" -gt 0 ]; then
    log_warn "Some extensions failed. Check the log file for details."
    echo "Common fixes:"
    echo "  - Ensure you're online"
    echo "  - Check VS Code version compatibility"
    echo "  - Try installing manually: $CODE_COMMAND --install-extension <extension-id>"
fi

log_info "Extension installation complete! Restart VS Code to activate all changes.\n"

# Show recommendations for WSL users
if grep -q "microsoft/wsl" /proc/version 2>/dev/null || [ -f /proc/sys/fs/binfmt_misc/WSLInterop ]; then
    echo -e "${YELLOW}💡 WSL Detected: Install ms-vscode-remote.remote-wsl on your Windows host${NC}"
    echo -e "   Then connect to WSL in VS Code via: Remote-WSL: New WSL Window\n"
fi

exit 0
