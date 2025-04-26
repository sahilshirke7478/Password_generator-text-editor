import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import random
import string
import pyperclip
import sqlite3
from cryptography.fernet import Fernet

# ----------------- Secure Storage -----------------
KEY = Fernet.generate_key()  # Generate a key (Use the same key every time in a real app)
cipher = Fernet(KEY)

# Create a database to store passwords securely
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY, 
                website TEXT, 
                password TEXT)""")
conn.commit()

# ----------------- GUI Setup -----------------
root = tk.Tk()
root.title("Password Generator & Text Editor")
root.geometry("700x500")

# Notebook (Tabs)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# ----------------- Password Generator -----------------
password_frame = ttk.Frame(notebook)
notebook.add(password_frame, text="Password Generator")

tk.Label(password_frame, text="Password Length:").pack(pady=5)
password_length = tk.IntVar(value=12)
tk.Entry(password_frame, textvariable=password_length).pack()

use_special = tk.BooleanVar(value=True)
tk.Checkbutton(password_frame, text="Include Special Characters", variable=use_special).pack()

password_display = tk.Entry(password_frame, font=("Arial", 14), justify="center", width=30)
password_display.pack(pady=5)

def generate_password():
    chars = string.ascii_letters + string.digits
    if use_special.get():
        chars += string.punctuation
    pwd = "".join(random.choice(chars) for _ in range(password_length.get()))
    password_display.delete(0, tk.END)
    password_display.insert(0, pwd)

tk.Button(password_frame, text="Generate Password", command=generate_password).pack(pady=5)

def copy_password():
    pyperclip.copy(password_display.get())
    messagebox.showinfo("Copied", "Password copied to clipboard!")

tk.Button(password_frame, text="Copy to Clipboard", command=copy_password).pack(pady=5)

# ----------------- Secure Password Storage -----------------
tk.Label(password_frame, text="Website:").pack()
website_entry = tk.Entry(password_frame, width=30)
website_entry.pack()

def save_password():
    website = website_entry.get()
    password = password_display.get()
    if not website or not password:
        messagebox.showwarning("Error", "Please enter website and generate a password!")
        return
    encrypted_password = cipher.encrypt(password.encode())
    cursor.execute("INSERT INTO passwords (website, password) VALUES (?, ?)", (website, encrypted_password))
    conn.commit()
    messagebox.showinfo("Saved", "Password saved securely!")

tk.Button(password_frame, text="Save Password", command=save_password).pack(pady=5)

# ----------------- Text Editor -----------------
text_editor_frame = ttk.Frame(notebook)
notebook.add(text_editor_frame, text="Text Editor")

text_editor = tk.Text(text_editor_frame, wrap="word", font=("Arial", 12))
text_editor.pack(expand=True, fill="both")

# Save & Load File
def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_editor.get("1.0", tk.END))
        messagebox.showinfo("Success", "File Saved Successfully!")

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            text_editor.delete("1.0", tk.END)
            text_editor.insert("1.0", file.read())

tk.Button(text_editor_frame, text="Open File", command=open_file).pack(side="left", padx=5, pady=5)
tk.Button(text_editor_frame, text="Save File", command=save_file).pack(side="left", padx=5, pady=5)

# ----------------- Customization (Themes & Fonts) -----------------
def change_theme(theme):
    if theme == "Dark":
        text_editor.config(bg="black", fg="white")
    else:
        text_editor.config(bg="white", fg="black")

def change_font(font_name):
    text_editor.config(font=(font_name, 12))

themes = ["Light", "Dark"]
fonts = ["Arial", "Courier", "Times New Roman"]

theme_menu = ttk.Combobox(text_editor_frame, values=themes, state="readonly")
theme_menu.set("Light")
theme_menu.pack(side="right", padx=5, pady=5)
theme_menu.bind("<<ComboboxSelected>>", lambda e: change_theme(theme_menu.get()))

font_menu = ttk.Combobox(text_editor_frame, values=fonts, state="readonly")
font_menu.set("Arial")
font_menu.pack(side="right", padx=5, pady=5)
font_menu.bind("<<ComboboxSelected>>", lambda e: change_font(font_menu.get()))

# ----------------- Run App -----------------
root.mainloop()
