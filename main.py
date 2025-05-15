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
st.set_page_config(page_title="TaskBid", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Montserrat:wght@400;500;600&display=swap');

        html, body, [class*="css"]  {
            background-color: #1c1c1e;
            color: #ffffff;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        .stButton>button {
            background: linear-gradient(90deg, #4B0082, #A64AC9);
            color: white;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1.2rem;
            border-radius: 8px;
        }

        .stTextInput>div>div>input,
        .stTextArea textarea {
            background-color: #2c2c2e;
            color: white;
            border-radius: 8px;
        }

        .task-card {
            background-color: #2c2c2e;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(166, 74, 201, 0.2);
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

