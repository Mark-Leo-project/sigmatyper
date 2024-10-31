import requests.certs
import requests
import time
import random
import pyautogui
import pyperclip
import keyboard
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import re  # For regular expressions
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import shutil
import zipfile
import webbrowser


def check_for_update():
    current_version = '0.4'  # Replace with your application's current version
    repo_owner = 'metrospeed'
    repo_name = 'sigmatyper'

    try:
        response = requests.get(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest',
            timeout=10
        )
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')  # Remove 'v' prefix if present
            if latest_version > current_version:
                if messagebox.askyesno(
                    "Update Available",
                    f"A new version ({latest_version}) is available.\n"
                    "Do you want to visit the download page?"
                ):
                    webbrowser.open(f'https://github.com/{repo_owner}/{repo_name}/releases/latest')
            else:
                messagebox.showinfo("Up-to-Date", "You are using the latest version.")
        else:
            messagebox.showwarning(
                "Update Check Failed",
                "Could not check for updates. Try again later."
            )
    except Exception as e:
        messagebox.showerror("Error", f"Update check failed: {e}")


def autotype_with_errors(typing_speed_range, mistake_chance, words_text):
    # Activate target window (the currently active window)
    time.sleep(1)  # Brief pause to allow user to switch to the target window if needed

    # Split the text into words and spaces, preserving whitespace
    tokens = re.findall(r'\S+|\s+', words_text)

    for token in tokens:
        if keyboard.is_pressed('esc'):
            print("Typing interrupted.")
            messagebox.showinfo("Typing stopped", "You stopped the typing process.")
            return

        if token.isspace():
            # Type spaces and newlines directly
            pyautogui.typewrite(token)
            continue

        # Decide whether to make a mistake on this word
        make_mistake = random.random() < mistake_chance

        if make_mistake:
            # Introduce a typing error
            incorrect_word, mistake_index = introduce_typo(token)
            type_word(incorrect_word, typing_speed_range)
            # Simulate realizing the mistake and correcting it
            time.sleep(random.uniform(0.2, 0.5))  # Pause before correcting

            # Delete characters one by one
            chars_to_delete = len(incorrect_word) - mistake_index
            for _ in range(chars_to_delete):
                pyautogui.press('backspace')
                time.sleep(random.uniform(0.05, 0.2))  # Pause between backspaces

            # Retype the correct characters
            correct_substring = token[mistake_index:]
            type_word(correct_substring, typing_speed_range)
        else:
            # Type the word correctly
            type_word(token, typing_speed_range)

    messagebox.showinfo("Typing Complete", "The typing task has been successfully completed.")


def type_word(word, typing_speed_range):
    for char in word:
        if keyboard.is_pressed('esc'):
            return
        typing_speed = random.uniform(typing_speed_range[0], typing_speed_range[1])
        time.sleep(typing_speed)
        pyautogui.typewrite(char)


def introduce_typo(word):
    typo_types = ['omit', 'transpose', 'repeat', 'wrong_letter']
    typo_choice = random.choice(typo_types)

    if len(word) < 2:
        typo_choice = 'wrong_letter'

    index = random.randint(0, len(word) - 1)
    mistake_index = index  # Position where the mistake occurs

    if typo_choice == 'omit':
        # Omit a letter
        incorrect_word = word[:index] + word[index + 1:]
    elif typo_choice == 'transpose' and index < len(word) - 1:
        # Transpose two adjacent letters
        incorrect_word = word[:index] + word[index + 1] + word[index] + word[index + 2:]
    elif typo_choice == 'repeat':
        # Repeat a letter
        incorrect_word = word[:index + 1] + word[index] + word[index + 1:]
    elif typo_choice == 'wrong_letter':
        # Replace a letter with a wrong one
        wrong_char = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        incorrect_word = word[:index] + wrong_char + word[index + 1:]
    else:
        incorrect_word = word  # Fallback to original word if something goes wrong

    return incorrect_word, mistake_index


def start_typing_with_delay():
    start_button.config(state="disabled")
    start_button.config(text="Starting in 3 seconds...")
    messagebox.showinfo("Typing Starting Soon", "Click where you want to type. Starting in 3 seconds.")
    root.after(3000, start_typing)


def start_typing():
    typing_speed_min = speed_slider_min.get() / 1000  # Convert ms to seconds
    typing_speed_max = speed_slider_max.get() / 1000
    mistake_chance = mistake_slider.get() / 100  # Convert percentage to fraction

    if words_file_path:
        file_ext = os.path.splitext(words_file_path)[1].lower()
        try:
            if file_ext == '.txt':
                with open(words_file_path, 'r', encoding='utf-8') as file:
                    words_text = file.read()
            elif file_ext == '.docx':
                try:
                    from docx import Document
                except ImportError:
                    messagebox.showerror(
                        "Error",
                        "python-docx module not found. Please install it using 'pip install python-docx'"
                    )
                    start_button.config(state="normal", text="Start Typing")
                    return
                doc = Document(words_file_path)
                words_text = '\n'.join([para.text for para in doc.paragraphs])
            elif file_ext == '.pdf':
                try:
                    import PyPDF2
                except ImportError:
                    messagebox.showerror(
                        "Error",
                        "PyPDF2 module not found. Please install it using 'pip install PyPDF2'"
                    )
                    start_button.config(state="normal", text="Start Typing")
                    return
                with open(words_file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    words_text = ''
                    for page in reader.pages:
                        words_text += page.extract_text() + '\n'
            else:
                messagebox.showerror("Error", f"Unsupported file type: {file_ext}")
                start_button.config(state="normal", text="Start Typing")
                return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the file: {str(e)}")
            start_button.config(state="normal", text="Start Typing")
            return
        if not words_text.strip():
            messagebox.showerror("Error", "The words file is empty.")
            start_button.config(state="normal", text="Start Typing")
            return
    else:
        # Read from text input
        words_text = text_input.get("1.0", tk.END).strip()
        if not words_text:
            words_text = pyperclip.paste()
        if not words_text.strip():
            messagebox.showerror(
                "Error",
                "No text available. Please enter text, copy text, or select a file."
            )
            start_button.config(state="normal", text="Start Typing")
            return

    autotype_with_errors(
        typing_speed_range=(typing_speed_min, typing_speed_max),
        mistake_chance=mistake_chance,
        words_text=words_text
    )
    start_button.config(state="normal", text="Start Typing")


def select_words_file():
    global words_file_path
    words_file_path = filedialog.askopenfilename(
        title="Select Words File",
        filetypes=[
            ("All Supported Files", ("*.txt", "*.docx", "*.pdf")),
            ("Text Files", "*.txt"),
            ("Word Documents", "*.docx"),
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
    )
    words_file_label.config(
        text=f"Selected file: {os.path.basename(words_file_path)}" if words_file_path else "No file selected"
    )
    save_settings_if_loaded()


def clear_words_file():
    global words_file_path
    words_file_path = ""
    words_file_label.config(text="No file selected")
    save_settings_if_loaded()


def save_settings():
    settings = {
        'typing_speed_min': speed_slider_min.get(),
        'typing_speed_max': speed_slider_max.get(),
        'mistake_chance': mistake_slider.get(),
        'words_file_path': words_file_path,
        'text_input_content': text_input.get("1.0", 'end-1c')  # Avoid extra newline
    }
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f)


def save_settings_if_loaded():
    if settings_loaded:
        save_settings()


def load_settings():
    global words_file_path, settings_loaded
    if os.path.exists('settings.json'):
        with open('settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            words_file_path = settings.get('words_file_path', '')
            if words_file_path:
                words_file_label.config(text=f"Selected file: {os.path.basename(words_file_path)}")
            else:
                words_file_label.config(text="No file selected")
            text_input_content = settings.get('text_input_content', '')
            text_input.delete("1.0", tk.END)
            text_input.insert(tk.END, text_input_content)
            speed_slider_min.set(settings.get('typing_speed_min', 50))
            speed_slider_max.set(settings.get('typing_speed_max', 100))
            mistake_slider.set(settings.get('mistake_chance', 10))
    else:
        speed_slider_min.set(50)
        speed_slider_max.set(100)
        mistake_slider.set(10)
    settings_loaded = True  # Set to True after loading settings


def update_speed_min_label(value):
    speed_slider_min_value_label.config(text=f"{int(float(value))} ms")
    save_settings_if_loaded()


def update_speed_max_label(value):
    speed_slider_max_value_label.config(text=f"{int(float(value))} ms")
    save_settings_if_loaded()


def update_mistake_slider_label(value):
    mistake_slider_value_label.config(text=f"{int(float(value))}%")
    save_settings_if_loaded()


# Function to get the resource path (useful when bundled with PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller creates a temp folder and stores path in _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def on_closing():
    save_settings()
    root.destroy()


# Initialize GUI
root = ttk.Window(themename="darkly")
root.title("Marks Typer")
root.geometry("450x600")
root.resizable(False, False)

words_file_path = ""
settings_loaded = False  # Initialize settings_loaded as False

# Style configuration
style = ttk.Style()

# Update the slider style to be simplistic and clean
style.configure("TScale", troughcolor="#C0C0C0")  # Grey background
style.configure("Horizontal.TScale", slidercolor="#1E90FF")  # Blue slider button

# Update other widget styles
style.configure("Custom.TFrame", background=style.colors.bg)
style.configure("Custom.TButton", font=("Helvetica", 12, "bold"))
style.configure("Custom.Small.TButton", font=("Helvetica", 8, "bold"), padding=2)
style.configure("Custom.TLabel", font=("Helvetica", 10), foreground=style.colors.light)

# Define standard padding
standard_pad = 10

# Title label with even spacing
title_label = ttk.Label(
    root, text="Marks Typer", font=("Helvetica", 24, "bold"), style="Custom.TLabel"
)
title_label.pack(pady=(standard_pad, 0))

# Apply the custom frame style
frame = ttk.Frame(root, padding=(standard_pad, 0), style="Custom.TFrame")
frame.pack(pady=(0, 0), padx=standard_pad, fill="both", expand=False)

# File selection frame
words_file_frame = ttk.Frame(frame, style="Custom.TFrame")
words_file_frame.pack(pady=(standard_pad, 5))

# Select Words File button
words_file_button = ttk.Button(
    words_file_frame,
    text="Select Words File",
    command=select_words_file,
    bootstyle="primary",
    style="Custom.TButton"
)
words_file_button.pack(side="left", padx=(0, 5))

# Clear Words File button as a small 'X'
clear_words_file_button = ttk.Button(
    words_file_frame,
    text="X",
    command=clear_words_file,
    bootstyle="danger",
    style="Custom.Small.TButton",
    width=2
)
clear_words_file_button.pack(side="left")

words_file_label = ttk.Label(frame, text="No file selected", style="Custom.TLabel")
words_file_label.pack(pady=(0, standard_pad))

# Text input with scrollbar
text_input_label = ttk.Label(frame, text="Or enter text below:", style="Custom.TLabel")
text_input_label.pack(pady=(0, 5))

text_input_frame = ttk.Frame(frame, style="Custom.TFrame")
text_input_frame.pack(pady=(0, standard_pad))

# Create the Text widget and Scrollbar
text_input = tk.Text(
    text_input_frame,
    height=4,
    width=45,
    bg=style.colors.bg,
    fg=style.colors.light,
    insertbackground=style.colors.light,
    highlightthickness=1,
    highlightbackground=style.colors.border,
    wrap="word"
)
text_input.pack(side="left", fill="both", expand=True)

text_scrollbar = ttk.Scrollbar(
    text_input_frame, orient="vertical", command=text_input.yview
)
text_scrollbar.pack(side="right", fill="y")

text_input.configure(yscrollcommand=text_scrollbar.set)
text_input.bind("<KeyRelease>", lambda event: save_settings_if_loaded())

# Typing Speed Controls
speed_label = ttk.Label(
    frame, text="Typing Speed (Min/Max in ms):", style="Custom.TLabel"
)
speed_label.pack(pady=(0, 5))

speed_frame = ttk.Frame(frame, style="Custom.TFrame")
speed_frame.pack(pady=(0, standard_pad))

# Min speed
speed_slider_min_label = ttk.Label(speed_frame, text="Min", style="Custom.TLabel")
speed_slider_min_label.grid(row=0, column=0, padx=5)

speed_slider_min = ttk.Scale(
    speed_frame,
    from_=10,
    to=500,
    orient='horizontal',
    length=150,
    command=update_speed_min_label
)
speed_slider_min.grid(row=1, column=0, padx=5)

speed_slider_min_value_label = ttk.Label(
    speed_frame, text="", style="Custom.TLabel"
)
speed_slider_min_value_label.grid(row=2, column=0)

# Max speed
speed_slider_max_label = ttk.Label(speed_frame, text="Max", style="Custom.TLabel")
speed_slider_max_label.grid(row=0, column=1, padx=5)

speed_slider_max = ttk.Scale(
    speed_frame,
    from_=10,
    to=500,
    orient='horizontal',
    length=150,
    command=update_speed_max_label
)
speed_slider_max.grid(row=1, column=1, padx=5)

speed_slider_max_value_label = ttk.Label(
    speed_frame, text="", style="Custom.TLabel"
)
speed_slider_max_value_label.grid(row=2, column=1)

# Mistake Frequency Control
mistake_label = ttk.Label(
    frame, text="Mistake Frequency (%):", style="Custom.TLabel"
)
mistake_label.pack(pady=(0, 5))

mistake_slider_frame = ttk.Frame(frame, style="Custom.TFrame")
mistake_slider_frame.pack(pady=(0, standard_pad))

mistake_slider = ttk.Scale(
    mistake_slider_frame,
    from_=0,
    to=100,
    orient='horizontal',
    length=320,
    command=update_mistake_slider_label
)
mistake_slider.pack()

mistake_slider_value_label = ttk.Label(
    mistake_slider_frame, text="", style="Custom.TLabel"
)
mistake_slider_value_label.pack()

# Start button
start_button = ttk.Button(
    frame,
    text="Start Typing",
    command=start_typing_with_delay,
    bootstyle="success",
    style="Custom.TButton"
)
start_button.pack(pady=(standard_pad, standard_pad))

# Footer Label
footer_label = ttk.Label(
    root,
    text="Made by Mark",
    font=("Helvetica", 10, "italic"),
    style="Custom.TLabel"
)
footer_label.pack(pady=(0, 0))

update_button = ttk.Button(
    root,
    text="Check for Updates",
    command=check_for_update
)
update_button.pack(side="bottom", pady=standard_pad)

# Load settings
load_settings()

# Update labels with initial values
update_speed_min_label(speed_slider_min.get())
update_speed_max_label(speed_slider_max.get())
update_mistake_slider_label(mistake_slider.get())

# Ensure settings are saved on exit
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
