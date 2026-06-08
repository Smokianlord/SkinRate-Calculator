import tkinter as tk
from tkinter import ttk

def calculate(event=None):  # Added 'event=None' to handle Enter key
    try:
        # Retrieve and convert inputs to float
        amount = float(amount_entry.get())
        item_rate = float(item_rate_entry.get()) if item_rate_entry.get() else None
        wallet_rate = float(wallet_rate_entry.get()) if wallet_rate_entry.get() else None
        
        # Perform calculations if values are provided
        if item_rate is not None:
            add_15 = round(amount * 1.15, 2)
            minus_15 = round(amount * 0.85, 2)
            item_cost = int(amount * item_rate)
            item_cashout_agent = int(item_cost * 1.0185)
            item_cashout_priyo = int(item_cost * 1.0149)
            
            # Update labels with the calculated values
            add_15_label.config(text=f"With Steam Tax (15%): ${add_15}")
            minus_15_label.config(text=f"Without Steam Tax (15%): ${minus_15}")
            item_cost_label.config(text=f"Item Transfer (Cost): {item_cost} TK")
            item_cashout_agent_label.config(text=f"Cashout (Agent): {item_cashout_agent} TK")
            item_cashout_priyo_label.config(text=f"Cashout (Priyo): {item_cashout_priyo} TK")

            # Show item frame if item rate is given
            item_frame.grid(row=0, column=0, padx=20, sticky="w")
        else:
            item_frame.grid_forget()  # Hide item frame if no item rate

        if wallet_rate is not None:
            add_15 = round(amount * 1.15, 2)
            minus_15 = round(amount * 0.85, 2)
            wallet_cost = int(amount * wallet_rate)
            wallet_cashout_agent = int(wallet_cost * 1.0185)
            wallet_cashout_priyo = int(wallet_cost * 1.0149)
            
            # Update labels with the calculated values
            add_15_label.config(text=f"With Steam Tax (15%): ${add_15}")
            minus_15_label.config(text=f"Without Steam Tax (15%): ${minus_15}")
            wallet_cost_label.config(text=f"Wallet Transfer (Cost): {wallet_cost} TK")
            wallet_cashout_agent_label.config(text=f"Cashout (Agent): {wallet_cashout_agent} TK")
            wallet_cashout_priyo_label.config(text=f"Cashout (Priyo): {wallet_cashout_priyo} TK")

            # Show wallet frame if wallet rate is given
            wallet_frame.grid(row=0, column=1, padx=20, sticky="w")
        else:
            wallet_frame.grid_forget()  # Hide wallet frame if no wallet rate

        # Clear error message
        error_label.config(text="")
    except ValueError:
        # Display error if input is invalid
        error_label.config(text="Please enter valid numbers!", fg="red")

def copy_to_clipboard(text):
    root.clipboard_clear()  # Clear current clipboard
    root.clipboard_append(text)  # Add new text to clipboard
    root.update()  # Update clipboard contents

# GUI Setup
root = tk.Tk()
root.title("SkinRate Calculator")
root.configure(bg="#f4f4f9")

# Automatically adjust window size based on content
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

title_label = tk.Label(root, text="SkinRate Calculator", font=("Helvetica", 18, "bold"), bg="#f4f4f9")
title_label.grid(row=0, column=0, pady=15)

# Input Frame
input_frame = tk.Frame(root, bg="#f4f4f9")
input_frame.grid(row=1, column=0, padx=20, pady=10)

# Labels and entries
tk.Label(input_frame, text="Amount ($)", font=("Arial", 12), bg="#f4f4f9").grid(row=0, column=0, padx=10, pady=5, sticky="w")
amount_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
amount_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(input_frame, text="Item Transfer Rate", font=("Arial", 12), bg="#f4f4f9").grid(row=1, column=0, padx=10, pady=5, sticky="w")
item_rate_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
item_rate_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(input_frame, text="Wallet Transfer Rate", font=("Arial", 12), bg="#f4f4f9").grid(row=2, column=0, padx=10, pady=5, sticky="w")
wallet_rate_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
wallet_rate_entry.grid(row=2, column=1, padx=10, pady=5)

# Calculate Button (use Enter to trigger calculate)
calc_button = tk.Button(root, text="Calculate", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=calculate, width=20)
calc_button.grid(row=2, column=0, pady=20)

# Bind Enter key to calculate function
root.bind("<Return>", calculate)

# Error message label
error_label = tk.Label(root, text="", font=("Arial", 12), fg="red", bg="#f4f4f9")
error_label.grid(row=3, column=0)

# Output Frame
output_frame = tk.Frame(root, bg="#f4f4f9")
output_frame.grid(row=4, column=0, pady=20, sticky="w")

# Columns for Item, Wallet, and Miscellaneous
item_frame = tk.Frame(output_frame, bg="#f4f4f9")
item_frame.grid(row=0, column=0, padx=20, sticky="w")
tk.Label(item_frame, text="Item Transfer", font=("Helvetica", 14, "bold"), bg="#f4f4f9").grid(row=0, column=0, columnspan=2)

# Item Transfer Fields
item_cost_label = tk.Label(item_frame, text="Item Transfer (Cost):", font=("Arial", 12), bg="#f4f4f9")
item_cost_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
copy_item_cost_button = tk.Button(item_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(item_cost_label.cget("text").split(": ")[1]), width=8)
copy_item_cost_button.grid(row=1, column=1, padx=10, pady=5)

item_cashout_agent_label = tk.Label(item_frame, text="Cashout (Agent):", font=("Arial", 12), bg="#f4f4f9")
item_cashout_agent_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
copy_item_cashout_agent_button = tk.Button(item_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(item_cashout_agent_label.cget("text").split(": ")[1]), width=8)
copy_item_cashout_agent_button.grid(row=2, column=1, padx=10, pady=5)

item_cashout_priyo_label = tk.Label(item_frame, text="Cashout (Priyo):", font=("Arial", 12), bg="#f4f4f9")
item_cashout_priyo_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
copy_item_cashout_priyo_button = tk.Button(item_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(item_cashout_priyo_label.cget("text").split(": ")[1]), width=8)
copy_item_cashout_priyo_button.grid(row=3, column=1, padx=10, pady=5)

wallet_frame = tk.Frame(output_frame, bg="#f4f4f9")
wallet_frame.grid(row=0, column=1, padx=20, sticky="w")
tk.Label(wallet_frame, text="Wallet Transfer", font=("Helvetica", 14, "bold"), bg="#f4f4f9").grid(row=0, column=0, columnspan=2)

# Wallet Transfer Fields
wallet_cost_label = tk.Label(wallet_frame, text="Wallet Transfer (Cost):", font=("Arial", 12), bg="#f4f4f9")
wallet_cost_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
copy_wallet_cost_button = tk.Button(wallet_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(wallet_cost_label.cget("text").split(": ")[1]), width=8)
copy_wallet_cost_button.grid(row=1, column=1, padx=10, pady=5)

wallet_cashout_agent_label = tk.Label(wallet_frame, text="Cashout (Agent):", font=("Arial", 12), bg="#f4f4f9")
wallet_cashout_agent_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
copy_wallet_cashout_agent_button = tk.Button(wallet_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(wallet_cashout_agent_label.cget("text").split(": ")[1]), width=8)
copy_wallet_cashout_agent_button.grid(row=2, column=1, padx=10, pady=5)

wallet_cashout_priyo_label = tk.Label(wallet_frame, text="Cashout (Priyo):", font=("Arial", 12), bg="#f4f4f9")
wallet_cashout_priyo_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
copy_wallet_cashout_priyo_button = tk.Button(wallet_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(wallet_cashout_priyo_label.cget("text").split(": ")[1]), width=8)
copy_wallet_cashout_priyo_button.grid(row=3, column=1, padx=10, pady=5)

# Miscellaneous Frame
misc_frame = tk.Frame(output_frame, bg="#f4f4f9")
misc_frame.grid(row=0, column=2, padx=20, sticky="w")
tk.Label(misc_frame, text="Miscellaneous", font=("Helvetica", 14, "bold"), bg="#f4f4f9").grid(row=0, column=0, columnspan=2)

add_15_label = tk.Label(misc_frame, text="With Steam Tax (15%):", font=("Arial", 12), bg="#f4f4f9")
add_15_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
copy_add_15_button = tk.Button(misc_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(add_15_label.cget("text").split(": ")[1]), width=8)
copy_add_15_button.grid(row=1, column=1, padx=10, pady=5)

minus_15_label = tk.Label(misc_frame, text="Without Steam Tax (15%):", font=("Arial", 12), bg="#f4f4f9")
minus_15_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
copy_minus_15_button = tk.Button(misc_frame, text="Copy", font=("Arial", 10), bg="#2196F3", fg="white", command=lambda: copy_to_clipboard(minus_15_label.cget("text").split(": ")[1]), width=8)
copy_minus_15_button.grid(row=2, column=1, padx=10, pady=5)

root.mainloop()
