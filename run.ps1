# PowerShell script to run tactile in WSL
# This script automatically opens WSL and activates the environment

Write-Host "Starting WSL with tactile environment..." -ForegroundColor Green
Write-Host ""

# Change to the project directory in WSL and activate environment
wsl bash -c "cd /mnt/c/Users/ethan/fabric-accessible-graphics && source venv/bin/activate && echo 'Environment activated!' && echo '' && echo 'You can now use:' && echo '  tactile info' && echo '  tactile image-to-piaf [IMAGE]' && echo '' && echo 'To deactivate when done, type: deactivate' && echo '' && exec bash"
