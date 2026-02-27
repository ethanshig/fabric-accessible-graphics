# PowerShell script to run tact/tasc in WSL
# This script automatically opens WSL and activates the environment

Write-Host "Starting WSL with tactile environment..." -ForegroundColor Green
Write-Host ""

# Get the WSL path for this script's directory
$winPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$wslPath = wsl wslpath -u "$winPath"

# Change to the project directory in WSL and activate environment
wsl bash -c "cd $wslPath && source venv/bin/activate && echo 'Environment activated!' && echo '' && echo 'You can now use:' && echo '  tact info' && echo '  tact convert [IMAGE]' && echo '  tasc version' && echo '' && echo 'To deactivate when done, type: deactivate' && echo '' && exec bash"
