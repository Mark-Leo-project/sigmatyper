import time
import random
import pyautogui
import pyperclip
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
import sys
import os
import requests
import shutil


# Global flag to control typing interruption
typing_interrupted = False

def on_press(key):
    global typing_interrupted
    try:
        if key == keyboard.Key.esc:
            typing_interrupted = True
            return False  # Stop the listener
    except AttributeError:
        pass

def autotype_with_mistakes(min_speed, max_speed, mistake_chance, words_file):
    global typing_interrupted
    typing_interrupted = False

    # Start a keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        with open(words_file, 'r') as file:
            words = file.read().splitlines()
    except FileNotFoundError:
        messagebox.showerror("Error", f"'{words_file}' not found.")
        return
    except IOError:
        messagebox.showerror("Error", f"An error occurred while reading '{words_file}'.")
        return

    clipboard_text = pyperclip.paste()

    if not clipboard_text:
        messagebox.showerror("Error", "Clipboard is empty.")
        return

    # Delay to allow user to switch to the target application
    time.sleep(5)

    i = 0
    while i < len(clipboard_text):
        # Check if ESC key is pressed to stop the typing
        if typing_interrupted:
            print("Typing interrupted.")
            break

        # Random chance to insert a mistake
        if random.random() < mistake_chance:
            # Insert a random word from words.txt
            mistake_word = random.choice(words)
            for char in mistake_word:
                pyautogui.typewrite(char)
                time.sleep(random.uniform(min_speed, max_speed))
            # Backspace over the mistake
            for _ in mistake_word:
                pyautogui.press('backspace')
                time.sleep(random.uniform(min_speed, max_speed))

        # Type the next character from clipboard_text
        pyautogui.typewrite(clipboard_text[i])
        time.sleep(random.uniform(min_speed, max_speed))
        
        i += 1

    listener.stop()
    print("Typing complete.")

def start_typing():
    try:
        min_speed = float(min_speed_entry.get())
        max_speed = float(max_speed_entry.get())
        mistake_chance = float(mistake_entry.get())
        
        # Input validation
        if not (0.01 <= min_speed <= 1):
            messagebox.showerror("Error", "Minimum typing speed must be between 0.01 and 1")
            return
        if not (0.01 <= max_speed <= 1):
            messagebox.showerror("Error", "Maximum typing speed must be between 0.01 and 1")
            return
        if min_speed > max_speed:
            messagebox.showerror("Error", "Minimum typing speed must be less than or equal to maximum typing speed")
            return
        if not (0 <= mistake_chance <= 1):
            messagebox.showerror("Error", "Mistake chance must be between 0 and 1")
            return

        threading.Thread(target=autotype_with_mistakes, args=(min_speed, max_speed, mistake_chance, words_file)).start()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

# Determine the application path
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Path to words.txt
words_file = os.path.join(application_path, 'words.txt')

# Define constants for your GitHub repository and current version
REPO_OWNER = "metrospeed"
REPO_NAME = "sigmatyper"
CURRENT_VERSION = "v0.3"  # Update this with each release

def get_latest_release():
    """Fetch the latest release version and download URL from GitHub."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()
        release_data = response.json()
        return release_data["tag_name"], release_data["assets"][0]["browser_download_url"]
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to check for updates: {e}")
        return None, None

def download_and_replace_exe(download_url):
    """Download and replace the current executable with the latest version."""
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        # Write the new version to a temporary file
        with open("update_temp.exe", "wb") as temp_file:
            shutil.copyfileobj(response.raw, temp_file)
        
        # Replace the current executable with the new one
        current_exe = sys.argv[0]
        os.remove(current_exe)  # Delete current .exe
        os.rename("update_temp.exe", current_exe)  # Replace with new version
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download the update: {e}")

def check_for_update():
    """Check if a new version is available and update if necessary."""
    latest_version, download_url = get_latest_release()
    
    if latest_version and latest_version != CURRENT_VERSION:
        user_response = messagebox.askyesno(
            "Update Available",
            f"A new version ({latest_version}) is available. Do you want to update?"
        )
        if user_response:
            download_and_replace_exe(download_url)
            messagebox.showinfo("Update", "Update complete. Please restart the application.")
            sys.exit()  # Exit the current instance to apply the update
    else:
        print("You are using the latest version.")

# Run update check at startup
check_for_update()


# Create the GUI application
root = tk.Tk()
root.title("AutoTyper")

# Create a frame for better organization
frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# Minimum Typing Speed input
min_speed_label = ttk.Label(frame, text="Minimum Typing Speed (seconds between keystrokes):")
min_speed_label.pack(pady=5)
min_speed_entry = ttk.Entry(frame)
min_speed_entry.insert(0, "0.03")  # Default value
min_speed_entry.pack(pady=5)

# Maximum Typing Speed input
max_speed_label = ttk.Label(frame, text="Maximum Typing Speed (seconds between keystrokes):")
max_speed_label.pack(pady=5)
max_speed_entry = ttk.Entry(frame)
max_speed_entry.insert(0, "0.1")  # Default value
max_speed_entry.pack(pady=5)

# Mistake Chance input
mistake_label = ttk.Label(frame, text="Mistake Chance (0 to 1):")
mistake_label.pack(pady=5)
mistake_entry = ttk.Entry(frame)
mistake_entry.insert(0, "0.05")  # Default value
mistake_entry.pack(pady=5)

# Create a Start Typing button
start_button = ttk.Button(frame, text="Start Typing", command=start_typing)
start_button.pack(pady=20)

# Add a help text
help_text = ttk.Label(frame, text="Press ESC to stop typing", font=("Arial", 8))
help_text.pack(pady=5)

# Add separator
ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)

# Add version and GitHub link
version_text = ttk.Label(frame, text="v0.2", font=("Arial", 8))
version_text.pack(side='bottom', pady=2)

github_link = ttk.Label(frame, text="GitHub", font=("Arial", 8), foreground="blue", cursor="hand2")
github_link.pack(side='bottom', pady=2)
github_link.bind("<Button-1>", lambda e: os.system("start https://github.com/metrospeed/sigmatyper/tree/main"))

# Run the GUI event loop
root.mainloop()