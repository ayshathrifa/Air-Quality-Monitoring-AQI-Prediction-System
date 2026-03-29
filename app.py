from flask import Flask, render_template, jsonify, request, send_file
from flask_mail import Mail, Message
from data_collector import AirQualityDataCollector
from model_trainer import AQIPredictor, forecast_24h
import database as db
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['MAIL_SERVER']         = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT']           = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS']        = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME']       = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']       = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

collector = AirQualityDataCollector()
predictor = AQIPredictor()

# Seed historical data and load/train model on startup
db.seed_historical_data()

if not predictor.load_model():
    print("Training new model...")
    predictor.train_model()
    predictor.save_model()

# Cache model comparison results so we don't retrain on every request
_model_comparison_cache = None

AQI_CATEGORIES = {
    1: {"label": "Good", "color": "#00e400", "description": "Air quality is satisfactory"},
    2: {"label": "Moderate", "color": "#ffff00", "description": "Air quality is acceptable"},
    3: {"label": "Unhealthy for Sensitive Groups", "color": "#ff7e00", "description": "Sensitive groups may experience health effects"},
    4: {"label": "Unhealthy", "color": "#ff0000", "description": "Everyone may begin to experience health effects"},
    5: {"label": "Very Unhealthy", "color": "#8f3f97", "description": "Health alert: everyone may experience serious health effects"},
}

HEALTH_RECOMMENDATIONS = {
    1: {
        "level": "Good",
        "color": "#00e400",
        "general": "Air quality is satisfactory. Enjoy outdoor activities!",
        "sensitive": "No restrictions for sensitive groups.",
        "outdoor": "✅ Safe for all outdoor activities.",
        "mask": "No mask needed.",
        "icon": "😊"
    },
    2: {
        "level": "Moderate",
        "color": "#ffff00",
        "general": "Air quality is acceptable for most people.",
        "sensitive": "Unusually sensitive individuals should consider limiting prolonged outdoor exertion.",
        "outdoor": "⚠️ Sensitive groups should limit prolonged outdoor exertion.",
        "mask": "Optional for sensitive individuals.",
        "icon": "😐"
    },
    3: {
        "level": "Unhealthy for Sensitive Groups",
        "color": "#ff7e00",
        "general": "Members of sensitive groups may experience health effects.",
        "sensitive": "Children, elderly, and people with respiratory/heart conditions should reduce outdoor activity.",
        "outdoor": "🚶 Reduce prolonged or heavy outdoor exertion.",
        "mask": "Recommended for sensitive groups (N95).",
        "icon": "😷"
    },
    4: {
        "level": "Unhealthy",
        "color": "#ff0000",
        "general": "Everyone may begin to experience health effects.",
        "sensitive": "Sensitive groups should avoid all outdoor exertion.",
        "outdoor": "🏠 Everyone should avoid prolonged outdoor activities.",
        "mask": "Wear N95 mask outdoors.",
        "icon": "🤢"
    },
    5: {
        "level": "Very Unhealthy",
        "color": "#8f3f97",
        "general": "Health alert — everyone may experience serious health effects.",
        "sensitive": "Sensitive groups should remain indoors and keep activity levels low.",
        "outdoor": "🔴 Avoid all outdoor activities. Stay indoors.",
        "mask": "N95/N99 mask mandatory if going outside.",
        "icon": "☠️"
    },
}


def detect_pollution_source(data):
    pm25, pm10, co, no2, so2 = data['pm2_5'], data['pm10'], data['co'], data['no2'], data['so2']
    sources = []
    if no2 > 40 and co > 600:
        sources.append({"source": "Traffic Emission", "confidence": 85})
    if so2 > 20 and pm10 > 100:
        sources.append({"source": "Industrial Pollution", "confidence": 78})
    if pm10 > pm25 * 2 and no2 < 30:
        sources.append({"source": "Construction Dust", "confidence": 72})
    if pm25 > 60 and co > 700:
        sources.append({"source": "Biomass Burning", "confidence": 80})
    return sources[0] if sources else {"source": "Mixed Sources", "confidence": 65}


# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/about')
def about():
    return render_template('about.html')


# ── Core API ───────────────────────────────────────────────────────────────────

@app.route('/api/current')
def get_current_data():
    lat = float(request.args.get('lat', 28.6139))
    lon = float(request.args.get('lon', 77.2090))

    data = collector.fetch_air_quality(lat, lon)
    features = [data['pm2_5'], data['pm10'], data['co'], data['no2'], data['o3'], data['so2']]
    predicted_aqi, probabilities = predictor.predict(features)

    data.update({
        'lat': lat, 'lon': lon,
        'predicted_aqi': predicted_aqi,
        'aqi_info': AQI_CATEGORIES[predicted_aqi],
        'confidence': float(max(probabilities) * 100),
        'health_advice': list(HEALTH_RECOMMENDATIONS[predicted_aqi].values()),
        'health_recommendation': HEALTH_RECOMMENDATIONS[predicted_aqi],
        'pollution_source': detect_pollution_source(data),
    })

    db.insert_record({**data, 'aqi': predicted_aqi})
    return jsonify(data)


@app.route('/api/history')
def get_history():
    return jsonify(db.fetch_records(50))


@app.route('/api/predict', methods=['POST'])
def predict_aqi():
    body = request.json
    features = [float(body.get(k, 0)) for k in ['pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2']]
    predicted_aqi, probabilities = predictor.predict(features)
    return jsonify({
        'predicted_aqi': predicted_aqi,
        'aqi_info': AQI_CATEGORIES[predicted_aqi],
        'confidence': float(max(probabilities) * 100),
        'probabilities': probabilities.tolist(),
        'health_recommendation': HEALTH_RECOMMENDATIONS[predicted_aqi],
    })


@app.route('/api/stats')
def get_stats():
    return jsonify(db.get_stats())


@app.route('/api/trend')
def get_trend():
    records = db.fetch_records(20)
    if not records:
        return jsonify({'timestamps': [], 'pm2_5': [], 'pm10': [], 'aqi': []})
    df = pd.DataFrame(records)
    return jsonify({
        'timestamps': df['timestamp'].tolist(),
        'pm2_5': df['pm2_5'].tolist(),
        'pm10': df['pm10'].tolist(),
        'aqi': df['aqi'].tolist(),
    })


@app.route('/api/download')
def download_data():
    df = db.fetch_all_df()
    path = 'data/air_quality_export.csv'
    df.to_csv(path, index=False)
    return send_file(path, as_attachment=True, download_name='air_quality_data.csv')


# ── New Advanced Endpoints ─────────────────────────────────────────────────────

@app.route('/api/model-comparison')
def model_comparison():
    """Compare multiple ML models and return accuracy metrics."""
    global _model_comparison_cache
    if _model_comparison_cache is None:
        df = db.fetch_all_df()
        data_path = None
        if not df.empty and len(df) >= 50:
            path = 'data/training_export.csv'
            df.to_csv(path, index=False)
            data_path = path
        _model_comparison_cache = predictor.compare_models(data_path)
        predictor.save_model()
    return jsonify(_model_comparison_cache)


@app.route('/api/forecast24h')
def forecast_24h_api():
    """24-hour AQI forecast using time-series projection."""
    df = db.fetch_all_df()
    forecasts = forecast_24h(df)
    return jsonify(forecasts)


@app.route('/api/seasonal-trends')
def seasonal_trends():
    """Monthly average PM2.5 and AQI for seasonal analysis."""
    df = db.fetch_all_df()
    if df.empty:
        return jsonify([])
    df['month'] = pd.to_datetime(df['timestamp']).dt.month
    monthly = df.groupby('month').agg(
        avg_pm25=('pm2_5', 'mean'),
        avg_aqi=('aqi', 'mean'),
        avg_pm10=('pm10', 'mean'),
        count=('id', 'count')
    ).reset_index()
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly['month_name'] = monthly['month'].apply(lambda m: month_names[m - 1])
    return jsonify(monthly.round(2).to_dict('records'))


@app.route('/api/heatmap')
def heatmap_data():
    """
    Return day-of-week × hour-of-day average PM2.5 for heatmap visualization.
    Falls back to synthetic pattern if insufficient real data.
    """
    df = db.fetch_all_df()
    if len(df) >= 50:
        df['dt'] = pd.to_datetime(df['timestamp'])
        df['dow'] = df['dt'].dt.dayofweek   # 0=Mon
        df['hour'] = df['dt'].dt.hour
        pivot = df.groupby(['dow', 'hour'])['pm2_5'].mean().reset_index()
        pivot.columns = ['day', 'hour', 'pm2_5']
        return jsonify(pivot.round(2).to_dict('records'))

    # Synthetic 7×24 pattern
    import numpy as np
    np.random.seed(7)
    rows = []
    for d in range(7):
        for h in range(24):
            rush = 1.4 if h in [7, 8, 9, 17, 18, 19] else 1.0
            weekend = 0.8 if d >= 5 else 1.0
            pm25 = round(float(np.random.uniform(30, 80) * rush * weekend), 1)
            rows.append({'day': d, 'hour': h, 'pm2_5': pm25})
    return jsonify(rows)


@app.route('/api/health-recommendation')
def health_recommendation():
    aqi = int(request.args.get('aqi', 1))
    aqi = max(1, min(5, aqi))
    return jsonify(HEALTH_RECOMMENDATIONS[aqi])


@app.route('/api/send-feedback', methods=['POST'])
def send_feedback():
    try:
        data    = request.json
        name    = data.get('name', '').strip()
        email   = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400

        developer_email = 'ayshathrifa26@gmail.com'

        msg = Message(
            subject=f"[AQI Monitor] Feedback: {subject}",
            sender=os.getenv('MAIL_USERNAME'),
            recipients=[developer_email],
            reply_to=email
        )
        msg.body = f"""You have received new feedback on AQI Monitor.

From    : {name}
Email   : {email}
Subject : {subject}

Message:
{message}
"""
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Feedback sent successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
