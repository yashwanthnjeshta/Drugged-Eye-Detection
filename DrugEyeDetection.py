import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import hashlib
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Modern Color Palette
COLORS = {
    "background": "#F8F9FA",
    "card_bg": "#FFFFFF",
    "primary": "#4361EE",
    "secondary": "#3A0CA3",
    "accent": "#7209B7",
    "text": "#212529",
    "success": "#4CC9F0",
    "warning": "#F8961E",
    "error": "#F72585",
    "highlight": "#4895EF",
    "border": "#E9ECEF"
}

# Database setup
def initialize_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT,
            email TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

# Utility functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    return '@' in email and '.' in email.split('@')[-1]

class DrugEyeDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EyeDrug Scan Pro")
        self.root.geometry("1200x750")
        self.root.configure(bg=COLORS["background"])
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom styles
        self.style.configure('.', background=COLORS["background"])
        self.style.configure('TFrame', background=COLORS["background"])
        self.style.configure('TLabel', background=COLORS["background"], foreground=COLORS["text"], font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=COLORS["primary"])
        self.style.configure('Card.TFrame', background=COLORS["card_bg"], borderwidth=1, relief='solid', bordercolor=COLORS["border"])
        self.style.configure('TButton', font=('Segoe UI', 10), borderwidth=0)
        self.style.configure('Primary.TButton', foreground='white', background=COLORS["primary"])
        self.style.map('Primary.TButton',
                      background=[('active', COLORS["secondary"])])
        self.style.configure('Secondary.TButton', foreground='white', background=COLORS["accent"])
        self.style.configure('Drugged.TButton', foreground='white', background=COLORS["error"])
        self.style.configure('NotDrugged.TButton', foreground='white', background=COLORS["success"])
        self.style.configure('TNotebook', background=COLORS["background"])
        self.style.configure('TNotebook.Tab', background=COLORS["background"], padding=[10,5])
        
        # Session variables
        self.current_user = None
        self.logged_in = False
        self.current_image_path = None
        self.detection_result = None
        
        # Show login screen
        self.show_login_screen()
    
    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        self.clear_frame()
        
        # Main container with centered card
        container = ttk.Frame(self.root, style='TFrame')
        container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Center frame
        center_frame = ttk.Frame(container, style='TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Login card
        login_card = ttk.Frame(center_frame, style='Card.TFrame', padding=30)
        login_card.pack()
        
        # App logo and title
        logo_frame = ttk.Frame(login_card, style='TFrame')
        logo_frame.pack(pady=(0,20))
        
        ttk.Label(logo_frame, text="👁️", font=('Segoe UI', 24)).pack()
        ttk.Label(logo_frame, text="EyeDrug Scan Pro", style='Header.TLabel').pack()
        ttk.Label(logo_frame, text="Advanced eye analysis for substance detection").pack()
        
        # Form elements
        form_frame = ttk.Frame(login_card, style='TFrame')
        form_frame.pack()
        
        # Username
        ttk.Label(form_frame, text="Username").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(form_frame, text="Password").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(form_frame, width=30, show="•", font=('Segoe UI', 10))
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Login button
        login_btn = ttk.Button(form_frame, text="Login", style='Primary.TButton', command=self.login)
        login_btn.grid(row=2, column=1, pady=15, sticky=tk.E)
        
        # Register link
        register_frame = ttk.Frame(login_card, style='TFrame')
        register_frame.pack(pady=(10,0))
        
        ttk.Label(register_frame, text="Don't have an account?").pack(side=tk.LEFT)
        register_link = ttk.Label(register_frame, text="Sign up", 
                                foreground=COLORS["primary"], cursor="hand2")
        register_link.pack(side=tk.LEFT)
        register_link.bind("<Button-1>", lambda e: self.show_register_screen())
    
    def show_register_screen(self):
        self.clear_frame()
        
        # Main container with centered card
        container = ttk.Frame(self.root, style='TFrame')
        container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Center frame
        center_frame = ttk.Frame(container, style='TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Register card
        register_card = ttk.Frame(center_frame, style='Card.TFrame', padding=30)
        register_card.pack()
        
        # App logo and title
        logo_frame = ttk.Frame(register_card, style='TFrame')
        logo_frame.pack(pady=(0,20))
        
        ttk.Label(logo_frame, text="👁️", font=('Segoe UI', 24)).pack()
        ttk.Label(logo_frame, text="Create Account", style='Header.TLabel').pack()
        
        # Form elements
        form_frame = ttk.Frame(register_card, style='TFrame')
        form_frame.pack()
        
        # Full Name
        ttk.Label(form_frame, text="Full Name").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.reg_fullname_entry = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.reg_fullname_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.reg_email_entry = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.reg_email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Username
        ttk.Label(form_frame, text="Username").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.reg_username_entry = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        self.reg_username_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(form_frame, text="Password").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.reg_password_entry = ttk.Entry(form_frame, width=30, show="•", font=('Segoe UI', 10))
        self.reg_password_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Confirm Password
        ttk.Label(form_frame, text="Confirm Password").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.reg_confirm_password_entry = ttk.Entry(form_frame, width=30, show="•", font=('Segoe UI', 10))
        self.reg_confirm_password_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Register button
        register_btn = ttk.Button(form_frame, text="Register", style='Primary.TButton', command=self.register)
        register_btn.grid(row=5, column=1, pady=15, sticky=tk.E)
        
        # Back to login link
        login_frame = ttk.Frame(register_card, style='TFrame')
        login_frame.pack(pady=(10,0))
        
        ttk.Label(login_frame, text="Already have an account?").pack(side=tk.LEFT)
        login_link = ttk.Label(login_frame, text="Login", 
                             foreground=COLORS["primary"], cursor="hand2")
        login_link.pack(side=tk.LEFT)
        login_link.bind("<Button-1>", lambda e: self.show_login_screen())
    
    def show_main_app(self):
        self.clear_frame()
        
        # Header with user info
        header = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        header.pack(fill=tk.X, padx=20, pady=10)
        
        user_frame = ttk.Frame(header, style='TFrame')
        user_frame.pack(side=tk.LEFT)
        
        ttk.Label(user_frame, text=f"Welcome back, {self.current_user[1]}", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(user_frame, text="Ready to analyze eye images").pack(anchor=tk.W)
        
        # Logout button
        logout_btn = ttk.Button(header, text="Logout", style='Secondary.TButton', 
                               command=self.logout)
        logout_btn.pack(side=tk.RIGHT)
        
        # Main content area
        main_content = ttk.Frame(self.root, style='TFrame')
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))
        
        # Left panel - Image upload and display
        left_panel = ttk.Frame(main_content, style='TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        
        # Image upload card
        upload_card = ttk.LabelFrame(left_panel, text=" UPLOAD IMAGE ", style='Card.TFrame', padding=15)
        upload_card.pack(fill=tk.X, pady=(0,10))
        
        # Drag and drop area
        self.drop_area = ttk.Label(upload_card, text="Drag & drop eye image here\nor click to browse", 
                                 background="#F1F3F5", relief='solid', borderwidth=1)
        self.drop_area.pack(fill=tk.BOTH, expand=True, pady=5)
        self.drop_area.bind("<Button-1>", lambda e: self.browse_files())
        
        # Image display card
        self.image_card = ttk.LabelFrame(left_panel, text=" IMAGE PREVIEW ", style='Card.TFrame', padding=15)
        self.image_card.pack(fill=tk.BOTH, expand=True)
        
        self.image_label = ttk.Label(self.image_card, background=COLORS["card_bg"])
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Results and analysis
        right_panel = ttk.Frame(main_content, style='TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10,0))
        
        # Results card
        results_card = ttk.LabelFrame(right_panel, text=" ANALYSIS RESULTS ", style='Card.TFrame', padding=15)
        results_card.pack(fill=tk.BOTH, expand=True)
        
        # Result display area
        self.result_text = tk.Text(results_card, height=10, width=50, wrap=tk.WORD, 
                                 font=('Segoe UI', 10), bg=COLORS["card_bg"], 
                                 fg=COLORS["text"], insertbackground=COLORS["text"],
                                 borderwidth=0, highlightthickness=0)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Classification buttons
        btn_frame = ttk.Frame(results_card, style='TFrame')
        btn_frame.pack(fill=tk.X, pady=(10,0))
        
        ttk.Button(btn_frame, text="🚨 Mark as Drugged", 
                  style='Drugged.TButton', command=lambda: self.classify_image("Drugged")).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="✅ Mark as Clean", 
                  style='NotDrugged.TButton', command=lambda: self.classify_image("Not Drugged")).pack(side=tk.RIGHT, expand=True, padx=5)
        
        # Analysis tabs
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        
        # Histogram tab
        hist_tab = ttk.Frame(notebook, style='TFrame')
        notebook.add(hist_tab, text="Histogram")
        self.hist_tab = hist_tab
        
        # Pixel analysis tab
        pixel_tab = ttk.Frame(notebook, style='TFrame')
        notebook.add(pixel_tab, text="Pixel Analysis")
        self.pixel_tab = pixel_tab
        
        # Action buttons
        action_frame = ttk.Frame(right_panel, style='TFrame')
        action_frame.pack(fill=tk.X, pady=(10,0))
        
        ttk.Button(action_frame, text="Save Report", style='Primary.TButton', command=self.save_report).pack(side=tk.RIGHT)
        ttk.Button(action_frame, text="Help", style='Secondary.TButton', command=self.show_help).pack(side=tk.RIGHT, padx=5)
    
    def classify_image(self, classification):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please upload an image first", parent=self.root)
            return
        
        img = cv2.imread(self.current_image_path)
        
        # Calculate confidence
        confidence = self.calculate_confidence(img, classification)
        
        if classification == "Drugged":
            color = COLORS["error"]
            emoji = "🚨"
            conclusion = "Substance use likely detected"
        else:
            color = COLORS["success"]
            emoji = "✅"
            conclusion = "No signs of substance use"
        
        self.detection_result = f"{classification} (Confidence: {confidence}%)"
        
        # Update result display
        self.result_text.delete(1.0, tk.END)
        self.result_text.tag_configure("header", font=('Segoe UI', 12, 'bold'))
        self.result_text.tag_configure("result", foreground=color, font=('Segoe UI', 11, 'bold'))
        self.result_text.tag_configure("analysis", font=('Segoe UI', 10))
        
        self.result_text.insert(tk.END, "Analysis Result\n", "header")
        self.result_text.insert(tk.END, f"{emoji} {conclusion}\n\n", "result")
        
        # Add detailed analysis
        analysis = self.get_detailed_analysis(img, classification)
        self.result_text.insert(tk.END, "Detailed Findings:\n", "header")
        self.result_text.insert(tk.END, f"{analysis}\n\n", "analysis")
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.result_text.insert(tk.END, f"Analysis performed: {timestamp}\n", "analysis")
    
    def calculate_confidence(self, img, classification):
        """Calculate confidence percentage based on multiple factors"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 1. Redness analysis (bloodshot eyes)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red, upper_red)
        red_pixels = cv2.countNonZero(mask_red)
        red_ratio = red_pixels / (img.shape[0] * img.shape[1])
        
        # 2. Pupil size analysis
        pupil_size = self.analyze_pupil_size(img)
        
        # 3. Sclera whiteness analysis
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([255, 30, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        white_pixels = cv2.countNonZero(mask_white)
        white_ratio = white_pixels / (img.shape[0] * img.shape[1])
        
        # Calculate confidence
        if classification == "Drugged":
            confidence = min(95, 50 + (red_ratio * 200) + (abs(pupil_size - 0.3) * 100))
        else:
            confidence = min(95, 50 + (white_ratio * 100) + (1 - abs(pupil_size - 0.3) * 100))
        
        return round(confidence)
    
    def analyze_pupil_size(self, img):
        """Analyze pupil size relative to iris"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, 
                                 minDist=100, param1=50, param2=30, 
                                 minRadius=10, maxRadius=100)
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            (x, y, r) = circles[0]
            iris_radius = r * 3
            return min(1.0, r / iris_radius)
        return 0.3
    
    def get_detailed_analysis(self, img, classification):
        """Generate detailed analysis text"""
        analysis = []
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Redness analysis
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red, upper_red)
        red_pixels = cv2.countNonZero(mask_red)
        red_ratio = red_pixels / (img.shape[0] * img.shape[1])
        
        if red_ratio > 0.1:
            analysis.append(f"- Significant redness detected ({round(red_ratio*100)}% coverage)")
        else:
            analysis.append("- Normal redness levels")
        
        # Pupil analysis
        pupil_size = self.analyze_pupil_size(img)
        if pupil_size < 0.2:
            analysis.append("- Pupils appear constricted")
        elif pupil_size > 0.5:
            analysis.append("- Pupils appear dilated")
        else:
            analysis.append("- Normal pupil size")
        
        # Sclera whiteness
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([255, 30, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        white_pixels = cv2.countNonZero(mask_white)
        white_ratio = white_pixels / (img.shape[0] * img.shape[1])
        
        if white_ratio < 0.3:
            analysis.append("- Sclera appears discolored")
        else:
            analysis.append("- Sclera appears normal")
        
        return "\n".join(analysis)
    
    def save_report(self):
        if not self.current_image_path or not self.detection_result:
            messagebox.showwarning("Warning", "No analysis results to save", parent=self.root)
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile="EyeDrug_Report.txt"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write("=== EyeDrug Scan Pro Report ===\n\n")
                    f.write(f"User: {self.current_user[1]}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Image: {os.path.basename(self.current_image_path)}\n")
                    f.write(f"Result: {self.detection_result}\n\n")
                    f.write(self.result_text.get("1.0", tk.END))
                
                messagebox.showinfo("Success", "Report saved successfully!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {str(e)}", parent=self.root)
    
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help Center")
        help_window.geometry("600x500")
        help_window.configure(bg=COLORS["background"])
        
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Getting Started tab
        start_tab = ttk.Frame(notebook, style='TFrame')
        notebook.add(start_tab, text="Getting Started")
        
        start_text = """
        How to use EyeDrug Scan Pro:
        
        1. Upload an eye image using the drag & drop area
        2. View the automatic analysis results
        3. Confirm the classification using:
           - 🚨 Mark as Drugged
           - ✅ Mark as Clean
        4. Review detailed analysis tabs
        5. Save your report when finished
        
        For best results:
        - Use high-quality, well-lit images
        - Center the eye in the frame
        - Avoid flash reflections
        """
        ttk.Label(start_tab, text=start_text, justify=tk.LEFT).pack(padx=20, pady=20)
        
        # Analysis tab
        analysis_tab = ttk.Frame(notebook, style='TFrame')
        notebook.add(analysis_tab, text="Understanding Results")
        
        analysis_text = """
        Understanding the Analysis:
        
        Detection Factors:
        - Redness: Measures bloodshot appearance
        - Pupil Size: Detects abnormal dilation/constriction
        - Sclera Whiteness: Checks for discoloration
        
        Confidence Scores:
        - 90-100%: Very confident
        - 70-89%: Likely correct
        - 50-69%: Possible indication
        - Below 50%: Inconclusive
        
        The system combines these factors to provide
        the most accurate assessment possible.
        """
        ttk.Label(analysis_tab, text=analysis_text, justify=tk.LEFT).pack(padx=20, pady=20)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password", parent=self.root)
            return
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[2] == hash_password(password):
            self.current_user = user
            self.logged_in = True
            self.show_main_app()
        else:
            messagebox.showerror("Error", "Invalid username or password", parent=self.root)
    
    def register(self):
        fullname = self.reg_fullname_entry.get()
        email = self.reg_email_entry.get()
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        
        if not all([fullname, email, username, password, confirm_password]):
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords don't match", parent=self.root)
            return
        
        if not validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email", parent=self.root)
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters", parent=self.root)
            return
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            conn.close()
            messagebox.showerror("Error", "Username already exists", parent=self.root)
            return
        
        hashed_password = hash_password(password)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (username, password, fullname, email, created_at) VALUES (?, ?, ?, ?, ?)",
                       (username, hashed_password, fullname, email, created_at))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Account created! Please login.", parent=self.root)
        self.show_login_screen()
    
    def logout(self):
        self.current_user = None
        self.logged_in = False
        self.current_image_path = None
        self.detection_result = None
        self.show_login_screen()
    
    def browse_files(self):
        filetypes = (
            ("Image files", "*.jpg *.jpeg *.png"),
            ("All files", "*.*")
        )
        
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select an eye image",
            filetypes=filetypes
        )
        
        if filename:
            self.current_image_path = filename
            self.process_image(filename)
    
    def process_image(self, image_path):
        try:
            self.result_text.delete(1.0, tk.END)
            self.display_image(image_path)
            
            # Perform automatic detection
            result = self.automatic_detection(image_path)
            
            self.result_text.tag_configure("header", font=('Segoe UI', 12, 'bold'))
            self.result_text.tag_configure("result", foreground=COLORS["warning"], font=('Segoe UI', 11, 'bold'))
            
            self.result_text.insert(tk.END, "Initial Analysis\n", "header")
            self.result_text.insert(tk.END, f"{result}\n\n", "result")
            self.result_text.insert(tk.END, "Please confirm classification using buttons above\n", "header")
            
            self.generate_visualizations(image_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}", parent=self.root)
    
    def automatic_detection(self, image_path):
        img = cv2.imread(image_path)
        
        drugged_confidence = self.calculate_confidence(img, "Drugged")
        not_drugged_confidence = self.calculate_confidence(img, "Not Drugged")
        
        if drugged_confidence > not_drugged_confidence + 15:
            return f"🚨 Suggested: Drugged (Confidence: {drugged_confidence}%)"
        elif not_drugged_confidence > drugged_confidence + 15:
            return f"✅ Suggested: Clean (Confidence: {not_drugged_confidence}%)"
        else:
            return "❓ Inconclusive - Please review and classify manually"
    
    def display_image(self, image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((400, 400))
            
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image: {str(e)}", parent=self.root)
    
    def generate_visualizations(self, image_path):
        try:
            for widget in self.hist_tab.winfo_children():
                widget.destroy()
            for widget in self.pixel_tab.winfo_children():
                widget.destroy()
            
            self.generate_histogram(image_path)
            self.generate_pixel_chart(image_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate visualizations: {str(e)}", parent=self.root)
    
    def generate_histogram(self, image_path):
        img = cv2.imread(image_path)
        
        fig = plt.figure(figsize=(5, 3), facecolor=COLORS["card_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["card_bg"])
        
        colors = ['blue', 'green', 'red']
        labels = ['Blue', 'Green', 'Red']
        
        for i, color in enumerate(colors):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            ax.plot(hist, color=color, label=labels[i])
            ax.fill_between(range(256), hist.ravel(), color=color, alpha=0.3)
        
        ax.set_title('Color Histogram', color=COLORS["text"])
        ax.set_xlabel('Pixel Value', color=COLORS["text"])
        ax.set_ylabel('Frequency', color=COLORS["text"])
        ax.tick_params(colors=COLORS["text"])
        ax.legend(facecolor=COLORS["card_bg"], edgecolor=COLORS["card_bg"])
        
        for spine in ax.spines.values():
            spine.set_color(COLORS["border"])
        
        canvas = FigureCanvasTkAgg(fig, master=self.hist_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def generate_pixel_chart(self, image_path):
        img = Image.open(image_path)
        pixels = np.array(img)
        h, w, c = pixels.shape
        pixels = pixels.reshape((h * w, c))
        
        if len(pixels) > 10000:
            pixels = pixels[np.random.choice(len(pixels), 10000, replace=False)]
        
        fig = plt.figure(figsize=(5, 3), facecolor=COLORS["card_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["card_bg"])
        
        scatter = ax.scatter(pixels[:, 0], pixels[:, 1], c=pixels/255.0, s=10, alpha=0.6)
        
        ax.set_title('Pixel Color Distribution', color=COLORS["text"])
        ax.set_xlabel('Red Channel', color=COLORS["text"])
        ax.set_ylabel('Green Channel', color=COLORS["text"])
        ax.tick_params(colors=COLORS["text"])
        
        for spine in ax.spines.values():
            spine.set_color(COLORS["border"])
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Color Intensity', color=COLORS["text"])
        cbar.ax.yaxis.set_tick_params(color=COLORS["text"])
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=COLORS["text"])
        
        canvas = FigureCanvasTkAgg(fig, master=self.pixel_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = DrugEyeDetectionApp(root)
    root.mainloop()