#!/usr/bin/env pwsh
# Setup Script para Google Gemini CLI
# Configura Google AI SDK com as chaves fornecidas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Google Gemini CLI Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Python installation
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
      Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
      exit 1
}

$pythonVersion = python --version
Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green

# Install Google Generative AI SDK
Write-Host "`nInstalling Google Generative AI SDK..." -ForegroundColor Yellow
python -m pip install --upgrade google-generativeai python-dotenv

if ($LASTEXITCODE -eq 0) {
      Write-Host "✓ Google Generative AI SDK installed" -ForegroundColor Green
}
else {
      Write-Host "✗ Installation failed" -ForegroundColor Red
      exit 1
}

# Load environment variables
Write-Host "`nLoading API keys from .env..." -ForegroundColor Yellow
$envFile = Join-Path $PSScriptRoot "..\..\.env"

if (!(Test-Path $envFile)) {
      Write-Host "✗ .env file not found at: $envFile" -ForegroundColor Red
      exit 1
}

# Parse .env file
$envContent = Get-Content $envFile
$apiKey1 = ($envContent | Select-String "GEMINI_API_KEY_1=(.+)").Matches.Groups[1].Value
$apiKey2 = ($envContent | Select-String "GEMINI_API_KEY_2=(.+)").Matches.Groups[1].Value

if ([string]::IsNullOrEmpty($apiKey1) -or [string]::IsNullOrEmpty($apiKey2)) {
      Write-Host "✗ API keys not found in .env file" -ForegroundColor Red
      exit 1
}

Write-Host "✓ API keys loaded successfully" -ForegroundColor Green
Write-Host "  Key 1: $($apiKey1.Substring(0,20))..." -ForegroundColor Cyan
Write-Host "  Key 2: $($apiKey2.Substring(0,20))..." -ForegroundColor Cyan

# Create Python test script
Write-Host "`nCreating test script..." -ForegroundColor Yellow

$testScript = @"
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY_1')
if not api_key:
    print("❌ API key not found")
    exit(1)

genai.configure(api_key=api_key)

# Test connection
print("Testing Gemini API connection...")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Gemini API is working!' in one sentence.")
    print(f"✓ Response: {response.text}")
    print("✓ Gemini API is configured correctly!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
"@

$testScriptPath = Join-Path $PSScriptRoot "test_gemini.py"
Set-Content -Path $testScriptPath -Value $testScript

# Run test
Write-Host "`nTesting Gemini API connection..." -ForegroundColor Yellow
python $testScriptPath

if ($LASTEXITCODE -eq 0) {
      Write-Host "✓ Gemini API test passed" -ForegroundColor Green
}
else {
      Write-Host "✗ Gemini API test failed" -ForegroundColor Red
}

# Create wrapper script for easier usage
Write-Host "`nCreating Gemini CLI wrapper..." -ForegroundColor Yellow

$wrapperScript = @"
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python gemini_cli.py 'your prompt here'")
        sys.exit(1)
    
    prompt = ' '.join(sys.argv[1:])
    
    # Try both API keys (for rate limiting)
    api_keys = [
        os.getenv('GEMINI_API_KEY_1'),
        os.getenv('GEMINI_API_KEY_2')
    ]
    
    for idx, api_key in enumerate(api_keys, 1):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            print(response.text)
            break
        except Exception as e:
            if idx < len(api_keys):
                print(f"Key {idx} failed, trying next key...", file=sys.stderr)
            else:
                print(f"All keys failed: {e}", file=sys.stderr)
                sys.exit(1)

if __name__ == '__main__':
    main()
"@

$wrapperPath = Join-Path $PSScriptRoot "gemini_cli.py"
Set-Content -Path $wrapperPath -Value $wrapperScript

Write-Host "✓ Gemini CLI wrapper created at: $wrapperPath" -ForegroundColor Green

# Create PowerShell function
Write-Host "`nAdding PowerShell function..." -ForegroundColor Yellow

$profilePath = $PROFILE.CurrentUserAllHosts
if (!(Test-Path $profilePath)) {
      New-Item -Path $profilePath -ItemType File -Force | Out-Null
}

$psFunction = @"

# Gemini CLI Function
function gemini {
    python "$wrapperPath" `$args
}

"@

Add-Content -Path $profilePath -Value $psFunction
Write-Host "✓ PowerShell function added" -ForegroundColor Green

# Final instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nQuick Start:" -ForegroundColor Yellow
Write-Host "  Restart PowerShell, then use:" -ForegroundColor Cyan
Write-Host "  gemini 'your prompt here'" -ForegroundColor Cyan
Write-Host "`nOr directly:" -ForegroundColor Yellow
Write-Host "  python $wrapperPath 'your prompt'" -ForegroundColor Cyan
Write-Host "`nFor web scraping tasks:" -ForegroundColor Yellow
Write-Host "  gemini 'Navigate to jinkosolar.com and list all product categories'" -ForegroundColor Cyan
Write-Host "  gemini 'Extract product model numbers from this HTML: <html>...</html>'" -ForegroundColor Cyan
