# streamlit_app.py
import streamlit as st
import requests

st.title("Make a Payment")

if st.button("Pay $15"):
    res = requests.post("http://localhost:5000/create-checkout-session", json={
        "task_name": "Task Example",
        "amount": 15,
        "success_url": "http://localhost:8501/success",
        "cancel_url": "http://localhost:8501/cancel"
    })
    if res.ok:
        url = res.json()["url"]
        st.markdown(f"[🔗 Click to complete payment]({url})", unsafe_allow_html=True)
    else:
        st.error("Error: " + res.json().get("error", "Unknown"))
