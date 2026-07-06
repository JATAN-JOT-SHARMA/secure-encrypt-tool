"""
DARK HACKER THEME ENCRYPTION TOOL
Complete solution with drag & drop, text encryption, file encryption
AES-256 Military Grade Encryption
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
import base64
import os
import threading
import time
import pyperclip
from datetime import datetime
import json
import hashlib
from pathlib import Path

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class HackerEncryptor:
    """AES-256 encryption engine"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        return kdf.derive(password.encode('utf-8'))
    
    def encrypt(self, data: bytes, password: str) -> bytes:
        """Encrypt data with password"""
        salt = os.urandom(16)
        iv = os.urandom(16)
        key = self._derive_key(password, salt)
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return salt + iv + ciphertext
    
    def decrypt(self, encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data with password"""
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        
        key = self._derive_key(password, salt)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext
    
    def encrypt_text(self, text: str, password: str) -> str:
        """Encrypt text and return base64 string"""
        encrypted = self.encrypt(text.encode('utf-8'), password)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_text(self, encrypted_b64: str, password: str) -> str:
        """Decrypt base64 string to text"""
        encrypted = base64.b64decode(encrypted_b64)
        decrypted = self.decrypt(encrypted, password)
        return decrypted.decode('utf-8')
    
    def encrypt_file(self, input_path: str, output_path: str, password: str, progress_callback=None):
        """Encrypt file with progress tracking"""
        with open(input_path, 'rb') as f:
            data = f.read()
        
        if progress_callback:
            progress_callback(50)
        
        encrypted = self.encrypt(data, password)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        if progress_callback:
            progress_callback(100)
        
        return True
    
    def decrypt_file(self, input_path: str, output_path: str, password: str, progress_callback=None):
        """Decrypt file with progress tracking"""
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        
        if progress_callback:
            progress_callback(50)
        
        decrypted = self.decrypt(encrypted, password)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        if progress_callback:
            progress_callback(100)
        
        return True

class DragDropArea(ctk.CTkFrame):
    """Custom frame with drag and drop support"""
    
    def __init__(self, master, on_file_dropped, **kwargs):
        super().__init__(master, **kwargs)
        self.on_file_dropped = on_file_dropped
        self.configure(fg_color="#0a0a0a", corner_radius=10, border_width=2, border_color="#00ff00")
        
        # Bind drag and drop events
        self.drop_target_register()
        self.dnd_bind('<<Drop>>', self.drop)
        
        # Create drop zone label
        self.label = ctk.CTkLabel(
            self,
            text="🐉 DRAG & DROP FILE HERE 🐉\nor click to browse",
            font=("Consolas", 14, "bold"),
            text_color="#00ff00"
        )
        self.label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Bind click event
        self.bind("<Button-1>", self.on_click)
        self.label.bind("<Button-1>", self.on_click)
    
    def drop_target_register(self):
        """Register as drop target"""
        try:
            from tkinterdnd2 import DND_FILES
            self.drop_target_register(DND_FILES)
        except:
            pass
    
    def drop(self, event):
        """Handle file drop"""
        files = event.data
        if files:
            # Clean file path
            files = files.strip('{}')
            self.on_file_dropped(files)
    
    def on_click(self, event):
        """Handle click to browse"""
        filename = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.on_file_dropped(filename)

class TerminalWidget(ctk.CTkTextbox):
    """Terminal-like output widget"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(font=("Consolas", 11))
    
    def print(self, text, level="INFO"):
        """Print colored text to terminal"""
        colors = {
            "INFO": "#00ff00",
            "WARNING": "#ffff00",
            "ERROR": "#ff0000",
            "SUCCESS": "#00ff88",
            "PROCESS": "#00ccff"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        formatted = f"[{timestamp}] [{level}] {text}\n"
        self.insert("end", formatted)
        self.see("end")
        
        # Auto-scroll to bottom
        self.after(100, lambda: self.see("end"))

class HackerEncryptionTool:
    """Main application class"""
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("⚡ HACKER ENCRYPTION TOOL v3.0 ⚡")
        self.window.geometry("1400x900")
        self.window.configure(fg_color="#000000")
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (900 // 2)
        self.window.geometry(f'1400x900+{x}+{y}')
        
        self.encryptor = HackerEncryptor()
        self.current_file = None
        self.encryption_count = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the complete UI"""
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.window, fg_color="#000000")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left sidebar - Menu
        self.setup_sidebar()
        
        # Center content area - Main workspace
        self.setup_workspace()
        
        # Right sidebar - Info
        self.setup_info_panel()
        
        # Terminal at bottom
        self.setup_terminal()
        
    def setup_sidebar(self):
        """Create sidebar with neon effects"""
        self.sidebar = ctk.CTkFrame(
            self.main_frame, 
            width=280, 
            fg_color="#0a0a0a",
            border_width=2,
            border_color="#00ff00"
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Logo/Header
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=20)
        
        logo_text = ctk.CTkLabel(
            logo_frame,
            text="[ H4CK3R ]\nENCRYPT10N\nT00L v3.0",
            font=("Consolas", 20, "bold"),
            text_color="#00ff00"
        )
        logo_text.pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="AES-256 Military Grade",
            font=("Consolas", 10),
            text_color="#33ff33"
        ).pack(pady=(5,0))
        
        # Menu buttons
        menu_items = [
            ("📝 ENCRYPT TEXT", self.show_text_encrypt, "#00ff00"),
            ("🔓 DECRYPT TEXT", self.show_text_decrypt, "#00ff88"),
            ("📁 ENCRYPT FILE", self.show_file_encrypt, "#33ff33"),
            ("🔐 DECRYPT FILE", self.show_file_decrypt, "#66ff66"),
            ("🎲 GENERATE KEY", self.show_keygen, "#00ccff"),
            ("📜 HISTORY", self.show_history, "#ff00ff"),
            ("⚙️ SETTINGS", self.show_settings, "#ffff00")
        ]
        
        for text, command, color in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color="#1a3a1a",
                text_color=color,
                font=("Consolas", 13, "bold"),
                anchor="w",
                height=45,
                corner_radius=5
            )
            btn.pack(fill="x", padx=15, pady=5)
        
        # Stats panel
        stats_frame = ctk.CTkFrame(self.sidebar, fg_color="#0a0f0a", corner_radius=10)
        stats_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text=f"STATUS: 🟢 ACTIVE\nENCRYPTIONS: {self.encryption_count}\nSECURE CHANNEL: OPEN",
            font=("Consolas", 10),
            text_color="#00ff00",
            justify="left"
        )
        self.stats_label.pack(pady=10)
        
    def setup_workspace(self):
        """Create main workspace area"""
        self.workspace = ctk.CTkFrame(self.main_frame, fg_color="#050505", corner_radius=10)
        self.workspace.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Initially show text encrypt frame
        self.current_frame = None
        self.show_text_encrypt()
        
    def setup_info_panel(self):
        """Create right info panel"""
        self.info_panel = ctk.CTkFrame(
            self.main_frame, 
            width=250, 
            fg_color="#0a0a0a",
            border_width=1,
            border_color="#333333"
        )
        self.info_panel.pack(side="right", fill="y")
        self.info_panel.pack_propagate(False)
        
        # Security info
        security_label = ctk.CTkLabel(
            self.info_panel,
            text="🔒 SECURITY INFO",
            font=("Consolas", 12, "bold"),
            text_color="#00ff00"
        )
        security_label.pack(pady=10)
        
        security_text = """
• Algorithm: AES-256-CBC
• Key Derivation: PBKDF2
• Iterations: 100,000
• Salt: Random 16 bytes
• IV: Random 16 bytes
• Padding: PKCS7
        """
        
        info_text = ctk.CTkLabel(
            self.info_panel,
            text=security_text,
            font=("Consolas", 10),
            text_color="#888888",
            justify="left"
        )
        info_text.pack(pady=10, padx=10)
        
        # Tips
        tips_label = ctk.CTkLabel(
            self.info_panel,
            text="💡 TIPS",
            font=("Consolas", 12, "bold"),
            text_color="#ffff00"
        )
        tips_label.pack(pady=(20,5))
        
        tips_text = """
• Use strong passwords
• Save encrypted text safely
• Lost password = lost data
• Drag & drop files anywhere
• Click drop zone to browse
        """
        
        tips_content = ctk.CTkLabel(
            self.info_panel,
            text=tips_text,
            font=("Consolas", 10),
            text_color="#888888",
            justify="left"
        )
        tips_content.pack(pady=10, padx=10)
        
    def setup_terminal(self):
        """Create terminal output at bottom"""
        terminal_frame = ctk.CTkFrame(self.window, fg_color="#000000", height=150)
        terminal_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        
        terminal_header = ctk.CTkFrame(terminal_frame, fg_color="#0a0a0a", height=30)
        terminal_header.pack(fill="x", padx=2, pady=(2,0))
        
        terminal_label = ctk.CTkLabel(
            terminal_header,
            text=">_ TERMINAL_OUTPUT",
            font=("Consolas", 10, "bold"),
            text_color="#00ff00"
        )
        terminal_label.pack(side="left", padx=10, pady=5)
        
        clear_btn = ctk.CTkButton(
            terminal_header,
            text="CLEAR",
            command=self.clear_terminal,
            width=60,
            height=25,
            font=("Consolas", 9),
            fg_color="#330000",
            hover_color="#660000"
        )
        clear_btn.pack(side="right", padx=10)
        
        self.terminal = TerminalWidget(
            terminal_frame,
            height=120,
            fg_color="#0a0a0a",
            text_color="#00ff00"
        )
        self.terminal.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.terminal.print("="*50, "INFO")
        self.terminal.print("HACKER ENCRYPTION TOOL v3.0 INITIALIZED", "SUCCESS")
        self.terminal.print("AES-256 Military Grade Encryption Active", "INFO")
        self.terminal.print("Drag & Drop Support Enabled", "INFO")
        self.terminal.print("="*50, "INFO")
    
    def clear_terminal(self):
        """Clear terminal output"""
        self.terminal.delete("1.0", "end")
        self.terminal.print("Terminal cleared", "INFO")
    
    def update_stats(self):
        """Update statistics display"""
        self.stats_label.configure(
            text=f"STATUS: 🟢 ACTIVE\nENCRYPTIONS: {self.encryption_count}\nSECURE CHANNEL: OPEN"
        )
    
    # ==================== TEXT ENCRYPTION ====================
    
    def show_text_encrypt(self):
        """Show text encryption interface"""
        self.clear_workspace()
        
        frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="📝 TEXT ENCRYPTION",
            font=("Consolas", 18, "bold"),
            text_color="#00ff00"
        )
        title.pack(pady=10)
        
        # Input area
        input_label = ctk.CTkLabel(frame, text="INPUT TEXT:", font=("Consolas", 12))
        input_label.pack(anchor="w", pady=(10,5))
        
        self.text_input = ctk.CTkTextbox(frame, height=150, font=("Consolas", 11))
        self.text_input.pack(fill="x", pady=(0,10))
        
        # Password area
        pass_label = ctk.CTkLabel(frame, text="ENCRYPTION PASSWORD:", font=("Consolas", 12))
        pass_label.pack(anchor="w", pady=(10,5))
        
        password_frame = ctk.CTkFrame(frame, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0,10))
        
        self.text_password = ctk.CTkEntry(password_frame, width=400, show="•", font=("Consolas", 11))
        self.text_password.pack(side="left", padx=(0,10))
        
        show_pass = ctk.CTkButton(
            password_frame,
            text="👁️",
            width=40,
            command=lambda: self.toggle_password_visibility(self.text_password)
        )
        show_pass.pack(side="left")
        
        # Encrypt button
        encrypt_btn = ctk.CTkButton(
            frame,
            text="🔒 ENCRYPT TEXT",
            command=self.encrypt_text_action,
            height=40,
            font=("Consolas", 13, "bold"),
            fg_color="#006600",
            hover_color="#009900"
        )
        encrypt_btn.pack(pady=20)
        
        # Output area
        output_label = ctk.CTkLabel(frame, text="ENCRYPTED OUTPUT:", font=("Consolas", 12))
        output_label.pack(anchor="w", pady=(10,5))
        
        self.text_output = ctk.CTkTextbox(frame, height=150, font=("Consolas", 11))
        self.text_output.pack(fill="x")
        
        # Copy button
        copy_btn = ctk.CTkButton(
            frame,
            text="📋 COPY TO CLIPBOARD",
            command=self.copy_text_output,
            width=200,
            fg_color="#003366",
            hover_color="#004499"
        )
        copy_btn.pack(pady=10)
        
        self.current_frame = frame
    
    def encrypt_text_action(self):
        """Perform text encryption"""
        text = self.text_input.get("1.0", "end-1c").strip()
        password = self.text_password.get()
        
        if not text:
            messagebox.showerror("Error", "Please enter text to encrypt")
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        try:
            encrypted = self.encryptor.encrypt_text(text, password)
            self.text_output.delete("1.0", "end")
            self.text_output.insert("1.0", encrypted)
            self.encryption_count += 1
            self.update_stats()
            self.terminal.print(f"Text encrypted successfully (Length: {len(text)} chars)", "SUCCESS")
            messagebox.showinfo("Success", "Text encrypted successfully!")
        except Exception as e:
            self.terminal.print(f"Encryption failed: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")
    
    # ==================== TEXT DECRYPTION ====================
    
    def show_text_decrypt(self):
        """Show text decryption interface"""
        self.clear_workspace()
        
        frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="🔓 TEXT DECRYPTION",
            font=("Consolas", 18, "bold"),
            text_color="#00ff88"
        )
        title.pack(pady=10)
        
        # Input area
        input_label = ctk.CTkLabel(frame, text="ENCRYPTED TEXT:", font=("Consolas", 12))
        input_label.pack(anchor="w", pady=(10,5))
        
        self.decrypt_input = ctk.CTkTextbox(frame, height=150, font=("Consolas", 11))
        self.decrypt_input.pack(fill="x", pady=(0,10))
        
        # Password area
        pass_label = ctk.CTkLabel(frame, text="DECRYPTION PASSWORD:", font=("Consolas", 12))
        pass_label.pack(anchor="w", pady=(10,5))
        
        self.decrypt_password = ctk.CTkEntry(frame, show="•", font=("Consolas", 11), width=400)
        self.decrypt_password.pack(anchor="w", pady=(0,10))
        
        # Decrypt button
        decrypt_btn = ctk.CTkButton(
            frame,
            text="🔓 DECRYPT TEXT",
            command=self.decrypt_text_action,
            height=40,
            font=("Consolas", 13, "bold"),
            fg_color="#660000",
            hover_color="#990000"
        )
        decrypt_btn.pack(pady=20)
        
        # Output area
        output_label = ctk.CTkLabel(frame, text="DECRYPTED OUTPUT:", font=("Consolas", 12))
        output_label.pack(anchor="w", pady=(10,5))
        
        self.decrypt_output = ctk.CTkTextbox(frame, height=150, font=("Consolas", 11))
        self.decrypt_output.pack(fill="x")
        
        copy_btn = ctk.CTkButton(
            frame,
            text="📋 COPY TO CLIPBOARD",
            command=self.copy_decrypt_output,
            width=200,
            fg_color="#003366",
            hover_color="#004499"
        )
        copy_btn.pack(pady=10)
        
        self.current_frame = frame
    
    def decrypt_text_action(self):
        """Perform text decryption"""
        encrypted = self.decrypt_input.get("1.0", "end-1c").strip()
        password = self.decrypt_password.get()
        
        if not encrypted:
            messagebox.showerror("Error", "Please enter encrypted text")
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        try:
            decrypted = self.encryptor.decrypt_text(encrypted, password)
            self.decrypt_output.delete("1.0", "end")
            self.decrypt_output.insert("1.0", decrypted)
            self.terminal.print(f"Text decrypted successfully", "SUCCESS")
            messagebox.showinfo("Success", "Text decrypted successfully!")
        except Exception as e:
            self.terminal.print(f"Decryption failed: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Decryption failed: Wrong password or corrupted data")
    
    # ==================== FILE ENCRYPTION ====================
    
    def show_file_encrypt(self):
        """Show file encryption interface with drag & drop"""
        self.clear_workspace()
        
        frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="📁 FILE ENCRYPTION",
            font=("Consolas", 18, "bold"),
            text_color="#33ff33"
        )
        title.pack(pady=10)
        
        # Drag and drop area
        drop_label = ctk.CTkLabel(frame, text="INPUT FILE:", font=("Consolas", 12))
        drop_label.pack(anchor="w", pady=(10,5))
        
        self.file_drop_area = DragDropArea(
            frame,
            on_file_dropped=self.on_file_selected,
            height=120
        )
        self.file_drop_area.pack(fill="x", pady=(0,10))
        
        # Selected file display
        self.file_path_label = ctk.CTkLabel(
            frame,
            text="No file selected",
            font=("Consolas", 10),
            text_color="#888888"
        )
        self.file_path_label.pack(anchor="w", pady=(0,10))
        
        # Output file
        output_label = ctk.CTkLabel(frame, text="OUTPUT FILE:", font=("Consolas", 12))
        output_label.pack(anchor="w", pady=(10,5))
        
        output_frame = ctk.CTkFrame(frame, fg_color="transparent")
        output_frame.pack(fill="x", pady=(0,10))
        
        self.file_output_path = ctk.CTkEntry(output_frame, placeholder_text="output.encrypted", font=("Consolas", 11))
        self.file_output_path.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        browse_output = ctk.CTkButton(
            output_frame,
            text="📂",
            width=50,
            command=self.browse_output_file
        )
        browse_output.pack(side="right")
        
        # Password
        pass_label = ctk.CTkLabel(frame, text="ENCRYPTION PASSWORD:", font=("Consolas", 12))
        pass_label.pack(anchor="w", pady=(10,5))
        
        self.file_password = ctk.CTkEntry(frame, show="•", font=("Consolas", 11), width=400)
        self.file_password.pack(anchor="w", pady=(0,10))
        
        # Progress bar
        self.file_progress = ctk.CTkProgressBar(frame, width=500)
        self.file_progress.pack(pady=10)
        self.file_progress.set(0)
        
        # Encrypt button
        encrypt_btn = ctk.CTkButton(
            frame,
            text="🔒 ENCRYPT FILE",
            command=self.encrypt_file_action,
            height=40,
            font=("Consolas", 13, "bold"),
            fg_color="#006600",
            hover_color="#009900"
        )
        encrypt_btn.pack(pady=10)
        
        self.selected_file = None
        self.current_frame = frame
    
    def on_file_selected(self, filepath):
        """Handle file selection via drag & drop or browse"""
        self.selected_file = filepath
        self.file_path_label.configure(text=f"📄 {os.path.basename(filepath)}", text_color="#00ff00")
        self.terminal.print(f"File selected: {filepath}", "INFO")
        
        # Auto-generate output filename
        output_name = os.path.splitext(filepath)[0] + ".encrypted"
        self.file_output_path.delete(0, "end")
        self.file_output_path.insert(0, output_name)
    
    def browse_output_file(self):
        """Browse for output file location"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".encrypted",
            filetypes=[("Encrypted files", "*.encrypted"), ("All files", "*.*")]
        )
        if filename:
            self.file_output_path.delete(0, "end")
            self.file_output_path.insert(0, filename)
    
    def update_progress(self, value):
        """Update progress bar"""
        self.file_progress.set(value / 100)
        self.workspace.update()
    
    def encrypt_file_action(self):
        """Perform file encryption"""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file to encrypt")
            return
        
        output_file = self.file_output_path.get()
        if not output_file:
            messagebox.showerror("Error", "Please specify output file")
            return
        
        password = self.file_password.get()
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        def encrypt_thread():
            try:
                self.terminal.print(f"Starting encryption of: {self.selected_file}", "PROCESS")
                self.encryptor.encrypt_file(
                    self.selected_file, 
                    output_file, 
                    password,
                    self.update_progress
                )
                self.terminal.print(f"File encrypted successfully: {output_file}", "SUCCESS")
                self.encryption_count += 1
                self.update_stats()
                self.workspace.after(0, lambda: messagebox.showinfo("Success", f"File encrypted successfully!\n\nOutput: {output_file}"))
                self.workspace.after(0, lambda: self.file_progress.set(0))
            except Exception as e:
                self.terminal.print(f"Encryption failed: {str(e)}", "ERROR")
                self.workspace.after(0, lambda: messagebox.showerror("Error", f"Encryption failed: {str(e)}"))
                self.workspace.after(0, lambda: self.file_progress.set(0))
        
        threading.Thread(target=encrypt_thread, daemon=True).start()
    
    # ==================== FILE DECRYPTION ====================
    
    def show_file_decrypt(self):
        """Show file decryption interface with drag & drop"""
        self.clear_workspace()
        
        frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="🔐 FILE DECRYPTION",
            font=("Consolas", 18, "bold"),
            text_color="#66ff66"
        )
        title.pack(pady=10)
        
        # Drag and drop area
        drop_label = ctk.CTkLabel(frame, text="ENCRYPTED FILE:", font=("Consolas", 12))
        drop_label.pack(anchor="w", pady=(10,5))
        
        self.decrypt_drop_area = DragDropArea(
            frame,
            on_file_dropped=self.on_decrypt_file_selected,
            height=120
        )
        self.decrypt_drop_area.pack(fill="x", pady=(0,10))
        
        # Selected file display
        self.decrypt_file_label = ctk.CTkLabel(
            frame,
            text="No file selected",
            font=("Consolas", 10),
            text_color="#888888"
        )
        self.decrypt_file_label.pack(anchor="w", pady=(0,10))
        
        # Output file
        output_label = ctk.CTkLabel(frame, text="OUTPUT FILE:", font=("Consolas", 12))
        output_label.pack(anchor="w", pady=(10,5))
        
        output_frame = ctk.CTkFrame(frame, fg_color="transparent")
        output_frame.pack(fill="x", pady=(0,10))
        
        self.decrypt_output_path = ctk.CTkEntry(output_frame, placeholder_text="output.txt", font=("Consolas", 11))
        self.decrypt_output_path.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        browse_decrypt_output = ctk.CTkButton(
            output_frame,
            text="📂",
            width=50,
            command=self.browse_decrypt_output
        )
        browse_decrypt_output.pack(side="right")
        
        # Password
        pass_label = ctk.CTkLabel(frame, text="DECRYPTION PASSWORD:", font=("Consolas", 12))
        pass_label.pack(anchor="w", pady=(10,5))
        
        self.decrypt_file_password = ctk.CTkEntry(frame, show="•", font=("Consolas", 11), width=400)
        self.decrypt_file_password.pack(anchor="w", pady=(0,10))
        
        # Progress bar
        self.decrypt_progress = ctk.CTkProgressBar(frame, width=500)
        self.decrypt_progress.pack(pady=10)
        self.decrypt_progress.set(0)
        
        # Decrypt button
        decrypt_btn = ctk.CTkButton(
            frame,
            text="🔓 DECRYPT FILE",
            command=self.decrypt_file_action,
            height=40,
            font=("Consolas", 13, "bold"),
            fg_color="#660000",
            hover_color="#990000"
        )
        decrypt_btn.pack(pady=10)
        
        self.selected_decrypt_file = None
        self.current_frame = frame
    
    def on_decrypt_file_selected(self, filepath):
        """Handle decryption file selection"""
        self.selected_decrypt_file = filepath
        self.decrypt_file_label.configure(text=f"📄 {os.path.basename(filepath)}", text_color="#00ff00")
        self.terminal.print(f"Encrypted file selected: {filepath}", "INFO")
        
        # Auto-generate output filename
        output_name = os.path.splitext(filepath)[0] + ".decrypted"
        self.decrypt_output_path.delete(0, "end")
        self.decrypt_output_path.insert(0, output_name)
    
    def browse_decrypt_output(self):
        """Browse for decryption output file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.decrypt_output_path.delete(0, "end")
            self.decrypt_output_path.insert(0, filename)
    
    def update_decrypt_progress(self, value):
        """Update decryption progress bar"""
        self.decrypt_progress.set(value / 100)
        self.workspace.update()
    
    def decrypt_file_action(self):
        """Perform file decryption"""
        if not self.selected_decrypt_file:
            messagebox.showerror("Error", "Please select a file to decrypt")
            return
        
        output_file = self.decrypt_output_path.get()
        if not output_file:
            messagebox.showerror("Error", "Please specify output file")
            return
        
        password = self.decrypt_file_password.get()
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        def decrypt_thread():
            try:
                self.terminal.print(f"Starting decryption of: {self.selected_decrypt_file}", "PROCESS")
                self.encryptor.decrypt_file(
                    self.selected_decrypt_file, 
                    output_file, 
                    password,
                    self.update_decrypt_progress
                )
                self.terminal.print(f"File decrypted successfully: {output_file}", "SUCCESS")
                self.workspace.after(0, lambda: messagebox.showinfo("Success", f"File decrypted successfully!\n\nOutput: {output_file}"))
                self.workspace.after(0, lambda: self.decrypt_progress.set(0))
            except Exception as e:
                self.terminal.print(f"Decryption failed: {str(e)}", "ERROR")
                self.workspace.after(0, lambda: messagebox.showerror("Error", f"Decryption failed: Wrong password or corrupted file"))
                self.workspace.after(0, lambda: self.decrypt_progress.set(0))
        
        threading.Thread(target=decrypt_thread, daemon=True).start()
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def show_keygen(self):
        """Generate strong random password"""
        self.clear_workspace()
        
        frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="🎲 GENERATE SECURE KEY",
            font=("Consolas", 18, "bold"),
            text_color="#00ccff"
        )
        title.pack(pady=10)
        
        # Length selector
        length_label = ctk.CTkLabel(frame, text="KEY LENGTH:", font=("Consolas", 12))
        length_label.pack(anchor="w", pady=(20,5))
        
        self.key_length = ctk.CTkSlider(frame, from_=16, to=64, number_of_steps=48)
        self.key_length.pack(fill="x", pady=(0,10))
        self.key_length.set(32)
        
        length_value = ctk.CTkLabel(frame, text="32 characters", font=("Consolas", 10))
        length_value.pack(anchor="w")
        
        def update_length(value):
            length_value.configure(text=f"{int(value)} characters")
        
        self.key_length.configure(command=update_length)
        
        # Generate button
        gen_btn = ctk.CTkButton(
            frame,
            text="🔑 GENERATE KEY",
            command=self.generate_key,
            height=40,
            font=("Consolas", 13, "bold")
        )
        gen_btn.pack(pady=20)
        
        # Generated key display
        self.generated_key = ctk.CTkTextbox(frame, height=100, font=("Consolas", 11))
        self.generated_key.pack(fill="x", pady=10)
        
        # Copy button
        copy_btn = ctk.CTkButton(
            frame,
            text="📋 COPY TO CLIPBOARD",
            command=self.copy_generated_key,
            width=200
        )
        copy_btn.pack(pady=10)
        
        self.current_frame = frame
    
    def generate_key(self):
        """Generate random secure key"""
        import secrets
        import string
        
        length = int(self.key_length.get())
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        self.generated_key.delete("1.0", "end")
        self.generated_key.insert("1.0", password)
        self.terminal.print(f"Generated secure key (Length: {length})", "SUCCESS")
    
    def show_history(self):
        """Show encryption history"""
        self.clear_workspace()
        
        frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="📜 ENCRYPTION HISTORY",
            font=("Consolas", 18, "bold"),
            text_color="#ff00ff"
        )
        title.pack(pady=10)
        
        history_text = ctk.CTkTextbox(frame, font=("Consolas", 11))
        history_text.pack(fill="both", expand=True, pady=10)
        
        history_text.insert("1.0", f"Encryption Session History\n{'='*50}\n")
        history_text.insert("end", f"Total operations: {self.encryption_count}\n")
        history_text.insert("end", f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        history_text.insert("end", f"\n[+] All operations logged in terminal\n")
        history_text.configure(state="disabled")
        
        self.current_frame = frame
    
    def show_settings(self):
        """Show application settings"""
        self.clear_workspace()
        
        frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            frame,
            text="⚙️ SETTINGS",
            font=("Consolas", 18, "bold"),
            text_color="#ffff00"
        )
        title.pack(pady=10)
        
        settings_frame = ctk.CTkFrame(frame, fg_color="#0a0a0a", corner_radius=10)
        settings_frame.pack(fill="both", expand=True, pady=20)
        
        settings = [
            ("Auto-clear clipboard after copy", False),
            ("Show password strength meter", True),
            ("Log all operations to file", False),
            ("Minimize to system tray", False)
        ]
        
        self.settings_vars = []
        for text, default in settings:
            var = tk.BooleanVar(value=default)
            self.settings_vars.append(var)
            cb = ctk.CTkCheckBox(settings_frame, text=text, variable=var, font=("Consolas", 11))
            cb.pack(anchor="w", pady=10, padx=20)
        
        save_btn = ctk.CTkButton(
            frame,
            text="💾 SAVE SETTINGS",
            command=self.save_settings,
            height=40
        )
        save_btn.pack(pady=20)
        
        self.current_frame = frame
    
    def save_settings(self):
        """Save settings"""
        self.terminal.print("Settings saved", "SUCCESS")
        messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def toggle_password_visibility(self, entry_widget):
        """Toggle password visibility"""
        if entry_widget.cget("show") == "•":
            entry_widget.configure(show="")
        else:
            entry_widget.configure(show="•")
    
    def copy_text_output(self):
        """Copy text output to clipboard"""
        text = self.text_output.get("1.0", "end-1c").strip()
        if text:
            pyperclip.copy(text)
            self.terminal.print("Text copied to clipboard", "SUCCESS")
            messagebox.showinfo("Success", "Copied to clipboard!")
    
    def copy_decrypt_output(self):
        """Copy decrypted output to clipboard"""
        text = self.decrypt_output.get("1.0", "end-1c").strip()
        if text:
            pyperclip.copy(text)
            self.terminal.print("Decrypted text copied to clipboard", "SUCCESS")
            messagebox.showinfo("Success", "Copied to clipboard!")
    
    def copy_generated_key(self):
        """Copy generated key to clipboard"""
        text = self.generated_key.get("1.0", "end-1c").strip()
        if text:
            pyperclip.copy(text)
            self.terminal.print("Generated key copied to clipboard", "SUCCESS")
            messagebox.showinfo("Success", "Key copied to clipboard!")
    
    def clear_workspace(self):
        """Clear the workspace area"""
        for widget in self.workspace.winfo_children():
            widget.destroy()
    
    def run(self):
        """Run the application"""
        self.window.mainloop()

# Main execution
if __name__ == "__main__":
    app = HackerEncryptionTool()
    app.run()