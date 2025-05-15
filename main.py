import streamlit as st
from models.user import User
from models.task import Task
from models.bid import Bid
from utils.auth import login, signup
import json
import os

# Simulated DB paths
USER_DB = "data/users.json"
TASK_DB = "data/tasks.json"
BID_DB = "data/bids.json"

# Load or initialize DB
def load_db(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        with open(path, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Corrupted or malformed JSON, reset file
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_db(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ----- 💅 Custom Styling -----
st.set_page_config(page_title="TaskBid", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        /* Base app background and font */
        .appview-container .main, .block-container {
            background-color: #000000 !important;
            color: #f0f0f5 !important;
            font-family: 'Poppins', sans-serif !important;
            padding: 2rem 3rem !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #1a001a !important;
            color: #ddd !important;
            padding: 1rem 1.5rem !important;
            font-weight: 500;
            letter-spacing: 0.04em;
        }

        /* Sidebar Menu */
        .css-1d391kg .css-1v0mbdj {
            background-color: transparent !important;
            color: #d1c4e9 !important;
            font-weight: 600;
            font-size: 1.1rem;
        }
        .css-1d391kg .css-1v0mbdj:focus, 
        .css-1d391kg .css-1v0mbdj:hover {
            background-color: #4B0082 !important;
            color: white !important;
            border-radius: 8px;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #4B0082, #A64AC9);
            color: white !important;
            font-weight: 700;
            border-radius: 10px;
            padding: 0.7rem 1.5rem;
            border: none;
            transition: background 0.3s ease;
            box-shadow: 0 4px 10px rgba(166, 74, 201, 0.6);
            cursor: pointer;
            font-size: 1rem;
        }
        .stButton > button:hover {
            background: linear-gradient(90deg, #6a2ea9, #c083ff);
            box-shadow: 0 6px 14px rgba(198, 109, 230, 0.9);
        }

        /* Inputs */
        .stTextInput > div > div > input,
        .stTextArea textarea {
            background-color: #1f1f2e !important;
            color: #ddd !important;
            border-radius: 12px !important;
            border: 1.5px solid #4B0082 !important;
            padding: 0.8rem 1rem !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            transition: border-color 0.3s ease;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {
            border-color: #a64ac9 !important;
            outline: none !important;
        }

        /* Task card styling */
        .task-card {
            background: linear-gradient(145deg, #1a001a, #2c0031);
            padding: 1.6rem 2rem;
            margin-bottom: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(166, 74, 201, 0.4);
            border: 1px solid #4B0082;
            transition: transform 0.3s ease;
        }
        .task-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 28px rgba(198, 109, 230, 0.8);
        }
        .task-card h4 {
            font-weight: 700;
            color: #d1c4e9;
            margin-bottom: 0.5rem;
        }
        .task-card p {
            font-weight: 400;
            font-size: 1rem;
            margin-bottom: 0.6rem;
            color: #ccc;
        }
        .task-card small {
            font-weight: 600;
            color: #a584cc;
        }

        /* Bid info box */
        .stInfo {
            background-color: #3b0066 !important;
            border-left: 5px solid #a64ac9 !important;
            color: #f4e6ff !important;
            font-weight: 600 !important;
            padding: 0.8rem 1.2rem !important;
            border-radius: 8px !important;
            margin-bottom: 0.8rem !important;
        }

        /* Expander style */
        .stExpander > button {
            background-color: #4B0082 !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 0.8rem 1rem !important;
            width: 100% !important;
            text-align: left !important;
            font-size: 1.1rem !important;
            margin-bottom: 0.6rem !important;
            box-shadow: 0 6px 18px rgba(166, 74, 201, 0.5);
            transition: background-color 0.3s ease;
        }
        .stExpander > button:hover {
            background-color: #7a4bcc !important;
        }

        /* Links and highlights */
        a, a:hover {
            color: #b39ddb;
            text-decoration: none;
            font-weight: 600;
        }

        /* Headers */
        h1, h2, h3, h4 {
            color: #d1c4e9;
            font-weight: 700;
        }
        h3 {
            border-bottom: 2px solid #a64ac9;
            padding-bottom: 0.3rem;
            margin-bottom: 1.2rem;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #1a001a;
        }
        ::-webkit-scrollbar-thumb {
            background: #4B0082;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #a64ac9;
        }
    </style>
""", unsafe_allow_html=True)

# ----- 🚀 App UI -----
st.image("static/logo.png", width=150)
st.title("🚀 Welcome to TaskBid — Micro Task Platform")

if "user" not in st.session_state:
    st.session_state.user = None

menu = ["Login", "Signup"] if not st.session_state.user else ["Dashboard", "Logout"]
choice = st.sidebar.selectbox("📋 Menu", menu)

if choice == "Login":
    login(USER_DB)

elif choice == "Signup":
    signup(USER_DB)

elif choice == "Logout":
    st.session_state.user = None
    st.success("🔒 Logged out successfully.")

elif choice == "Dashboard":
    user = st.session_state.user
    st.subheader(f"👤 Welcome, **{user['username']}** ({user['role'].capitalize()})")

    tasks = load_db(TASK_DB)
    bids = load_db(BID_DB)

    if user['role'] == 'buyer':
        st.markdown("### 📌 Your Posted Tasks")
        user_tasks = [t for t in tasks if t['buyer'] == user['username']]
        for t in user_tasks:
            st.markdown(f"""<div class='task-card'>
                <h4>{t['title']} — ${t['price']}</h4>
                <p>{t['description']}</p>
                <small>Status: <b>{t['status'].capitalize()}</b></small><br>""", unsafe_allow_html=True)
            
            if t['status'] == 'open':
                task_bids = [b for b in bids if b['task'] == t['title']]
                for b in task_bids:
                    st.info(f"📬 Bid from **{b['seller']}**:\n> {b['message']}")
                    if st.button(f"✅ Accept Bid from {b['seller']}", key=f"{t['title']}_{b['seller']}"):
                        t['status'] = 'assigned'
                        save_db(TASK_DB, tasks)
                        st.success("🎉 Bid Accepted!")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### ➕ Post a New Task")
        title = st.text_input("📝 Task Title")
        desc = st.text_area("🧾 Description")
        if st.button("📤 Post Task"):
            new_task = Task(title, desc, user['username'])
            tasks.append(new_task.to_dict())
            save_db(TASK_DB, tasks)
            st.success("✅ Task Posted!")

    elif user['role'] == 'seller':
        st.markdown("### 🔍 Open Tasks")
        open_tasks = [t for t in tasks if t['status'] == 'open']
        for t in open_tasks:
            with st.expander(f"💼 {t['title']} — ${t['price']}"):
                st.markdown(f"🧾 {t['description']}")
                msg = st.text_input(f"✏️ Bid Message for '{t['title']}'", key=t['title'])
                if st.button("📨 Submit Bid", key=f"{t['title']}_bid"):
                    new_bid = Bid(t['title'], user['username'], msg)
                    bids.append(new_bid.to_dict())
                    save_db(BID_DB, bids)
                    st.success("🚀 Bid Submitted!")

        st.markdown("### 📁 Your Bids")
        my_bids = [b for b in bids if b['seller'] == user['username']]
        for b in my_bids:
            st.markdown(f"- **Task:** {b['task']} | 💬 **Message:** {b['message']}")

