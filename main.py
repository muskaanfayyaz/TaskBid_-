import streamlit as st
from models.user import User
from models.task import Task
from models.bid import Bid
from utils.auth import login, signup
from utils.stripe_utils import create_checkout_session
import json
import os

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

# Show Stripe result messages from query params
query_params = st.query_params
status = query_params.get("status", None)
restored_user = query_params.get("user", None)


if status == "success":
    st.success("🎉 Payment successful! Thank you.")
    st.query_params.clear()
    st.session_state['menu'] = "Dashboard"
    if "user" not in st.session_state and restored_user:
        users = load_db(USER_DB)
        matching_user = next((u for u in users if u['username'] == restored_user), None)
        if matching_user:
            st.session_state.user = matching_user
elif status == "cancel":
    st.warning("⚠️ Payment was canceled or failed.")

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
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="input"] input {
            background-color: #f0f0f0 !important;
            color: #000 !important;
            border: 1px solid #ccc !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            font-size: 1rem !important;
        }

        .task-card {
            background: #f0f0f0;
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

# Logo & Title
st.image("static/logo.png", width=150)
st.title("🚀 Welcome to TaskBid — Micro Task Platform")
st.markdown("""
### 💡 What is TaskBid?

**TaskBid** is a micro task marketplace where users can **buy or sell simple tasks** — like editing a video, fixing a bug, or designing a logo — all for **$10 per gig**.

- ✅ Buyers pay $10 per task.
- 💰 Sellers receive **$9** after a **$1 platform fee** is deducted.
- 🚀 Simple. Fast. Efficient.
""")



if "user" not in st.session_state:
    st.session_state.user = None

menu = ["Login", "Signup"] if not st.session_state.user else ["Dashboard", "Logout"]
choice = st.sidebar.selectbox("📋 Menu", menu, key="sidebar_menu")

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
        price = st.number_input("💲 Price (Max $10)", min_value=1, max_value=10, value=5, key="task_price")
        if st.button("📤 Post Task", key="post_task_btn"):
            if price > 10:
                st.warning("❌ Task price must not exceed $10.")
            elif not any(t['title'] == title for t in tasks):
                new_task = Task(title, desc, user['username'], price)
                tasks.append(new_task.to_dict())
                save_db(TASK_DB, tasks)
                st.success("✅ Task Posted!")
            else:
                st.warning("⚠️ A task with this title already exists.")

    st.markdown("## 🔎 Available Tasks to Bid")
    open_tasks = [t for t in tasks if t['status'] == 'open' and t['buyer'] != user['username']]
    for i, t in enumerate(open_tasks):
        with st.expander(f"💼 {t['title']} — ${t['price']} (Seller earns ${t['price'] - 1})"):
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
                <h4>{t['title']} — ${t['price']} (Seller receives ${t['price'] - 1})</h4>
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
                        try:
                            success_url = f"https://mf-taskb.streamlit.app/?status=success&user={user['username']}"
                            cancel_url = "https://mf-taskb.streamlit.app/?status=cancel"
                            session_url = create_checkout_session(
                                task_title=t['title'],
                                amount=t['price'],
                                success_url=success_url,
                                cancel_url=cancel_url
                            )
                            st.success("✅ Stripe session created successfully!")
                            st.markdown(f"""<a href="{session_url}" target="_blank"><button>💳 Pay Now</button></a>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"❌ Failed to create Stripe session: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## 💼 Your Submitted Bids")
    my_bids = [b for b in bids if b['seller'] == user['username']]
    for b in my_bids:
        st.markdown(f"- **Task:** {b['task']} | 💬 **Message:** {b['message']}")
