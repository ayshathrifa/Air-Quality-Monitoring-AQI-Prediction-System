import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

FEATURES = ['pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2']


class AQIPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def generate_training_data(self, n_samples=2000):
        np.random.seed(42)
        pm25 = np.random.uniform(0, 250, n_samples)
        data = {
            'pm2_5': pm25,
            'pm10': pm25 * np.random.uniform(1.3, 2.0, n_samples),
            'co': pm25 * np.random.uniform(4, 9, n_samples),
            'no2': pm25 * np.random.uniform(0.3, 0.8, n_samples),
            'o3': np.random.uniform(20, 300, n_samples),
            'so2': pm25 * np.random.uniform(0.08, 0.3, n_samples),
        }
        df = pd.DataFrame(data)
        df['aqi'] = pd.cut(
            df['pm2_5'],
            bins=[-1, 12, 35.4, 55.4, 150.4, 500],
            labels=[1, 2, 3, 4, 5]
        ).astype(int)
        return df

    def compare_models(self, data_path=None):
        """Train and compare RF, GBM, Logistic Regression (and XGBoost if available)."""
        if data_path and os.path.exists(data_path):
            df = pd.read_csv(data_path)
        else:
            df = self.generate_training_data()

        X = df[FEATURES]
        y = df['aqi']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        X_train_s = self.scaler.fit_transform(X_train)
        X_test_s = self.scaler.transform(X_test)

        candidates = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        }
        # XGBoost requires 0-indexed labels starting from 0
        label_min = int(y_train.min())
        y_train_xgb = y_train - label_min
        y_test_xgb = y_test - label_min
        self._xgb_label_min = label_min

        if XGBOOST_AVAILABLE:
            candidates['XGBoost'] = XGBClassifier(
                n_estimators=100, random_state=42,
                eval_metric='mlogloss', verbosity=0
            )

        results = {}
        best_acc = 0
        best_model = None

        for name, clf in candidates.items():
            is_xgb = XGBOOST_AVAILABLE and name == 'XGBoost'
            clf.fit(X_train_s, y_train_xgb if is_xgb else y_train)
            preds = clf.predict(X_test_s)
            acc = accuracy_score(y_test_xgb if is_xgb else y_test, preds)
            cv_y = y_train_xgb if is_xgb else y_train
            cv = cross_val_score(clf, X_train_s, cv_y, cv=3, scoring='accuracy').mean()
            results[name] = {'accuracy': round(float(acc) * 100, 2), 'cv_accuracy': round(float(cv) * 100, 2)}
            print(f"{name}: Test={acc:.3f}, CV={cv:.3f}")
            if acc > best_acc:
                best_acc = acc
                best_model = clf

        self.model = best_model
        return results

    def train_model(self, data_path=None):
        self.compare_models(data_path)

    def predict(self, features):
        if self.model is None:
            raise ValueError("Model not trained yet!")
        X = pd.DataFrame([features], columns=FEATURES)
        scaled = self.scaler.transform(X)
        pred = int(self.model.predict(scaled)[0])
        proba = self.model.predict_proba(scaled)[0]
        if XGBOOST_AVAILABLE and isinstance(self.model, XGBClassifier):
            pred = pred + getattr(self, '_xgb_label_min', 1)
        pred = max(1, min(5, pred))
        return pred, proba

    def save_model(self, model_path='models/aqi_model.pkl', scaler_path='models/scaler.pkl'):
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)

    def load_model(self, model_path='models/aqi_model.pkl', scaler_path='models/scaler.pkl'):
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            return True
        return False


def forecast_24h(df: pd.DataFrame) -> list:
    """
    Simple 24-hour AQI forecast using rolling mean + seasonal noise.
    Uses last 30 days of PM2.5 to project next 24 hours.
    """
    if df.empty or len(df) < 5:
        return []

    recent_pm25 = df['pm2_5'].tail(30).values
    mean_pm25 = recent_pm25.mean()
    std_pm25 = recent_pm25.std() if len(recent_pm25) > 1 else mean_pm25 * 0.1

    np.random.seed(int(mean_pm25) % 100)
    forecasts = []
    for h in range(1, 25):
        # Diurnal pattern: higher in morning/evening rush hours
        hour_factor = 1.0 + 0.15 * np.sin((h - 8) * np.pi / 12)
        pm25_pred = max(1, mean_pm25 * hour_factor + np.random.normal(0, std_pm25 * 0.3))

        if pm25_pred <= 12: aqi = 1
        elif pm25_pred <= 35.4: aqi = 2
        elif pm25_pred <= 55.4: aqi = 3
        elif pm25_pred <= 150.4: aqi = 4
        else: aqi = 5

        forecasts.append({'hour': h, 'pm2_5': round(float(pm25_pred), 1), 'aqi': aqi})

    return forecasts


if __name__ == '__main__':
    predictor = AQIPredictor()
    results = predictor.compare_models()
    predictor.save_model()
    print("\nModel Comparison Results:")
    for name, metrics in results.items():
        print(f"  {name}: Accuracy={metrics['accuracy']}%, CV={metrics['cv_accuracy']}%")
