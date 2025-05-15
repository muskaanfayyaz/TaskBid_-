import streamlit as st
import json

def login(user_db_path):
    users = json.load(open(user_db_path))
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        for u in users:
            if u['username'] == username and u['password'] == password:
                st.session_state.user = u
                st.success("Logged in successfully!")
                return
        st.error("Invalid credentials")

def signup(user_db_path):
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["buyer", "seller"])
    if st.button("Signup"):
        users = json.load(open(user_db_path))
        if any(u['username'] == username for u in users):
            st.error("Username already exists")
        else:
            user = {"username": username, "email": email, "role": role, "password": password}
            users.append(user)
            json.dump(users, open(user_db_path, 'w'), indent=2)
            st.success("Account created successfully! You can now log in.")
