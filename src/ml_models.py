<<<<<<< HEAD
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def load_data(file_path):
    """Load data from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def train_failure_prediction_model(data, model_path='models/failure_prediction_model.pkl'):
    """Train a RandomForest model for failure prediction and save it."""
    try:
        X = data.drop(columns=['failure'])
        y = data['failure']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(random_state=42, n_estimators=100, max_depth=8)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy:.3f}")
        print(classification_report(y_test, y_pred))
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        print(f"Model saved to {model_path}.")
    except Exception as e:
        print(f"Error training model: {e}")

def predict_failure(input_features, model_path='models/failure_prediction_model.pkl'):
    """Predict failure using the trained model."""
    try:
        model = joblib.load(model_path)
        prediction = model.predict([input_features])
        return prediction[0]
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

def evaluate_model(data, model_path='models/failure_prediction_model.pkl'):
    """Evaluate the trained model on the provided data."""
    try:
        X = data.drop(columns=['failure'])
        y = data['failure']
        model = joblib.load(model_path)
        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        print(f"Overall Model Accuracy: {accuracy:.3f}")
        print(classification_report(y, y_pred))
    except Exception as e:
=======
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def load_data(file_path):
    """Load data from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def train_failure_prediction_model(data, model_path='models/failure_prediction_model.pkl'):
    """Train a RandomForest model for failure prediction and save it."""
    try:
        X = data.drop(columns=['failure'])
        y = data['failure']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(random_state=42, n_estimators=100, max_depth=8)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy:.3f}")
        print(classification_report(y_test, y_pred))
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        print(f"Model saved to {model_path}.")
    except Exception as e:
        print(f"Error training model: {e}")

def predict_failure(input_features, model_path='models/failure_prediction_model.pkl'):
    """Predict failure using the trained model."""
    try:
        model = joblib.load(model_path)
        prediction = model.predict([input_features])
        return prediction[0]
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

def evaluate_model(data, model_path='models/failure_prediction_model.pkl'):
    """Evaluate the trained model on the provided data."""
    try:
        X = data.drop(columns=['failure'])
        y = data['failure']
        model = joblib.load(model_path)
        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        print(f"Overall Model Accuracy: {accuracy:.3f}")
        print(classification_report(y, y_pred))
    except Exception as e:
>>>>>>> 52ce655ce85126d4f7249c6c512f79f7223f613b
        print(f"Error evaluating model: {e}")