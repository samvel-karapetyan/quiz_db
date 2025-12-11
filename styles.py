import tkinter as tk
from tkinter import ttk

class StyleManager:
    def __init__(self, root: tk.Tk):
        self.style = ttk.Style()
        self.setup_styles()
    
    def setup_styles(self) -> None:
        self.style.theme_use('clam')
        
        self.style.configure('Title.TLabel', 
                           font=('Arial', 18, 'bold'),
                           foreground='#ffffff',
                           background='#34495e')
        
        self.style.configure('Heading.TLabel',
                           font=('Arial', 12, 'bold'),
                           foreground='#2c3e50',
                           background='#f5f5f5')
        
        self.style.configure('Primary.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='#ffffff',
                           background='#4a90e2',
                           padding=10,
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Primary.TButton',
                      background=[('active', '#357abd'),
                                ('pressed', '#2a5f8f'),
                                ('disabled', '#b0c4de')],
                      foreground=[('active', '#ffffff'),
                                ('pressed', '#ffffff'),
                                ('disabled', '#888888')])
        
        self.style.configure('Success.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='#ffffff',
                           background='#52c41a',
                           padding=8,
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Success.TButton',
                      background=[('active', '#45a016'),
                                ('pressed', '#388012'),
                                ('disabled', '#b7eb8f')],
                      foreground=[('active', '#ffffff'),
                                ('pressed', '#ffffff'),
                                ('disabled', '#888888')])
        
        self.style.configure('Danger.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='#ffffff',
                           background='#ff4d4f',
                           padding=8,
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Danger.TButton',
                      background=[('active', '#e63946'),
                                ('pressed', '#cc2936'),
                                ('disabled', '#ffb3b5')],
                      foreground=[('active', '#ffffff'),
                                ('pressed', '#ffffff'),
                                ('disabled', '#888888')])
        
        self.style.configure('Warning.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='#ffffff',
                           background='#faad14',
                           padding=8,
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Warning.TButton',
                      background=[('active', '#d48806'),
                                ('pressed', '#ad6800'),
                                ('disabled', '#ffe58f')],
                      foreground=[('active', '#ffffff'),
                                ('pressed', '#ffffff'),
                                ('disabled', '#888888')])
        
        self.style.configure('Info.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='#ffffff',
                           background='#1890ff',
                           padding=8,
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Info.TButton',
                      background=[('active', '#096dd9'),
                                ('pressed', '#0050b3'),
                                ('disabled', '#91d5ff')],
                      foreground=[('active', '#ffffff'),
                                ('pressed', '#ffffff'),
                                ('disabled', '#888888')])
        
        self.style.configure('Card.TFrame',
                           background='#ffffff',
                           relief='flat',
                           borderwidth=1)
        
        self.style.configure('TLabelFrame',
                           background='#ffffff',
                           foreground='#2c3e50',
                           borderwidth=2,
                           relief='solid')
        
        self.style.configure('TLabelFrame.Label',
                           background='#ffffff',
                           foreground='#2c3e50',
                           font=('Arial', 11, 'bold'))

