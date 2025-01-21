#!/path/to/virtualenv/bin/python3
import time
import logging
import subprocess
from plyer import notification

# ==========================
#       CONFIGURATION
# ==========================
CODE_EDITORS = [
    "Code", "Electron", "pycharm", "sublime_text", "Terminal", "atom", "notepad++", "Source Filmmaker"
]

INITIAL_GRACE_PERIOD = 15 * 60   # 15 minutes
REWARD_EXTENSION      = 5 * 60    # 5 minutes
CHECK_INTERVAL        = 2         # Check every 2 seconds
WAKE_GRACE_PERIOD     = 5 * 60    # 5 minutes after wake

# Tracks when YouTube is allowed until this timestamp
allowed_until = time.time() + INITIAL_GRACE_PERIOD

# Flags for state management
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
    """Send a startup notification."""
    show_notification(
        "Script Running",
        "Distraction blocker is active. 15-minute grace period started."
    )
    logging.info("Script started and initial grace period granted.")


def block_youtube():
    """
    Disable YouTube by redirecting requests in Chrome.
    This is re-run every loop when time is up.
    """
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                '''
                tell application "Google Chrome"
                    repeat with t in tabs of windows
                        if URL of t contains "youtube.com" then
                            set URL of t to "data:text/plain,YouTube Blocked: Start Coding to Unlock"
                        end if
                    end repeat
                end tell
                '''
            ],
            check=True
        )
        logging.info("YouTube tabs blocked.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error blocking YouTube (Chrome script error): {e}")
    except Exception as ex:
        logging.error(f"Unexpected error blocking YouTube: {ex}")


def is_coding():
    """
    Check if a coding editor is the frontmost application.
    Return True if the frontmost process name matches any
    in CODE_EDITORS.
    """
    try:
        # AppleScript to get the frontmost application
        active_process = subprocess.check_output(
            ["osascript", "-e",
             "tell application \"System Events\" to get name of first application process whose frontmost is true"]
        ).strip().decode()

        # Compare with known coding apps (case-insensitive)
        for app in CODE_EDITORS:
            if app.lower() in active_process.lower():
                logging.debug(f"Detected coding editor: {active_process}")
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
    global allowed_until, grace_notification_sent, last_checked_time

    notify_startup()

    while True:
        now = time.time()

        # Detect Sleep/Wake Events
        if now - last_checked_time > CHECK_INTERVAL * 10:  # Large gap, likely sleep
            logging.info("System wake detected. Adding wake grace period.")
            allowed_until = max(allowed_until, now + WAKE_GRACE_PERIOD)
            show_notification("Welcome Back", "You have 5 minutes of grace time to resume coding.")

        last_checked_time = now

        # Handle Grace Period
        if now < allowed_until and not grace_notification_sent:
            logging.debug(f"Grace period active. {int(allowed_until - now)} seconds remaining.")
        elif not grace_notification_sent and now >= allowed_until:
            show_notification("Grace Period Over", "YouTube is now monitored. Start coding!")
            grace_notification_sent = True
            logging.info("Grace period expired.")

        # Check for Coding Activity
        if is_coding():
            # Extend allowed time by REWARD_EXTENSION
            if allowed_until < now:
                allowed_until = now
            allowed_until += REWARD_EXTENSION

            # Cap the maximum allowed time to 15 minutes from now
            max_allowed_time = now + INITIAL_GRACE_PERIOD
            allowed_until = min(allowed_until, max_allowed_time)

            show_notification("Good Job!", "5 extra minutes added. Keep coding!")
            logging.debug(f"New allowed_until: {allowed_until} ({allowed_until - now:.2f} seconds left).")

        # If time is up, block YouTube
        if now > allowed_until:
            show_notification("Time's Up!", "YouTube is blocked until you code again.")
            block_youtube()

        time.sleep(CHECK_INTERVAL)



# ==========================
#      ENTRY POINT
# ==========================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped manually.")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        show_notification("Script Error", f"An error occurred: {e}")
