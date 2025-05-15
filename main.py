import streamlit as st
from models.user import User
from models.task import Task
from models.bid import Bid
from utils.auth import login, signup
import json, os

# Simulated DB paths
USER_DB = "data/users.json"
TASK_DB = "data/tasks.json"
BID_DB = "data/bids.json"

def load_db(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        with open(path, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_db(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ----- Page Config -----
st.set_page_config(
    page_title="TaskBid — Micro Task Platform",
    layout="wide",
    page_icon="🚀"
)

# ----- Light Theme Style -----
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #f9f9ff;
            color: #222;
        }
        .stButton>button {
            background: linear-gradient(90deg, #6200ea, #9c27b0);
            color: white;
            padding: 0.6rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #7b1fa2, #ba68c8);
        }
        input, textarea {
            background-color: #ffffff !important;
            color: #000 !important;
            border: 1px solid #ccc !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            font-size: 1rem !important;
        }
        .task-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        h1, h2, h3, h4 {
            color: #333;
        }
        .stExpander>button {
            background: #eeeeff;
            color: #333;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# ----- App Content -----
st.image("static/logo.png", width=120)
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
            st.markdown(f"""
                <div class='task-card'>
                    <h4>{t['title']} — ${t['price']}</h4>
                    <p>{t['description']}</p>
                    <small>Status: <b>{t['status'].capitalize()}</b></small>
            """, unsafe_allow_html=True)

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
        price = st.number_input("💲 Price", min_value=1, value=10)
        if st.button("📤 Post Task"):
            new_task = Task(title, desc, user['username'], price)
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
