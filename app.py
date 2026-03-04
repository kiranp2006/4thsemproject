import streamlit as st
import sqlite3
import pandas as pd

# Initialize database
def init_db():
    conn = sqlite3.connect('institution.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS institutions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  address TEXT,
                  courses TEXT,
                  contact TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS registrations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  institution_id INTEGER,
                  registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (institution_id) REFERENCES institutions(id))''')
    conn.commit()
    conn.close()

init_db()

# Helper functions
def get_institutions():
    conn = sqlite3.connect('institution.db')
    df = pd.read_sql_query("SELECT * FROM institutions", conn)
    conn.close()
    return df

def register_student(name, email, inst_id):
    conn = sqlite3.connect('institution.db')
    c = conn.cursor()
    c.execute("INSERT INTO registrations (student_name, email, institution_id) VALUES (?,?,?)",
              (name, email, inst_id))
    conn.commit()
    conn.close()

# Streamlit UI
st.set_page_config(page_title="Student Registration Portal", layout="wide")
st.title("🎓 Student Registration & Institution Info")

menu = ["Home", "View Institutions", "Register", "Admin (Add Institution)"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Welcome")
    st.write("Use this portal to register at your preferred institution and view details about schools/colleges.")

elif choice == "View Institutions":
    st.subheader("Institution Directory")
    df = get_institutions()
    if not df.empty:
        for _, row in df.iterrows():
            with st.expander(f"{row['name']}"):
                st.write(f"**Address:** {row['address']}")
                st.write(f"**Courses Offered:** {row['courses']}")
                st.write(f"**Contact:** {row['contact']}")
    else:
        st.info("No institutions added yet.")

elif choice == "Register":
    st.subheader("Student Registration")
    df = get_institutions()
    if df.empty:
        st.warning("No institutions available. Please contact admin.")
    else:
        with st.form("registration_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            inst_name = st.selectbox("Select Institution", df['name'].tolist())
            submitted = st.form_submit_button("Register")
            if submitted:
                if name and email:
                    inst_id = df[df['name'] == inst_name]['id'].values[0]
                    register_student(name, email, inst_id)
                    st.success(f"Registration successful for {name} at {inst_name}!")
                else:
                    st.error("Please fill all fields.")

elif choice == "Admin (Add Institution)":
    st.subheader("Add New Institution")
    with st.form("add_institution"):
        name = st.text_input("Institution Name")
        address = st.text_area("Address")
        courses = st.text_input("Courses Offered (comma separated)")
        contact = st.text_input("Contact Email/Phone")
        submitted = st.form_submit_button("Add Institution")
        if submitted:
            if name:
                conn = sqlite3.connect('institution.db')
                c = conn.cursor()
                c.execute("INSERT INTO institutions (name, address, courses, contact) VALUES (?,?,?,?)",
                          (name, address, courses, contact))
                conn.commit()
                conn.close()
                st.success(f"Institution '{name}' added!")
            else:
                st.error("Institution name is required.")
