# Windows Quick Start Guide

## You're seeing a PowerShell error? You're in the right place!

This toolkit needs to run in **WSL (Windows Subsystem for Linux)**, not PowerShell.

## Easiest Way to Start

### Method 1: Use the PowerShell Script (Simplest!)

1. **In PowerShell or Command Prompt:**
   ```powershell
   cd C:\Users\ethan\fabric-accessible-graphics
   .\run.ps1
   ```

2. **That's it!** WSL will open with everything ready to go.

### Method 2: Open WSL Directly

1. **Open WSL** - Choose one:
   - Type `wsl` in PowerShell
   - Press Windows Key, search for "Ubuntu" or "WSL"
   - Open "Windows Terminal" and select Ubuntu

2. **You'll see a Linux prompt like:**
   ```
   ethan@DESKTOP:~$
   ```

3. **Navigate to the project:**
   ```bash
   cd /mnt/c/Users/ethan/fabric-accessible-graphics
   ```

4. **Run the start script:**
   ```bash
   ./run.sh
   ```

5. **You'll see:**
   ```
   Activating virtual environment...

   Environment activated! You can now use:
     fabric-access info
     fabric-access image-to-piaf [IMAGE]

   To deactivate when done, type: deactivate
   ```

## Now You Can Use the Toolkit!

```bash
# See what it does
fabric-access info

# Convert an image
fabric-access image-to-piaf my-image.jpg --verbose

# Get help
fabric-access --help
```

## Common Questions

**Q: Why do I need WSL?**
A: This toolkit uses Linux tools (Python virtual environments, bash scripts) that don't work in Windows PowerShell. WSL lets you run Linux programs on Windows.

**Q: How do I know if I'm in WSL?**
A: Your prompt will look like `ethan@DESKTOP:/mnt/c/...` instead of `PS C:\...`

**Q: Can I just use PowerShell?**
A: No, the toolkit was built for Linux/WSL. The `run.ps1` script is just a shortcut to open WSL for you.

**Q: Where are my Windows files in WSL?**
A: Windows C: drive is at `/mnt/c/` in WSL
   - `C:\Users\ethan\` = `/mnt/c/Users/ethan/` in WSL

**Q: How do I exit WSL?**
A: Type `exit` or close the terminal window

## Troubleshooting

**Error: "wsl: command not found"**
- WSL is not installed. You need to install Windows Subsystem for Linux first.
- See: https://docs.microsoft.com/en-us/windows/wsl/install

**Error: "No such file or directory"**
- Make sure you're in the right directory:
  ```bash
  cd /mnt/c/Users/ethan/fabric-accessible-graphics
  pwd  # Shows current directory
  ```

**Error: "Permission denied: ./run.sh"**
- Make it executable:
  ```bash
  chmod +x run.sh
  ./run.sh
  ```

## Next Steps

Once you're in WSL with the environment activated, read:
- **WALKTHROUGH.md** - Detailed usage guide
- **README.md** - Full documentation

Or just try it:
```bash
fabric-access info
```
