import streamlit as st
from datetime import date
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# -------------------- DATABASE SETUP --------------------
engine = create_engine('sqlite:///agrirent.db', echo=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hashed
    email = Column(String)
    role = Column(String)  # 'owner' or 'renter'
    location = Column(String)

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    category = Column(String)
    description = Column(String)
    daily_rate = Column(Float)
    location = Column(String)
    available_from = Column(Date)
    available_to = Column(Date)
    image_url = Column(String)

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    renter_id = Column(Integer, ForeignKey('users.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    total_cost = Column(Float)
    status = Column(String)  # 'pending', 'confirmed', 'cancelled'

# Create tables if they don't exist
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# -------------------- UTILITY FUNCTIONS --------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login_user(username, password):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    if user and check_password(password, user.password):
        st.session_state["user"] = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "location": user.location
        }
        return True
    return False

def logout():
    st.session_state["user"] = None
    st.rerun()

# -------------------- STREAMLIT APP --------------------
st.set_page_config(page_title="Agri Equipment Rental", layout="wide")

# Initialize session state
if "user" not in st.session_state:
    st.session_state["user"] = None

# Sidebar menu
menu = ["Home", "Login", "Register", "List Equipment", "Search Equipment", "Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# Logout button if user is logged in
if st.session_state["user"]:
    if st.sidebar.button("Logout"):
        logout()

# Create a new database session for each interaction
db_session = Session()

# ---------------- HOME ----------------
if choice == "Home":
    st.title("🌾 Smart Agri Equipment Rental Platform")
    st.write("Rent tractors, harvesters and farming equipment easily.")
    st.image("https://images.unsplash.com/photo-1598046889427-3f7e9b9f5b4a?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", use_column_width=True)

# ---------------- LOGIN ----------------
elif choice == "Login":
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- REGISTER ----------------
elif choice == "Register":
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["owner", "renter"])
    location = st.text_input("Location")
    if st.button("Register"):
        existing = db_session.query(User).filter_by(username=username).first()
        if existing:
            st.error("Username already exists")
        else:
            new_user = User(
                username=username,
                password=hash_password(password),
                email=email,
                role=role,
                location=location
            )
            db_session.add(new_user)
            db_session.commit()
            st.success("Registration Successful")

# ---------------- LIST EQUIPMENT (OWNER ONLY) ----------------
elif choice == "List Equipment":
    if st.session_state["user"] and st.session_state["user"]["role"] == "owner":
        st.title("Add Equipment")
        name = st.text_input("Equipment Name")
        category = st.selectbox("Category", ["Tractor", "Harvester", "Seeder", "Sprayer"])
        description = st.text_area("Description")
        daily_rate = st.number_input("Daily Rate ($)", min_value=0.0, step=0.01)
        location = st.text_input("Location", value=st.session_state["user"]["location"])
        available_from = st.date_input("Available From", value=date.today())
        available_to = st.date_input("Available To", value=date.today())
        image_url = st.text_input("Image URL (optional)")
        if st.button("Add Equipment"):
            equipment = Equipment(
                owner_id=st.session_state["user"]["id"],
                name=name,
                category=category,
                description=description,
                daily_rate=daily_rate,
                location=location,
                available_from=available_from,
                available_to=available_to,
                image_url=image_url
            )
            db_session.add(equipment)
            db_session.commit()
            st.success("Equipment Added")
    else:
        st.warning("Please login as an owner to list equipment.")

# ---------------- SEARCH EQUIPMENT (RENTER ONLY) ----------------
elif choice == "Search Equipment":
    if st.session_state["user"] and st.session_state["user"]["role"] == "renter":
        st.title("Search Equipment")
        category_filter = st.selectbox("Category", ["All", "Tractor", "Harvester", "Seeder", "Sprayer"])
        location_filter = st.text_input("Location (optional)")
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())

        if st.button("Search"):
            # Build base query
            query = db_session.query(Equipment)
            if category_filter != "All":
                query = query.filter(Equipment.category == category_filter)
            if location_filter:
                query = query.filter(Equipment.location.contains(location_filter))

            # Check equipment availability period
            query = query.filter(
                Equipment.available_from <= start_date,
                Equipment.available_to >= end_date
            )

            results = query.all()
            if not results:
                st.info("No equipment matches your criteria.")
            else:
                for eq in results:
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if eq.image_url:
                                st.image(eq.image_url, width=150)
                            else:
                                st.image("https://via.placeholder.com/150", width=150)
                        with col2:
                            st.subheader(eq.name)
                            st.write(f"**Category:** {eq.category}")
                            st.write(f"**Rate:** ${eq.daily_rate}/day")
                            st.write(f"**Location:** {eq.location}")
                            st.write(f"**Available:** {eq.available_from} to {eq.available_to}")
                            days = (end_date - start_date).days
                            if days <= 0:
                                st.error("End date must be after start date.")
                            else:
                                total = days * eq.daily_rate
                                st.write(f"**Total for {days} days:** ${total:.2f}")

                                # Check if already booked during these dates
                                overlapping = db_session.query(Booking).filter(
                                    Booking.equipment_id == eq.id,
                                    Booking.start_date <= end_date,
                                    Booking.end_date >= start_date,
                                    Booking.status.in_(["pending", "confirmed"])
                                ).first()
                                if overlapping:
                                    st.warning("This equipment is already booked for the selected dates.")
                                else:
                                    if st.button(f"Book Now", key=eq.id):
                                        booking = Booking(
                                            equipment_id=eq.id,
                                            renter_id=st.session_state["user"]["id"],
                                            start_date=start_date,
                                            end_date=end_date,
                                            total_cost=total,
                                            status="pending"
                                        )
                                        db_session.add(booking)
                                        db_session.commit()
                                        st.success("Booking request sent! Check your dashboard for updates.")
                                        st.rerun()
                        st.divider()
    else:
        st.warning("Please login as a renter to search equipment.")

# ---------------- DASHBOARD ----------------
elif choice == "Dashboard":
    if st.session_state["user"]:
        user = st.session_state["user"]
        if user["role"] == "owner":
            st.title("Owner Dashboard")
            # Show owner's equipment
            equipments = db_session.query(Equipment).filter_by(owner_id=user["id"]).all()
            if equipments:
                for eq in equipments:
                    with st.expander(f"{eq.name} (${eq.daily_rate}/day)"):
                        st.write(f"**Category:** {eq.category}")
                        st.write(f"**Description:** {eq.description}")
                        st.write(f"**Location:** {eq.location}")
                        st.write(f"**Available:** {eq.available_from} to {eq.available_to}")

                        # Show bookings for this equipment
                        bookings = db_session.query(Booking).filter_by(equipment_id=eq.id).all()
                        if bookings:
                            st.write("**Bookings:**")
                            for b in bookings:
                                renter = db_session.query(User).get(b.renter_id)
                                col1, col2, col3 = st.columns([2,1,1])
                                with col1:
                                    st.write(f"{renter.username}: {b.start_date} to {b.end_date}")
                                with col2:
                                    st.write(f"Total: ${b.total_cost}")
                                with col3:
                                    if b.status == "pending":
                                        if st.button(f"Confirm", key=f"conf_{b.id}"):
                                            b.status = "confirmed"
                                            db_session.commit()
                                            st.rerun()
                                    else:
                                        st.write(f"Status: **{b.status}**")
                        else:
                            st.write("No bookings yet.")
            else:
                st.info("You haven't listed any equipment yet.")
        else:  # renter
            st.title("My Bookings")
            bookings = db_session.query(Booking).filter_by(renter_id=user["id"]).all()
            if bookings:
                for b in bookings:
                    eq = db_session.query(Equipment).get(b.equipment_id)
                    owner = db_session.query(User).get(eq.owner_id)
                    with st.container():
                        st.write(f"**{eq.name}** from {owner.username}")
                        st.write(f"Dates: {b.start_date} to {b.end_date}")
                        st.write(f"Total Cost: ${b.total_cost}")
                        st.write(f"Status: **{b.status}**")
                        st.divider()
            else:
                st.info("You have no bookings yet.")
    else:
        st.warning("Please login first.")

# Close the database session at the end of the script
db_session.close()
