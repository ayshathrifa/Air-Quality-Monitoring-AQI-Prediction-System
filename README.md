# Real-Time Air Quality Monitoring & AQI Prediction

## Project Overview
A comprehensive web-based system for real-time air quality monitoring and AQI (Air Quality Index) prediction using Machine Learning.

## Features
- ✅ Real-time air quality data collection
- ✅ AQI prediction using Random Forest ML model
- ✅ Interactive web dashboard
- ✅ Multiple pollutant monitoring (PM2.5, PM10, CO, NO2, O3, SO2)
- ✅ Custom AQI prediction
- ✅ Historical data tracking
- ✅ Statistics and analytics

## Technology Stack
- **Backend**: Flask (Python)
- **Machine Learning**: Scikit-learn (Random Forest Classifier)
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML, CSS, JavaScript
- **API**: OpenWeatherMap Air Pollution API

## Project Structure
```
AirQualityMonitoring/
├── app.py                  # Flask web application
├── data_collector.py       # Air quality data collection
├── model_trainer.py        # ML model training
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── data/                   # Data storage
├── models/                 # Trained ML models
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── script.js      # Frontend logic
└── templates/
    └── index.html         # Main dashboard
```

## Installation & Setup

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key (Optional)
Edit `.env` file and add your OpenWeatherMap API key:
```
API_KEY=your_api_key_here
```
Note: The system works with demo data if no API key is provided.

### Step 3: Train the ML Model
```bash
python model_trainer.py
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Access the Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### 1. View Current AQI
- The dashboard automatically displays current air quality data
- AQI is color-coded based on severity
- Confidence level shows prediction accuracy

### 2. Change Location
- Enter latitude and longitude coordinates
- Click "Update" to fetch data for that location
- Default location: Delhi, India (28.6139, 77.2090)

### 3. Custom Prediction
- Enter pollutant values manually
- Click "Predict AQI" to get prediction
- Useful for "what-if" scenarios

### 4. View Statistics
- Total records collected
- Average pollutant levels
- Historical trends

## AQI Categories

| AQI | Category | Color | Description |
|-----|----------|-------|-------------|
| 1 | Good | Green | Air quality is satisfactory |
| 2 | Moderate | Yellow | Air quality is acceptable |
| 3 | Unhealthy for Sensitive Groups | Orange | Sensitive groups may be affected |
| 4 | Unhealthy | Red | Everyone may experience health effects |
| 5 | Very Unhealthy | Purple | Health alert for everyone |

## ML Model Details
- **Algorithm**: Random Forest Classifier
- **Features**: PM2.5, PM10, CO, NO2, O3, SO2
- **Target**: AQI Category (1-5)
- **Accuracy**: ~95% on test data
- **Training Data**: 1000 synthetic samples based on EPA standards

## API Endpoints

### GET /api/current
Fetch current air quality data
- Parameters: `lat`, `lon`
- Returns: Current pollutant levels and predicted AQI

### GET /api/history
Get historical data
- Returns: Last 50 records

### POST /api/predict
Predict AQI from custom input
- Body: JSON with pollutant values
- Returns: Predicted AQI and confidence

### GET /api/stats
Get statistics
- Returns: Aggregated statistics

## Troubleshooting

### Issue: Module not found
**Solution**: Install all dependencies
```bash
pip install -r requirements.txt
```

### Issue: Model not found
**Solution**: Train the model first
```bash
python model_trainer.py
```

### Issue: Port already in use
**Solution**: Change port in app.py or kill the process using port 5000

## Future Enhancements
- [ ] Add data visualization charts
- [ ] Implement user authentication
- [ ] Add email/SMS alerts
- [ ] Mobile app development
- [ ] Integration with more data sources
- [ ] Advanced ML models (LSTM, XGBoost)

## Contributors
- Your Name - Mini Project

## License
MIT License

## Submission Date
Target: 10th (MVP)
