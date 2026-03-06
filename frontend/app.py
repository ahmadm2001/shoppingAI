import streamlit as st
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_URL = f"{BACKEND_URL}/api"

st.set_page_config(
    page_title="AI Shopping Website",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"
if "chat_session_id" not in st.session_state:
    import uuid
    st.session_state.chat_session_id = str(uuid.uuid4())
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0


def get_headers():
    """Get authorization headers if user is logged in."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def navigate(page: str):
    """Navigate to a different page."""
    st.session_state.current_page = page


# Import pages
from components import main_page, auth_page, favorites_page, orders_page, chat_page

# Sidebar navigation
with st.sidebar:
    st.title("🛒 AI Shop")
    st.divider()

    if st.session_state.user:
        st.write(f"Welcome, **{st.session_state.user['first_name']}**!")
        st.divider()

    if st.button("🏠 Main Store", use_container_width=True):
        navigate("main")

    if st.session_state.user:
        if st.button("❤️ Favorites", use_container_width=True):
            navigate("favorites")
        if st.button("📦 My Orders", use_container_width=True):
            navigate("orders")

    if st.button("🤖 Chat Assistant", use_container_width=True):
        navigate("chat")

    st.divider()

    if st.session_state.user:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.current_page = "main"
            st.rerun()

        if st.button("🗑️ Delete Account", use_container_width=True, type="secondary"):
            navigate("delete_account")
    else:
        if st.button("🔑 Login / Register", use_container_width=True):
            navigate("auth")

# Main content routing
page = st.session_state.current_page

if page == "main":
    main_page.render(API_URL, get_headers)
elif page == "auth":
    auth_page.render(API_URL)
elif page == "favorites":
    if not st.session_state.user:
        st.warning("Please login to access your favorites.")
        auth_page.render(API_URL)
    else:
        favorites_page.render(API_URL, get_headers)
elif page == "orders":
    if not st.session_state.user:
        st.warning("Please login to access your orders.")
        auth_page.render(API_URL)
    else:
        orders_page.render(API_URL, get_headers)
elif page == "chat":
    chat_page.render(API_URL, get_headers)
elif page == "delete_account":
    auth_page.render_delete_account(API_URL, get_headers)
