import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from database import Database
from styles import StyleManager

class AuthWindow:
    def __init__(self, db: Database, on_success: Callable):
        self.db = db
        self.on_success = on_success
        self.current_user = None
        
        self.window = tk.Tk()
        self.window.title("Quiz System - Login")
        self.window.geometry("450x400")
        self.window.resizable(False, False)
        self.window.configure(bg='#f5f5f5')
        
        self.style_manager = StyleManager(self.window)
        self.create_widgets()
    
    def create_widgets(self) -> None:
        header_frame = tk.Frame(self.window, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, text="Quiz System", style='Title.TLabel')
        title_label.pack(pady=25)
        
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        login_frame = ttk.LabelFrame(main_frame, text="Login / Register", padding="25")
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(login_frame, text="Username:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.username_entry = ttk.Entry(login_frame, width=30, font=('Arial', 11))
        self.username_entry.grid(row=0, column=1, pady=10, padx=10, sticky=tk.EW)
        
        ttk.Label(login_frame, text="Password:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*", font=('Arial', 11))
        self.password_entry.grid(row=1, column=1, pady=10, padx=10, sticky=tk.EW)
        
        login_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=25)
        
        ttk.Button(button_frame, text="Login", command=self.login, 
                  style='Primary.TButton', width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Register", command=self.register, 
                  style='Success.TButton', width=15).pack(side=tk.LEFT, padx=10)
        
        info_label = ttk.Label(main_frame, 
                              text="Admin login: username='admin', password='admin'",
                              font=('Arial', 9), foreground='#666666', wraplength=400)
        info_label.pack(pady=(15, 0))
        
        self.username_entry.focus()
        self.password_entry.bind("<Return>", lambda e: self.login())
    
    def login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            role_text = "Administrator" if user["role"] == "admin" else "User"
            messagebox.showinfo("Login Successful", f"Welcome {user['username']}!\nYou are logged in as: {role_text}")
            self.window.destroy()
            self.on_success(user)
        else:
            messagebox.showerror("Error", "Invalid username or password.")
    
    def register(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if username.lower() == "admin":
            messagebox.showerror("Error", "Cannot register as 'admin'. Use the admin login instead.")
            return
        
        try:
            self.db.create_user(username, password, "user")
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.password_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def run(self) -> None:
        self.window.mainloop()
