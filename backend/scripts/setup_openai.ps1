#!/usr/bin/env pwsh
# Setup Script para OpenAI API com Codex
# Configura OpenAI SDK e testa conexão

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenAI API Setup (with Codex)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Python
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
      Write-Host "✗ Python not found" -ForegroundColor Red
      exit 1
}
Write-Host "✓ Python found: $(python --version)" -ForegroundColor Green

# Install OpenAI SDK
Write-Host "`nInstalling OpenAI SDK..." -ForegroundColor Yellow
python -m pip install --upgrade openai python-dotenv tiktoken

if ($LASTEXITCODE -eq 0) {
      Write-Host "✓ OpenAI SDK installed" -ForegroundColor Green
}
else {
      Write-Host "✗ Installation failed" -ForegroundColor Red
      exit 1
}

# Load API key
Write-Host "`nLoading OpenAI API key..." -ForegroundColor Yellow
$envFile = Join-Path $PSScriptRoot "..\..\.env"
$envContent = Get-Content $envFile
$apiKey = ($envContent | Select-String "OPENAI_API_KEY=(.+)").Matches.Groups[1].Value

if ([string]::IsNullOrEmpty($apiKey)) {
      Write-Host "✗ API key not found" -ForegroundColor Red
      exit 1
}

Write-Host "✓ API key loaded: $($apiKey.Substring(0,20))..." -ForegroundColor Green

# Create test script
Write-Host "`nCreating test script..." -ForegroundColor Yellow

$testScript = @"
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

print("Testing OpenAI API connection...")
try:
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'OpenAI API is working!' in one sentence."}
        ],
        max_tokens=50
    )
    print(f"✓ Response: {response.choices[0].message.content}")
    print("✓ OpenAI API is configured correctly!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
"@

$testScriptPath = Join-Path $PSScriptRoot "test_openai.py"
Set-Content -Path $testScriptPath -Value $testScript

# Run test
Write-Host "`nTesting OpenAI API..." -ForegroundColor Yellow
python $testScriptPath

# Create code generation wrapper
Write-Host "`nCreating OpenAI Codex wrapper..." -ForegroundColor Yellow

$codexWrapper = @"
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_code(prompt, language='python'):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {language} programmer. Generate clean, efficient, production-ready code."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # Lower temperature for more deterministic code
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python openai_codex.py 'describe what code you need'")
        sys.exit(1)
    
    prompt = ' '.join(sys.argv[1:])
    language = 'python'  # default
    
    if '--lang' in sys.argv:
        lang_idx = sys.argv.index('--lang')
        if lang_idx + 1 < len(sys.argv):
            language = sys.argv[lang_idx + 1]
            # Remove --lang and language from prompt
            prompt = ' '.join([arg for i, arg in enumerate(sys.argv[1:]) 
                              if i not in [lang_idx-1, lang_idx]])
    
    print(generate_code(prompt, language))
"@

$codexPath = Join-Path $PSScriptRoot "openai_codex.py"
Set-Content -Path $codexPath -Value $codexWrapper

Write-Host "✓ Codex wrapper created" -ForegroundColor Green

# Create PowerShell function
$profilePath = $PROFILE.CurrentUserAllHosts
$psFunction = @"

# OpenAI Codex Function
function codex {
    python "$codexPath" `$args
}

"@

Add-Content -Path $profilePath -Value $psFunction
Write-Host "✓ PowerShell function added" -ForegroundColor Green

# Final instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nUsage Examples:" -ForegroundColor Yellow
Write-Host "  Restart PowerShell, then:" -ForegroundColor Cyan
Write-Host "  codex 'create a playwright script to scrape product images'" -ForegroundColor Cyan
Write-Host "  codex 'write a function to process and optimize images' --lang python" -ForegroundColor Cyan
Write-Host "`nFor this project:" -ForegroundColor Yellow
Write-Host "  codex 'create Dagster pipeline for daily manufacturer scraping'" -ForegroundColor Cyan
Write-Host "  codex 'implement Facebook Catalog API batch uploader'" -ForegroundColor Cyan
