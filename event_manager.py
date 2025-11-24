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
import shutil
try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    QR_CODE_AVAILABLE = True
except ImportError:
    QR_CODE_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


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
        self.event_vars = {}
        
        # Event ID
        ttk.Label(event_frame, text="Event ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        id_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=id_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["id"] = id_var
        row += 1
        
        # Title
        ttk.Label(event_frame, text="Title:").grid(row=row, column=0, sticky=tk.W, pady=5)
        title_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=title_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["title"] = title_var
        row += 1
        
        # Description
        ttk.Label(event_frame, text="Description:").grid(row=row, column=0, sticky=tk.W, pady=5)
        desc_var = tk.StringVar()
        desc_entry = tk.Text(event_frame, height=4, width=50)
        desc_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["description"] = (desc_var, desc_entry)
        row += 1
        
        # Type
        ttk.Label(event_frame, text="Type:").grid(row=row, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(event_frame, textvariable=type_var, values=["exhibit", "scavenger_hunt", "competition", "workshop"])
        type_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["type"] = type_var
        row += 1
        
        # Location
        ttk.Label(event_frame, text="Location:").grid(row=row, column=0, sticky=tk.W, pady=5)
        location_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=location_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["location"] = location_var
        row += 1
        
        # Latitude
        ttk.Label(event_frame, text="Latitude:").grid(row=row, column=0, sticky=tk.W, pady=5)
        latitude_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=latitude_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["latitude"] = latitude_var
        row += 1
        
        # Longitude
        ttk.Label(event_frame, text="Longitude:").grid(row=row, column=0, sticky=tk.W, pady=5)
        longitude_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=longitude_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["longitude"] = longitude_var
        row += 1
        
        # Radius in Meters
        ttk.Label(event_frame, text="Radius (meters):").grid(row=row, column=0, sticky=tk.W, pady=5)
        radius_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=radius_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["radiusMeters"] = radius_var
        row += 1
        
        # Always Visible
        ttk.Label(event_frame, text="Always Visible:").grid(row=row, column=0, sticky=tk.W, pady=5)
        always_visible_var = tk.BooleanVar()
        ttk.Checkbutton(event_frame, variable=always_visible_var).grid(row=row, column=1, sticky=tk.W, pady=5)
        self.event_vars["alwaysVisible"] = always_visible_var
        row += 1
        
        # Status
        ttk.Label(event_frame, text="Status:").grid(row=row, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(event_frame, textvariable=status_var, values=["active", "upcoming", "ended", "draft"])
        status_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["status"] = status_var
        row += 1
        
        # Start Date
        ttk.Label(event_frame, text="Start Date:").grid(row=row, column=0, sticky=tk.W, pady=5)
        start_date_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=start_date_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["startDate"] = start_date_var
        row += 1
        
        # End Date
        ttk.Label(event_frame, text="End Date:").grid(row=row, column=0, sticky=tk.W, pady=5)
        end_date_var = tk.StringVar()
        ttk.Entry(event_frame, textvariable=end_date_var).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.event_vars["endDate"] = end_date_var
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
        qr_menu = tk.Menu(self.root, tearoff=0)
        qr_menu.add_command(label="Save as PNG Files", command=self.generate_qr_codes)
        qr_menu.add_command(label="Save as PDF Grid", command=self.generate_qr_pdf)
        
        qr_button = ttk.Menubutton(button_frame, text="Generate QR Codes ▼")
        qr_button['menu'] = qr_menu
        qr_button.pack(side=tk.LEFT, padx=(10, 0))
        
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
            elif field == "alwaysVisible":
                # Handle null/true values: null or False -> unchecked, True -> checked
                value = self.current_event.get(field)
                var.set(value is True)
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
            "latitude": 0.0,
            "longitude": 0.0,
            "radiusMeters": 100,
            "alwaysVisible": None,
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
            elif field == "alwaysVisible":
                # Save as true if checked, null if unchecked
                self.current_event[field] = True if var.get() else None
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
        dialog.geometry("700x900")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configure dialog to be resizable
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make canvas window resize with canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Form fields
        row = 0
        
        ttk.Label(scrollable_frame, text="ID:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=specimen["id"] if specimen else f"spec-{uuid.uuid4().hex[:8]}")
        ttk.Entry(scrollable_frame, textvariable=id_var, width=50).grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Name:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=specimen["name"] if specimen else "")
        ttk.Entry(scrollable_frame, textvariable=name_var, width=50).grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Locality:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        locality_var = tk.StringVar(value=specimen["locality"] if specimen else "")
        ttk.Entry(scrollable_frame, textvariable=locality_var, width=50).grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Description:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        desc_text = tk.Text(scrollable_frame, height=5, width=50, wrap=tk.WORD)
        desc_text.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            desc_text.insert(1.0, specimen.get("description", ""))
        
        row += 1
        ttk.Label(scrollable_frame, text="Rarity:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        rarity_var = tk.StringVar(value=specimen.get("rarity", "common") if specimen else "common")
        rarity_combo = ttk.Combobox(scrollable_frame, textvariable=rarity_var, values=["common", "uncommon", "rare", "legendary"], width=47)
        rarity_combo.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        row += 1
        ttk.Label(scrollable_frame, text="Photo URL:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        photo_var = tk.StringVar(value=specimen.get("photoUrl", "") if specimen else "")
        photo_frame = ttk.Frame(scrollable_frame)
        photo_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Entry(photo_frame, textvariable=photo_var, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(photo_frame, text="Browse", command=lambda: self.browse_and_copy_file(photo_var, "images")).pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1
        ttk.Label(scrollable_frame, text="Audio Note URL:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        audio_var = tk.StringVar(value=specimen.get("audioNoteUrl", "") if specimen else "")
        audio_frame = ttk.Frame(scrollable_frame)
        audio_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Entry(audio_frame, textvariable=audio_var, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(audio_frame, text="Browse", command=lambda: self.browse_and_copy_file(audio_var, "audio")).pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1
        ttk.Label(scrollable_frame, text="Composition:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        comp_container = ttk.Frame(scrollable_frame)
        comp_container.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Unicode buttons for composition - stacked in three rows
        composition_text = tk.Text(scrollable_frame, height=4, width=50, wrap=tk.WORD)
        
        # Row 1: Subscripts
        sub_frame = ttk.Frame(comp_container)
        sub_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(sub_frame, text="Sub:").pack(side=tk.LEFT, padx=(0, 5))
        
        subscripts = [('0', '₀'), ('1', '₁'), ('2', '₂'), ('3', '₃'), ('4', '₄'), ('5', '₅'), ('6', '₆'), ('7', '₇'), ('8', '₈'), ('9', '₉')]
        for label, sub in subscripts:
            ttk.Button(sub_frame, text=sub, width=2, 
                      command=lambda s=sub: composition_text.insert(tk.INSERT, s)).pack(side=tk.LEFT, padx=1)
        
        # Row 2: Superscripts
        sup_frame = ttk.Frame(comp_container)
        sup_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(sup_frame, text="Sup:").pack(side=tk.LEFT, padx=(0, 5))
        
        superscripts = [('0', '⁰'), ('1', '¹'), ('2', '²'), ('3', '³'), ('4', '⁴'), ('5', '⁵'), ('6', '⁶'), ('7', '⁷'), ('8', '⁸'), ('9', '⁹')]
        for label, sup in superscripts:
            ttk.Button(sup_frame, text=sup, width=2,
                      command=lambda s=sup: composition_text.insert(tk.INSERT, s)).pack(side=tk.LEFT, padx=1)
        
        # Row 3: Special characters
        special_frame = ttk.Frame(comp_container)
        special_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(special_frame, text="Special:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Superscript plus/minus, subscript minus, superscript slash, center dot (hydration), empty box (vacancy)
        special_chars = [('⁺', '⁺'), ('⁻', '⁻'), ('₋', '₋'), ('ᐟ', 'ᐟ'), ('·', '·'), ('□', '□')]
        for label, char in special_chars:
            ttk.Button(special_frame, text=char, width=2,
                      command=lambda s=char: composition_text.insert(tk.INSERT, s)).pack(side=tk.LEFT, padx=1)
        
        composition_text.grid(row=row+1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            composition_text.insert(1.0, specimen.get("composition", ""))
        row += 2
        
        ttk.Label(scrollable_frame, text="Fun Facts:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        fun_facts_text = tk.Text(scrollable_frame, height=6, width=50, wrap=tk.WORD)
        fun_facts_text.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            fun_facts_text.insert(1.0, specimen.get("funFacts", ""))
        
        row += 1
        ttk.Label(scrollable_frame, text="Story:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=5)
        story_text = tk.Text(scrollable_frame, height=10, width=50, wrap=tk.WORD)
        story_text.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        if specimen:
            story_text.insert(1.0, specimen.get("story", ""))
        
        # Configure columns to expand with window
        scrollable_frame.columnconfigure(1, weight=1)
        scrollable_frame.columnconfigure(2, weight=1)
        
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
        
        # Grid canvas and scrollbar for proper resizing
        canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
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
        # Common SF Symbols for badges
        icon_options = [
            "star.fill",
            "star",
            "trophy.fill",
            "trophy",
            "medal.fill",
            "medal",
            "crown.fill",
            "crown",
            "rosette",
            "flag.fill",
            "flag",
            "checkmark.seal.fill",
            "checkmark.seal",
            "checkmark.circle.fill",
            "checkmark.circle",
            "bolt.fill",
            "bolt",
            "flame.fill",
            "flame",
            "sparkles",
            "heart.fill",
            "heart",
            "diamond.fill",
            "diamond",
            "gem.fill",
            "gem",
            "target",
            "scope",
            "eye.fill",
            "eye",
            "binoculars.fill",
            "binoculars",
            "magnifyingglass",
            "location.fill",
            "location",
            "map.fill",
            "map",
            "compass.drawing",
            "figure.walk",
            "figure.hiking"
        ]
        icon_combo = ttk.Combobox(dialog, textvariable=icon_var, values=icon_options, state="normal")
        icon_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
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
    
    def browse_and_copy_file(self, target_var, asset_type):
        """Browse for a file, copy it to assets folder, and set the GitHub Pages URL"""
        # Determine file types based on asset type
        if asset_type == "images":
            filetypes = [
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.svg"),
                ("All files", "*.*")
            ]
        elif asset_type == "audio":
            filetypes = [
                ("Audio files", "*.mp3 *.wav *.m4a *.aac *.ogg"),
                ("All files", "*.*")
            ]
        else:
            filetypes = [("All files", "*.*")]
        
        filename = filedialog.askopenfilename(
            title=f"Select {asset_type} file",
            filetypes=filetypes
        )
        
        if filename:
            try:
                # Create assets directory if it doesn't exist
                assets_dir = os.path.join(os.getcwd(), "assets", asset_type)
                os.makedirs(assets_dir, exist_ok=True)
                
                # Get the base filename
                base_filename = os.path.basename(filename)
                
                # Copy file to assets directory
                dest_path = os.path.join(assets_dir, base_filename)
                
                # If file already exists, ask user if they want to overwrite
                if os.path.exists(dest_path):
                    if not messagebox.askyesno("File Exists", f"{base_filename} already exists. Overwrite?"):
                        return
                
                shutil.copy2(filename, dest_path)
                
                # Generate GitHub Pages URL
                github_url = f"https://aaroncelestian.github.io/specimenpro-events/assets/{asset_type}/{base_filename}"
                target_var.set(github_url)
                
                messagebox.showinfo("Success", f"File copied to assets/{asset_type}/\nURL set to GitHub Pages location")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy file: {str(e)}")
    
    def browse_file(self, target_var):
        """Browse for a file and update the target variable (legacy method)"""
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
    
    def generate_qr_codes(self):
        """Generate QR codes for all specimens in the current event"""
        if not QR_CODE_AVAILABLE:
            messagebox.showerror("Error", "QR code generation requires the 'qrcode' library. Please install it with: pip install qrcode[pil]")
            return
            
        if not self.current_event:
            messagebox.showwarning("No Event", "Please select or create an event first")
            return
            
        specimens = self.current_event.get("specimens", [])
        if not specimens:
            messagebox.showwarning("No Specimens", "This event has no specimens to generate QR codes for")
            return
        
        # Ask user to select output directory
        output_dir = filedialog.askdirectory(title="Select directory to save QR codes")
        if not output_dir:
            return
        
        try:
            event_id = self.current_event["id"]
            generated_count = 0
            
            for specimen in specimens:
                specimen_id = specimen["id"]
                specimen_name = specimen["name"]
                
                # Create HTML URL with deep link fallback
                qr_url = f"https://aaroncelestian.github.io/specimenpro-events/event/{event_id}/{specimen_id}"
                
                # Generate QR code with high error correction
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=ERROR_CORRECT_H,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_url)
                qr.make(fit=True)
                
                # Create QR code image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Save with descriptive filename
                safe_name = "".join(c for c in specimen_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name}_{specimen_id}.png"
                filepath = os.path.join(output_dir, filename)
                
                img.save(filepath)
                generated_count += 1
            
            messagebox.showinfo("Success", f"Generated {generated_count} QR codes in:\n{output_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR codes: {str(e)}")
    
    def generate_qr_pdf(self):
        """Generate QR codes in a PDF grid layout"""
        if not QR_CODE_AVAILABLE:
            messagebox.showerror("Error", "QR code generation requires the 'qrcode' library. Please install it with: pip install qrcode[pil]")
            return
            
        if not PDF_AVAILABLE:
            messagebox.showerror("Error", "PDF generation requires the 'reportlab' library. Please install it with: pip install reportlab")
            return
            
        if not self.current_event:
            messagebox.showwarning("No Event", "Please select or create an event first")
            return
            
        specimens = self.current_event.get("specimens", [])
        if not specimens:
            messagebox.showwarning("No Specimens", "This event has no specimens to generate QR codes for")
            return
        
        # Show configuration dialog
        config = self.show_pdf_config_dialog()
        if not config:
            return
        
        try:
            # Ask user to select output file
            filename = filedialog.asksaveasfilename(
                title="Save QR Code PDF",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"{self.current_event['id']}_qr_codes.pdf"
            )
            if not filename:
                return
            
            self.create_pdf_qr_grid(filename, specimens, config)
            messagebox.showinfo("Success", f"Generated QR code PDF:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
    
    def show_pdf_config_dialog(self):
        """Show configuration dialog for PDF generation"""
        dialog = tk.Toplevel(self.root)
        dialog.title("PDF Configuration")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configuration variables
        config = {}
        
        # Page size
        ttk.Label(dialog, text="Page Size:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        page_size_var = tk.StringVar(value="Letter")
        page_size_combo = ttk.Combobox(dialog, textvariable=page_size_var, values=["Letter", "A4"], state="readonly")
        page_size_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Grid columns
        ttk.Label(dialog, text="Columns:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        columns_var = tk.IntVar(value=3)
        columns_spin = ttk.Spinbox(dialog, from_=1, to=10, textvariable=columns_var, width=10)
        columns_spin.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Grid rows
        ttk.Label(dialog, text="Rows:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        rows_var = tk.IntVar(value=4)
        rows_spin = ttk.Spinbox(dialog, from_=1, to=10, textvariable=rows_var, width=10)
        rows_spin.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # QR code size
        ttk.Label(dialog, text="QR Code Size:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        qr_size_var = tk.DoubleVar(value=1.0)
        qr_size_spin = ttk.Spinbox(dialog, from_=0.5, to=3.0, increment=0.1, textvariable=qr_size_var, width=10)
        qr_size_spin.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(dialog, text="(in inches)").grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Include specimen names
        include_names_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Include specimen names", variable=include_names_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # Include specimen IDs
        include_ids_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Include specimen IDs", variable=include_ids_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # Include event title
        include_title_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Include event title on first page", variable=include_title_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        dialog.columnconfigure(1, weight=1)
        
        def on_ok():
            config['page_size'] = page_size_var.get()
            config['columns'] = columns_var.get()
            config['rows'] = rows_var.get()
            config['qr_size'] = qr_size_var.get()
            config['include_names'] = include_names_var.get()
            config['include_ids'] = include_ids_var.get()
            config['include_title'] = include_title_var.get()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        ttk.Button(button_frame, text="Generate", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        return config if config else None
    
    def create_pdf_qr_grid(self, filename, specimens, config):
        """Create PDF with QR codes in a grid layout"""
        # Page setup
        page_size = letter if config['page_size'] == 'Letter' else A4
        doc = SimpleDocTemplate(filename, pagesize=page_size)
        story = []
        styles = getSampleStyleSheet()
        
        # Add title if requested
        if config['include_title']:
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center
            )
            title = Paragraph(f"SpecimenPro Event: {self.current_event['title']}", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
        
        # Calculate grid dimensions
        qr_size_inches = config['qr_size']
        qr_size_points = qr_size_inches * inch
        
        # Generate QR codes
        qr_data = []
        event_id = self.current_event["id"]
        
        for specimen in specimens:
            specimen_id = specimen["id"]
            specimen_name = specimen["name"]
            
            # Create HTML URL with deep link fallback
            qr_url = f"https://aaroncelestian.github.io/specimenpro-events/event/{event_id}/{specimen_id}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=2,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # Create QR code image and convert to bytes
            pil_img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = BytesIO()
            pil_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Create ReportLab Image
            rl_img = RLImage(img_buffer, width=qr_size_points, height=qr_size_points)
            
            # Create cell data
            cell_text = []
            if config['include_names']:
                cell_text.append(f"<b>{specimen_name}</b>")
            if config['include_ids']:
                cell_text.append(f"ID: {specimen_id}")
            
            qr_data.append((rl_img, "<br/>".join(cell_text)))
        
        # Create table data
        cols = config['columns']
        rows = config['rows']
        cells_per_page = cols * rows
        
        # Text style for labels
        label_style = ParagraphStyle(
            'QRLabel',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,  # Center
            spaceAfter=2
        )
        
        for page_start in range(0, len(qr_data), cells_per_page):
            page_data = qr_data[page_start:page_start + cells_per_page]
            
            # Create table grid
            table_data = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    idx = i * cols + j
                    if idx < len(page_data):
                        rl_img, text = page_data[idx]
                        
                        # Create cell content as a list
                        cell_content = []
                        
                        # Add QR code image
                        cell_content.append(rl_img)
                        
                        # Add text label if present
                        if text:
                            cell_content.append(Spacer(1, 5))
                            cell_content.append(Paragraph(text, label_style))
                        
                        row.append(cell_content)
                    else:
                        row.append("")
                table_data.append(row)
            
            # Calculate row heights based on content
            row_height = qr_size_points + (30 if config['include_names'] or config['include_ids'] else 10)
            
            # Create table
            table = Table(table_data, colWidths=[qr_size_points + 20] * cols, rowHeights=[row_height] * rows)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            story.append(table)
            
            # Add page break except for last page
            if page_start + cells_per_page < len(qr_data):
                from reportlab.platypus import PageBreak
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
    
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
