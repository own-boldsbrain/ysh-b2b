# ============================================================================
# VS Code Extensions Auto-Installer (PowerShell)
# ============================================================================
# Purpose: Automatically install all recommended extensions from .vscode/extensions.json
# Usage: .\scripts\install-vscode-extensions.ps1
# Platform: Windows (PowerShell 5.1+)
# ============================================================================

param(
    [string]$CodeVersion = "code-insiders",  # or "code" for stable
    [switch]$Verbose = $false
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$extensionsJsonPath = ".vscode/extensions.json"
$installLog = "install-extensions-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Color codes for output
$ColorGreen = [ConsoleColor]::Green
$ColorYellow = [ConsoleColor]::Yellow
$ColorRed = [ConsoleColor]::Red
$ColorCyan = [ConsoleColor]::Cyan

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-ColorOutput {
    param(
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    Write-Host $Message -ForegroundColor $Color
}

function Get-ExtensionsFromJson {
    param(
        [string]$JsonPath
    )
    
    if (-not (Test-Path $JsonPath)) {
        Write-ColorOutput "❌ extensions.json not found at: $JsonPath" $ColorRed
        exit 1
    }
    
    try {
        $json = Get-Content $JsonPath | ConvertFrom-Json
        return $json.recommendations
    }
    catch {
        Write-ColorOutput "❌ Failed to parse extensions.json: $_" $ColorRed
        exit 1
    }
}

function Check-VsCodeInstalled {
    param(
        [string]$CodeCommand
    )
    
    try {
        $version = & $CodeCommand --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Found $CodeCommand (v$(($version -split '\n')[0]))" $ColorGreen
            return $true
        }
    }
    catch {
        # Command not found
    }
    
    Write-ColorOutput "❌ $CodeCommand not found in PATH" $ColorRed
    Write-ColorOutput "   Please install VS Code or VS Code Insiders first" $ColorYellow
    return $false
}

function Install-Extension {
    param(
        [string]$ExtensionId,
        [string]$CodeCommand
    )
    
    Write-ColorOutput "   Installing: $ExtensionId" $ColorCyan
    
    try {
        & $CodeCommand --install-extension $ExtensionId --force 2>&1 | Tee-Object -FilePath $installLog -Append | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "   ✅ Installed" $ColorGreen
            return $true
        }
        else {
            Write-ColorOutput "   ⚠️  Installation may have failed (exit code: $LASTEXITCODE)" $ColorYellow
            return $false
        }
    }
    catch {
        Write-ColorOutput "   ❌ Error: $_" $ColorRed
        return $false
    }
}

function Group-ExtensionsByCategory {
    param(
        [string[]]$Extensions
    )
    
    $categories = @{
        "GitHub & Copilot" = @()
        "Python & Linting" = @()
        "Remote Development" = @()
        "Code Quality" = @()
        "Git & Version Control" = @()
        "Testing" = @()
        "Docker & DevOps" = @()
        "API & Database" = @()
        "Productivity" = @()
        "Jupyter & ML" = @()
        "Themes & Icons" = @()
        "Other" = @()
    }
    
    $categoryMap = @{
        "GitHub.copilot" = "GitHub & Copilot"
        "GitHub.copilot-chat" = "GitHub & Copilot"
        "GitHub.vscode-pull-request-github" = "Git & Version Control"
        "ms-python.python" = "Python & Linting"
        "ms-python.vscode-pylance" = "Python & Linting"
        "ms-python.debugpy" = "Python & Linting"
        "ms-python.black-formatter" = "Python & Linting"
        "ms-python.pylint" = "Python & Linting"
        "ms-python.pytest" = "Testing"
        "charliermarsh.ruff" = "Code Quality"
        "sonarsource.sonarlint-vscode" = "Code Quality"
        "ms-vscode-remote.remote-wsl" = "Remote Development"
        "ms-vscode-remote.remote-containers" = "Remote Development"
        "ms-vscode-remote.remote-ssh" = "Remote Development"
        "eamodio.gitlens" = "Git & Version Control"
        "mhutchie.git-graph" = "Git & Version Control"
        "donjayamanne.githistory" = "Git & Version Control"
        "ms-azuretools.vscode-docker" = "Docker & DevOps"
        "humao.rest-client" = "API & Database"
        "rangav.vscode-thunder-client" = "API & Database"
        "cweijan.vscode-postgresql-client2" = "API & Database"
        "ms-mssql.mssql" = "API & Database"
        "gruntfuggly.todo-tree" = "Productivity"
        "wayou.vscode-todo-highlight" = "Productivity"
        "usernamehw.errorlens" = "Productivity"
        "ms-toolsai.jupyter" = "Jupyter & ML"
        "ms-toolsai.vscode-jupyter-cell-tags" = "Jupyter & ML"
        "zhuangtongfa.Material-theme" = "Themes & Icons"
        "vscode-icons-team.vscode-icons" = "Themes & Icons"
        "PKief.material-icon-theme" = "Themes & Icons"
    }
    
    foreach ($ext in $Extensions) {
        $category = $categoryMap[$ext]
        if (-not $category) {
            $category = "Other"
        }
        $categories[$category] += $ext
    }
    
    return $categories
}

# ============================================================================
# MAIN
# ============================================================================

Write-ColorOutput "`n╔════════════════════════════════════════════════════════════════╗" $ColorCyan
Write-ColorOutput "║    VS Code Extensions Auto-Installer (PowerShell)           ║" $ColorCyan
Write-ColorOutput "║    Project: Helios (HaaS)                                  ║" $ColorCyan
Write-ColorOutput "╚════════════════════════════════════════════════════════════════╝`n" $ColorCyan

# Check VS Code availability
if (-not (Check-VsCodeInstalled $CodeVersion)) {
    exit 1
}

# Load extensions from JSON
Write-ColorOutput "📋 Loading extensions from: $extensionsJsonPath" $ColorYellow
$extensions = Get-ExtensionsFromJson $extensionsJsonPath
$totalExtensions = $extensions.Count

if ($totalExtensions -eq 0) {
    Write-ColorOutput "❌ No extensions found in extensions.json" $ColorRed
    exit 1
}

Write-ColorOutput "📦 Found $totalExtensions extensions to install`n" $ColorGreen

# Group by category
$grouped = Group-ExtensionsByCategory $extensions

$installedCount = 0
$failedCount = 0

# Install extensions by category
foreach ($category in $grouped.Keys) {
    $exts = $grouped[$category]
    if ($exts.Count -gt 0) {
        Write-ColorOutput "`n[$(($category).ToUpper())]" $ColorYellow
        
        foreach ($ext in $exts) {
            if (Install-Extension $ext $CodeVersion) {
                $installedCount++
            }
            else {
                $failedCount++
            }
        }
    }
}

# Summary
Write-ColorOutput "`n╔════════════════════════════════════════════════════════════════╗" $ColorCyan
Write-ColorOutput "║                      Installation Summary                    ║" $ColorCyan
Write-ColorOutput "╚════════════════════════════════════════════════════════════════╝" $ColorCyan

Write-ColorOutput "   Total: $totalExtensions" $ColorCyan
Write-ColorOutput "   ✅ Installed: $installedCount" $ColorGreen
Write-ColorOutput "   ❌ Failed: $failedCount" $(if ($failedCount -gt 0) { $ColorRed } else { $ColorGreen })
Write-ColorOutput "   📝 Log file: $installLog`n" $ColorYellow

if ($failedCount -gt 0) {
    Write-ColorOutput "⚠️  Some extensions failed. Check the log file for details." $ColorYellow
    Write-ColorOutput "   Common fixes:" $ColorYellow
    Write-ColorOutput "   - Ensure you're online" $ColorYellow
    Write-ColorOutput "   - Check VS Code version compatibility" $ColorYellow
    Write-ColorOutput "   - Try installing manually: $CodeCommand --install-extension <extension-id>" $ColorYellow
}

Write-ColorOutput "`n✅ Extension installation complete! Restart VS Code to activate all changes.`n" $ColorGreen
