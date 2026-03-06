import streamlit as st
import requests
import pandas as pd


def render(api_url: str, get_headers):
    """Render the orders page with order list and order processing."""
    st.title("📦 My Orders")

    try:
        response = requests.get(
            f"{api_url}/orders/",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            orders = response.json()
        else:
            st.error("Failed to load orders.")
            orders = []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the server.")
        orders = []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        orders = []

    if not orders:
        st.info("You have no orders yet. Start shopping and add items to your order!")
        return

    # Separate TEMP and CLOSE orders
    temp_orders = [o for o in orders if o["status"] == "TEMP"]
    closed_orders = [o for o in orders if o["status"] == "CLOSE"]

    # --- Pending Order ---
    if temp_orders:
        st.subheader("🟡 Pending Order")
        order = temp_orders[0]
        _render_temp_order(api_url, get_headers, order)

    # --- Closed Orders ---
    if closed_orders:
        st.subheader("✅ Order History")
        for order in closed_orders:
            _render_closed_order(order)


def _render_temp_order(api_url, get_headers, order):
    """Render the pending (TEMP) order with edit capabilities."""
    with st.container(border=True):
        st.markdown(
            f"**Order #{order['id']}** | "
            f"Date: {order['order_date'][:10]} | "
            f"**Status: PENDING**"
        )

        # Items table
        if order["items"]:
            items_data = []
            for item in order["items"]:
                items_data.append({
                    "Item": item.get("item_name", f"Item #{item['item_id']}"),
                    "Quantity": item["quantity"],
                    "Price": f"${item['price_at_order']:.2f}",
                    "Subtotal": f"${item['price_at_order'] * item['quantity']:.2f}",
                })

            df = pd.DataFrame(items_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown(f"### Total: ${order['total_price']:.2f}")

        # Shipping address
        st.divider()
        st.markdown("**Shipping Address:**")
        new_address = st.text_input(
            "Update shipping address",
            value=order.get("shipping_address", ""),
            key="shipping_address_input",
        )
        if st.button("📍 Update Address", key="update_address"):
            _update_address(api_url, get_headers, new_address)

        st.divider()

        # Item management
        st.markdown("**Manage Items:**")
        if order["items"]:
            for item in order["items"]:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    item_name = item.get('item_name', f'Item #{item["item_id"]}')
                    st.write(f"{item_name} - Qty: {item['quantity']}")

                with col2:
                    new_qty = st.number_input(
                        "Qty",
                        min_value=0,
                        value=item["quantity"],
                        key=f"qty_{item['item_id']}",
                        label_visibility="collapsed",
                    )
                    if new_qty != item["quantity"]:
                        if st.button("Update", key=f"update_qty_{item['item_id']}"):
                            _update_quantity(api_url, get_headers, item["item_id"], new_qty)
                with col3:
                    if st.button("🗑️", key=f"remove_order_item_{item['item_id']}"):
                        _remove_item(api_url, get_headers, item["item_id"])

        st.divider()

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Purchase Order", type="primary", use_container_width=True):
                _purchase_order(api_url, get_headers)
        with col2:
            if st.button("🗑️ Delete Order", type="secondary", use_container_width=True):
                _delete_order(api_url, get_headers)


def _render_closed_order(order):
    """Render a closed (historical) order - view only."""
    with st.expander(
        f"Order #{order['id']} | {order['order_date'][:10]} | "
        f"Total: ${order['total_price']:.2f} | ✅ COMPLETED"
    ):
        if order["items"]:
            items_data = []
            for item in order["items"]:
                items_data.append({
                    "Item": item.get("item_name", f"Item #{item['item_id']}"),
                    "Quantity": item["quantity"],
                    "Price": f"${item['price_at_order']:.2f}",
                    "Subtotal": f"${item['price_at_order'] * item['quantity']:.2f}",
                })
            df = pd.DataFrame(items_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown(f"**Shipping Address:** {order.get('shipping_address', 'N/A')}")
        st.markdown(f"**Total Price:** ${order['total_price']:.2f}")


def _update_address(api_url, get_headers, address):
    try:
        response = requests.put(
            f"{api_url}/orders/address",
            json={"shipping_address": address},
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success("Shipping address updated!")
            st.rerun()
        else:
            st.error(response.json().get("detail", "Failed to update address"))
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _update_quantity(api_url, get_headers, item_id, quantity):
    try:
        response = requests.put(
            f"{api_url}/orders/items",
            json={"item_id": item_id, "quantity": quantity},
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success("Quantity updated!")
            st.rerun()
        else:
            st.error(response.json().get("detail", "Failed to update quantity"))
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _remove_item(api_url, get_headers, item_id):
    try:
        response = requests.delete(
            f"{api_url}/orders/items/{item_id}",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success(response.json().get("message", "Item removed!"))
            st.rerun()
        else:
            st.error(response.json().get("detail", "Failed to remove item"))
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _purchase_order(api_url, get_headers):
    try:
        response = requests.post(
            f"{api_url}/orders/purchase",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success("🎉 Order purchased successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error(response.json().get("detail", "Failed to purchase order"))
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _delete_order(api_url, get_headers):
    try:
        response = requests.delete(
            f"{api_url}/orders/",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            st.success("Order deleted successfully!")
            st.rerun()
        else:
            st.error(response.json().get("detail", "Failed to delete order"))
    except Exception as e:
        st.error(f"Error: {str(e)}")
