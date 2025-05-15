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

# Page Config
st.set_page_config(
    page_title="TaskBid — Micro Task Platform",
    layout="wide",
    page_icon="🚀"
)

# Styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #0f0f0f;
            color: #ffffff;
        }
        .stButton>button {
            background: linear-gradient(90deg, #8e24aa, #512da8);
            color: white;
            padding: 0.6rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #ba68c8, #7e57c2);
        }
        input, textarea {
            background-color: #1f1f1f !important;
            color: #fff !important;
            border: 1px solid #555 !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            font-size: 1rem !important;
        }
        .task-card {
            background: #1e1e2f;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.05);
        }
        h1, h2, h3, h4 {
            color: #fff;
        }
        .stExpander>button {
            background: #2e2e4e;
            color: #fff;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Content
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
    st.subheader(f"👤 Welcome, **{user['username']}** (Multi-role)")

    tasks = load_db(TASK_DB)
    bids = load_db(BID_DB)

    st.markdown("## 🎯 Post or View Tasks")
    with st.expander("➕ Post a Task"):
        title = st.text_input("📝 Task Title", key="task_title")
        desc = st.text_area("🧾 Description", key="task_desc")
        price = st.number_input("💲 Price", min_value=1, value=10, key="task_price")
        if st.button("📤 Post Task", key="post_task_btn"):
            if not any(t['title'] == title for t in tasks):
                new_task = Task(title, desc, user['username'], price)
                tasks.append(new_task.to_dict())
                save_db(TASK_DB, tasks)
                st.success("✅ Task Posted!")
            else:
                st.warning("⚠️ A task with this title already exists.")

    st.markdown("## 🔎 Available Tasks to Bid")
    open_tasks = [t for t in tasks if t['status'] == 'open' and t['buyer'] != user['username']]
    for i, t in enumerate(open_tasks):
        with st.expander(f"💼 {t['title']} — ${t['price']}"):
            st.markdown(f"🧾 {t['description']}")
            key_msg = f"bid_msg_{i}_{t['title']}"
            key_btn = f"bid_btn_{i}_{t['title']}"
            msg = st.text_input("✏️ Your Bid Message", key=key_msg)
            if st.button("📨 Submit Bid", key=key_btn):
                new_bid = Bid(t['title'], user['username'], msg)
                if not any(b['task'] == t['title'] and b['seller'] == user['username'] for b in bids):
                    bids.append(new_bid.to_dict())
                    save_db(BID_DB, bids)
                    st.success("🚀 Bid Submitted!")
                else:
                    st.warning("❌ You've already submitted a bid for this task.")

    st.markdown("## 📁 Your Tasks and Bids")
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
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Accept Bid from {b['seller']}", key=f"accept_{t['title']}_{b['seller']}"):
                        t['status'] = 'assigned'
                        save_db(TASK_DB, tasks)
                        st.success("🎉 Bid Accepted! Task Assigned.")
                with col2:
                    if st.button(f"💳 Pay with Stripe", key=f"pay_{t['title']}_{b['seller']}"):
                        st.info("🔐 Stripe payment would be processed here.")
                        # NOTE: Replace below with actual secure backend logic to create a Stripe session
                        # Example:
                        # session = create_stripe_checkout_session(task=t, buyer=user, seller=b['seller'])
                        # st.markdown(f"[🔗 Pay Now]({session.url})")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## 💼 Your Submitted Bids")
    my_bids = [b for b in bids if b['seller'] == user['username']]
    for b in my_bids:
        st.markdown(f"- **Task:** {b['task']} | 💬 **Message:** {b['message']}")

# 🔒 Note: Stripe integration should happen on a backend server for security.