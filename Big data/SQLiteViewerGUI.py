import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Global variables for auto-update and current table
auto_update_enabled = False
current_table = None
update_interval = 5000  # update every 5000 ms (5 seconds)

def list_tables(cursor):
    """Return a list of table names in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]

def load_table_data(cursor, table_name):
    """Retrieve column names and rows from the selected table."""
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error accessing table: {e}")
        return [], []
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return columns, rows

def refresh_table():
    """Refresh the currently selected table if auto-update is enabled."""
    global current_table
    if auto_update_enabled and current_table:
        columns, rows = load_table_data(cursor, current_table)
        # Clear the previous tree view data
        for item in tree.get_children():
            tree.delete(item)
        tree["columns"] = columns
        tree["show"] = "headings"
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        # Insert rows into the treeview
        for row in rows:
            tree.insert("", "end", values=row)
    # Schedule next refresh
    root.after(update_interval, refresh_table)

def on_table_select(event):
    """Callback for when a table is selected from the listbox."""
    global current_table
    selected = listbox_tables.curselection()
    if not selected:
        current_table = None
        return
    current_table = listbox_tables.get(selected[0])
    columns, rows = load_table_data(cursor, current_table)
    # Clear the previous tree view data
    for item in tree.get_children():
        tree.delete(item)
    tree["columns"] = columns
    tree["show"] = "headings"
    # Configure columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)
    # Insert rows into the treeview
    for row in rows:
        tree.insert("", "end", values=row)

def toggle_auto_update():
    """Toggle the auto-update feature on or off."""
    global auto_update_enabled
    auto_update_enabled = not auto_update_enabled
    status = "enabled" if auto_update_enabled else "disabled"
    messagebox.showinfo("Auto Update", f"Auto-update is now {status}.")

def load_database():
    """Open a file dialog to choose a database and load its tables."""
    db_file = filedialog.askopenfilename(
        title="Select SQLite Database",
        filetypes=[("SQLite DB Files", "*.db *.sqlite *.sqlite3"), ("All Files", "*.*")]
    )
    if db_file:
        try:
            global conn, cursor
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            tables = list_tables(cursor)
            listbox_tables.delete(0, tk.END)
            for table in tables:
                listbox_tables.insert(tk.END, table)
            root.title(f"SQLite Visual - {db_file}")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Could not connect to database: {e}")

# Main application window
root = tk.Tk()
root.title("SQLite Visual")
root.geometry("800x600")

# Create a menu bar with option to load a database file
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Open Database", command=load_database)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

# Left frame: List of tables and auto-update toggle
frame_left = tk.Frame(root, width=200)
frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

label_tables = tk.Label(frame_left, text="Tables", font=("Arial", 12, "bold"))
label_tables.pack(pady=5)

listbox_tables = tk.Listbox(frame_left)
listbox_tables.pack(fill=tk.BOTH, expand=True)
listbox_tables.bind("<<ListboxSelect>>", on_table_select)

btn_auto_update = tk.Button(frame_left, text="Toggle Auto-Update", command=toggle_auto_update)
btn_auto_update.pack(pady=10)

# Right frame: Table data display
frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

tree = ttk.Treeview(frame_right)
tree.pack(fill=tk.BOTH, expand=True)

# Start the auto-update loop
root.after(update_interval, refresh_table)

root.mainloop()
