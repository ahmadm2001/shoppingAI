import streamlit as st
import requests


def render(api_url: str):
    """Render the login and registration page."""
    st.title("🔑 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        _render_login(api_url)

    with tab2:
        _render_register(api_url)


def _render_login(api_url: str):
    """Render the login form."""
    st.subheader("Login to your account")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

    if submit:
        if not username or not password:
            st.error("Please fill in all fields.")
            return

        try:
            response = requests.post(
                f"{api_url}/users/login",
                json={"username": username, "password": password},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.session_state.current_page = "main"
                st.success(f"Welcome back, {data['user']['first_name']}!")
                st.rerun()
            else:
                error_detail = response.json().get("detail", "Login failed")
                st.error(error_detail)
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the server. Please try again later.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def _render_register(api_url: str):
    """Render the registration form."""
    st.subheader("Create a new account")

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *")
            email = st.text_input("Email *")
            country = st.text_input("Country")
            username = st.text_input("Username *", key="reg_username")
        with col2:
            last_name = st.text_input("Last Name *")
            phone = st.text_input("Phone")
            city = st.text_input("City")
            password = st.text_input("Password *", type="password", key="reg_password")

        submit = st.form_submit_button("Register", use_container_width=True)

    if submit:
        if not first_name or not last_name or not email or not username or not password:
            st.error("Please fill in all required fields (marked with *).")
            return

        try:
            response = requests.post(
                f"{api_url}/users/register",
                json={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone or None,
                    "country": country or None,
                    "city": city or None,
                    "username": username,
                    "password": password,
                },
                timeout=10,
            )
            if response.status_code == 200:
                st.success("Account created successfully! You can now login.")
            else:
                error_detail = response.json().get("detail", "Registration failed")
                st.error(error_detail)
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the server. Please try again later.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def render_delete_account(api_url: str, get_headers):
    """Render the delete account confirmation page."""
    st.title("🗑️ Delete Account")
    st.warning(
        "**Warning:** This action is irreversible. "
        "All your data including orders, favorites, and account information will be permanently deleted."
    )

    if st.button("⚠️ Yes, Delete My Account", type="primary"):
        try:
            response = requests.delete(
                f"{api_url}/users/me",
                headers=get_headers(),
                timeout=10,
            )
            if response.status_code == 200:
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.current_page = "main"
                st.success("Your account has been deleted successfully.")
                st.rerun()
            else:
                error_detail = response.json().get("detail", "Failed to delete account")
                st.error(error_detail)
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if st.button("Cancel"):
        st.session_state.current_page = "main"
        st.rerun()
