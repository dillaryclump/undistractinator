#!/venv/bin/python3
import time
import logging
import subprocess
import json
from plyer import notification

# ==========================
#       CONFIGURATION
# ==========================
CODE_EDITORS = [
    "Code", "Electron", "pycharm", "sublime_text",
    "Terminal", "atom", "notepad++", "Source Filmmaker"
]

INITIAL_GRACE_PERIOD  = 15 * 60  # 15 minutes
REWARD_EXTENSION      = 5 * 60   # 5 minutes
CHECK_INTERVAL        = 2        # Check every 2 seconds
WAKE_GRACE_PERIOD     = 5 * 60   # 5 minutes after wake

# Tracking "allowed_until" and other state
allowed_until = time.time() + INITIAL_GRACE_PERIOD
grace_notification_sent = False
last_checked_time = time.time()

# ==========================
#     LOGGING SETUP
# ==========================
logging.basicConfig(
    filename="/tmp/your_script.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==========================
#      HELPER FUNCTIONS
# ==========================
def show_notification(title: str, message: str):
    """Send a system notification and log it."""
    notification.notify(
        title=title,
        message=message,
        timeout=5
    )
    logging.info(f"Notification sent - {title}: {message}")


def notify_startup():
    """Send a startup notification and log the event."""
    show_notification("Script Running",
                      "Distraction blocker is active. 15-minute grace period started.")
    logging.info("Script started. Initial grace period granted.")


def load_config():
    """Load the blocking config from undistractinator_config.json."""
    try:
        with open("undistractinator_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("No undistractinator_config.json found. Using defaults.")
        return {}
    except json.JSONDecodeError as e:
        logging.warning(f"Error decoding JSON: {e}. Using empty config.")
        return {}


def block_websites_in_chrome(websites):
    """
    For each site in websites, forcibly change any matching Chrome tabs
    to a simple 'blocked' URL. 
    """
    try:
        # Construct AppleScript that checks all open Chrome tabs
        # and if they match a site in 'websites', it redirects them.
        # We'll chain multiple 'if URL of t contains "<site>" then...' lines.
        conditions = []
        for site in websites:
            conditions.append(f'''
                if URL of t contains "{site}" then
                    set URL of t to "data:text/plain,Blocked: {site} - Start Coding to Unlock"
                end if
            ''')
        conditional_block_script = "\n".join(conditions)

        script = f'''
            tell application "Google Chrome"
                repeat with t in tabs of windows
                    {conditional_block_script}
                end repeat
            end tell
        '''

        subprocess.run(["osascript", "-e", script], check=True)
        logging.info("Blocked websites in Chrome.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error blocking websites (Chrome script error): {e}")
    except Exception as ex:
        logging.error(f"Unexpected error blocking websites: {ex}")


def block_apps(apps):
    """
    Attempt to quit or 'nudge' undesired apps if they are open.
    (macOS approach: use AppleScript to quit them.)
    """
    try:
        for app in apps:
            script = f'''
                tell application "System Events"
                    set appList to name of every process
                    if appList contains "{app}" then
                        try
                            tell application "{app}" to quit
                            delay 1
                        on error errMsg
                            display notification "Can't quit {app}: " & errMsg
                        end try
                    end if
                end tell
            '''
            subprocess.run(["osascript", "-e", script], check=True)
        logging.info(f"Attempted to block apps: {apps}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error blocking apps (AppleScript error): {e}")
    except Exception as ex:
        logging.error(f"Unexpected error blocking apps: {ex}")


def is_coding():
    """
    Check if a coding editor is the frontmost application on macOS.
    Returns True if the frontmost process name matches any in CODE_EDITORS.
    """
    try:
        active_process = subprocess.check_output(
            [
                "osascript",
                "-e",
                "tell application \"System Events\" to get name of first application process whose frontmost is true"
            ]
        ).strip().decode()

        for app in CODE_EDITORS:
            if app.lower() in active_process.lower():
                logging.debug(f"Detected coding editor in front: {active_process}")
                return True
    except subprocess.CalledProcessError as e:
        logging.error(f"CalledProcessError detecting active process: {e}")
    except Exception as ex:
        logging.error(f"Unexpected error detecting active process: {ex}")

    return False


# ==========================
#         MAIN LOOP
# ==========================
def main():
    # Load config from JSON
    config = load_config()
    websites_to_block = config.get("websites_to_block", [])
    apps_to_block = config.get("apps_to_block", [])
    # (Optionally read other config keys like focus_time_minutes, grace_period_minutes, etc.)

    global allowed_until, grace_notification_sent, last_checked_time

    notify_startup()

    while True:
        now = time.time()

        # Detect Sleep/Wake events
        if now - last_checked_time > CHECK_INTERVAL * 10:
            # Probably the system just woke up
            logging.info("System wake detected. Adding wake grace period.")
            allowed_until = max(allowed_until, now + WAKE_GRACE_PERIOD)
            show_notification("Welcome Back",
                              "You have 5 minutes of grace time to resume coding.")

        last_checked_time = now

        # Handle Grace Period notifications
        if now < allowed_until and not grace_notification_sent:
            remaining = int(allowed_until - now)
            logging.debug(f"Grace period active. {remaining} seconds remaining.")
        elif not grace_notification_sent and now >= allowed_until:
            show_notification("Grace Period Over",
                              "Blocking will now occur. Start coding to earn more time!")
            grace_notification_sent = True
            logging.info("Grace period expired.")

        # If the user is coding, reward them
        if is_coding():
            # If we were already out of time, bring 'allowed_until' up to now
            if allowed_until < now:
                allowed_until = now
            # Add the reward extension
            allowed_until += REWARD_EXTENSION
            # But don’t exceed the max extension of 15 minutes from now
            max_allowed_time = now + INITIAL_GRACE_PERIOD
            allowed_until = min(allowed_until, max_allowed_time)

            show_notification("Good Job!", "5 extra minutes added. Keep coding!")
            logging.debug(
                f"New allowed_until = {allowed_until} ({allowed_until - now:.2f} seconds left)."
            )

        # If time is up, block the sites & apps
        if now > allowed_until:
            show_notification("Time's Up!", "Websites/apps blocked until you code again.")
            block_websites_in_chrome(websites_to_block)
            block_apps(apps_to_block)

        time.sleep(CHECK_INTERVAL)


# ==========================
#      ENTRY POINT
# ==========================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped manually via KeyboardInterrupt.")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        show_notification("Script Error", f"An error occurred: {e}")