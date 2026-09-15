import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import oracledb
from importlib.metadata import version as pkg_version
import os

DSN = os.getenv("ORACLE_DSN")

class WorkshopApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Workshop Registration System")
        self.con = None

        self.build_login_ui()

    def build_login_ui(self):
        self.login_frame = ttk.Frame(self.root, padding=30)
        self.login_frame.pack(fill="both", expand=True)

        ttk.Label(self.login_frame, text="User:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)

        self.user_entry = tk.StringVar()
        self.password_entry = tk.StringVar()

        user_entry = ttk.Entry(self.login_frame, textvariable=self.user_entry, width=30)
        password_entry = ttk.Entry(self.login_frame, textvariable=self.password_entry, show="·", width=30)

        user_entry.grid(row=0, column=1, pady=5)
        password_entry.grid(row=1, column=1, pady=5)

        connect_button = ttk.Button(self.login_frame, text="Connect", command=self.connect_to_db)
        connect_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.login_frame.columnconfigure(1, weight=1)

    def connect_to_db(self):
        user = self.user_entry.get().strip()
        password = self.password_entry.get()

        if not user or not password:
            messagebox.showerror("Input Error", "Please enter both username and password.")
            return
        try:
            print(f"Oracle DSN: {DSN}")
            self.con = oracledb.connect(user=user, password=password, dsn=DSN)
            print("Connected.")
            print("Database Product Name: Oracle")
            try:
                with self.con.cursor() as cursor:
                    cursor.execute("SELECT banner FROM v$version WHERE banner LIKE 'Oracle Database%'")
                    row = cursor.fetchone()
                if row:
                    banner = row[0]
                    split_token = "Release "
                    if split_token in banner:
                        before, after = banner.split(split_token, 1)
                        print("Database Product Version:",before + "Release " + after)
                    else:
                        print("Database Product Version:", banner)
                else:
                    print("Database Product Version: Oracle Database", self.con.version)
            except oracledb.DatabaseError:
                print("Database Product Version: Oracle Database", self.con.version)

            print(f"Version {self.con.version}")
            print("Database Driver: python-oracledb")

            try:
                major, minor, update, patch, port_update = oracledb.clientversion()
                driver_version = f"{major}.{minor}.{update}.{patch}.{port_update}"
            except Exception:
                try:
                    driver_version = pkg_version("oracledb")
                except Exception:
                    driver_version = getattr(oracledb, '__version__', 'unknown')
            print(f"Database Driver Version: {driver_version}")
            print()

            ok = self.ask_and_run_sql_script()
            if not ok:
                self.quit()
                return
            
        except oracledb.DatabaseError as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{e}")
            return
        
        self.login_frame.destroy()
        self.build_main_ui()

    def ask_and_run_sql_script(self):
        script_path = simpledialog.askstring("SQL Script\n", "Enter the path to the SQL script file:", parent=self.root)
        if script_path is None or not script_path.strip():
            return False
        script_path = script_path.strip()
        try:
            self.run_sql_script(script_path)
            messagebox.showinfo("Success", "SQL script executed successfully.")
            return True
        except ValueError as e:
            messagebox.showerror("Database Error", f"Error executing SQL script:\n{e}")
            return False
        except oracledb.DatabaseError as e:
            messagebox.showerror("Database Error", f"Error executing SQL script:\n{e}")
            return False

    def run_sql_script(self, script_path):
        try:
            with open(script_path, 'r') as file:
                sql_script = file.read()           
        
        except FileNotFoundError:
            raise ValueError(f"SQL script file not found: {script_path}")
        except OSError as e:
            raise ValueError(f"Error reading SQL script file: {e}")
        
        statements = []
        buffer_lines = []

        for line in sql_script.splitlines():
            stripped_line = line.strip()

            if stripped_line.startswith('--') or not stripped_line:
                continue

            buffer_lines.append(line)
            if stripped_line.endswith(';'):
                stmt = '\n'.join(buffer_lines)
                stmt = stmt.rstrip().rstrip(';')
                statements.append(stmt)
                buffer_lines = []
        if buffer_lines:
            stmt = '\n'.join(buffer_lines)
            if stmt:
                statements.append(stmt)
        
        with self.con.cursor() as cursor:
            for statement in statements:
                stmt = statement.strip()
                if not stmt:
                    continue
                try:
                    cursor.execute(stmt)
                except oracledb.DatabaseError as e:
                    error = e.args[0]
                    print(f"Error executing statement:\n{stmt}\nError Code: {error.code}, Message: {error.message}")
                    self.con.rollback()
                    raise ValueError(f"Error executing SQL script: {error.code} - {error.message}")
        
        self.con.commit()
        print("SQL script executed successfully.")


    def build_main_ui(self):
        self.root.geometry("1000x600")

        main_frame = ttk.Frame(self.root, padding=30)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame, padding=30)
        left_frame.pack(side="left", fill="y")

        ttk.Label(left_frame, text="MENU", font=("Arial", 16, "bold")).pack(pady=(0, 10))
        ttk.Button(left_frame, text="1. View Table Contents", command=self.view_table_contents).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="2. Search Workshops", command=self.search_workshops).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="3. Show Registered Students", command=self.show_registered_students).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="4. Register a New Student", command=self.register_new_student).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="5. Delete a Registration", command=self.delete_registration).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="6. Exit", command=self.quit).pack(fill="x", pady=5)

        right_frame = ttk.Frame(main_frame, padding=30)
        right_frame.pack(side="right", fill="both", expand=True)
        self.output_text = tk.Text(right_frame, wrap="none", font=("Courier New", 10), padx=20, pady=20)
        self.output_text.pack(fill="both", expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def run_query(self, query, params=None):

        try:
            with self.con.cursor() as cursor:
                cursor.execute(query, params or {})
                return cursor.fetchall()
        except oracledb.DatabaseError as e:
            messagebox.showerror("Database Error", f"An error occurred:\n{e}")
            return None
    def execute_command(self, query, params=None, commit=True):
        try:
            with self.con.cursor() as cursor:
                cursor.execute(query, params or {})
                if commit:
                    self.con.commit()
                return True
        except oracledb.DatabaseError as e:
            messagebox.showerror("Database Error", f"An error occurred:\n{e}")
            return False
        
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        
    def view_table_contents(self):

        choice = simpledialog.askstring(
                "View Table Contents\n",
                "------------------------------ TABLES ------------------------\n"
                "   1. Workshops\n"
                "   2. Registrations\n"
                "--------------------------------------------------------------\n\n"  
                "Enter the table name to view its content (1-2): ",
                parent = self.root

        )

        if choice is None:
            return
        
        choice = choice.strip()

        
        if choice not in ('1', '2'):
            messagebox.showerror("Input Error", "Invalid choice. Please select 1 or 2.")
            return
        
        self.clear_output()

        if choice == "1":
            rows = self.run_query("SELECT WorkshopID, Title, Category, TO_CHAR(EventDate, 'YYYY-MM-DD') AS EventDate, Location, Capacity FROM Workshops ORDER BY WorkshopId")

            if rows is None:
                return  
            
            if not rows:
                self.output_text.insert(tk.END, "No data found in Workshops table.\n")
            else:
                self.output_text.insert(tk.END, "\nWorkshops Table Contents: \n")
                self.output_text.insert(tk.END, f"{'Id':<5} {'Title':<30} {'Category':<10} {'Date':<12} {'Location':<30} {'Capacity':<4}\n")
                for id, title, category, date, location, capacity in rows:
                    self.output_text.insert(tk.END, f"{id:<5} {title[:28]:<30} {category:<10} {date:<12} {location[:28]:<30} {capacity:<4}\n")

        elif choice == '2':
                rows = self.run_query("SELECT WorkshopID, StudentID, TO_CHAR(RegisteredOn, 'YYYY-MM-DD') AS RegistrationDate FROM Registrations ORDER BY WorkshopID, StudentID")
                if rows is None:
                    return  
                if not rows:
                    self.output_text.insert(tk.END, "No data found in Registrations table.\n")
                else:
                    self.output_text.insert(tk.END, "\nRegistrations Table Contents: \n")
                    self.output_text.insert(tk.END, f"{'Id':<5} {'StudentId':<10} {'RegistrationDate':<15}\n")
                    for id, student_id, registration_date in rows:
                        self.output_text.insert(tk.END, f"{id:<5} {student_id:<10} {registration_date:<15}\n")

    def search_workshops(self):
        search = simpledialog.askstring(
            "Search Workshops\n",
            "Enter WorkshopId, Title, or Category to search: ",
            parent=self.root
        )

        if search is None:
            return
        
        search = search.strip()

        if not search:
            messagebox.showerror("Input Error", "Search term cannot be empty.")
            return
        
        try:
            workshop_id = int(search)
            rows = self.run_query("SELECT WorkshopID, Title, Category, TO_CHAR(EventDate, 'YYYY-MM-DD') AS EventDate, Location, Capacity FROM Workshops WHERE WorkshopID = :wid ORDER BY EventDate", {"wid": workshop_id})
        except ValueError:
            
            pattern = f"%{search.lower()}%"
            rows = self.run_query("SELECT WorkshopID, Title, Category, TO_CHAR(EventDate, 'YYYY-MM-DD') AS EventDate, Location, Capacity FROM Workshops WHERE LOWER(Title) LIKE :search OR LOWER(Category) LIKE :search ORDER BY EventDate", {"search": pattern})  

        if rows is None:
            return

        self.clear_output()

        if not rows:
            self.output_text.insert(tk.END, "No workshops found matching the criteria.\n")
        else:
            self.output_text.insert(tk.END, f"\n{'Id':<5} {'Title':<30} {'Category':<10} {'Date':<12} {'Location':<30} {'Capacity':<4}\n")
            for id, title, category, date, location, capacity in rows:
                self.output_text.insert(tk.END, f"{id:<5} {title[:28]:<30} {category:<10} {date:<12} {location[:28]:<30} {capacity:<4}\n")

    def show_registered_students(self):
        search = simpledialog.askstring(
        "Show Registered Students\n",
        "Enter WorkshopId or title to view registered students: ", 
        parent=self.root)

        if search is None:
            return
        search = search.strip()
        
        if not search:
            messagebox.showerror("Input Error", "Search term cannot be empty.")
            return

        try:
            workshop_id = int(search)
            workshops = self.run_query("""
                SELECT WorkshopID, Title, Capacity FROM Workshops WHERE WorkshopID = :wid
            """, {"wid": workshop_id})
        except ValueError:
            search = f"%{search.lower()}%"
            workshops = self.run_query("""
                SELECT WorkshopID, Title, Capacity FROM Workshops WHERE LOWER(Title) LIKE :search
            """, {"search": search})
        if workshops is None:
            return
        self.clear_output()
        
        if not workshops:
            messagebox.showinfo("No Results", "No workshops found matching the criteria.")
            return
        
        for workshop_id, title, capacity in workshops:
            students = self.run_query("""
                SELECT StudentID, TO_CHAR(RegisteredOn, 'YYYY-MM-DD') AS RegistrationDate FROM Registrations WHERE WorkshopID = :wid ORDER BY StudentID
            """, {"wid": workshop_id})

            if students is None:
                return
            
            available = capacity - len(students)
            self.output_text.insert(tk.END, f"\nWorkshop {workshop_id} - {title}\n")
            self.output_text.insert(tk.END, f"Available Seats: {available} / {capacity}\n")

            if not students:
                self.output_text.insert(tk.END, "No registered students found for this workshop.\n")
            else:
                self.output_text.insert(tk.END, f"\n{'StudentId':<12} {'RegistrationDate':<12}\n")
                for student_id, registration_date in students:
                    self.output_text.insert(tk.END, f"{student_id:<12} {registration_date:<12}\n")

    def register_new_student(self):
        workshop_id = simpledialog.askstring("Register New Student\n", "Enter WorkshopId to register: ", parent=self.root)
        if workshop_id is None or not workshop_id.strip():
            return

        student_id = simpledialog.askstring("Register New Student\n", "Enter StudentId to register: ", parent=self.root)
        if student_id is None or not student_id.strip():
            return
    
        try:
            workshop_id = int(workshop_id.strip())
        except ValueError:
            messagebox.showerror("Input Error", "Invalid WorkshopId. It must be a number.")
            return
        
        student_id = student_id.strip()



        row = self.run_query("SELECT Capacity FROM Workshops WHERE WorkshopID = :wid", {"wid": workshop_id})
        if row is None:
            return
        if not row:
            messagebox.showerror("Input Error", f"WorkshopId {workshop_id} does not exist.")
            return
        
        capacity = row[0][0]

        count_row = self.run_query("SELECT COUNT(*) FROM Registrations WHERE WorkshopID = :wid", {"wid": workshop_id})
        if count_row is None:
            return
        registration_count = count_row[0][0]
        if registration_count >= capacity:
            messagebox.showinfo("Registration Full", f"WorkshopId {workshop_id} is full. Cannot register more students.\n")
            return
        
        exists = self.run_query("SELECT 1 FROM Registrations WHERE WorkshopID = :wid AND StudentID = :sid", {"wid": workshop_id, "sid": student_id})
        if exists is None:
            return
        if exists:
            messagebox.showinfo("Already Registered", f"StudentId {student_id} is already registered for WorkshopId {workshop_id}.\n")
            return
        register = self.execute_command("INSERT INTO Registrations (WorkshopID, StudentID, RegisteredOn) VALUES (:wid, :sid, SYSDATE)", {"wid": workshop_id, "sid": student_id})

        if register:
            messagebox.showinfo("Registration Successful", f"StudentId {student_id} has been successfully registered for WorkshopId {workshop_id}.\n")

    def delete_registration(self):
        workshop_id = simpledialog.askstring("Delete Registration\n", "Enter WorkshopId to delete registration from: ", parent=self.root)
        if workshop_id is None or not workshop_id.strip():
            return
        
        student_id = simpledialog.askstring("Delete Registration\n", "Enter StudentId to delete registration for: ", parent=self.root)
        if student_id is None or not student_id.strip():
            return
        
        try:
            workshop_id = int(workshop_id.strip())
        except ValueError:
            messagebox.showerror("Input Error", "Invalid WorkshopId. It must be a number.")
            return
        
        student_id = student_id.strip()

        confirmation = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the registration of StudentId {student_id} for WorkshopId {workshop_id}?")
        if not confirmation:
            messagebox.showinfo("Deletion Cancelled", "Deletion cancelled.")
            return
        
        exists = self.run_query("SELECT 1 FROM Registrations WHERE WorkshopID = :wid AND StudentID = :sid", {"wid": workshop_id, "sid": student_id})
        if exists is None:
            return
        if not exists:
            messagebox.showinfo("No Registration Found", f"No registration found for StudentId {student_id} in WorkshopId {workshop_id}.\n")


        else:
            delete = self.execute_command("DELETE FROM Registrations WHERE WorkshopID = :wid AND StudentID = :sid", {"wid": workshop_id, "sid": student_id})
            if delete:
                messagebox.showinfo("Deletion Successful", f"Registration of StudentId {student_id} for WorkshopId {workshop_id} has been deleted successfully.\n")

    def quit(self):
        if self.con is not None:
            try:
                self.con.close()
            except Exception as e:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WorkshopApp(root)
    root.mainloop()