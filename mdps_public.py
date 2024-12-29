import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import re
import sqlite3

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )''')
    conn.commit()
    conn.close()

# Add a new user
def add_user(name, email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Authenticate user
def authenticate_user(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    return user is not None

# Initialize the database
init_db()

# Load saved models
diabetes_model = pickle.load(open('diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open('heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open('parkinsons_model.sav', 'rb'))

# Function to validate email format
def validate_email(email):
    email = email.strip().lower()
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) and email.endswith("@gmail.com")

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "name" not in st.session_state:
    st.session_state.name = None

# Sidebar for navigation
with st.sidebar:
    if not st.session_state.logged_in:
        selected = option_menu(
            "Predictive Disease Detection App",
            ["Login", "Signup"],
            icons=["key", "person-plus"],
            default_index=0,
        )
    else:
        selected = option_menu(
            "Predictive Disease Detection App",
            [
                "Home",
                "Diabetes Prediction",
                "Heart Disease Prediction",
                "Parkinson's Prediction",
                "Logout",
            ],
            icons=["house", "activity", "heart", "person", "box-arrow-right"],
            default_index=0,
        )

# Handle Logout separately
if selected == "Logout":
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.name = None
    st.success("You have been logged out.")
    st.stop()

# Signup Page
if selected == "Signup":
    st.title("Signup Page")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not validate_email(email):
            st.error("Please enter a valid Gmail address (e.g., example@gmail.com).")
        elif password != confirm_password:
            st.error("Passwords do not match. Please try again.")
        elif add_user(name, email, password):
            st.success(f"Account created successfully for {name}!")
            st.session_state.logged_in = True
            st.session_state.user = email
            st.session_state.name = name
        else:
            st.error("This email is already registered. Please login.")

# Login Page
elif selected == "Login":
    st.title("Login Page")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not validate_email(email):
            st.error("Please enter a valid Gmail address (e.g., example@gmail.com).")
        elif authenticate_user(email, password):
            st.session_state.logged_in = True
            st.session_state.user = email
            st.session_state.name = email.split("@")[0]
            st.success("Login successful!")
        else:
            st.error("Invalid email or password. Please try again.")

# Disease Prediction Pages (visible after successful login)
if st.session_state.logged_in:
    if selected == "Home":
        st.title("Welcome to the Predictive Disease Detection App")
        st.markdown(
            """
            This application predicts the likelihood of various diseases:
            - **Diabetes**
            - **Heart Disease**
            - **Parkinson's Disease**

            Use the sidebar to select a disease prediction option.
            """
        )

    elif selected == "Diabetes Prediction":
        st.title("Diabetes Prediction")

        Pregnancies = st.number_input("Number of Pregnancies", min_value=0)
        Glucose = st.number_input("Glucose Level", min_value=0)
        BloodPressure = st.number_input("Blood Pressure", min_value=0)
        SkinThickness = st.number_input("Skin Thickness", min_value=0)
        Insulin = st.number_input("Insulin Level", min_value=0)
        BMI = st.number_input("BMI", min_value=0.0, format="%.2f")
        DiabetesPedigreeFunction = st.number_input("Diabetes Pedigree Function", min_value=0.0, format="%.2f")
        Age = st.number_input("Age", min_value=0)

        if st.button("Predict Diabetes"):
            try:
                prediction = diabetes_model.predict(
                    [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]]
                )
                result = "Positive" if prediction[0] == 1 else "Negative"
                st.success(f"Prediction: {result}")
            except Exception as e:
                st.error(f"Error in prediction: {e}")

    elif selected == "Heart Disease Prediction":
        st.title("Heart Disease Prediction")

        age = st.number_input("Age")
        sex = st.selectbox("Sex", options=["Female", "Male"])
        cp = st.number_input("Chest Pain Type", min_value=0, max_value=3)
        trestbps = st.number_input("Resting Blood Pressure")
        chol = st.number_input("Serum Cholesterol")
        fbs = st.number_input("Fasting Blood Sugar > 120 mg/dl", min_value=0, max_value=1)
        restecg = st.number_input("Resting ECG Results", min_value=0, max_value=2)
        thalach = st.number_input("Max Heart Rate Achieved")
        exang = st.number_input("Exercise Induced Angina", min_value=0, max_value=1)
        oldpeak = st.number_input("ST Depression")
        slope = st.number_input("Slope of Peak Exercise ST Segment", min_value=0, max_value=2)
        ca = st.number_input("Number of Major Vessels", min_value=0, max_value=3)
        thal = st.number_input("Thalassemia", min_value=0, max_value=2)

        if st.button("Predict Heart Disease"):
            try:
                inputs = [
                    age, int(sex == "Male"), cp, trestbps, chol, fbs, restecg, thalach,
                    exang, oldpeak, slope, ca, thal
                ]
                prediction = heart_disease_model.predict([inputs])
                result = "Positive" if prediction[0] == 1 else "Negative"
                st.success(f"Prediction: {result}")
            except Exception as e:
                st.error(f"Error in prediction: {e}")

    elif selected == "Parkinson's Prediction":
        st.title("Parkinson's Prediction")

        fo = st.number_input("MDVP:Fo(Hz)")
        fhi = st.number_input("MDVP:Fhi(Hz)")
        flo = st.number_input("MDVP:Flo(Hz)")
        Jitter_percent = st.number_input("MDVP:Jitter(%)")
        Jitter_Abs = st.number_input("MDVP:Jitter(Abs)")
        RAP = st.number_input("MDVP:RAP")
        PPQ = st.number_input("MDVP:PPQ")
        DDP = st.number_input("Jitter:DDP")
        Shimmer = st.number_input("MDVP:Shimmer")
        Shimmer_dB = st.number_input("MDVP:Shimmer(dB)")
        NHR = st.number_input("NHR")
        HNR = st.number_input("HNR")
        RPDE = st.number_input("RPDE")
        DFA = st.number_input("DFA")
        spread1 = st.number_input("Spread1")
        spread2 = st.number_input("Spread2")
        D2 = st.number_input("D2")
        PPE = st.number_input("PPE")

        if st.button("Predict Parkinson's"):
            try:
                inputs = [
                    fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP, Shimmer,
                    Shimmer_dB, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE
                ]
                prediction = parkinsons_model.predict([inputs])
                result = "Positive" if prediction[0] == 1 else "Negative"
                st.success(f"Prediction: {result}")
            except Exception as e:
                st.error(f"Error in prediction: {e}")
