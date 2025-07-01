import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import threading
import time
import calendar

class TodoApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_database()
        self.build_ui()
        self.refresh_tasks()
        self.start_reminder_checker()
        
    def setup_database(self):
        """Initialize SQLite database"""
        self.connection = sqlite3.connect('todo_tasks.db')
        self.cursor = self.connection.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                due_date TEXT,
                due_time TEXT,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Pending',
                reminder_enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                week_day TEXT
            )
        ''')
        self.connection.commit()
        
    def build_ui(self):
        """Create the user interface"""
        self.root.title("Advanced Todo Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Header with live time
        header_frame = tk.Frame(self.root, bg='#2c5aa0', height=80)
        header_frame.pack(fill='x', pady=(0,10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="📋 Advanced Todo Manager", 
                              font=('Arial', 18, 'bold'), bg='#2c5aa0', fg='white')
        title_label.pack(pady=10)
        
        self.time_label = tk.Label(header_frame, font=('Arial', 12), bg='#2c5aa0', fg='#cccccc')
        self.time_label.pack()
        self.update_time()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left side - Input form
        left_frame = tk.LabelFrame(main_frame, text="Add/Edit Task", font=('Arial', 12, 'bold'), 
                                  bg='#ffffff', fg='#2c5aa0', padx=15, pady=15)
        left_frame.pack(side='left', fill='y', padx=(0,10))
        
        # Task description
        tk.Label(left_frame, text="Task Description:", font=('Arial', 10, 'bold'), 
                bg='#ffffff').grid(row=0, column=0, sticky='w', pady=5)
        
        self.task_text = tk.Text(left_frame, height=4, width=35, font=('Arial', 10), 
                                wrap=tk.WORD, relief='solid', bd=1)
        self.task_text.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')
        
        # Date selection with calendar popup
        tk.Label(left_frame, text="Due Date:", font=('Arial', 10, 'bold'), 
                bg='#ffffff').grid(row=2, column=0, sticky='w', pady=5)
        
        date_frame = tk.Frame(left_frame, bg='#ffffff')
        date_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(date_frame, textvariable=self.date_var, font=('Arial', 10),
                                  relief='solid', bd=1, width=20)
        self.date_entry.pack(side='left', padx=(0,5))
        
        self.calendar_btn = tk.Button(date_frame, text="📅", font=('Arial', 12),
                                     command=self.show_calendar, bg='#e0e0e0')
        self.calendar_btn.pack(side='left')
        
        # Time selection
        tk.Label(left_frame, text="Due Time:", font=('Arial', 10, 'bold'), 
                bg='#ffffff').grid(row=4, column=0, sticky='w', pady=5)
        
        time_frame = tk.Frame(left_frame, bg='#ffffff')
        time_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")
        self.ampm_var = tk.StringVar(value="PM")
        
        hour_spin = tk.Spinbox(time_frame, from_=1, to=12, textvariable=self.hour_var,
                              width=3, font=('Arial', 10))
        hour_spin.pack(side='left', padx=2)
        
        tk.Label(time_frame, text=":", bg='#ffffff', font=('Arial', 12)).pack(side='left')
        
        minute_spin = tk.Spinbox(time_frame, from_=0, to=59, textvariable=self.minute_var,
                               width=3, font=('Arial', 10), format="%02.0f")
        minute_spin.pack(side='left', padx=2)
        
        ampm_combo = ttk.Combobox(time_frame, textvariable=self.ampm_var, 
                                 values=["AM", "PM"], width=3, state="readonly")
        ampm_combo.pack(side='left', padx=5)
        
        # Priority selection
        tk.Label(left_frame, text="Priority:", font=('Arial', 10, 'bold'), 
                bg='#ffffff').grid(row=6, column=0, sticky='w', pady=5)
        
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(left_frame, textvariable=self.priority_var,
                                     values=["Low", "Medium", "High", "Critical"], 
                                     state="readonly", width=32)
        priority_combo.grid(row=7, column=0, columnspan=2, pady=5, sticky='ew')
        
        # Reminder checkbox
        self.reminder_var = tk.BooleanVar()
        reminder_check = tk.Checkbutton(left_frame, text="Enable Reminder Notification",
                                       variable=self.reminder_var, bg='#ffffff',
                                       font=('Arial', 10))
        reminder_check.grid(row=8, column=0, columnspan=2, pady=10, sticky='w')
        
        # Action buttons
        button_frame = tk.Frame(left_frame, bg='#ffffff')
        button_frame.grid(row=9, column=0, columnspan=2, pady=15, sticky='ew')
        
        self.add_btn = tk.Button(button_frame, text="➕ Add Task", command=self.add_task,
                                bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                                relief='flat', padx=20, pady=8)
        self.add_btn.pack(fill='x', pady=2)
        
        self.update_btn = tk.Button(button_frame, text="✏️ Update Task", command=self.update_task,
                                   bg='#ffc107', fg='black', font=('Arial', 10, 'bold'),
                                   relief='flat', padx=20, pady=8)
        self.update_btn.pack(fill='x', pady=2)
        
        self.complete_btn = tk.Button(button_frame, text="✅ Mark Complete", command=self.complete_task,
                                     bg='#17a2b8', fg='white', font=('Arial', 10, 'bold'),
                                     relief='flat', padx=20, pady=8)
        self.complete_btn.pack(fill='x', pady=2)
        
        self.delete_btn = tk.Button(button_frame, text="🗑️ Delete Task", command=self.delete_task,
                                   bg='#dc3545', fg='white', font=('Arial', 10, 'bold'),
                                   relief='flat', padx=20, pady=8)
        self.delete_btn.pack(fill='x', pady=2)
        
        clear_btn = tk.Button(button_frame, text="🧹 Clear Form", command=self.clear_form,
                             bg='#6c757d', fg='white', font=('Arial', 10, 'bold'),
                             relief='flat', padx=20, pady=8)
        clear_btn.pack(fill='x', pady=2)
        
        # Right side - Task list
        right_frame = tk.LabelFrame(main_frame, text="Task List", font=('Arial', 12, 'bold'),
                                   bg='#ffffff', fg='#2c5aa0', padx=15, pady=15)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Filter options
        filter_frame = tk.Frame(right_frame, bg='#ffffff')
        filter_frame.pack(fill='x', pady=(0,10))
        
        tk.Label(filter_frame, text="Filter:", font=('Arial', 10, 'bold'), bg='#ffffff').pack(side='left')
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["All", "Pending", "Completed", "High Priority", "Today's Tasks"],
                                   state="readonly", width=15)
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
        refresh_btn = tk.Button(filter_frame, text="🔄", command=self.refresh_tasks,
                               bg='#e0e0e0', relief='flat')
        refresh_btn.pack(side='right')
        
        # Task listbox with scrollbar
        list_frame = tk.Frame(right_frame, bg='#ffffff')
        list_frame.pack(fill='both', expand=True)
        
        self.task_listbox = tk.Listbox(list_frame, font=('Courier', 9), selectmode=tk.SINGLE,
                                      height=20, bg='#f8f9fa', relief='solid', bd=1)
        
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=self.task_listbox.yview)
        self.task_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.task_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)
        
        # Selected task info
        self.selected_task_id = None
        
    def update_time(self):
        """Update the live time display"""
        now = datetime.datetime.now()
        time_str = now.strftime("%A, %B %d, %Y | %I:%M:%S %p")
        self.time_label.config(text=time_str)
        self.root.after(1000, self.update_time)
        
    def show_calendar(self):
        """Show calendar popup for date selection"""
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Select Date")
        cal_window.geometry("300x250")
        cal_window.resizable(False, False)
        cal_window.configure(bg='#ffffff')
        
        # Center the window
        cal_window.transient(self.root)
        cal_window.grab_set()
        
        now = datetime.datetime.now()
        
        # Month/Year selection
        nav_frame = tk.Frame(cal_window, bg='#ffffff')
        nav_frame.pack(pady=10)
        
        self.cal_month = tk.IntVar(value=now.month)
        self.cal_year = tk.IntVar(value=now.year)
        
        tk.Button(nav_frame, text="◀", command=lambda: self.change_month(-1, cal_frame, cal_window),
                 bg='#e0e0e0').pack(side='left')
        
        month_label = tk.Label(nav_frame, text=f"{calendar.month_name[now.month]} {now.year}",
                              font=('Arial', 12, 'bold'), bg='#ffffff')
        month_label.pack(side='left', padx=20)
        self.month_label = month_label
        
        tk.Button(nav_frame, text="▶", command=lambda: self.change_month(1, cal_frame, cal_window),
                 bg='#e0e0e0').pack(side='left')
        
        # Calendar frame
        cal_frame = tk.Frame(cal_window, bg='#ffffff')
        cal_frame.pack(pady=10)
        
        self.create_calendar(cal_frame, cal_window)
        
    def change_month(self, direction, cal_frame, cal_window):
        """Change month in calendar"""
        new_month = self.cal_month.get() + direction
        new_year = self.cal_year.get()
        
        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1
            
        self.cal_month.set(new_month)
        self.cal_year.set(new_year)
        
        self.month_label.config(text=f"{calendar.month_name[new_month]} {new_year}")
        
        # Clear and recreate calendar
        for widget in cal_frame.winfo_children():
            widget.destroy()
        self.create_calendar(cal_frame, cal_window)
        
    def create_calendar(self, parent, cal_window):
        """Create calendar grid"""
        month = self.cal_month.get()
        year = self.cal_year.get()
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            tk.Label(parent, text=day, font=('Arial', 10, 'bold'), bg='#e9ecef',
                    width=4, height=1).grid(row=0, column=i, padx=1, pady=1)
        
        # Calendar days
        cal = calendar.monthcalendar(year, month)
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    tk.Label(parent, text="", width=4, height=2, bg='#ffffff').grid(
                        row=week_num+1, column=day_num, padx=1, pady=1)
                else:
                    btn = tk.Button(parent, text=str(day), width=4, height=2,
                                   command=lambda d=day: self.select_date(d, cal_window),
                                   bg='#f8f9fa', relief='solid', bd=1)
                    btn.grid(row=week_num+1, column=day_num, padx=1, pady=1)
                    
                    # Highlight today
                    today = datetime.date.today()
                    if (day == today.day and month == today.month and year == today.year):
                        btn.config(bg='#007bff', fg='white', font=('Arial', 10, 'bold'))
                        
    def select_date(self, day, cal_window):
        """Handle date selection from calendar"""
        month = self.cal_month.get()
        year = self.cal_year.get()
        
        selected_date = datetime.date(year, month, day)
        date_str = selected_date.strftime("%Y-%m-%d")
        
        self.date_var.set(date_str)
        cal_window.destroy()
        
    def add_task(self):
        """Add new task to database"""
        task = self.task_text.get("1.0", tk.END).strip()
        if not task:
            messagebox.showwarning("Input Error", "Please enter a task description!")
            return
            
        due_date = self.date_var.get()
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        ampm = self.ampm_var.get()
        
        due_time = ""
        week_day = ""
        
        if due_date:
            try:
                date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d")
                week_day = date_obj.strftime("%A")
            except ValueError:
                messagebox.showerror("Date Error", "Invalid date format! Use YYYY-MM-DD")
                return
        
        if hour and minute:
            # Convert to 24-hour format
            hour_24 = int(hour)
            if ampm == "PM" and hour_24 != 12:
                hour_24 += 12
            elif ampm == "AM" and hour_24 == 12:
                hour_24 = 0
            due_time = f"{hour_24:02d}:{int(minute):02d}"
        
        priority = self.priority_var.get()
        reminder = 1 if self.reminder_var.get() else 0
        
        self.cursor.execute('''
            INSERT INTO todos (task, due_date, due_time, priority, reminder_enabled, week_day)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (task, due_date, due_time, priority, reminder, week_day))
        
        self.connection.commit()
        self.refresh_tasks()
        self.clear_form()
        messagebox.showinfo("Success", "Task added successfully!")
        
    def update_task(self):
        """Update selected task"""
        if not self.selected_task_id:
            messagebox.showwarning("Selection Error", "Please select a task to update!")
            return
            
        task = self.task_text.get("1.0", tk.END).strip()
        if not task:
            messagebox.showwarning("Input Error", "Please enter a task description!")
            return
            
        due_date = self.date_var.get()
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        ampm = self.ampm_var.get()
        
        due_time = ""
        week_day = ""
        
        if due_date:
            try:
                date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d")
                week_day = date_obj.strftime("%A")
            except ValueError:
                messagebox.showerror("Date Error", "Invalid date format! Use YYYY-MM-DD")
                return
        
        if hour and minute:
            hour_24 = int(hour)
            if ampm == "PM" and hour_24 != 12:
                hour_24 += 12
            elif ampm == "AM" and hour_24 == 12:
                hour_24 = 0
            due_time = f"{hour_24:02d}:{int(minute):02d}"
        
        priority = self.priority_var.get()
        reminder = 1 if self.reminder_var.get() else 0
        
        self.cursor.execute('''
            UPDATE todos SET task=?, due_date=?, due_time=?, priority=?, 
            reminder_enabled=?, week_day=? WHERE id=?
        ''', (task, due_date, due_time, priority, reminder, week_day, self.selected_task_id))
        
        self.connection.commit()
        self.refresh_tasks()
        self.clear_form()
        messagebox.showinfo("Success", "Task updated successfully!")
        
    def complete_task(self):
        """Mark selected task as completed"""
        if not self.selected_task_id:
            messagebox.showwarning("Selection Error", "Please select a task to complete!")
            return
            
        self.cursor.execute("UPDATE todos SET status='Completed' WHERE id=?", (self.selected_task_id,))
        self.connection.commit()
        self.refresh_tasks()
        self.clear_form()
        messagebox.showinfo("Success", "Task marked as completed!")
        
    def delete_task(self):
        """Delete selected task"""
        if not self.selected_task_id:
            messagebox.showwarning("Selection Error", "Please select a task to delete!")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.cursor.execute("DELETE FROM todos WHERE id=?", (self.selected_task_id,))
            self.connection.commit()
            self.refresh_tasks()
            self.clear_form()
            messagebox.showinfo("Success", "Task deleted successfully!")
            
    def clear_form(self):
        """Clear all input fields"""
        self.task_text.delete("1.0", tk.END)
        self.date_var.set("")
        self.hour_var.set("12")
        self.minute_var.set("00")
        self.ampm_var.set("PM")
        self.priority_var.set("Medium")
        self.reminder_var.set(False)
        self.selected_task_id = None
        
    def refresh_tasks(self):
        """Refresh task list display"""
        self.task_listbox.delete(0, tk.END)
        
        query = "SELECT * FROM todos ORDER BY priority DESC, due_date ASC, due_time ASC"
        self.cursor.execute(query)
        tasks = self.cursor.fetchall()
        
        for task in tasks:
            task_id, description, due_date, due_time, priority, status, reminder, created_at, week_day = task
            
            # Format display
            status_icon = "✅" if status == "Completed" else "⏳"
            priority_icon = {"Low": "🔵", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}.get(priority, "⚪")
            reminder_icon = "🔔" if reminder else ""
            
            # Format time for display (convert back to 12-hour)
            time_display = ""
            if due_time:
                try:
                    time_obj = datetime.datetime.strptime(due_time, "%H:%M")
                    time_display = time_obj.strftime("%I:%M %p")
                except ValueError:
                    time_display = due_time
            
            due_info = ""
            if due_date:
                due_info = f" | {due_date}"
                if week_day:
                    due_info += f" ({week_day})"
                if time_display:
                    due_info += f" {time_display}"
            
            display_text = f"{status_icon} {priority_icon} {description[:50]}{'...' if len(description) > 50 else ''}{due_info} {reminder_icon}"
            
            self.task_listbox.insert(tk.END, f"ID:{task_id} | {display_text}")
            
    def apply_filter(self, event=None):
        """Apply filter to task list"""
        filter_type = self.filter_var.get()
        self.task_listbox.delete(0, tk.END)
        
        if filter_type == "All":
            query = "SELECT * FROM todos ORDER BY priority DESC, due_date ASC"
        elif filter_type == "Pending":
            query = "SELECT * FROM todos WHERE status='Pending' ORDER BY priority DESC, due_date ASC"
        elif filter_type == "Completed":
            query = "SELECT * FROM todos WHERE status='Completed' ORDER BY created_at DESC"
        elif filter_type == "High Priority":
            query = "SELECT * FROM todos WHERE priority IN ('High', 'Critical') ORDER BY priority DESC, due_date ASC"
        elif filter_type == "Today's Tasks":
            today = datetime.date.today().strftime("%Y-%m-%d")
            query = f"SELECT * FROM todos WHERE due_date='{today}' ORDER BY due_time ASC"
        
        self.cursor.execute(query)
        tasks = self.cursor.fetchall()
        
        for task in tasks:
            task_id, description, due_date, due_time, priority, status, reminder, created_at, week_day = task
            
            status_icon = "✅" if status == "Completed" else "⏳"
            priority_icon = {"Low": "🔵", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}.get(priority, "⚪")
            reminder_icon = "🔔" if reminder else ""
            
            time_display = ""
            if due_time:
                try:
                    time_obj = datetime.datetime.strptime(due_time, "%H:%M")
                    time_display = time_obj.strftime("%I:%M %p")
                except ValueError:
                    time_display = due_time
            
            due_info = ""
            if due_date:
                due_info = f" | {due_date}"
                if week_day:
                    due_info += f" ({week_day})"
                if time_display:
                    due_info += f" {time_display}"
            
            display_text = f"{status_icon} {priority_icon} {description[:50]}{'...' if len(description) > 50 else ''}{due_info} {reminder_icon}"
            self.task_listbox.insert(tk.END, f"ID:{task_id} | {display_text}")
            
    def on_task_select(self, event):
        """Handle task selection to populate form"""
        selection = self.task_listbox.curselection()
        if not selection:
            return
            
        selected_text = self.task_listbox.get(selection[0])
        task_id = int(selected_text.split(" | ")[0].replace("ID:", ""))
        
        self.cursor.execute("SELECT * FROM todos WHERE id=?", (task_id,))
        task = self.cursor.fetchone()
        
        if task:
            self.selected_task_id = task_id
            
            # Populate form
            self.task_text.delete("1.0", tk.END)
            self.task_text.insert("1.0", task[1])
            
            self.date_var.set(task[2] if task[2] else "")
            
            if task[3]:  # due_time
                try:
                    time_obj = datetime.datetime.strptime(task[3], "%H:%M")
                    hour_12 = time_obj.hour
                    ampm = "AM"
                    
                    if hour_12 == 0:
                        hour_12 = 12
                    elif hour_12 > 12:
                        hour_12 -= 12
                        ampm = "PM"
                    elif hour_12 == 12:
                        ampm = "PM"
                    
                    self.hour_var.set(str(hour_12))
                    self.minute_var.set(f"{time_obj.minute:02d}")
                    self.ampm_var.set(ampm)
                except ValueError:
                    pass
            
            self.priority_var.set(task[4])
            self.reminder_var.set(bool(task[6]))
            
    def start_reminder_checker(self):
        """Start background thread for checking reminders"""
        def check_reminders():
            while True:
                try:
                    now = datetime.datetime.now()
                    
                    # Check for tasks due in the next 15 minutes
                    self.cursor.execute('''
                        SELECT id, task, due_date, due_time FROM todos 
                        WHERE reminder_enabled=1 AND status='Pending' 
                        AND due_date IS NOT NULL
                    ''')
                    
                    reminder_tasks = self.cursor.fetchall()
                    
                    for task in reminder_tasks:
                        task_id, description, due_date, due_time = task
                        
                        try:
                            if due_time:
                                due_datetime = datetime.datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %H:%M")
                            else:
                                due_datetime = datetime.datetime.strptime(due_date, "%Y-%m-%d")
                            
                            time_diff = (due_datetime - now).total_seconds()
                            
                            # Alert if due within 15 minutes (900 seconds)
                            if 0 <= time_diff <= 900:
                                self.root.after(0, lambda: messagebox.showinfo(
                                    "Task Reminder", 
                                    f"⏰ Upcoming Task!\n\n{description}\n\nDue: {due_date} {due_time if due_time else ''}"
                                ))
                                
                                # Disable reminder after showing
                                self.cursor.execute("UPDATE todos SET reminder_enabled=0 WHERE id=?", (task_id,))
                                self.connection.commit()
                                
                        except ValueError:
                            continue
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception:
                    time.sleep(60)
        
        reminder_thread = threading.Thread(target=check_reminders, daemon=True)
        reminder_thread.start()
        
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        finally:
            self.connection.close()

# Create and run the application
if __name__ == "__main__":
    app = TodoApplication()
    app.run()