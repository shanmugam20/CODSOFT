from tkinter import *
import random, string
import pyperclip

# Main window setup
root = Tk()
root.geometry("450x550")
root.title("Secure Password Creator")
root.configure(bg="#2c3e50")

# Header section
title_frame = Frame(root, bg="#2c3e50")
title_frame.pack(pady=20)
Label(title_frame, text="SECURE PASSWORD CREATOR", font=("Georgia", 16, "bold"), 
      bg="#2c3e50", fg="#ecf0f1").pack()

# Password length section
length_frame = Frame(root, bg="#2c3e50")
length_frame.pack(pady=15)
Label(length_frame, text="Select Password Length:", font=("Georgia", 11), 
      bg="#2c3e50", fg="#bdc3c7").pack()

pwd_length = IntVar()
pwd_length.set(12)  # Default value
length_selector = Spinbox(length_frame, from_=6, to_=50, textvariable=pwd_length, 
                         width=20, font=("Courier", 10))
length_selector.pack(pady=5)

# Character options
options_frame = Frame(root, bg="#2c3e50")
options_frame.pack(pady=15)

include_symbols = BooleanVar()
include_symbols.set(True)
Checkbutton(options_frame, text="Include Special Characters (!@#$%)", 
           variable=include_symbols, bg="#2c3e50", fg="#ecf0f1", 
           selectcolor="#34495e", font=("Georgia", 10)).pack(anchor=W)

# Generated password display
password_result = StringVar()

def create_password():
    chars_upper = string.ascii_uppercase
    chars_lower = string.ascii_lowercase  
    chars_numbers = string.digits
    chars_special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Build character set based on options
    all_chars = chars_upper + chars_lower + chars_numbers
    if include_symbols.get():
        all_chars += chars_special
    
    # Create password with guaranteed variety
    new_password = ""
    length = pwd_length.get()
    
    if length >= 3:
        # Ensure at least one from each main category
        new_password += random.choice(chars_upper)
        new_password += random.choice(chars_lower)
        new_password += random.choice(chars_numbers)
        
        if include_symbols.get() and length >= 4:
            new_password += random.choice(chars_special)
            remaining = length - 4
        else:
            remaining = length - 3
    else:
        remaining = length
    
    # Fill remaining positions
    for i in range(remaining):
        new_password += random.choice(all_chars)
    
    # Mix up the order
    password_chars = list(new_password)
    random.shuffle(password_chars)
    final_password = ''.join(password_chars)
    
    password_result.set(final_password)

# Generate button
btn_frame = Frame(root, bg="#2c3e50")
btn_frame.pack(pady=20)

generate_btn = Button(btn_frame, text="CREATE PASSWORD", command=create_password,
                     bg="#e74c3c", fg="white", font=("Georgia", 12, "bold"),
                     padx=20, pady=8, relief=RAISED, bd=2)
generate_btn.pack()

# Password display
display_frame = Frame(root, bg="#2c3e50")
display_frame.pack(pady=15)

Label(display_frame, text="Generated Password:", font=("Georgia", 11), 
      bg="#2c3e50", fg="#bdc3c7").pack()

password_entry = Entry(display_frame, textvariable=password_result, width=40, 
                      font=("Courier", 11), justify=CENTER, state="readonly",
                      readonlybackground="#ecf0f1")
password_entry.pack(pady=5)

# Copy functionality
def copy_to_clipboard():
    if password_result.get():
        pyperclip.copy(password_result.get())
        status_label.config(text="Password copied to clipboard!", fg="#27ae60")
        root.after(2000, lambda: status_label.config(text="", fg="#bdc3c7"))

copy_btn = Button(display_frame, text="COPY PASSWORD", command=copy_to_clipboard,
                 bg="#3498db", fg="white", font=("Georgia", 10, "bold"),
                 padx=15, pady=5)
copy_btn.pack(pady=10)

# Status message
status_label = Label(root, text="", font=("Georgia", 9), bg="#2c3e50", fg="#bdc3c7")
status_label.pack(pady=5)

# Instructions
info_frame = Frame(root, bg="#2c3e50")
info_frame.pack(side=BOTTOM, pady=20)
Label(info_frame, text="Tip: Use passwords with 12+ characters for better security", 
      font=("Georgia", 9, "italic"), bg="#2c3e50", fg="#95a5a6").pack()

root.mainloop()