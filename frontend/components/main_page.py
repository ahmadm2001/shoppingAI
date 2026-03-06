import streamlit as st
import requests
import pandas as pd


def render(api_url: str, get_headers):
    """Render the main store page with items grid and search."""
    st.title("🛍️ Welcome to AI Shop")
    st.markdown("Browse our products, search by name, price, or stock availability.")

    # --- Search Section ---
    st.subheader("🔍 Search Products")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_name = st.text_input(
            "Search by name",
            placeholder="e.g. sun, table (comma-separated for multiple)",
            help="Enter one or more keywords separated by commas",
        )

    with col2:
        price_col1, price_col2 = st.columns(2)
        with price_col1:
            price_op = st.selectbox("Price filter", ["None", "<", ">", "="], index=0)
        with price_col2:
            price_val = st.number_input("Price value", min_value=0.0, value=0.0, step=1.0)

    with col3:
        stock_col1, stock_col2 = st.columns(2)
        with stock_col1:
            stock_op = st.selectbox("Stock filter", ["None", "<", ">", "="], index=0)
        with stock_col2:
            stock_val = st.number_input("Stock value", min_value=0, value=0, step=1)

    search_clicked = st.button("🔍 Search", use_container_width=True)

    st.divider()

    # --- Fetch Items ---
    try:
        if search_clicked and (search_name or price_op != "None" or stock_op != "None"):
            params = {}
            if search_name:
                params["name"] = search_name
            if price_op != "None" and price_val > 0:
                params["price"] = price_val
                params["price_op"] = price_op
            if stock_op != "None":
                params["stock"] = stock_val
                params["stock_op"] = stock_op

            response = requests.get(f"{api_url}/items/search", params=params, timeout=10)
        else:
            response = requests.get(f"{api_url}/items/", timeout=10)

        if response.status_code == 200:
            items = response.json()
        else:
            st.error(f"Failed to load items: {response.text}")
            items = []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend server. Please make sure the server is running.")
        items = []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        items = []

    # --- Display Items ---
    if not items:
        if search_clicked:
            st.warning("🔍 No items found matching your search criteria.")
        else:
            st.info("No items available at the moment.")
        return

    st.subheader(f"📦 Available Items ({len(items)} products)")

    # Display as DataFrame
    df = pd.DataFrame(items)
    display_df = df[["name", "price", "stock", "category", "description"]].copy()
    display_df.columns = ["Item Name", "Price (USD)", "In Stock", "Category", "Description"]
    display_df["Price (USD)"] = display_df["Price (USD)"].apply(lambda x: f"${x:.2f}")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # Display as cards grid
    st.subheader("🛒 Product Cards")
    cols = st.columns(3)
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {item['name']}")
                st.markdown(f"**Category:** {item.get('category', 'N/A')}")
                st.markdown(f"**Price:** ${item['price']:.2f}")

                if item["stock"] > 0:
                    st.markdown(f"**In Stock:** {item['stock']}")
                else:
                    st.markdown("**⚠️ Out of Stock**")

                if item.get("description"):
                    with st.expander("Description"):
                        st.write(item["description"])

                # Action buttons (only for logged-in users)
                if st.session_state.user:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if item["stock"] > 0:
                            if st.button("🛒 Add to Order", key=f"order_{item['id']}"):
                                _add_to_order(api_url, get_headers, item)
                        else:
                            st.button(
                                "❌ Out of Stock",
                                key=f"order_{item['id']}",
                                disabled=True,
                            )
                    with btn_col2:
                        if st.button("❤️ Favorite", key=f"fav_{item['id']}"):
                            _add_to_favorites(api_url, get_headers, item)


def _add_to_order(api_url, get_headers, item):
    """Add an item to the user's pending order."""
    try:
        response = requests.post(
            f"{api_url}/orders/items",
            json={"item_id": item["id"], "quantity": 1},
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success(response.json().get("message", "Item added to order!"))
        else:
            error_detail = response.json().get("detail", "Failed to add item to order")
            st.error(error_detail)
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _add_to_favorites(api_url, get_headers, item):
    """Add an item to the user's favorites."""
    try:
        response = requests.post(
            f"{api_url}/favorites/{item['id']}",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success(response.json().get("message", "Item added to favorites!"))
        else:
            error_detail = response.json().get("detail", "Failed to add to favorites")
            st.error(error_detail)
    except Exception as e:
        st.error(f"Error: {str(e)}")
