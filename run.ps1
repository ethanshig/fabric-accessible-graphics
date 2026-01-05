# PowerShell script to run fabric-access in WSL
# This script automatically opens WSL and activates the environment

Write-Host "Starting WSL with fabric-access environment..." -ForegroundColor Green
Write-Host ""

# Change to the project directory in WSL and activate environment
wsl bash -c "cd /mnt/c/Users/ethan/fabric-accessible-graphics && source venv/bin/activate && echo 'Environment activated!' && echo '' && echo 'You can now use:' && echo '  fabric-access info' && echo '  fabric-access image-to-piaf [IMAGE]' && echo '' && echo 'To deactivate when done, type: deactivate' && echo '' && exec bash"
