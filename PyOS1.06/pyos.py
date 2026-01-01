"""
PyOS 1.06 - A Simple Operating System Simulation with In-Memory Files

This script creates a simulated desktop environment with a taskbar,
start menu, and basic applications like a clock, settings, and a
file explorer, all built with the tkinter library.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import datetime
import json
import base64
import sys
import copy # Used for deep copying items to the recycle bin

# --- NEW: In-memory file system data structure ---
# This dictionary will hold all files and folders.
# Files are strings, folders are nested dictionaries.
# This replaces the need for actual file system operations.
in_memory_file_system = {
    'Documents': {
        'my_first_file.txt': 'Hello, PyOS!',
        'A cool folder': {}
    },
    'Images': {},
    # Hidden folder for deleted items (The Recycle Bin)
    '.recyclebin': {} 
}

class PyOS:
    """
    Main class for the PyOS simulation.
    Manages the UI, windows, and core functionalities.
    """
    def __init__(self, master):
        self.master = master
        master.title("PyOS 1.06")
        master.geometry("1280x720")
        master.configure(bg="#2e2e2e")

        self.start_menu = None
        self.current_path_label = None
        self.status_bar_label = None
        self.tree = None # Ensure treeview is initialized
        self.file_system = in_memory_file_system
        self.current_path = [] # Path is now a list of keys

        # Storage Limit
        self.storage_limit_mb = 64
        self.storage_limit_bytes = self.storage_limit_mb * 1024 * 1024
        self.storage_label = None
        self.storage_bar = None
        self.settings = {"theme": "dark"}

        # Create the main user interface
        self.create_ui()
        self.update_time()

    def create_ui(self):
        """
        Builds the main desktop and taskbar UI elements.
        """
        # Desktop Area (main frame for app windows)
        self.desktop = tk.Frame(self.master, bg="#2e2e2e")
        self.desktop.pack(fill="both", expand=True)
        
        # --- NEW: Warning message for in-memory files ---
        warning_label = tk.Label(self.desktop, text="WARNING: This version uses an in-memory file system. Files will NOT be saved to your computer.",
                                 bg="#f39c12", fg="white", font=("Inter", 12, "bold"))
        warning_label.pack(pady=10, padx=10, fill="x")

        # Taskbar at the bottom
        self.taskbar = tk.Frame(self.master, bg="#333333", height=40)
        self.taskbar.pack(side="bottom", fill="x")

        # Start button
        self.start_button = tk.Button(self.taskbar, text="Start", font=("Inter", 12),
                                      command=self.show_start_menu, bg="#4CAF50", fg="white",
                                      bd=0, relief="flat", activebackground="#66bb6a",
                                      padx=10, pady=5)
        self.start_button.pack(side="left", padx=(10, 5))

        # Clock label
        self.time_label = tk.Label(self.taskbar, text="", font=("Inter", 12),
                                   bg="#333333", fg="white")
        self.time_label.pack(side="right", padx=(5, 10))

        # Open window list (for a more advanced taskbar)
        self.open_windows = {}

    def update_time(self):
        """
        Updates the time label every second.
        """
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        self.time_label.config(text=time_str)
        self.master.after(1000, self.update_time)

    def show_start_menu(self):
        """
        Creates and displays the Start menu as a pop-up window.
        """
        if self.start_menu:
            self.start_menu.destroy()

        self.start_menu = tk.Toplevel(self.master, bg="#444444", relief="raised", bd=2)
        self.start_menu.overrideredirect(True)
        self.start_menu.geometry("250x300")
        
        start_button_x = self.start_button.winfo_rootx()
        start_button_y = self.start_button.winfo_rooty()
        self.start_menu.geometry(f"+{start_button_x}+{start_button_y - 300}")

        app_list = [
            ("Settings", self.show_settings),
            ("Files", self.show_file_explorer),
            ("Notepad", lambda: self.show_notepad()), 
            ("Calculator", self.show_calculator), # ADDED: Calculator
            ("Paint", self.show_paint),
            ("Exit PyOS", self.master.quit)
        ]

        for app_name, command in app_list:
            app_button = tk.Button(self.start_menu, text=app_name, font=("Inter", 12),
                                   command=lambda cmd=command: (self.start_menu.destroy(), cmd()),
                                   bg="#555555", fg="white", activebackground="#777777",
                                   relief="flat", bd=0, padx=10, pady=5)
            app_button.pack(fill="x", pady=2, padx=5)

        self.start_menu.bind("<FocusOut>", lambda e: self.start_menu.destroy())
        self.start_menu.focus_set()

    def create_app_window(self, title, width, height):
        """
        Creates a new styled window for an application.
        """
        window = tk.Toplevel(self.master, bg="#2e2e2e")
        window.title(title)
        window.geometry(f"{width}x{height}")
        desktop_width = self.desktop.winfo_width()
        desktop_height = self.desktop.winfo_height()
        pos_x = (desktop_width - width) // 2
        pos_y = (desktop_height - height) // 2
        window.geometry(f"+{pos_x}+{pos_y}")

        title_bar = tk.Frame(window, bg="#444444", relief="raised", bd=1)
        title_bar.pack(side="top", fill="x")

        title_label = tk.Label(title_bar, text=title, bg="#444444", fg="white", font=("Inter", 10, "bold"))
        title_label.pack(side="left", padx=5)

        close_button = tk.Button(title_bar, text="X", command=window.destroy, bg="#e74c3c", fg="white", bd=0, relief="flat", padx=5)
        close_button.pack(side="right")
        
        def start_move(event):
            window._drag_x = event.x
            window._drag_y = event.y

        def on_move(event):
            x = window.winfo_x() + event.x - window._drag_x
            y = window.winfo_y() + event.y - window._drag_y
            window.geometry(f"+{x}+{y}")

        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", on_move)

        return window

    def show_settings(self):
        """
        Opens the simulated Settings application.
        """
        settings_window = self.create_app_window("Settings", 400, 300)
        settings_frame = tk.Frame(settings_window, bg="#2e2e2e", padx=20, pady=20)
        settings_frame.pack(fill="both", expand=True)

        theme_label = tk.Label(settings_frame, text="Theme:", bg="#2e2e2e", fg="white", font=("Inter", 12))
        theme_label.pack(side="top", anchor="w")

        self.theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        
        dark_radio = tk.Radiobutton(settings_frame, text="Dark", variable=self.theme_var, value="dark",
                                    bg="#2e2e2e", fg="white", selectcolor="#2e2e2e",
                                    font=("Inter", 10), command=self.apply_theme)
        dark_radio.pack(side="top", anchor="w", padx=10)

        light_radio = tk.Radiobutton(settings_frame, text="Light (Not implemented)", variable=self.theme_var, value="light",
                                     bg="#2e2e2e", fg="white", selectcolor="#2e2e2e",
                                     font=("Inter", 10), state="disabled")
        light_radio.pack(side="top", anchor="w", padx=10)

    def apply_theme(self):
        """
        Changes the color theme of the OS.
        """
        theme = self.theme_var.get()
        if theme == "dark":
            bg_color = "#2e2e2e"
            taskbar_bg = "#333333"
            fg_color = "white"
        else:
            bg_color = "#f0f0f0"
            taskbar_bg = "#cccccc"
            fg_color = "black"

        self.master.configure(bg=bg_color)
        self.desktop.configure(bg=bg_color)
        self.taskbar.configure(bg=taskbar_bg)
        self.time_label.configure(bg=taskbar_bg, fg=fg_color)
        self.start_button.configure(bg="#4CAF50", fg="white")

        self.settings["theme"] = theme
    
    def calculate_directory_size(self):
        """
        Recursively calculates the size of the in-memory file system.
        """
        def get_size(node):
            total_size = 0
            for key, value in node.items():
                if isinstance(value, dict):
                    total_size += get_size(value)
                else:
                    total_size += len(value.encode('utf-8'))
            return total_size

        return get_size(self.file_system)

    def update_storage_display(self):
        """
        Updates the storage usage label and progress bar.
        """
        used_space = self.calculate_directory_size()
        used_mb = used_space / (1024 * 1024)
        
        if self.storage_label:
            self.storage_label.config(text=f"Storage Used: {used_mb:.2f} MB / {self.storage_limit_mb:.0f} MB")
        
        if self.storage_bar:
            percentage = (used_space / self.storage_limit_bytes) * 100
            self.storage_bar['value'] = percentage
            if percentage > 90:
                self.storage_bar.configure(style="Red.TProgressbar")
            elif percentage > 70:
                self.storage_bar.configure(style="Orange.TProgressbar")
            else:
                self.storage_bar.configure(style="Green.TProgressbar")

    def show_file_explorer(self):
        """
        Opens the simulated File Explorer with file management options.
        """
        file_explorer = self.create_app_window("Files", 600, 400)
        
        top_frame = tk.Frame(file_explorer, bg="#444444")
        top_frame.pack(fill="x", side="top")
        
        tk.Button(top_frame, text="New File", command=self.create_file_dialog, bg="#555555", fg="white", bd=0, padx=5).pack(side="left", padx=2, pady=2)
        tk.Button(top_frame, text="New Folder", command=self.create_folder_dialog, bg="#555555", fg="white", bd=0, padx=5).pack(side="left", padx=2, pady=2)
        tk.Button(top_frame, text="Rename", command=self.rename_selected_item, bg="#555555", fg="white", bd=0, padx=5).pack(side="left", padx=2, pady=2)
        # Delete button now moves to recycle bin
        tk.Button(top_frame, text="Delete", command=self.delete_selected_item, bg="#e74c3c", fg="white", bd=0, padx=5).pack(side="left", padx=2, pady=2)
        # Recycle Bin Button
        tk.Button(top_frame, text="Recycle Bin", command=self.show_recycle_bin_management, bg="#3498db", fg="white", bd=0, padx=5).pack(side="left", padx=2, pady=2)
        tk.Button(top_frame, text="Refresh", command=self.refresh_file_explorer, bg="#3498db", fg="white", bd=0, padx=5).pack(side="right", padx=2, pady=2)

        # Path and status displays
        self.current_path_label = tk.Label(file_explorer, text=f"Current Path: /", bg="#2e2e2e", fg="lightgray", font=("Inter", 9))
        self.current_path_label.pack(fill="x", padx=10, pady=(5, 0))

        tree_frame = ttk.Frame(file_explorer, padding="10")
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        
        # --- Progress bar styling fix ---
        style = ttk.Style()
        style.theme_use("default") # Use a known theme
        style.configure("Green.TProgressbar", foreground='green', background='green')
        style.configure("Orange.TProgressbar", foreground='orange', background='orange')
        style.configure("Red.TProgressbar", foreground='red', background='red')
        
        # Storage display at the bottom of the file explorer
        storage_frame = tk.Frame(file_explorer, bg="#444444", padx=10, pady=5)
        storage_frame.pack(side="bottom", fill="x")

        self.storage_label = tk.Label(storage_frame, text="", bg="#444444", fg="white", font=("Inter", 10))
        self.storage_label.pack(side="left", fill="x", expand=True)
        
        self.storage_bar = ttk.Progressbar(storage_frame, orient="horizontal", length=200, mode="determinate", style="Green.TProgressbar")
        self.storage_bar.pack(side="right")
        self.storage_bar["maximum"] = 100

        # Status bar
        self.status_bar_label = tk.Label(file_explorer, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.populate_tree()
        self.update_storage_display()
        self.status_bar_label.config(text="File explorer loaded.")
        
    def get_current_node(self):
        node = self.file_system
        for key in self.current_path:
            # Safely navigate the dictionary
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return {} # Return an empty node if path is invalid
        return node
        
    def populate_tree(self):
        """
        Populates the file explorer treeview from the in-memory file system.
        """
        self.tree.delete(*self.tree.get_children())

        # Update path display
        path_str = "/" + "/".join(self.current_path)
        self.current_path_label.config(text=f"Current Path: {path_str}")

        # Back button/nav
        if len(self.current_path) > 0:
            self.tree.insert("", "end", text="[..] Back", values=("..",))

        current_node = self.get_current_node()
        items = sorted(current_node.keys())
        
        for item in items:
            # Skip hidden recycle bin folder in normal view
            if item == '.recyclebin' and len(self.current_path) == 0:
                continue

            item_path = "/".join(self.current_path + [item])
            if isinstance(current_node[item], dict):
                # Folder: use [D] for directory
                self.tree.insert("", "end", text=f"[D] {item}", values=(item_path,))
            else:
                # File: use [F] for file
                self.tree.insert("", "end", text=f"[F] {item}", values=(item_path,))
            
        self.tree.bind("<Double-1>", self.on_double_click_file_explorer)

    def on_double_click_file_explorer(self, event):
        """
        Handles double-click events in the file explorer tree.
        """
        item_id = self.tree.focus()
        item_text = self.tree.item(item_id, "text")

        if item_text == "[..] Back":
            if len(self.current_path) > 0:
                self.current_path.pop()
        else:
            # Extract the actual item name from the formatted string
            item_name = item_text.split("] ")[1]
            current_node = self.get_current_node()
            
            if isinstance(current_node.get(item_name), dict):
                self.current_path.append(item_name)
            else:
                # Open the file for viewing/editing using the new Notepad
                full_path = self.current_path[:] # A copy of the current path
                file_content = current_node.get(item_name, "File not found.")
                
                # LAUNCH NOTEPAD
                self.show_notepad(filename=item_name, initial_content=file_content, file_path=full_path) 
                
        self.populate_tree()

    # --- START: Notepad Application Methods ---
    def show_notepad(self, filename=None, initial_content="", file_path=None):
        """
        Opens the Notepad text editor application.
        Can open an existing file or a blank document.
        """
        if filename:
            title = f"Notepad - {filename}"
        else:
            title = "Notepad - Untitled"
            
        notepad_window = self.create_app_window(title, 600, 500)
        
        # Store file metadata on the window itself
        notepad_window.filename = filename
        notepad_window.file_path = file_path # The list of folder names leading to the file
        notepad_window.is_saved = True # Initial state is saved if opening existing, or blank new.

        # Menu Bar
        menu_bar = tk.Menu(notepad_window)
        notepad_window.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # New/Open are for future full implementation, focus on Save/Save As for now
        file_menu.add_command(label="New", command=lambda: self.show_notepad(filename=None)) 
        file_menu.add_command(label="Open (WIP)", command=lambda: messagebox.showinfo("WIP", "Use File Explorer to open files.")) 
        file_menu.add_separator()
        
        # Bind the save command to the window
        file_menu.add_command(label="Save", command=lambda: self.save_notepad_file(notepad_window))
        file_menu.add_command(label="Save As...", command=lambda: self.save_notepad_file(notepad_window, save_as=True))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=notepad_window.destroy)

        # Text Widget for editing
        text_widget = tk.Text(notepad_window, bg="#3c3c3c", fg="white", insertbackground="white", font=("Consolas", 11), undo=True)
        text_widget.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Add the text widget to the window object for access in the save function
        notepad_window.text_widget = text_widget
        
        # Load content
        text_widget.insert(tk.END, initial_content)
        
        # Unsaved changes tracker
        def mark_unsaved(event):
            if notepad_window.is_saved:
                notepad_window.is_saved = False
                notepad_window.title(f"Notepad - *{notepad_window.filename or 'Untitled'}")

        text_widget.bind("<KeyRelease>", mark_unsaved)

        # Prompt before closing if unsaved
        def on_closing():
            if not notepad_window.is_saved:
                if messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you want to exit without saving?"):
                    notepad_window.destroy()
            else:
                notepad_window.destroy()

        notepad_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Refresh the file explorer when this window is closed
        notepad_window.bind("<Destroy>", lambda e: self.refresh_file_explorer())


    def save_notepad_file(self, window, save_as=False):
        """
        Saves the content of the Notepad editor to the in-memory file system.
        Handles both saving an existing file and 'Save As' for new files.
        """
        content = window.text_widget.get("1.0", tk.END).strip()
        
        # Calculate new size to check against limit
        content_size = len(content.encode('utf-8'))

        # --- Get the target node (path to the file) ---
        target_node = self.file_system
        if window.file_path:
            for key in window.file_path:
                target_node = target_node.get(key)
                if not target_node or not isinstance(target_node, dict):
                    messagebox.showerror("Save Error", "Original path is invalid. Saving to root (/).")
                    target_node = self.file_system # Fallback to root
                    window.file_path = []
                    break

        # --- Handle Save As / New File ---
        if save_as or not window.filename:
            new_name = simpledialog.askstring("Save As", "Enter a file name:", initialvalue=window.filename or "new_file.txt")
            if not new_name:
                return # User cancelled
            
            # Use the current File Explorer path for "Save As" location
            current_explorer_node = self.get_current_node() 
            if new_name in current_explorer_node and new_name != window.filename:
                 if not messagebox.askyesno("File Exists", f"Overwrite existing file '{new_name}'?"):
                    return
            
            window.filename = new_name
            target_node = current_explorer_node
            window.file_path = self.current_path[:] 

        # --- Final Save & Storage Check ---
        old_size = len(target_node.get(window.filename, "").encode('utf-8'))
        
        # Check if the new size exceeds the total limit after accounting for the old size
        current_total_size = self.calculate_directory_size()
        size_change = content_size - old_size
        
        if (current_total_size + size_change) > self.storage_limit_bytes:
            return messagebox.showerror("Storage Full", "Cannot save file. Storage limit reached.")

        # Save the content and update window metadata
        target_node[window.filename] = content
        window.title(f"Notepad - {window.filename}")
        window.is_saved = True
        
        self.status_bar_label.config(text=f"File '{window.filename}' saved successfully.")
        self.update_storage_display()
        self.refresh_file_explorer()
    # --- END: Notepad Application Methods ---


    def create_file_dialog(self):
        """
        Prompts the user to create a new file.
        """
        new_file_name = simpledialog.askstring("New File", "Enter the new file name:")
        if new_file_name:
            # Check for storage limit
            if self.calculate_directory_size() < self.storage_limit_bytes:
                current_node = self.get_current_node()
                if new_file_name in current_node:
                    messagebox.showwarning("File Exists", f"A file or folder with the name '{new_file_name}' already exists.")
                else:
                    current_node[new_file_name] = "" # Create an empty file
                    self.status_bar_label.config(text=f"File '{new_file_name}' created.")
                    self.populate_tree()
                    self.update_storage_display()
            else:
                messagebox.showerror("Storage Full", "Cannot create new file. Storage limit reached.")

    def create_folder_dialog(self):
        """
        Prompts the user to create a new folder.
        """
        new_folder_name = simpledialog.askstring("New Folder", "Enter the new folder name:")
        if new_folder_name:
            current_node = self.get_current_node()
            if new_folder_name in current_node:
                messagebox.showwarning("Folder Exists", f"A file or folder with the name '{new_folder_name}' already exists.")
            else:
                current_node[new_folder_name] = {} # Create an empty folder
                self.status_bar_label.config(text=f"Folder '{new_folder_name}' created.")
                self.populate_tree()
                self.update_storage_display()

    def rename_selected_item(self):
        """
        Renames the selected file or folder.
        """
        item_id = self.tree.focus()
        if not item_id:
            return messagebox.showwarning("No Item Selected", "Please select a file or folder to rename.")
        
        item_text = self.tree.item(item_id, "text")
        if item_text == "[..] Back":
             return messagebox.showwarning("Cannot Rename", "Cannot rename the back navigation item.")
             
        old_name = item_text.split("] ")[1]
        
        new_name = simpledialog.askstring("Rename", f"Enter a new name for '{old_name}':", initialvalue=old_name)
        if new_name and new_name != old_name:
            current_node = self.get_current_node()
            if new_name in current_node:
                return messagebox.showwarning("Name Exists", f"A file or folder with the name '{new_name}' already exists.")
            
            # Copy the old item to the new name and delete the old one
            current_node[new_name] = current_node.pop(old_name)
            self.status_bar_label.config(text=f"'{old_name}' renamed to '{new_name}'.")
            self.populate_tree()

    def delete_selected_item(self):
        """
        Moves the selected file or folder to the .recyclebin.
        """
        item_id = self.tree.focus()
        if not item_id:
            return messagebox.showwarning("No Item Selected", "Please select a file or folder to delete.")
            
        item_text = self.tree.item(item_id, "text")
        if item_text == "[..] Back":
             return messagebox.showwarning("Cannot Delete", "Cannot delete the back navigation item.")

        item_name = item_text.split("] ")[1]
        current_node = self.get_current_node()
        
        if messagebox.askyesno("Delete Item", f"Move '{item_name}' to the Recycle Bin?"):
            if item_name in current_node:
                # 1. Get a deep copy of the item to preserve its content/structure
                item_to_move = copy.deepcopy(current_node[item_name])
                
                # 2. Delete it from the current location
                del current_node[item_name]
                
                # 3. Move it to the recycle bin with a timestamp/unique key to avoid name conflicts
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                recycle_key = f"{item_name}_DELETED_{timestamp}"
                
                self.file_system['.recyclebin'][recycle_key] = {
                    'original_name': item_name,
                    'original_path': self.current_path[:], # Store a copy of the path where it was deleted
                    'content': item_to_move
                }
                
                self.status_bar_label.config(text=f"'{item_name}' moved to Recycle Bin.")
                self.populate_tree()
                self.update_storage_display()
    
    # --- START: Recycle Bin Management Methods ---

    def show_recycle_bin_management(self):
        """
        Opens a separate window for managing the Recycle Bin (restore/empty).
        """
        recycle_window = self.create_app_window("Recycle Bin", 500, 400)
        
        control_frame = tk.Frame(recycle_window, bg="#2e2e2e", padx=10, pady=5)
        control_frame.pack(side="top", fill="x")
        
        tk.Button(control_frame, text="Restore Selected", command=lambda: self.restore_item(recycle_tree), bg="#4CAF50", fg="white", bd=0, padx=5).pack(side="left", padx=2, pady=2)
        tk.Button(control_frame, text="Permanently Delete Selected", command=lambda: self.permanently_delete_item(recycle_tree), bg="#e74c3c", fg="white", bd=0, padx=5).pack(side="left", padx=2, pady=2)
        tk.Button(control_frame, text="Empty Recycle Bin", command=self.empty_recycle_bin, bg="#c0392b", fg="white", bd=0, padx=5).pack(side="right", padx=2, pady=2)

        recycle_tree_frame = ttk.Frame(recycle_window, padding="10")
        recycle_tree_frame.pack(fill="both", expand=True)

        recycle_tree = ttk.Treeview(recycle_tree_frame, columns=('Original Name', 'Deleted Key'))
        recycle_tree.heading('#0', text='Type')
        recycle_tree.heading('Original Name', text='Original Name')
        recycle_tree.heading('Deleted Key', text='Deleted Key', anchor=tk.W)
        recycle_tree.column('#0', width=50, stretch=tk.NO)
        recycle_tree.column('Original Name', width=150, stretch=tk.YES)
        recycle_tree.column('Deleted Key', width=200, stretch=tk.YES)
        recycle_tree.pack(side="left", fill="both", expand=True)

        self.populate_recycle_bin(recycle_tree)
        
        # Status bar for recycle bin
        recycle_status_label = tk.Label(recycle_window, text=f"Items: {len(self.file_system['.recyclebin'])}", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        recycle_status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def populate_recycle_bin(self, tree_widget):
        """
        Fills the Recycle Bin treeview with deleted items.
        """
        tree_widget.delete(*tree_widget.get_children())
        
        for key, value in self.file_system['.recyclebin'].items():
            original_name = value['original_name']
            item_type = "[D]" if isinstance(value['content'], dict) else "[F]"
            
            tree_widget.insert("", "end", text=item_type, 
                               values=(original_name, key))

    def restore_item(self, tree_widget):
        """
        Restores the selected item from the recycle bin to its original path.
        """
        selected_item_id = tree_widget.focus()
        if not selected_item_id:
            return messagebox.showwarning("Selection Error", "Please select an item to restore.")
            
        # Get the unique key from the values
        key_to_restore = tree_widget.item(selected_item_id, 'values')[1]
        item_data = self.file_system['.recyclebin'].get(key_to_restore)
        
        if not item_data: return

        original_path_list = item_data['original_path']
        original_name = item_data['original_name']
        content_to_restore = item_data['content']

        # Determine the target restoration node by traversing the path
        restore_node = self.file_system
        for key in original_path_list:
            if key in restore_node and isinstance(restore_node[key], dict):
                restore_node = restore_node[key]
            else:
                # If the original folder path is missing, restore to root
                restore_node = self.file_system
                original_path_list = []
                messagebox.showwarning("Path Missing", f"Original path for '{original_name}' not found. Restoring to root (/).")
                break

        # Check for name collision in the restoration location
        if original_name in restore_node:
            response = messagebox.askyesno("Name Conflict", f"'{original_name}' already exists at the restoration location. Restore as '{original_name}_restored' instead?")
            if response:
                original_name += "_restored"
            else:
                return

        # Restore the item and update the recycle bin
        restore_node[original_name] = content_to_restore
        del self.file_system['.recyclebin'][key_to_restore]
        
        messagebox.showinfo("Restored", f"'{original_name}' restored to /{'/'.join(original_path_list)}")
        
        # Refresh both the Recycle Bin window and the File Explorer (if open)
        self.populate_recycle_bin(tree_widget)
        self.refresh_file_explorer()

    def permanently_delete_item(self, tree_widget):
        """
        Permanently deletes the selected item from the recycle bin.
        """
        selected_item_id = tree_widget.focus()
        if not selected_item_id:
            return messagebox.showwarning("Selection Error", "Please select an item to permanently delete.")
            
        key_to_delete = tree_widget.item(selected_item_id, 'values')[1]
        original_name = tree_widget.item(selected_item_id, 'values')[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you SURE you want to permanently delete '{original_name}'?"):
            del self.file_system['.recyclebin'][key_to_delete]
            self.status_bar_label.config(text=f"'{original_name}' permanently deleted.")
            self.populate_recycle_bin(tree_widget)
            self.update_storage_display()

    def empty_recycle_bin(self):
        """
        Permanently deletes all contents of the recycle bin.
        """
        count = len(self.file_system['.recyclebin'])
        if count == 0:
            return messagebox.showinfo("Recycle Bin", "Recycle Bin is already empty.")

        if messagebox.askyesno("Empty Recycle Bin", f"Are you SURE you want to permanently delete all {count} items in the Recycle Bin?"):
            self.file_system['.recyclebin'] = {}
            self.status_bar_label.config(text="Recycle Bin emptied.")
            
            # Close the recycle bin window if it exists and refresh explorer
            for window in self.master.winfo_children():
                if isinstance(window, tk.Toplevel) and window.title() == "Recycle Bin":
                    window.destroy()

            self.refresh_file_explorer()
    # --- END: Recycle Bin Management Methods ---


    def refresh_file_explorer(self):
        """
        Refreshes the file explorer view.
        """
        if self.tree:
            self.populate_tree()
            self.update_storage_display()
            self.status_bar_label.config(text="File explorer refreshed.")

    # --- START: Calculator Application Methods ---

    def show_calculator(self):
        """
        Opens the Calculator application.
        """
        calc_window = self.create_app_window("Calculator", 250, 300)
        calc_window.configure(bg="#2e2e2e")
        
        # Entry field to display numbers and results
        self.calc_entry = tk.Entry(calc_window, width=14, font=('Inter', 20), bd=5, relief=tk.FLAT, 
                                   bg="#3c3c3c", fg="white", justify='right')
        self.calc_entry.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # Calculator buttons layout
        buttons = [
            ('7', 1, 0, '#555555'), ('8', 1, 1, '#555555'), ('9', 1, 2, '#555555'), ('/', 1, 3, '#f39c12'),
            ('4', 2, 0, '#555555'), ('5', 2, 1, '#555555'), ('6', 2, 2, '#555555'), ('*', 2, 3, '#f39c12'),
            ('1', 3, 0, '#555555'), ('2', 3, 1, '#555555'), ('3', 3, 2, '#555555'), ('-', 3, 3, '#f39c12'),
            ('0', 4, 0, '#555555'), ('.', 4, 1, '#555555'), ('=', 4, 2, '#4CAF50', 1, 2), ('+', 4, 3, '#f39c12'),
            ('C', 5, 0, '#e74c3c', 1, 4) # Clear button
        ]
        
        # Configure button size (weights)
        for i in range(4):
            calc_window.grid_columnconfigure(i, weight=1)
        for i in range(6):
            calc_window.grid_rowconfigure(i, weight=1)

        for (text, r, c, bg_color, r_span, c_span) in [(t, r, c, bg, 1, 1) for t, r, c, bg in buttons[:16]] + [(buttons[16][0], buttons[16][1], buttons[16][2], buttons[16][3], buttons[16][4], buttons[16][5])]:
            
            if text == '=':
                cmd = self.calculate_expression
            elif text == 'C':
                cmd = lambda t=text: self.calc_entry.delete(0, tk.END)
            else:
                cmd = lambda t=text: self.calc_entry.insert(tk.END, t)

            btn = tk.Button(calc_window, text=text, font=('Inter', 14, 'bold'),
                            bg=bg_color, fg="white", bd=0, relief=tk.FLAT, 
                            activebackground="#777777", command=cmd)
            
            btn.grid(row=r, column=c, rowspan=r_span, columnspan=c_span, sticky="nsew", padx=2, pady=2)


    def calculate_expression(self):
        """
        Evaluates the expression in the calculator entry field.
        """
        expression = self.calc_entry.get().replace('x', '*') # Replace 'x' with '*' for Python's eval
        
        try:
            # Use safe evaluation to calculate the result
            # NOTE: For a production-level OS, using ast.literal_eval or a custom parser 
            # is safer than direct eval(), but for a simulation, eval() is simplest.
            result = str(eval(expression))
            
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, result)
            
        except ZeroDivisionError:
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, "Error: Div by Zero")
        except:
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, "Error")
    # --- END: Calculator Application Methods ---

    # --- START: Paint Application Methods ---
    def show_paint(self):
        paint_window = self.create_app_window("Paint", 800, 600)
        control_frame = tk.Frame(paint_window, bg="#444444")
        control_frame.pack(side="top", fill="x")

        self.current_color = "black"
        self.color_button = tk.Button(control_frame, text="Color", bg=self.current_color, fg="white",
                                      command=self.choose_color_for_paint, bd=0)
        self.color_button.pack(side="left", padx=5, pady=5)
        
        clear_button = tk.Button(control_frame, text="Clear", command=lambda: self.canvas.delete("all"),
                                 bg="#e74c3c", fg="white", bd=0)
        clear_button.pack(side="right", padx=5, pady=5)

        self.canvas = tk.Canvas(paint_window, bg="white", width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        self.last_x, self.last_y = None, None

        self.canvas.bind("<B1-Motion>", self.draw_line)
        self.canvas.bind("<ButtonRelease-1>", self.reset_last_coords)

    def choose_color_for_paint(self):
        color_choice = simpledialog.askstring("Choose Color", "Enter a color name (e.g., red, blue, green) or hex code (e.g., #FF5733):", initialvalue=self.current_color)
        if color_choice:
            self.current_color = color_choice
            self.color_button.config(bg=self.current_color)
    
    def draw_line(self, event):
        if self.last_x and self.last_y:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    fill=self.current_color, width=2, capstyle=tk.ROUND, smooth=tk.TRUE)
        self.last_x, self.last_y = event.x, event.y

    def reset_last_coords(self, event):
        self.last_x, self.last_y = None, None
    # --- END: Paint Application Methods ---


if __name__ == "__main__":
    root = tk.Tk()
    app = PyOS(root)
    root.mainloop()