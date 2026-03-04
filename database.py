import sqlite3

def init_db():
    conn = sqlite3.connect('institution.db')
    c = conn.cursor()
    
    # Table for institutions
    c.execute('''CREATE TABLE IF NOT EXISTS institutions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  address TEXT,
                  courses TEXT,
                  contact TEXT)''')
    
    # Table for student registrations
    c.execute('''CREATE TABLE IF NOT EXISTS registrations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  institution_id INTEGER,
                  registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (institution_id) REFERENCES institutions(id))''')
    
    # Insert some sample institutions if table is empty
    c.execute("SELECT COUNT(*) FROM institutions")
    if c.fetchone()[0] == 0:
        sample_data = [
            ("ABC University", "123 Main St, City", "Computer Science, Mathematics", "info@abc.edu"),
            ("XYZ College", "456 Oak Ave, Town", "Business, Arts", "admissions@xyz.edu"),
        ]
        c.executemany("INSERT INTO institutions (name, address, courses, contact) VALUES (?,?,?,?)", sample_data)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
