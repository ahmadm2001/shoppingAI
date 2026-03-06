import streamlit as st
import requests
import uuid


def render(api_url: str, get_headers):
    """Render the AI chat assistant page."""
    st.title("🤖 AI Shopping Assistant")
    st.markdown(
        "Ask me anything about our products! I can help you find items, "
        "check availability, compare prices, and more."
    )

    # Session info
    remaining = 5 - st.session_state.chat_count
    if remaining > 0:
        st.info(f"💬 You have **{remaining}** prompts remaining in this session.")
    else:
        st.error("❌ You have used all 5 prompts for this session.")
        if st.button("🔄 Start New Session"):
            st.session_state.chat_session_id = str(uuid.uuid4())
            st.session_state.chat_messages = []
            st.session_state.chat_count = 0
            st.rerun()
        return

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])

    # Chat input
    user_input = st.chat_input(
        "Ask about our products...",
        disabled=(st.session_state.chat_count >= 5),
    )

    if user_input:
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": user_input})

        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)

        # Send to backend
        try:
            response = requests.post(
                f"{api_url}/chat/",
                json={
                    "message": user_input,
                    "session_id": st.session_state.chat_session_id,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                reply = data["reply"]
                prompts_remaining = data["prompts_remaining"]

                # Update count
                st.session_state.chat_count = 5 - prompts_remaining

                # Add assistant message to history
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})

                # Display assistant message
                with chat_container:
                    with st.chat_message("assistant"):
                        st.write(reply)

                st.rerun()
            else:
                error_detail = response.json().get("detail", "Failed to get response")
                st.error(error_detail)
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the server. Please try again later.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # New session button
    st.divider()
    if st.button("🔄 Start New Chat Session"):
        st.session_state.chat_session_id = str(uuid.uuid4())
        st.session_state.chat_messages = []
        st.session_state.chat_count = 0
        st.rerun()
