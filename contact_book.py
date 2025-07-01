import tkinter as tk
from tkinter import messagebox, font
import pickle
import hashlib
from datetime import datetime

class PersonalContactManager:
    def __init__(self):
        self.master = tk.Tk()
        self.initialize_application()
        self.contact_database = self.retrieve_contact_data()
        self.currently_selected = None
        self.setup_user_interface()
        self.populate_contact_display()
    
    def initialize_application(self):
        """Setup main application window properties"""
        self.master.title("Personal Contact Manager v2.1")
        self.master.geometry("1100x750")
        self.master.configure(bg="#1a1a2e")
        self.master.resizable(width=True, height=True)
        
        # Position window in center of screen
        screen_w = self.master.winfo_screenwidth()
        screen_h = self.master.winfo_screenheight()
        pos_x = (screen_w // 2) - (1100 // 2)
        pos_y = (screen_h // 2) - (750 // 2)
        self.master.geometry(f"1100x750+{pos_x}+{pos_y}")
        
        # Custom fonts
        self.header_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.entry_font = font.Font(family="Segoe UI", size=10)
    
    def retrieve_contact_data(self):
        """Load contact information from storage file"""
        storage_file = "personal_contacts.pkl"
        try:
            with open(storage_file, 'rb') as file:
                return pickle.load(file)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            return {}
    
    def persist_contact_data(self):
        """Save contact information to storage file"""
        storage_file = "personal_contacts.pkl"
        try:
            with open(storage_file, 'wb') as file:
                pickle.dump(self.contact_database, file)
            return True
        except Exception as error:
            messagebox.showerror("Storage Error", f"Unable to save data: {error}")
            return False
    
    def setup_user_interface(self):
        """Construct the complete user interface"""
        
        # Header section
        header_section = tk.Frame(self.master, bg="#16213e", height=90)
        header_section.pack(fill=tk.X, padx=15, pady=(15, 0))
        header_section.pack_propagate(False)
        
        main_title = tk.Label(header_section, text="🔗 Personal Contact Manager", 
                             font=self.header_font, bg="#16213e", fg="#00d4aa")
        main_title.place(relx=0.5, rely=0.5, anchor="center")
        
        # Central workspace
        workspace = tk.Frame(self.master, bg="#1a1a2e")
        workspace.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Contact listing panel
        listing_panel = tk.Frame(workspace, bg="#0f3460", relief=tk.RIDGE, bd=3)
        listing_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        list_header = tk.Label(listing_panel, text="📋 Contact Directory", 
                              font=self.label_font, bg="#0f3460", fg="#e94560")
        list_header.pack(pady=12)
        
        # Search interface
        search_section = tk.Frame(listing_panel, bg="#0f3460")
        search_section.pack(fill=tk.X, padx=15, pady=(0, 12))
        
        search_label = tk.Label(search_section, text="Find Contact:", 
                               bg="#0f3460", fg="#ffffff", font=self.label_font)
        search_label.pack(side=tk.LEFT)
        
        self.search_input = tk.StringVar()
        self.search_input.trace("w", self.perform_search)
        search_field = tk.Entry(search_section, textvariable=self.search_input, 
                               font=self.entry_font, bg="#ffffff", fg="#000000", width=20)
        search_field.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        
        # Contact list display
        list_container = tk.Frame(listing_panel, bg="#0f3460")
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Custom listbox with styling
        list_frame = tk.Frame(list_container, bg="#ffffff", relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_bar = tk.Scrollbar(list_frame, bg="#cccccc")
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.contact_list = tk.Listbox(list_frame, yscrollcommand=scroll_bar.set,
                                      font=self.entry_font, bg="#f8f9fa", fg="#212529",
                                      selectbackground="#007bff", selectforeground="#ffffff",
                                      relief=tk.FLAT, bd=0, highlightthickness=0)
        self.contact_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_bar.config(command=self.contact_list.yview)
        
        self.contact_list.bind("<<ListboxSelect>>", self.handle_contact_selection)
        
        # Data entry panel
        entry_panel = tk.Frame(workspace, bg="#533483", relief=tk.RIDGE, bd=3)
        entry_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
        
        form_header = tk.Label(entry_panel, text="📝 Contact Information", 
                              font=self.label_font, bg="#533483", fg="#ffd700")
        form_header.pack(pady=12)
        
        # Input form area
        form_area = tk.Frame(entry_panel, bg="#533483")
        form_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Input field definitions
        field_specs = [
            ("Full Name *", "contact_name"),
            ("Phone Number *", "contact_phone"), 
            ("Email Address *", "contact_email"),
            ("Home Address", "contact_address")
        ]
        
        self.input_fields = {}
        
        for idx, (display_name, field_key) in enumerate(field_specs):
            field_label = tk.Label(form_area, text=display_name, bg="#533483", 
                                  fg="#ffffff", font=self.label_font)
            field_label.grid(row=idx*2, column=0, sticky="w", pady=(8, 3))
            
            if field_key == "contact_address":
                input_widget = tk.Text(form_area, font=self.entry_font, height=4, width=35,
                                      bg="#ffffff", fg="#000000", relief=tk.SOLID, bd=1)
            else:
                input_widget = tk.Entry(form_area, font=self.entry_font, width=35,
                                       bg="#ffffff", fg="#000000", relief=tk.SOLID, bd=1)
            
            input_widget.grid(row=idx*2+1, column=0, pady=(0, 8), sticky="ew")
            self.input_fields[field_key] = input_widget
        
        form_area.columnconfigure(0, weight=1)
        
        # Required field notice
        notice = tk.Label(form_area, text="* Mandatory Information", 
                         bg="#533483", fg="#ff6b6b", font=("Segoe UI", 9, "italic"))
        notice.grid(row=len(field_specs)*2, column=0, sticky="w", pady=(5, 15))
        
        # Action buttons section
        button_section = tk.Frame(entry_panel, bg="#533483")
        button_section.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Button configuration
        button_style = {
            "width": 15,
            "height": 2,
            "font": self.label_font,
            "cursor": "hand2",
            "relief": "raised",
            "bd": 3
        }
        
        # Action buttons
        create_button = tk.Button(button_section, text="CREATE", 
                                 bg="#28a745", fg="#ffffff", activebackground="#218838",
                                 command=self.execute_create, **button_style)
        create_button.grid(row=0, column=0, padx=8, pady=8)
        
        update_button = tk.Button(button_section, text="UPDATE", 
                                 bg="#007bff", fg="#ffffff", activebackground="#0056b3",
                                 command=self.execute_update, **button_style)
        update_button.grid(row=0, column=1, padx=8, pady=8)
        
        delete_button = tk.Button(button_section, text="DELETE", 
                                 bg="#dc3545", fg="#ffffff", activebackground="#c82333",
                                 command=self.execute_delete, **button_style)
        delete_button.grid(row=1, column=0, padx=8, pady=8)
        
        modify_button = tk.Button(button_section, text="CLEAR", 
                                 bg="#6c757d", fg="#ffffff", activebackground="#5a6268",
                                 command=self.execute_clear, **button_style)
        modify_button.grid(row=1, column=1, padx=8, pady=8)
        
        button_section.columnconfigure(0, weight=1)
        button_section.columnconfigure(1, weight=1)
    
    def generate_contact_id(self, name):
        """Generate unique identifier for contact"""
        timestamp = str(datetime.now().timestamp())
        unique_string = f"{name.lower().strip()}{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def validate_contact_data(self, name, phone, email):
        """Verify that contact information is valid"""
        if not name.strip():
            messagebox.showerror("Input Error", "Contact name cannot be empty!")
            return False
        
        if not phone.strip():
            messagebox.showerror("Input Error", "Phone number is required!")
            return False
        
        if not email.strip():
            messagebox.showerror("Input Error", "Email address is required!")
            return False
        
        # Email format validation
        if "@" not in email or email.count("@") != 1 or "." not in email.split("@")[1]:
            messagebox.showerror("Format Error", "Invalid email address format!")
            return False
        
        # Phone number validation
        digits_only = ''.join(filter(str.isdigit, phone))
        if len(digits_only) < 10:
            messagebox.showerror("Format Error", "Phone number needs at least 10 digits!")
            return False
        
        return True
    
    def execute_create(self):
        """Add new contact to database"""
        name = self.input_fields["contact_name"].get().strip()
        phone = self.input_fields["contact_phone"].get().strip()
        email = self.input_fields["contact_email"].get().strip()
        address = self.input_fields["contact_address"].get("1.0", tk.END).strip()
        
        if not self.validate_contact_data(name, phone, email):
            return
        
        # Check for duplicate names
        for contact_info in self.contact_database.values():
            if contact_info["name"].lower() == name.lower():
                messagebox.showerror("Duplicate Error", "Contact with this name already exists!")
                return
        
        # Generate unique ID and store contact
        contact_id = self.generate_contact_id(name)
        self.contact_database[contact_id] = {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.persist_contact_data():
            messagebox.showinfo("Success", "New contact has been created!")
            self.execute_clear()
            self.populate_contact_display()
    
    def execute_update(self):
        """Modify existing contact information"""
        if not self.currently_selected:
            messagebox.showerror("Selection Error", "Please choose a contact to update!")
            return
        
        name = self.input_fields["contact_name"].get().strip()
        phone = self.input_fields["contact_phone"].get().strip()
        email = self.input_fields["contact_email"].get().strip()
        address = self.input_fields["contact_address"].get("1.0", tk.END).strip()
        
        if not self.validate_contact_data(name, phone, email):
            return
        
        # Check for name conflicts (excluding current contact)
        for contact_id, contact_info in self.contact_database.items():
            if (contact_id != self.currently_selected and 
                contact_info["name"].lower() == name.lower()):
                messagebox.showerror("Duplicate Error", "Another contact with this name exists!")
                return
        
        # Update contact information
        self.contact_database[self.currently_selected].update({
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        if self.persist_contact_data():
            messagebox.showinfo("Success", "Contact information has been updated!")
            self.populate_contact_display()
    
    def execute_delete(self):
        """Remove contact from database"""
        if not self.currently_selected:
            messagebox.showerror("Selection Error", "Please choose a contact to delete!")
            return
        
        contact_name = self.contact_database[self.currently_selected]["name"]
        confirm = messagebox.askyesno("Confirm Deletion", 
                                     f"Delete contact '{contact_name}'?\n\nThis action cannot be undone.")
        
        if confirm:
            del self.contact_database[self.currently_selected]
            if self.persist_contact_data():
                messagebox.showinfo("Success", "Contact has been removed!")
                self.execute_clear()
                self.populate_contact_display()
                self.currently_selected = None
    
    def execute_clear(self):
        """Reset all input fields"""
        self.input_fields["contact_name"].delete(0, tk.END)
        self.input_fields["contact_phone"].delete(0, tk.END)
        self.input_fields["contact_email"].delete(0, tk.END)
        self.input_fields["contact_address"].delete("1.0", tk.END)
        self.currently_selected = None
        
        # Clear search and selection
        self.search_input.set("")
        self.contact_list.selection_clear(0, tk.END)
    
    def populate_contact_display(self):
        """Refresh the contact list display"""
        self.contact_list.delete(0, tk.END)
        
        # Sort contacts alphabetically by name
        sorted_contacts = sorted(self.contact_database.items(), 
                               key=lambda x: x[1]["name"].lower())
        
        for contact_id, contact_info in sorted_contacts:
            display_text = f"{contact_info['name']} | {contact_info['phone']}"
            self.contact_list.insert(tk.END, display_text)
            # Store contact ID for reference
            self.contact_list.insert(tk.END, contact_id)
            self.contact_list.delete(tk.END)
    
    def handle_contact_selection(self, event):
        """Process contact selection from list"""
        selection = self.contact_list.curselection()
        if not selection:
            return
        
        selected_text = self.contact_list.get(selection[0])
        selected_name = selected_text.split(" | ")[0]
        
        # Find contact by name
        for contact_id, contact_info in self.contact_database.items():
            if contact_info["name"] == selected_name:
                self.currently_selected = contact_id
                
                # Populate form fields
                self.execute_clear()
                self.input_fields["contact_name"].insert(0, contact_info["name"])
                self.input_fields["contact_phone"].insert(0, contact_info["phone"])
                self.input_fields["contact_email"].insert(0, contact_info["email"])
                self.input_fields["contact_address"].insert("1.0", contact_info["address"])
                
                self.currently_selected = contact_id
                break
    
    def perform_search(self, *args):
        """Filter contacts based on search input"""
        search_term = self.search_input.get().lower()
        self.contact_list.delete(0, tk.END)
        
        # Filter and display matching contacts
        for contact_id, contact_info in self.contact_database.items():
            if (search_term in contact_info["name"].lower() or
                search_term in contact_info["phone"].lower() or
                search_term in contact_info["email"].lower() or
                search_term in contact_info["address"].lower() or
                search_term == ""):
                
                display_text = f"{contact_info['name']} | {contact_info['phone']}"
                self.contact_list.insert(tk.END, display_text)
    
    def start_application(self):
        """Launch the contact manager"""
        self.master.mainloop()

def launch_contact_manager():
    """Initialize and start the contact management application"""
    try:
        manager = PersonalContactManager()
        manager.start_application()
    except Exception as error:
        print(f"Application startup error: {error}")
        tk.messagebox.showerror("Startup Error", f"Failed to initialize application: {error}")

if __name__ == "__main__":
    launch_contact_manager()