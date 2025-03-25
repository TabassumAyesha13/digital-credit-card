import streamlit as st
import random
import sqlite3
import hashlib
import os
import matplotlib.pyplot as plt

# ------------------------------
# DATABASE SETUP
# ------------------------------
conn = sqlite3.connect('farmer_data.db', check_same_thread=False)
c = conn.cursor()

# Create user profiles table
c.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
    aadhaar TEXT PRIMARY KEY,
    name TEXT,
    phone TEXT
)''')

# Create user credentials table
c.execute('''CREATE TABLE IF NOT EXISTS user_credentials (
    aadhaar TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
)''')

# Create loan history table
c.execute('''CREATE TABLE IF NOT EXISTS loan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aadhaar TEXT,
    name TEXT,
    amount REAL,
    status TEXT
)''')

# Create credit cards table
c.execute('''CREATE TABLE IF NOT EXISTS credit_cards (
    aadhaar TEXT,
    card_number TEXT,
    limit_amount REAL,
    activation_code TEXT,
    status TEXT
)''')

conn.commit()

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(aadhaar, name, phone, username, password):
    """Registers a new user, including username and password."""
    password_hash = hash_password(password)
    c.execute("INSERT INTO user_profiles VALUES (?, ?, ?)", (aadhaar, name, phone))
    c.execute("INSERT INTO user_credentials VALUES (?, ?, ?)", (aadhaar, username, password_hash))
    conn.commit()

def user_exists(aadhaar):
    """Checks if a user with the given Aadhaar number already exists."""
    c.execute("SELECT * FROM user_profiles WHERE aadhaar = ?", (aadhaar,))
    return c.fetchone() is not None

def username_exists(username):
    """Checks if a username already exists."""
    c.execute("SELECT * FROM user_credentials WHERE username = ?", (username,))
    return c.fetchone() is not None

def verify_login(username, password):
    """Verifies the username and password against the database."""
    c.execute("SELECT password_hash, aadhaar FROM user_credentials WHERE username = ?", (username,))
    result = c.fetchone()
    if result:
        password_hash, aadhaar = result
        if hash_password(password) == password_hash:
            return aadhaar  # Return the Aadhaar number upon successful login
    return None  # Return None if login fails

def get_user(aadhaar):
    c.execute("SELECT * FROM user_profiles WHERE aadhaar = ?", (aadhaar,))
    return c.fetchone()

def add_loan(aadhaar, name, amount):
    c.execute("INSERT INTO loan_history (aadhaar, name, amount, status) VALUES (?, ?, ?, ?)", (aadhaar, name, amount, 'Pending'))
    conn.commit()

def get_loans(aadhaar):
    c.execute("SELECT * FROM loan_history WHERE aadhaar = ?", (aadhaar,))
    return c.fetchall()

def issue_credit_card(aadhaar, limit_amount):
    card_number = f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    activation_code = str(random.randint(1000, 9999))
    c.execute("INSERT INTO credit_cards (aadhaar, card_number, limit_amount, activation_code, status) VALUES (?, ?, ?, ?, ?)",
              (aadhaar, card_number, limit_amount, activation_code, 'Inactive'))
    conn.commit()
    return card_number, activation_code

def activate_card(aadhaar, code):
    c.execute("SELECT activation_code FROM credit_cards WHERE aadhaar = ?", (aadhaar,))
    result = c.fetchone()
    if result and result[0] == code:
        c.execute("UPDATE credit_cards SET status = 'Active' WHERE aadhaar = ?", (aadhaar,))
        conn.commit()
        return True
    return False

# ------------------------------
# STREAMLIT UI SETUP
# ------------------------------
st.set_page_config(page_title="Tenant Farmer Loan Management System", layout="wide")

# ------------------------------
# SIDEBAR MENU
# ------------------------------
# Sidebar Logo or Image (Top Right Full Width)
sidebar_img_path = r"C:\Users\vidya\Downloads\WhatsApp Image 2025-03-25 at 9.52.01 AM.jpeg"  # Update with your image path

if os.path.exists(sidebar_img_path):
    st.sidebar.image(sidebar_img_path, use_container_width=True)
else:
    st.sidebar.error("❗ Sidebar image not found! Check the path.")

st.sidebar.title("🌱 HarvestPay - Tenant Farmer Loan System")
menu = st.sidebar.radio("Choose a feature:", [
    "Home", "Features", "User Registration", "Loan Application", "Risk Assessment",
    "Credit Card Issuance", "Activation", "User Profile Management",
    "Loan History", "Feedback System"
])

# ------------------------------
# DEFAULT IMAGE ON INITIAL LOAD (FULL WIDTH)
# ------------------------------
if "home_displayed" not in st.session_state:
    st.session_state.home_displayed = False

if menu == "Home":
    if not st.session_state.home_displayed:
        # Main Image on Top on Initial Load
        home_img_path = r"C:\Users\vidya\Downloads\WhatsApp Image 2025-03-25 at 9.52.01 AM (2).jpeg"

        if os.path.exists(home_img_path):
            st.image(home_img_path, use_container_width=True)
        else:
            st.error("❗ Home page image not found! Check the path.")

        st.session_state.home_displayed = True
    else:
        # ------------------------------
        # HOME PAGE CONTENT
        # ------------------------------
        st.title("🏡 Welcome to the Tenant Farmer Loan Management System")
        st.write("### Features available:")
        st.markdown(
            """
            - ✅ User Registration
            - 💸 Loan Application
            - 🤖 Risk Assessment
            - 💳 Credit Card Issuance
            - 🔐 Card Activation
            - 👤 User Profile Management
            - 📚 Loan History
            - 📝 Feedback System
            """
        )

# ------------------------------
# FEATURES PAGE WITH ICON NAVIGATION
# ------------------------------
elif menu == "Features":
    st.title("✨ System Features Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 👤 User Registration")
        st.write("Register new users with Aadhaar, name, and phone number.")

        st.markdown("#### 💸 Loan Application")
        st.write("Apply for loans by specifying the amount and details.")

        st.markdown("#### 🤖 Risk Assessment")
        st.write("AI-based risk analysis for loan approval.")

    with col2:
        st.markdown("#### 💳 Credit Card Issuance")
        st.write("Issue credit cards with set limits for users.")

        st.markdown("#### 🔐 Card Activation")
        st.write("Activate issued cards with one-time code.")

        st.markdown("#### 👤 User Profile Management")
        st.write("Manage and view user details.")

    with col3:
        st.markdown("#### 📚 Loan History")
        st.write("Track and manage previous loan applications.")

        st.markdown("#### 📝 Feedback System")
        st.write("Allow users to submit feedback on services.")

        st.markdown("#### 📊 Dashboard & Reporting")
        st.write("View statistics and loan summary reports.")

# ------------------------------
# USER REGISTRATION
# ------------------------------
elif menu == "User Registration":
    st.title("👤 User Registration")

    # Registration/Login Selection
    reg_login_option = st.radio(
        "Choose:",
        ("Register", "Login"),
        horizontal=True
    )

    if reg_login_option == "Register":
        # Registration Form
        st.subheader("Register")
        aadhaar = st.text_input("Enter Aadhaar Number (12 digits):")
        name = st.text_input("Enter Full Name:")
        phone = st.text_input("Enter Phone Number:")
        username = st.text_input("Enter Username:")
        password = st.text_input("Enter Password:", type="password")

        if st.button("Register"):
            if len(aadhaar) == 12 and aadhaar.isdigit():
                if not user_exists(aadhaar):
                    if not username_exists(username):
                        register_user(aadhaar, name, phone, username, password)
                        st.success("✅ User registered successfully! Please log in.")
                    else:
                        st.error("⚠️ Username already exists. Please choose a different username.")
                else:
                    st.error("⚠️ User with this Aadhaar already exists.")
            else:
                st.error("❗ Invalid Aadhaar Number. Please enter a valid 12-digit number.")

    elif reg_login_option == "Login":
        # Login Form
        st.subheader("Login")
        login_username = st.text_input("Username:")
        login_password = st.text_input("Password:", type="password")

        if st.button("Login"):
            aadhaar = verify_login(login_username, login_password)
            if aadhaar:
                st.session_state['login_status'] = True
                st.session_state['aadhaar'] = aadhaar
                st.success("✅ Logged in successfully!")
            else:
                st.error("⚠️ Invalid username or password.")

# ------------------------------
# LOAN APPLICATION
# ------------------------------
elif menu == "Loan Application":
    st.title("💸 Loan Application")
    if 'aadhaar' in st.session_state and st.session_state['login_status']:
        aadhaar = st.session_state['aadhaar']
        name = st.text_input("Enter Your Name:")
        income = st.number_input("Enter Annual Income (₹):", min_value=0.0)
        loan_amount = st.number_input("Enter Loan Amount (₹):", min_value=0.0)

        if st.button("Submit Loan Application"):
            add_loan(aadhaar, name, loan_amount)
            st.success("✅ Loan application submitted successfully! Loan is being reviewed.")
    else:
        st.error("⚠️ Please log in to apply for a loan.")

# ------------------------------
# RISK ASSESSMENT
# ------------------------------
elif menu == "Risk Assessment":
    st.title("🤖 Risk Assessment")
    aadhaar = st.text_input("Enter Aadhaar Number for Risk Check:")
    c.execute("SELECT * FROM loan_history WHERE aadhaar = ?", (aadhaar,))
    loans = c.fetchall()

    if loans:
        total_loans = len(loans)
        total_amount = sum([loan[3] for loan in loans])

        st.write(f"📊 Loan Applications: {total_loans}")
        st.write(f"💰 Total Loan Amount: ₹{total_amount}")

        # Random risk score
        risk_score = random.randint(1, 100)
        st.write(f"⚖️ Risk Score: {risk_score}/100")

        if risk_score < 40:
            st.success("✅ Low Risk - Loan likely to be approved.")
        elif 40 <= risk_score < 70:
            st.warning("⚠️ Medium Risk - Review required.")
        else:
            st.error("❗ High Risk - Loan likely to be rejected.")
    else:
        st.error("❌ No loan history found for this Aadhaar.")

# ------------------------------
# CREDIT CARD ISSUANCE
# ------------------------------
elif menu == "Credit Card Issuance":
    st.title("💳 Credit Card Issuance")
    aadhaar = st.text_input("Enter Aadhaar Number:")
    c.execute("SELECT * FROM user_profiles WHERE aadhaar = ?", (aadhaar,))
    if c.fetchone():
        limit_amount = st.number_input("Enter Credit Limit (₹):", min_value=0.0)
        card_number = f"4214{random.randint(1000000000, 9999999999)}"
        activation_code = str(random.randint(1000, 9999))

        if st.button("Issue Credit Card"):
            c.execute("INSERT INTO credit_cards VALUES (?, ?, ?, ?, ?)", (aadhaar, card_number, limit_amount, activation_code, "Inactive"))
            conn.commit()
            st.success(f"✅ Credit Card Issued!\n\n💳 Card Number: {card_number}\n🔐 Activation Code: {activation_code}")
    else:
        st.error("⚠️ Aadhaar Number not found. Please register first.")

# ------------------------------
# CARD ACTIVATION
# ------------------------------
elif menu == "Activation":
    st.title("🔐 Card Activation")
    aadhaar = st.text_input("Enter Aadhaar Number:")
    activation_code = st.text_input("Enter Activation Code:")

    c.execute("SELECT * FROM credit_cards WHERE aadhaar = ? AND activation_code = ?", (aadhaar, activation_code))
    card = c.fetchone()

    if card:
        c.execute("UPDATE credit_cards SET status = 'Active' WHERE aadhaar = ?", (aadhaar,))
        conn.commit()
        st.success("✅ Card activated successfully!")
    elif st.button("Activate"):
        st.error("❗ Invalid Aadhaar or Activation Code.")

# ------------------------------
# USER PROFILE MANAGEMENT
# ------------------------------
elif menu == "User Profile Management":
    st.title("👤 User Profile Management")
    aadhaar = st.text_input("Enter Aadhaar Number:")
    c.execute("SELECT * FROM user_profiles WHERE aadhaar = ?", (aadhaar,))
    profile = c.fetchone()

    if profile:
        st.write(f"📛 Name: {profile[1]}")
        st.write(f"📞 Phone: {profile[2]}")
    else:
        st.error("❌ Profile not found.")

# ------------------------------
# LOAN HISTORY
# ------------------------------
elif menu == "Loan History":
    st.title("📚 Loan History")
    aadhaar = st.text_input("Enter Aadhaar Number:")
    c.execute("SELECT * FROM loan_history WHERE aadhaar = ?", (aadhaar,))
    loans = c.fetchall()

    if loans:
        for loan in loans:
            st.write(f"💰 Amount: ₹{loan[3]} | Status: {loan[4]}")
    else:
        st.error("❌ No loan history found.")

# ------------------------------
# FEEDBACK SYSTEM
# ------------------------------
elif menu == "Feedback System":
    st.title("📝 Feedback System")
    feedback = st.text_area("Enter your feedback or suggestions:")
    if st.button("Submit Feedback"):
        st.success("✅ Thank you for your feedback!")

# Close the connection when the app is closed
conn.close()
