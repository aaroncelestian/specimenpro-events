#!/usr/bin/env python3
"""
SpecimenPro Event Manager
A GUI application for managing SpecimenPro events, specimens, and badges.
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import uuid
import os


class SpecimenProEventManager:
    def __init__(self, root):
        self.root = root
        self.root.title("SpecimenPro Event Manager")
        self.root.geometry("1200x800")
        
        self.events_file = "events.json"
        self.events_data = self.load_events()
        self.current_event = None
        
        self.setup_ui()
        self.refresh_events_list()
    
    def load_events(self):
        """Load events from the JSON file"""
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default structure if file doesn't exist
                return {
                    "version": 1,
                    "lastUpdated": datetime.now().isoformat() + "Z",
                    "events": []
                }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events: {e}")
            return {"version": 1, "lastUpdated": datetime.now().isoformat() + "Z", "events": []}
    
    def save_events(self):
        """Save events to the JSON file"""
        try:
            self.events_data["lastUpdated"] = datetime.now().isoformat() + "Z"
            with open(self.events_file, 'w') as f:
                json.dump(self.events_data, f, indent=2)
            messagebox.showinfo("Success", "Events saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save events: {e}")
    
    def setup_ui(self):
        """Setup the main UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Events list
        left_frame = ttk.LabelFrame(main_frame, text="Events", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Events listbox with scrollbar
        events_scroll = ttk.Scrollbar(left_frame)
        events_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.events_listbox = tk.Listbox(left_frame, yscrollcommand=events_scroll.set)
        self.events_listbox.pack(fill=tk.BOTH, expand=True)
        events_scroll.config(command=self.events_listbox.yview)
        
        self.events_listbox.bind('<<ListboxSelect>>', self.on_event_select)
        
        # Buttons for events
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="New Event", command=self.new_event).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Event", command=self.delete_event).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Save All", command=self.save_events).pack(side=tk.RIGHT)
        
        # Right panel - Event details
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(0, weight=1)
        
        # Event info tab
        self.setup_event_tab()
        
        # Specimens tab
        self.setup_specimens_tab()
        
        # Badges tab
        self.setup_badges_tab()
    
    def setup_event_tab(self):
        """Setup the event information tab"""
        event_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(event_frame, text="Event Info")
        event_frame.columnconfigure(1, weight=1)
        
        # Event fields
        row = 0
        fields = [
            ("Event ID:", "id"),
            ("Title:", "title"),
            ("Description:", "description"),
            ("Type:", "type"),
            ("Location:", "location"),
            ("Status:", "status"),
            ("Start Date (YYYY-MM-DD):", "startDate"),
            ("End Date (YYYY-MM-DD):", "endDate")
        ]
        
        self.event_vars = {}
        
        for label, field in fields:
            ttk.Label(event_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            if field == "description":
                var = tk.StringVar()
                entry = tk.Text(event_frame, height=4, width=50)
                entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                self.event_vars[field] = (var, entry)
            elif field == "type":
                var = tk.StringVar()
                values = ["exhibit", "scavenger_hunt", "competition", "workshop"]
                combo = ttk.Combobox(event_frame, textvariable=var, values=values)
                combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                self.event_vars[field] = var
            elif field == "status":
                var = tk.StringVar()
                values = ["active", "upcoming", "ended", "draft"]
                combo = ttk.Combobox(event_frame, textvariable=var, values=values)
                combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                self.event_vars[field] = var
            else:
                var = tk.StringVar()
                entry = ttk.Entry(event_frame, textvariable=var)
                entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                self.event_vars[field] = var
            
            row += 1
        
        # Save button for current event
        ttk.Button(event_frame, text="Update Event", command=self.update_current_event).grid(row=row, column=1, pady=20, sticky=tk.E)
    
    def setup_specimens_tab(self):
        """Setup the specimens tab"""
        specimens_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(specimens_frame, text="Specimens")
        specimens_frame.columnconfigure(0, weight=1)
        specimens_frame.rowconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(specimens_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Add Specimen", command=self.add_specimen).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Remove Specimen", command=self.remove_specimen).pack(side=tk.LEFT, padx=(10, 0))
        
        # Specimens list
        self.specimens_tree = ttk.Treeview(specimens_frame, columns=("name", "locality", "rarity"), show="tree headings")
        self.specimens_tree.heading("#0", text="ID")
        self.specimens_tree.heading("name", text="Name")
        self.specimens_tree.heading("locality", text="Locality")
        self.specimens_tree.heading("rarity", text="Rarity")
        
        self.specimens_tree.column("#0", width=50)
        self.specimens_tree.column("name", width=150)
        self.specimens_tree.column("locality", width=200)
        self.specimens_tree.column("rarity", width=100)
        
        self.specimens_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for specimens
        specimens_scroll = ttk.Scrollbar(specimens_frame, orient=tk.VERTICAL, command=self.specimens_tree.yview)
        specimens_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.specimens_tree.configure(yscrollcommand=specimens_scroll.set)
        
        self.specimens_tree.bind('<Double-1>', self.edit_specimen)
    
    def setup_badges_tab(self):
        """Setup the badges tab"""
        badges_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(badges_frame, text="Badges")
        badges_frame.columnconfigure(0, weight=1)
        badges_frame.rowconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(badges_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Add Badge", command=self.add_badge).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Remove Badge", command=self.remove_badge).pack(side=tk.LEFT, padx=(10, 0))
        
        # Badges list
        self.badges_tree = ttk.Treeview(badges_frame, columns=("title", "description", "requirement"), show="tree headings")
        self.badges_tree.heading("#0", text="ID")
        self.badges_tree.heading("title", text="Title")
        self.badges_tree.heading("description", text="Description")
        self.badges_tree.heading("requirement", text="Requirement")
        
        self.badges_tree.column("#0", width=50)
        self.badges_tree.column("title", width=150)
        self.badges_tree.column("description", width=200)
        self.badges_tree.column("requirement", width=150)
        
        self.badges_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for badges
        badges_scroll = ttk.Scrollbar(badges_frame, orient=tk.VERTICAL, command=self.badges_tree.yview)
        badges_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.badges_tree.configure(yscrollcommand=badges_scroll.set)
        
        self.badges_tree.bind('<Double-1>', self.edit_badge)
    
    def refresh_events_list(self):
        """Refresh the events listbox"""
        self.events_listbox.delete(0, tk.END)
        for event in self.events_data.get("events", []):
            display_text = f"{event['title']} ({event['status']})"
            self.events_listbox.insert(tk.END, display_text)
    
    def on_event_select(self, event):
        """Handle event selection"""
        selection = self.events_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_event = self.events_data["events"][index]
            self.load_event_to_form()
    
    def load_event_to_form(self):
        """Load current event data into the form"""
        if not self.current_event:
            return
        
        # Load basic event info
        for field, var in self.event_vars.items():
            if field == "description":
                var[0].set(self.current_event.get(field, ""))
                var[1].delete(1.0, tk.END)
                var[1].insert(1.0, self.current_event.get(field, ""))
            else:
                var.set(self.current_event.get(field, ""))
        
        # Load specimens
        self.specimens_tree.delete(*self.specimens_tree.get_children())
        for specimen in self.current_event.get("specimens", []):
            # Display basic info in tree, but keep full data in memory
            display_name = specimen["name"][:30] + "..." if len(specimen["name"]) > 30 else specimen["name"]
            self.specimens_tree.insert("", tk.END, iid=specimen["id"], 
                                      text=specimen["id"],
                                      values=(display_name, specimen["locality"], specimen.get("rarity", "")))
        
        # Load badges
        self.badges_tree.delete(*self.badges_tree.get_children())
        for badge in self.current_event.get("badges", []):
            requirement_text = f"{badge['requirement']} {badge['requirementType']}"
            self.badges_tree.insert("", tk.END, iid=badge["id"],
                                   text=badge["id"],
                                   values=(badge["title"], badge["description"], requirement_text))
    
    def new_event(self):
        """Create a new event"""
        event_id = f"event-{uuid.uuid4().hex[:8]}"
        new_event = {
            "id": event_id,
            "title": "New Event",
            "description": "Event description",
            "startDate": datetime.now().strftime("%Y-%m-%d") + "T00:00:00Z",
            "endDate": datetime.now().strftime("%Y-%m-%d") + "T23:59:59Z",
            "status": "draft",
            "type": "scavenger_hunt",
            "location": "Location",
            "imageUrl": None,
            "specimens": [],
            "badges": []
        }
        
        self.events_data["events"].append(new_event)
        self.refresh_events_list()
        
        # Select the new event
        self.events_listbox.selection_clear(0, tk.END)
        self.events_listbox.selection_set(tk.END)
        self.on_event_select(None)
    
    def delete_event(self):
        """Delete the current event"""
        if not self.current_event:
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete event '{self.current_event['title']}'?"):
            self.events_data["events"] = [e for e in self.events_data["events"] if e["id"] != self.current_event["id"]]
            self.current_event = None
            self.refresh_events_list()
            self.clear_form()
    
    def update_current_event(self):
        """Update the current event with form data"""
        if not self.current_event:
            return
        
        # Update basic event info
        for field, var in self.event_vars.items():
            if field == "description":
                self.current_event[field] = var[1].get(1.0, tk.END).strip()
            else:
                self.current_event[field] = var.get()
        
        self.refresh_events_list()
        messagebox.showinfo("Success", "Event updated successfully!")
    
    def add_specimen(self):
        """Add a new specimen to the current event"""
        if not self.current_event:
            messagebox.showwarning("No Event", "Please select or create an event first")
            return
        
        self.open_specimen_dialog()
    
    def open_specimen_dialog(self, specimen=None):
        """Open dialog for adding/editing a specimen"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Specimen Details")
        dialog.geometry("500x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        row = 0
        
        ttk.Label(scrollable_frame, text="ID:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=specimen["id"] if specimen else f"spec-{uuid.uuid4().hex[:8]}")
        ttk.Entry(scrollable_frame, textvariable=id_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Name:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=specimen["name"] if specimen else "")
        ttk.Entry(scrollable_frame, textvariable=name_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Locality:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        locality_var = tk.StringVar(value=specimen["locality"] if specimen else "")
        ttk.Entry(scrollable_frame, textvariable=locality_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Description:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        desc_text = tk.Text(scrollable_frame, height=3, width=40)
        desc_text.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            desc_text.insert(1.0, specimen.get("description", ""))
        
        row += 1
        ttk.Label(scrollable_frame, text="Rarity:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        rarity_var = tk.StringVar(value=specimen.get("rarity", "common") if specimen else "common")
        rarity_combo = ttk.Combobox(scrollable_frame, textvariable=rarity_var, values=["common", "uncommon", "rare", "legendary"], width=37)
        rarity_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Photo URL:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        photo_var = tk.StringVar(value=specimen.get("photoUrl", "") if specimen else "")
        photo_frame = ttk.Frame(scrollable_frame)
        photo_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Entry(photo_frame, textvariable=photo_var, width=30).pack(side=tk.LEFT)
        ttk.Button(photo_frame, text="Browse", command=lambda: self.browse_file(photo_var)).pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1
        ttk.Label(scrollable_frame, text="Audio Note URL:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        audio_var = tk.StringVar(value=specimen.get("audioNoteUrl", "") if specimen else "")
        audio_frame = ttk.Frame(scrollable_frame)
        audio_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Entry(audio_frame, textvariable=audio_var, width=30).pack(side=tk.LEFT)
        ttk.Button(audio_frame, text="Browse", command=lambda: self.browse_file(audio_var)).pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1
        ttk.Label(scrollable_frame, text="Composition:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        composition_text = tk.Text(scrollable_frame, height=3, width=40)
        composition_text.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            composition_text.insert(1.0, specimen.get("composition", ""))
        
        row += 1
        ttk.Label(scrollable_frame, text="Fun Facts:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        fun_facts_text = tk.Text(scrollable_frame, height=4, width=40)
        fun_facts_text.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            fun_facts_text.insert(1.0, specimen.get("funFacts", ""))
        
        row += 1
        ttk.Label(scrollable_frame, text="Story:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        story_text = tk.Text(scrollable_frame, height=6, width=40)
        story_text.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            story_text.insert(1.0, specimen.get("story", ""))
        
        scrollable_frame.columnconfigure(1, weight=1)
        
        def save_specimen():
            specimen_data = {
                "id": id_var.get(),
                "name": name_var.get(),
                "locality": locality_var.get(),
                "description": desc_text.get(1.0, tk.END).strip(),
                "rarity": rarity_var.get(),
                "photoUrl": photo_var.get(),
                "audioNoteUrl": audio_var.get(),
                "composition": composition_text.get(1.0, tk.END).strip(),
                "funFacts": fun_facts_text.get(1.0, tk.END).strip(),
                "story": story_text.get(1.0, tk.END).strip(),
                "imageUrl": None  # Keep for backward compatibility
            }
            
            if specimen:  # Editing existing
                for i, s in enumerate(self.current_event["specimens"]):
                    if s["id"] == specimen["id"]:
                        self.current_event["specimens"][i] = specimen_data
                        break
            else:  # Adding new
                self.current_event["specimens"].append(specimen_data)
            
            self.load_event_to_form()
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row+1, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save", command=save_specimen).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def remove_specimen(self):
        """Remove selected specimen"""
        if not self.current_event:
            return
        
        selection = self.specimens_tree.selection()
        if selection:
            specimen_id = selection[0]
            if messagebox.askyesno("Confirm Delete", "Remove this specimen?"):
                self.current_event["specimens"] = [s for s in self.current_event["specimens"] if s["id"] != specimen_id]
                self.load_event_to_form()
    
    def edit_specimen(self, event):
        """Edit selected specimen"""
        selection = self.specimens_tree.selection()
        if selection:
            specimen_id = selection[0]
            specimen = next((s for s in self.current_event["specimens"] if s["id"] == specimen_id), None)
            if specimen:
                self.open_specimen_dialog(specimen)
    
    def add_badge(self):
        """Add a new badge to the current event"""
        if not self.current_event:
            messagebox.showwarning("No Event", "Please select or create an event first")
            return
        
        self.open_badge_dialog()
    
    def open_badge_dialog(self, badge=None):
        """Open dialog for adding/editing a badge"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Badge Details")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        ttk.Label(dialog, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=badge["id"] if badge else f"badge-{uuid.uuid4().hex[:8]}")
        ttk.Entry(dialog, textvariable=id_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(dialog, text="Title:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        title_var = tk.StringVar(value=badge["title"] if badge else "")
        ttk.Entry(dialog, textvariable=title_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(dialog, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        desc_text = tk.Text(dialog, height=3, width=30)
        desc_text.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        if badge:
            desc_text.insert(1.0, badge["description"])
        
        ttk.Label(dialog, text="Icon:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        icon_var = tk.StringVar(value=badge.get("icon", "star.fill") if badge else "star.fill")
        ttk.Entry(dialog, textvariable=icon_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(dialog, text="Color:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        color_var = tk.StringVar(value=badge.get("color", "blue") if badge else "blue")
        color_combo = ttk.Combobox(dialog, textvariable=color_var, values=["blue", "gold", "green", "red", "purple"])
        color_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(dialog, text="Requirement Type:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        req_type_var = tk.StringVar(value=badge.get("requirementType", "collect_count") if badge else "collect_count")
        req_type_combo = ttk.Combobox(dialog, textvariable=req_type_var, values=["collect_count", "collect_all", "scan_specific"])
        req_type_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(dialog, text="Requirement Value:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        req_value_var = tk.IntVar(value=badge.get("requirement", 1) if badge else 1)
        ttk.Entry(dialog, textvariable=req_value_var).grid(row=6, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        dialog.columnconfigure(1, weight=1)
        
        def save_badge():
            badge_data = {
                "id": id_var.get(),
                "title": title_var.get(),
                "description": desc_text.get(1.0, tk.END).strip(),
                "icon": icon_var.get(),
                "color": color_var.get(),
                "requirement": req_value_var.get(),
                "requirementType": req_type_var.get()
            }
            
            if badge:  # Editing existing
                for i, b in enumerate(self.current_event["badges"]):
                    if b["id"] == badge["id"]:
                        self.current_event["badges"][i] = badge_data
                        break
            else:  # Adding new
                self.current_event["badges"].append(badge_data)
            
            self.load_event_to_form()
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save", command=save_badge).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def browse_file(self, target_var):
        """Browse for a file and update the target variable"""
        filename = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("Audio files", "*.mp3 *.wav *.m4a *.aac *.ogg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            # Convert to relative path if possible
            try:
                rel_path = os.path.relpath(filename, os.getcwd())
                target_var.set(rel_path)
            except:
                target_var.set(filename)
    
    def remove_badge(self):
        """Remove selected badge"""
        if not self.current_event:
            return
        
        selection = self.badges_tree.selection()
        if selection:
            badge_id = selection[0]
            if messagebox.askyesno("Confirm Delete", "Remove this badge?"):
                self.current_event["badges"] = [b for b in self.current_event["badges"] if b["id"] != badge_id]
                self.load_event_to_form()
    
    def edit_badge(self, event):
        """Edit selected badge"""
        selection = self.badges_tree.selection()
        if selection:
            badge_id = selection[0]
            badge = next((b for b in self.current_event["badges"] if b["id"] == badge_id), None)
            if badge:
                self.open_badge_dialog(badge)
    
    def clear_form(self):
        """Clear all form fields"""
        for field, var in self.event_vars.items():
            if field == "description":
                var[0].set("")
                var[1].delete(1.0, tk.END)
            else:
                var.set("")
        
        self.specimens_tree.delete(*self.specimens_tree.get_children())
        self.badges_tree.delete(*self.badges_tree.get_children())


def main():
    root = tk.Tk()
    app = SpecimenProEventManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
