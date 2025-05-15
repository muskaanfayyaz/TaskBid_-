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

# Initialize session state variables
for key in ["user", "menu", "task_post_status", "bid_status", "accept_status", "complete_status"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Page Config
st.set_page_config(
    page_title="TaskBid — Micro Task Platform",
    layout="wide",
    page_icon="🚀"
)

# Handle Stripe results
query_params = st.query_params
status = query_params.get("status", None)
restored_user = query_params.get("user", None)

if st.session_state.user is None and restored_user:
    users = load_db(USER_DB)
    match = next((u for u in users if u['username'] == restored_user), None)
    if match:
        st.session_state.user = match

if status == "success":
    st.success("🎉 Payment successful! Thank you.")
    tasks = load_db(TASK_DB)
    task_title = query_params.get("task")
    if task_title:
        for t in tasks:
            if t['title'] == task_title and t['buyer'] == restored_user:
                t['status'] = 'completed'
                save_db(TASK_DB, tasks)
                st.success("✅ Task marked as completed and paid!")
    st.query_params.clear()
    st.session_state.menu = "Dashboard"
    st.rerun()
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

st.image("static/logo.png", width=150)
st.title("🚀 Welcome to TaskBid — Micro Task Platform")
st.markdown("""
### 💡 What is TaskBid?

**TaskBid** is a micro task marketplace where users can **buy or sell simple tasks** — like editing a video, fixing a bug, or designing a logo — all for **$10 per gig**.

- ✅ Buyers pay $10 per task.
- 💰 Sellers receive $9 after a $1 platform fee is deducted.
- 🚀 Simple. Fast. Efficient.
""")

menu = ["Login", "Signup"] if not st.session_state.user else ["Dashboard", "Logout"]
choice = st.sidebar.selectbox("📋 Menu", menu, key="sidebar_menu")

if choice == "Login":
    login(USER_DB)
elif choice == "Signup":
    signup(USER_DB)
elif choice == "Logout":
    st.session_state.user = None
    st.success("🔐 Logged out successfully.")
elif choice == "Dashboard":
    user = st.session_state.user
    st.subheader(f"👤 Welcome, **{user['username']}** (Multi-role)")
    tasks = load_db(TASK_DB)
    bids = load_db(BID_DB)

    st.markdown("## 🎯 Post or View Tasks")
    with st.expander("➕ Post a Task"):
        title = st.text_input("📝 Task Title", key="task_title")
        desc = st.text_area("🧒️ Description", key="task_desc")
        price = st.number_input("💲 Price (Max $10)", min_value=1, max_value=10, value=5, key="task_price")

        if st.button("📤 Post Task", key="post_task_btn"):
            if price > 10:
                st.session_state.task_post_status = "price_error"
            elif not any(t['title'] == title for t in tasks):
                new_task = Task(title, desc, user['username'], price)
                tasks.append(new_task.to_dict())
                save_db(TASK_DB, tasks)
                st.session_state.task_post_status = "success"
                st.rerun()
            else:
                st.session_state.task_post_status = "duplicate"

        if st.session_state.task_post_status == "success":
            st.success("✅ Task Posted!")
            st.session_state.task_post_status = None
        elif st.session_state.task_post_status == "duplicate":
            st.warning("⚠️ A task with this title already exists.")
            st.session_state.task_post_status = None
        elif st.session_state.task_post_status == "price_error":
            st.warning("❌ Task price must not exceed $10.")
            st.session_state.task_post_status = None

    st.markdown("## 🔎 Available Tasks to Bid")
    open_tasks = [t for t in tasks if t['status'] == 'open' and t['buyer'] != user['username']]
    for i, t in enumerate(open_tasks):
        with st.expander(f"💼 {t['title']} — ${t['price']} (Seller_earns_${t['price'] - 1})"):
            st.markdown(f"🧒️ {t['description']}")
            key_msg = f"bid_msg_{i}_{t['title']}"
            key_btn = f"bid_btn_{i}_{t['title']}"
            msg = st.text_input("✏️ Your Bid Message", key=key_msg)
            if st.button("📨 Submit Bid", key=key_btn):
                new_bid = Bid(t['title'], user['username'], msg)
                if not any(b['task'] == t['title'] and b['seller'] == user['username'] for b in bids):
                    bids.append(new_bid.to_dict())
                    save_db(BID_DB, bids)
                    st.session_state.bid_status = "submitted"
                    st.rerun()
                else:
                    st.session_state.bid_status = "duplicate"
                    st.rerun()

    if st.session_state.bid_status == "submitted":
        st.success("🚀 Bid Submitted!")
        st.session_state.bid_status = None
    elif st.session_state.bid_status == "duplicate":
        st.warning("❌ You've already submitted a bid for this task.")
        st.session_state.bid_status = None

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
                if st.button(f"✅ Accept Bid from {b['seller']}", key=f"accept_{t['title']}_{b['seller']}"):
                    t['assigned_to'] = b['seller']
                    save_db(TASK_DB, tasks)
                    st.session_state.accept_status = f"🎉 Bid Accepted! {b['seller']} can now work on the task."
                    st.rerun()

        if st.session_state.accept_status:
            st.success(st.session_state.accept_status)
            st.session_state.accept_status = None

        if t.get('assigned_to') and t['status'] == 'pending_payment':
            st.info(f"✅ {t['assigned_to']} has completed this task. Please proceed with payment.")
            if st.button("💳 Pay with Stripe", key=f"pay_after_{t['title']}"):
                try:
                    success_url = f"https://mf-taskb.streamlit.app/?status=success&user={user['username']}&task={t['title']}"
                    cancel_url = "https://mf-taskb.streamlit.app/?status=cancel"
                    session_url = create_checkout_session(
                        task_title=t['title'],
                        amount=t['price'],
                        success_url=success_url,
                        cancel_url=cancel_url
                    )
                    st.markdown(f"""<a href=\"{session_url}\" target=\"_blank\"><button>💳 Pay Now</button></a>""", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Failed to create Stripe session: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## 💼 Your Submitted Bids")
    my_bids = [b for b in bids if b['seller'] == user['username']]
    for b in my_bids:
        st.markdown(f"- **Task:** {b['task']} | 💬 **Message:** {b['message']}")

    st.markdown("## 📌 Assigned Tasks To You")
    assigned_to_me = [t for t in tasks if t.get('assigned_to') == user['username'] and t['status'] != 'completed']
    for t in assigned_to_me:
        st.markdown(f"### 🧒️ {t['title']} — ${t['price']}")
        st.write(t['description'])
        if st.button("✅ Mark as Completed", key=f"complete_{t['title']}"):
            t['status'] = 'pending_payment'
            save_db(TASK_DB, tasks)
            st.session_state.complete_status = "🎯 Task marked as completed. Awaiting buyer payment."
            st.rerun()

    if st.session_state.complete_status:
        st.success(st.session_state.complete_status)
        st.session_state.complete_status = None
