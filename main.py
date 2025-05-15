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
st.set_page_config(page_title="TaskBid — Micro Task Platform", layout="centered", page_icon="🚀")

# ----- Custom Style -----
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif !important;
        }
        .main {
            background: radial-gradient(circle at top left, #1a002d 0%, #000000 100%) !important;
            padding: 3rem 5rem;
        }
        section[data-testid="stSidebar"] {
            background-color: #13001a;
            color: #eee;
        }
        .stButton>button {
            background: linear-gradient(90deg, #6f00ff, #bb86fc);
            color: white;
            padding: 0.8rem 2rem;
            border-radius: 10px;
            font-weight: bold;
            border: none;
            box-shadow: 0 4px 12px rgba(187,134,252,0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #8e24aa, #ce93d8);
            box-shadow: 0 6px 18px rgba(206,147,216,0.5);
        }
        input, textarea {
            background-color: #1f1f2e !important;
            color: #fff !important;
            border-radius: 10px !important;
            border: 1.5px solid #6f00ff !important;
            padding: 0.75rem !important;
            font-size: 1rem !important;
        }
        .task-card {
            background: #1b0033;
            border: 1px solid #6f00ff;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 14px rgba(111, 0, 255, 0.2);
            transition: transform 0.3s ease;
        }
        .task-card:hover {
            transform: translateY(-5px);
        }
        h1, h2, h3, h4 {
            color: #f0d9ff;
        }
        .stExpander>button {
            background: #37005a;
            color: white;
            border-radius: 10px;
            font-weight: 600;
        }
        .stExpander>button:hover {
            background: #5c00a3;
        }
    </style>
""", unsafe_allow_html=True)

# ----- App Content -----
st.image("static/logo.png", width=120)
st.title(":rocket: Welcome to TaskBid — Micro Task Platform")

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
    st.success("🔐 Logged out successfully.")

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
        desc = st.text_area("🧞 Description")
        price = st.number_input("Price ($)", min_value=5.0, step=1.0)
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
                st.markdown(f"🧞 {t['description']}")
                msg = st.text_input(f"✍️ Bid Message for '{t['title']}'", key=t['title'])
                if st.button("📨 Submit Bid", key=f"{t['title']}_bid"):
                    new_bid = Bid(t['title'], user['username'], msg)
                    bids.append(new_bid.to_dict())
                    save_db(BID_DB, bids)
                    st.success("🚀 Bid Submitted!")

        st.markdown("### 📁 Your Bids")
        my_bids = [b for b in bids if b['seller'] == user['username']]
        for b in my_bids:
            st.markdown(f"- **Task:** {b['task']} | 💬 **Message:** {b['message']}")
