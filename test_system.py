"""
Test Script - Verify All Components
"""
import os
import sys

print("=" * 70)
print("AIR QUALITY MONITORING SYSTEM - COMPONENT TEST")
print("=" * 70)
print()

# Test 1: Check Python version
print("[OK] Test 1: Python Version")
print(f"  Python {sys.version}")
print()

# Test 2: Check required files
print("[OK] Test 2: Required Files")
required_files = [
    'app.py',
    'data_collector.py',
    'model_trainer.py',
    'requirements.txt',
    'templates/index.html',
    'static/css/style.css',
    'static/js/script.js'
]

for file in required_files:
    if os.path.exists(file):
        print(f"  [OK] {file}")
    else:
        print(f"  [FAIL] {file} - MISSING!")
print()

# Test 3: Check directories
print("[OK] Test 3: Required Directories")
required_dirs = ['data', 'models', 'static', 'templates']

for dir in required_dirs:
    if os.path.exists(dir):
        print(f"  [OK] {dir}/")
    else:
        print(f"  [FAIL] {dir}/ - MISSING!")
print()

# Test 4: Import required modules
print("[OK] Test 4: Python Modules")
modules = {
    'flask': 'Flask',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'sklearn': 'Scikit-learn',
    'requests': 'Requests',
    'joblib': 'Joblib',
    'dotenv': 'Python-dotenv'
}

for module, name in modules.items():
    try:
        __import__(module)
        print(f"  [OK] {name}")
    except ImportError:
        print(f"  [FAIL] {name} - NOT INSTALLED!")
print()

# Test 5: Check ML model
print("[OK] Test 5: ML Model")
if os.path.exists('models/aqi_model.pkl'):
    print("  [OK] Model file exists")
    try:
        import joblib
        model = joblib.load('models/aqi_model.pkl')
        print("  [OK] Model loads successfully")
    except:
        print("  [FAIL] Model failed to load")
else:
    print("  [FAIL] Model not found - Run: python model_trainer.py")
print()

# Test 6: Test data collector
print("[OK] Test 6: Data Collector")
try:
    from data_collector import AirQualityDataCollector
    collector = AirQualityDataCollector()
    data = collector.get_demo_data()
    print("  [OK] Data collector works")
    print(f"  Sample data: AQI={data['aqi']}, PM2.5={data['pm2_5']}")
except Exception as e:
    print(f"  [FAIL] Data collector failed: {e}")
print()

# Test 7: Test model predictor
print("[OK] Test 7: Model Predictor")
try:
    from model_trainer import AQIPredictor
    predictor = AQIPredictor()
    if predictor.load_model():
        test_features = [35.5, 50, 500, 40, 80, 20]
        aqi, prob = predictor.predict(test_features)
        print("  [OK] Model predictor works")
        print(f"  Test prediction: AQI={aqi}, Confidence={max(prob)*100:.1f}%")
    else:
        print("  [FAIL] Model not loaded")
except Exception as e:
    print(f"  [FAIL] Model predictor failed: {e}")
print()

# Final Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print()
print("If all tests passed, your project is ready to run!")
print()
print("To start the application:")
print("  1. Run: python app.py")
print("  2. Open browser: http://localhost:5000")
print()
print("=" * 70)
