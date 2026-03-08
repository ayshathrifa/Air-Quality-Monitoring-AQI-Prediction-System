import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class AQIPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def generate_training_data(self, n_samples=1000):
        """Generate synthetic training data"""
        np.random.seed(42)
        
        data = {
            'pm2_5': np.random.uniform(0, 250, n_samples),
            'pm10': np.random.uniform(0, 400, n_samples),
            'co': np.random.uniform(0, 2000, n_samples),
            'no2': np.random.uniform(0, 200, n_samples),
            'o3': np.random.uniform(0, 300, n_samples),
            'so2': np.random.uniform(0, 100, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate AQI based on PM2.5 (simplified)
        def calculate_aqi(row):
            pm25 = row['pm2_5']
            if pm25 <= 12: return 1
            elif pm25 <= 35.4: return 2
            elif pm25 <= 55.4: return 3
            elif pm25 <= 150.4: return 4
            else: return 5
        
        df['aqi'] = df.apply(calculate_aqi, axis=1)
        return df
    
    def train_model(self, data_path=None):
        """Train the AQI prediction model"""
        if data_path and os.path.exists(data_path):
            df = pd.read_csv(data_path)
        else:
            df = self.generate_training_data()
        
        X = df[['pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2']]
        y = df['aqi']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def predict(self, features):
        """Predict AQI from features"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        return int(prediction), probability
    
    def save_model(self, model_path='models/aqi_model.pkl', scaler_path='models/scaler.pkl'):
        """Save trained model and scaler"""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path='models/aqi_model.pkl', scaler_path='models/scaler.pkl'):
        """Load trained model and scaler"""
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            print("Model loaded successfully")
            return True
        return False

if __name__ == "__main__":
    predictor = AQIPredictor()
    predictor.train_model()
    predictor.save_model()
    
    # Test prediction
    test_features = [35.5, 50, 500, 40, 80, 20]
    aqi, prob = predictor.predict(test_features)
    print(f"\nTest Prediction - AQI: {aqi}, Probabilities: {prob}")
