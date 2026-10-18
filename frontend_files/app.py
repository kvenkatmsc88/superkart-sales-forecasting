import os
import requests
import pandas as pd
import streamlit as st

# URL of the Flask backend. Inside the Docker network the backend is reachable by its container name.
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")
CURRENT_YEAR = 2025

# Product type -> Product_Id prefix and perishable category (same logic as used in training)
DRINKS = ["Soft Drinks", "Hard Drinks"]
NON_CONSUMABLES = ["Household", "Health and Hygiene", "Others"]
PERISHABLES = ["Dairy", "Meat", "Fruits and Vegetables", "Breakfast", "Breads", "Seafood"]
PRODUCT_TYPES = sorted([
    "Meat", "Snack Foods", "Hard Drinks", "Dairy", "Canned", "Soft Drinks", "Health and Hygiene",
    "Baking Goods", "Breads", "Breakfast", "Frozen Foods", "Fruits and Vegetables", "Household",
    "Seafood", "Starchy Foods", "Others",
])

st.set_page_config(page_title="SuperKart Sales Forecasting", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecasting")
st.write("Forecast the revenue of a product in a store from its product and store attributes.")

online_tab, batch_tab = st.tabs(["Single prediction", "Batch prediction"])

# ---------------------------------------------------------------- Online prediction
with online_tab:
    st.subheader("Product details")
    product_type = st.selectbox("Product Type", PRODUCT_TYPES)

    # Product_Id prefix is derived from the product type: FD = Food, DR = Drinks, NC = Non-Consumable
    if product_type in DRINKS:
        product_id_char = "DR"
    elif product_type in NON_CONSUMABLES:
        product_id_char = "NC"
    else:
        product_id_char = "FD"

    if product_id_char == "NC":
        sugar_content = st.selectbox("Product Sugar Content", ["No Sugar"],
                                     help="Non-consumable products always have 'No Sugar'.")
    else:
        sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])

    product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
    product_allocated_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0,
                                             value=0.068, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=147.0, step=1.0)

    st.subheader("Store details")
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"], index=1)
    store_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    store_type = st.selectbox("Store Type", ["Departmental Store", "Supermarket Type1",
                                             "Supermarket Type2", "Food Mart"], index=2)
    establishment_year = st.number_input("Store Establishment Year", min_value=1950, max_value=CURRENT_YEAR,
                                         value=2009, step=1)

    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": sugar_content,
        "Product_Allocated_Area": product_allocated_area,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_city_type,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": int(CURRENT_YEAR - establishment_year),
        "Product_Type_Category": "Perishables" if product_type in PERISHABLES else "Non Perishables",
    }

    if st.button("Predict Sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted_Sales"]
                st.success(f"Forecasted Product Store Sales Total: **{prediction:,.2f}**")
            else:
                st.error(f"Error from the API ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

    with st.expander("Payload sent to the API"):
        st.json(payload)

# ---------------------------------------------------------------- Batch prediction
with batch_tab:
    st.write("Upload a CSV file with the columns: " + ", ".join(f"`{c}`" for c in payload.keys()))
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.dataframe(batch_df.head())

        if st.button("Predict Batch", type="primary"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": ("batch.csv", batch_df.to_csv(index=False).encode("utf-8"), "text/csv")},
                    timeout=120,
                )
                if response.status_code == 200:
                    predictions = response.json()
                    batch_df["Predicted_Sales"] = [predictions[str(i)] for i in range(len(batch_df))]
                    st.success("Batch predictions completed.")
                    st.dataframe(batch_df)
                    st.download_button("Download predictions", batch_df.to_csv(index=False).encode("utf-8"),
                                       file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"Error from the API ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
