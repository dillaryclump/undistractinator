# Undistractinator

**Undistractinator** is a lightweight, customizable productivity tool designed primarily for **Mac computers with M-series chips**, but it can be **modified** to run on Windows (and Linux) as well. This tool helps you stay consistent in your coding (or studying) sessions by blocking distracting websites and apps until your designated work period ends.

---

## Key Features

- **Configurable Block Lists**  
  Add or remove websites and apps to block by editing a separate `undistractinator_config.json` file.

- **Focus & Grace Periods**  
  Define how long you want to remain in focus mode and how long a grace period you need before blocking starts.

- **Platform Flexibility**  
  - Optimized for macOS M-series chips using built-in macOS commands (like AppleScript).  
  - Adaptable for Windows by changing the blocking/detection mechanisms.

- **Lightweight & Open Source**  
  - No heavy installations or hidden data collection.  
  - Code is fully accessible to modify or review.

---

## Compatible with a Separate Config File

To ensure code and configuration remain **decoupled**, this project uses an external `undistractinator_config.json` file. Your `main.py` might look like this:

    import json
    import os

    def load_config():
        with open("undistractinator_config.json", "r") as f:
            return json.load(f)

    def main():
        config = load_config()
        websites_to_block = config.get("websites_to_block", [])
        apps_to_block = config.get("apps_to_block", [])
        focus_time = config.get("focus_time_minutes", 60)
        grace_time = config.get("grace_period_minutes", 5)

        print("Blocking sites:", websites_to_block)
        print("Blocking apps:", apps_to_block)
        print("Focus time:", focus_time, "minutes")
        print("Grace period:", grace_time, "minutes")

        # ...Add your actual blocking logic here (AppleScript, Windows hosts edit, etc.)...

    if __name__ == "__main__":
        main()

By separating the config, you can simply update `undistractinator_config.json` without altering core code.

---

## Installation & Usage

1. **Clone This Repository**

    git clone https://github.com/<YOUR_USERNAME>/Undistractinator.git
    cd Undistractinator

2. **Install Dependencies (If Any)**

    pip install -r requirements.txt

   *(Skip this if you have no extra dependencies.)*

3. **Configure**

  The script uses a configuration file: `undistractinator_config.json`. Example:

  ```json
  {
    "websites_to_block": ["facebook.com", "twitter.com", "youtube.com", "reddit.com"],
    "apps_to_block": ["Slack", "Discord"],
    "focus_apps": ["Code", "Pycharm", "Notepad++"],
    "focus_time_minutes": 30,
    "grace_period_minutes": 5
  }
     
   - Adjust sites, apps, and time intervals to suit your needs. You can add or rename keys as necessary—just be sure your `main.py` references them correctly.
   - create a venv and add it to the undistractinator folder main folder with latest version of python (as of mine 3.10.6 but should be compatible with the latest version)


    - Using macOS LaunchAgents (Recommended)
	1.	Create a file in ~/Library/LaunchAgents named something like com.yourname.distractionblocker.plist.
	2.	Paste in content like this (make sure to edit the paths and script name accordingly):

4. **Run the Script on macOS (M-Series)**

   - **Terminal**:
     
         python3 main.py

   - Or if you have a shell script (e.g., `run_script.sh`):
     
         chmod +x run_script.sh
         ./run_script.sh

   - If the script uses AppleScript (`osascript`) or similar Mac-specific calls, it should work out of the box on M-series. If issues occur, ensure **Rosetta** is installed (if needed) and confirm your Python environment supports Apple Silicon.

---

## Modifying for Windows

1. **Replace macOS-Specific Code**  
   If `main.py` relies on AppleScript, switch to Windows equivalents:
   - Editing the **hosts** file (requires Admin privileges) to block domains.
   - Using **Windows Firewall** commands (`netsh`) to block certain sites or ports.
   - Libraries like `pywin32` or `pywinauto` to detect which app is in the foreground.

3. **Scheduling**

   - Use **Task Scheduler**:
     1. **Win+R**, then type `taskschd.msc`.
     2. **Create Basic Task** → Name it “Undistractinator”.
     3. **Trigger**: “At log on” or whichever schedule you prefer.
     4. **Action**: “Start a program” → `python.exe` → `C:\path\to\main.py`.
     5. Click **OK**.

4. **Admin Permissions**  
   - Editing the hosts file or firewall rules typically requires **administrator** rights.

---

## Why This Helps Me Stay Consistent

- **Removes Distractions**  
  Social media or chat apps are blocked the moment I’m supposed to be focusing, so there’s less chance of drifting off task.

- **Encourages Good Habits**  
  By automating the blocking process, I rely less on sheer willpower to avoid distractions—saving mental energy for actual work.

- **Customizable Workflow**  
  A separate `undistractinator_config.json` ensures I can add or remove sites and apps at will, all without touching the core script logic.

---

## No Sensitive Data

- This repo does **not** store or transmit personal credentials.  
- Check your `.gitignore` and environment to ensure no private data is committed.

---

## Contributing

1. **Fork** this repository on GitHub.  
2. **Create a new branch**:
   
       git checkout -b feature/new-behavior
   
3. **Commit and Push** your changes:
   
       git commit -m "Add new blocking method"
       git push origin feature/new-behavior
   
4. **Open a Pull Request** to have it merged.

---

## License

This project is released under the **[MIT License](LICENSE)**.  
You’re free to use, modify, and distribute it as long as you keep the license text intact.

---


**Enjoy your distraction-free coding sessions on your M-series Mac, or adapt the script for Windows to stay consistent in your productivity!**