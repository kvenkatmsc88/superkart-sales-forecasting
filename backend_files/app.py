# Import necessary libraries
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Forecaster")
# Keep the batch predictions in the same order as the input rows
superkart_api.json.sort_keys = False

# Load the trained model pipeline (preprocessing + tuned XGBoost)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the order used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page (GET request)
@superkart_api.get("/")
def home():
    """Health check / welcome message for the API."""
    return "Welcome to the SuperKart Sales Forecasting API!"


# Define an endpoint for a single prediction (POST request)
@superkart_api.post("/v1/predict")
def predict_sales():
    """
    Takes the product and store details as a JSON payload and
    returns the forecasted Product_Store_Sales_Total.
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be a JSON object."}), 400

    # Validate that all required features are present
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Convert the input into a single-row DataFrame
    sample = pd.DataFrame([{f: data[f] for f in FEATURES}])

    # Make the prediction
    prediction = float(model.predict(sample)[0])

    return jsonify({"Predicted_Sales": round(prediction, 2)})


# Define an endpoint for batch predictions (POST request with a CSV file)
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """
    Takes a CSV file with the feature columns and returns a JSON where
    each key is the row index and the value is the forecasted sales.
    """
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "Please upload a CSV file using the 'file' key."}), 400

    input_data = pd.read_csv(file)

    # Validate that all required features are present
    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    # Make predictions for all rows
    predictions = model.predict(input_data[FEATURES])

    # Map each row index to its predicted sales
    result = {str(idx): round(float(pred), 2) for idx, pred in zip(input_data.index, predictions)}

    return jsonify(result)


# Run the Flask app (used only when running the file directly; gunicorn is used in Docker)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
