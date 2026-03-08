from flask import Flask, render_template, jsonify, request
from data_collector import AirQualityDataCollector
from model_trainer import AQIPredictor
import pandas as pd
import os

app = Flask(__name__)

collector = AirQualityDataCollector()
predictor = AQIPredictor()

# Load or train model
if not predictor.load_model():
    print("Training new model...")
    predictor.train_model()
    predictor.save_model()

AQI_CATEGORIES = {
    1: {"label": "Good", "color": "#00e400", "description": "Air quality is satisfactory"},
    2: {"label": "Moderate", "color": "#ffff00", "description": "Air quality is acceptable"},
    3: {"label": "Unhealthy for Sensitive Groups", "color": "#ff7e00", "description": "Sensitive groups may experience health effects"},
    4: {"label": "Unhealthy", "color": "#ff0000", "description": "Everyone may begin to experience health effects"},
    5: {"label": "Very Unhealthy", "color": "#8f3f97", "description": "Health alert: everyone may experience serious health effects"}
}

def get_health_advice(aqi, pm25):
    """Advanced Feature 1: Personalized Health Risk Alert"""
    advice = []
    
    if aqi == 1:
        advice = ["Air quality is good. Enjoy outdoor activities!"]
    elif aqi == 2:
        advice = [
            "Air quality is acceptable",
            "Sensitive individuals should limit prolonged outdoor exertion"
        ]
    elif aqi == 3:
        advice = [
            "⚠️ Sensitive groups should reduce outdoor activities",
            "Children and elderly should stay indoors",
            "Consider wearing a mask if going outside"
        ]
    elif aqi == 4:
        advice = [
            "🚨 Everyone should avoid prolonged outdoor activities",
            "Wear N95 mask when going outside",
            "Close windows and use air purifiers",
            "Asthma patients should keep inhalers ready"
        ]
    else:  # aqi == 5
        advice = [
            "🔴 HEALTH ALERT! Stay indoors",
            "Avoid all outdoor activities",
            "Use N95/N99 masks if you must go out",
            "Keep windows closed, use air purifiers",
            "Vulnerable groups should consult doctors"
        ]
    
    return advice

def detect_pollution_source(data):
    """Advanced Feature 4: Pollution Source Detection"""
    pm25 = data['pm2_5']
    pm10 = data['pm10']
    co = data['co']
    no2 = data['no2']
    
    sources = []
    
    # Traffic pollution (high NO2 and CO)
    if no2 > 40 and co > 600:
        sources.append({"source": "Traffic Emission", "confidence": 85})
    
    # Industrial pollution (high SO2 and PM10)
    if data['so2'] > 20 and pm10 > 100:
        sources.append({"source": "Industrial Pollution", "confidence": 78})
    
    # Construction dust (high PM10, low gases)
    if pm10 > pm25 * 2 and no2 < 30:
        sources.append({"source": "Construction Dust", "confidence": 72})
    
    # Biomass burning (high PM2.5 and CO)
    if pm25 > 60 and co > 700:
        sources.append({"source": "Biomass Burning", "confidence": 80})
    
    if not sources:
        sources.append({"source": "Mixed Sources", "confidence": 65})
    
    return sources[0]

@app.route('/')
def index():
    """Landing Page"""
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    """Main Dashboard"""
    return render_template('index.html')

@app.route('/alerts')
def alerts():
    """Alerts Page"""
    return render_template('alerts.html')

@app.route('/info')
def info():
    """Info Page - AQI Categories & Health Tips"""
    return render_template('info.html')

@app.route('/about')
def about():
    """About & Contact Page"""
    return render_template('about.html')

@app.route('/api/current', methods=['GET'])
def get_current_data():
    """Get current air quality data"""
    lat = request.args.get('lat', 12.9716)
    lon = request.args.get('lon', 77.5946)
    
    data = collector.fetch_air_quality(float(lat), float(lon))
    
    # Predict AQI
    features = [data['pm2_5'], data['pm10'], data['co'], data['no2'], data['o3'], data['so2']]
    predicted_aqi, probabilities = predictor.predict(features)
    
    data['predicted_aqi'] = int(predicted_aqi)
    data['aqi_info'] = AQI_CATEGORIES[predicted_aqi]
    data['confidence'] = float(max(probabilities) * 100)
    
    # Advanced Feature 1: Health Risk Alert
    data['health_advice'] = get_health_advice(predicted_aqi, data['pm2_5'])
    
    # Advanced Feature 2: Pollution Source Detection
    data['pollution_source'] = detect_pollution_source(data)
    
    # Save data
    collector.save_data(data)
    
    return jsonify(data)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical data"""
    data_file = 'data/air_quality_data.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df = df.tail(50)  # Last 50 records
        return jsonify(df.to_dict('records'))
    
    return jsonify([])

@app.route('/api/predict', methods=['POST'])
def predict_aqi():
    """Predict AQI from custom input"""
    data = request.json
    
    features = [
        float(data.get('pm2_5', 0)),
        float(data.get('pm10', 0)),
        float(data.get('co', 0)),
        float(data.get('no2', 0)),
        float(data.get('o3', 0)),
        float(data.get('so2', 0))
    ]
    
    predicted_aqi, probabilities = predictor.predict(features)
    
    return jsonify({
        'predicted_aqi': int(predicted_aqi),
        'aqi_info': AQI_CATEGORIES[predicted_aqi],
        'confidence': float(max(probabilities) * 100),
        'probabilities': probabilities.tolist()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    data_file = 'data/air_quality_data.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        
        stats = {
            'total_records': len(df),
            'avg_pm2_5': float(df['pm2_5'].mean()),
            'avg_pm10': float(df['pm10'].mean()),
            'avg_aqi': float(df['aqi'].mean()) if 'aqi' in df.columns else 0,
            'max_pm2_5': float(df['pm2_5'].max()),
            'min_pm2_5': float(df['pm2_5'].min())
        }
        
        return jsonify(stats)
    
    return jsonify({'total_records': 0})

@app.route('/api/trend', methods=['GET'])
def get_trend():
    """Advanced Feature 2: Pollution Trend Analysis"""
    data_file = 'data/air_quality_data.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df = df.tail(20)  # Last 20 records for trend
        
        trend_data = {
            'timestamps': df['timestamp'].tolist() if 'timestamp' in df.columns else [],
            'pm2_5': df['pm2_5'].tolist(),
            'pm10': df['pm10'].tolist(),
            'aqi': df['aqi'].tolist()
        }
        
        return jsonify(trend_data)
    
    return jsonify({'timestamps': [], 'pm2_5': [], 'pm10': [], 'aqi': []})

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    """Forecast AQI for next few hours"""
    data_file = 'data/air_quality_data.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        if len(df) > 0:
            # Simple forecast: use trend from last records
            recent_aqi = df['aqi'].tail(5).mean()
            forecast = [
                {'hour': 1, 'aqi': int(recent_aqi * 1.05)},
                {'hour': 3, 'aqi': int(recent_aqi * 1.08)},
                {'hour': 6, 'aqi': int(recent_aqi * 1.10)},
                {'hour': 12, 'aqi': int(recent_aqi * 1.12)},
            ]
            return jsonify(forecast)
    
    return jsonify([])

@app.route('/api/download', methods=['GET'])
def download_data():
    """Download data as CSV"""
    from flask import send_file
    data_file = 'data/air_quality_data.csv'
    
    if os.path.exists(data_file):
        return send_file(data_file, as_attachment=True, download_name='air_quality_data.csv')
    
    return jsonify({'error': 'No data available'}), 404

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
