import streamlit as st
import requests
import pandas as pd


def render(api_url: str, get_headers):
    """Render the favorites page."""
    st.title("❤️ My Favorites")

    try:
        response = requests.get(
            f"{api_url}/favorites/",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            favorites = response.json()
        else:
            st.error("Failed to load favorites.")
            favorites = []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the server.")
        favorites = []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        favorites = []

    if not favorites:
        st.info("Your favorites list is empty. Browse the store and add items you like!")
        return

    st.subheader(f"You have {len(favorites)} favorite item(s)")

    # Display as DataFrame
    df = pd.DataFrame(favorites)
    display_df = df[["name", "price", "stock", "category", "description"]].copy()
    display_df.columns = ["Item Name", "Price (USD)", "In Stock", "Category", "Description"]
    display_df["Price (USD)"] = display_df["Price (USD)"].apply(lambda x: f"${x:.2f}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # Display as cards with remove option
    cols = st.columns(3)
    for idx, fav in enumerate(favorites):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {fav['name']}")
                st.markdown(f"**Price:** ${fav['price']:.2f}")

                if fav["stock"] > 0:
                    st.markdown(f"**In Stock:** {fav['stock']}")
                else:
                    st.markdown("**⚠️ Out of Stock**")

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if fav["stock"] > 0:
                        if st.button("🛒 Add to Order", key=f"fav_order_{fav['item_id']}"):
                            _add_to_order(api_url, get_headers, fav)
                    else:
                        st.button("❌ Out of Stock", key=f"fav_order_{fav['item_id']}", disabled=True)
                with btn_col2:
                    if st.button("🗑️ Remove", key=f"fav_remove_{fav['item_id']}"):
                        _remove_favorite(api_url, get_headers, fav)


def _add_to_order(api_url, get_headers, fav):
    """Add a favorite item to the order."""
    try:
        response = requests.post(
            f"{api_url}/orders/items",
            json={"item_id": fav["item_id"], "quantity": 1},
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success(response.json().get("message", "Item added to order!"))
        else:
            st.error(response.json().get("detail", "Failed to add item"))
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _remove_favorite(api_url, get_headers, fav):
    """Remove an item from favorites."""
    try:
        response = requests.delete(
            f"{api_url}/favorites/{fav['item_id']}",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success("Item removed from favorites!")
            st.rerun()
        else:
            st.error(response.json().get("detail", "Failed to remove item"))
    except Exception as e:
        st.error(f"Error: {str(e)}")
